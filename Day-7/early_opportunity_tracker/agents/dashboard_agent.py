import streamlit as st
import os
import json
from agents.notifier_agent import notify_placement_officer

def parse_json_output(text):
    """Safely parses JSON from a string, handling markdown code blocks."""
    try:
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        return json.loads(text)
    except (json.JSONDecodeError, IndexError):
        return {"Error": "Failed to parse AI response.", "RawOutput": text}

def display_dashboard(student, opportunities):
    """
    Renders the main opportunities dashboard with tabs for matched and all jobs.
    """
    st.header(f"📊 Opportunities Dashboard for {student['name']}")

    if 'job_status' not in st.session_state:
        st.session_state.job_status = {}

    tab1, tab2 = st.tabs(["🏆 Matched for You", "All Opportunities"])

    with tab1:
        st.write(f"Opportunities matched based on your skills: **{', '.join(student['skills'])}**")
        
        matched_ops = sorted(
            [opp for opp in opportunities if opp['match_score'] > 0],
            key=lambda x: x['match_score'],
            reverse=True
        )

        if not matched_ops:
            st.info("No opportunities match your selected skills yet. A Placement Officer can upload a relevant job posting.")

        for opp in matched_ops:
            source_name = os.path.basename(opp['source'])
            job_title = source_name.replace('.txt', '').replace('_', ' ').title()
            status_key = f"{student['id']}_{source_name}"
            current_status = st.session_state.job_status.get(status_key, "Not Started")

            with st.expander(f"**{job_title}** (Match Score: {opp['match_score']})"):
                st.info(f"**Current Status:** {current_status}")

                if st.button("✨ Analyze with Gemini", key=f"analyze_{source_name}"):
                    with st.spinner("Gemini is extracting details..."):
                        prompt = f"""
                        From the job description below, extract the following details: Role, Eligibility, Deadline, and Benefits. 
                        Format the output as a clean JSON object. If a value is not found, use "Not mentioned".
                        Text: "{opp['content']}"
                        """
                        response = st.session_state.qa_chain.run(prompt)
                        st.json(parse_json_output(response))

                status_options = ["Not Started", "Applied", "Interviewing", "Offer Received"]
                current_idx = status_options.index(current_status)
                new_status = st.radio(
                    "Update Application Status:",
                    options=status_options,
                    key=f"status_{status_key}",
                    index=current_idx,
                    horizontal=True
                )
                if new_status != current_status:
                    st.session_state.job_status[status_key] = new_status
                    if new_status == "Applied":
                        notify_placement_officer(student['name'], source_name)
                    st.rerun()

    with tab2:
        st.write("A list of all available opportunities in the system.")
        all_ops_sorted = sorted(opportunities, key=lambda x: os.path.basename(x['source']))

        for opp in all_ops_sorted:
            source_name = os.path.basename(opp['source'])
            job_title = source_name.replace('.txt', '').replace('_', ' ').title()
            status_key = f"{student['id']}_{source_name}"
            current_status = st.session_state.job_status.get(status_key, "Not Started")

            with st.container(border=True):
                st.markdown(f"**{job_title}**")
                st.caption(f"Status: `{current_status}` | Your Match Score: `{opp['match_score']}`")
                with st.expander("View Full Job Description"):
                    st.text(opp['content'])