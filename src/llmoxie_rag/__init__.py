"""Agentic RAG system for LLMaven.

This package provides advanced RAG capabilities with multi-vector embeddings
(Dense, Sparse, ColBERT) and hybrid search using Qdrant Named Vectors.
"""

__all__ = [
    "config",
    "AgenticRAGError",
    "QdrantManager",
    "IngestionPipeline",
    "HybridSearcher",
    "SearchResult",
    "RAGAgent",
    "RAGResponse",
    "Citation",
]

from llmoxie_rag.settings import config
from llmoxie_rag.exceptions import AgenticRAGError
from llmoxie_rag.vector_store import QdrantManager
from llmoxie_rag.ingestion import IngestionPipeline
from llmoxie_rag.search import HybridSearcher
from llmoxie_rag.search.models import SearchResult
from llmoxie_rag.agent import RAGAgent
from llmoxie_rag.agent.models import RAGResponse, Citation
