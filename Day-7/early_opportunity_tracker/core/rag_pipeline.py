import os
import streamlit as st
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader

# Define paths relative to the root of the project
INDEX_PATH = "vector_store/faiss_index_gemini"
POSTINGS_DIR = "data/job_postings"

def initialize_rag_pipeline():
    """
    Initializes the RAG pipeline. It first checks for a valid, non-empty index
    directory to load. If one is not found, it creates a new index from scratch.
    """
    # Ensure the necessary directories exist before any other operations
    os.makedirs(POSTINGS_DIR, exist_ok=True)
    os.makedirs(INDEX_PATH, exist_ok=True)

    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    # --- FIXED: Robust check to prevent the RuntimeError ---
    # We now check if the path is a directory AND if it contains files.
    # An empty directory would also cause an error on load.
    try:
        if os.path.isdir(INDEX_PATH) and os.listdir(INDEX_PATH):
            st.info("Loading existing vector store...")
            db = FAISS.load_local(
                INDEX_PATH,
                embeddings,
                allow_dangerous_deserialization=True
            )
        else:
            st.info("Creating a new vector store...")
            # Check if there are any text files to load
            if not any(f.endswith('.txt') for f in os.listdir(POSTINGS_DIR)):
                # Create a dummy document to initialize the store if it's empty
                st.warning("Job postings directory is empty. Creating a dummy index.")
                dummy_doc = [Document(page_content="No jobs posted yet.")]
                db = FAISS.from_documents(dummy_doc, embeddings)
            else:
                loader = DirectoryLoader(
                    POSTINGS_DIR,
                    glob="**/*.txt",
                    show_progress=True,
                    loader_cls=TextLoader
                )
                documents = loader.load()
                text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
                docs = text_splitter.split_documents(documents)
                db = FAISS.from_documents(docs, embeddings)
            
            # Save the newly created index to the specified path
            db.save_local(INDEX_PATH)
            st.success("New vector store created and saved.")

    except Exception as e:
        st.error(f"An error occurred during vector store initialization: {e}")
        st.info("Attempting to rebuild the index. Please delete the 'vector_store' folder and restart the app if the problem persists.")
        # As a fallback, delete the potentially corrupted index and stop
        # shutil.rmtree(INDEX_PATH, ignore_errors=True)
        st.stop()


    st.session_state.db = db

    # Initialize the LLM. It will automatically use the GOOGLE_API_KEY from the environment.
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.1, convert_system_message_to_human=True)
    
    # Create the retriever from the database
    retriever = st.session_state.db.as_retriever(search_kwargs={'k': 10})
    
    # Create the QA chain
    st.session_state.qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever
    )
    st.success("✅ RAG Pipeline Initialized!")

