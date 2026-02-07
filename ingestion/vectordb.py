from langchain_chroma import Chroma
from ingestion.embedding import embedding_model
import logging

def create_vectordb(chunks,persists_directory="vector_store\\chroma_db"):

    if not chunks:
        raise ValueError("No Chunks provided.")

    embeddings=embedding_model()
    
    vector_db=Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_metadata={"hnsw:space": "cosine"},
        persist_directory=persists_directory
    )

    logging.info("vectore store created successfully")

    return vector_db