from dotenv import load_dotenv
load_dotenv()

from google.adk.models.anthropic_llm import AnthropicLlm

def get_model(model_name="claude-sonnet-4-6"):
    return AnthropicLlm(model=model_name)
