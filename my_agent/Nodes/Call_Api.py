import os
import requests
from dotenv import load_dotenv

load_dotenv()

def call_openrouter(prompt):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("API key not found in environment variables")
    headers = {
        "Authorization": f"Bearer {api_key}",  # Replace with your real key
        "HTTP-Referer": "http://localhost",  # Required by OpenRouter
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistralai/mixtral-8x7b-instruct",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    response.raise_for_status()  # Raise error if request fails
    return response.json()["choices"][0]["message"]["content"]


