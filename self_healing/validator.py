import logging
from app.config import Config
import google.generativeai as genai

def validate_retrieval_quality(query,documents, min_score=0.3):
    """Validate if retrived documents are good eouugh"""

    if not documents:
        return {
            "is_valid": False,
            "score":0.0,
            "reason":"No Documents retrived"
        }
    
    query_terms=set(query.lower().split())
    scores=[]

    for doc in documents:
        content_lower=doc.page_content.lower()
        matches=sum(1 for term in query_terms if term in content_lower)
        score=matches/len(query_terms) if query_terms else 0

        scores.append(score)

    avg_score=sum(scores)/len(scores) if scores else 0

    is_valid=avg_score >= min_score

    result={
        "is_valid":is_valid,
        "score":avg_score,
        "reason":"Quality sufficient" if is_valid else f"Low quality (score: {avg_score:.2f})"

    }

    logging.info(f"Retrieval validation :{result}")
    return result

def validate_answer_quality(query,answer,documnets):
    """Validate if the generated answer is acceptable."""
    
    issues=[]

    if not answer or len(answer.split()) <5:
        issues.append("Answer too short")

    generic_phrases=[
        "as an ai",
        "i'm just a",
        "i cannot provide",
        "please consult"
    ]

    answer_lower=answer.lower()
    for phrase in generic_phrases:
        if phrase in answer_lower:
            issues.append(f"Contains generic phrases: '{phrase}'")

    dont_know_phrases=[
        "i don't know",
        "i do not know",
        "no information",
        "not enough information"
    ]

    says_dont_know=any(phrase in answer_lower for phrase in dont_know_phrases)

    if says_dont_know:
        return {
            "is_valid": True,
            "issues": [],
            "confidence": 0.5,
            "reason": "Honest 'don't know' response"
        }
    
    if documnets:
        doc_content=" ".join([doc.page_content for doc in documnets]).lower()
        answer_words=set(answer_lower.split())

        matches=sum(1 for word in answer_words if len(word)>3 and word in doc_content)
        overlap_ratio=matches/len(answer_words) if answer_words else 0

        if overlap_ratio <0.1:
            issues.append(f"Low documents overlap ({overlap_ratio:.1%})")
        
        confidence=min(overlap_ratio*2,1.0)

    else:
        confidence=0.0
        issues.append("No source documents")

    is_valid=len(issues)==0
    result={
        "is_valid": is_valid,
        "issues": issues,
        "confidence": confidence,
        "reason": "Valid answer" if is_valid else f"Issues: {', '.join(issues)}"
    }
    logging.info(f"Answer validation: {result}")
    return result

def validate_with_llm(query,answer,context):
    """Use LLM to validate if answer matches the context"""

    logging.info("Running LLM-based Validation...")

    try:
        genai.configure(api_key=Config.GEMINI_API_KEY)
        model=genai.GenerativeModel(model_name=Config.GEMINI_MODEL)

        validation_prompt=f"""You are a validation assistant. Determine if the answer directly addresses the question using ONLY the provided context.

Question: {query}

Context: {context[:1000]}...

Answer: {answer}

Does the answer correctly address the question using only the context? 
Respond with ONLY: VALID or INVALID

Response:"""
        
        response=model.generate_content(validation_prompt)
        result_text=response.text.strip().upper()

        is_valid="VALID" in result_text

        result={
            "is_valid": is_valid,
            "reason": "LLM validation passed" if is_valid else "LLM validation failed"
        }


        logging.info(f"LLM Validation result: {result}")
        return result
    
    except Exception as e:
        logging.exception(f"LLM validation result: {result}")
        return {
            "is_valid":True,
            "reason":"Validation error -defaulting to valid"
        }
    
def check_response_health(query,answer,documents):
    """Comprehensive health check of the entire response."""

    logging.info("Running comprehensive health check...")

    #running all validation
    retrieval_check=validate_retrieval_quality(query,documents=documents)
    answer_check=validate_answer_quality(query,answer,documents)

    all_valid=retrieval_check["is_valid"] and answer_check["is_valid"]

    health_report={
        "is_healthy":all_valid,
        "retrieval":retrieval_check,
        "answer": answer_check,
        "overall_confidence": (retrieval_check["score"] + answer_check["confidence"]) / 2
    
    }

    if all_valid:
        logging.info("Respone health check PASSED")
        
    else:
        logging.warning(f"Response health check FAILED: {health_report}")

    return health_report
