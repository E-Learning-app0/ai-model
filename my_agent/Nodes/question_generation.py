from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from my_agent.state import InputState,OutputState
from dotenv import load_dotenv
from openai import OpenAI
from my_agent.Nodes.Call_Api import call_openrouter
import re


question_prompt = ChatPromptTemplate.from_messages([
    ("system", "Generate 10 4-choice questions with answers from the following lesson content."),
    ("user", "{lesson_text}")
])

def generate_questions(state: InputState) -> OutputState:
    # Your original prompt (unchanged)
    prompt = (
        "Generate 5 questions with 4 options each. ALL OPTIONS (A/B/C/D) MUST BE PRESENT.\n\n"
        "For each question, provide the correct answer immediately after the options in this format:\n"
        "Answer: X\n\n"
        "Q1: [Question]\n"
        "A) [Must be a valid option]\n"  
        "B) [Must be a valid option]\n"
        "C) [Must be a valid option]\n"  
        "D) [Must be a valid option]\n"
        "Answer: [A/B/C/D]\n"
        "---\n"
        "(Repeat for Q2-Q5)\n\n"
        
        "SOURCE TEXT:\n" + state["lesson_text"] + 
        "\n\n**GENERATE.**"
    )

    # Get the raw output
    raw_output = call_openrouter(prompt)
    
    # Initialize lists
    questions = []
    answers = []
    
    # Split into individual lines
    lines = [line.strip() for line in raw_output.split('\n') if line.strip()]
    
    current_question = None
    current_options = []
    
    for line in lines:
        # Detect new question
        if line.startswith('Q'):
            # Save previous question if complete
            if current_question and len(current_options) == 4:
                questions.append({
                    'question': current_question,
                    'options': current_options
                })
            
            # Start new question
            current_question = line
            current_options = []
        
        # Collect options
        elif line.startswith(('A)', 'B)', 'C)', 'D)')):
            current_options.append(line)
        
        # Capture answer
        elif line.lower().startswith('answer:'):
            answer = line.split(':')[-1].strip().upper()
            if answer in ('A', 'B', 'C', 'D'):
                answers.append(answer)
    
    # Add the last question if complete
    if current_question and len(current_options) == 4 and len(answers) > len(questions):
        questions.append({
            'question': current_question,
            'options': current_options
        })
    
    # Ensure we have matching counts
    questions = questions[:len(answers)]
    answers = answers[:len(questions)]
    
    return {
        'questions': questions,  # Max 5 questions
        'answers': answers       # Matching answers
    }