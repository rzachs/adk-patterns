from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search
from google.genai import types

from dotenv import load_dotenv
load_dotenv()

retry_config = types.HttpRetryOptions(
    attempts=5,       # Maximum retry attempts
    exp_base=7,       # Delay multiplier between retries
    initial_delay=1,  # Seconds before first retry
    http_status_codes=[429, 500, 503, 504]  # Which errors trigger a retry
)

root_agent = Agent(
    name="helpful_assistant",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=retry_config
    ),
    description="A simple agent that can answer general questions.",
    instruction="You are a helpful assistant. Use Google Search for current info or if unsure.",
    tools=[google_search],
)