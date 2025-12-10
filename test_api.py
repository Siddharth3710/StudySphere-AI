import os
import requests
from dotenv import load_dotenv
import pathlib

# Load environment file correctly
env_path = pathlib.Path(__file__).parent / ".env"
load_dotenv(env_path)

API_KEY = os.getenv("OPENROUTER_API_KEY")
print("Loaded API Key:", bool(API_KEY))

headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

data = {
    "model": "meta-llama/llama-3.1-8b-instruct",
    "messages": [{"role": "user", "content": "Hello, this is a test request!"}],
}

response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data
)

print("Status:", response.status_code)
print("Response:", response.text)
