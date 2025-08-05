import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def call_openrouter(prompt):
    """
    Calls a free OpenRouter model (e.g., mistralai/mistral-7b-instruct:free)
    """
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://your-app-or-site.com",  # optional
            "X-Title": "MyOpenRouterApp"  # optional
        }

        payload = {
            "model": "mistralai/mistral-7b-instruct:free",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", 
                                 headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    except requests.exceptions.Timeout:
        raise ValueError("OpenRouter API request timed out.")
    except requests.exceptions.ConnectionError:
        raise ValueError("Network error. Cannot reach OpenRouter.")
    except Exception as e:
        raise ValueError(f"OpenRouter error: {str(e)}")

