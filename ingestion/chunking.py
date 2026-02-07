from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import Config
import logging

def chunk_documents(documents):
    """Splits documents into semantically meaningful chunks"""
    
    if not documents:
        raise ValueError("No documents provided for chunking.")


    logging.info("Starting documnets chunking...")
    
    splitter=RecursiveCharacterTextSplitter(
        separators=["\n\n","\n",".", " ", ""],
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNKING_OVERLAP
    )
    
    chunks=splitter.split_documents(documents=documents)

    logging.info(f"Createrd {len(chunks)} chunks")

    chunks= [c for c in chunks if len(c.page_content)>100]
    return chunks

