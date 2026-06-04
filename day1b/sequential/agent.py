from config import get_model

from google.adk.agents import Agent, SequentialAgent

outline_agent = Agent(
    name="OutlineAgent",
    model=get_model(),
    instruction="""Create a blog outline for the given topic with:
    1. A catchy headline
    2. An introduction hook
    3. 3-5 main sections with 2-3 bullet points each
    4. A concluding thought""",
    output_key="blog_outline",
)

writer_agent = Agent(
    name="WriterAgent",
    model=get_model(),
    instruction="""Following this outline strictly: {blog_outline}
    Write a brief 200-300 word blog post with an engaging tone.""",
    output_key="blog_draft",
)

editor_agent = Agent(
    name="EditorAgent",
    model=get_model(),
    instruction="""Edit this draft: {blog_draft}
    Fix grammatical errors, improve flow, and enhance clarity.""",
    output_key="final_blog",
)

root_agent = SequentialAgent(
    name="BlogPipeline",
    sub_agents=[outline_agent, writer_agent, editor_agent],
)