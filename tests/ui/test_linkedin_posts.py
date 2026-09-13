from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

UI_PATH = Path(__file__).resolve().parent.parent.parent / "ui"
if str(UI_PATH) not in sys.path:
    sys.path.insert(0, str(UI_PATH))


# ── Filtres SQL (_posts_where) ────────────────────────────────────────────────

def _posts_where(filters):
    from postgres import _posts_where as fn
    return fn(filters)


class TestPostsWhere:
    def test_no_filters(self):
        sql, params = _posts_where({})
        assert sql == ""
        assert params == ()

    def test_search_filter(self):
        sql, params = _posts_where({"search": "IA"})
        assert "ILIKE" in sql
        assert "%IA%" in params

    def test_author_filter(self):
        sql, params = _posts_where({"author_id": "uuid-1"})
        assert "linkedin_target_id" in sql
        assert "uuid-1" in params

    def test_category_filter_uses_subquery(self):
        sql, params = _posts_where({"category": "ai_practitioner"})
        assert "linkedin_target_categories" in sql
        assert "ai_practitioner" in params

    def test_status_filter(self):
        sql, params = _posts_where({"status": "observed"})
        assert "p.status = %s" in sql
        assert "observed" in params

    def test_date_from_filter(self):
        from datetime import date
        sql, params = _posts_where({"date_from": date(2026, 1, 1)})
        assert "posted_at >=" in sql

    def test_date_to_filter(self):
        from datetime import date
        sql, params = _posts_where({"date_to": date(2026, 12, 31)})
        assert "posted_at <=" in sql

    def test_combined_search_and_status(self):
        sql, params = _posts_where({"search": "IA", "status": "observed"})
        assert "AND" in sql
        assert len(params) == 3


# ── Valeurs facultatives ──────────────────────────────────────────────────────

class TestListLinkedInPosts:
    def _make_row(self, **overrides):
        base = {
            "id": "uuid-p1",
            "linkedin_target_id": "uuid-t1",
            "url": "https://www.linkedin.com/posts/alice_123",
            "text": "Contenu du post",
            "posted_at": None,
            "observed_at": None,
            "status": "observed",
            "created_at": None,
            "updated_at": None,
            "author_name": "Alice",
            "author_linkedin_url": "https://www.linkedin.com/in/alice",
        }
        base.update(overrides)
        return base

    def test_post_without_posted_at(self):
        from postgres import list_linkedin_posts
        row = self._make_row(posted_at=None)
        with patch("postgres.fetchall", return_value=[row]):
            rows = list_linkedin_posts({}, limit=10, offset=0)
        assert rows[0]["posted_at"] is None

    def test_post_without_raw_payload_handled_by_get(self):
        from postgres import get_linkedin_post
        row = {**self._make_row(), "raw_payload": None}
        with patch("postgres.fetchone", return_value=row):
            post = get_linkedin_post("uuid-p1")
        assert post["raw_payload"] is None

    def test_multi_category_author_does_not_duplicate_post(self):
        from postgres import list_linkedin_posts
        row = self._make_row()
        with patch("postgres.fetchall", return_value=[row]):
            rows = list_linkedin_posts({"category": "ai_practitioner"}, limit=10, offset=0)
        assert len(rows) == 1

    def test_url_returned_as_string(self):
        from postgres import list_linkedin_posts
        row = self._make_row(url="https://www.linkedin.com/posts/alice_123")
        with patch("postgres.fetchall", return_value=[row]):
            rows = list_linkedin_posts({}, limit=10, offset=0)
        assert isinstance(rows[0]["url"], str)

    def test_text_returned_unchanged(self):
        original = "Bonjour\nMonde"
        from postgres import list_linkedin_posts
        row = self._make_row(text=original)
        with patch("postgres.fetchall", return_value=[row]):
            rows = list_linkedin_posts({}, limit=10, offset=0)
        assert rows[0]["text"] == original


# ── Source Items absent après UIPOSTS ────────────────────────────────────────

def test_source_items_removed_from_navigation():
    import ast
    app_source = (UI_PATH / "app.py").read_text()
    tree = ast.parse(app_source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "VIEWS":
                    keys = [
                        k.value if isinstance(k, ast.Constant) else ""
                        for k in node.value.keys
                    ]
                    assert "Posts LinkedIn" in keys, "Posts LinkedIn doit être dans VIEWS"
                    return
    pytest.fail("VIEWS dict not found in app.py")
