# In /main_app.py

import os
import json
import streamlit as st
from core.rag_pipeline import initialize_rag_pipeline
from agents.opportunity_agent import create_opportunity_agent

# --- Page Configuration, Initialization, and Data Loading ---
# (These sections remain the same - no changes needed here)
st.set_page_config(page_title="Agentic Opportunity Tracker", page_icon="🤖", layout="wide")

if not os.environ.get("GOOGLE_API_KEY"):
    st.error("🚨 Google AI API Key not found. Please set it as an environment variable.")
    st.stop()

def initialize_system():
    if 'system_initialized' not in st.session_state:
        with st.spinner("Booting up the system... Please wait."):
            initialize_rag_pipeline()
            st.session_state.agent_executor = create_opportunity_agent()
            st.session_state.system_initialized = True
            st.session_state.opportunities = []
            st.session_state.job_status = {}
            st.toast("System Initialized Successfully!")

@st.cache_data
def load_student_profiles():
    try:
        with open('data/student_profiles.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Fatal Error: `data/student_profiles.json` not found.")
        st.stop()

# --- Main App Logic ---
initialize_system()
student_profiles = load_student_profiles()
student_names = [profile['name'] for profile in student_profiles]

st.title("🎓 Agentic Early Opportunity Tracker")
st.markdown("An AI-powered dashboard that uses a LangChain agent to manage and match job opportunities.")

# --- Sidebar ---
# (This section remains the same)
st.sidebar.header("👤 Student Profile")
selected_student_name = st.sidebar.selectbox("Select Your Profile", student_names)
selected_student = next(p for p in student_profiles if p['name'] == selected_student_name)
st.sidebar.info(f"**Skills:** {', '.join(selected_student['skills'])}")
st.sidebar.info(f"**Graduation Year:** {selected_student['graduation_year']}")
st.sidebar.divider()
st.sidebar.header("💼 Placement Officer Zone")
uploaded_file = st.sidebar.file_uploader("Upload a new Job Posting (.txt)", type=["txt"])

if uploaded_file:
    with st.spinner(f"Agent is ingesting '{uploaded_file.name}'..."):
        file_content = uploaded_file.getvalue().decode("utf-8")
        response = st.session_state.agent_executor.invoke({
            "input": f"A new job posting file named '{uploaded_file.name}' has been uploaded. Ingest it. The file content is: {file_content}"
        })
        st.sidebar.success(response['output'])
        st.session_state.pop('opportunities', None) 
        st.toast("New job added! Refreshing dashboard...")


# --- Main Dashboard ---
# (The "Find Matching Opportunities" button logic is already correct)
st.header(f"📊 Opportunities Dashboard for {selected_student['name']}")

if st.button("Find Matching Opportunities", use_container_width=True) or 'opportunities' not in st.session_state or not st.session_state.opportunities:
    with st.spinner("Agent is searching for opportunities..."):
        response = st.session_state.agent_executor.invoke({
            "input": f"Find all matching job opportunities for a student with the following skills: {selected_student['skills']}"
        })
        
        if response.get("intermediate_steps"):
            tool_output = response["intermediate_steps"][-1][1]
            if isinstance(tool_output, list):
                 st.session_state.opportunities = tool_output
            else:
                st.error("Agent did not return a list of opportunities.")
                st.session_state.opportunities = []
        else:
            st.error(f"Agent returned a response I couldn't process directly: {response.get('output')}")
            st.session_state.opportunities = []


# Display Opportunities
if not st.session_state.get('opportunities'):
    st.info("No opportunities found. Click the button above to search or have a Placement Officer upload a new job.")
else:
    opportunities = st.session_state.opportunities
    matched_ops = [opp for opp in opportunities if isinstance(opp, dict) and opp.get('match_score', 0) > 0]
    
    if not matched_ops:
        st.warning("No opportunities match your specific skills. You can view all available jobs in the 'All Opportunities' tab.")

    tab1, tab2 = st.tabs([f"🏆 Matched for You ({len(matched_ops)})", f"All Opportunities ({len(opportunities)})"])

    with tab1:
        for opp in matched_ops:
            source_name = os.path.basename(opp['source'])
            job_title = source_name.replace('.txt', '').replace('_', ' ').title()
            with st.expander(f"**{job_title}** (Match Score: {opp['match_score']})"):
                if st.button("✨ Analyze with Gemini Agent", key=f"analyze_tab1_{source_name}"):
                    with st.spinner("Agent is extracting details..."):
                        analysis_response = st.session_state.agent_executor.invoke({
                            "input": f"Analyze the following job description and extract its details: {opp['content']}"
                        })
                        
                        # --- CHANGE 1: FIX FOR THE ANALYSIS BUTTON IN TAB 1 ---
                        if analysis_response.get("intermediate_steps"):
                            tool_output = analysis_response["intermediate_steps"][-1][1]
                            if isinstance(tool_output, dict):
                                st.json(tool_output)
                            else:
                                st.error("Analysis tool returned an unexpected format.")
                                st.write(tool_output)
                        else:
                            st.error("Agent did not return a parsable analysis.")
                            st.write(analysis_response.get("output"))
                        # --- END OF CHANGE 1 ---
                        
                st.text(opp['content'])
    
    with tab2:
        for opp in opportunities:
            if isinstance(opp, dict):
                source_name = os.path.basename(opp['source'])
                job_title = source_name.replace('.txt', '').replace('_', ' ').title()
                with st.container(border=True):
                     st.markdown(f"**{job_title}** (Match Score: {opp.get('match_score', 'N/A')})")
                     if st.button("Analyze This Job", key=f"analyze_tab2_{source_name}"):
                         with st.spinner("Agent is extracting details..."):
                            analysis_response = st.session_state.agent_executor.invoke({
                                "input": f"Analyze the following job description and extract its details: {opp['content']}"
                            })

                            # --- CHANGE 2: FIX FOR THE ANALYSIS BUTTON IN TAB 2 ---
                            if analysis_response.get("intermediate_steps"):
                                tool_output = analysis_response["intermediate_steps"][-1][1]
                                if isinstance(tool_output, dict):
                                    st.json(tool_output)
                                else:
                                    st.error("Analysis tool returned an unexpected format.")
                                    st.write(tool_output)
                            else:
                                st.error("Agent did not return a parsable analysis.")
                                st.write(analysis_response.get("output"))
                            # --- END OF CHANGE 2 ---

                     with st.expander("View Full Job Description"):
                        st.text(opp.get('content', ''))