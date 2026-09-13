from __future__ import annotations

from app.config import settings
from app.infrastructure.postgres.linkedin_comment_repository import PostgresLinkedInCommentRepository
from app.linkedin_comments.contracts import CommentRunResult, RevisionBudget
from app.linkedin_comments.llm_factory import build_llm_client
from app.linkedin_comments.runtime import LinkedInCommentRuntime


class LinkedInPostNotFound(ValueError):
    pass


def run_linkedin_comment(
    post_id: str,
    reader_world: str,
    budget: RevisionBudget | None = None,
) -> CommentRunResult:
    repository = PostgresLinkedInCommentRepository(settings.database_url)
    post = repository.load_post(post_id)
    if post is None:
        raise LinkedInPostNotFound(f"LinkedIn post {post_id} not found")
    client = build_llm_client(settings)
    runtime = LinkedInCommentRuntime(
        client,
        repository,
        analysis_max_tokens=settings.comment_analysis_max_tokens,
        writer_max_tokens=settings.comment_writer_max_tokens,
        judge_max_tokens=settings.comment_judge_max_tokens,
    )
    return runtime.run(post, reader_world, budget)
