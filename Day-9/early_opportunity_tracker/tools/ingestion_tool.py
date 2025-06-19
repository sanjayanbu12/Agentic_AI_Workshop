import os
from langchain.tools import tool
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
import streamlit as st

POSTINGS_DIR = "data/job_postings"
INDEX_PATH = "vector_store/faiss_index_gemini"

@tool
def ingest_new_job_posting(file_name: str, file_content: str) -> str:
    """
    Saves a new job posting from an uploaded file and adds it to the FAISS vector store.
    Use this tool when a placement officer uploads a new job description file.
    The input `file_content` should be the decoded string from the uploaded file.
    """
    try:
        db = st.session_state.db
        
        # Save the file to the job postings directory
        file_path = os.path.join(POSTINGS_DIR, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(file_content)

        # Load the new document and add it to the vector store
        loader = TextLoader(file_path)
        new_document = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        docs_to_add = text_splitter.split_documents(new_document)

        db.add_documents(docs_to_add)
        db.save_local(INDEX_PATH)
        
        # Update the retriever in the session state
        st.session_state.qa_chain.retriever = db.as_retriever()

        return f"Successfully ingested and indexed the job posting: '{file_name}'."
    except Exception as e:
        return f"Failed to ingest job posting. Error: {e}"