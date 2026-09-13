import os
import logging
from contextlib import asynccontextmanager
from typing import Any
import json

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.infrastructure.observability.logging import configure_application_logging, log_json
from app.interfaces.api.routes_linkedin_comment_runs import router as linkedin_comment_runs_router
from app.config import settings

LOG_LEVEL_NAME = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_LEVEL = getattr(logging, LOG_LEVEL_NAME, logging.INFO)
configure_application_logging(LOG_LEVEL_NAME)

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)


@asynccontextmanager
async def lifespan(_: FastAPI):
    log_json(
        logger,
        "info",
        "runtime_bootstrap",
        ollama_url=settings.ollama_url,
        ollama_model=settings.ollama_model,
        postgres_configured=bool(settings.database_url),
        log_level=LOG_LEVEL_NAME,
    )
    yield


app = FastAPI(
    title="Pestel Nexus Engine",
    description="AI-driven content engine for source-grounded operational, editorial, and transformation content.",
    version="1.1.0",
    lifespan=lifespan,
)


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    raw_body: Any = exc.body
    if isinstance(raw_body, bytes):
        body_preview = raw_body.decode("utf-8", errors="replace")
    else:
        body_preview = json.dumps(raw_body, ensure_ascii=False, default=str)
    if len(body_preview) > 4000:
        body_preview = f"{body_preview[:4000]}...<truncated>"

    log_json(
        logger,
        "error",
        "request_validation_failed",
        method=request.method,
        path=request.url.path,
        query_params=str(request.query_params),
        validation_errors=exc.errors(),
        body_preview=body_preview,
    )
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/ping")
def ping():
    return {"status": "ok"}

app.include_router(linkedin_comment_runs_router)
