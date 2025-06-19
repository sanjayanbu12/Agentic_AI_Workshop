# 🎓 Agentic Early Opportunity Tracker


### 🎯 Core Functionality
* **AI Agent-Driven Matching:** Uses a central LangChain agent to handle intelligent job matching and analysis
* **RAG Pipeline:** Implements a FAISS vector store for efficient semantic search of job postings
* **Dual-User Interface:** Separate, intuitive interfaces for Students and Placement Officers
* **On-the-Fly Analysis:** Extracts key job details (Role, Eligibility, Requirements, etc.) with a single click

### 🧠 AI-Powered Features
* **Semantic Job Matching:** Matches students based on skills, experience, and preferences using vector similarity
* **Natural Language Processing:** Understands job descriptions and student profiles in natural language
* **Intelligent Recommendations:** Provides personalized job suggestions with match scores
* **Automated Analysis:** Extracts and summarizes key information from job postings

### 👥 User Features
* **Student Dashboard:** Browse jobs, view matches, analyze opportunities
* **Placement Officer Portal:** Upload jobs, manage postings, view analytics
* **Real-time Search:** Instant search and filtering capabilities
* **Interactive UI:** Clean, responsive interface built with Streamlit

## 🛠️ Tech Stack

### Backend & AI
* **Python 3.11+** - Core programming language
* **LangChain** - AI agent framework and orchestration
* **Google Gemini** - Large language model for analysis and matching
* **FAISS** - Vector database for similarity search
* **Sentence-Transformers** - Text embeddings for semantic search

### Frontend & Deployment
* **Streamlit** - Web application framework
* **Pandas** - Data manipulation and analysis
* **NumPy** - Numerical computations
* **Plotly** - Interactive visualizations (if applicable)

### Data Storage
* **Local File System** - Job postings and user data storage
* **Vector Store** - FAISS index for efficient similarity search

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │  LangChain      │    │  Google Gemini  │
│   (Frontend)    │◄──►│  Agent          │◄──►│  (LLM)          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  User Interface │    │  Job Matching   │    │  Text Analysis  │
│  Management     │    │  Logic          │    │  & Generation   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│  Local Storage  │    │  FAISS Vector   │
│  (Jobs/Profiles)│    │  Store          │
└─────────────────┘    └─────────────────┘
```

## 🚀 Getting Started

Follow these steps to run the project locally.

### 1. Prerequisites

Before you begin, ensure you have the following installed:
* **Python 3.11 or higher** ([Download Python](https://www.python.org/downloads/))
* **Git** ([Download Git](https://git-scm.com/downloads))
* **A Google AI API Key** ([Get API Key](https://ai.google.dev/))

### 2. Clone the Repository

git clone https://github.com/yourusername/agentic-early-opportunity-tracker.git
cd agentic-early-opportunity-tracker

### 3. Environment Setup

#### Create and activate a virtual environment:

**macOS/Linux:**
python3 -m venv venv
source venv/bin/activate

**Windows:**
python -m venv venv
.\venv\Scripts\activate

### 4. Install Dependencies

**macOS/Linux:**
pip3 install -r requirements.txt

**Windows:**
pip install -r requirements.txt

### 5. Environment Configuration

Create a `.env` file in the root directory and add your API key:
GOOGLE_API_KEY=your_google_api_key_here

### 6. Run the Application

streamlit run main_app.py


**The application will now be running in your web browser at `http://localhost:8501`.**