import logging
import time
from datetime import datetime

_metrics_history=[]

def calculate_retrieval_precision(query, retrieved_docs, relevant_doc_ids):
    """Calculating the precision, that tells us what percentage ofg retrieved docs are relevant?
    Precision=(Relevant Retrieved)/(Total Retrived)
    """

    if not retrieved_docs:
        return 0.0
    
    retrived_ids=[doc.metadata.get("id",doc.metadata.get("source")) for doc in retrieved_docs]

    relevant_count=sum(1 for docs_id in retrived_ids if docs_id in relevant_doc_ids)

    precision=relevant_count/len(retrieved_docs)

    logging.info(f"Retrieval Precision: {precision:.2%} ({relevant_count}/{len(retrieved_docs)})")
    return precision

def calculate_retrieval_recall(query, retrieved_docs, relevant_doc_ids):
    """Calculating the recall, that tells us what percentage of relevant docs were retrived?
        Recall=(Relevant Retrived)/(Total relevant)

    """

    if not relevant_doc_ids:
        return 0.0
    
    retrieved_ids =[doc.metadata.get("id",doc.metadata.get("source")) for doc in retrieved_docs]

    relevant_count=sum(1 for doc_id in relevant_doc_ids if doc_id in retrieved_ids)

    recall=relevant_count/len(relevant_doc_ids)

    logging.info(f"Retrived Recall: {recall:.2%} ({relevant_count}/{len(relevant_doc_ids)})")
    return recall

def calculate_f1_score(precision, recall):
    """Calculating F1 score 
        f1=2*(precision * recall) / (precision +recall)


    """

    if precision+recall ==0:
        return 0.0
    
    f1=2 * (precision*recall)/(precision +recall)

    logging.info(f"F1 score: {f1:.2%}")
    return f1

def calculate_answer_correctness(generated_answer,ground_truth_answer):
    """Simple correctness check.... 'Are key facts present?' """

    if not generated_answer or not ground_truth_answer:
        return 0.0
    
    gen_lower=generated_answer.lower()
    truth_lower=ground_truth_answer.lower()

    truth_words=set(word for word in truth_lower.split() if len(word)>3)

    if not truth_words:
        return 0.0
    
    matches = sum(1 for word in truth_words if word in gen_lower)

    correctness = matches/len(truth_words)

    logging.info(f"Answer Correctness: {correctness:.2%} ({matches}/{len(truth_words)} key terms)")

    return correctness

def calculate_answeer_faithfullness(answer,source_documents):
    """Faithfulness: is answer grounded in source documnets?"""

    if not answer or not source_documents:
        return 0.0
    
    source_text = " ".join([doc.page_content for doc in source_documents]).lower()

    answer_words=set(word for word in answer.lower().split() if len(word)>3)

    if not answer_words:
        return 0.0
    
    grounded_words =sum(1 for word in answer_words if word in source_text)

    faithfulness=grounded_words/len(answer_words)

    logging.info(f"Answer Faithfulness: {faithfulness:.2%} ({grounded_words}/{len(answer_words)} words grounded)")

    return faithfulness

def measure_latency(func, *args,**kwargs):
    """Measure how long a function takes to execute"""

    start_time=time.time()
    result=func(*args,**kwargs)
    end_time=time.time()

    latency=end_time-start_time

    logging.info(f"Function '{func.__name__}' took {latency:.3f}s")
    return result,latency

