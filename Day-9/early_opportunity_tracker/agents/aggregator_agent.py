import os
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader

POSTINGS_DIR = "data/job_postings"
INDEX_PATH = "vector_store/faiss_index_gemini"

def ingest_new_job(uploaded_file, db):
    """
    Saves the uploaded job posting and adds it to the FAISS vector store.
    Args:
        uploaded_file: The file-like object from st.file_uploader.
        db: The FAISS database instance from st.session_state.
    """
    file_path = os.path.join(POSTINGS_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    loader = TextLoader(file_path)
    new_document = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs_to_add = text_splitter.split_documents(new_document)

    db.add_documents(docs_to_add)
    db.save_local(INDEX_PATH)
    
    return f"Successfully added '{uploaded_file.name}'!"