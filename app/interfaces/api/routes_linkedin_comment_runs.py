from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.application.use_cases.run_linkedin_comment import LinkedInPostNotFound, run_linkedin_comment
from app.infrastructure.postgres.linkedin_comment_repository import PostgresCommentRepositoryError
from app.linkedin_comments.contracts import CommentRunResult, StartLinkedInCommentRun
from app.linkedin_comments.llm_errors import OllamaUnavailable

router = APIRouter(prefix="/v1", tags=["linkedin-comments"])


@router.post("/linkedin-comment-runs", response_model=CommentRunResult, status_code=201)
def start_linkedin_comment_run(request: StartLinkedInCommentRun) -> CommentRunResult:
    try:
        return run_linkedin_comment(str(request.linkedin_post_id), request.reader_world, request.budget)
    except LinkedInPostNotFound as exc:
        raise HTTPException(status_code=404, detail="LinkedIn post not found") from exc
    except OllamaUnavailable as exc:
        raise HTTPException(status_code=503, detail="Ollama unavailable") from exc
    except PostgresCommentRepositoryError as exc:
        raise HTTPException(status_code=503, detail="PostgreSQL unavailable") from exc
