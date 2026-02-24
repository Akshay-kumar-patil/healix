import logging
import json
import os
from datetime import datetime

_conversations={}
_current_session_id=None

def create_session(session_id=None):
    """Create a new conversation session"""

    global _current_session_id

    if not session_id:
        session_id =f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    _conversations[session_id]={
        "session_id":session_id,
        "created_at":datetime.now().isoformat(),
        "exchanges":[],
        "metadata":{}
    }

    _current_session_id=session_id

    logging.info(f"New session created: {session_id}")
    return session_id

def get_current_session_id():
    """Get the current active session ID"""
    return _current_session_id

def add_exchange(query,answer,session_id=None,metadata=None):
    """Add a query-answer exchange to conversation history"""

    session_id=session_id or _current_session_id

    if not session_id:
        logging.warning("No active session. Creating new session...")
        session_id=create_session()

    if session_id not in _conversations:
        logging.warning(f"Session {session_id} not found. Creating...")
        create_session(session_id)

    exchange={
        "turn": len(_conversations[session_id]["exchanges"]) + 1,
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "answer": answer,
        "metadata": metadata or {}
    }

    _conversations[session_id]["exchanges"].append(exchange)

    logging.info(f"Exchange added to session {session_id} (Turn {exchange['turn']})")
    return True

def get_conversation_history(session_id=None,last_n=None):
    """Get conversation history for a session"""

    session_id = session_id or _current_session_id

    if not session_id or session_id not in _conversations:
        logging.warning("No conversation history found")
        return []

    exchanges=_conversations[session_id]["exchanges"]
    
    if last_n and last_n>0:
        exchanges=exchanges[-last_n:]

    return exchanges

def get_context_for_llm(session_id=None,last_n=3):
    """Format conversation history as context for LLM"""
    exchanges=get_conversation_history(session_id=session_id,last_n=last_n)

    if not exchanges:
        return ""
    
    context_parts=[]

    for exchange in exchanges:
        context_parts.append(
            f"User:{exchange['query']}\n"
            f"Assistant: {exchange['answer'][:200]} "
        )

    context="\n\n".join(context_parts)

    logging.info(f"Built conversation context from {len(exchanges)} exchanges")
    return context

def get_last_exchanges(session_id=None):
    """Get the Most recent exchange"""

    exchanges=get_conversation_history(session_id=session_id)

    if not exchanges:
        return None
    
    return exchanges[-1]

def get_last_query(session_id=None):
    """Get the last query asked"""

    last=get_last_exchanges(session_id)
    return last["query"] if last else None

def get_last_answer(sess_id=None):
    """Get the last answer given"""

    last=get_last_exchanges(session_id=sess_id)
    return last["answer"] if last else None

def resolve_references(query,session_id=None):
    """Resolve ambiguous references like "it", "this", "that" using conversation history"""

    query_lower=query.lower()

    ambiguous_words=["it", "this", "that" , "they", "them", "its", "their"]
    has_reference=any(word in query_lower.split() for word in ambiguous_words)

    if not has_reference:
        return query
    
    last_query = get_last_query(session_id)

    if not last_query:      
        return query        
    
    resolved=f"{query} (reference to: {last_query})"
    
    logging.info(f"Resolved referene: '{query}'  -> '{resolved}'")
    return resolved

def clear_session(session_id=None):
    """Clear a specific session"""

    global _current_session_id

    session_id=session_id or _current_session_id

    if session_id and session_id in _conversations:
        del _conversations[session_id]
        logging.info(f"Session {session_id} cleared" )
        

    if _current_session_id==session_id:
        _current_session_id=None


def clear_all_session():
    """clear all session"""

    global _conversations, _current_session_id
    count=len(_conversations)
    _conversations={}
    _current_session_id=None
    logging.info(f"Cleared {count} sessions")

def get_session_summary(session_id=None):
    """get a summary of the currect session"""

    session_id=session_id or _current_session_id

    if not session_id or session_id not in _conversations:
        return None
    
    session=_conversations[session_id]
    exchanges=session["exchanges"]
    
    summary={
        "session_id":session_id,
        "created_at":session["created_at"],
        "total_turns": len(exchanges),
        "queries": [exch["query"] for exch in exchanges],
        "last_active": exchanges[-1]["timestamp"] if exchanges else None
    }

    return summary

def save_session_to_file(file_path,session_id=None):
    """Save session to a JSON file for persistence"""
    session_id=session_id or _current_session_id

    if not session_id or session_id not in _conversations:
        logging.warning("No session to save")
        return False
    
    try:
        os.makedirs(os.path.dirname(file_path),exist_ok=True)

        with open(file_path, 'w') as f:
            json.dump(_conversations[session_id],f,indent=2)

        logging.info(f"session saved to {file_path}")
        return True
    
    except Exception as e:
        logging.exception(f"Failed to save session: {e}")
        return False
    
def load_session_from_file(file_path):
    """Load a session from json file"""

    global _current_session_id

    if not os.path.exists(file_path):
        logging.error(f"Session file not found: {file_path}")
        return  None
    
    try:
        with open(file_path,'r') as f:
            session_data=json.load(f)

        session_id=session_data["session_id"]
        _conversations[session_id]=session_data
        _current_session_id=session_id

        logging.info(f"Session loaded from {file_path}")
        return session_id
    
    except Exception as e:
        logging.exception(f"failed to load session: {e}")
        return None
        