from io import BytesIO
from PyPDF2 import PdfReader
from my_agent.state import InputState, OutputState

def extract_text_from_pdf(state: InputState) -> OutputState:
    # Create a file-like object from the bytes
    pdf_file = BytesIO(state["lesson_text"])
    
    # Read the PDF
    reader = PdfReader(pdf_file)
    text = "".join(page.extract_text() for page in reader.pages)
    print("----------------------------------------------")
    print(text)
    print("----------------------------------------------")
    return {"lesson_text": text}