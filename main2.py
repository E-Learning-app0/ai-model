# main.py
import uuid, json
from fastapi import FastAPI, UploadFile, File, HTTPException, Body, Response
from fastapi.middleware.cors import CORSMiddleware
import redis
import httpx
import os
from my_agent.agent import graph

app = FastAPI(
    title="E-Learning Agent Service", 
    description="AI Agent service for quiz and exam generation",
    version="1.0.0"
)

# Environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
CONTENT_SERVICE_URL = os.getenv("CONTENT_SERVICE_URL", "https://nginx-gateway.blackbush-661cc25b.spaincentral.azurecontainerapps.io")

# Redis client with external host support and Azure Redis Cache compatibility
if REDIS_PASSWORD:
    r = redis.Redis(
        host=REDIS_HOST, 
        port=REDIS_PORT, 
        db=0,
        password=REDIS_PASSWORD,
        ssl=True,
        ssl_check_hostname=False,
        ssl_cert_reqs=None
    )
else:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
CACHE_TTL = 24 * 3600  # 24 hours

QUIZ_SERVICE_EXAM_API = f"{CONTENT_SERVICE_URL}/api/v1/exams"

# Health check endpoint
@app.get("/health")
async def health_check():
    logger.info(f"----Hello World ---")
    return {
        "status": "healthy",
        "service": "agent-service",
        "version": "1.0.0",
        "content_service_url": CONTENT_SERVICE_URL,
        "redis_host": REDIS_HOST,
        "redis_port": REDIS_PORT
    }

from pydantic import BaseModel
class QuizRequest(BaseModel):
    pdf_path: str

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("agent-service")  # custom logger

@app.post("/upload-quiz")
async def upload_quiz(pdf: UploadFile = File(...)):
    logger.info(f"Received upload request: filename={pdf.filename}")
    try:
        # Lazy import to avoid startup issues
        from my_agent.agent import graph
        
        content = await pdf.read()
        logger.info(f"PDF read successfully, size={len(content)} bytes")
        resp = graph.invoke({"lesson_text": content})
        logger.info(f"Graph invocation result: {resp}")
        logger.info(f"start Quiz generating")

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
        logger.info(f"Quiz generated successfully: {quiz}")

        quiz_id = str(uuid.uuid4())
        r.setex(quiz_id, CACHE_TTL, json.dumps(quiz))

        return {"quizId": quiz_id}
    except Exception as e:
        logger.exception(f"Quiz generated faild")

        raise HTTPException(status_code=500, detail=f"Quiz generation error: {str(e)}")


@app.post("/upload-exam")
async def upload_exam(pdf: UploadFile = File(...), module_id: str = None):
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
    data = r.get(exam_id)
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


