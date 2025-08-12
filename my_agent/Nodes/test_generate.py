from typing import Dict,List
from my_agent.state import InputState, OutputState
from my_agent.Nodes.Call_Api import call_openrouter
import xml.etree.ElementTree as ET
import xml.dom.minidom
import re





def generate_qcm(state: InputState) -> OutputState:
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
    
    
    print("questions")
    print(questions)
    print("answers")
    print(answers)

    return {
        'questions': questions,  # Max 5 questions
        'answers': answers       # Matching answers
    }



def generate_true_false(state: InputState) -> OutputState:
    # Prompt for generating True/False questions
    prompt = (
        "Generate 5 True/False questions based on the lesson content.\n\n"
        "For each question, provide the correct answer immediately after in this format:\n"
        "Answer: True OR Answer: False\n\n"
        "Q1: [Question]\n"
        "Answer: [True/False]\n"
        "---\n"
        "Q2: [Question]\n"
        "Answer: [True/False]\n"
        "---\n"
        "Q3: [Question]\n"
        "Answer: [True/False]\n"
        "---\n"
        "Q4: [Question]\n"
        "Answer: [True/False]\n"
        "---\n"
        "Q5: [Question]\n"
        "Answer: [True/False]\n\n"
        
        "SOURCE TEXT:\n" + state["lesson_text"] + 
        "\n\n**GENERATE.**"
    )

    # Get the raw output from the model
    raw_output = call_openrouter(prompt)
    
    print("Raw True/False output:")
    print(raw_output)
    print("----------------------------")
    
    # Initialize lists
    questions = []
    answers = []
    
    # Split into individual lines
    lines = [line.strip() for line in raw_output.split('\n') if line.strip()]
    
    current_question = None
    
    for line in lines:
        # Detect new question
        if line.startswith('Q'):
            # Save previous question if we have one
            if current_question is not None:
                questions.append({'question': current_question})
            current_question = line
        
        # Capture answer
        elif line.lower().startswith('answer:'):
            answer = line.split(':')[-1].strip().capitalize()
            if answer in ('True', 'False'):
                answers.append(answer)
    
    # Add last question if missing
    if current_question is not None and len(answers) > len(questions):
        questions.append({'question': current_question})
    
    # Ensure counts match
    questions = questions[:len(answers)]
    answers = answers[:len(questions)]
    
    print("True/False questions:")
    print(questions)
    print("True/False answers:")
    print(answers)
    print("----------------------------")
    
    return {
        'questions': questions,  # Max 5 questions
        'answers': answers       # Matching answers
    }

def generate_resolution(state: InputState) -> OutputState:
    # Prompt to generate resolution questions
    prompt = (
        "Generate 2 resolution/explanation questions based on the lesson content.\n\n"
        "For each question, provide a detailed explanation as the answer.\n"
        "Format:\n"
        "Q1: [Question requiring explanation]\n"
        "Answer: [Detailed explanation]\n"
        "---\n"
        "Q2: [Another question requiring explanation]\n"
        "Answer: [Detailed explanation]\n\n"
        
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
    current_answer = []
    
    for line in lines:
        # Detect new question
        if line.startswith('Q'):
            # Save previous question and answer if we have them
            if current_question is not None and current_answer:
                questions.append({'question': current_question})
                answers.append(' '.join(current_answer))
            
            current_question = line
            current_answer = []
        
        # Capture answer
        elif line.lower().startswith('answer:'):
            answer_text = line.split(':', 1)[-1].strip()
            current_answer.append(answer_text)
        elif current_answer:  # Continue collecting answer text
            current_answer.append(line)
    
    # Add last question if missing
    if current_question is not None and current_answer and len(answers) < len(questions) + 1:
        questions.append({'question': current_question})
        answers.append(' '.join(current_answer))
    
    # Ensure counts match
    questions = questions[:len(answers)]
    answers = answers[:len(questions)]
    
    print("resolution questions")
    print(questions)
    print("resolution answers")
    print(answers)
    
    return {
        'questions': questions,
        'answers': answers
    }



def generate_exam(state: InputState) -> OutputState:
    print("\nStart generation test")
    try:
        print("\nStart generation qcm")
        qcm = generate_qcm(state)
        print("\nStart generation true false")
        tf = generate_true_false(state)
        print("\nStart generation resolution")
        res = generate_resolution(state)
        print("\nEnd generation")

        # Fusionner questions et réponses
        questions = qcm['questions'] + tf['questions'] + res['questions']
        answers = qcm['answers'] + tf['answers'] + res['answers']

        if not questions or not answers:
            raise ValueError("Aucune question ou réponse générée.")
        return {
            'questions': questions,
            'answers': answers
        }
    except Exception as e:
        print(f"Erreur lors de la génération de l'examen : {e}")
        return {
            'questions': [],
            'answers': [],
            'error': str(e)
        }
