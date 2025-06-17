import os
import json
import streamlit as st

os.environ['GOOGLE_API_KEY'] = "AIzaSyB6O2Tgx0DotP_SMAI75pQMhSqb8WbUXH8"

from core.rag_pipeline import initialize_rag_pipeline
from agents.aggregator_agent import ingest_new_job
from agents.matcher_agent import get_all_opportunities
from agents.dashboard_agent import display_dashboard

st.set_page_config(
    page_title="Dynamic Opportunity Tracker",
    page_icon="🎓",
    layout="wide"
)

if not os.environ.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_API_KEY") == "PASTE_YOUR_NEW_API_KEY_HERE":
    st.error("🚨 Google AI API Key not found or not set.")
    st.info("Please paste your API key into the `os.environ['GOOGLE_API_KEY']` variable in the `main_app.py` file.")
    st.stop()

@st.cache_data
def load_student_profiles():
    if not os.path.exists('data/student_profiles.json'):
        st.error("Fatal Error: `data/student_profiles.json` not found. Please create it.")
        st.stop()
    with open('data/student_profiles.json', 'r') as f:
        return json.load(f)

student_profiles = load_student_profiles()
student_names = [profile['name'] for profile in student_profiles]

st.title("🎓 Dynamic Early Opportunity Tracker")

if 'qa_chain' not in st.session_state:
    initialize_rag_pipeline()

st.sidebar.header("👤 Student Profile")
selected_student_name = st.sidebar.selectbox("Select Your Profile", student_names)
selected_student = next(p for p in student_profiles if p['name'] == selected_student_name)

st.sidebar.info(f"**Skills:** {', '.join(selected_student['skills'])}")
st.sidebar.info(f"**Graduation Year:** {selected_student['graduation_year']}")

st.sidebar.divider()

st.sidebar.header("💼 Placement Officer Zone")
uploaded_file = st.sidebar.file_uploader("Upload a new Job Posting (.txt)", type=["txt"])

if uploaded_file is not None:
    if 'db' in st.session_state:
        with st.spinner(f"Ingesting '{uploaded_file.name}'..."):
            message = ingest_new_job(uploaded_file, st.session_state.db)
            st.session_state.qa_chain.retriever = st.session_state.db.as_retriever()
            st.sidebar.success(message)
            st.toast("New job added! The dashboard has been updated.")
    else:
        st.sidebar.error("Database not initialized. Please refresh the page.")

if 'db' in st.session_state:
    all_opportunities = get_all_opportunities(st.session_state.db, selected_student['skills'])

    display_dashboard(selected_student, all_opportunities)
else:
    st.warning("RAG pipeline is not ready. Please ensure your API key is set correctly and refresh.")

