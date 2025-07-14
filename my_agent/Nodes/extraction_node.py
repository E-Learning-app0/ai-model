from PyPDF2 import PdfReader
from my_agent.state import InputState,OutputState
def extract_text_from_pdf(state: InputState) -> OutputState:
    reader = PdfReader(state["lesson_text"])
    text = "".join(page.extract_text() for page in reader.pages)
    print(text)
    return {"lesson_text": text}
