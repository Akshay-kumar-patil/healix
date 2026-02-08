from langchain_chroma import Chroma
from ingestion.vectordb import create_vectordb
import logging
from app.config import Config

db=create_vectordb()

def _retriver(query):
    """search the relevent vectors from the db"""

    logging.info("Starting Retriver part...")
    retriver=db.as_retriver(search_kwargs=Config.TOP_K)
    relevant_docs=retriver.invoke(query)
    print("\n")

    logging.info("retriver done...")
    
    print("\ncontent---------------------")
    for i,doc in enumerate(relevant_docs):
        print(f"Document {i}:\n{doc.page_content}\n")

    return relevant_docs



    