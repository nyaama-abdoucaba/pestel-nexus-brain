"""Dry-run — livrable n°5 de la mission.

Fait tourner le moteur sur des posts déjà archivés et sort le décompte
draft / skip / error, ainsi que les brouillons produits.

Usage :
    python -m app.linkedin_comments.dry_run --world icp1 --fixtures
    python -m app.linkedin_comments.dry_run --world icp1 --db --limit 20

--fixtures (par défaut) lit app/linkedin_comments/fixtures/archived_posts_sample.json
— voir fixtures/README.md : un seul post y est réel, les autres sont des
gabarits synthétiques pour un test de fumée multi-post_type.

--db interroge PostgreSQL (nécessite DATABASE_URL et une table linkedin_posts
déjà peuplée) : c'est le seul mode qui peut effectivement vérifier le critère
d'acceptation de la mission (trois brouillons publiables tels quels, sur de
vrais posts francophones du feed cible).

Un monde de lecteur (--world) s'applique à tout le lot : un dry-run porte
normalement sur un seul monde de lecteur à la fois ; la liste des mondes
déclarés vit dans worlds.py.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from uuid import UUID

from app.config import settings
from app.linkedin_comments.contracts import CommentRunResult, LinkedInPost, RunOutcome
from app.linkedin_comments.llm_factory import build_llm_client
from app.linkedin_comments.runtime import LinkedInCommentRuntime
from app.linkedin_comments.worlds import known_world_ids

FIXTURES_PATH = Path(__file__).parent / "fixtures" / "archived_posts_sample.json"


class _NullRepository:
    """Un dry-run n'écrit rien en base : le résultat reste en mémoire pour l'affichage."""

    def save(self, result: CommentRunResult) -> None:
        pass


def _load_fixture_posts(path: Path) -> list[LinkedInPost]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [
        LinkedInPost(id=UUID(item["id"]), text=item["text"], url=item.get("url"), author_name=item.get("author_name"))
        for item in raw
    ]


def _load_db_posts(limit: int, category: str | None = None, observed_date: date | None = None) -> list[LinkedInPost]:
    import psycopg
    from psycopg.rows import dict_row

    if not settings.database_url:
        raise SystemExit("DATABASE_URL est absente : impossible de lire les posts archivés depuis PostgreSQL.")
    with psycopg.connect(settings.database_url, row_factory=dict_row) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT p.id, p.text, p.url, t.name AS author_name
                FROM linkedin_posts p
                JOIN linkedin_targets t ON t.id = p.linkedin_target_id
                WHERE (%s::text IS NULL OR EXISTS (
                    SELECT 1 FROM linkedin_target_categories c
                    WHERE c.linkedin_target_id = t.id AND c.category_slug = %s
                ))
                AND (%s::date IS NULL OR (p.observed_at >= %s::date AT TIME ZONE 'UTC'
                    AND p.observed_at < (%s::date + 1) AT TIME ZONE 'UTC'))
                ORDER BY p.posted_at DESC NULLS LAST, p.id
                LIMIT %s
                """,
                (category, category, observed_date, observed_date, observed_date, limit),
            )
            rows = cursor.fetchall()
    return [LinkedInPost.model_validate(row) for row in rows]


