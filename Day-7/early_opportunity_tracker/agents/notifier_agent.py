import streamlit as st

def notify_placement_officer(student_name, job_source):
    """
    Creates a notification toast. This can be expanded to send emails, etc.
    """
    job_title = job_source.replace('.txt', '').replace('_', ' ').title()
    st.toast(f"🔔 PO Notification: **{student_name}** has applied for **{job_title}**!")