def calculate_system_metrics(query,retrieved_docs,answer,ground_truth_docs=None,ground_truth_answer=None,retrieval_time=None,generation_time=None):

    """Calculate comprehensive system metrics"""

    metrics = {
        "query": query,
        "timestamp": datetime.now().isoformat(),
        "num_retrieved": len(retrieved_docs) if retrieved_docs else 0,
        "answer_length": len(answer.split()) if answer else 0
    }

    # Retrieval metrics
    if ground_truth_docs:
        precision=calculate_retrieval_precision(query,retrieved_docs,ground_truth_docs)
        recall=calculate_retrieval_recall(query,retrieved_docs,ground_truth_docs)
        f1 =calculate_f1_score(precision,recall)

        metrics["retrieval_precision"]=precision
        metrics["retrieval_recall"]=recall
        metrics["retrieval_f1"]=f1

    if retrieved_docs:
        faithfulness=calculate_answeer_faithfullness(answer,retrieved_docs)
        metrics["answer_faithfulness"]=faithfulness

    if ground_truth_answer:
        correctness=calculate_answer_correctness(answer,ground_truth_answer)
        metrics["answer_correctness"]=correctness

    if retrieval_time:
        metrics["retrieval_time_seconds"]=retrieval_time

    if generation_time:
        metrics["generation_time_seconds"]=generation_time

    if retrieval_time and generation_time:
        metrics["total_time_seconds"]=retrieval_time+generation_time

    _metrics_history.append(metrics)

    logging.info(f"System metrics calculate: {metrics}")
    return metrics

def get_average_metrics():
    """Calculate average metrics across all recorded evaluations"""

    if not _metrics_history:
        logging.warning("No metrics history available")
        return {}
    
    numeric_keys=[
        "retrieval_precision", "retrieval_recall", "retrieval_f1",
        "answer_faithfulness", "answer_correctness",
        "retrieval_time_seconds", "generation_time_seconds", "total_time_seconds"
    ]

    averages={}

    for key in numeric_keys:
        values=[m[key] for m in _metrics_history if key in m]

        if values:
            averages[f"avg_{key}"]=sum(values)/len(values)

    averages["total_queries"]=len(_metrics_history)

    logging.info(f"Average metrics: {averages}")
    return averages

def print_metrics_summary(metrics):
    """Pretty print metrics summary"""

    print("\n"+"="*80)
    print("EVALUATION METRICS SUMMARY")
    print("=" *80)

    if "retrieval_precision" in metrics:
        print("\n Retrieval Metrics:")
        print(f"Precision: {metrics['retrieval_precision']:.2%}")
        print(f"Recall: {metrics['retrieval_recall']:.2%}")
        print(f"F1 Score: {metrics['retrieval_f1']:.2%}")

    print("\n Answer Metrics:")
    if "answer_faithfulness" in metrics:
        print(f"Faithfulness: {metrics['answer_faithfulness']:.2%}")

    if "answer_correctness" in metrics:
        print(f"Correctness: {metrics['answer_correctness']:.2%}")

    if "retrieval_time_seconds" in metrics or "generation_time_seconds" in metrics:
        print("\n Latency Metricd:")
        if "retrieval_time_seconds" in metrics:
            print(f"Retrieval: {metrics['retrieval_time_seconds']:.3f}s")
        if "generation_time_seconds" in metrics:
            print(f"Generation: {metrics['generation_time_seconds']:.3f}s")
        if "total_time_seconds" in metrics:
            print(f"Total: {metrics['total_time_seconds']:.3f}s")

    print("\n"+"="*80+"\n")


def evaluate_rag_pipeline(query,process_func,ground_truth_docs=None,ground_truth_answer=None):
    """Evaluate entire Rag Pipeline"""

    logging.info(f"Evaluating pipeline for query: '{query}'")

    start_time=time.time()
    result=process_func(query)
    end_time=time.time()
    total_time=end_time-start_time

    answer=result.get("answer","")
    sources=result.get("sources",[])

    retrieved_docs=result.get("documents",[])

    metrics=calculate_system_metrics(query=query,retrieved_docs=retrieved_docs,answer=answer,ground_truth_docs=ground_truth_docs,ground_truth_answer=ground_truth_answer,generation_time=total_time)

    metrics["pipeline_status"]=result.get("status","unknown")

    print_metrics_summary(metrics=metrics)

    return metrics

def reset_metrics_history():
    """Clear metrics history"""

    global _metrics_history
    count=len(_metrics_history)
    _metrics_history=[]
    logging.info(f"Cleared {count} metric records")


def get_metrics_history():
    """Get all stored metrics."""
    return _metrics_history.copy()

    