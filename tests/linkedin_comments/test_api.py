from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.interfaces.api.routes_linkedin_comment_runs import router
from app.linkedin_comments.contracts import CommentRunResult, RunOutcome


def test_start_run_delegates_to_runtime(monkeypatch):
    post_id = uuid4()
    expected = CommentRunResult(
        linkedin_post_id=post_id,
        outcome=RunOutcome.SKIP,
        reason_code="promotional_only",
        reader_world="icp1",
        model="gemma4:31b-cloud",
        diagnostics=["promotional_only"],
    )
    captured = {}

    def fake_run(received_post_id, reader_world, budget):
        captured.update(post_id=received_post_id, reader_world=reader_world, budget=budget)
        return expected

    monkeypatch.setattr("app.interfaces.api.routes_linkedin_comment_runs.run_linkedin_comment", fake_run)
    app = FastAPI()
    app.include_router(router)

    response = TestClient(app).post(
        "/v1/linkedin-comment-runs",
        json={"linkedin_post_id": str(post_id), "reader_world": "icp1"},
    )

    assert response.status_code == 201
    assert response.json()["outcome"] == "skip"
    assert response.json()["reason_code"] == "promotional_only"
    assert captured["post_id"] == str(post_id)
    assert captured["reader_world"] == "icp1"


def test_start_run_returns_not_found(monkeypatch):
    from app.application.use_cases.run_linkedin_comment import LinkedInPostNotFound

    monkeypatch.setattr(
        "app.interfaces.api.routes_linkedin_comment_runs.run_linkedin_comment",
        lambda *_: (_ for _ in ()).throw(LinkedInPostNotFound("missing")),
    )
    app = FastAPI()
    app.include_router(router)

    response = TestClient(app).post(
        "/v1/linkedin-comment-runs",
        json={"linkedin_post_id": str(uuid4()), "reader_world": "icp1"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "LinkedIn post not found"


def test_start_run_requires_reader_world():
    app = FastAPI()
    app.include_router(router)

    response = TestClient(app).post(
        "/v1/linkedin-comment-runs",
        json={"linkedin_post_id": str(uuid4())},
    )

    assert response.status_code == 422
