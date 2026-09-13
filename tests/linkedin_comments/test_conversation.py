"""Régressions métier de la conversation libre et de sa traçabilité."""
import json
from dataclasses import replace
from uuid import uuid4

import pytest

from app.linkedin_comments.contracts import LinkedInPost
from app.linkedin_comments.controls import ControlContext, run_controls
from app.linkedin_comments.prompts import analyzer_prompt, judge_prompt, writer_prompt
from app.linkedin_comments.worlds import WORLDS
from app.linkedin_comments.runtime import LinkedInCommentRuntime
from app.linkedin_comments.contracts import DraftResult, SourceLanguage
from test_runtime import FakeLlm, FakeRepo


@pytest.mark.parametrize('world', WORLDS)
def test_free_contribution_and_full_audit_for_every_world(world):
    post = LinkedInPost(id=uuid4(), text="Nous avons formé les équipes au suivi de caisse.")
    llm = FakeLlm([
        {'decision':'commentable','source_language':'fr','post_type':'celebration','domaines':[],'skip_reason':None},
        {'comment':'Bravo pour ce travail sur le suivi de caisse. Quel usage les équipes souhaitent-elles reprendre en premier ?',
         'language':'fr','editorial_hypothesis':'S’intéresser au choix des équipes.'},
        {'decision':'approve','reasons':['Question concrète sur les usages.'],'rewrite_instructions':[]},
    ])
    repo = FakeRepo()
    result = LinkedInCommentRuntime(llm, repo).run(post,world)
    assert result.outcome == 'draft'
    assert result.comment_mode == 'conversation'
    assert result.editorial_context['world']['id'] == world
    assert [t.stage for t in result.model_calls] == ['analysis','writing','judging']
    assert all(t.response and t.duration_ms >= 0 for t in result.model_calls)
    assert json.loads(result.model_calls[1].user)['principes_disponibles'] == []
    assert repo.saved == [result]


def test_malformed_model_response_is_preserved_for_audit():
    result = LinkedInCommentRuntime(FakeLlm([{'broken':True}]),FakeRepo()).run(
        LinkedInPost(id=uuid4(),text='Un post.'),'icp1')
    assert result.outcome == 'error'
    assert json.loads(result.model_calls[0].response) == {'broken':True}


def test_icp1_policy_does_not_change_other_worlds():
    post = LinkedInPost(id=uuid4(),text='Une nouvelle application pour former les équipes.')
    icp, _, _ = analyzer_prompt(post,[],world=WORLDS['icp1'])
    other, _, _ = analyzer_prompt(post,[],world=WORLDS['icp1bis'])
    assert "relayer l'annonce d'un éditeur" not in icp
    assert "relayer l'annonce d'un éditeur" in other
    assert WORLDS['icp1'].question_du_juge != WORLDS['icp1bis'].question_du_juge


def test_no_forced_proper_name_question_or_concrete_opener():
    ctx = ControlContext(comment="La stratégie gagne ici à partir des moyens disponibles.",
        declared_language='fr', expected_language='fr')
    assert run_controls(ctx) == []
    assert 'hyperlink_present' in run_controls(replace(ctx,comment=ctx.comment+' https://example.com'))


def test_invented_experience_is_rejected_without_becoming_a_draft():
    llm = FakeLlm([
        {'decision':'commentable','source_language':'fr','post_type':'fond','domaines':[],'skip_reason':None},
        {'comment':"J'ai formé dix équipes sur ce sujet.",'language':'fr','editorial_hypothesis':'Une expérience.'},
        {'decision':'reject','reasons':["J'ai formé dix équipes : vécu absent des sources."],'rewrite_instructions':[]},
    ])
    result = LinkedInCommentRuntime(llm,FakeRepo()).run(LinkedInPost(id=uuid4(),text='Comment former une équipe ?'),'icp1')
    assert result.outcome == 'skip'
    assert result.comment_text is None
    assert result.revisions[0].judge.decision == 'reject'


def test_la_note_de_relation_va_au_redacteur_et_nulle_part_ailleurs():
    """`why_follow` vient d'Abdoulaye, le post vient du web. On ne les mélange pas.

    La note dit sur quel terrain travaille la personne suivie. Elle sert à
    choisir l'angle, donc elle va au rédacteur. Elle n'a rien à faire chez
    l'analyseur, qui classe un post, ni chez le juge, qui relit un commentaire.
    Et elle ne descend jamais dans la charge utile aux côtés du texte du post,
    qui est déclaré non fiable au modèle.
    """
    note = "Createur de la bibliotheque Instructor. Terrain commun : les sorties JSON contraintes."
    post = LinkedInPost(id=uuid4(), text="Un post sur les schemas JSON.", why_follow=note)
    w = WORLDS['icp1']

    sys_red, user_red, _ = writer_prompt(
        post, world=w, required_language=SourceLanguage.FRENCH, principes=[], feedback=[])
    sys_ana, user_ana, _ = analyzer_prompt(post, [], world=w)
    draft = DraftResult(comment='Un commentaire.', language=SourceLanguage.FRENCH,
                        editorial_hypothesis='Une hypothese.')
    sys_juge, user_juge, _ = judge_prompt(post, draft, [], world=w)

    assert note in sys_red
    assert "ne t'autorise jamais à prêter un vécu" in sys_red
    for texte in (user_red, sys_ana, user_ana, sys_juge, user_juge):
        assert note not in texte
    assert 'why_follow' not in json.loads(user_red)['post']


def test_sans_note_le_prompt_ne_porte_aucun_bloc_vide():
    post = LinkedInPost(id=uuid4(), text="Un post.", why_follow=None)
    system, _, _ = writer_prompt(
        post, world=WORLDS['icp1'], required_language=SourceLanguage.FRENCH,
        principes=[], feedback=[])
    assert "Ce qu'Abdoulaye a noté" not in system
