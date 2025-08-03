from io import BytesIO
from PyPDF2 import PdfReader
from my_agent.state import InputState, OutputState

def extract_text_from_pdf(state: InputState) -> OutputState:
    lesson_content = state["lesson_text"]
    
    # Handle both bytes (PDF) and string input
    if isinstance(lesson_content, bytes):
        # Create a file-like object from the bytes
        pdf_file = BytesIO(lesson_content)
        
        # Read the PDF
        reader = PdfReader(pdf_file)
        text = "".join(page.extract_text() for page in reader.pages)
    else:
        # If it's already a string, use it directly
        text = lesson_content
    
    print("----------------------------------------------")
    print(text)
    print("----------------------------------------------")
    return {"lesson_text": text}