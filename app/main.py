import argparse
import sys
import os
from pathlib import Path

from utils.logger import setup_logger,disable_external_loggers
from utils.helpers import validate_env_variables,format_sources
from ingestion.pipeline import execute_ingestion
from orchestrator.controller import process_query
from memory.conversation_store import create_session,get_conversation_history,clear_session,save_session_to_file
from evaluation.metrics import evaluate_rag_pipeline,get_average_metrics,reset_metrics_history

logger=None

def setup_system():
    """Initialize the system: logging,environment validation,etc"""

    global logger

    print("\n"+"="*80)
    print("Self Healing RAG System")
    print("\n"+"="*80)

    logger=setup_logger(
        name="main",
        log_to_file=True,
        log_dir="logs"
    )

    disable_external_loggers()

    logger.info("System initialization started")

    required_vars=["GEMINI_API_KEY"]
    validation=validate_env_variables(required_vars)

    if not validation["all_valid"]:
        logger.error("Missing required environment variables")
        print("\n ERROR: Missing environment variables")
        print("Please create a .env file with:")
        print("  GEMINI_API_KEY=your_api_key_here")
        return False
    
    logger.info("System Initialization complete ")
    return True

def ingest_mode(source=None,doc_type=None):
    """Run ingestion pipeline loads documents into vector store"""

    logger.info("starting ingestion mode")

    print("\n"+"="*80)
    print("Documents Ingestion")
    print("="*80+"\n")

    if not source:
        print("enter the path to documents or URL:")
        source=input("Source: ").strip()

        if not source:
            print("No Source provided")

            return False
        
    if not doc_type:
        print("\n Select documents type:")
        print("1.PDF")
        print("2.DOCX (word)")
        print("3.CSV")
        print("4.URL")

        choice=input("\nChoice (1-4): ").strip()

        type_map={
            "1":"pdf",
            "2":"docx",
            "3":"csv",
            "4":"url",
        }

        doc_type=type_map.get(choice)


        if not doc_type:
            print("Invalid choice")
            return False
        

    if doc_type !="url":
        if not os.path.exists(source):
            print(f"file not found: {source}")
            logger.error(f"File not found: {source}")

            return False
        
    print(f"\n Source: {source}" )
    print(f"Type: {doc_type.upper()}")
    print("Starting ingestion...")

    try:
        vector_store=execute_ingestion(source=source,doc_type=doc_type)

        print(f"\n ingestion completed successfully")
        logger.info(f"\n ingestion completed successfully")
        return True
    
    except Exception as e:
        print(f"Ingestion failed: {e}")
        logger.exception(f"ingestion failed: {e}")
        return False
    

def chat_mode(enable_evaluation=False):
    """Interative chat mode with conversation memory"""

    logger.info("starting chat mode")

    session_id=create_session()

    print("\n"+"="*80)
    print("INGESTION CHAT MODE")
    print("="*80)
    print("\nTips:")
    print("  - Ask follow-up questions (I'll remember context)")
    print("  - Type 'exit' or 'quit' to end")
    print("  - Type 'history' to see conversation")
    print("  - Type 'clear' to reset conversation")
    print("  - Type 'save' to save session")
    
    if enable_evaluation:
        print(" -Type 'metrics to see performance stats")
    print("\n"+"="*80 +"\n")

    turn_count=0

    while True:
        try:
            user_input=input("You: ").strip()

            if not user_input:
                continue


            if user_input.lower() in ['exit', 'quit','q']:
                print("\n Goodbye")
                break
            elif user_input.lower() == 'history':
                history=get_conversation_history()
                if not history:
                    print("No Conversation history ywt.\n")

                else:
                    print("\n Conversation History:")
                    for i,exchange in enumerate(history,1):
                        print(f"\n Turn: {i}")
                        print(f"You: {exchange['query']}")
                        print(f"Bot: {exchange['answer'][:200]}....")
                    print()

                continue

            elif user_input.lower()=='clear':
                clear_session()
                turn_count=0
                print("Conversation Cleared \n")
                continue

            elif user_input.lower()=='save':
                save_path=f"data/sessions/session_{session_id}.json"
                save_session_to_file(save_path)
                print(f"Session saved to {save_path}\n")
                continue

            elif user_input.lower() =='metrics' and enable_evaluation:
                metrics=get_average_metrics()
                if metrics:
                    print("\n Average Metrics:")
                    print(f"Total Queries: {metrics.get('total_queries',0)}")
                    if 'avg_answer_faithfulness' in metrics:
                        print(f"Faithfullness: {metrics['avg_answer_faithfulness']:.2%}")

                    if 'avg_total_time_seconds' in metrics:
                        print(f"Avg Latency: {metrics['avg_total_time_seconds']:.3f}s")
                    print()
                    
                else:
                    print("No metrics available yet.\n")
                continue

            turn_count+=1

            print(f"\n Processing... (turn {turn_count})\n")

            if enable_evaluation:
                result=evaluate_rag_pipeline(
                    query=user_input,
                    process_func=process_query
                )
            else:
                result =process_query(user_input)

            print(f"Bot: {result['answer']}\n")

            if result.get('sources'):
                print("Sources:")
                print(format_sources(result['sources']))
                print()

            if result.get('status') != 'success':
                print(f"Status: {result['status']}\n")

            
        except KeyboardInterrupt:
            print("\n \n Interrupted. Goodbye")
            break

        except Exception as e:
            logger.exception(f"Error in chat mode: {e}")
            print(f"\n ERROR: {e}\n")
            print("Please try again or type 'exit' to quit.\n")

    if enable_evaluation:
        print("\n Final Metrics")

        metrics=get_average_metrics()
        if metrics:
            print(f"  Total Queries: {metrics.get('total_queries', 0)}")
            if 'avg_answer_faithfulness' in metrics:
                print(f"  Avg Faithfulness: {metrics['avg_answer_faithfulness']:.2%}")
            if 'avg_total_time_seconds' in metrics:
                print(f"  Avg Latency: {metrics['avg_total_time_seconds']:.3f}s")
        print()

        
