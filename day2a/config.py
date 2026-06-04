from dotenv import load_dotenv
load_dotenv()

from google.adk.models.google_llm import Gemini
from google.genai import types

retry_config = types.HttpRetryOptions(
    attempts=5, exp_base=7, initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)

def get_model(model_name="gemini-2.5-flash-lite"):
    return Gemini(model=model_name, retry_options=retry_config)