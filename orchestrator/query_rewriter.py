import logging 
import google.generativeai as genai
from app.config import Config
from memory.conversation_store import get_context_for_llm, get_last_query
from llm.prompt_templates import QUERY_REWRITE_PROMPT

def should_rewrite_query(query):
    """determine if a query needs rewritting"""

    if not query:
        return False
    
    vague_indicator=[
        len(query.split())<3,
        query.lower().startswith(("what about","tell me about", "how about")),
        "it" in query.lower() and len(query.split())<5,
        "this" in query.lower() and len(query.split())<5,
        "that" in query.lower() and len(query.split())<5,
    ]

    is_vague=any(vague_indicator)
    
    if is_vague:
        logging.info(f"Query appears vague: '{query}")

    return is_vague

def rewrite_query(query, conversation_history=None):
    """Rewrite a vague to be more specific and clear"""

    if not query:
        logging.error("Empty query provided")
        return query
    logging.info(f"Rewriting query: '{query}'")


    try:

        genai.configure(api_key=Config.GEMINI_API_KEY)
        model=genai.GenerativeModel(model=Config.GEMINI_MODEL)

        
        if conversation_history:
            context = "\n".join([
                f"Previous Q: {item['query']}\nPrevious A: {item['answer'][:100]}..."
                for item in conversation_history[-3:]
            ])
        else:
            context=get_context_for_llm(last_n=3)
        if context:
            prompt = f"""Previous conversation:
{context}

Current vague query: {query}

Rewrite this query to be specific and clear for document retrieval. Consider the conversation context.

Rewritten query:"""
        else:
            prompt = f"""Rewrite this vague query to be more specific and clear for document retrieval.

Original Query: {query}

Rewritten Query:"""
            
        response=model.generate_content(prompt)
        rewritten=response.text.strip()

        if not rewritten or len(rewritten)<3:
            logging.warning("Rewrite failed, using original query")
            return query
        
        logging.info(f"Re-Written the query: '{rewritten}'")
        return rewritten
    
    except Exception as e:
        logging.exception(f"Query rewriting failed: {e}")
        return query 
    


def expand_query(query):
    """Expand query with synonyms and related terms for better retrieval"""
    
    if not query:
        logging.error("Empty query provided")
        return query
    
    last_topic = get_last_query()
    try:
        genai.configure(api_key=Config.GEMINI_API_KEY)
        model=genai.GenerativeModel(model=Config.GEMINI_MODEL)

        context_hint = f"\nPrevious topic: {last_topic}" if last_topic else ""
        
        prompt = f"""Expand this query with relevant synonyms and related terms for better document retrieval.{context_hint}

Original query: {query}

Expanded query (under 20 words):"""
        
        response=model.generate_content(prompt)
        expanded=response.text.strip()

        logging.info(f"Query expanded to: '{expanded}'")
        return expanded
    
    except Exception as e:
        logging.exception(f"Query expansion failed: {e}")
        return query
    


