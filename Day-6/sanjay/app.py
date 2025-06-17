import streamlit as st
import os
import json
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader

# --- GOOGLE AI API KEY SETUP ---
# IMPORTANT: Make sure to set your Google AI API key.
# You can get a free key from Google AI Studio: https://aistudio.google.com/app/apikey
# You can uncomment the line below and paste your key,
# or set it as an environment variable.
os.environ["GOOGLE_API_KEY"] = "AIzaSyB6O2Tgx0DotP_SMAI75pQMhSqb8WbUXH8" 

# --- UI CONFIGURATION ---
st.set_page_config(page_title="Dynamic Opportunity Tracker", layout="wide")
st.title("🎓 Dynamic Early Opportunity Tracker")
st.write("Upload new job postings via the sidebar and see them appear on the dashboard instantly.")

# --- DYNAMIC RAG PIPELINE SETUP ---
# We use session_state to store the RAG pipeline and update it dynamically.

def initialize_rag_pipeline():
    """
    Initializes the RAG pipeline. If the FAISS index exists, it loads it.
    If not, it creates it from the job_postings directory.
    Stores the chain and db in Streamlit's session state.
    """
    index_path = "faiss_index_gemini" # Use a different index for Gemini
    postings_dir = "job_postings"
    
    os.makedirs(postings_dir, exist_ok=True)

    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    if os.path.exists(index_path):
        st.info("Loading existing vector store...")
        db = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    else:
        st.info("Creating a new vector store...")
        if not os.listdir(postings_dir):
            dummy_doc = [Document(page_content="No jobs posted yet. Upload one to get started.")]
            db = FAISS.from_documents(dummy_doc, embeddings)
        else:
            loader = DirectoryLoader(postings_dir, glob="**/*.txt")
            documents = loader.load()
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
            docs = text_splitter.split_documents(documents)
            db = FAISS.from_documents(docs, embeddings)
        
        db.save_local(index_path)

    st.session_state.db = db

    # --- THIS IS THE KEY CHANGE: Use Google's Gemini model ---
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.1, convert_system_message_to_human=True)
    retriever = st.session_state.db.as_retriever()
    st.session_state.qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=False
    )
    st.success("RAG Pipeline with Gemini AI Initialized and Ready!")

# --- INITIALIZE ON FIRST RUN ---
if 'qa_chain' not in st.session_state:
    # Check for API key before initializing
    if not os.environ.get("GOOGLE_API_KEY"):
        st.error("🚨 Google AI API Key not found. Please set it in the script or as an environment variable.")
    else:
        initialize_rag_pipeline()

# --- SIDEBAR FOR PROFILE AND UPLOADS ---
st.sidebar.header("👤 Student Profile")
student_name = st.sidebar.text_input("Your Name", "Sanjay Anbazhagan")
student_skills = st.sidebar.multiselect(
    "Your Skills",
    ['Python', 'Java', 'C++', 'React', 'Cloud', 'Machine Learning', 'Data Analysis', 'SQL', 'HTML/CSS', 'JavaScript', 'Django', 'Flask', 'Node.js', 'TypeScript', 'Go', 'Ruby on Rails', 'Swift', 'Kotlin', 'PHP', 'C#', 'Rust', 'Scala', 'GraphQL', 'TensorFlow', 'PyTorch', 'FastAPI', 'Spring Boot', 'Angular', 'Vue.js', 'Next.js', 'Bootstrap', 'Tailwind CSS', 'Material UI', 'Sass', 'Webpack', 'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'Firebase', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch', 'RabbitMQ', 'Apache Kafka', 'GraphQL', 'RESTful APIs', 'Microservices', 'Agile', 'Scrum', 'DevOps', 'CI/CD', 'Unit Testing', 'Integration Testing', 'System Design'],
    default=[]
)
student_year = st.sidebar.selectbox("Graduation Year", [2025, 2026, 2027], index=0)

st.sidebar.header("💼 Placement Officer Zone")
uploaded_file = st.sidebar.file_uploader("Upload a new Job Posting (.txt)", type=["txt"])

