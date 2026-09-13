"""Orchestrateur du moteur de commentaires LinkedIn.

Chaîne actuelle (refonte du 05/09/2026) :

    post -> [analyseur]   commentable . langue . post_type . DOMAINES touchés
         -> [code]        domaines -> principes de ces domaines
         -> [rédacteur]   le regard, les principes applicables, les règles
                          d'écriture et cinq exemples validés
         -> [contrôles]   quatre règles objectives, aucune de fond ni de style
         -> [juge]        fabrication, platitude, valeur. Une réécriture au plus
         -> skip | draft | error

Ce qui a disparu. Le corpus d'ancrages et son sélecteur : mesuré sur le feed
consultant, le sélecteur refusait les candidats 27 fois sur 27, et quinze faits
datés ne couvrent pas la diversité d'un fil d'actualité.

Ce qui n'a pas bougé : la défense anti-injection dans les trois rôles modèle, la
séparation analyseur / rédacteur / juge, le forçage de la langue sur celle du
post, et le pouvoir du juge de rejeter et pas seulement corriger.
"""

from __future__ import annotations

from dataclasses import asdict
import json
import re
import time
from typing import Protocol

from pydantic import ValidationError

from app.linkedin_comments.contracts import (
    AnalysisResult,
    CommentRunResult,
    DraftResult,
    JudgeResult,
    LinkedInPost,
    PostType,
    RevisionBudget,
    RevisionRecord,
    RunOutcome,
    SourceUnit,
)
from app.linkedin_comments.controls import ControlContext, explain_violation, normalize_comment, run_controls
from app.linkedin_comments.audit import complete_with_trace
from app.linkedin_comments.profil import domaines_pour, principes_des_domaines
from app.linkedin_comments.llm_errors import LlmResponseError, OllamaUnavailable
from app.linkedin_comments.ollama_client import Completion
from app.linkedin_comments.prompts import (
    PROMPT_VERSION,
    analyzer_prompt,
    judge_prompt,
    writer_prompt,
)
from app.linkedin_comments.worlds import World, get_world, known_world_ids

# Boucle de révision bornée à une seule réécriture (attempt 1 = brouillon
# initial, attempt 2 = l'unique réécriture autorisée), qu'elle soit déclenchée
# par les contrôles ou par le juge. Le juge reçoit l'historique cumulé des
# retours pour ne pas osciller entre deux exigences contraires.
MAX_ATTEMPTS = 2


class CommentLlm(Protocol):
    model: str

    def healthcheck(self) -> None: ...

    def complete(
        self, *, system: str, user: str, max_tokens: int, temperature: float, schema: dict
    ) -> Completion: ...


class RunRepository(Protocol):
    def save(self, result: CommentRunResult) -> None: ...


def source_units_from_text(text: str) -> list[SourceUnit]:
    chunks = [chunk.strip() for chunk in re.split(r"(?<=[.!?])\s+|\n+", text) if chunk.strip()]
    return [SourceUnit(id=f"s{index}", text=chunk) for index, chunk in enumerate(chunks, start=1)] or [
        SourceUnit(id="s1", text=text.strip())
    ]


def json_object_from_llm(text: str) -> str:
    cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned).strip()
    if cleaned.startswith("{") and cleaned.endswith("}"):
        return cleaned

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start >= 0 and end > start:
        return cleaned[start : end + 1]
    return cleaned


