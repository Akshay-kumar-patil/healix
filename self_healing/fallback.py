import logging

def get_fallback_answer(query,failure_reason="unknown"):
    """Provide a fallback answer all else fails"""

    logging.warning(f"using fallback. Reason: {failure_reason}")

    if "no documents" in failure_reason.lower():
        return (
            "I couldn't find relevant information in my knowledge base to answer your question. "
            "This might be because:\n"
            "- The topic isn't covered in the available documents\n"
            "- The question is phrased in a way I don't recognize\n\n"
            "Try rephrasing your question or asking about a different topic."
        )
    
    elif "quality" in failure_reason.lower():
        return (
            "I found some information, but I'm not confident it fully answers your question. "
            "Could you please rephrase or provide more context?"
        )
    
    elif "error" in failure_reason.lower():
        return (
            "I encountered a technical issue while processing your question. "
            "Please try again in a moment."
        )
    
    else:
        return (
            "I'm having trouble answering this question right now. "
            "Please try:\n"
            "- Rephrasing your question\n"
            "- Breaking it into smaller questions\n"
            "- Asking about a different topic"
        )
    
def get_cached_response(query, cache=None):
    """try to retrive a cached respone for similar queries"""

    if not cache:
        return None;

    query_lower=query.lower().strip()
    if query_lower in cache:
        logging.info("Found Exact cache match")
        return cache[query_lower]

    for cached_query,cached_response in cache.items():
        if _queries_similar(query_lower, cached_query):
            logging.info(f"Found similar cached query: '{cached_query}'")
            return cached_response
        
    logging.info("No cached response found")
    return None

def _queries_similar(query1,query2,threshold=0.7):
    """similarity chech between two queries"""
    words1=set(query1.split())
    words2=set(query2.split())

    if not words1 or not words2:
        return False
    
    intersection=len(words1 & words2)
    union=len(words1 |words2)

    similarity= intersection/union if union >0 else 0
    return similarity>=threshold

def provide_partial_answer(documents,query):
    """Provide a partial answer using available documents even if incomplete"""

    if not documents:
        return None
    
    logging.info("Attempting to provide partial answer from available documents")

    snippets=[]
    query_terms=set(query.lower().split())

    for doc in documents[:3]:
        content=doc.page_content
        content_lower=content.lower()

        has_terms=any(term in content_lower for term in query_terms)

        if has_terms:
            snippet=content[:200]+"..."
            source=doc.metadata.get("source","Unknown")
            snippets.append(f"from {source}: {snippet}")


    if snippets:
        partial = (
            "I found some potentially relevant information, though I'm not fully confident:\n\n" +
            "\n\n".join(snippets) +
            "\n\nPlease verify this information and consider rephrasing your question for a better answer."
        )

        logging.info("Constructed partial answer")
        return partial
    
    return None

def suggest_alternative_queries(query):
    """suggest alternative ways to phrase the query"""

    suggestions=[]

    suggestions.append(f"What specific aspect of {query} are you interested in?")

    if len(query.split())>5:
        suggestions.append("Try breaking your question into smaller parts")

    suggestions.append(f"Could you provide more context about {query}?")

    logging.info(f"Generated {len(suggestions)} query suggestions")

    return suggestions


_response_cache={}

def cache_response(query,response):
    """cache a successful response"""
    query_key =query.lower().strip()
    _response_cache[query_key]=response
    logging.info(f"Cached response for: '{query}'")

def get_from_cached(query):
    """retrive from cache"""
    return get_cached_response(query,_response_cache)