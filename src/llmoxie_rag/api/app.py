"""FastAPI application serving the agentic RAG endpoints.

Routes match the ones llmoxie served: ``/v1/agentic/chat`` and
``/v1/agentic/retrieve``.
"""

from __future__ import annotations

from fastapi import APIRouter, FastAPI

from llmoxie_rag.api import agentic_chat, agentic_retrieve

app = FastAPI(title="LLMoxie RAG")

v1_router = APIRouter(prefix="/v1")
v1_router.include_router(agentic_retrieve.router)
v1_router.include_router(agentic_chat.router)

app.include_router(v1_router)
