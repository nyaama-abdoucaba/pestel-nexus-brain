from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any, Generator

import psycopg
from psycopg.rows import dict_row


class UiPostgresError(Exception):
    """Erreur de couche d'accès PostgreSQL, sans fuite des credentials."""


def _database_url() -> str:
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        raise UiPostgresError(
            "Variable d'environnement DATABASE_URL absente. "
            "Définissez-la avant de démarrer l'UI."
        )
    return url


def get_connection() -> psycopg.Connection:
    try:
        return psycopg.connect(_database_url(), row_factory=dict_row)
    except psycopg.OperationalError as exc:
        raise UiPostgresError(
            f"Impossible de se connecter à PostgreSQL : {exc.__class__.__name__}. "
            "Vérifiez que la base est démarrée et que DATABASE_URL est correcte."
        ) from exc


@contextmanager
def transaction() -> Generator[psycopg.Cursor, None, None]:
    conn = get_connection()
    try:
        with conn, conn.cursor() as cur:
            yield cur
    except psycopg.errors.UniqueViolation as exc:
        raise UiPostgresError("unique_violation") from exc
    except psycopg.Error as exc:
        raise UiPostgresError(f"Erreur base de données : {exc.__class__.__name__}.") from exc
    finally:
        conn.close()


def fetchall(sql: str, params: tuple | None = None) -> list[dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchall()  # type: ignore[return-value]


def fetchone(sql: str, params: tuple | None = None) -> dict[str, Any] | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchone()  # type: ignore[return-value]


# ── LinkedIn targets ─────────────────────────────────────────────────────────

def list_target_categories() -> list[dict[str, Any]]:
    return fetchall("SELECT slug, label FROM target_categories ORDER BY label")


def count_linkedin_targets(filters: dict[str, Any]) -> int:
    sql, params = _targets_where(filters)
    row = fetchone(f"SELECT COUNT(DISTINCT t.id) AS n FROM linkedin_targets t {sql}", params)
    return int(row["n"]) if row else 0


def list_linkedin_targets(
    filters: dict[str, Any], limit: int, offset: int
) -> list[dict[str, Any]]:
    where_sql, params = _targets_where(filters)
    sql = f"""
        SELECT
            t.id,
            t.name,
            t.linkedin_url,
            t.why_follow,
            t.status,
            t.scrape_enabled,
            t.last_scraped_at,
            t.created_at,
            t.updated_at,
            t.metadata,
            COALESCE(
                STRING_AGG(DISTINCT tc.category_slug, ', ' ORDER BY tc.category_slug),
                ''
            ) AS categories
        FROM linkedin_targets t
        LEFT JOIN linkedin_target_categories tc ON tc.linkedin_target_id = t.id
        {where_sql}
        GROUP BY t.id
        ORDER BY t.updated_at DESC NULLS LAST, t.id
        LIMIT %s OFFSET %s
    """
    return fetchall(sql, (*params, limit, offset))


def get_linkedin_target(target_id: str) -> dict[str, Any] | None:
    sql = """
        SELECT
            t.id,
            t.name,
            t.linkedin_url,
            t.why_follow,
            t.status,
            t.scrape_enabled,
            t.last_scraped_at,
            t.created_at,
            t.updated_at,
            t.metadata,
            COALESCE(
                STRING_AGG(DISTINCT tc.category_slug, ', ' ORDER BY tc.category_slug),
                ''
            ) AS categories
        FROM linkedin_targets t
        LEFT JOIN linkedin_target_categories tc ON tc.linkedin_target_id = t.id
        WHERE t.id = %s
        GROUP BY t.id
    """
    return fetchone(sql, (target_id,))


def create_linkedin_target(data: dict[str, Any], category_slugs: list[str]) -> str:
    with transaction() as cur:
        cur.execute(
            """
            INSERT INTO linkedin_targets
                (name, linkedin_url, why_follow, status, scrape_enabled)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                data["name"],
                data["linkedin_url"],
                data.get("why_follow") or None,
                data.get("status", "candidate"),
                data.get("scrape_enabled", False),
            ),
        )
        row = cur.fetchone()
        target_id = row["id"]
        for slug in category_slugs:
            cur.execute(
                """
                INSERT INTO linkedin_target_categories (linkedin_target_id, category_slug)
                VALUES (%s, %s)
                """,
                (str(target_id), slug),
            )
    return str(target_id)


def _targets_where(filters: dict[str, Any]) -> tuple[str, tuple]:
    clauses: list[str] = []
    params: list[Any] = []

    if filters.get("search"):
        clauses.append("(t.name ILIKE %s OR t.linkedin_url ILIKE %s)")
        like = f"%{filters['search']}%"
        params.extend([like, like])

    if filters.get("status"):
        clauses.append("t.status = %s")
        params.append(filters["status"])

    if filters.get("category"):
        clauses.append(
            "EXISTS (SELECT 1 FROM linkedin_target_categories x "
            "WHERE x.linkedin_target_id = t.id AND x.category_slug = %s)"
        )
        params.append(filters["category"])

    if filters.get("scrape_enabled") is not None:
        clauses.append("t.scrape_enabled = %s")
        params.append(filters["scrape_enabled"])

    sql = "WHERE " + " AND ".join(clauses) if clauses else ""
    return sql, tuple(params)


# ── LinkedIn posts ────────────────────────────────────────────────────────────

def list_post_statuses() -> list[str]:
    rows = fetchall("SELECT DISTINCT status FROM linkedin_posts WHERE status IS NOT NULL ORDER BY status")
    return [r["status"] for r in rows]


def count_linkedin_posts(filters: dict[str, Any]) -> int:
    sql, params = _posts_where(filters)
    row = fetchone(f"SELECT COUNT(DISTINCT p.id) AS n FROM linkedin_posts p JOIN linkedin_targets t ON t.id = p.linkedin_target_id {sql}", params)
    return int(row["n"]) if row else 0


def list_linkedin_posts(
    filters: dict[str, Any], limit: int, offset: int
) -> list[dict[str, Any]]:
    where_sql, params = _posts_where(filters)
    sql = f"""
        SELECT
            p.id,
            p.linkedin_target_id,
            p.url,
            p.text,
            p.posted_at,
            p.observed_at,
            p.status,
            p.created_at,
            p.updated_at,
            t.name AS author_name,
            t.linkedin_url AS author_linkedin_url
        FROM linkedin_posts p
        JOIN linkedin_targets t ON t.id = p.linkedin_target_id
        {where_sql}
        GROUP BY p.id, t.name, t.linkedin_url
        ORDER BY p.posted_at DESC NULLS LAST, p.observed_at DESC, p.id
        LIMIT %s OFFSET %s
    """
    return fetchall(sql, (*params, limit, offset))


def get_linkedin_post(post_id: str) -> dict[str, Any] | None:
    sql = """
        SELECT
            p.id,
            p.linkedin_target_id,
            p.url,
            p.text,
            p.posted_at,
            p.observed_at,
            p.status,
            p.raw_payload,
            p.created_at,
            p.updated_at,
            t.name AS author_name,
            t.linkedin_url AS author_linkedin_url
        FROM linkedin_posts p
        JOIN linkedin_targets t ON t.id = p.linkedin_target_id
        WHERE p.id = %s
    """
    return fetchone(sql, (post_id,))


def _posts_where(filters: dict[str, Any]) -> tuple[str, tuple]:
    clauses: list[str] = []
    params: list[Any] = []

    if filters.get("search"):
        clauses.append("(p.text ILIKE %s OR t.name ILIKE %s)")
        like = f"%{filters['search']}%"
        params.extend([like, like])

    if filters.get("author_id"):
        clauses.append("p.linkedin_target_id = %s")
        params.append(filters["author_id"])

    if filters.get("category"):
        clauses.append(
            "EXISTS (SELECT 1 FROM linkedin_target_categories x "
            "WHERE x.linkedin_target_id = t.id AND x.category_slug = %s)"
        )
        params.append(filters["category"])

    if filters.get("status"):
        clauses.append("p.status = %s")
        params.append(filters["status"])

    if filters.get("date_from"):
        clauses.append("p.posted_at >= %s")
        params.append(filters["date_from"])

    if filters.get("date_to"):
        clauses.append("p.posted_at <= %s")
        params.append(filters["date_to"])

    sql = "WHERE " + " AND ".join(clauses) if clauses else ""
    return sql, tuple(params)
