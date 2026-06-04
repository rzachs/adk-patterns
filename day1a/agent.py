from dotenv import load_dotenv
load_dotenv()

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from google.adk.agents import Agent
from google.adk.models.anthropic_llm import AnthropicLlm

from shared.tools import web_search

root_agent = Agent(
    name="helpful_assistant",
    model=AnthropicLlm(model="claude-sonnet-4-6"),
    description="A simple agent that can answer general questions.",
    instruction="You are a helpful assistant. Use web_search for current info or if unsure.",
    tools=[web_search],
)
