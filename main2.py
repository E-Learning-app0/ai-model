# main.py
import uuid, json
from fastapi import FastAPI, UploadFile, File, HTTPException,Body,Response
from fastapi.middleware.cors import CORSMiddleware
import redis
from my_agent.agent import graph

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
r = redis.Redis(host="localhost", port=6379, db=0)  # Basic redis-py client :contentReference[oaicite:2]{index=2}
CACHE_TTL = 24 * 3600  # 24 hours

from pydantic import BaseModel
class QuizRequest(BaseModel):
    pdf_path: str


@app.post("/upload-quiz")
async def upload_quiz(pdf: UploadFile = File(...)):
    content = await pdf.read()
    resp = graph.invoke({"lesson_text": content})
    quiz = {
        "title": "Auto Quiz",
        "questions": [
            {
                "id": i + 1,
                "question": q["question"],
                "options": q["options"],
                "answerIndex": ord(resp["answers"][i].upper()) - ord("A"),
            }
            for i, q in enumerate(resp["questions"])
        ]
    }
    quiz_id = str(uuid.uuid4())
    r.setex(quiz_id, CACHE_TTL, json.dumps(quiz))
    return {"quizId": quiz_id}


@app.get("/quiz/{quiz_id}")
async def get_quiz(quiz_id: str):
    data = r.get(quiz_id)
    if not data:
        raise HTTPException(404, "Quiz not found or expired")
    return json.loads(data)


from fastapi.responses import FileResponse
import os


FILES_DIR = "C:/Users/ASUS/Postman/files"  # Folder containing PDFs

@app.get("/files/{filename}")
def get_file(filename: str):
    file_path = os.path.join(FILES_DIR, filename)
    if not os.path.exists(file_path):
        return Response(content="File not found", status_code=404)
    
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=filename,
        headers={
            "Content-Disposition": f'inline; filename="{filename}"'
        }
    )