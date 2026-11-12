""""
Takes the data and embeds it into the chromadb
"""

import json
import logging

from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_ollama import ChatOllama
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.runnables import RunnablePassthrough

log = logging.getLogger()

class LangchainRAG():
    log.info("Initializing RAG class...")
    def create_embeds(self):
        print("Loading the scraped data")
        try:
            with open("scraped_products.json", "r", encoding="utf-8") as f:

                items_data=json.load(f)

            docs = []
            for item in items_data:
                page_content = f"Vehicle:{item.get('title')}\nPrice:{item.get('price')}\nYear:{item.get('year')}\nCountry:{item.get('country_of_origin')}\nMileage:{item.get('mileage')}"
                metadata={"title": item.get('title')}

                docs.append(Document(page_content=page_content, metadata=metadata))
        except Exception as e:
            log.error(f"Experienced an error while loading the data from local: {e}")
            return
        try:
            print("Creating embeddings of the uploaded data")
            
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            vector_store =Chroma.from_documents(
                documents=docs,
                embedding=embeddings,
                persist_directory="./chroma_db"
            )

            print("Created embeddings successfully")
            return

        except Exception as e:
            print(f"Experienced an error while creating data embeddings: {e} ")
            print("Terminating ....")
            return

if __name__ == "__main__":
    rag = LangchainRAG()
    rag.create_embeds()