class LinkedInCommentRuntime:
    def __init__(
        self,
        llm: CommentLlm,
        repository: RunRepository,
        *,
        budget: RevisionBudget | None = None,
        analysis_max_tokens: int = 1200,
        writer_max_tokens: int = 700,
        judge_max_tokens: int = 800,
    ):
        self.llm = llm
        self.repository = repository
        self.default_budget = budget or RevisionBudget()
        self.analysis_max_tokens = analysis_max_tokens
        self.writer_max_tokens = writer_max_tokens
        self.judge_max_tokens = judge_max_tokens

    def run(self, post: LinkedInPost, reader_world: str, budget: RevisionBudget | None = None) -> CommentRunResult:
        effective_budget = budget or self.default_budget
        result = CommentRunResult(
            linkedin_post_id=post.id,
            outcome=RunOutcome.ERROR,
            model=self.llm.model,
            prompt_version=PROMPT_VERSION,
            reader_world=reader_world or None,
            content_hash=post.content_hash,
        )

        if not reader_world:
            result.outcome = RunOutcome.SKIP
            result.reason_code = "monde_lecteur_manquant"
            result.diagnostics = ["reader_world absent : impossible de choisir une politique éditoriale."]
            return self._finish(result)

        # Un monde inconnu est une panne de configuration, pas une décision
        # éditoriale : il range sous ERROR. Sans ce contrôle, une faute de frappe
        # produisait un skip silencieux indiscernable d'un post hors sujet.
        world = get_world(reader_world)
        if world is None:
            return self._error(
                result,
                "monde_lecteur_inconnu",
                detail=f"reader_world={reader_world!r} absent du registre. Mondes déclarés : {known_world_ids()}.",
            )

        result.editorial_context = {
            "world": asdict(world),
            "domains": [asdict(domain) for domain in domaines_pour(world.id)],
            "principes_proposes": [],
        }
        started_at = time.monotonic()
        used_tokens = 0
        try:
            self.llm.healthcheck()

            analysis, completion = self._analyze(post, world, result.model_calls)
            used_tokens += completion.output_tokens
            result.analysis = analysis
            result.source_language = analysis.source_language
            result.post_type = analysis.post_type

            if analysis.decision == "skip":
                result.outcome = RunOutcome.SKIP
                result.reason_code = analysis.skip_reason or "analyzer_skip"
                return self._finish(result)

            if analysis.post_type is None:
                # Une classification manquante n'est pas un contrat rompu : plus
                # aucune structure ne dépend du post_type. On la fixe plutôt que
                # de ranger le post en panne.
                analysis = analysis.model_copy(update={"post_type": PostType.FOND})
                result.analysis = analysis
                result.post_type = analysis.post_type
                result.diagnostics.append("post_type absent de l'analyse, replié sur fond.")

            # Le post touche-t-il un des domaines d'Abdoulaye ? Si oui, les
            # principes de ces domaines sont proposés au rédacteur, qui garde la
            # liberté de n'en retenir aucun. Sinon, il répond en conversation.
            principes = principes_des_domaines(analysis.domaines, world.id)
            result.domaines = analysis.domaines
            result.comment_mode = "principe" if principes else "conversation"
            result.editorial_context["principes_proposes"] = [label for _, label in principes]

            feedback: list[str] = []
            feedback_history: list[str] = []
            prior_comments: set[str] = set()

            for attempt in range(1, MAX_ATTEMPTS + 1):
                if self._budget_exhausted(started_at, used_tokens, effective_budget):
                    return self._error(result, "budget_execution_epuise")

                draft, completion = self._write(post, world, analysis, principes, feedback, result.model_calls)
                used_tokens += completion.output_tokens
                # Les identifiants du principe et de l'ancrage sont estampillés par
                # le code, jamais recopiés depuis la sortie du modèle : on ne
                # demande jamais à un modèle de répéter une constante qu'on connaît déjà.
                draft = draft.model_copy(
                    update={"model": self.llm.model, "prompt_version": PROMPT_VERSION}
                )

                violations = run_controls(
                    ControlContext(
                        comment=draft.comment,
                        declared_language=draft.language.value,
                        expected_language=analysis.source_language.value,
                        prior_comments=frozenset(prior_comments),
                    )
                )
                record = RevisionRecord(attempt=attempt, draft=draft, control_violations=violations, feedback=feedback)
                result.revisions.append(record)
                prior_comments.add(normalize_comment(draft.comment))

                if violations:
                    feedback = [explain_violation(violation) for violation in violations]
                    feedback_history += feedback
                    if attempt == MAX_ATTEMPTS:
                        result.outcome = RunOutcome.SKIP
                        result.reason_code = "controles_echec_apres_reecriture"
                        result.diagnostics = list(violations)
                        return self._finish(result)
                    continue

                # Aucune vérification de budget ici, volontairement. Le budget décide
                # si on ENTREPREND une tentative, jamais s'il faut jeter une tentative
                # déjà écrite. Un brouillon non jugé est du travail perdu : la
                # rédaction a coûté un appel, le juge en coûte un seul de plus.
                # Le 05/09/2026, trois posts sur seize sont sortis en erreur avec un
                # commentaire rédigé et jamais lu, faute d'un test placé ici.
                judge, completion = self._judge(post, draft, feedback_history, world, result.model_calls)
                used_tokens += completion.output_tokens
                record.judge = judge

                if judge.decision == "approve":
                    result.outcome = RunOutcome.DRAFT
                    result.comment_text = draft.comment
                    return self._finish(result)

                if judge.decision == "reject":
                    result.outcome = RunOutcome.SKIP
                    result.reason_code = "juge_reject"
                    result.diagnostics = judge.reasons or ["juge : rejet sans motif détaillé"]
                    return self._finish(result)

                # judge.decision == "rewrite"
                feedback = [f"juge:{item}" for item in (judge.rewrite_instructions or judge.reasons)]
                feedback_history += feedback
                if attempt == MAX_ATTEMPTS:
                    result.outcome = RunOutcome.SKIP
                    result.reason_code = "juge_reecriture_epuisee"
                    result.diagnostics = list(feedback)
                    return self._finish(result)

            # Ne devrait jamais être atteint : la boucle couvre déjà les deux issues.
            return self._error(result, "boucle_revision_non_resolue")

        except OllamaUnavailable as exc:
            return self._error(result, "ollama_indisponible", detail=f"{exc.__class__.__name__}: {exc}")
        except (ValidationError, ValueError, TypeError, json.JSONDecodeError, LlmResponseError) as exc:
            # Une erreur de contrat n'est pas une décision, c'est une panne :
            # elle range sous ERROR, jamais sous SKIP.
            return self._error(result, f"contrat_invalide:{exc.__class__.__name__}", detail=str(exc))
        except Exception as exc:
            return self._error(result, f"erreur_runtime:{exc.__class__.__name__}", detail=str(exc))

    def _analyze(self, post: LinkedInPost, world: World, traces) -> tuple[AnalysisResult, Completion]:
        system, user, schema = analyzer_prompt(post, source_units_from_text(post.text), world=world)
        completion = complete_with_trace(self.llm, traces, stage="analysis",
            system=system, user=user, max_tokens=self.analysis_max_tokens, temperature=0.1, schema=schema
        )
        analysis = AnalysisResult.model_validate_json(json_object_from_llm(completion.text))
        return analysis, completion

    def _write(
        self,
        post: LinkedInPost,
        world: World,
        analysis: AnalysisResult,
        principes: list[tuple[str, str]],
        feedback: list[str],
        traces,
    ) -> tuple[DraftResult, Completion]:
        """Un seul rédacteur. `principes` vide, c'est le régime conversation."""
        system, user, schema = writer_prompt(
            post,
            world=world,
            required_language=analysis.source_language,
            principes=principes,
            feedback=feedback,
        )
        completion = complete_with_trace(self.llm, traces, stage="writing",
            system=system, user=user, max_tokens=self.writer_max_tokens, temperature=0.5, schema=schema
        )
        draft = DraftResult.model_validate_json(json_object_from_llm(completion.text))
        return draft, completion

    def _judge(
        self,
        post: LinkedInPost,
        draft: DraftResult,
        feedback_history: list[str],
        world: World,
        traces,
    ) -> tuple[JudgeResult, Completion]:
        system, user, schema = judge_prompt(post, draft, feedback_history, world=world)
        completion = complete_with_trace(self.llm, traces, stage="judging",
            system=system, user=user, max_tokens=self.judge_max_tokens, temperature=0.0, schema=schema
        )
        judge = JudgeResult.model_validate_json(json_object_from_llm(completion.text))
        return judge, completion

    @staticmethod
    def _budget_exhausted(started_at: float, used_tokens: int, budget: RevisionBudget) -> bool:
        return used_tokens >= budget.max_total_tokens or (time.monotonic() - started_at) >= budget.max_duration_seconds

    def _error(self, result: CommentRunResult, reason_code: str, detail: str | None = None) -> CommentRunResult:
        result.outcome = RunOutcome.ERROR
        result.reason_code = reason_code
        if detail:
            result.diagnostics = [detail]
        return self._finish(result)

    def _finish(self, result: CommentRunResult) -> CommentRunResult:
        self.repository.save(result)
        return result
