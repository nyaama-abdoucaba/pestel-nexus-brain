from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_linkedin_target_urls_accept_profiles_pages_and_schools():
    schema = (REPO_ROOT / "db" / "init" / "010_linkedin_targets.sql").read_text()
    migration = (
        REPO_ROOT / "db" / "migrations" / "2026-09-02-linkedin-target-url-kinds.sql"
    ).read_text()

    expected_pattern = "(in|company|school)/[^/?#]+/?$"

    assert expected_pattern in schema
    assert expected_pattern in migration
