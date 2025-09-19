import typer
from . import doc_loader, rag, debate

doc_app = typer.Typer(help="AI CLI Knowledge Agent")

@doc_app.command()
def load(path: str):
    """
    Load documents (PDF, Markdown, code) and build embeddings.
    """
    docs = doc_loader.load_documents(path)
    rag.build_vectorstore(docs)
    typer.echo(f"✅ Loaded {len(docs)} documents from {path}")

@doc_app.command()
def ask(query: str):
    """
    Ask questions about loaded documents.
    """
    answer = rag.query_vectorstore(query)
    typer.echo(f"💡 {answer['result']}")

@doc_app.command()
def init_debate(topic: str):
    """Simulate a multi-agent debate on a topic"""
    result = debate.run_debate(topic)

    typer.echo("\n🧠 Debate Finished!")
    typer.echo("\n--- Researcher ---\n" + result["researcher_output"])
    typer.echo("\n--- Summarizer ---\n" + result["summarizer_output"])
    typer.echo("\n--- Critic ---\n" + result["critic_output"])
    typer.echo("\n✅ Final Consensus:\n" + result["consensus_output"])
if __name__ == "__main__":
    doc_app()
