"""FastAPI application: §9 HTTP API (rag-architecture.md §9); UI lives in ``web/`` (Next.js)."""

from __future__ import annotations

import json
import logging
import secrets
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ingest.repo_dotenv import load_repo_dotenv

load_repo_dotenv()

from runtime.phase_8_threads.store import (
    create_thread,
    get_thread,
    list_messages,
    list_threads,
    thread_exists,
)
from runtime.phase_9_api.config import admin_reindex_secret, api_debug_enabled
from runtime.phase_9_api.schemas import (
    CreateThreadBody,
    HealthResponse,
    MessageOut,
    MessagesListResponse,
    PostMessageBody,
    PostMessageResponse,
    ThreadOut,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    from runtime.phase_8_threads.store import ensure_schema

    ensure_schema()
    try:
        import groq  # noqa: F401
    except ModuleNotFoundError:
        logger.warning(
            "Package 'groq' is not installed — factual RAG replies will fail until you run: pip install groq"
        )
    yield


app = FastAPI(
    title="MF FAQ runtime API",
    description="Application layer (rag-architecture.md §9) over phase 8 threads + phase 7 RAG.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _msg_out(m, *, include_retrieval_debug: bool) -> MessageOut:
    return MessageOut(
        id=m.id,
        role=m.role,
        content=m.content,
        created_at=m.created_at,
        retrieval_debug_id=m.retrieval_debug_id if include_retrieval_debug else None,
    )


@app.get("/health", response_model=HealthResponse, tags=["health"])
def health() -> HealthResponse:
    return HealthResponse()


@app.get("/threads", response_model=list[ThreadOut], tags=["threads"])
def get_threads(session_key: str | None = Query(default=None, max_length=256)) -> list[ThreadOut]:
    """List threads (newest first); supports §8.4 thread list UI."""
    return [
        ThreadOut(id=t.id, session_key=t.session_key, created_at=t.created_at)
        for t in list_threads(session_key=session_key)
    ]


@app.post("/threads", response_model=ThreadOut, tags=["threads"])
def post_thread(body: CreateThreadBody | None = None) -> ThreadOut:
    body = body or CreateThreadBody()
    tid = create_thread(session_key=body.session_key)
    t = get_thread(tid)
    if not t:
        raise HTTPException(status_code=500, detail="thread created but not readable")
    return ThreadOut(id=t.id, session_key=t.session_key, created_at=t.created_at)


@app.get("/threads/{thread_id}/messages", response_model=MessagesListResponse, tags=["threads"])
def get_thread_messages(thread_id: str) -> MessagesListResponse:
    if not thread_exists(thread_id):
        raise HTTPException(status_code=404, detail="thread not found")
    dbg = api_debug_enabled()
    msgs = [_msg_out(m, include_retrieval_debug=dbg) for m in list_messages(thread_id)]
    return MessagesListResponse(thread_id=thread_id, messages=msgs)


@app.post("/threads/{thread_id}/messages", response_model=PostMessageResponse, tags=["threads"])
def post_thread_message(
    thread_id: str,
    body: PostMessageBody,
    allow_pii_queries: bool = Query(default=False),
) -> PostMessageResponse:
    if not thread_exists(thread_id):
        raise HTTPException(status_code=404, detail="thread not found")
    from runtime.phase_8_threads.chat_service import post_user_message

    t0 = time.perf_counter()
    try:
        user_row, asst_row = post_user_message(
            thread_id,
            body.content,
            expand_for_retrieval=body.expand_for_retrieval,
            block_on_pii_in_query=not allow_pii_queries,
        )
    except ModuleNotFoundError as e:
        if getattr(e, "name", None) == "groq":
            raise HTTPException(
                status_code=503,
                detail=(
                    "Optional dependency 'groq' is not installed. "
                    "Run: pip install groq   (or pip install -r requirements.txt)"
                ),
            ) from e
        raise HTTPException(status_code=500, detail=str(e)) from e
    except ValueError as e:
        if str(e) == "GROQ_API_KEY is not set":
            raise HTTPException(
                status_code=503,
                detail="GROQ_API_KEY is not set in the environment (see .env.example).",
            ) from e
        raise HTTPException(status_code=500, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
    dbg = api_debug_enabled()
    user_out = _msg_out(user_row, include_retrieval_debug=dbg)
    asst_out = _msg_out(asst_row, include_retrieval_debug=dbg)
    debug_block: dict | None = None
    if dbg:
        gen: dict = {}
        if asst_row.retrieval_debug_id:
            try:
                gen = json.loads(asst_row.retrieval_debug_id)
            except json.JSONDecodeError:
                gen = {"raw": asst_row.retrieval_debug_id}
        debug_block = {
            "latency_ms": elapsed_ms,
            "generation": gen,
            "note": "Chunk IDs/scores not yet wired; enable when retriever exposes them (§9.2).",
        }
    return PostMessageResponse(
        assistant_message=asst_row.content,
        user=user_out,
        assistant=asst_out,
        debug=debug_block,
    )


@app.post("/admin/reindex", tags=["admin"])
def admin_reindex(authorization: str | None = Header(default=None)) -> dict:
    """
    Optional protected stub (§9.1). Ingest is run via CLI or GitHub Actions (rag §4);
    successful auth returns 501 with guidance.
    """
    secret = admin_reindex_secret()
    if not secret:
        raise HTTPException(
            status_code=503,
            detail="Admin reindex disabled (set ADMIN_REINDEX_SECRET to enable).",
        )
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.removeprefix("Bearer ").strip()
    if not secrets.compare_digest(token, secret):
        raise HTTPException(status_code=401, detail="Invalid token")
    raise HTTPException(
        status_code=501,
        detail={
            "message": "Reindex trigger not implemented in-process.",
            "hint": "Run ingest pipeline: python -m ingest.phases.phase_4_0_scheduler_scraping or GitHub Actions workflow.",
        },
    )


@app.get("/", include_in_schema=False)
def root() -> JSONResponse:
    """API root; run the Next.js UI from ``web/`` (see ``web/README.md``)."""
    return JSONResponse(
        {
            "service": "mf-faq-runtime-api",
            "docs": "/docs",
            "openapi": "/openapi.json",
            "health": "/health",
            "ui": (
                "Next.js app in repository folder `web/`: "
                "`cd web && npm install && cp .env.local.example .env.local` "
                "(set NEXT_PUBLIC_API_URL to this API origin, e.g. http://127.0.0.1:8765) "
                "then `npm run dev`."
            ),
        }
    )
