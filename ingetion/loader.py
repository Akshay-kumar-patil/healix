import os
from langchain_community.document_loaders import TextLoader,UnstructuredURLLoader,DirectoryLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from pypdf import PdfReader
from langchain_community.document_loaders import Docx2txtLoader


def load_pdf(file_path: str):
    """Loading the pdf"""

    if not os.path.exists(file_path):
        raise FileExistsError(f"The file {file_path} does not exists")
    
    print(f"loading documents from{file_path}...")
    try:
        docss=PdfReader(file_path)
    except Exception as e:
        print(f"loader.failed: {e}")
        raise

    print(f"Successfuly loaded the pdf")
    return docss


def load_docx(path):
    """loading documents"""
    if not os.path.exists(path):
        raise FileExistsError(f"The file {path} does not exists")

    print(f"Loading the documents from {path}")

    loader=Docx2txtLoader(path)
    doc=loader.load()

    print(f"Successfully loaded the dcuments")
    return doc


def url_loader(urls):
    """Loading the URL """
    
    loader = UnstructuredURLLoader(urls=urls)
    data = loader.load()
    print(f"Successfully loaded the URL")
    return data

def load_csv(path):
    """loading the csv file"""

    if not os.path.exists(path):
        raise FileExistsError(f"The file {path} does not exists")
    
    print(f"laoding the csv file {path}")

    loader=CSVLoader(path=path)
    data=loader.load()

    print("Successfully loaded the csv file")
    return data


    
