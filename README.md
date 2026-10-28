# llmoxie-rag

Agentic retrieval-augmented generation (RAG) over your documents, with
multi-vector hybrid search in [Qdrant](https://qdrant.tech/). Extracted from
[uw-ssec/llmoxie](https://github.com/uw-ssec/llmoxie), which now focuses on the
LiteLLM gateway and MLflow observability platform.

**Roadmap:** this package will grow into a standalone MCP search service
([uw-ssec/llmoxie#72](https://github.com/uw-ssec/llmoxie/issues/72)).

## Prerequisites

This project uses [Pixi](https://pixi.sh) for dependency management and task
execution. Install Pixi by following the
[installation instructions](https://pixi.sh/latest/#installation).

## Getting Started

### GitHub Codespaces / Dev Containers

The repository ships a [`.devcontainer/`](.devcontainer/) configuration. Open it
in GitHub Codespaces (or VS Code Dev Containers) to get a container with Pixi
and the Claude Code, Codex, Copilot CLI, and OpenCode agent CLIs preinstalled;
the Pixi environment is installed and auto-activated on first start.

### Installation

Install dependencies:

```bash
# Install dependencies (Pixi will automatically create the environment)
pixi install
```

### Onboarding

For first-time setup, use the onboarding environment to configure your
development environment:

```bash
pixi run -e onboard onboard
```

This will:

- Install pre-commit hooks in your git repository
- Set up shell completion for ssec-cli
- Run the SSEC onboarding process

## Quickstart

```bash
pixi install                      # installs llmoxie-rag in the default environment
docker compose up -d qdrant       # Qdrant on http://localhost:6333

export AGENTIC_LLM_PROVIDER=openai OPENAI_API_KEY=...   # or see Configuration Options
pixi run llmoxie-rag ingest ./docs
pixi run llmoxie-rag search "What is machine learning?"
pixi run llmoxie-rag chat
```

The HTTP API serves `POST /v1/agentic/retrieve` and `POST /v1/agentic/chat`:

```bash
pixi run uvicorn llmoxie_rag.api.app:app --reload
```

Tests: `pixi run test` (needs Docker for the Qdrant testcontainer) and
`pixi run test-cli`.

## Agentic RAG System

The Agentic RAG system is a next-generation retrieval and question-answering
system that combines hybrid search (Dense + Sparse + ColBERT) with intelligent
agent-based answer generation. It provides superior retrieval accuracy compared
to single-vector search.

### Architecture Overview

The agentic RAG system consists of four main components:

1. **Ingestion Pipeline** (`src/llmoxie_rag/ingestion/pipeline.py`)
   - Multi-format document processing with `docling`
   - Intelligent chunking that preserves document structure
   - Multi-vector embedding generation (Dense, Sparse, ColBERT)
   - Batch processing with progress indicators

2. **Vector Store** (`src/llmoxie_rag/vector_store/qdrant_manager.py`)
   - Qdrant Named Vectors support
   - Collection management and validation
   - Hybrid search operations

3. **Hybrid Search** (`src/llmoxie_rag/search/hybrid_searcher.py`)
   - Three-stage search pipeline:
     - **Prefetch**: Parallel Dense + Sparse vector queries
     - **Rerank**: Optional ColBERT MaxSim reranking
   - Configurable top-K parameters
   - Score metadata tracking

4. **RAG Agent** (`src/llmoxie_rag/agent/rag_agent.py`)
   - Pydantic-AI based agent with structured output
   - Citation support with relevance scores
   - Multi-provider LLM support (OpenAI, Ollama, LiteLLM, Azure OpenAI,
     HuggingFace)
   - Message history for multi-turn conversations

### Usage Examples

#### CLI Commands

**Ingest Documents:**

```bash
# Ingest documents from a directory
llmoxie-rag ingest ./docs

# Ingest from multiple directories with custom collection
llmoxie-rag ingest ./docs ./papers --collection research-docs

# Force overwrite existing collection
llmoxie-rag ingest ./docs --force

# Custom batch size
llmoxie-rag ingest ./docs --batch-size 50
```

**Search Knowledge Base:**

```bash
# Basic hybrid search
llmoxie-rag search "What is machine learning?"

# Search with custom top-k
llmoxie-rag search "transformer architecture" --top-k 10

# Search without reranking (faster)
llmoxie-rag search "vector embeddings" --no-rerank

# Search specific collection
llmoxie-rag search "query" --collection my-collection
```

**Interactive Chat:**

```bash
# Start interactive RAG chat
llmoxie-rag chat

# Chat with custom collection
llmoxie-rag chat --collection my-docs

# Use different LLM provider
llmoxie-rag chat --provider ollama --model llama2

# Route through the local LiteLLM proxy
llmoxie-rag chat --provider litellm --litellm-base http://localhost:4000 --model gpt-4o-mini
```

#### Python API Usage

```python
from llmoxie_rag import RAGAgent, HybridSearcher, IngestionPipeline

# Ingest documents
pipeline = IngestionPipeline(collection_name="docs")
pipeline.ingest(directories=["./docs"], force=True)

# Search
searcher = HybridSearcher(collection_name="docs")
results = searcher.search("What is machine learning?", limit=5)

# Chat with agent
agent = RAGAgent(collection_name="docs")
response = agent.run_sync("Explain transformers")
print(response.answer)
for citation in response.citations:
    print(f"- {citation.source_file}: {citation.relevance_score}")
```

### Configuration Options

The agentic RAG system uses environment variables with the `AGENTIC_` prefix:

**Qdrant Configuration:**

```bash
AGENTIC_QDRANT_URL=http://localhost:6333
AGENTIC_QDRANT_API_KEY=your-api-key  # Optional
AGENTIC_COLLECTION_NAME=agentic-rag
```

**Embedding Models:**

```bash
AGENTIC_DENSE_MODEL=sentence-transformers/all-MiniLM-L6-v2
AGENTIC_SPARSE_MODEL=Qdrant/bm25
AGENTIC_COLBERT_MODEL=colbert-ir/colbertv2.0
```

**LLM Configuration:**

```bash
AGENTIC_LLM_PROVIDER=openai  # Options: openai, ollama, litellm, azure, huggingface
AGENTIC_LLM_MODEL=gpt-4o-mini
AGENTIC_HUGGINGFACE_MODEL=optional-local-model

# litellm provider
AGENTIC_LITELLM_API_BASE=http://localhost:4000
AGENTIC_LITELLM_API_KEY=your-key
AGENTIC_LITELLM_MODEL_PREFIX=openai/  # Optional

# azure provider
AGENTIC_AZURE_ENDPOINT=https://<resource>.openai.azure.com
AGENTIC_AZURE_API_KEY=your-key
AGENTIC_AZURE_DEPLOYMENT_NAME=gpt-4o
AGENTIC_AZURE_API_VERSION=2024-10-21
```

**Search Configuration:**

```bash
AGENTIC_ENABLE_RERANK=true
AGENTIC_PREFETCH_TOP_K=20
AGENTIC_FINAL_TOP_K=5
```


## Project Structure

This project is organized using Pixi features for modular dependency management:

- **`rag`**: The `llmoxie-rag` package (editable, with its test extra) and the
  `test` / `test-cli` tasks
- **`pre-commit`**: Code quality and consistency checks
- **`gh-cli`**: GitHub CLI for repository interactions
- **`okf`**: The `okf` CLI for reading and writing project memory in
  `knowledge/`
- **`onboard`**: Tools for project onboarding and setup

## Available Environments

- **`default`**: Standard development environment with `llmoxie-rag`, pre-commit
  hooks, GitHub CLI, and the `okf` CLI
- **`onboard`**: Extended environment including onboarding tools

## Development

### Using Different Environments

Switch between environments as needed:

```bash
# Use default environment
pixi shell

# Use onboard environment
pixi shell -e onboard
```

### Adding Dependencies

Conda packages come from a single channel, the prefix.dev mirror of conda-forge
(`https://prefix.dev/conda-forge`).

Edit `pixi.toml` to add new dependencies:

```toml
[dependencies]
your-package = ">=1.0.0"
```

Then run:

```bash
pixi install
```

or

Directly add packages (this will edit the pixi toml and install):

```bash
pixi add your-package
```

## AI Agents

The repository is set up for AI coding agents such as Claude Code, Codex, Copilot,
Cursor, and Gemini CLI:

- [`AGENTS.md`](AGENTS.md) is the agent entry point. It points to the rules in
  [`.agents/rules/`](.agents/rules/), which agents load on demand.
- [`.agents/skills/`](.agents/skills/) holds task skills such as `commit`,
  `push`, `create-pr`, `merge-pr`, and `okf-memory`; `.claude/skills` links
  there so Claude Code finds them.
- [`knowledge/`](knowledge/) is project memory: an OKF bundle that agents read
  and write with `pixi run okf`, as the `okf-memory` skill describes.

A project that doesn't want project memory can remove the `okf` feature from the
`default` environment in `pixi.toml`, then delete `.agents/skills/okf-memory/`
and `knowledge/`.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of
conduct and the process for submitting pull requests. If you use AI tools while
contributing, read the [AI Policy](AI_POLICY.md) first: it covers disclosure,
review responsibility, and how to credit AI assistance in commits.

## License

This project is licensed under the terms specified in the [LICENSE](LICENSE)
file.
