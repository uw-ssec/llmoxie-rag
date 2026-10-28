# Repository Map

**Load when:** you need to know what this repository is, where a file lives, or
what CI runs against it.

## Repository Overview

**llmoxie-rag** is an agentic retrieval-augmented generation (RAG) system from
UW SSEC: document ingestion, multi-vector hybrid search (dense + sparse +
ColBERT) over Qdrant, and a Pydantic-AI agent that answers with citations. It
was extracted from [uw-ssec/llmoxie](https://github.com/uw-ssec/llmoxie) with
its git history, and will grow into an MCP search service (llmoxie#72).

**Repository Stats:**

- **Type:** Python package (`src/` layout, hatchling), import name
  `llmoxie_rag`, console script `llmoxie-rag`
- **Language:** Python 3.12 (`requires-python = ">=3.12"`)
- **Build System:** Pixi; the `rag` feature installs the package editable in
  the `default` environment
- **Platform:** macOS (osx-arm64) and Linux (linux-64, linux-aarch64)
- **License:** BSD 3-Clause

Settings use the `AGENTIC_` environment-variable prefix
(`src/llmoxie_rag/settings.py`), unchanged from llmoxie so existing `.env`
files keep working. Don't change the embedding-model defaults: search over
existing collections depends on them (`tests/test_settings.py` guards this).

## Project Structure & Key Files

```
.
├── .devcontainer/               # Codespaces / Dev Containers image: pixi + coding agent CLIs
├── .agents/
│   ├── rules/                   # On-demand rules referenced by AGENTS.md
│   └── skills/                  # User-invocable skills (/commit, /create-pr, ...)
├── .claude/
│   └── skills -> ../.agents/skills  # Symlink so Claude Code discovers the skills
├── .github/
│   ├── dependabot.yml           # Dependabot config for GitHub Actions
│   ├── pull_request_template.md # PR template (requires pre-commit checks)
│   ├── release.yml              # Release notes configuration
│   ├── workflows/               # ci.yml (tests), zizmor workflow linting, Copilot agent setup
│   └── ISSUE_TEMPLATE/          # Issue templates (bug, feature, docs, onboard, etc.)
├── src/llmoxie_rag/
│   ├── cli.py                   # Typer CLI: ingest, search, chat
│   ├── settings.py              # AgenticConfig (AGENTIC_* env vars)
│   ├── exceptions.py            # AgenticRAGError hierarchy
│   ├── agent/                   # RAGAgent and response/citation models
│   ├── ingestion/               # IngestionPipeline: load, parse, chunk, embed, upsert
│   ├── providers/               # LLM provider factory (openai, ollama, litellm, azure, huggingface)
│   ├── search/                  # HybridSearcher and SearchResult
│   ├── vector_store/            # QdrantManager (named vectors)
│   └── api/                     # FastAPI app: /v1/agentic/chat, /v1/agentic/retrieve
├── tests/                       # pytest suite; conftest.py starts Qdrant via testcontainers
├── docs/
│   └── testcontainers.md        # How the tests run Qdrant
├── docker-compose.yml           # Local Qdrant on port 6333
├── knowledge/                   # OKF project memory, managed by the okf CLI (okf-memory skill)
├── .pre-commit-config.yaml      # Pre-commit hook configuration
├── pixi.toml                    # **PRIMARY CONFIG**: Dependencies, tasks, features
├── pixi.lock                    # Lock file (auto-generated, don't manually edit)
├── pyproject.toml               # Package metadata, dependencies, test extra, console script
├── .gitignore                   # Ignores .pixi/ and .DS_Store
├── AGENTS.md                    # Entry point for AI assistants
├── CLAUDE.md                    # Points Claude Code at AGENTS.md (@AGENTS.md)
├── CODE_OF_CONDUCT.md           # Contributor Covenant v2.0
├── CONTRIBUTING.md              # Contribution guidelines (references Conventional Commits)
├── LICENSE                      # BSD 3-Clause License
├── README.md                    # Project documentation
└── onboarded.md                 # Empty file (excluded from pre-commit)
```

**Tests:** `pixi run test` runs `pytest tests/` except `tests/test_cli.py`
(Docker must be running for the Qdrant testcontainer); `pixi run test-cli` runs
the CLI tests.

## Continuous Integration & Validation

**Tests:** `.github/workflows/ci.yml` runs `pixi run test` and
`pixi run test-cli` on pushes and PRs to `main`, with actions pinned by commit
SHA.

**Workflow lint:** `.github/workflows/zizmor.yml` runs
[zizmor](https://github.com/zizmorcore/zizmor) static analysis to lint workflow
files for security issues. Changes to anything under `.github/workflows/` must
keep this check passing.

**Copilot cloud agent:** `.github/workflows/copilot-setup-steps.yml` prepares
the GitHub Copilot coding agent's environment (pixi install from `pixi.lock`,
pre-commit hook environments). Copilot reads `AGENTS.md` and `.agents/skills/`
on its own; keep the pinned `pixi-version` in sync with
`.devcontainer/Dockerfile`.

**Pre-commit.ci Integration:** The `.pre-commit-config.yaml` includes a `ci:`
section, suggesting integration with https://pre-commit.ci for automated PR
checks. Verify if enabled on the repository.

**Dependabot:** Configured to update GitHub Actions weekly (groups all action
updates together).

## Further Reading

For more information on SSEC best practices, see:
https://rse-guidelines.readthedocs.io/en/latest/llms-full.txt
