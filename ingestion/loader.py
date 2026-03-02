import os
from langchain_community.document_loaders import TextLoader,UnstructuredURLLoader,DirectoryLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from pypdf import PdfReader
import logging
from langchain_core.documents import Document
from langchain_community.document_loaders import Docx2txtLoader


def load_pdf(file_path: str):
    """Loading the pdf"""

    if not os.path.exists(file_path):
        raise FileExistsError(f"The file {file_path} does not exists")
    
    logging.info(f"loading documents from{file_path}...")

    try:
        pdf_reader=PdfReader(file_path)
        documents=[]
        for page_num,page in enumerate(pdf_reader.pages,1):
            text = page.extract_text()

            if not text or not text.strip():
                logging.warning(f"Page {page_num} is empty ,skipping...")
                continue

            doc=Document(
                page_content=text,
                metadata={
                    "source": file_path,
                    "page": page_num,
                    "total_page":len(pdf_reader.pages),
                    "file_type":"pdf"
                }
            )
            documents.append(doc)

        logging.info(f"Successfully loaded {len(documents) }pages from pdf")
        return documents

    except Exception as e:
        logging.exception(f"loader.failed: {e}")
        raise




def load_docx(path):
    """loading documents"""
    if not os.path.exists(path):
        raise FileExistsError(f"The file {path} does not exists")

    logging.info(f"Loading the documents from {path}...")
    try:
        loader=Docx2txtLoader(path)
        doc=loader.load()

        logging.info(f"Successfully loaded the dcuments")
        return doc
    except Exception as e:
        logging.exception(f"loader.failed: {e}")
        raise



def load_url(urls):
    """Loading the URL """
    if not urls:
        raise ValueError("No Urls provided")
    
    if not isinstance(urls,list):
        urls=[urls]

    logging.info(f"Loading url of len {len(urls)}...")
    
    try:
        loader = UnstructuredURLLoader(urls=urls)
        data = loader.load()
        logging.info(f"Successfully loaded the URL")
        return data

    except Exception as e:
        logging.exception("Failed to load urls")
        raise


def load_csv(path):
    """loading the csv file"""

    if not os.path.exists(path):
        raise FileExistsError(f"The file {path} does not exists")
    
    logging.info(f"laoding the csv file {path}")

    try:
        loader=CSVLoader(file_path=path)
        data=loader.load()

        logging.info("Successfully loaded the csv file")
        return data
    
    except Exception as e:
        logging.exception("failed to load csv")
        raise


    
