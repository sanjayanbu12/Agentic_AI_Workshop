def calculate_match_score(job_text, student_skills):
    """Calculates a simple match score based on skill overlap."""
    score = 0
    job_text_lower = job_text.lower()
    for skill in student_skills:
        if skill.lower() in job_text_lower:
            score += 1
    return score

def get_all_opportunities(db, student_skills):
    """
    Fetches all documents and enriches them with a match score for the student.
    Args:
        db: The FAISS database instance.
        student_skills: A list of the student's skills.
    Returns:
        A list of unique opportunities, each as a dictionary.
    """
    all_docs = db.similarity_search(query="job opportunity role company", k=100)
    
    opportunities = []
    for doc in all_docs:
        opportunities.append({
            "source": doc.metadata.get('source', 'N/A'),
            "content": doc.page_content,
            "match_score": calculate_match_score(doc.page_content, student_skills)
        })

    unique_opportunities = list({opp['source']: opp for opp in opportunities}.values())
    
    return unique_opportunities