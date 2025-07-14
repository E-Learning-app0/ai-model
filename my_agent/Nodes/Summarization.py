from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from my_agent.state import InputState
from my_agent.Nodes.Call_Api import call_openrouter


def summarize_text(state: InputState) -> InputState:
    prompt = (
    "Vous êtes un assistant qui résume des textes pédagogiques.\n"
    "Veuillez fournir un résumé clair et detaille , concis et complet du contenu de la leçon ci-dessous.\n"
    "Le résumé doit couvrir les points essentiels sans ajouter d'informations non présentes dans le texte.\n\n"
    "Contenu de la leçon :\n"
    + state["lesson_text"]
)

    summary = call_openrouter(prompt)

    print("-----------Summary------------")
    print(summary)
    return {"lesson_text": summary.strip()}
