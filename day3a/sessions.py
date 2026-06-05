import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from config import get_model
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

APP_NAME = "sessions_demo"
USER_ID = "user_01"

# Create agent
root_agent = LlmAgent(
    model=get_model(),
    name="chat_bot",
    description="A simple chatbot that remembers conversation history",
)

# In-memory session service — lost on restart
session_service = InMemorySessionService()
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)


async def run_session(queries, session_id="default"):
    print(f"\n### Session: {session_id}")

    try:
        session = await session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=session_id
        )
    except:
        session = await session_service.get_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=session_id
        )

    if isinstance(queries, str):
        queries = [queries]

    for query in queries:
        print(f"\nUser > {query}")
        content = types.Content(role="user", parts=[types.Part(text=query)])

        async for event in runner.run_async(
            user_id=USER_ID, session_id=session.id, new_message=content
        ):
            if event.content and event.content.parts:
                if event.content.parts[0].text and event.content.parts[0].text != "None":
                    print(f"Agent > {event.content.parts[0].text}")


async def main():
    # Demo 1: Agent remembers within the same session
    await run_session(
        [
            "Hi, I am Sam! What is the capital of the United States?",
            "What is my name?",  # Agent should remember
        ],
        "same-session",
    )

    # Demo 2: Different session — agent forgets
    await run_session(
        ["What is my name?"],  # Agent won't know
        "different-session",
    )


if __name__ == "__main__":
    asyncio.run(main())