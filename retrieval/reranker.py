import logging
from langchain_core.documents import Document
from app.config import Config
from sentence_transformers import CrossEncoder

def rerank_documents(query,documents,top_n=None):
    """re-rank retrived documents to put the most relevant ones first"""

    if not documents:
        logging.warning("No documents to re-rank")
        return []
    
    if not query:
        print("No query provided, returning original documents")
        logging.warning("No query provided, returning original documents")
        return documents
    
    logging.info(f"Ranking {len(documents)} documents...")
    
    try:
        scores_doc=[]

        for doc in documents:
            scores=calculate_relevance_score(query,doc.page_content)
            scores_doc.append((doc, scores))

        
        scores_doc.sort(key=lambda x:x[1],reverse=True)

        reranked=[doc for doc,scores in scores_doc]

        if top_n:
            reranked=reranked[:top_n]

        logging.info(f"Reranking complete. Returning top {len(reranked)} documents...")
        return reranked
    
    except Exception as e:
        logging.error(f"Reranking failed: {e}")
        return documents
    

def calculate_relevance_score(query,content):
    """calculate how documents are relevant to query"""

    query_lower=query.lower()
    content_lower=content.lower()

    query_word=query_lower.split()


    scores =0.0
    # if ecxact phrasesd matches
    if query_lower in content_lower:
        scores+=10.0

    #  count matching keywords
    for word in query_word:
        if  len(word)>2:
            count=content_lower.count(word)     # count how many times the word appears
            scores+=count*2.0
    

    #  for multiple query word appearing together

    consecutive_matches=0
    for i in range(len(query_word)-1):
        if query_word[i] in content_lower and query_word[i+1] in content_lower:
            consecutive_matches +=1

    scores+=consecutive_matches *3.0

    # penalty for very large docs
    if len(content)> 2000:
        scores-=1.0
        
    return scores

def rerank_with_cross_encoder(query,documents,model_name=Config.CROSS_ENCODER_MODEL,top_n=None):
    """rerank using a cross encoder model"""
    
    if not documents:
        logging.warning("No documents to rerank")
        return []
    
    if not query:
        logging.warning("No query provided, returning original documents")
        return documents
    
    logging.info(f"Reraning using Cross-Encoder model: {model_name}")

    try:

        model=CrossEncoder(model_name)

        pairs=[[query,doc.page_content] for doc in documents]

        scores = model.predict(pairs)
        
        # paking the pair 
        scores_doc=list(zip(documents,scores))

        scores_doc.sort(key=lambda x:x[1],reverse=True)

        reranked=[doc for doc,scores in scores_doc]

        if top_n:
            reranked=reranked[:top_n]

        print("Cross-Encoder reranking complete")
        logging.info(f"Cross-Encoder reranking complete")
        return reranked
    
    except ImportError:
        logging.warning("sentence-transformers not installed. Install with: pip install sentence-transformers")
        logging.info("Falling back to simple reranking...")
        return rerank_documents(query, documents, top_n)                                        
    
    except Exception as e:
        print(f"Cross-Encoder reranking failed: {e}")
        logging.error(f"Cross-Encoder reranking failed: {e}")
        return documents
    
def show_reranked_scores(query,scored_docs):
    """print reranked results with scores"""

    if not scored_docs:
        print("\n No Documents to display \n")
        return
    
    print("\n" + "=" * 80)
    print(f" QUERY: {query}")
    print("=" * 80)
    print(f"\n RERANKED RESULTS (Top {len(scored_docs)}):\n")                                                           

    for i ,(docs,scores) in enumerate(scored_docs,start=1):
        source=docs.metadata.get("source","unknown")
        page=docs.metadata.get("page","N/A")

        print(f"Rank {i} | source: {scores:.4f}")
        print(f" Source: {source} | Page: {page}")
        print(f" Content : {docs.page_content[:150]}...")
        print("-"*80)
    
    print()