# groq_utils.py
import os
from dotenv import load_dotenv
from groq import Groq

# Carrega as variáveis de ambiente ao importar o módulo
load_dotenv()

# --- Instância do Cliente Groq em Nível de Módulo ---
_groq_client = None

def _initialize_groq_client():
    """
    Inicializa o cliente Groq. Esta é uma função auxiliar interna.
    """
    global _groq_client
    if _groq_client is None:
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY não encontrada nas variáveis de ambiente. Verifique seu arquivo .env.")
        _groq_client = Groq(api_key=groq_api_key)

# Chama o inicializador uma vez quando o módulo é carregado
_initialize_groq_client()

# --- Funções para Interações com Groq ---

def get_groq_system_prompt() -> str:
    """
    Define e retorna o prompt do sistema para o modelo Groq.
    """
    return (
        "Você é uma entidade misteriosa que responde a perguntas de um jogador sobre uma charada. "
        "Seu objetivo é ajudar o jogador a adivinhar a resposta da charada, mas apenas com 'Sim', 'Não' ou 'Irrelevante'.\n\n"
        "Regras:\n"
        "1. Se a pergunta do usuário NÃO puder ser respondida com 'Sim' ou 'Não' (ex: 'Onde está a chave?', 'Qual é a resposta?'), "
        "você deve responder APENAS: 'Não é uma pergunta sim/não'.\n"
        "2. Caso contrário, responda APENAS com 'Sim', 'Não' ou 'Irrelevante' com base na charada, na resposta da charada e na pergunta do usuário.\n"
        "3. 'Irrelevante' deve ser usado se a pergunta for sim/não mas não tiver relação direta com a charada ou sua resposta, "
        "ou se a informação não for útil para adivinhar a resposta."
    )

def get_groq_raw_interpretation(user_question_text: str, riddle: str, riddle_answer: str) -> str:
    """
    Usa a API do Groq para interpretar a pergunta do usuário e retorna a resposta bruta (limpa e em minúsculas).
    """
    if not user_question_text:
        return "Não consegui entender sua pergunta em texto. Por favor, tente novamente."

    system_prompt = get_groq_system_prompt()
    user_prompt = (
        f"A charada é: \"{riddle}\"\n"
        f"A resposta correta da charada é: \"{riddle_answer}\"\n"
        f"A pergunta do jogador é: \"{user_question_text}\"\n\n"
        "Responda apenas 'Sim', 'Não', 'Irrelevante' ou 'Não é uma pergunta sim/não'."
    )

    try:
        chat_completion = _groq_client.chat.completions.create( # Usa o cliente de nível de módulo
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            model="llama3-8b-8192", # Ou outro modelo Groq de sua preferência
            temperature=0.0,
            max_tokens=20,
            top_p=1,
            stop=None,
            stream=False,
        )

        groq_raw_response = chat_completion.choices[0].message.content.strip().lower()
        print(f"Resposta bruta do Groq: '{groq_raw_response}'")
        return groq_raw_response # Retorna a resposta bruta para ser interpretada pelo ai_model.py

    except Exception as e:
        print(f"Erro ao comunicar com a API Groq: {e}")
        # Retorna uma string de erro específica que ai_model.py pode reconhecer
        return "GROQ_API_ERROR"