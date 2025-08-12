from typing import TypedDict, Union
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages

class InputState(TypedDict):
    lesson_text: Union[str, bytes]  # Allow both string and bytes for PDF processing
    module_id: str

class OutputState(TypedDict):
    questions: list[str]
    answers: list[str]
    module_done: bool  # add module_done flag
    generate_exam: bool  # add generate_exam flag
    
class OverallState(TypedDict):
    lesson_text: Union[str, bytes]  # Allow both string and bytes
    questions: list[str]
    answers: list[str]
    messages: list[BaseMessage]
    module_done: bool
    generate_exam: bool
