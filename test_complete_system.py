import sys
import os
import time
import traceback
#config
from app.config import Config
# ingestion 
from ingestion.embedding import embedding_model
from ingestion.loader import load_csv,load_docx,load_pdf,load_url
import requests
from ingestion.chunking import chunk_documents
from ingestion.vectordb import create_vectordb, load_vectordb
# retrieval
from retrieval.retriever import retriever_documents
# reranking
from retrieval.reranker import rerank_documents
# generation
from llm.generator import generate_answer
# memory store
from memory.conversation_store import create_session, add_exchange, get_conversation_history,get_last_query,resolve_references,clear_session
# query rewriter
from orchestrator.query_rewriter import should_rewrite_query, rewrite_query
# validation
from self_healing.validator import validate_retrieval_quality, validate_answer_quality
#  utils
from utils.helpers import safe_divide, truncate_text, clean_text, format_sources, extract_keywords
# orchestrator
from orchestrator.controller import process_query


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

class Symbols:
    CORRECT='✓'
    CROSS='✗'
    WARNING='⚠'
    INFO='ℹ'


def print_header(text):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{' '*29}{Colors.BOLD}{Colors.GREEN}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}\n")

def print_success(text):
    """Print sucess message"""
    print(f"{Colors.GREEN}{Symbols.CORRECT} {text}{Colors.END} ")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}{Symbols.CROSS} {text}{Colors.END}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}{Symbols.WARNING} {text}{Colors.END}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}{Symbols.INFO} {text}{Colors.END}")


class TestResults:
    """Track test results"""
    def __init__(self):
        self.passed=0
        self.failed=0
        self.skipped=0
        self.errors =[]

    def add_pass(self,test_name):
        self.passed+=1
        print_success(f"{test_name} -PASSED")

    def add_fail(self,test_name,error):
        self.failed+=1
        self.errors.append((test_name,error))
        print_error(f"{test_name} -FAILED: {error}")
    
    def add_skip(self, test_name, reason):
        self.skipped +=1
        print_warning(f"{test_name} -SKIPPED: {reason}")

    def print_summary(self):
        """printing summary"""
        total  =self.passed+self.failed +self.skipped
        print_header("TEST SUMMARY")
        print(f"Total tests: {total}")
        print_success(f"Passed: {self.passed}")
        print_error(f"Failed: {self.failed}")
        print_warning(f"Skipped: {self.skipped}")

        if self.failed>0:
            print(f"\n{Colors.BOLD}Failed Tests:{Colors.END}")
            for test_name,error in self.errors:
                print(f" - {test_name}: {error}")

        success_rate=(self.passed/total*100) if total>0 else 0

        print(f"\n{Colors.BOLD}Success Rate: {success_rate:.1f}%{Colors.END}")


results=TestResults()


# Config Testing ---------------------------------------------------------------------
def test_config():
    """Test configuration loading"""
    print_header("Test 1: Configuration")

    try:
        
        assert hasattr(Config, "GEMINI_API_KEY"), "Missing GEMINI_API_KEY"
        assert hasattr(Config, "GEMINI_MODEL"), "Missing GEMINI_MODEL"
        assert hasattr(Config, "EMBEDDING_MODEL"), "Missing EMBEDDING_MODEL"
        assert hasattr(Config, "CHUNK_SIZE"), "Missing CHUNK_SIZE"
        assert hasattr(Config, "TOP_K"), "Missing TOP_K"

        print_info(f"GEMINI_MODEL: {Config.GEMINI_MODEL}")
        print_info(f"EMBEDDING_MODEL: {Config.EMBEDDING_MODEL}")
        print_info(f"CHUNK_SIZE: {Config.CHUNK_SIZE}")
        print_info(f"TOP_K: {Config.TOP_K}")

        results.add_pass("Config Loading")
        return True
    
    except Exception as e:
        results.add_fail("Config Loading", str(e))
        return False
    

#  Embedding model--------------------------------------------------------------
def test_embedding_model():
    """Testing embedding model loading"""

    print_header("Test 2: Embedding Model")

    try:
        print_info("Loading embedding model....")
        model=embedding_model()
        
        assert model is not None, "Model is None"

        test_text="This is a test sentence for embedding"
        embedding = model.embed_query(test_text)

        assert len(embedding) >0, "Empty embedding"
        print_info(f"Embedding dimesion: {len(embedding)}")

        results.add_pass("Embedding model")
        return model
    
    except Exception as e:
        results.add_fail("Embedding Model",str(e))
        return None
    

