import logging
from retrieval.retriever import retriever_documents, prepare_context_for_llm
from retrieval.reranker import rerank_documents
from llm.generator import generate_answer_with_sources
from orchestrator.query_rewriter import should_rewrite_query, rewrite_query, expand_query
from app.config import Config
from memory.conversation_store import get_conversation_history,add_exchange,get_context_for_llm,resolve_references,create_session,get_current_session_id

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
    
    if not get_current_session_id():
        create_session()

    logging.info("=" * 80)
    logging.info(f" PROCESSING QUERY: {query}")
    logging.info("=" * 80)

    original_query=query
    max_retries=max_retries or Config.MAX_RETRIES
    attempt=0

    query = resolve_references(query)
    logging.info(f"Resolved query: '{query}'")

    conversation_context = get_context_for_llm(last_n=3)

    while attempt<max_retries:
        attempt+=1;
        logging.info(f"attemp : {attempt}/{max_retries}")

        try:

            # stage1: Query Analysis
            if should_rewrite_query(query):
                logging.info("Query needs improvement")
                history = get_conversation_history(last_n=3)
                query=rewrite_query(query,history)
            else:
                logging.info("No re writing needed. query is good")

            # stage2: Retrival
            logging.info("retrival stage...")
            documents=retriever_documents(query,Config.TOP_K)

            if not documents:
                logging.warning("No documents retrived")

                if attempt<max_retries:
                    logging.info("Retrying with expanded query ...")
                    query=expand_query(query)
                    continue
                else:
                    add_exchange(
                        query=original_query,
                        answer="I couldn't find relevant information.",
                        metadata={"status": "no_results"}
                    )
                    return{
                        "answer":"I couldn't find any relevant documents",
                        "sources":[],
                        "status":"no_result",
                        "original_query":original_query,
                        "processed_query":query
                    }
            
            logging.info(f"Retrieved {len(documents)} documents")

            #stage3: Reranking
            if enable_reranking and len(documents)>3:
                logging.info("Reranking stage...")
                documents=rerank_documents(
                    query=query,
                    documents=documents,
                    top_n=min(5,len(documents))
                )
                logging.info(f"Reranked to top {len(documents)} documents")
            
            else:
                logging.info("Skipping the reranking stage")


            #stage 4: Quality check
            quality_score=check_retrieval_quality(query,documents)
            logging.info(f"Retrival Quality score: {quality_score}")

            if quality_score<0.3:
                logging.warning("Low quality retrieval, retrying...")
                query=expand_query(query=query)
                continue

            #stage 5:Answer Generation
            logging.info("Answer Generation stage ....")
            response=generate_answer_with_sources(query=query,documents=documents)

            #stage 6: answer validation
            logging.info("Answer validation stage")
            is_valid=validate_answer(query, response["answer"], documents)

            if not is_valid and attempt<max_retries:
                logging.warning("Answer validation failed, retrying...")
                continue

            logging.info("Query processed successfully")
            
            add_exchange(
                query=original_query,
                answer=response["answer"],
                metadata={
                    "sources": response["sources"],
                    "status": "success",
                    "quality_score": quality_score,
                    "attempts": attempt,
                    "processed_query": query
                }
            )

            return {
                "answer":response["answer"],
                "sources":response["sources"],
                "status":"Success",
                "query":original_query,
                "preocessed_query":query,
                "retrieval_quality": quality_score,
                "attempts": attempt
            }
        except Exception as e:
            logging.error(f"Error in attemp {attempt}:{e}")
            if attempt >= max_retries:
                return {
                    "answer": "I encountered an error while processing your question. Please try again.",
                    "sources": [],
                    "status": "error",
                    "original_query": original_query,
                    "error": str(e)
                }
        
    logging.error("Max retries reached without success")
    return {
        "answer": "I'm having trouble finding a good answer. Please try rephrasing your question.",
        "sources": [],
        "status": "max_retries_reached",
        "original_query": original_query
    }

def check_retrieval_quality(query,documents):
    """Estimate quality of retrieved documents"""

    if not documents:
        return 0.0
    
    query_terms=set(query.lower().split())

    scores=[]
    for doc in documents:
        content_lower=doc.page_content.lower()

        matches=sum(1 for term in query_terms if term in content_lower)
        score=matches/len(query_terms) if len(query_terms)>0 else 0
        scores.append(score)
        
    avg_score=sum(scores)/len(scores) if len(scores) >0 else 0
    return avg_score


def validate_answer(query,answer,documents):
    """Validate that the answer is grounded in the retrieved documents"""

    if len(answer.split())<5:
        logging.warning("Answer is too short")
        return False
    
    dont_know_phrases = [
        "i don't know",
        "i do not know", 
        "no information",
        "cannot answer",
        "unable to answer"
    ]

    answer_lower=answer.lower()

    if any(phrase in answer_lower for phrase in dont_know_phrases):
        logging.info("Answer indicates lack of information")
        return True
    
    # check for answer contain some content from documents
    doc_content=" ".join([doc.page_content for doc in documents]).lower()
    answer_word = set(answer_lower.split())

    # check id at least some answer words appear in documents
    matches =sum(1 for word in answer_word if len(word)>3 and word in doc_content)
    match_ratio=matches/len(answer_word) if answer_word else 0

    if match_ratio<0.1:
        logging.warning(f" Low Answer answer-document overlap: {match_ratio:.2%})")
        return False
    
    logging.info(f"Answer validation passed (overlap: {match_ratio:.2%})")
    return True


def process_simple_query(query):
    """Simplified query processing without retries or validation"""

    if not query:
        return {
            "answer": "Please provide a question.",
            "sources": [],
            "status": "error"
        }
    
    logging.info(f"Processing simple query: {query}")

    try:
        documents=retriever_documents(query,top_k=5)

        if not documents:
            return{
                "answer": "I couldn't find relevant information.",
                "sources": [],
                "status": "no_results"
            }
        
        result=generate_answer_with_sources(query,documents)

        result["status"]="success"
        add_exchange(query=query, answer=result["answer"])

        return result
    
    except Exception as e:
        logging.exception(f"Simple query failed: {e}")
        return{
            "answer": "An error occurred.",
            "sources": [],
            "status": "error"
        }