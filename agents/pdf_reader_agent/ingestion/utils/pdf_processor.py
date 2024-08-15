from llama_index.core.schema import TextNode
import os
import pdfplumber
from llama_index.core.node_parser import SentenceSplitter
from pydantic import BaseModel


class DocumentMetadata(BaseModel):
    filename: str
    page: int


def process_pdfs_in_directory(directory):
    splitter = SentenceSplitter(
        chunk_size=512,
        chunk_overlap=30,
    )
    
    documents = []
    
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            filepath = os.path.join(directory, filename)
            with pdfplumber.open(filepath) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        text_list = splitter.split_text(text)
                        from llama_index.embeddings.openai import OpenAIEmbedding

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