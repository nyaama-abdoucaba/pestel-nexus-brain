"""Le regard d'Abdoulaye : ses domaines, et les principes qui vivent dedans.

Refonte du 05/09/2026. Le moteur partait du corpus d'ancrages : il cherchait un
vécu à placer, puis une façon de l'insérer. Mesuré sur le feed consultant, le
sélecteur a refusé les ancrages 27 fois sur 27. Quinze faits datés ne couvrent
pas la diversité d'un fil d'actualité, et les recycler ferait dire la même chose
à tous les commentaires.

La chaîne part maintenant du post :

    le post touche-t-il un de mes domaines ?
        oui  -> un principe de ce domaine s'applique-t-il ?
                    oui  -> rédiger avec ce principe
                    non  -> rédiger en conversation
        non  -> rédiger en conversation

Un domaine décrit ce que quinze ans de métier permettent de VOIR. Il n'affirme
rien, donc il n'a rien à prouver. Les principes qu'il porte sont transposables :
ils s'appliquent à un post qu'Abdoulaye n'a jamais vécu, sans lui prêter aucune
expérience.

Le corpus d'ancrages (corpus.json) reste dans le dépôt mais ne nourrit plus la
rédaction. Énumérer une vie professionnelle dans une application est un autre
travail que celui de commenter.

Source des domaines : CV du 05/09/2026. Répartition des principes validée par
Abdoulaye le 05/09/2026.
"""

from __future__ import annotations

from dataclasses import dataclass

# Les douze principes transposables. Le libellé seul : les tags de situation qui
# servaient à atteindre un ancrage n'ont plus d'objet.
PRINCIPES: dict[str, str] = {
    "p1": "La forme validée n'est pas le fond validé.",
    "p2": "Une règle qui doit être garantie ne se demande pas, elle se contraint.",
    "p3": "Ce qui rend un dispositif utile, c'est le corpus réel, pas l'outil ni la méthode.",
    "p4": "Le standard échoue exactement là où vit le cas limite.",
    "p5": "Déléguer l'exécution, c'est perdre l'apprentissage.",
    "p6": "Un système ne doit pas arbitrer ce qu'il ne sait pas, il doit le signaler.",
    "p7": "La configuration se transmet, le prompt ne se transmet pas.",
    "p8": "Ce qui coince n'est presque jamais l'outil, c'est la procédure jamais rouverte.",
    "p9": "Un dossier n'est pas écarté sur le fond, il est écarté sur la conformité formelle.",
    "p10": "Le coût annoncé n'est pas le coût réel.",
    "p11": "Un titre individuel n'est pas un statut d'organisation.",
    "p12": "La vitesse d'un prototype ne dit rien de sa tenue en production.",
}


@dataclass(frozen=True)
class Domaine:
    id: str
    label: str
    # Formulé en « ce qu'il voit », jamais en « ce qu'il sait faire ». Un savoir
    # se vend, un regard se partage, et c'est un registre de conversation.
    regard: str
    principes: tuple[str, ...]
    mondes: tuple[str, ...]


DOMAINES: tuple[Domaine, ...] = (
    Domaine(
        id="strategie_pilotage",
        label="Stratégie et pilotage",
        regard="comment une décision se prépare, se priorise et se finance dans une administration "
               "ou une grande organisation",
        principes=("p3", "p4", "p10"),
        mondes=("icp1", "icp1bis"),
    ),
    Domaine(
        id="corporate_finance",
        label="Corporate finance",
        regard="comment un dossier se monte, ce qu'un investisseur regarde, pourquoi une valorisation "
               "se discute",
        principes=("p1", "p9", "p10"),
        mondes=("icp1", "icp1bis"),
    ),
    Domaine(
        id="transformation_organisations",
        label="Transformation des organisations",
        regard="où un processus se grippe, et ce qu'une procédure produit réellement une fois écrite",
        principes=("p2", "p4", "p6", "p7", "p8"),
        mondes=("icp1", "icp1bis", "dev"),
    ),
    Domaine(
        id="politiques_publiques",
        label="Politiques publiques et bailleurs",
        regard="comment un programme se cadre, s'évalue et se finance, et ce qu'un canevas impose "
               "à ceux qui y répondent",
        principes=("p9", "p11"),
        mondes=("icp1", "icp1bis"),
    ),
    Domaine(
        id="entrepreneuriat_startups",
        label="Entrepreneuriat et startups",
        regard="ce qui bloque au démarrage, et ce qu'un modèle économique tient ou ne tient pas",
        principes=("p5", "p10", "p12"),
        mondes=("icp1", "icp1bis", "dev"),
    ),
    Domaine(
        id="ingenierie_ia",
        label="Ingénierie IA appliquée",
        regard="ce qu'un modèle fait vraiment, où il casse, et ce que coûte le passage en production",
        principes=("p1", "p2", "p5", "p6", "p7", "p12"),
        mondes=("icp1", "icp1bis", "dev", "ai_practitioner"),
    ),
)

DOMAINES_PAR_ID: dict[str, Domaine] = {d.id: d for d in DOMAINES}


def domaines_pour(monde: str) -> list[Domaine]:
    """Les domaines crédibles devant ce lecteur, dans l'ordre de déclaration."""
    return [d for d in DOMAINES if monde in d.mondes]


def regard_en_texte(monde: str) -> str:
    return "\n".join(f"- {d.label} : {d.regard}." for d in domaines_pour(monde))


def principes_des_domaines(ids: list[str], monde: str) -> list[tuple[str, str]]:
    """Les principes portés par ces domaines, dédoublonnés, ordre de déclaration.

    Un principe appartient souvent à plusieurs domaines : p10 parle autant d'une
    mission de conseil que d'un business plan. On le propose une seule fois.
    """
    ouverts = {d.id for d in domaines_pour(monde)}
    vus: list[str] = []
    for did in ids:
        domaine = DOMAINES_PAR_ID.get(did)
        if domaine is None or domaine.id not in ouverts:
            continue
        for pid in domaine.principes:
            if pid not in vus:
                vus.append(pid)
    return [(pid, PRINCIPES[pid]) for pid in vus]
