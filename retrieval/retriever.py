from langchain_chroma import Chroma
from ingestion.embedding import embedding_model
import logging
import os
from app.config import Config

def retriever_documents(query,top_K=None):
    """Search for relevant documents based on user query"""

    if not query:
        logging.error("Query is empty")
        return []
    
    logging.info(f"Searching for: '{query}")

    # loading the vetore db
    try:
        vector_store_path= os.path.join("vector_store","chroma_db")

        if not os.path.exists(vector_store_path):
            logging.error(f"Vector store not found! please run ingetion first")
            return []
        
        #loading embedding model
        embeddings=embedding_model()    

        #load vector db
        vectore_db=Chroma(
            persist_directory=vector_store_path,
            embedding_function=embeddings
        )

        logging.info("vector database loaded")

    except Exception as e:
        logging.error(f"Failed to load database: {e}")
        return []
    
    
    #search for documents

    try:
        if top_K:
            k=top_K
        else:
            k=Config.TOP_K
        
        documents=vectore_db.similarity_search(query=query,k=k)
        
        if not documents:
            logging.error(f"No relevant documents find for this query: '{query}")
            return []

        logging.info(f"Found {len(documents)} documents")
        return documents
    
    except Exception as e:
        logging.error(f"Search failed: {e}")
        return []
    

def retriver_with_scores(query,top_k=None):
    """Search for documents and gert there similarity score"""

    if not query:
        logging.error("Query is empty")
        return []
    
    logging.info(f"Searching with scores for: '{query}'")
        
    try: 
        vector_store_path = os.path.join(Config.CHROMA_DIR, "chroma_db")
        embedding=embedding_model()

        vector_db=Chroma(
            persist_directory=vector_store_path,
            embedding_function=embedding
        )

        if top_k:
            k=top_k
        else:
            k=Config.TOP_K
        documents=vector_db.similarity_search_with_score(query=query,k=k)

        logging.info(f"Found{len(documents)} documents")
        return documents
    
    except Exception as e:
        logging.error(f"Search with score failed: {e}")
        return []
    

def show_result(documents):
    """print documents in a nice format"""

    if not documents:
        print("\n No documents found \n")
        return
    
    print("\n"+"="*80)
    print(f"Found {len(documents)} documents")
    print("="*80+"\n")

    for i, doc in enumerate(documents,start=1):
        source=doc.metadata.get("source","unknown")
    
        page=doc.metadata.get("page","N/A")

        print(f" Documnet {i}")
        print(f" Source: {source}")
        print(f" page:{page}")
        print(f" {doc.page_content[:300]}...")
        print("-"*80+"\n")


def prepare_context_for_llm(documents):
    """convert retrived documents into text format for the llm"""

    if not documents:
        return "No relevant information found"
    
    context=[]
    for i,doc in enumerate(documents,start=1):
        source=doc.metadata.get("source","unknown")
        page=doc.metadata.get("page","N/A")

        context.append(
            f"----Document {i} ---\n"
            f"Source: {source} | Page: {page}\n"
            f"{doc.page_content}\n"
        )

    return "\n".join(context)