from langchain.tools import tool
import streamlit as st

def _calculate_match_score(job_text: str, student_skills: list[str]) -> int:
    """Calculates a simple match score based on skill overlap."""
    score = 0
    job_text_lower = job_text.lower()
    for skill in student_skills:
        if skill.lower() in job_text_lower:
            score += 1
    return score

@tool
def find_matching_opportunities(student_skills: list[str]) -> list[dict]:
    """
    Finds and ranks job opportunities from the vector store based on a student's skills.
    Use this tool to get a list of all jobs relevant to a student.
    Returns a list of dictionaries, each containing the job source, content, and a match score.
    """
    db = st.session_state.db
    # A generic query to fetch all documents
    all_docs = db.similarity_search(query="job opportunity role company", k=100) 
    
    opportunities = []
    for doc in all_docs:
        opportunities.append({
            "source": doc.metadata.get('source', 'N/A'),
            "content": doc.page_content,
            "match_score": _calculate_match_score(doc.page_content, student_skills)
        })

    # Remove duplicates by source
    unique_opportunities = list({opp['source']: opp for opp in opportunities}.values())
    
    # Sort by match score in descending order
    return sorted(unique_opportunities, key=lambda x: x['match_score'], reverse=True)