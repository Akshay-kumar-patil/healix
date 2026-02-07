import logging

from ingestion.loader import load_docx,load_pdf,load_csv,url_loader
from ingestion.chunking import chunk_documents
from ingestion.vectordb import create_vectordb


def execute_ingestion(source,type):
    try:
        logging.info("Starting ingetion pipeline...")
        
        # 1. Loading
        if type=="pdf":
            documents=load_pdf(source)
        
        elif type=="csv":
            documents=load_csv(source)
        
        elif type=="url":
            documents=url_loader(source)
        
        elif type=="docx":
            documents = load_docx(source)

        if not documents:
            raise ValueError("No documents loaded")
        
        logging.info(f"{len(documents)} documents loaded")

        # 2.chunking
        chunks=chunk_documents(documents)

        if not chunks:
            raise ValueError("Chunking failed")

        logging.info(f"{len(chunks)} chunks created")

        #3. vectore db
        vector_store=create_vectordb(chunks=chunks)
        logging.info("Ingestion pipeline completed successfully")
        
        return vector_store
    
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        raise
