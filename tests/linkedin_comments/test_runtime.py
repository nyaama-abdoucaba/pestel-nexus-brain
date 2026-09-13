"""Scénarios d'orchestration, avec un faux modèle.

Ces tests prouvent que les bonnes données circulent et que chaque issue tombe au
bon endroit. Ils ne prouvent pas qu'un modèle réel écrit un bon commentaire :
c'est le rôle du dry-run et du lot de véracité.
"""

from __future__ import annotations

import json
import unittest
from uuid import uuid4

from app.linkedin_comments.contracts import LinkedInPost, RevisionBudget, RunOutcome
from app.linkedin_comments.ollama_client import Completion
from app.linkedin_comments.profil import DOMAINES_PAR_ID
from app.linkedin_comments.runtime import LinkedInCommentRuntime

BROUILLON = {
    "comment": "Votre point sur les moyens mérite une suite. Comment le repérez-vous avant de proposer ?",
    "language": "fr",
    "editorial_hypothesis": "Répondre au point des moyens.",
}
APPROUVE = {"decision": "approve", "reasons": [], "rewrite_instructions": []}


def make_post(text: str = "Un post qui parle de méthodes et de moyens.") -> LinkedInPost:
    return LinkedInPost(id=uuid4(), text=text, url=None, author_name="X")


def analyse(**kwargs) -> dict:
    base = {"decision": "commentable", "source_language": "fr", "post_type": "fond",
            "domaines": [], "skip_reason": None}
    base.update(kwargs)
    return base


class FakeLlm:
    model = "qwen-test"

    def __init__(self, responses: list[dict]):
        self.responses = list(responses)
        self.calls = 0

    def healthcheck(self) -> None:
        pass

    def complete(self, *, system, user, max_tokens, temperature, schema) -> Completion:
        self.calls += 1
        self.last_user = user
        payload = self.responses.pop(0)
        return Completion(text=json.dumps(payload, ensure_ascii=False), output_tokens=10)


class FakeRepo:
    def __init__(self):
        self.saved = []

    def save(self, result) -> None:
        self.saved.append(result)


class MondeDuLecteur(unittest.TestCase):
    def test_missing_world_skips_before_any_model_call(self):
        llm = FakeLlm([])
        result = LinkedInCommentRuntime(llm, FakeRepo()).run(make_post(), reader_world="")
        self.assertEqual(result.outcome, RunOutcome.SKIP)
        self.assertEqual(result.reason_code, "monde_lecteur_manquant")
        self.assertEqual(llm.calls, 0)

    def test_unknown_world_is_an_error_not_a_silent_skip(self):
        """Une faute de frappe est une panne de configuration, pas une décision."""
        llm = FakeLlm([])
        result = LinkedInCommentRuntime(llm, FakeRepo()).run(make_post(), reader_world="veille_ia")
        self.assertEqual(result.outcome, RunOutcome.ERROR)
        self.assertEqual(result.reason_code, "monde_lecteur_inconnu")
        self.assertEqual(llm.calls, 0)


class DecisionDeLAnalyseur(unittest.TestCase):
    def test_skip_carries_its_reason(self):
        llm = FakeLlm([analyse(decision="skip", skip_reason="hors_sujet_professionnel", post_type=None)])
        result = LinkedInCommentRuntime(llm, FakeRepo()).run(make_post(), reader_world="icp1")
        self.assertEqual(result.outcome, RunOutcome.SKIP)
        self.assertEqual(result.reason_code, "hors_sujet_professionnel")
        self.assertEqual(llm.calls, 1)

    def test_missing_post_type_falls_back_instead_of_failing(self):
        """Plus aucune structure ne dépend du post_type : son absence n'est pas une panne."""
        llm = FakeLlm([
            {"decision": "commentable", "source_language": "fr", "domaines": [], "skip_reason": None},
            BROUILLON, APPROUVE,
        ])
        result = LinkedInCommentRuntime(llm, FakeRepo()).run(make_post(), reader_world="icp1")
        self.assertEqual(result.outcome, RunOutcome.DRAFT)
        self.assertEqual(result.post_type.value, "fond")

    def test_broken_contract_is_an_error_never_a_skip(self):
        llm = FakeLlm([{"decision": "commentable", "post_type": "fond", "domaines": []}])
        result = LinkedInCommentRuntime(llm, FakeRepo()).run(make_post(), reader_world="icp1")
        self.assertEqual(result.outcome, RunOutcome.ERROR)
        self.assertTrue(result.reason_code.startswith("contrat_invalide:"))


