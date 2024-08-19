from llama_index.core.schema import TextNode
import os
import pdfplumber
from llama_index.core.node_parser import SentenceSplitter
from pydantic import BaseModel
from llama_index.embeddings.openai import OpenAIEmbedding
import re

class DocumentMetadata(BaseModel):
    filename: str
    page: int

def clean_text(text):
    # Remove newlines within sentences
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
    # Remove any extra spaces
    text = re.sub(r'\s+', ' ', text)
    return text

def contains_references(text):
    """Determine if a page contains the 'References' section as a header."""
    lowered_text = text.lower().strip()
    
    # Identify if the page contains a 'References' header
    if re.search(r'\breferences\b', lowered_text):
        # Check if "References" is the start of a line (header-like)
        lines = lowered_text.splitlines()
        for line in lines:
            if line.strip().startswith("references"):
                return True
        # Consider "References" if it appears late in the document (e.g., after 70% of content)
        if lowered_text.find("references") > len(lowered_text) * 0.7:
            return True
    
    return False

def process_pdfs_in_directory(directory):
    splitter = SentenceSplitter(
        chunk_size=512,
        chunk_overlap=30,
        separator="\n",
    )
    
    documents = []
    skip_pages = False  # Flag to skip pages after detecting references
    
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            filepath = os.path.join(directory, filename)
            skip_pages = False
            with pdfplumber.open(filepath) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        # If skip_pages is True, skip the rest of the pages
                        if skip_pages:
                            print(f"Skipping page {page_num + 1} in file {filename} after 'References'.")
                            continue
                        
                        # Check if this page contains the 'References' section
                        if contains_references(text):
                            print(f"Detected 'References' on page {page_num + 1} in file {filename}.")
                            skip_pages = True  # Set the flag to start skipping subsequent pages
                        
                        # Clean and split the text
                        cleaned_text = clean_text(text)
                        text_list = splitter.split_text(cleaned_text)

                        embed_model = OpenAIEmbedding(model="text-embedding-3-small")
                        metadata = DocumentMetadata(filename=filename, page=page_num + 1)
                        metadata_dict = metadata.dict()
                        page_documents = [TextNode(text=t, 
                                                   embedding= embed_model.get_text_embedding(t),
                                                   metadata=metadata_dict, 
                                                   excluded_llm_metadata_keys=["filename", "page"],
                                                   excluded_embed_metadata_keys=["filename", "page"]) 
                                          for t in text_list]
                        documents.extend(page_documents)
    
    return documents

# Usage example:
# directory_path = "./data/"
# all_documents = process_pdfs_in_directory(directory_path)
# print(f"Processed {len(all_documents)} documents from PDFs.")
