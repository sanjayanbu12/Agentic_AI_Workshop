# 🎓 Agentic Early Opportunity Tracker

An AI-powered Streamlit application using a LangChain agent and Google Gemini to intelligently match students with job opportunities. It allows placement officers to upload jobs and students to find and analyze roles matched to their skills.

## ✨ Key Features

* **AI Agent-Driven:** Uses a central LangChain agent to handle job matching and analysis.
* **RAG Pipeline:** Implements a FAISS vector store for efficient semantic search of job postings.
* **Dual-User Interface:** Simple and effective UI for both Students and Placement Officers.
* **On-the-Fly Analysis:** Extracts key job details (Role, Eligibility, etc.) with a single click.

## 🛠️ Tech Stack

* **Backend:** Python
* **AI Frameworks:** LangChain, Google Gemini
* **Vector Store:** FAISS, Sentence-Transformers
* **Frontend:** Streamlit

## 🚀 Getting Started

Follow these steps to run the project locally.

### 1. Prerequisites
* Python 3.11+
* A Google AI API Key

### 2. Setup & Run

1.  **Create and activate a virtual environment:**
    * **macOS/Linux:** `python3 -m venv venv && source venv/bin/activate`
    * **Windows:** `python -m venv venv && .\venv\Scripts\activate`

2.  **Install dependencies:**
    * **macOS/Linux:** pip3 install -r requirements.txt
    * **Windows:** pip install -r requirements.txt

3.  **Run the application:**
    streamlit run main_app.py

**The application will now be running in your web browser.**