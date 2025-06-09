from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ai_model import interpret_question_with_ai
from riddles import get_riddle_by_id, get_first_riddle_id
import os
import shutil
import base64 # Needed for Base64 encoding
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:3002",
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
    current_riddle_id: int = Form(...), # NOVO: Recebe o ID da charada atual
    player_intent: str = Form(...)      # NOVO: Recebe a intenção ('ask_question' ou 'say_answer')
):
    temp_audio_path = f"temp_{audio_file.filename}"
    try:
        with open(temp_audio_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)

        # interpret_question_with_ai agora retorna um dicionário
        result = interpret_question_with_ai(
            temp_audio_path,
            current_riddle_id,
            player_intent
        )

        # Codifica o áudio para Base64 apenas se houver áudio e não for vazio
        audio_base64 = base64.b64encode(result["audio_base64"]).decode('utf-8') if result.get("audio_base64") else ""

        # Retorna a resposta estruturada para o frontend
        return {
            "status": result["status"],
            "type": result.get("type"), # 'question_response', 'answer_evaluation', 'game_complete'
            "message": result["message"],
            "audio": audio_base64,
            "current_riddle_id": current_riddle_id,
            "correct": result.get("correct"), # Apenas para 'answer_evaluation'
            "next_riddle_text": result.get("next_riddle_text"), # Apenas se correto e houver próxima charada
            "current_riddle_text": result.get("current_riddle_text")
        }

    except ValueError as ve:
        raise HTTPException(status_code=500, detail=f"Erro de configuração: {ve}")
    except Exception as e:
        import traceback
        traceback.print_exc() # Imprime o traceback completo no terminal do FastAPI
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {e}")
    finally:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

@app.get("/get_initial_riddle")
async def get_initial_riddle():
    first_riddle_id = get_first_riddle_id()
    if not first_riddle_id:
        raise HTTPException(status_code=404, detail="Nenhuma charada encontrada.")
    riddle = get_riddle_by_id(first_riddle_id)
    return {"riddle_id": riddle['id'], "riddle_text": riddle['text']}

@app.get("/")
async def read_root():
    return {"message": "API do Jogo de Horror Stories com IA está online!"}