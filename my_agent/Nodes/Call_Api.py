import os
import requests
from dotenv import load_dotenv

load_dotenv()

def call_openrouter(prompt):
    """
    Free AI function - uses Ollama (completely free and local)
    """
    return call_ollama(prompt)

def call_ollama(prompt):
    """Use local Ollama (completely free)"""
    try:
        payload = {
            "model": "llama3.1:8b",  # Much faster, better quality model (4.7GB)
            "prompt": prompt,
            "stream": False
        }
        # Increased timeout for larger content processing
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=300)
        response.raise_for_status()
        return response.json()["response"]
    except requests.exceptions.Timeout:
        raise ValueError("Ollama processing timeout. Try with shorter content or restart Ollama service.")
    except requests.exceptions.ConnectionError:
        raise ValueError("Ollama is not running. Please start Ollama service: ollama serve")
    except Exception as e:
        raise ValueError(f"Ollama error: {str(e)}. Make sure Ollama is running properly.")


