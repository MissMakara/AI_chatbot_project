import os
import logging

from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

log = logging.getLogger(__name__)

class RetrieverClass():
    def retrieve_response():
        #STEP 1:Load the exact embedding model used to save to db
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

        #STEP 2: Connect to your previously saved Chroma vector store directory
        vector_store = Chroma(
            persist_directory=Chroma(
                persist_directory="./chroma_db",
                embedding_function = embeddings
            )
        )

        #3.Create a retriever from the vector store (fetches top 3 matching products)
        retriever = vector_store.as_retriever(search_kwargs={"k":3})

        #4: Initialize the Gemini Chat Model
        llm = ChatGoogleGenerativeAI(model="gemini-3.8-flash", temperature=0.3)

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful product assistant. Answer the user's question using ONLY the provided context below.\n\nContext:\n{context}"),
            ("human", "{question}")
        ])

        #Combine the retrieved document chunks into a single string
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        rag_chain =(
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            |prompt_template
            |llm
            |StrOutputParser()
        )

        # 8. Ask a question about your scraped website data!
        user_query = "What products do you have that mention a specific description or feature?"
        log.info(f"User Query: {user_query}\n")

        response = rag_chain.invoke(user_query)
        log.info("Gemini Answer:")
        log.info(response)
