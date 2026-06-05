from dotenv import load_dotenv
load_dotenv()

from google.adk.models.lite_llm import LiteLlm

def get_model(model_name="anthropic/claude-sonnet-4-6"):
    return LiteLlm(model=model_name)
