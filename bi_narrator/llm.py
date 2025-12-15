import google.generativeai as genai
from bi_narrator.config import GEMINI_MODEL_NAME
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY is not set...")

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

_MODEL = genai.GenerativeModel(GEMINI_MODEL_NAME)
  
def call_llm_local(
    prompt: str,
    max_tokens: int,
    temperature: float,
) -> str:
    """
    Gemini-based LLM call.
    Stateless, API-backed.
    """

    response = _MODEL.generate_content(
        prompt,
        generation_config={
            "max_output_tokens": max_tokens,
            "temperature": temperature,
        }
    )

    if not response or not response.text:
        return ""

    return response.text.strip()