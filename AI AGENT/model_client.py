
import os

from dotenv import load_dotenv
from groq import Groq

# Load configuration from the BLACKVAULT repository root.
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT_DIR, ".env"))

MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")


def get_client() -> Groq:
    """Create a Groq client using the local environment configuration."""
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Configure it in BLACKVAULT/.env."
        )

    return Groq(api_key=api_key, timeout=30.0, max_retries=0)


def ask_model(messages: list[dict]) -> str:
    """Send a conversation to Groq and return the model's text response."""
    client = get_client()

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0,
        max_completion_tokens=500,
    )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError("The model returned an empty response.")

    return content
