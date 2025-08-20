from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from my_agent.state import InputState
from my_agent.Nodes.Call_Api import call_openrouter
import redis
import json
import os

# Redis connection with environment variable support
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# Create Redis connection with Azure Redis Cache support
if REDIS_PASSWORD:
    redis_client = redis.Redis(
        host=REDIS_HOST, 
        port=REDIS_PORT, 
        db=0,
        password=REDIS_PASSWORD,
        ssl=True,
        ssl_check_hostname=False,
        ssl_cert_reqs=None
    )
else:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
def save_summary(lesson_id: str, summary_text: str, ttl_seconds: int = 60*60*24*90):
    key = f"lesson_summary:{lesson_id}"
    redis_client.set(key, json.dumps({"summary": summary_text}), ex=ttl_seconds)
    print(f"Summary saved in Redis with key {key} (TTL {ttl_seconds}s)")


def summarize_text(state: InputState) -> InputState:
    prompt = (
    "Vous êtes un assistant qui résume des textes pédagogiques.\n"
    "Veuillez fournir un résumé clair et detaille , concis et complet du contenu de la leçon ci-dessous.\n"
    "Le résumé doit couvrir les points essentiels sans ajouter d'informations non présentes dans le texte.\n\n"
    "Contenu de la leçon :\n"
    + state["lesson_text"]
)

    summary = call_openrouter(prompt)
    summary = summary.strip()
    # Sauvegarde dans Redis
    lesson_id = state.get("lesson_id", "unknown_lesson")
    save_summary(lesson_id, summary)
    print(summary)
    return {"lesson_text": summary}