class DesDomainesAuxPrincipes(unittest.TestCase):
    """Le cœur de la refonte : le post entre-t-il dans un domaine, et si oui,
    quels principes sont proposés au rédacteur."""

    def test_no_domain_gives_the_conversation_register(self):
        llm = FakeLlm([analyse(domaines=[]), BROUILLON, APPROUVE])
        result = LinkedInCommentRuntime(llm, FakeRepo()).run(make_post(), reader_world="icp1")
        self.assertEqual(result.outcome, RunOutcome.DRAFT)
        self.assertEqual(result.comment_mode, "conversation")
        self.assertEqual(result.domaines, [])

    def test_a_matched_domain_offers_its_principles_to_the_writer(self):
        llm = FakeLlm([analyse(domaines=["politiques_publiques"]), BROUILLON, APPROUVE])
        result = LinkedInCommentRuntime(llm, FakeRepo()).run(make_post(), reader_world="icp1")
        self.assertEqual(result.comment_mode, "principe")
        self.assertEqual(result.domaines, ["politiques_publiques"])
        proposes = result.editorial_context["principes_proposes"]
        self.assertEqual(len(proposes), len(DOMAINES_PAR_ID["politiques_publiques"].principes))
        envoye = json.loads(result.model_calls[1].user)["principes_disponibles"]
        self.assertEqual(envoye, proposes)

    def test_two_domains_do_not_duplicate_a_shared_principle(self):
        """p10 appartient à trois domaines : il ne doit être proposé qu'une fois."""
        llm = FakeLlm([
            analyse(domaines=["strategie_pilotage", "corporate_finance"]), BROUILLON, APPROUVE,
        ])
        result = LinkedInCommentRuntime(llm, FakeRepo()).run(make_post(), reader_world="icp1")
        proposes = result.editorial_context["principes_proposes"]
        self.assertEqual(len(proposes), len(set(proposes)))

    def test_a_domain_closed_to_this_world_is_ignored(self):
        """ai_practitioner ne voit que le domaine ingénierie IA."""
        llm = FakeLlm([analyse(domaines=["corporate_finance"]), BROUILLON, APPROUVE])
        result = LinkedInCommentRuntime(llm, FakeRepo()).run(make_post(), reader_world="ai_practitioner")
        self.assertEqual(result.comment_mode, "conversation")
        self.assertEqual(result.editorial_context["principes_proposes"], [])


class BoucleDeRevision(unittest.TestCase):
    def test_control_failure_triggers_one_rewrite_then_succeeds(self):
        llm = FakeLlm([
            analyse(),
            {**BROUILLON, "comment": "Voir https://exemple.com pour la suite."},
            BROUILLON, APPROUVE,
        ])
        result = LinkedInCommentRuntime(llm, FakeRepo()).run(make_post(), reader_world="icp1")
        self.assertEqual(result.outcome, RunOutcome.DRAFT)
        self.assertEqual(result.revisions[0].control_violations, ["hyperlink_present"])
        self.assertIn("Supprime le lien.", result.revisions[1].feedback)

    def test_judge_reject_ends_the_run(self):
        llm = FakeLlm([
            analyse(), BROUILLON,
            {"decision": "reject", "reasons": ["vécu fabriqué"], "rewrite_instructions": []},
        ])
        result = LinkedInCommentRuntime(llm, FakeRepo()).run(make_post(), reader_world="icp1")
        self.assertEqual(result.outcome, RunOutcome.SKIP)
        self.assertEqual(result.reason_code, "juge_reject")
        self.assertEqual(result.diagnostics, ["vécu fabriqué"])

    def test_only_one_rewrite_is_allowed(self):
        llm = FakeLlm([
            analyse(), BROUILLON,
            {"decision": "rewrite", "reasons": ["paraphrase"], "rewrite_instructions": ["Ajoute un angle."]},
            {**BROUILLON, "comment": "Un autre angle sur les moyens, plus concret que le précédent."},
            {"decision": "rewrite", "reasons": ["encore"], "rewrite_instructions": ["Encore."]},
        ])
        result = LinkedInCommentRuntime(llm, FakeRepo()).run(make_post(), reader_world="icp1")
        self.assertEqual(result.outcome, RunOutcome.SKIP)
        self.assertEqual(result.reason_code, "juge_reecriture_epuisee")
        self.assertEqual(len(result.revisions), 2)


