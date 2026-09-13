"""Les contrôles objectifs — et rien d'autre.

Décision d'Abdoulaye du 05/09/2026 : aucune règle Python ne touche plus au fond
ni au style. Ces deux registres passent par les prompts et par le juge.

Ce qui a été retiré, et pourquoi. Le nombre de phrases, la longueur des phrases,
la ponctuation, le sujet concret, la présence d'un terme du post, l'interdiction
de féliciter : ce sont des jugements de style qu'une règle mécanique applique mal.
Le compte de phrases se trompait sur « Gemini 3.8 », l'interdiction de mots creux
a produit quatre synonymes, la présence obligatoire d'un nom propre forçait des
tournures artificielles.

Ce qui reste tient en quatre règles, et chacune constate un fait vérifiable sans
interpréter une intention : la langue déclarée, la langue réellement écrite,
l'absence de lien, et l'absence de doublon entre deux tentatives d'un même run.

Volontairement sans dépendance à `contracts.py` ou `pydantic` : ces fonctions
doivent pouvoir être testées et relues seules.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Règle : aucun lien dans le commentaire
#
# Ce n'est ni du fond ni du style : la présence d'une URL est un fait, et un
# commentaire qui en porte un ressemble à une publicité quel qu'en soit le texte.
# ---------------------------------------------------------------------------

_URL_PATTERN = re.compile(r"(https?://|www\.)\S+", re.IGNORECASE)


def check_no_hyperlink(comment: str) -> list[str]:
    return ["hyperlink_present"] if _URL_PATTERN.search(comment) else []


# ---------------------------------------------------------------------------
# Règle : la langue du commentaire est celle du post
#
# Deux vérifications, pas une. Un petit modèle peut déclarer "fr" et écrire en
# anglais : on contrôle le champ déclaré ET le texte produit.
# ---------------------------------------------------------------------------

_FRENCH_MARKERS = frozenset({
    "le", "la", "les", "des", "une", "un", "et", "est", "pour", "avec", "dans",
    "sur", "que", "ce", "cette", "vous", "nous", "pas",
})
_ENGLISH_MARKERS = frozenset({
    "the", "a", "an", "and", "is", "are", "for", "with", "in", "on", "that",
    "this", "you", "we", "not", "to", "of",
})


def detect_language(text: str) -> str | None:
    words = re.findall(r"[a-zàâçéèêëîïôûùüÿñæœ]+", text.lower())
    french_score = sum(word in _FRENCH_MARKERS for word in words)
    english_score = sum(word in _ENGLISH_MARKERS for word in words)
    if french_score == english_score:
        return None
    return "fr" if french_score > english_score else "en"


def check_language_match(declared_language: str, expected_language: str) -> list[str]:
    return [] if declared_language == expected_language else ["language_mismatch"]


def check_detected_language_match(comment: str, expected_language: str) -> list[str]:
    detected = detect_language(comment)
    if detected is not None and detected != expected_language:
        return ["detected_language_mismatch"]
    return []


# ---------------------------------------------------------------------------
# Règle : pas deux fois le même brouillon sur les deux tentatives autorisées
# ---------------------------------------------------------------------------

def normalize_comment(text: str) -> str:
    return " ".join(re.findall(r"\w+", text.lower()))


def check_not_duplicate(comment: str, prior_comments: frozenset[str]) -> list[str]:
    normalized = normalize_comment(comment)
    return ["duplicate_comment"] if normalized and normalized in prior_comments else []


# ---------------------------------------------------------------------------
# Traduction d'un code de violation en consigne rédigée.
#
# La boucle de révision renvoyait au rédacteur des codes machine. On lui
# demandait de corriger une faute qu'on ne lui avait jamais expliquée.
# ---------------------------------------------------------------------------

_VIOLATION_HELP: dict[str, str] = {
    "hyperlink_present": "Supprime le lien.",
    "language_mismatch": "Écris dans la langue demandée, et déclare la même dans le champ language.",
    "detected_language_mismatch": "Le texte écrit n'est pas dans la langue demandée.",
    "duplicate_comment": "Ce commentaire est identique au précédent. Change d'angle.",
}


def explain_violation(code: str) -> str:
    return _VIOLATION_HELP.get(code.split(":", 1)[0], code)


# ---------------------------------------------------------------------------
# Agrégation
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ControlContext:
    comment: str
    declared_language: str
    expected_language: str
    prior_comments: frozenset[str] = frozenset()
    extra_violations: list[str] = field(default_factory=list)


def run_controls(ctx: ControlContext) -> list[str]:
    """Quatre règles, toutes objectives. Le fond et le style vivent ailleurs."""
    violations: list[str] = []
    violations += check_no_hyperlink(ctx.comment)
    violations += check_language_match(ctx.declared_language, ctx.expected_language)
    violations += check_detected_language_match(ctx.comment, ctx.expected_language)
    violations += check_not_duplicate(ctx.comment, ctx.prior_comments)
    violations += ctx.extra_violations
    return violations
