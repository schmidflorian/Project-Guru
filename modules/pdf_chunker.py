from langchain_community.document_loaders import PyPDFLoader
from langchain_community.docstore.document import Document
from typing import List


def get_chunks(text_splitter, paths) -> List[Document]:
    """
    retrieves chunks of information including metadata from pdfs
    :return:
    """
    pdf_file_paths = paths
    chunks = []
    for pdf_file_path in pdf_file_paths:
        print("~process file", pdf_file_path.__str__())
        loader = PyPDFLoader(pdf_file_path.__str__())
        pages = loader.load_and_split(text_splitter)
        chunks.extend(pages)
    return chunks


def get_documents_from_file(text_splitter, file) -> List[Document]:
    """
    retrieves chunks of information including metadata from pdfs
    :return:
    """
    print("~process file", file.__str__())
    loader = PyPDFLoader(file)
    pages = loader.load_and_split(text_splitter)
    return pages
