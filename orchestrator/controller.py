import logging
from retrieval.retriever import retrieve_documents, prepare_context_for_llm
from retrieval.reranker import rerank_documents
from llm.generator import generate_answer_with_sources
from orchestrator.query_rewriter import should_rewrite_query, rewrite_query, expand_query
from app.config import Config


_conversation_history=[]

def process_query(query,enable_reranking=True,max_retries=None):
    """ processes a user query through the entire RAG pipeline"""

    if not query or not query.strip():
        logging.error("Empty query received")
        return {
            "answer":"Please provide a queston",
            "sources": [],
            "status": "error",
            "original_query": query
        }
    
    logging.info("=" * 80)
    logging.info(f" PROCESSING QUERY: {query}")
    logging.info("=" * 80)

    original_query=query
    max_retries=max_retries or Config.MAX_RETRIES
    attempt=0

    