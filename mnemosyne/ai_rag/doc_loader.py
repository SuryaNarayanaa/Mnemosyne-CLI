import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Reusable splitter (tweak chunk_size & overlap if needed)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,      # each chunk ~800 characters
    chunk_overlap=100,   # small overlap to keep context
)

def load_documents(path: str):
    docs = []
    if os.path.isfile(path):
        docs.extend(_load_file(path))
    else:
        for root, _, files in os.walk(path):
            for f in files:
                docs.extend(_load_file(os.path.join(root, f)))
    return docs

def _load_file(filepath: str):
    ext = filepath.lower().split(".")[-1]
    if ext == "pdf":
        loader = PyPDFLoader(filepath)
        pages = loader.load()
        return text_splitter.split_documents(pages)
    elif ext in ["md", "txt", "py", "js", "java"]:
        loader = TextLoader(filepath, encoding="utf-8")
        docs = loader.load()
        return text_splitter.split_documents(docs)
    else:
        return []
