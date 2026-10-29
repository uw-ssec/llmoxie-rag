"""RAG Agent implementation using pydantic-ai.

This module provides the RAG agent with structured output and tool calling.
"""

__all__ = [
    "RAGAgent",
    "RAGAgentDependencies",
    "Citation",
    "RAGResponse",
]

from llmoxie_rag.agent.rag_agent import RAGAgent, RAGAgentDependencies
from llmoxie_rag.agent.models import Citation, RAGResponse
