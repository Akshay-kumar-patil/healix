from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import logging
from app.config import Config

_embeddings = None

def embedding():
    """Create and persist ChromaDB vector store"""

    global _embedding
    if _embedding is not None:
        return _embedding

    try:
        logging.info("Loading embedding model...")

        _embeddings=HuggingFaceEmbeddings(
            model_name=Config.EMBEDDING_MODEL,
            model_kwargs={"device":Config.DEVICE},
            encode_kwargs={"normalize_embedding":True}
        )

        logging.info("Embedding model laoded successfully.")
        return _embedding
    
    except Exception as e:
        logging.error(f"Embedding model failed: {e}")
        raise
