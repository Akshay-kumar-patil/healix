import logging 
import google.generativeai as genai
from app.config import Config
from llm.prompt_templates import QUERY_REWRITE_PROMPT

def should_rewrite_query(query):
    """determine if a query needs rewritting"""

    if not query:
        return False
    
    vague_indicator=[
        len(query.split())<3,
        query.lower().startwith(("what about","tell me about", "how about")),
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
    logging.info("Rewriting query: '{query}")


    try:

        genai.configure(api_key=Config.GEMINI_API_KEY)
        model=genai.GenerativeModel(model=Config.GEMINI_MODEL)

        context=[]
        if conversation_history:
            recent=conversation_history[-5:]
            context="\n".join([f"previous Q:{item['query']}\n previous A: {[item['answer'][:100]]}" for item in recent])

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
            
        response=model.generate_content(context)
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
    
    try:
        genai.configure(api_key=Config.GEMINI_API_KEY)
        model=genai.GenerativeModel(model=Config.GEMINI_MODEL)

        prompt=f"""Expand this query by adding relevant synonyms and related terms for better document retrieval.

Original query: {query}

Expanded query (keep it concise, under 20 words):"""
        
        response=model.generate_content(prompt)
        expanded=response.text.strip()

        logging.info(f"Query expanded to: '{expanded}'")
        return expanded
    
    except Exception as e:
        logging.exception(f"Query expansion failed: {e}")
        return query
    


