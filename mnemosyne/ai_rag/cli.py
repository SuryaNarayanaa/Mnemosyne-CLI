import typer
import asyncio
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client

from . import doc_loader, rag

doc_app = typer.Typer(help="AI CLI Knowledge Agent")

@doc_app.command()
def load(path: str):
    """
    Load documents (PDF, Markdown, code) and build embeddings locally.
    """
    docs = doc_loader.load_documents(path)
    rag.build_vectorstore(docs)
    typer.echo(f"✅ Loaded {len(docs)} documents from {path}")


@doc_app.command()
def ask_mcp(query: str):
    """
    Ask a question through the MCP server.
    """
    async def _ask():
        async with stdio_client(["python mcp_server.py"]) as (read, write):
            async with ClientSession("mnemosyne-rag", read, write) as client:
                result = await client.call_resource(
                    "query://anything", {"question": query}
                )
                return result

    result = asyncio.run(_ask())
    typer.echo(f"💡 {result['answer']}")


@doc_app.command()
def docs_mcp(path: str = "./document/"):
    """
    Load documents through the MCP server.
    """
    async def _docs():
        async with stdio_client(["python mcp_server.py"]) as (read, write):
            async with ClientSession("mnemosyne-rag", read, write) as client:
                result = await client.call_resource(
                    "documents://anything", {"path": path}
                )
                return result

    result = asyncio.run(_docs())
    typer.echo(f"📄 Loaded {result['count']} documents from {path}")


if __name__ == "__main__":
    doc_app()
