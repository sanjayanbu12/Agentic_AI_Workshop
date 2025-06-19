from langchain.tools import tool
import streamlit as st
import json

def _parse_json_output(text: str) -> dict:
    """Safely parses JSON from a string, handling markdown code blocks."""
    try:
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        return json.loads(text)
    except (json.JSONDecodeError, IndexError):
        return {"Error": "Failed to parse AI response.", "RawOutput": text}

@tool
def analyze_job_details(job_content: str) -> dict:
    """
    Analyzes the text of a single job description to extract structured details.
    Use this tool when you need to find specific information like Role, Eligibility, Deadline, and Benefits from a job posting.
    """
    qa_chain = st.session_state.qa_chain
    prompt = f"""
    From the job description text provided below, extract the following details: 
    Role, Company, Eligibility, Deadline, and Benefits. 
    Format the output as a clean JSON object. If a value is not found for a key, use "Not mentioned".
    
    Job Description Text:
    "{job_content}"
    """
    response = qa_chain.run(prompt)
    return _parse_json_output(response)