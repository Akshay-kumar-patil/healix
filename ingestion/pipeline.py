import logging
import time
from typing import Union,List
from ingestion.loader import load_docx,load_pdf,load_csv,load_url
from ingestion.chunking import chunk_documents
from ingestion.vectordb import create_vectordb
from ingestion.embedding import embedding_model
import os


def execute_ingestion(source: Union[str,List[str]],doc_type:str,persist_directory:str=None):
    """Execute ingetion pipeline"""
    if not source:
        raise ValueError("Source cannot be empty")
    
    valid_type=['pdf','docx','csv','url']
    if doc_type not in valid_type:
        raise ValueError(f"Invalid doc_type")
    
    logging.info("="*60)
    logging.info("Starting Ingetion Pipeline")
    logging.info(f"source: {source}")
    logging.info(f"Type:{doc_type}")
    logging.info("="*60)
    
    try:
        logging.info("state 1/3 Loading Documents...")
        stage_start=time.time()

        
        # 1. Loading
        if type=="pdf":
            documents=load_pdf(source)
        
        elif type=="csv":
            documents=load_csv(source)
        
        elif type=="url":
            documents=load_url(source)
        
        elif type=="docx":
            documents = load_docx(source)

        if not documents:
            raise ValueError("No documents loaded")
        
        stage_time=time.time()-stage_start
        logging.info(f"{len(documents)} documents loaded. in {stage_time}s")


        # 2.chunking
        logging.info("Stage 2/3 Chunking documents....")
        stage_start=time.time()

        chunks=chunk_documents(documents)

        if not chunks:
            raise ValueError("Chunking failed")

        stage_time=time.time()-stage_time
        logging.info(f"{len(chunks)} chunks created. in {stage_time}s")


        #3. vectore db
        logging.ingo("Stage 3/3  vector store")
        stage_time=time.time()

        vector_store=create_vectordb(chunks=chunks,persists_directory=persist_directory)
        stage_time=time.time()-stage_start
        
        logging.info(f"Ingestion pipeline completed successfully in {stage_time}s" )
        
        return vector_store
    
    except FileNotFoundError as e:
        logging.exception(f"File not found: {e}")
        raise
    
    except ValueError as e:
        logging.exception(f"Validation error: {e}")
        raise

    except Exception as e:
        logging.exception(f"Pipeline failed: {e} due to unexpected error")
        raise


def validate_pipeline_health():
    """Quick health check of pipeline"""

    health={
        "embedding_model": False,
        "vector_store_dir":False
    }

    try:
        model=embedding_model()
        health["embedding_model"]=True
        logging.info("Embedding Model loaded successfully")
        
    except Exception as e:
        logging.error(f"Embedding model failed:{e}")

    
    try:
        persist_dir=os.path.join("vectore_store","chroma_db")
        health["vector_store_dir"]=os.path.exists(persist_dir)

        if health["vector_store_dir"]:
            logging.enfo(f"Vectore store directory exists: {persist_dir}")

        else:
            logging.warning(f"vector store directory not found: {persist_dir}")

    except Exception as e:
        logging.error(f"Directory Check failed : {e}")
    
    return health