# Documents loader-------------------------------------------------------------
def test_loaders():
    """Test documents loaders"""
    print_header("Test 3: Documents Loader")

    # PDF
    try:
        print("PDF Loader")
        pdf_path="docs\\attention-is-all-you-need.pdf"

        if os.path.exists(pdf_path):
            print_info(f"Testing PDF loader with: {pdf_path}")
            docs=load_pdf(pdf_path)
            assert len(docs)>0 ,"No documents loaded"
            print_info(f"Loaded {len(docs)} pages")
            print_info(f"first page preview: {docs[0].page_content[:50]}...")
            results.add_pass("PDF Loader")
        else:
            results.add_skip("PDF Loader", f"File not found: {pdf_path}")

    except Exception as e:
        results.add_fail("PDF Loader",str(e))

    # CSV
    try:
        print("CSV loader")
        csv_path="docs\\cereal.csv"

        if os.path.exists(csv_path):
            print_info(f"Testing CSV Loader with: {csv_path}")
            docs=load_csv(csv_path)
            assert len(docs)>0,"No Csv documents loaded"
            print_info(f"Loaded {len(docs)} pages")
            print_info(f"First page preview: {docs[0].page_content[:50]}...")
            results.add_pass("CSV Loader")
        else:
            results.add_skip("CSV Loader", f"File not Found: {csv_path}")
        
    except Exception as e:
        results.add_fail("CSV Loader",str(e))

    # docx
    try:
        print("DOCX loader")
        docx_path="docs\\test.docx"

        if os.path.exists(docx_path):
            print_info(f"Testing DOCX Loader with: {docx_path}")
            docs=load_docx(docx_path)
            assert len(docs)>0,"No DOCX documents loaded"
            print_info(f"Loaded {len(docs)} pages")
            print_info(f"First page preview: {docs[0].page_content[:50]}...")
            results.add_pass("DOCX Loader")
        else:
            results.add_skip("DOCX Loader", f"File not Found: {docx_path}")
        
    except Exception as e:
        results.add_fail("DOCX Loader",str(e))


    # URL
    try:

        
        print_info("Testing URL loader...")
        
        test_url = 'https://www.geeksforgeeks.org/artificial-intelligence/artificial-intelligence/'
        
        try:
            print_info(f"Checking URL accessibility: {test_url}")
            response = requests.head(test_url, timeout=5, allow_redirects=True)
            
            if response.status_code == 200:
                print_info(f"URL accessible (Status: {response.status_code})")
                
                docs = load_url(test_url)
                
                assert docs is not None, "load_url returned None"
                assert len(docs) > 0, "No documents loaded"
                
                print_info(f"Loaded {len(docs)} page(s)")
                print_info(f"Page preview: {docs[0].page_content[:100]}...")
                
                results.add_pass("URL Loader")
            else:
                results.add_skip("URL Loader", f"URL returned status {response.status_code}")
        
        except requests.RequestException as e:
            results.add_skip("URL Loader", f"Network error: {str(e)[:50]}")
        
    except ImportError:
        results.add_skip("URL Loader", "requests library not installed")
        
    except Exception as e:
        results.add_fail("URL Loader", str(e))  # FIXED: Was str[0]
        traceback.print_exc()
            

# Chunking ----------------------------------------------------------------------
def test_chunking():
    """Test documents chunking"""
    print_header("TEST 4: Documents Chunking")

    try:
        pdf_path="docs\\attention-is-all-you-need.pdf"

        if not os.path.exists(pdf_path):
            results.add_skip("Chunking","PDF file not found")
            return None
        
        print_info("Loading and chunking documents...")
        docs=load_pdf(pdf_path)
        chunks=chunk_documents(docs)
        
        assert len(chunks) >0,"No chunks created"
        assert len(chunks[0].page_content) >100, "Chunks too small"

        print_info(f"Created {len(chunks)} chunks")
        print_info(f"First chunk size: {len(chunks[0].page_content)} chars")

        results.add_pass("Documents Chunking")
        return chunks
    
    except Exception as e:
        results.add_fail("Documents Chunking",str(e))
        traceback.print_exc()
        return None

# Vector Store---------------------------------------------------------------
def test_vector_store(chunks):
    """Test vector store creation and loading"""
    print_header("TEST 5: Vector Store")

    if chunks is None:
        results.add_skip("vector store creation","No chunks available")
        return False
    
    try:
        print_info("Crearting vector store with test chunks...")
        test_chunks =chunks[:10]

        vector_store=create_vectordb(test_chunks)
        assert vector_store is not None, "Vector store is None"
       
        print_info("Vector store is created successfully")
        results.add_pass("vector store creation")

        print_info("Testing vector store loading...")
        loaded_store=load_vectordb()
        assert loaded_store is not None, "Failed to load vector store"

        results.add_pass("Vector store loading")
        return True
    
    except Exception as e:
        results.add_fail("Vector Store",str(e))
        traceback.print_exc()
        return False


