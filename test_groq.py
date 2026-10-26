
import os
from dotenv import load_dotenv
from groq import Groq

print("1. Starting test...", flush=True)

load_dotenv(".env")
api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

print("2. API key found:", bool(api_key), flush=True)
print("3. Model:", model, flush=True)

if not api_key:
    raise RuntimeError("GROQ_API_KEY is missing")

client = Groq(api_key=api_key, timeout=30.0, max_retries=0)

print("4. Sending request to Groq...", flush=True)

response = client.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "user",
            "content": "Reply with exactly: BLACKVAULT connection successful",
        }
    ],
    temperature=0,
    max_completion_tokens=50,
)

print("5. Groq responded:", flush=True)
print(response.choices[0].message.content, flush=True)
