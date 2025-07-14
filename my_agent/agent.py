from langgraph.graph import StateGraph, START, END
from my_agent.state import OverallState,InputState,OutputState
from my_agent.Nodes.extraction_node import extract_text_from_pdf
from my_agent.Nodes.question_generation import generate_questions
from my_agent.Nodes.Summarization  import summarize_text

builder = StateGraph(OverallState,input=InputState,output=OutputState)
builder.add_node("summarize", summarize_text)

builder.add_node("extract_text", extract_text_from_pdf)
builder.add_node("generate_questions", generate_questions)

"""
builder.add_edge(START, "summarize")
builder.add_edge("summarize", "generate_questions")
builder.add_edge("generate_questions", END)
"""
builder.add_edge(START, "extract_text")
builder.add_edge("extract_text", "summarize")
builder.add_edge("summarize", "generate_questions")
builder.add_edge("generate_questions", END)

graph = builder.compile()
