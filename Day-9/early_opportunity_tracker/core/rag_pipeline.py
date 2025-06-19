import os
import streamlit as st
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader

INDEX_PATH = "vector_store/faiss_index_gemini"
POSTINGS_DIR = "data/job_postings"

def initialize_rag_pipeline():
    """
    Initializes the RAG pipeline by setting up the Vector Store and QA Chain.
    This function is designed to be called once and stored in Streamlit's session state.
    """
    os.makedirs(POSTINGS_DIR, exist_ok=True)
    os.makedirs(INDEX_PATH, exist_ok=True)

    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    try:
        if os.path.isdir(INDEX_PATH) and os.listdir(INDEX_PATH):
            db = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
            st.session_state.db = db
        else:
            st.info("Creating a new vector store...")
            if not any(f.endswith('.txt') for f in os.listdir(POSTINGS_DIR)):
                st.warning("Job postings directory is empty. Creating a dummy index.")
                dummy_doc = [Document(page_content="No jobs posted yet.")]
                db = FAISS.from_documents(dummy_doc, embeddings)
            else:
                loader = DirectoryLoader(POSTINGS_DIR, glob="**/*.txt", loader_cls=TextLoader)
                documents = loader.load()
                text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
                docs = text_splitter.split_documents(documents)
                db = FAISS.from_documents(docs, embeddings)
            
            db.save_local(INDEX_PATH)
            st.session_state.db = db
            st.success("New vector store created and saved.")

    except Exception as e:
        st.error(f"An error occurred during vector store initialization: {e}")
        st.stop()

    # Initialize the LLM for the RAG chain
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.1, convert_system_message_to_human=True)
    
    # Create the QA chain for detailed analysis and store it
    retriever = st.session_state.db.as_retriever()
    st.session_state.qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever
    )
    
    st.success("✅ RAG Pipeline and Vector Store Initialized!")