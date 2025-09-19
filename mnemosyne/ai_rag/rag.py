
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from dotenv import load_dotenv

load_dotenv()

def build_vectorstore(docs):
    if not docs:
        raise ValueError("❌ No documents found. Please check your docs path.")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(docs, embeddings)
    vectorstore.save_local("ai_rag/vectorstore/docs_index")

def query_vectorstore(query: str):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.load_local(
        "ai_rag/vectorstore/docs_index", embeddings, allow_dangerous_deserialization=True
    )
    retriever = vectorstore.as_retriever()

    api_key = os.getenv("GOOGLE_API_KEY")
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0, google_api_key=api_key)
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    return qa.invoke(query)
