import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from typing import Any, Dict
from config import get_model
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.tool_context import ToolContext
from google.genai import types

APP_NAME = "state_demo"
USER_ID = "user_01"


def save_userinfo(tool_context: ToolContext, user_name: str, country: str) -> Dict[str, Any]:
    """Records and saves user name and country in session state.

    Args:
        user_name: The username to store
        country: The user's country
    """
    tool_context.state["user:name"] = user_name
    tool_context.state["user:country"] = country
    return {"status": "success"}


def retrieve_userinfo(tool_context: ToolContext) -> Dict[str, Any]:
    """Retrieves user name and country from session state."""
    user_name = tool_context.state.get("user:name", "Username not found")
    country = tool_context.state.get("user:country", "Country not found")
    return {"status": "success", "user_name": user_name, "country": country}


root_agent = LlmAgent(
    model=get_model(),
    name="stateful_chat_bot",
    description="""A chatbot with session state tools.
    * Use save_userinfo tool when user provides their name and country.
    * Use retrieve_userinfo tool when asked about user name or country.
    """,
    tools=[save_userinfo, retrieve_userinfo],
)

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

    # Inspect session state after conversation
    session = await session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=session_id
    )
    print(f"\nSession state: {session.state}")


async def main():
    # Demo: agent saves and retrieves structured state
    await run_session(
        [
            "Hi, what is my name?",           # Agent doesn't know yet
            "My name is Sam. I'm from Poland.", # Agent saves to state
            "What is my name and country?",    # Agent retrieves from state
        ],
        "state-demo-session",
    )

    # New session — state is isolated
    await run_session(
        ["What is my name?"],
        "isolated-session",
    )


if __name__ == "__main__":
    asyncio.run(main())