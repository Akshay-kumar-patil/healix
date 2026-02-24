import logging
from llm.prompt_templates import RAG_PROMPT
from google.genai import types
from app.config import Config
from google import genai
def generate_answer(query, context):
    """generatesw answer from gemini """

    if not query:
        logging.error("No query provided.")
        return "Please provide a question"
    
    if not context:
        logging.warning("No ccontext provided - cannot answer")
        return "I don't have enough knowledge to answer this question"
    
    logging.info("Generating answer for your query")

    try:
        client = genai.Client(api_key=Config.GEMINI_API_KEY)

        prompt = RAG_PROMPT.format(
            context=context,
            question=query
        )
        
        logging.debug(f"Prompt length: {len(prompt)} characters")

        response = client.models.generate_content(
            model=Config.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=Config.TEMPERATURE,
                top_p=0.95,
                top_k=40,
                max_output_tokens=1024,
            ),
        )

        answer=response.text

        logging.info("Answer generated Successfully")
        logging.debug(f"Answer prevview: {answer[:100]}...")


        return answer.strip()
    
    except Exception as e:
        logging.exception(f"Answer generation failed: {e}")
        return "Sorry, I encountered an error while generating the answer."
    
def generate_answer_with_sources(query,documents):
    """generate answer and include source citations"""


    if not documents :
        return {
            "answer": "I dont't have enough information to answer this question",
            "sources":[]
        }
    
    try:
        context_parts=[]
        sources=[]

        for i, doc in enumerate(documents,start=1):
            source=doc.metadata.get("source", "unknown")
            page=doc.metadata.get("page","N/A")

            context_parts.append(f"[source {i}] {doc.page_content}")
            sources.append({"source":source,"page":page})

        context="\n\n".join(context_parts)

        answer=generate_answer(query=query,context=context)

        return {
            "answer":answer,
            "sources":sources
        }
    
    except Exception as e:
        logging.exception(f"Generation with sources failed: {e}")
        return {
            "answer": "Sorry, I encountered an error.",
            "sources": []
        }