import os
import sys
from pathlib import Path

def _load_local_env():
    env_path = Path(__file__).with_name(".env")
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ[key.strip()] = value.strip().strip('"').strip("'")

def _get_api_key():
    _load_local_env()
    api_key = os.getenv("GROQ_API_KEY", "").strip()

    if not api_key:
        raise RuntimeError("❌ GROQ_API_KEY not found in .env file")

    return api_key

def generate_response(prompt, temperature=0.5, max_tokens=1024):
    try:
        from groq import Groq
    except ImportError:
        return "❌ Install groq: pip install groq"

    api_key = _get_api_key()
    client = Groq(api_key=api_key)

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_completion_tokens=max_tokens,
        )
        return completion.choices[0].message.content

    except Exception as e:
        return f"❌ Error: {str(e)}"