def single_query_mode(query):
    """process a single query and exit"""

    logger.info(f"Processing single query: {query}")

    print("\n" + "=" * 80)
    print(" SINGLE QUERY MODE")
    print("=" * 80 + "\n")
    
    print(f"Query: {query}\n")
    print(" Processing...\n")

    try:
        result=process_query(query)

        print("="*80)
        print("Answer:")
        print("="*80)
        print(f"\n{result['answer']}\n")

        if result.get('sources'):
            print("=" * 80)
            print("SOURCES:")
            print("=" * 80)
            print(format_sources(result['sources']))
            print()

        # metadata
        print("=" * 80)
        print("METADATA:")
        print("=" * 80)
        print(f"Status: {result.get('status', 'unknown')}")
        if 'attempts' in result:
            print(f"Attempts: {result['attempts']}")
        if 'retrieval_quality' in result:
            print(f"Retrieval Quality: {result['retrieval_quality']:.2%}")
        print()
        
        logger.info("Single query processed successfully")
        return True

    except Exception as e:
        print(f"Error : {e}\n")
        logger.exception(f"Single query failed: {e}")
        return False
    
def main():
    """Main entry point with CLI argument parsing."""

    parser=argparse.ArgumentParser(
        description="Self-Healing RAG System - Production-Grade Q&A with Auto-Correction",

        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest documents (interactive)
  python -m app.main --ingest
  
  # Ingest with specified file
  python -m app.main --ingest --source data/medical.pdf --type pdf
  
  # Interactive chat
  python -m app.main --chat
  
  # Chat with performance tracking
  python -m app.main --chat --evaluate
  
  # Single query
  python -m app.main --query "What is diabetes?"
"""
    )

    mode_group=parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        '--ingest',
        action='store_true',
        help='Run documents ingestion pipeline'
    )
    mode_group.add_argument(
        '--chat',
        action='store_true',
        help='Start interactive chat mode'
    )
    mode_group.add_argument(
        '--query',
        type=str,
        help='Process a single query and exit'
    )
    
    parser.add_argument(
        '--source',
        type=str,
        help='Path to documents or URL (for --ingest mode)'
    )
    parser.add_argument(
        '--type',
        type=str,
        choices=['pdf', 'docx', 'csv', 'url'],
        help='Document type (for --ingest mode)'
    )
    parser.add_argument(
        '--evaluate',
        action='store_true',
        help='Enable performance metrics tracking (for --chat mode)'
    )

    args=parser.parse_args()

    if not setup_system():
        sys.exit(1)

    try:
        if args.ingest:
            success =ingest_mode(source=args.source,doc_type=args.type)
            sys.exit(0 if success else 1)

        elif args.chat:
            chat_mode(enable_evaluation=args.evaluate)
            sys.exit(0)
        
        elif args.query:
            sucess=single_query_mode(args.query)
            sys.exit(0 if sucess else 1)

    except KeyboardInterrupt:
        print("\n \n Interrupted Exitting...")
        sys.exit(0)

    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        print(f"\n fatal error: {e}")
        sys.exit(1)


if __name__=="__main__":
    main()