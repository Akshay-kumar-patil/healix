from langchain_huggingface import HuggingFaceEmbeddings
import logging
from app.config import Config

_embeddings = None

def embedding_model():
    """Create and persist ChromaDB vector store"""

    global _embeddings
    if _embeddings is not None:
        logging.info("Using cached embedding model")
        return _embeddings

    try:
        logging.info("Loading embedding model...")

        _embeddings=HuggingFaceEmbeddings(
            model_name=Config.EMBEDDING_MODEL,
            model_kwargs={"device":Config.DEVICE},
            encode_kwargs={"normalize_embedding":True}
        )

        logging.info("Embedding model laoded successfully.")
        return _embeddings
    
    except Exception as e:
        logging.error(f"Embedding model failed: {e}")
        raise