if uploaded_file is not None and 'db' in st.session_state:
    file_path = os.path.join("job_postings", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    loader = TextLoader(file_path)
    new_document = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs_to_add = text_splitter.split_documents(new_document)

    st.session_state.db.add_documents(docs_to_add)
    st.session_state.db.save_local("faiss_index_gemini")
    st.session_state.qa_chain.retriever = st.session_state.db.as_retriever()
    
    st.sidebar.success(f"✅ Successfully added '{uploaded_file.name}'!")
    st.toast("New job added! The dashboard has been updated.")

# --- HELPER FUNCTIONS ---
def calculate_match_score(job_text, student_skills):
    score = 0
    job_text_lower = job_text.lower()
    for skill in student_skills:
        if skill.lower() in job_text_lower:
            score += 1
    return score

def parse_json_output(text):
    try:
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        return json.loads(text)
    except (json.JSONDecodeError, IndexError):
        return {"Error": "Failed to parse AI response.", "RawOutput": text}

# --- MAIN DASHBOARD UI ---
st.header("📊 Shared Opportunities Dashboard")

if 'job_status' not in st.session_state:
    st.session_state.job_status = {}

# Ensure the app doesn't crash if the pipeline failed to initialize
if 'db' in st.session_state:
    all_docs = st.session_state.db.similarity_search(query="job opportunity role company", k=50)

    opportunities = []
    for doc in all_docs:
        source = doc.metadata.get('source', 'N/A')
        clean_source = os.path.basename(source)
        current_status = st.session_state.job_status.get(clean_source, "Not Started")
        opportunities.append({
            "Source": clean_source,
            "Match Score": calculate_match_score(doc.page_content, student_skills),
            "Full Text": doc.page_content,
            "Status": current_status
        })

    unique_opportunities = list({opp['Source']: opp for opp in opportunities}.values())

    tab1, tab2 = st.tabs(["🏆 Matched for You", "All Opportunities"])

    with tab1:
        st.write(f"Opportunities matched for **{student_name}** based on skills: {', '.join(student_skills)}")
        matched_opportunities = sorted(
            [opp for opp in unique_opportunities if opp['Match Score'] > 0], 
            key=lambda x: x['Match Score'], 
            reverse=True
        )
        
        if not matched_opportunities:
            st.info("No opportunities match your selected skills yet. Try changing your profile or uploading a relevant job posting.")

        for opp in matched_opportunities:
            with st.expander(f"**{opp['Source'].replace('.txt', '')}** (Match Score: {opp['Match Score']})"):
                st.info(f"**Current Status:** {opp['Status']}")
                
                extraction_prompt = f"""
                From the text below, extract Role, Eligibility, Deadline, and Benefits. Format the output as a clean JSON object with these exact keys.
                If a value is not found, use the string "Not mentioned".
                
                Text: "{opp['Full Text']}"
                """
                
                if st.button("✨ Analyze with Gemini", key=f"analyze_{opp['Source']}"):
                    with st.spinner("Gemini is extracting details..."):
                        extracted_info_raw = st.session_state.qa_chain.run(extraction_prompt)
                        extracted_info = parse_json_output(extracted_info_raw)
                        st.json(extracted_info)

                status_options = ["Not Started", "Applied", "Interviewing", "Offer Received"]
                current_status_index = status_options.index(opp['Status'])
                new_status = st.radio(
                    "Update Application Status:",
                    options=status_options,
                    key=f"status_{opp['Source']}",
                    index=current_status_index,
                    horizontal=True
                )
                if new_status != opp['Status']:
                    st.session_state.job_status[opp['Source']] = new_status
                    if new_status == "Applied":
                        st.toast(f"✅ Applied! Placement Officer notified about {student_name}'s application.")
                    st.rerun()

    with tab2:
        st.write("A list of all available opportunities in the system.")
        for opp in sorted(unique_opportunities, key=lambda x: x['Source']):
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{opp['Source'].replace('.txt', '')}**")
                    st.caption(f"Status: `{opp['Status']}` | Your Match Score: `{opp['Match Score']}`")
                with col2:
                     if st.button("View Details", key=f"details_{opp['Source']}"):
                        st.write(opp['Full Text'])
else:
    st.warning("RAG pipeline not initialized. Please ensure your API key is set correctly and restart the app.")
