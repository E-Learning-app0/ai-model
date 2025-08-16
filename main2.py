# main.py
import uuid, json
from fastapi import FastAPI, UploadFile, File, HTTPException,Body,Response
from fastapi.middleware.cors import CORSMiddleware
import redis
from my_agent.agent import graph
app = FastAPI()
#app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
r = redis.Redis(host="localhost", port=6379, db=0)  # Basic redis-py client :contentReference[oaicite:2]{index=2}
CACHE_TTL = 24 * 3600  # 24 hours

QUIZ_SERVICE_EXAM_API = "http://localhost:8002/exams"

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


@app.post("/upload-exam")
async def upload_exam(pdf: UploadFile = File(...)):
    try:
        content = await pdf.read()
        
        # Force exam generation by setting module_done flag
        # This will trigger the exam generation path in the graph
        resp = graph.invoke({
            "lesson_text": content,
            "module_done": True,
            "generate_exam": True
        })
        
        # Process exam questions and answers
        exam_questions = []
        for i, q in enumerate(resp["questions"]):
            question_data = {
                "id": i + 1,
                "question": q["question"],
                "type": "mcq" if "options" in q else "true_false" if resp["answers"][i] in ["True", "False"] else "resolution",
                "answer": resp["answers"][i]
            }
            
            # Add options for MCQ questions
            if "options" in q:
                question_data["options"] = q["options"]
                question_data["answerIndex"] = ord(resp["answers"][i].upper()) - ord("A") if resp["answers"][i] in ["A", "B", "C", "D"] else None
            
            exam_questions.append(question_data)
        
        exam = {
            "title": "Auto Exam",
            "questions": exam_questions,
            "total_questions": len(exam_questions)
        }
        
        exam_id = str(uuid.uuid4())
        r.setex(exam_id, CACHE_TTL, json.dumps(exam))
        # Store first version in Postgres via Exam Service
        async with httpx.AsyncClient() as client:
            await client.post(QUIZ_SERVICE_EXAM_API, json={
                "id": exam_id,
                "title": "Auto Exam",
                "description": "Generated from PDF",
                "content": exam,       # the full JSON of questions
                "module_id": module_id
            })



        return {"examId": exam_id}
    except ValueError as e:
        raise HTTPException(status_code=503, detail=f"AI Service Error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")


@app.get("/quiz/{quiz_id}")
async def get_quiz(quiz_id: str):
    data = r.get(quiz_id)
    if not data:
        raise HTTPException(404, "Quiz not found or expired")
    return json.loads(data)


@app.get("/exam/{exam_id}")
async def get_exam(exam_id: str):
    ؤ
    if not data:
        raise HTTPException(404, "Exam not found or expired")
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


