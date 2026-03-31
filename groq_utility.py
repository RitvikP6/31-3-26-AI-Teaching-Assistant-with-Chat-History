import os
from pathlib import Path

from groq import Groq


SYSTEM_PROMPT = (
    "You are a helpful AI teaching assistant. Give clear, accurate, beginner-friendly "
    "answers with short examples when useful."
)


def _load_local_env():
    env_path = Path(__file__).with_name(".env")
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key and key not in os.environ:
            os.environ[key] = value


def generate_response(question, temperature=0.5, max_tokens=1024):
    _load_local_env()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return (
            "GROQ_API_KEY is not set. Create a local .env file in this project with:\n"
            'GROQ_API_KEY="your_groq_api_key"'
        )

    client = Groq(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
            temperature=temperature,
            max_completion_tokens=min(max_tokens, 4096),
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        error_text = str(exc)
        if "invalid_api_key" in error_text or "Invalid API Key" in error_text:
            return (
                "Your Groq API key is invalid.\n"
                "Update GROQ_API_KEY in your local .env file or terminal, then restart the app."
            )
        return f"Sorry, I couldn't generate a response right now: {error_text}"
