"""CLI for LLMoxie RAG.

Ingest documents into Qdrant, search them, and chat with the RAG agent.
"""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console

console = Console()
console_err = Console(stderr=True)

app = typer.Typer(
    name="llmoxie-rag",
    help="LLMoxie RAG - agentic retrieval over your documents",
    add_completion=False,
)


@app.command()
def ingest(
    directories: list[str] = typer.Argument(
        ...,
        help="One or more directories containing documents to ingest",
    ),
    collection: Optional[str] = typer.Option(
        None,
        "--collection",
        "-c",
        help="Collection name (defaults to config)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        is_flag=True,
        help="Overwrite existing collection without confirmation",
    ),
    batch_size: int = typer.Option(
        100,
        "--batch-size",
        "-b",
        help="Number of documents to process per batch",
    ),
) -> None:
    """Ingest documents into Qdrant collection.

    Ingests documents from one or more directories into a Qdrant collection
    with multi-vector embeddings (Dense, Sparse, ColBERT).

    Examples:
        Ingest documents from docs directory:
            llmoxie-rag ingest ./docs

        Ingest from multiple directories:
            llmoxie-rag ingest ./docs ./papers

        Force overwrite existing collection:
            llmoxie-rag ingest ./docs --force

        Use custom collection name:
            llmoxie-rag ingest ./docs --collection my-collection
    """
    from pathlib import Path
    from llmoxie_rag.ingestion import IngestionPipeline
    from llmoxie_rag.exceptions import AgenticRAGError

    try:
        # Validate directories exist
        dir_paths_str = []
        for directory in directories:
            path = Path(directory)
            if not path.exists():
                console_err.print(f"[red]✗[/red] Directory not found: {directory}")
                raise typer.Exit(code=1)
            if not path.is_dir():
                console_err.print(f"[red]✗[/red] Not a directory: {directory}")
                raise typer.Exit(code=1)
            dir_paths_str.append(str(path))

        console.print("[blue]→[/blue] Initializing ingestion pipeline...")

        # Create ingestion pipeline
        pipeline = IngestionPipeline(
            collection_name=collection,
            batch_size=batch_size,
        )

        # Ingest documents
        console.print(
            f"[blue]→[/blue] Ingesting documents from {len(dir_paths_str)} director{'y' if len(dir_paths_str) == 1 else 'ies'}..."
        )

        # Ingest all directories at once (ingest() accepts list of directory strings)
        pipeline.ingest(directories=dir_paths_str, force=force)

        console.print("\n[green]✓[/green] Ingestion complete!")

    except AgenticRAGError as e:
        console_err.print(f"[red]✗[/red] Ingestion failed: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console_err.print(f"[red]✗[/red] Unexpected error: {e}")
        raise typer.Exit(code=1)


@app.command()
def search(
    query: str = typer.Argument(
        ...,
        help="Search query",
    ),
    collection: Optional[str] = typer.Option(
        None,
        "--collection",
        "-c",
        help="Collection name (defaults to config)",
    ),
    top_k: Optional[int] = typer.Option(
        None,
        "--top-k",
        "-k",
        help="Number of results to return (defaults to config)",
    ),
    prefetch_k: Optional[int] = typer.Option(
        None,
        "--prefetch-k",
        "-p",
        help="Number of prefetch candidates per method (defaults to config)",
    ),
    rerank: bool = typer.Option(
        True,
        "--rerank/--no-rerank",
        help="Enable/disable ColBERT reranking",
    ),
) -> None:
    """Search the knowledge base.

    Executes a hybrid search query with Dense, Sparse, and optional
    ColBERT reranking.

    Examples:
        Basic search:
            llmoxie-rag search "What is machine learning?"

        Search with custom top-k:
            llmoxie-rag search "architecture patterns" --top-k 10

        Search without reranking:
            llmoxie-rag search "deployment" --no-rerank

        Search specific collection:
            llmoxie-rag search "query" --collection my-collection
    """
    from llmoxie_rag.search import HybridSearcher
    from llmoxie_rag.exceptions import AgenticRAGError

    try:
        console.print(f"[blue]→[/blue] Searching for: [bold]{query}[/bold]")

        # Create searcher
        searcher = HybridSearcher(
            collection_name=collection,
            enable_rerank=rerank,
            prefetch_top_k=prefetch_k,
            final_top_k=top_k,
        )

        # Execute search
        results = searcher.search(query=query, limit=top_k)

        if not results:
            console.print("[yellow]![/yellow] No results found")
            return

        # Display results
        console.print(
            f"\n[green]✓[/green] Found {len(results)} result{'s' if len(results) != 1 else ''}:\n"
        )

        for i, result in enumerate(results, 1):
            console.print(
                f"[bold cyan]Result {i}[/bold cyan] (score: {result.score:.4f})"
            )
            console.print(f"[dim]Source:[/dim] {result.file_path}")
            if result.heading_hierarchy:
                console.print(f"[dim]Section:[/dim] {result.heading_hierarchy}")
            console.print(
                f"\n{result.text[:300]}{'...' if len(result.text) > 300 else ''}\n"
            )

    except AgenticRAGError as e:
        console_err.print(f"[red]✗[/red] Search failed: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console_err.print(f"[red]✗[/red] Unexpected error: {e}")
        raise typer.Exit(code=1)


@app.command()
def chat(
    collection: Optional[str] = typer.Option(
        None,
        "--collection",
        "-c",
        help="Collection name (defaults to config)",
    ),
    provider: Optional[str] = typer.Option(
        None,
        "--provider",
        help="LLM provider override (openai, ollama, litellm, azure, huggingface)",
    ),
    model: Optional[str] = typer.Option(
        None,
        "--model",
        "-m",
        help="LLM model override",
    ),
    litellm_base: Optional[str] = typer.Option(
        None,
        "--litellm-base",
        help="LiteLLM proxy base URL (e.g., http://localhost:4000)",
    ),
    litellm_api_key: Optional[str] = typer.Option(
        None,
        "--litellm-api-key",
        help="LiteLLM API key",
    ),
    litellm_model_prefix: Optional[str] = typer.Option(
        None,
        "--litellm-prefix",
        help="LiteLLM model prefix (e.g., openai/, anthropic/)",
    ),
    azure_endpoint: Optional[str] = typer.Option(
        None,
        "--azure-endpoint",
        help="Azure OpenAI endpoint URL (e.g., https://myresource.openai.azure.com)",
    ),
    azure_api_key: Optional[str] = typer.Option(
        None,
        "--azure-api-key",
        help="Azure API key",
    ),
    azure_deployment: Optional[str] = typer.Option(
        None,
        "--azure-deployment",
        help="Azure deployment name",
    ),
) -> None:
    """Launch interactive RAG chat.

    Starts an interactive REPL for conversing with the RAG agent.
    The agent has access to the knowledge base and can provide
    answers with citations.

    Examples:
        Start chat:
            llmoxie-rag chat

        Chat with specific collection:
            llmoxie-rag chat --collection my-docs

        Use different LLM:
            llmoxie-rag chat --provider ollama --model llama2

        Use LiteLLM proxy:
            llmoxie-rag chat --provider litellm --litellm-base http://localhost:4000 --model gpt-4o-mini

        Use Azure OpenAI:
            llmoxie-rag chat --provider azure --azure-endpoint https://myresource.openai.azure.com --azure-deployment gpt-4o
    """
    from rich.markdown import Markdown
    from rich.panel import Panel

    from llmoxie_rag.agent import RAGAgent
    from llmoxie_rag.exceptions import AgenticRAGError
    from llmoxie_rag.settings import config

    try:
        console.print("[blue]→[/blue] Initializing RAG agent...")

        # Override config with CLI options
        if litellm_base:
            config.litellm_api_base = litellm_base
        if litellm_api_key:
            config.litellm_api_key = litellm_api_key
        if litellm_model_prefix:
            config.litellm_model_prefix = litellm_model_prefix
        if azure_endpoint:
            config.azure_endpoint = azure_endpoint
        if azure_api_key:
            config.azure_api_key = azure_api_key
        if azure_deployment:
            config.azure_deployment_name = azure_deployment

        # Create agent
        agent = RAGAgent(
            collection_name=collection,
            llm_provider=provider,
            llm_model=model,
        )

        console.print(
            Panel(
                "[bold green]RAG Chat Session[/bold green]\n\n"
                "Ask questions about your knowledge base.\n"
                "Type 'exit' or 'quit' to end the session.",
                border_style="green",
            )
        )

        message_history = []

        while True:
            # Get user input
            try:
                query = console.input("\n[bold cyan]You:[/bold cyan] ")
            except (KeyboardInterrupt, EOFError):
                console.print("\n[yellow]![/yellow] Session ended")
                break

            if query.strip().lower() in ["exit", "quit"]:
                console.print("[yellow]![/yellow] Session ended")
                break

            if not query.strip():
                continue

            # Get agent response
            console.print("[blue]→[/blue] Thinking...")

            try:
                response = agent.run_sync(query=query, message_history=message_history)

                # Display answer
                console.print("\n[bold green]Assistant:[/bold green]")
                console.print(Markdown(response.answer))

                # Display citations
                if response.citations:
                    console.print(
                        f"\n[dim]Citations ({len(response.citations)}):[/dim]"
                    )
                    for i, citation in enumerate(response.citations, 1):
                        console.print(
                            f"  [{i}] {citation.source_file} "
                            f"(score: {citation.relevance_score:.2f})"
                        )
                        console.print(f"      {citation.quote[:100]}...")

                console.print(
                    f"\n[dim]Confidence: {response.confidence:.2f} | Sources: {response.sources_used}[/dim]"
                )

                # Update message history
                message_history.append({"role": "user", "content": query})
                message_history.append(
                    {"role": "assistant", "content": response.answer}
                )

            except Exception as e:
                console_err.print(f"[red]✗[/red] Error: {e}")

    except AgenticRAGError as e:
        console_err.print(f"[red]✗[/red] Failed to start chat: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console_err.print(f"[red]✗[/red] Unexpected error: {e}")
        raise typer.Exit(code=1)


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
