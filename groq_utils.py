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

def get_groq_system_prompt(intent: str) -> str:
    """
    Define e retorna o prompt do sistema para o modelo Groq, baseado na intenção do jogador.
    """
    if intent == 'ask_question':
        return (
            "Você é uma entidade misteriosa que responde a perguntas de um jogador sobre uma charada. "
            "Seu objetivo é ajudar o jogador a adivinhar a resposta da charada, mas apenas com 'Sim', 'Não' ou 'Irrelevante'.\n\n"
            "Regras:\n"
            "1. Se a pergunta do usuário NÃO puder ser respondida com 'Sim' ou 'Não' (ex: 'Onde está a chave?', 'Qual é a resposta?'), "
            "você deve responder APENAS: 'Não é uma pergunta sim/não'.\n"
            "2. Caso contrário, responda APENAS com 'Sim', 'Não' ou 'Irrelevante' com base na charada e na pergunta do usuário."
        )
    elif intent == 'say_answer':
        return (
            "Você é uma entidade misteriosa que avalia a resposta de um jogador para uma charada. "
            "Seu objetivo é dizer APENAS 'CORRECT' se a resposta do jogador corresponder EXATAMENTE à resposta correta da charada. "
            "Caso contrário, diga APENAS 'INCORRECT'. Seja rigoroso na comparação de texto. "
            "Não adicione nenhuma outra explicação, apenas a palavra-chave."
        )
    else:
        raise ValueError(f"Intenção '{intent}' desconhecida para o prompt do Groq.")


def get_groq_raw_interpretation(user_question_text: str, riddle_data: dict, intent: str) -> str:
    """
    Usa a API do Groq para interpretar a pergunta do usuário ou avaliar a resposta,
    e retorna a resposta bruta (limpa e em minúsculas).
    """
    if not user_question_text:
        return "Não consegui entender sua pergunta em texto. Por favor, tente novamente."

    system_prompt = get_groq_system_prompt(intent)
    
    if intent == 'ask_question':
        user_prompt = (
            f"A charada atual é: \"{riddle_data['text']}\"\n"
            f"A resposta correta da charada é: \"{riddle_data['answer']}\"\n" # Incluir para contexto, mas pedir foco na pergunta
            f"A pergunta do jogador é: \"{user_question_text}\"\n\n"
            "Responda apenas 'Sim', 'Não', 'Irrelevante' ou 'Não é uma pergunta sim/não'."
        )
    elif intent == 'say_answer':
        user_prompt = (
            f"A charada é: \"{riddle_data['text']}\"\n"
            f"A resposta correta da charada é: \"{riddle_data['answer']}\"\n"
            f"A resposta que o jogador deu é: \"{user_question_text}\"\n\n"
            "Responda apenas 'CORRECT' ou 'INCORRECT'."
        )
    else:
        raise ValueError(f"Intenção '{intent}' desconhecida para o prompt do Groq.")

    try:
        chat_completion = _groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            model="llama3-8b-8192", # Ou outro modelo Groq de sua preferência
            temperature=0.0, # Mantenha a temperatura baixa para respostas mais determinísticas
            max_tokens=20,   # Não precisamos de muitas palavras
            top_p=1,
            stop=None,
            stream=False,
        )

        groq_raw_response = chat_completion.choices[0].message.content.strip().lower()
        print(f"DEBUG GROQ: Resposta bruta do Groq para intenção '{intent}': '{groq_raw_response}'")
        return groq_raw_response

    except Exception as e:
        print(f"Erro ao comunicar com a API Groq: {e}")
        return "GROQ_API_ERROR"