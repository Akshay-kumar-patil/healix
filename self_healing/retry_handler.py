import logging
import time
import traceback
from orchestrator.query_rewriter import expand_query

def retry_with_backoff(func,max_attempts=3,inital_delay=1.0,backoff_factor=2.0,*args,**kwargs):
    """retry a function with exponential backoff"""
    
    attempt=0
    delay=inital_delay
    last_exception=None

    while attempt<max_attempts:
        attempt+=1

        try:
            logging.info(f"Attempt {attempt}/{max_attempts}...")
            result=func(*args,**kwargs)
            logging.info(f"Success on attempt {attempt}")
            return result
        
        except Exception as e:
            last_exception=e
            logging.warning(f"Attempt {attempt} failed: {e}")
            traceback.print_exc() 

            if attempt<max_attempts:
                logging.info(f"retrying in {delay:.1f}s...")
                time.sleep(delay)
                delay*=backoff_factor
                
            else:
                logging.error(f"All {max_attempts} attempt failed")

    raise last_exception

def retry_with_modifications(func,modify_func,max_attempts=3,inital_delay=1.0,backoff_factor=2.0,*args,**kwargs):
    """retry a function with modification between attempts"""

    attempt=0
    current_args=list(args)
    current_kwargs=kwargs.copy()

    while attempt<max_attempts:
        attempt+=1
        
        try:
            logging.info(f"Attempt {attempt}/{max_attempts}...")

            result=func(*current_args,**current_kwargs)
            logging.info(f"Success on attempt {attempt}")
            return result

        except Exception as e:
            logging.warning(f"Attempt {attempt} failed: {e}")

            if attempt <max_attempts:
                logging.info("Modifying parameters for retry...")
                current_args,current_kwargs=modify_func(current_args,current_kwargs,attempt)

            else:
                logging.error("All attempts exhausted")
                raise

def retry_retrieval(query,retrieval_func,max_attempt=3):
    """Retry retrieval with query modification"""
    attempt=0
    current_query=query
    while attempt<max_attempt:
        attempt+=1
        logging.info(f"Retrieval attempt {attempt}/{max_attempt} with query: '{current_query}'")

        try:
            documents =retrieval_func(current_query)

            if documents is not None and len(documents) > 0:
                logging.info(f"Retrieved {len(documents)} documents on attempt {attempt}")
                return documents
            
            else:
                logging.warning("No Documents retrived")

                if attempt <max_attempt:

                    logging.info("Expanding query for retry...")
                    current_query=expand_query(current_query)

        except Exception as e:
            logging.exception(f"Retrival attempt {attempt} failed: {e}")

            if attempt >=max_attempt:
                raise
        
    logging.warning("All retrieval attempts returned no result")
    return []

def retry_generation(query, context, generation_func,max_attempts=2):
    """Retry answer generation"""

    attempt=0
    while attempt<max_attempts:
        attempt+=1
        logging.info(f"Generation attempt {attempt}/{max_attempts}")

        try:
            answer=generation_func(query,context)

            if answer and len(answer.strip())>5:
                logging.info(f"generated answer on attempt {attempt}")    
                return answer
            
            else:
                logging.warning("Generated answer too short")

                if attempt>=max_attempts:
                    return "I apologize, but I couldn't generate a satisfactory answer."
            
        except Exception as e:
            logging.exception(f"Generation attempt {attempt} failed: {e}")
            traceback.print_exc()

            if attempt>=max_attempts:
                return "I encountered an error while generating the answer."
        
    return "Failed to generate answer after multiple attempts"
    
def should_retry(validation_result):
    """Determine if a retry is warranted based on validation"""
    if not validation_result:
        return False
    
    if validation_result.get("is_valid",False):
        logging.info("Validation passed - no retry needed")
        return False
    
    confidence=validation_result.get("confidence",0)

    if confidence<0.3:
        logging.info(f"Low confidence ({confidence:.2f}) - retyr recommended")
        return True
    
    issues=validation_result.get("issues",[])

    no_retry_issues=["No source documents","Honest 'don't know' response"  ]

    for issue in issues:
        if any(no_retry in issue for no_retry in no_retry_issues):
            logging.info(f"issue '{issue}' -retry not helpful")
            return False
        
    logging.info("Validation failed -retry recommended")
    return True