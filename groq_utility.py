import os
import sys


def _normalize_key(raw_key):
    key = raw_key.strip()
    if (key.startswith('"') and key.endswith('"')) or (key.startswith("'") and key.endswith("'")):
        key = key[1:-1].strip()
    return key


def _prompt_api_key():
    # Use visible input so users can paste/verify the key in the terminal.
    return input("Enter your GROQ_API_KEY: ")


def _get_api_key(force_prompt=False):
    api_key = ""
    if not force_prompt:
        api_key = _normalize_key(os.environ.get("GROQ_API_KEY", ""))
    if not api_key:
        api_key = _normalize_key(_prompt_api_key())
        if api_key:
            os.environ["GROQ_API_KEY"] = api_key
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is required to continue.")
    if " " in api_key:
        raise RuntimeError(
            "GROQ_API_KEY contains spaces. Remove any surrounding quotes or spaces."
        )
    if not api_key.startswith("gsk_"):
        # Warn but do not block; Groq keys commonly start with "gsk_".
        print("Warning: GROQ_API_KEY does not look like a Groq key (expected prefix 'gsk_').")
    return api_key


def generate_response(
    prompt, temperature=0.7, max_tokens=65536, model="openai/gpt-oss-20b"
):
    try:
        from groq import Groq
    except ImportError:
        return (
            "Missing dependency: install the 'groq' package (e.g., `pip install groq`). "
            "On Streamlit Cloud, add it to requirements.txt."
        )
    while True:
        api_key = _get_api_key(force_prompt=False)
        client = Groq(api_key=api_key)
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return completion.choices[0].message.content
        except Exception as exc:
            if exc.__class__.__name__ == "AuthenticationError":
                os.environ.pop("GROQ_API_KEY", None)
                print("Groq authentication failed. Please re-enter your GROQ_API_KEY.")
                # Force prompt on the next loop.
                _get_api_key(force_prompt=True)
                continue
            if exc.__class__.__name__ == "BadRequestError":
                raise RuntimeError(
                    "Groq rejected the request. If this mentions a decommissioned model, "
                    "switch to a supported model like 'llama-3.1-8b-instant' or "
                    "'llama-3.3-70b-versatile'."
                ) from exc
            raise
