from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
from my_agent.agent import graph


lesson_text = r"C:\Users\ASUS\Desktop\E-learning_app\ai-model\testc.pdf"
response = graph.invoke({"lesson_text": lesson_text})


print("Questions:")
for q in response["questions"]:
    print(f"- {q}")

print("\nAnswers:")
for a in response["answers"]:
    print(f"- {a}")