def _print_verbose(post: LinkedInPost, result: CommentRunResult) -> None:
    indent = "    "
    if result.analysis is not None:
        a = result.analysis
        print(f"{indent}analyse: decision={a.decision} post_type={a.post_type} "
              f"langue={a.source_language.value} domaines={a.domaines} "
              f"skip_reason={a.skip_reason}")
    for record in result.revisions:
        print(f"{indent}tentative {record.attempt}:")
        if record.draft is not None:
            print(f"{indent}  brouillon: {record.draft.comment!r}")
            print(f"{indent}  langue déclarée={record.draft.language.value}")
        if record.control_violations:
            print(f"{indent}  violations de contrôle: {record.control_violations}")
        else:
            print(f"{indent}  contrôles: OK")
        if record.judge is not None:
            j = record.judge
            print(f"{indent}  juge: decision={j.decision} reasons={j.reasons} "
                  f"rewrite_instructions={j.rewrite_instructions}")
    if result.diagnostics:
        print(f"{indent}diagnostics: {result.diagnostics}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Dry-run du moteur de commentaires LinkedIn.")
    parser.add_argument(
        "--world", required=True,
        help=f"Monde du lecteur pour ce lot. Mondes déclarés : {', '.join(known_world_ids())}.",
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--fixtures", metavar="PATH", nargs="?", const=str(FIXTURES_PATH), default=None,
                         help="Lit les posts d'un fichier JSON (défaut si aucune source n'est précisée).")
    source.add_argument("--db", action="store_true", help="Lit les posts déjà archivés dans PostgreSQL.")
    parser.add_argument("--limit", type=int, default=20, help="Nombre de posts à traiter (mode --db uniquement).")
    parser.add_argument(
        "--verbose", action="store_true",
        help="Affiche pour chaque post : tags de l'analyseur, candidats présélectionnés, choix du "
             "sélecteur, chaque brouillon avec ses violations de contrôle, et le verdict du juge. "
             "À utiliser pour diagnostiquer un lot qui ne produit aucun draft.",
    )
    parser.add_argument("--category", help="Catégorie PostgreSQL, indépendante du monde éditorial.")
    parser.add_argument("--observed-date", type=date.fromisoformat, help="Date de collecte UTC (YYYY-MM-DD).")
    parser.add_argument("--output", type=Path, help="Rapport JSON complet, écrit après chaque post.")
    args = parser.parse_args()
    if args.world not in known_world_ids():
        parser.error("Monde inconnu : " + args.world)
    if args.limit < 1:
        parser.error("--limit doit être positif")
    if not args.db and (args.category or args.observed_date):
        parser.error("--category et --observed-date nécessitent --db")

    if args.db:
        posts = _load_db_posts(args.limit, args.category, args.observed_date)
    else:
        posts = _load_fixture_posts(Path(args.fixtures or FIXTURES_PATH))

    if not posts:
        print("Aucun post à traiter.")
        return

    client = build_llm_client(settings)
    print(f"Transport LLM : {settings.llm_transport}  ({client.__class__.__name__})\n")
    runtime = LinkedInCommentRuntime(
        client,
        _NullRepository(),
        analysis_max_tokens=settings.comment_analysis_max_tokens,
        writer_max_tokens=settings.comment_writer_max_tokens,
        judge_max_tokens=settings.comment_judge_max_tokens,
    )

    counts = {RunOutcome.DRAFT: 0, RunOutcome.SKIP: 0, RunOutcome.ERROR: 0}
    drafts: list[tuple[LinkedInPost, CommentRunResult]] = []

    report = []
    for post in posts:
        result = runtime.run(post, reader_world=args.world)
        counts[result.outcome] += 1
        report.append({"post": post.model_dump(mode="json"), "result": result.model_dump(mode="json")})
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[{result.outcome.value:5}] {(post.author_name or '?'):18.18} "
              f"mode={result.comment_mode or '-':8} reason={result.reason_code or '-'}")
        if args.verbose:
            _print_verbose(post, result)
        if result.outcome == RunOutcome.DRAFT:
            drafts.append((post, result))

    print()
    print(
        f"draft={counts[RunOutcome.DRAFT]}  skip={counts[RunOutcome.SKIP]}  "
        f"error={counts[RunOutcome.ERROR]}  total={len(posts)}"
    )
    print()

    if drafts:
        print("--- brouillons produits ---")
        for post, result in drafts:
            print(f"\nPost {post.id} ({post.author_name or 'auteur inconnu'}) :")
            preview = post.text[:200] + ("..." if len(post.text) > 200 else "")
            print(f"  {preview}")
            print(f"  -> {result.comment_text}")
            post_type = result.post_type.value if result.post_type else "-"
            print(f"  (post_type={post_type}, mode={result.comment_mode}, domaines={result.domaines})")
    else:
        print("Aucun brouillon produit sur ce lot.")


if __name__ == "__main__":
    main()
