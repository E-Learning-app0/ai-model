from langgraph.graph import StateGraph, START, END
from my_agent.state import OverallState, InputState, OutputState
from my_agent.Nodes.extraction_node import extract_text_from_pdf
from my_agent.Nodes.question_generation import generate_questions
from my_agent.Nodes.Summarization import summarize_text
from my_agent.Nodes.checkLessons import check_if_module_done
from my_agent.Nodes.CombineSummary import combine_all_summaries
from my_agent.Nodes.test_generate import generate_exam

builder = StateGraph(OverallState, input=InputState, output=OutputState)

builder.add_node("extract_text", extract_text_from_pdf)
builder.add_node("summarize", summarize_text)
builder.add_node("check_if_module_done", check_if_module_done)
builder.add_node("combine_all_summaries", combine_all_summaries)
builder.add_node("generate_questions", generate_questions)  # quiz generator
builder.add_node("generate_exam", generate_exam)            # exam generator

# Flow edges
builder.add_edge(START, "extract_text")
builder.add_edge("extract_text", "summarize")
builder.add_edge("summarize", "check_if_module_done")

# Decision branch (fixed for your langgraph version)
builder.add_conditional_edges(
    "check_if_module_done",
    lambda state: "done" if state.get("module_done") else "not_done",
    {
        "done": "combine_all_summaries",
        "not_done": "generate_questions"
    }
)

builder.add_edge("combine_all_summaries", "generate_exam")
builder.add_edge("generate_questions", END)
builder.add_edge("generate_exam", END)

graph = builder.compile()
