import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from config import get_model
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types

APP_NAME = "persistent_demo"
USER_ID = "user_01"

chatbot_agent = LlmAgent(
    model=get_model(),
    name="persistent_chat_bot",
    description="A chatbot with persistent memory",
)

# SQLite database — survives restarts
session_service = DatabaseSessionService(db_url="sqlite+aiosqlite:///day3a_sessions.db")
runner = Runner(agent=chatbot_agent, app_name=APP_NAME, session_service=session_service)


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
    # Run 1: Introduce name and ask a question
    await run_session(
        [
            "Hi, I am Sam! What is the capital of India?",
            "What is my name?",
        ],
        "persistent-session-01",
    )

    print("\n--- Simulating restart: same session ID, same DB ---\n")

    # Run 2: Resume the same session — agent should still know the name
    await run_session(
        [
            "What is the capital of France?",
            "What is my name?",  # Should still remember Sam
        ],
        "persistent-session-01",  # Same session ID
    )


if __name__ == "__main__":
    asyncio.run(main())