import logging
import os
from datetime import datetime

def setup_logger(name=None,log_level=logging.INFO,log_to_file=True, log_dir="logs",log_format=None):
    """setup cerntralized logger for the application"""

    logger=logging.getLogger(name or "self_healing_rag")
    logger.setLevel(log_level)

    if logger.handlers:
        return logger
    
    if not log_format:
        log_format="%(asctime)s -%(name)s -%(levelname)s - %(message)s"

    formatter=logging.Formatter(log_format,datefmt="%Y-%m-%d %H:%M:%S") 
    console_handler =logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_to_file:

        os.makedirs(log_dir,exist_ok=True)
        timestamp=datetime.now().strftime("%Y%M%d")
        log_file=os.path.join(log_dir,f"rag_system_{timestamp}.log")

        file_handler=logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        logger.info(f"Logging to file: {log_file}")

    return logger
    
def get_logger(name=None):
    """get existing logger or create new one"""

    logger=logging.getLogger(name or "self_healing_rag")

    if not logger.handlers:
        return setup_logger(name)
    
    return logger

def set_log_level(level):
    """Change log level for all logger"""

    logger=get_logger()
    logger.setLevel(level)

    for handler in logger.handlers:
        handler.setLevel(level)

    logger.info(f"Log level changed to {logging.getLevelName(level)}")

def disable_external_loggers():
    """Disable verbose logging from external libraries"""
    noisy_loggers=[
        "httpx",
        "httpcore",
        "chromadb",
        "sentence_transformers",
        "transformers",
        "urllib3"
    ]

    for logger_name in noisy_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    logging.info("External library loggers suppressed")


def log_function_call(func):
    """Its a Decorator to log function calls"""

    def wrapper(*args,**kwargs):
        logger=get_logger()
        logger.debug(f"Calling {func.__name__}  with args={args}, kwargs={kwargs}")

        try:
            result=func(*args,**kwargs)
            logger.debug(f"{func.__name__} completed successfully" )
            return result
        
        except Exception as e:
            logger.exception(f"{func.__name__} raised exception: {e}")
            raise

    return wrapper


            
