from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from app.linkedin_comments.audit import ModelCallTrace


class SourceLanguage(StrEnum):
    FRENCH = "fr"
    ENGLISH = "en"


class PostType(StrEnum):
    """Classification du post — défaut n°2 de l'audit du 01/09/2026.

    Sur un post de célébration, nuancer la célébration retourne l'auteur
    contre nous : le rédacteur applique une structure différente selon ce
    type, pas seulement un contenu différent (voir prompts.py).
    """

    CELEBRATION = "celebration"
    FOND = "fond"
    ANNONCE = "annonce"
    RECRUTEMENT = "recrutement"
    TERRAIN = "terrain"


class RevisionBudget(BaseModel):
    """Budget d'exécution (temps/tokens) — pas un budget de tentatives.

    Le nombre de réécritures n'est plus configurable : il est borné en dur à
    une seule réécriture (voir MAX_ATTEMPTS dans runtime.py), conformément à
    la correction du défaut n°3.
    """

    max_total_tokens: int = Field(default=6000, ge=1000, le=50000)
    # 150 s, choisi pour s'emboîter dans la chaîne des délais :
    #   client Ollama 60 s  <  budget 150 s  <  node n8n 300 s
    # Pire cas : le budget autorise une dernière tentative à 149 s, l'appel dure
    # au plus 60 s, total 209 s, sous les 300 s du node. Mesuré le 06/09/2026,
    # un post sain prend 11 à 17 s, donc ce budget vaut dix fois la normale.
    max_duration_seconds: int = Field(default=150, ge=10, le=900)


class LinkedInPost(BaseModel):
    id: UUID
    text: str = Field(min_length=1)
    url: str | None = None
    author_name: str | None = None
    content_hash: str | None = None
    # `linkedin_targets.why_follow`, écrit par Abdoulaye sur la personne suivie.
    # Contrairement à `text`, cette note est une source de confiance : elle vient
    # de lui, pas du web. Elle est donc placée dans le prompt système du
    # rédacteur, jamais dans la charge utile aux côtés du post, et elle est
    # retirée des prompts de l'analyseur et du juge, qui n'en ont pas l'usage.
    why_follow: str | None = None


class SourceUnit(BaseModel):
    id: str
    text: str = Field(min_length=1)


class AnalysisResult(BaseModel):
    """decision · langue · post_type · domaines touchés.

    Les cinquante `tags_situation` n'existaient que pour atteindre un ancrage
    dans le corpus. Le corpus a quitté la chaîne le 05/09/2026 : l'analyseur
    répond désormais à une question fermée sur six domaines, ce qu'un petit
    modèle local classe bien plus sûrement.
    """

    decision: Literal["commentable", "skip"]
    source_language: SourceLanguage
    post_type: PostType | None = None
    domaines: list[str] = Field(default_factory=list)
    skip_reason: str | None = None

    @field_validator("domaines")
    @classmethod
    def unique_domaines(cls, value: list[str]) -> list[str]:
        return list(dict.fromkeys(value))


class DraftResult(BaseModel):
    comment: str = Field(min_length=1)
    language: SourceLanguage
    editorial_hypothesis: str = Field(min_length=1, max_length=280)
    prompt_version: str = ""
    model: str = ""

    @field_validator("editorial_hypothesis", mode="before")
    @classmethod
    def truncate_hypothesis(cls, value: object) -> object:
        """Un champ de diagnostic ne doit jamais transformer un bon commentaire en panne.

        `editorial_hypothesis` ne part jamais sur LinkedIn : il sert à comprendre
        pourquoi le rédacteur a écrit ça. Le schéma passé au modèle borne déjà ce
        champ à 280 caractères, mais Ollama n'impose pas `maxLength` de façon
        fiable. Un modèle bavard cassait alors la validation et rangeait le post
        sous ERROR, en jetant un commentaire par ailleurs valide.
        """
        if isinstance(value, str) and len(value) > 280:
            return value[:277] + "..."
        return value


class JudgeResult(BaseModel):
    """Le juge garde le pouvoir de rejeter, pas seulement de corriger — inchangé.

    Il ne reçoit plus le grounding_contract de l'analyseur (voir
    prompts.py::judge_prompt) : une seule question irréductible.
    """

    # Rempli avant la décision, par construction du schéma : la phrase du post
    # dont le commentaire est le plus proche. Le juge doit lire avant de juger.
    passage_le_plus_proche: str = ""
    decision: Literal["approve", "rewrite", "reject"]
    reasons: list[str] = Field(default_factory=list)
    rewrite_instructions: list[str] = Field(default_factory=list)


class RevisionRecord(BaseModel):
    attempt: int
    draft: DraftResult | None = None
    control_violations: list[str] = Field(default_factory=list)
    judge: JudgeResult | None = None
    feedback: list[str] = Field(default_factory=list)


class RunOutcome(StrEnum):
    """Trois issues, jamais confondues — défaut n°3 (observabilité) de l'audit.

    Une erreur de contrat (JSON qui ne respecte pas le schéma attendu) n'est
    pas une décision : c'est une panne. Elle range sous ERROR, jamais sous
    SKIP — sans quoi un feed pauvre en résultat et un moteur en panne
    deviennent indiscernables dans les journaux.
    """

    DRAFT = "draft"
    SKIP = "skip"
    ERROR = "error"


class CommentRunResult(BaseModel):
    run_id: UUID = Field(default_factory=uuid4)
    linkedin_post_id: UUID
    outcome: RunOutcome
    reason_code: str | None = None
    source_language: SourceLanguage | None = None
    post_type: PostType | None = None
    reader_world: str | None = None
    # Décrit le contexte fourni, pas un registre imposé au commentaire.
    # "ancre" = expérience disponible ; "libre" = aucune expérience injectée.
    # Tracé sur le résultat pour qu'un dry-run distingue les deux régimes sans
    # relire les prompts.
    comment_mode: str | None = None
    # Les domaines d'expertise reconnus dans le post. Ils décident quels principes
    # sont proposés au rédacteur, donc ils expliquent après coup pourquoi un
    # commentaire est parti en régime principe ou en régime conversation.
    domaines: list[str] = Field(default_factory=list)
    editorial_context: dict = Field(default_factory=dict)
    model_calls: list[ModelCallTrace] = Field(default_factory=list)
    comment_text: str | None = None
    analysis: AnalysisResult | None = None
    revisions: list[RevisionRecord] = Field(default_factory=list)
    diagnostics: list[str] = Field(default_factory=list)
    model: str
    prompt_version: str = "lcr-v4-domaines"
    content_hash: str | None = Field(default=None, exclude=True)
    # Estampillé par le code après coup, jamais recopié depuis une sortie modèle.
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StartLinkedInCommentRun(BaseModel):
    linkedin_post_id: UUID
    reader_world: str = Field(min_length=1)
    budget: RevisionBudget | None = None
