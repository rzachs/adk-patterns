from config import get_model

from google.adk.agents import Agent, LoopAgent, SequentialAgent
from google.adk.tools import FunctionTool

initial_writer_agent = Agent(
    name="InitialWriterAgent",
    model=get_model(),
    instruction="Based on the user's prompt, write the first draft of a short story (100-150 words). Output only the story text, no introduction or explanation.",
    output_key="current_story",
)

critic_agent = Agent(
    name="CriticAgent",
    model=get_model(),
    instruction="""You are a constructive story critic. Review the story below.
Story: {current_story}

Evaluate plot, characters, and pacing.
- If the story is well-written and complete, respond with the exact phrase: "APPROVED"
- Otherwise, provide 2-3 specific, actionable suggestions for improvement.""",
    output_key="critique",
)

def exit_loop():
    """Call this function ONLY when the critique is 'APPROVED', indicating the story is finished."""
    return {"status": "approved", "message": "Story approved. Exiting refinement loop."}

refiner_agent = Agent(
    name="RefinerAgent",
    model=get_model(),
    instruction="""You are a story refiner.

Story Draft: {current_story}
Critique: {critique}

- IF the critique is EXACTLY "APPROVED", you MUST call the exit_loop function and nothing else.
- OTHERWISE, rewrite the story to fully incorporate the feedback.""",
    output_key="current_story",
    tools=[FunctionTool(exit_loop)],
)

story_refinement_loop = LoopAgent(
    name="StoryRefinementLoop",
    sub_agents=[critic_agent, refiner_agent],
    max_iterations=2,
)

root_agent = SequentialAgent(
    name="StoryPipeline",
    sub_agents=[initial_writer_agent, story_refinement_loop],
)