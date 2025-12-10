import os
import time
import requests
import pathlib
import subprocess
from dotenv import load_dotenv

# Load .env from project root
env_path = pathlib.Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "meta-llama/llama-3.1-8b-instruct"

# --------- OPTIONAL: local llama.cpp fallback config ----------
# TODO: change these to your actual paths if you want real local fallback
LLAMA_BIN = r"C:\path\to\llama.cpp\main.exe"  # change me
LLAMA_MODEL = r"C:\path\to\your_model.gguf"  # change me


def call_local_model(prompt: str, system: str = "You are a helpful assistant."):
    """
    Optional fallback using llama.cpp CLI.
    If not configured, returns a friendly message.
    """
    if not (os.path.exists(LLAMA_BIN) and os.path.exists(LLAMA_MODEL)):
        return "⚠️ OpenRouter failed and local model fallback is not configured. Please set LLAMA_BIN and LLAMA_MODEL."

    try:
        full_prompt = f"{system}\n\nUser: {prompt}\nAssistant:"
        result = subprocess.run(
            [
                LLAMA_BIN,
                "-m",
                LLAMA_MODEL,
                "-p",
                full_prompt,
                "-n",
                "512",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except Exception as e:
        return f"⚠️ Local model fallback error: {e}"


def call_ai(prompt, system="You are a helpful learning assistant.", max_tokens=2000):
    """
    Call OpenRouter API with configurable token limit

    Args:
        prompt: User prompt
        system: System message
        max_tokens: Maximum tokens in response (default 2000, increased from 350)
    """
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,  # Now configurable!
    }

    last_error = None
    last_status = None

    for attempt in range(5):
        try:
            resp = requests.post(url, headers=headers, json=data, timeout=60)

            last_status = resp.status_code

            # Handle rate limit with backoff
            if resp.status_code == 429:
                time.sleep(2**attempt)
                continue

            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

        except Exception as e:
            last_error = str(e)
            time.sleep(0.5)

    # If we reach here, OpenRouter failed → try local fallback for 401/429/timeout
    if last_status in (401, 429, 500, 502, 503):
        return call_local_model(prompt, system)

    return f"⚠️ AI Error: {last_error or 'Unknown error'}"
