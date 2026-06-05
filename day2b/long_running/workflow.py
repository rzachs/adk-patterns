import asyncio
import uuid
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from google.genai import types
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.apps.app import App, ResumabilityConfig

from agent import shipping_agent

# --- Setup ---
shipping_app = App(
    name="shipping_coordinator",
    root_agent=shipping_agent,
    resumability_config=ResumabilityConfig(is_resumable=True),
)

session_service = InMemorySessionService()

shipping_runner = Runner(
    app=shipping_app,
    session_service=session_service,
)

# --- Helper functions ---
def check_for_approval(events):
    for event in events:
        if event.content and event.content.parts:
            for part in event.content.parts:
                if (
                    part.function_call
                    and part.function_call.name == "adk_request_confirmation"
                ):
                    return {
                        "approval_id": part.function_call.id,
                        "invocation_id": event.invocation_id,
                    }
    return None


def print_agent_response(events):
    for event in events:
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(f"Agent > {part.text}")


def create_approval_response(approval_info, approved):
    confirmation_response = types.FunctionResponse(
        id=approval_info["approval_id"],
        name="adk_request_confirmation",
        response={"confirmed": approved},
    )
    return types.Content(
        role="user", parts=[types.Part(function_response=confirmation_response)]
    )


# --- Main workflow ---
async def run_shipping_workflow(query: str, auto_approve: bool = True):
    print(f"\n{'='*60}")
    print(f"User > {query}\n")

    session_id = f"order_{uuid.uuid4().hex[:8]}"

    await session_service.create_session(
        app_name="shipping_coordinator",
        user_id="test_user",
        session_id=session_id
    )

    query_content = types.Content(role="user", parts=[types.Part(text=query)])
    events = []

    # Step 1: Send initial request
    async for event in shipping_runner.run_async(
        user_id="test_user",
        session_id=session_id,
        new_message=query_content
    ):
        events.append(event)

    # Step 2: Check if agent paused for approval
    approval_info = check_for_approval(events)

    if approval_info:
        print(f"Pausing for approval...")
        print(f"Human decision: {'APPROVE' if auto_approve else 'REJECT'}\n")

        # Step 3: Resume with human decision
        async for event in shipping_runner.run_async(
            user_id="test_user",
            session_id=session_id,
            new_message=create_approval_response(approval_info, auto_approve),
            invocation_id=approval_info["invocation_id"],
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(f"Agent > {part.text}")
    else:
        print_agent_response(events)

    print(f"{'='*60}\n")


async def main():
    # Small order - auto approved
    await run_shipping_workflow("Ship 3 containers to Singapore")

    # Large order - approved
    await run_shipping_workflow("Ship 10 containers to Rotterdam", auto_approve=True)

    # Large order - rejected
    await run_shipping_workflow("Ship 8 containers to Los Angeles", auto_approve=False)


if __name__ == "__main__":
    asyncio.run(main())