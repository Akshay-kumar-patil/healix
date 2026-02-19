import os
import json
import time
from functools import wraps

def timer(func):
    """decorater to measure functrion executin time"""
    def wrapper(*args, **kwargs):
        start=time.time()
        result=func(*args, **kwargs)
        end=time.time()

        print(f"{func.__name__} took {end-start:.3f}s")
        return result
    
    return wrapper

def ensure_directory_exists(directory_path):
    """ Create directory if it doesn't exist """

    try:
        os.makedirs(directory_path,exist_ok=True)
        return True
    except Exception as e:
        print(f"Failed to create directory {directory_path}: {e}")
        return False
    
    
def load_json(file_path):
    """Load json from file"""

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}" )
        return None
    
    try:
        with open(file_path,'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Failed to laod JSON from {file_path}: {e}")
        return None
    
def save_json(data,file_path):
    """save data to json file"""
        
    try:
        directory=os.path.dirname(file_path)
        if directory:
            ensure_directory_exists(directory)

        with open(file_path,'w') as f:
            json.dump(data,f,indent=2)
        
        return True
    except Exception as e:
        print(f"Failed to save JSON to {file_path}: {e}")
        return False
    
def truncate_text(text,max_length=100,suffix="..."):
    """truncate text to maximum length"""

    if not text:
        return ""
    
    if len(text)<=max_length:

        return text
    
    return text[max_length-len(suffix)] +suffix

def clean_text(text):

    """clean text by removing extra whitespace and newliness"""

    if not text:
        return ""
    
    text=" ".join(text.split())
    
    text=text.strip()

    return text

def chunk_list(items,chunk_size):
    "split a lest into chunks of specified size"

    chunks=[]
    for i in range(0,len(items),chunk_size):
        chunks.append(items[i:i +chunk_size])

    return chunks

def flatten_list(nested_list):
    """Falatten a nested list """
    flat_list = []
    for sublist in nested_list:
        for item in sublist:
            flat_list.append(item)

    return flat_list

def format_file_size(size_bytes):
    """format file size in human-readable format"""
    for unit in['B',"KB","MB","GB","TB"]:
        if size_bytes<1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes/=1024.0

    return f"{size_bytes:.1f} PB"        

def get_file_info(file_path):
    """Get information about a file"""

    if not os.path.exists(file_path):
        return None
    
    stat=os.stat(file_path)

    return {
        "path": file_path,
        "name": os.path.basename(file_path),
        "size": stat.st_size,
        "size_formatted": format_file_size(stat.st_size),
        "created": time.ctime(stat.st_ctime),
        "modified": time.ctime(stat.st_mtime)
    }

def safe_divide(numerator,denominator,default:0.0):
    """safe division that returns default value if denominator is zero"""

    try:
        if denominator ==0:
            return default
        return numerator/denominator
    except:
        return default
    
def retry_on_failure(max_retries=3,delay=1.0):
    """Decorator to retry function on failure"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args,**kwargs):
            last_exception=None

            for attempt in len(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception=e
                    if attempt<max_retries-1:
                        time.sleep(delay)
            
            raise last_exception
        raise wrapper
    raise decorator

def format_sources(sources):
    """format source citations nicely"""

    if not sources:
        return "No sources"

    formatted=[]
    for i,source in enumerate(sources,1):
        source_name=source.get("source","unknown")
        page=source.get("page","N/A")
        formatted.append(f"{i}. {source_name} (Page {page})")

    return "\n".join(formatted)

def extract_keywords(text,min_length=4,top_n=10):
    """Extract important keywords from text"""

    if not text:
        return []
    
    words=text.lower().split()

    common_words={'the', 'and', 'for', 'with', 'from', 'that', 'this', 'have', 'been','could','has', 'had', 'Your'}

    words=[w for w in words if len(w)>=min_length and w not in common_words]

    word_freq={}

    for word in words:
        word_freq[word]=word_freq.get(word,0)+1

    sorted_words=sorted(word_freq.items(),key=lambda x: x[1], reverse=True)

    return [word for word, freq in sorted_words[:top_n]]                                     

def validate_env_variables(required_vars):
    """Check if required environment variables are set"""
    results ={}
    all_valid=True

    for var in required_vars:
        value=os.getenv(var)
        is_set=bool(value)
        results[var]={
            "is_set":is_set,
            "value":value if is_set else None

        }

        if not is_set:
            all_valid=False
            print(f"Missing environment variables: {var}")

    results["all_valid"]=all_valid
    return results

