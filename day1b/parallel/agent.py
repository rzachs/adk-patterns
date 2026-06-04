from config import get_model

from dotenv import load_dotenv
load_dotenv()

from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search
from google.genai import types

retry_config = types.HttpRetryOptions(
    attempts=5, exp_base=7, initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)

tech_researcher = Agent(
    name="TechResearcher",
    model=get_model(),
    instruction="Research the latest AI/ML trends. Include 3 key developments, main companies involved, and potential impact. Keep it under 100 words.",
    tools=[google_search],
    output_key="tech_research",
)

health_researcher = Agent(
    name="HealthResearcher",
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
    instruction="Research recent medical breakthroughs. Include 3 significant advances, practical applications, and timelines. Keep it under 100 words.",
    tools=[google_search],
    output_key="health_research",
)

finance_researcher = Agent(
    name="FinanceResearcher",
    model=get_model(),
    instruction="Research current fintech trends. Include 3 key trends, market implications, and future outlook. Keep it under 100 words.",
    tools=[google_search],
    output_key="finance_research",
)

aggregator_agent = Agent(
    name="AggregatorAgent",
    model=get_model(),
    instruction="""Combine these three research findings into a single executive summary:

**Technology Trends:**
{tech_research}

**Health Breakthroughs:**
{health_research}

**Finance Innovations:**
{finance_research}

Highlight common themes, surprising connections, and key takeaways. Around 200 words.""",
    output_key="executive_summary",
)

parallel_research_team = ParallelAgent(
    name="ParallelResearchTeam",
    sub_agents=[tech_researcher, health_researcher, finance_researcher],
)

root_agent = SequentialAgent(
    name="ResearchSystem",
    sub_agents=[parallel_research_team, aggregator_agent],
)