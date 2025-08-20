import logging
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from my_agent.state import InputState, OutputState
from dotenv import load_dotenv
from openai import OpenAI
from my_agent.Nodes.Call_Api import call_openrouter
import re

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("agent-service")  # custom logger

question_prompt = ChatPromptTemplate.from_messages([
    ("system", "Generate 10 4-choice questions with answers from the following lesson content."),
    ("user", "{lesson_text}")
])

def generate_questions(state: InputState) -> OutputState:
    prompt = (
        "Génère 5 questions avec 4 options chacune. TOUTES LES OPTIONS (A/B/C/D DOIVENT ÊTRE PRÉSENTES).\n\n"
        "Pour chaque question, fournis la bonne réponse immédiatement après les options dans ce format :\n"
        "Réponse : X\n\n"
        "Q1 : [Question]\n"
        "A) [Doit être une option valide]\n"  
        "B) [Doit être une option valide]\n"
        "C) [Doit être une option valide]\n"  
        "D) [Doit être une option valide]\n"
        "Réponse : [A/B/C/D]\n"
        "---\n"
        "(Répéter pour Q2-Q5)\n\n"
        "TEXTE SOURCE :\n" + state["lesson_text"] + 
        "\n\n**GÉNÉRER.**"
    )

    logger.info("Start generation of QCM questions")
    try:
        raw_output = call_openrouter(prompt)
        logger.info("Received raw output from OpenRouter API")
        logger.info(raw_output)
    except Exception as e:
        logger.error(f"Error during OpenRouter call: {e}", exc_info=True)
        return {'questions': [], 'answers': []}

    questions = []
    answers = []

    lines = [line.strip() for line in raw_output.split('\n') if line.strip()]
    current_question = None
    current_options = []

    for line in lines:
        # Detect new question: either "1." or "Q1:"
        if (line[0].isdigit() and line[1] == '.') or line.upper().startswith('Q'):
            if current_question and len(current_options) == 4:
                questions.append({
                    'question': current_question,
                    'options': current_options
                })
            current_question = line
            current_options = []

        # Collect options
        elif line.startswith(('A)', 'B)', 'C)', 'D)')):
            current_options.append(line)

        # Capture answer (in French or English)
        elif line.lower().startswith('réponse') or line.lower().startswith('answer'):
            answer = line.split(':')[-1].strip().upper()
            if answer in ('A', 'B', 'C', 'D'):
                answers.append(answer)

    # Add the last question if complete
    if current_question and len(current_options) == 4 and len(answers) > len(questions):
        questions.append({
            'question': current_question,
            'options': current_options
        })

    # Ensure matching counts
    questions = questions[:len(answers)]
    answers = answers[:len(questions)]

    logger.info(f"Generated {len(questions)} questions with {len(answers)} answers")
    return {
        'questions': questions,
        'answers': answers
    }