class Tracabilite(unittest.TestCase):
    def test_every_model_call_is_recorded_in_order(self):
        llm = FakeLlm([analyse(), BROUILLON, APPROUVE])
        result = LinkedInCommentRuntime(llm, FakeRepo()).run(make_post(), reader_world="icp1")
        self.assertEqual([t.stage for t in result.model_calls], ["analysis", "writing", "judging"])

    def test_the_result_is_persisted_exactly_once(self):
        repo = FakeRepo()
        llm = FakeLlm([analyse(), BROUILLON, APPROUVE])
        result = LinkedInCommentRuntime(llm, repo).run(make_post(), reader_world="icp1")
        self.assertEqual(repo.saved, [result])


if __name__ == "__main__":
    unittest.main()


class BudgetEtTravailDejaFait(unittest.TestCase):
    """Le budget décide si on entreprend, jamais s'il faut jeter.

    Le 05/09/2026, trois posts sur seize sont sortis en ERROR alors qu'un
    commentaire venait d'être rédigé. Le moteur vérifiait le budget entre la
    rédaction et le juge, et jetait le brouillon sans l'avoir fait lire. La
    rédaction coûte un appel, le juge un seul de plus : le refuser est un
    mauvais échange dans tous les cas.
    """

    class LlmBavard(FakeLlm):
        """Chaque réponse consomme 600 jetons de sortie, de quoi épuiser un petit budget."""

        def complete(self, *, system, user, max_tokens, temperature, schema):
            completion = super().complete(
                system=system, user=user, max_tokens=max_tokens,
                temperature=temperature, schema=schema,
            )
            return Completion(text=completion.text, output_tokens=600)

    def _budget_serre(self) -> RevisionBudget:
        # 1000 est le minimum autorisé. Analyse 600, rédaction 600 : le budget
        # est dépassé au moment précis où l'ancien test se déclenchait.
        return RevisionBudget(max_total_tokens=1000, max_duration_seconds=900)

    def test_un_brouillon_ecrit_est_toujours_juge(self):
        llm = self.LlmBavard([analyse(), BROUILLON, APPROUVE])

        result = LinkedInCommentRuntime(llm, FakeRepo()).run(
            make_post(), "icp1", budget=self._budget_serre()
        )

        self.assertEqual(result.outcome, RunOutcome.DRAFT)
        self.assertEqual(result.comment_text, BROUILLON["comment"])
        self.assertEqual([t.stage for t in result.model_calls], ["analysis", "writing", "judging"])
        self.assertIsNotNone(result.revisions[0].judge)

    def test_le_budget_arrete_avant_d_entreprendre_une_reecriture(self):
        """La garde reste en place là où elle est utile : à l'entrée d'une tentative."""
        rejet = {"decision": "rewrite", "reasons": ["trop général"], "rewrite_instructions": ["précise"]}
        llm = self.LlmBavard([analyse(), BROUILLON, rejet, BROUILLON, APPROUVE])

        result = LinkedInCommentRuntime(llm, FakeRepo()).run(
            make_post(), "icp1", budget=self._budget_serre()
        )

        self.assertEqual(result.outcome, RunOutcome.ERROR)
        self.assertEqual(result.reason_code, "budget_execution_epuise")
        # Trois appels : la deuxième rédaction n'a jamais été entreprise.
        self.assertEqual(llm.calls, 3)
