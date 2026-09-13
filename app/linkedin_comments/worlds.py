"""Le registre des mondes de lecteur — un espace de noms métier, plus une chaîne libre.

Avant ce module, `reader_world` était une chaîne quelconque validée nulle part.
Un monde mal orthographié ne levait aucune erreur : la présélection ne trouvait
rien et le moteur répondait `corpus_vide_pour_ce_post`, exactement comme pour un
post réellement hors sujet. Les deux pannes devenaient indiscernables dans les
journaux.

Le registre porte aussi ce qui change d'un monde à l'autre. Deux rôles
commerciaux existent dans la doctrine (fiche 04 du coffre, tri du 02/09/2026),
et ils n'appellent pas le même moteur :

    vendre         prouver une compétence vécue à un acheteur possible.
    se_faire_voir  contribuer chez des gens plus qualifiés que soi.

Le rôle ne décide plus si l'on commente, seulement de la question que le juge
pose en fin de chaîne. Le réglage `ancrage_requis` a été retiré le 05/09/2026 :
aucun monde n'exige plus une preuve vécue pour commenter, et un réglage qui ne
varie plus est un réglage mort. Le garde-fou contre le vécu fabriqué vit
désormais dans la première question du juge, pas dans l'absence de commentaire.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class WorldRole(StrEnum):
    VENDRE = "vendre"
    SE_FAIRE_VOIR = "se_faire_voir"


@dataclass(frozen=True)
class World:
    """Un monde de lecteur et tout ce qui change de comportement avec lui."""

    id: str
    label: str
    role: WorldRole
    # L'anti-corpus « actualité IA / annonce produit » de la fiche 07. Devant un
    # acheteur, commenter une sortie de framework n'apporte aucun avantage. Chez
    # des praticiens IA, l'actualité est leur métier : la règle rejetterait tout.
    rejette_actualite: bool
    # La question irréductible du juge. Elle n'est pas la même selon qu'on parle
    # à un acheteur ou à quelqu'un qui en sait plus que soi.
    question_du_juge: str
    # Contexte relationnel utilisé par le rédacteur, indépendant du corpus.
    posture: str = "Contribuer utilement sans vendre ni supposer une relation préalable."
    policy_version: str = "conversation-v1"


_VENDRE_JUGE = (
    "Ce commentaire apporte-t-il vraiment quelque chose au lecteur, au-delà de ce que l'auteur a déjà "
    "écrit dans son post ? Un commentaire qui ressemble à une offre déguisée, même sans mot de vente "
    "explicite, n'apporte rien au lecteur : reject."
)

_VOIR_JUGE = (
    "L'auteur de ce post connaît le sujet mieux que celui qui commente. Une seule question compte : "
    "aurait-il envie de répondre à ce commentaire ? Rejette sans hésiter un commentaire qui lui "
    "réexplique ce qu'il sait déjà, qui résume son propre post, qui le corrige sur son terrain, ou qui "
    "cherche à impressionner. Un commentaire poli mais vide vaut moins que le silence."
)

WORLDS: dict[str, World] = {
    "icp1": World(
        id="icp1",
        label="Le consultant qui vit de sa production écrite (atelier 1)",
        role=WorldRole.VENDRE,
        rejette_actualite=False,
        question_du_juge=(
            "Le commentaire répond-il à un point précis de ce post avec naturel et respect, comme un pair ? "
            "Un accord développé, une appréciation précise ou une question sincère sont des contributions "
            "suffisantes. N'exige ni nouveauté spectaculaire, ni contradiction, ni question finale. "
            "Rejette les banalités interchangeables, l'offre déguisée, la leçon non sollicitée et les "
            "questions dont le post donne déjà la réponse. Une question concrète qui invite l'auteur à "
            "développer un choix est utile même si elle ne contient pas d'affirmation nouvelle."
        ),
        posture=(
            "Échanger entre pairs avec des consultants en Afrique francophone. S'intéresser à leur "
            "travail, leurs choix et leurs expériences. Le but immédiat est une conversation crédible, "
            "pas une preuve d'expertise ni une transition commerciale. Vouvoyer par défaut."
        ),
    ),
    "icp1bis": World(
        id="icp1bis",
        label="Le cadre en organisation, achète pour son équipe (atelier 1)",
        role=WorldRole.VENDRE,
        rejette_actualite=True,
        question_du_juge=_VENDRE_JUGE,
    ),
    "dev": World(
        id="dev",
        label="Le développeur qui utilise déjà Claude Code (atelier 2)",
        role=WorldRole.VENDRE,
        rejette_actualite=True,
        question_du_juge=_VENDRE_JUGE,
    ),
    # Le slug reprend celui de la catégorie déjà en base (table target_categories,
    # « Praticien IA »), pour qu'un monde de lecteur et une catégorie de cible
    # portent le même nom.
    "ai_practitioner": World(
        id="ai_practitioner",
        label="Praticiens IA suivis par veille, aucune intention commerciale",
        role=WorldRole.SE_FAIRE_VOIR,
        rejette_actualite=False,
        question_du_juge=_VOIR_JUGE,
    ),
}


def get_world(world_id: str) -> World | None:
    """Renvoie le monde déclaré, ou None. Un monde inconnu est une panne, pas un skip."""
    return WORLDS.get(world_id)


def known_world_ids() -> list[str]:
    return sorted(WORLDS)
