# In /agents/opportunity_agent.py

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from tools.ingestion_tool import ingest_new_job_posting
from tools.matching_tool import find_matching_opportunities
from tools.analysis_tool import analyze_job_details

def create_opportunity_agent():
    """
    Creates and returns the main LangChain AgentExecutor.
    This agent is responsible for orchestrating all actions related to job opportunities.
    """
    tools = [
        ingest_new_job_posting,
        find_matching_opportunities,
        analyze_job_details
    ]

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0, convert_system_message_to_human=True)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant for the Dynamic Early Opportunity Tracker. Your goal is to help students and placement officers manage job postings. You have access to a set of tools to ingest, find, and analyze job opportunities."),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    agent = create_tool_calling_agent(llm, tools, prompt)

    # The Agent Executor runs the agent and tools
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        return_intermediate_steps=True  # <--- THIS IS THE CRITICAL CHANGE
    )
    
    return agent_executor