#  Retrieval--------------------------------------------------------------------------
def test_retrieval():
    """Test documents retrieval"""
    print_header("TEST 6: Document RETRIEVAL")

    try:
        if not os.path.exists("vector_store/chroma_db"):
            results.add_skip("Retrieval","No vector store found")
            return None
        
        print_info("Testing documents retrieval...")
        query= "What is attention mechanism?"
        docs=retriever_documents(query,top_K=3)

        assert docs is not None, "No documents returned"
        assert len(docs) <=3, f"Too many documents returned: {len(docs)}"

        print_info(f"Retrieved {len(docs)} documents")
        for i, doc in enumerate(docs,1):
            print_info(f"Doc {i}: {doc.page_content[:80]}...")

        results.add_pass("Documents Retrieval")
        return docs

    except Exception as e:
        results.add_fail("Document Retrieval", str(e))
        traceback.print_exc()
        return None
    
# Reranking-----------------------------------------------------------------------
def test_reranking(docs):
    """Test documents reranking"""
    print_header("Test 7: Documents Reranking")

    if docs is None or len(docs)==0:
        results.add_skip("Reranking","No documents available ")
        return
    
    try:
        print_info("Testing documents reranking....")
        query="attention mechanism"
        reranked=rerank_documents(query,docs,top_n=2)

        assert reranked is not None, "Reranking returned None"
        assert len(reranked)<=2, f"Wrong number of documents: {len(reranked)}"

        print_info(f"Reranked to top {len(reranked)} documents")
        results.add_pass("Documents Reranking")

    except Exception as e:
        results.add_fail("Documets Reranking", str(e))
        traceback.print_exc()


# LLM Generation---------------------------------------------------------------------
def test_generation():
    """Test answer generation"""

    print_header("Test 8: Answer generation")

    try:
        print_info("Testing answer generation")
        query="What is machine learning?"
        context="Machine learning is a subset of artificial intelligence that enables systems to learn from data."

        answer=generate_answer(query=query, context=context)

        assert answer is not None, "No answer generated"
        assert len(answer) >10,"Answer too short"

        print_info(f"Generated answer: {answer[:100]}....")
        results.add_pass("Answer Genration")

    except Exception as e:
        results.add_fail("Answer Generation", str(e))
        traceback.print_exc()

# Conversation Memory----------------------------------------------------
def test_memory():
    """Test conversation memory"""
    print_header("Test 9: Convesation Histroy")

    try:
        print_info("Creating session...")
        session_id=create_session()
        assert session_id is not None, "Session ID is None"
        results.add_pass("Session Creation")

        print_info("Adding exchanges...")
        add_exchange("What is AI?", "AI is artificial intelligence")
        add_exchange("How does it work?", "AI uses machine learning algorithms")

        history=get_conversation_history()
        assert len(history) ==2, f"Wrong history length: {len(history)}"
        results.add_pass("Add Exchange")

        last_q=get_last_query()
        assert last_q =="How does it work?", f"Wrong last query: {last_q}"
        results.add_pass("Get last query")

        resolved=resolve_references("What about it?")
        assert "it" not in resolved or "reference" in resolved.lower()
        results.add_pass("Reference Resolution")

        clear_session(session_id=session_id)
        results.add_pass("Clear Session")

    except Exception as e:
        results.add_fail("Conversation Memory", str(e))
        traceback.print_exc()


# Query Rewriter-------------------------------------------------------------
def test_query_rewriter():
    """Test query rewriting"""
    print_header("Test 10: Query Rewriter")

    try:
        print_info("Testing vague query detection...")
        vague=should_rewrite_query("tell me about it")
        assert vague==True, "Should detect vague query"
        results.add_pass("vague query detection")

        clear_query=should_rewrite_query("What is the transformer architecture?")
        assert clear_query==False, "Should not detect as vague"
        results.add_pass("Clear query detection")

        print_info("Testing query rewriting...")
        try:
            rewritten=rewrite_query("what about it")
            assert rewritten is not None, "Rewrite returned None"
            print_info(f"Rewritten: '{rewritten}")
            results.add_pass("Query Rewritting")
        
        except Exception as e:
            results.add_skip("Query Rewriting", f"API error: {str(e)[:50]}")
        
    except Exception as e:
        results.add_fail("Query Rewriter", str(e))
        traceback.print_exc()

