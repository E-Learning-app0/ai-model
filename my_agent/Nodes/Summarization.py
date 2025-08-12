from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from my_agent.state import InputState
from my_agent.Nodes.Call_Api import call_openrouter
import redis
import json



redis_client = redis.Redis(host='localhost', port=6379, db=0)
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
