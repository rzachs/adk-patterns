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
from google.adk.memory import InMemoryMemoryService
from google.adk.tools import load_memory, preload_memory
from google.genai import types

APP_NAME = "memory_demo"
USER_ID = "user_01"

# Both services needed
session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()


async def run_session(runner_instance, queries, session_id="default"):
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

        async for event in runner_instance.run_async(
            user_id=USER_ID, session_id=session.id, new_message=content
        ):
            if event.content and event.content.parts:
                if event.content.parts[0].text and event.content.parts[0].text != "None":
                    print(f"Agent > {event.content.parts[0].text}")

    return session


# --- Demo 1: Manual memory workflow ---
async def demo_manual_memory():
    print("\n" + "="*60)
    print("DEMO 1: Manual Memory Workflow")
    print("="*60)

    # Agent without memory tools first
    basic_agent = LlmAgent(
        model=get_model(),
        name="MemoryDemoAgent",
        instruction="Answer user questions in simple words.",
    )

    basic_runner = Runner(
        agent=basic_agent,
        app_name=APP_NAME,
        session_service=session_service,
        memory_service=memory_service,
    )

    # Step 1: Have a conversation
    session = await run_session(
        basic_runner,
        "My favorite color is blue-green. Can you write a Haiku about it?",
        "conversation-01",
    )

    # Step 2: Manually save to memory
    await memory_service.add_session_to_memory(session)
    print("\n✅ Session saved to memory")

    # Step 3: New agent WITH load_memory tool
    memory_agent = LlmAgent(
        model=get_model(),
        name="MemoryDemoAgent",
        instruction="Answer user questions. Use load_memory tool to recall past conversations.",
        tools=[load_memory],
    )

    memory_runner = Runner(
        agent=memory_agent,
        app_name=APP_NAME,
        session_service=session_service,
        memory_service=memory_service,
    )

    # Step 4: Ask in a NEW session — agent must use memory
    await run_session(
        memory_runner,
        "What is my favorite color?",
        "color-test",  # Different session
    )


# --- Demo 2: Automatic memory with callbacks ---
async def demo_auto_memory():
    print("\n" + "="*60)
    print("DEMO 2: Automatic Memory with Callbacks")
    print("="*60)

    async def auto_save_to_memory(callback_context):
        """Automatically save session to memory after each agent turn."""
        await callback_context._invocation_context.memory_service.add_session_to_memory(
            callback_context._invocation_context.session
        )

    auto_memory_agent = LlmAgent(
        model=get_model(),
        name="AutoMemoryAgent",
        instruction="Answer user questions.",
        tools=[preload_memory],
        after_agent_callback=auto_save_to_memory,
    )

    auto_runner = Runner(
        agent=auto_memory_agent,
        app_name=APP_NAME,
        session_service=session_service,
        memory_service=memory_service,
    )

    # First conversation — callback auto-saves
    await run_session(
        auto_runner,
        "I gifted a new toy to my nephew on his 1st birthday!",
        "auto-save-test",
    )

    # Second conversation — different session, agent retrieves from memory
    await run_session(
        auto_runner,
        "What did I gift my nephew?",
        "auto-save-test-2",
    )


async def main():
    await demo_manual_memory()
    await demo_auto_memory()


if __name__ == "__main__":
    asyncio.run(main())