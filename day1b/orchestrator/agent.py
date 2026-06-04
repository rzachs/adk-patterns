from config import get_model

from dotenv import load_dotenv
load_dotenv()

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import AgentTool, google_search
from google.genai import types

retry_config = types.HttpRetryOptions(
    attempts=5, exp_base=7, initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)

research_agent = Agent(
    name="ResearchAgent",
    model=get_model(),
    instruction="Use google_search to find 2-3 relevant pieces of information on the topic and present findings with citations.",
    tools=[google_search],
    output_key="research_findings",
)

summarizer_agent = Agent(
    name="SummarizerAgent",
    model=get_model(),
    instruction="Read the provided research findings: {research_findings}\nCreate a concise summary as a bulleted list with 3-5 key points.",
    output_key="final_summary",
)

root_agent = Agent(
    name="ResearchCoordinator",
    model=get_model(),
    instruction="""You are a research coordinator.
1. MUST call ResearchAgent to find information on the user's topic.
2. MUST call SummarizerAgent to summarize the findings.
3. Present the final summary to the user.""",
    tools=[AgentTool(research_agent), AgentTool(summarizer_agent)],
)