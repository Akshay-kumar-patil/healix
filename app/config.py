class Config:
    
    MODEL_NAME="model/gemini-2.5-flash"

    EMBEDDING_MODEL='sentence-transformers/all-MiniLM-L6-v2'

    # Rag settings
    CHUNK_SIZE=1000
    TOP_K=5

    # reliability setting
    RETRY_COUNT=3
    SIMILARITY_THRESHOLD =0.75

    TEMPERATURE=0.3
    MAX_TOKENS=1500