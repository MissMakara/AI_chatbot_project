import logging
from pathlib import Path

from fastapi import APIRouter
from langchain_chroma import Chroma
# from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from app.schemas.chat_schema import ChatRequest

log = logging.getLogger(__name__)

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    query = request.query

    log.info(f"Received request query: {query}")

    log.info("Initializing the db and llm")

    # 1. Initialize DB and LLM (using the updated model name)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    chroma_dir = str(Path(__file__).resolve().parents[1] / "rag" / "chroma_db")
    vector_store = Chroma(persist_directory=chroma_dir, embedding_function=embeddings)
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    log.info("Setting llama temperature")
    llm = ChatOllama(model="llama3.2", temperature=0.3)

    prompt_template = ChatPromptTemplate.from_messages([
    ("system", 
     "You are a strict product assistant. "
     "You MUST answer the user's question using ONLY the factual context provided below. "
     "Do NOT use any outside knowledge, pre-trained facts, or assumptions. "
     "If the answer cannot be found explicitly within the provided context, you must say: "
     "'I cannot find the answer in the provided documents.'\n\n"
     "Context:\n{context}"
    ),
    ("human", "{question}")
    ])

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    log.info("Setting up the retriever ....")

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt_template
        | llm
        | StrOutputParser()
    )

    log.info("Receiving the query ...")
    log.info("Checking what is in the retrieved docs ....")
    retrieved_docs = retriever.invoke(query)

    print(f"--- Retrieved {len(retrieved_docs)} documents from ChromaDB ---")
    for i, doc in enumerate(retrieved_docs):
        print(f"Doc {i+1}: {doc.page_content[:200]}...\n")
    response = rag_chain.invoke(request.query)
    return {"answer": response}




