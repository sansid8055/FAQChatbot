"""Request/response models for §9 API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CreateThreadBody(BaseModel):
    session_key: str | None = Field(default=None, max_length=256)


class ThreadOut(BaseModel):
    id: str
    session_key: str | None = None
    created_at: str


class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: str
    retrieval_debug_id: str | None = None


class PostMessageBody(BaseModel):
    content: str = Field(..., min_length=1, max_length=16_000)
    expand_for_retrieval: bool = True


class PostMessageResponse(BaseModel):
    assistant_message: str
    user: MessageOut
    assistant: MessageOut
    debug: dict[str, Any] | None = None


class MessagesListResponse(BaseModel):
    thread_id: str
    messages: list[MessageOut]


class HealthResponse(BaseModel):
    status: str = "ok"
