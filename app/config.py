import os
from dotenv import load_dotenv

load_dotenv()
class Config:
    
    MODEL_NAME="model/gemini-2.5-flash"

    EMBEDDING_MODEL='sentence-transformers/all-MiniLM-L6-v2'

    # Rag settings
    CHUNK_SIZE=1000
    CHUNKING_OVERLAP=150
    TOP_K=5
    DEVICE = "cuda"
    MODEL_CACHE_DIR = "./models"

    # retrival 
    CHROMA_DIR="vectore_store"
    SEARCH_TYPE="similarity"
    CROSS_ENCODER_MODEL="cross-encoder/ms-marco-MiniLM-L-6-v2"
    # reliability setting
    RETRY_COUNT=3
    SIMILARITY_THRESHOLD =0.75

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = "gemini-2.0-flash-exp"
    TEMPERATURE=0.3
    MAX_TOKENS=1500

    MAX_RETRIES = 2 
    QUALITY_THRESHOLD = 0.3 

    # Orchestrator settings
    MAX_RETRIES = 2
    QUALITY_THRESHOLD = 0.3
