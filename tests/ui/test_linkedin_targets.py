from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

UI_PATH = Path(__file__).resolve().parent.parent.parent / "ui"
if str(UI_PATH) not in sys.path:
    sys.path.insert(0, str(UI_PATH))

from views.linkedin_targets import normalize_linkedin_url


# ── normalize_linkedin_url ────────────────────────────────────────────────────

class TestNormalizeLinkedInUrl:
    def test_removes_query_string(self):
        result = normalize_linkedin_url("https://www.linkedin.com/in/johndoe?trk=abc")
        assert "?" not in result
        assert "trk" not in result

    def test_removes_trailing_slash(self):
        result = normalize_linkedin_url("https://www.linkedin.com/in/johndoe/")
        assert not result.endswith("/")

    def test_normalizes_to_www(self):
        result = normalize_linkedin_url("https://fr.linkedin.com/in/johndoe")
        assert result == "https://www.linkedin.com/in/johndoe"

    def test_valid_profile(self):
        result = normalize_linkedin_url("https://www.linkedin.com/in/jane-doe")
        assert result == "https://www.linkedin.com/in/jane-doe"

    def test_http_accepted(self):
        result = normalize_linkedin_url("http://www.linkedin.com/in/johndoe")
        assert "linkedin.com/in/johndoe" in result

    def test_rejects_non_linkedin(self):
        with pytest.raises(ValueError):
            normalize_linkedin_url("https://www.google.com/search?q=test")

    def test_rejects_company_page(self):
        with pytest.raises(ValueError):
            normalize_linkedin_url("https://www.linkedin.com/company/acme")

    def test_rejects_post_url(self):
        with pytest.raises(ValueError):
            normalize_linkedin_url("https://www.linkedin.com/posts/johndoe_activity-123")

    def test_rejects_bare_linkedin_domain(self):
        with pytest.raises(ValueError):
            normalize_linkedin_url("https://www.linkedin.com/")

    def test_rejects_empty_slug(self):
        with pytest.raises(ValueError):
            normalize_linkedin_url("https://www.linkedin.com/in/")

    def test_strips_whitespace(self):
        result = normalize_linkedin_url("  https://www.linkedin.com/in/johndoe  ")
        assert result == "https://www.linkedin.com/in/johndoe"

    def test_rejects_empty_string(self):
        with pytest.raises(ValueError):
            normalize_linkedin_url("")


# ── Filtres SQL (via _targets_where) ─────────────────────────────────────────

def _targets_where(filters):
    from postgres import _targets_where as fn
    return fn(filters)


class TestTargetsWhere:
    def test_no_filters_returns_empty_where(self):
        sql, params = _targets_where({})
        assert sql == ""
        assert params == ()

    def test_search_adds_ilike_clauses(self):
        sql, params = _targets_where({"search": "Alice"})
        assert "ILIKE" in sql
        assert params == ("%Alice%", "%Alice%")

    def test_status_filter(self):
        sql, params = _targets_where({"status": "active"})
        assert "t.status = %s" in sql
        assert "active" in params

    def test_category_filter_uses_subquery(self):
        sql, params = _targets_where({"category": "ai_practitioner"})
        assert "linkedin_target_categories" in sql
        assert "ai_practitioner" in params

    def test_scrape_enabled_true(self):
        sql, params = _targets_where({"scrape_enabled": True})
        assert "scrape_enabled" in sql
        assert True in params

    def test_scrape_enabled_false(self):
        sql, params = _targets_where({"scrape_enabled": False})
        assert "scrape_enabled" in sql

    def test_combined_filters(self):
        sql, params = _targets_where({
            "search": "Bob",
            "status": "active",
            "category": "ai_practitioner",
        })
        assert "AND" in sql
        assert len(params) == 4

    def test_no_string_concatenation_in_params(self):
        sql, params = _targets_where({"status": "active"})
        # La valeur doit être dans les paramètres, pas concaténée dans le SQL
        assert "active" not in sql


# ── Transaction atomique pour la création ────────────────────────────────────

class TestCreateLinkedInTarget:
    def test_inserts_target_and_categories(self, monkeypatch):
        from postgres import create_linkedin_target

        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = {"id": "uuid-1"}

        with patch("postgres.transaction") as mock_tx:
            mock_tx.return_value.__enter__ = MagicMock(return_value=mock_cur)
            mock_tx.return_value.__exit__ = MagicMock(return_value=False)
            result = create_linkedin_target(
                {
                    "name": "Alice Dupont",
                    "linkedin_url": "https://www.linkedin.com/in/alice",
                    "status": "candidate",
                    "scrape_enabled": False,
                },
                category_slugs=["ai_practitioner"],
            )

        assert result == "uuid-1"
        calls = mock_cur.execute.call_args_list
        assert len(calls) == 2
        first_sql = calls[0][0][0]
        assert "INSERT INTO linkedin_targets" in first_sql
        second_sql = calls[1][0][0]
        assert "linkedin_target_categories" in second_sql

    def test_unique_violation_raises_ui_error(self):
        import psycopg
        from postgres import UiPostgresError, create_linkedin_target

        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_cur.execute.side_effect = psycopg.errors.UniqueViolation()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        with patch("postgres.get_connection", return_value=mock_conn):
            with pytest.raises(UiPostgresError, match="unique_violation"):
                create_linkedin_target(
                    {
                        "name": "Alice",
                        "linkedin_url": "https://www.linkedin.com/in/alice",
                        "status": "candidate",
                        "scrape_enabled": False,
                    },
                    category_slugs=["ai_practitioner"],
                )

    def test_default_status_is_candidate(self, monkeypatch):
        from postgres import create_linkedin_target

        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = {"id": "uuid-2"}

        with patch("postgres.transaction") as mock_tx:
            mock_tx.return_value.__enter__ = MagicMock(return_value=mock_cur)
            mock_tx.return_value.__exit__ = MagicMock(return_value=False)
            create_linkedin_target(
                {
                    "name": "Bob",
                    "linkedin_url": "https://www.linkedin.com/in/bob",
                },
                category_slugs=["ai_practitioner"],
            )

        insert_call = mock_cur.execute.call_args_list[0]
        params = insert_call[0][1]
        assert "candidate" in params
        assert False in params  # scrape_enabled = False par défaut


# ── Multi-catégorie sans duplication ─────────────────────────────────────────

class TestListLinkedInTargets:
    def test_multi_category_target_appears_once(self, monkeypatch):
        from postgres import list_linkedin_targets

        mock_row = {
            "id": "uuid-1",
            "name": "Alice",
            "linkedin_url": "https://www.linkedin.com/in/alice",
            "why_follow": None,
            "status": "active",
            "scrape_enabled": True,
            "last_scraped_at": None,
            "created_at": None,
            "updated_at": None,
            "metadata": None,
            "categories": "ai_practitioner, cxo",
        }
        with patch("postgres.fetchall", return_value=[mock_row]):
            rows = list_linkedin_targets({}, limit=10, offset=0)

        assert len(rows) == 1
        assert rows[0]["name"] == "Alice"
        assert "ai_practitioner" in rows[0]["categories"]
