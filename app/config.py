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

    # reliability setting
    RETRY_COUNT=3
    SIMILARITY_THRESHOLD =0.75

    TEMPERATURE=0.3
    MAX_TOKENS=1500