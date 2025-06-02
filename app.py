from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ai_model import interpret_question_with_ai
import os
import shutil
import base64 # Needed for Base64 encoding
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:5500",
    # Add your production site domain here, e.g., "https://seujogo.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ask_ai_audio")
async def ask_ai_audio(
    audio_file: UploadFile = File(...),
    riddle: str = Form(...),
    riddle_answer: str = Form(...)
):
    temp_audio_path = f"temp_{audio_file.filename}"
    try:
        with open(temp_audio_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)

        # interpret_question_with_ai now returns text AND audio bytes
        text_answer, audio_bytes = interpret_question_with_ai(
            temp_audio_path,
            riddle,
            riddle_answer
        )

        # Encode audio bytes to Base64 string for JSON transmission
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

        return {"answer": text_answer, "audio": audio_base64}
    except ValueError as ve:
        raise HTTPException(status_code=500, detail=f"Erro de configuração: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {e}")
    finally:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

@app.get("/")
async def read_root():
    return {"message": "API do Jogo de Horror Stories com IA (Áudio) está online!"}