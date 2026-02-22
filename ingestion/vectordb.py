from langchain_chroma import Chroma
from ingestion.embedding import embedding_model
import logging
import os

def create_vectordb(chunks,persist_directory=None):

    if not chunks:
        raise ValueError("No Chunks provided.")
    
    if persist_directory is None:
        persist_directory = os.path.join("vector_store", "chroma_db")

    os.makedirs(persist_directory,exist_ok=True)

    logging.info(f"Creating vector store with {len(chunks)} chunks...")
    logging.info(f"Persist directory: {persist_directory}")

    try:
        embeddings=embedding_model()
        
        vector_db=Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_metadata={"hnsw:space": "cosine"},
            persist_directory=persist_directory
        )

        logging.info("vectore store created successfully")
        logging.info(f"Stored at: {os.path.abspath(persist_directory)}")

        return vector_db
    
    except Exception as e:
        logging.exception(f"Failed to create vector store: {e}")
        raise

def load_vectordb(persist_directory=None):
    """loading existing ChromaDB vectore store"""

    if persist_directory is None:
        persist_directory=os.path.join("vectore_store","chroma_db")

    if not os.path.exists(persist_directory):
        raise FileExistsError(
            f"Vectore store not found at {persist_directory}"
            "Please run ingetion pipeline first"
        )
    
    logging.info(f"loading vectore store from {persist_directory}")

    try:
        embedding=embedding_model()

        vector_db=Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding,
            collection_metadata={"hnsw:space":"cosine"}
        )

        logging.info(f"vector store loaded successfully")
        return vector_db
    
    except Exception as e:
        logging.exception(f"Failed to load vectore store: {e}")
        raise