from mcp.server.fastmcp import FastMCP
from mnemosyne.ai_rag import doc_loader, rag

mcp = FastMCP("mnemosyne-rag")

@mcp.resource("documents://{params}")
async def list_documents(params: dict) -> dict:
    path = params.get("path", "./document/")
    docs = doc_loader.load_documents(path)
    return {"count": len(docs), "docs": [d.page_content[:200] for d in docs]}

@mcp.resource("query://{params}")
async def query_docs(params: dict) -> dict:
    question = params.get("question", "")
    answer = rag.query_vectorstore(question)
    return {"answer": answer}

if __name__ == "__main__":
    print("🚀 Starting MCP server: mnemosyne-rag (waiting for client...)")
    mcp.run()