# validation------------------------------------------------------------------
def test_validation():
    """Test validation function"""
    print_header("Test 11: validation")
    try:
        class MockDoc:
            def __init__(self,content):
                self.page_content=content
            
        docs={
            MockDoc("Machine learning is a type of artificial intelligence"),
            MockDoc("Deep learning uses neural networks")
        }

        print_info("Testing retrieval validation....")
        result =validate_retrieval_quality("machine learning", docs)
        assert result['score']>0, "Score should be positive"
        results.add_pass("Retrieval Validation")

        print("Testing answer validation....")
        answer="Machine learning is used for pattern recognition"
        result=validate_answer_quality("wat is ML?", answer,docs)
        assert 'is_valid' in result, "Missing is_valid key"
        results.add_pass("Answer Validation")

    except Exception as e:
        results.add_fail("Validation", str(e))
        traceback.print_exc()

    
#  Helper------------------------------------------------------------------------
def test_helpers():
    """Test helper function"""
    print_header("Test 12: helper Functions")

    try:
        result=safe_divide(10,2)
        assert result==5.0, f"Wrong results: {result}"

        result=safe_divide(10,0, default=0.0)
        assert result ==0.0, "Should return default"
        results.add_pass("Safe divide")

        text="This is a very long text that should be truncated"
        truncated=truncate_text(text,max_length=20)
        assert len(truncated) <=23, "Text not truncated"
        results.add_pass("Truncated Text")

        messy = "   lots     of      space"
        clean=clean_text(messy)
        assert clean=="lots of space", f"Wrong results: {clean}"
        results.add_pass("Clean Text")

        sources=[
            {"source": "doc1.pdf", "page":5},
            {"source": "doc2.pdf", "page":10},
        ]
        formated= format_sources(sources)
        assert "doc2.pdf" in formated, "Missing source"
        assert "Page 5" in formated, "Missing page"
        results.add_pass("Format sources")

        text="machine learning artificial intelligence neural networks"
        keywords =extract_keywords(text,top_n=3)
        assert len(keywords)<=3, "Too many Keywords"
        results.add_pass("Extract keywords")

    except Exception as e:
        results.add_fail("Helper Function", str(e))
        traceback.print_exc()

# Testing end-to-end pipeline-------------------------------------------------------------------
def test_end_to_end():
    """Test complete pipeline"""
    print_header("Test 13: END-TO-END Pipeline")

    if not os.path.exists("vector_store/chroma_db"):
        results.add_skip("END-TO-END", "No vector store found -run ingestion first")
        return
    
    try:
        print_info("Creating session...")
        create_session()

        print_info("Processing session....")
        query="What is the attention mechanism?"
        result=process_query(query)

        assert 'answer' in result, "Missing answer"
        assert 'sources' in result, "Missing sources"
        assert 'status' in result, "Missing status"

        print_info(f"Status: {result['status']}")
        print_info(f"Answer: {result['answer'][:100]}...")

        if result['sources']:
            print_info(f"Sources: {len(result['sources'])} documents")

        results.add_pass("End-to-End Pipeline")
    
    except Exception as e:
        results.add_fail("End-to-End Pipeline", str(e))
        traceback.print_exc()


# Error handling ---------------------------------------------------------------------
def test_error_handling():
    """Test error handling"""
    print_header("Test 14: Error Handling")

    try:
        print_info("Testing empty query...")
        result=process_query("")
        assert result['status']=='error', "Should handle empty query"
        results.add_pass("Empty query handling")

        print_info("Testing None query...")
        result=process_query(None)
        assert result['status']=='error', "Should handle None query"
        results.add_pass("None query handling")

    except Exception as e:
        results.add_fail("Error Handling", str(e))
        traceback.print_exc()


# main test runner------------------------------------------------------------------------
def run_all_tests():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}SELF-HEALING RAG SYSTEM - COMPLETE TEST SUITE{Colors.END}")
    print(f"{Colors.BOLD}{'='*80}{Colors.END}\n")

    start_time=time.time()
    test_config()
    
    embedding_model = test_embedding_model()
    
    test_loaders()
    
    chunks = test_chunking()
    
    vector_store_created = test_vector_store(chunks)
    
    docs = test_retrieval()
    
    test_reranking(docs)
    
    test_generation()
    
    test_memory()
    
    test_query_rewriter()
    
    test_validation()
    
    test_helpers()
    
    test_end_to_end()
    
    test_error_handling()

    end_time=time.time()
    duration =end_time-start_time
    print(f"\n{Colors.BOLD}Total Time: {duration:.2f} seconds{Colors.END}\n")
    results.print_summary()

    return 0 if results.failed==0 else 1

if __name__ =="__main__":
    exit_code =run_all_tests()
    sys.exit(exit_code)