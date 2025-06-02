import os
from groq_utils import get_groq_raw_interpretation
from utils import audio_to_text, text_to_audio_bytes


def interpret_question_with_ai(
    audio_file_path: str,
    riddle: str,
    riddle_answer: str,
) -> bytes:
    """
    1. Transcreve o áudio para texto.
    2. Envia o texto para a função Groq utilitária para obter a resposta bruta.
    3. Interpreta a resposta bruta do Groq nas categorias 'Sim', 'Não', 'Irrelevante'
       ou 'Não é uma pergunta sim/não' para o jogo.
    """
    user_question_text = audio_to_text(audio_file_path)

    if not user_question_text:
        return "Não consegui entender sua pergunta no áudio. Por favor, tente novamente."

    # Obtém a resposta bruta do Groq
    groq_raw_response = get_groq_raw_interpretation(user_question_text, riddle, riddle_answer)

    final_answer_text: str
    if groq_raw_response == "GROQ_API_ERROR":
        final_answer_text = "Desculpe, a entidade está ocupada no momento. Tente novamente."
    elif "sim" in groq_raw_response:
        final_answer_text = "Sim"
    elif "não é uma pergunta sim/não" in groq_raw_response or "não é uma pergunta de sim ou não" in groq_raw_response:
        final_answer_text = "Não é uma pergunta sim/não"
    elif "não" in groq_raw_response:
        final_answer_text = "Não"
    elif "irrelevante" in groq_raw_response:
        final_answer_text = "Irrelevante"
    else:
        # Caso o modelo dê uma resposta inesperada mesmo após a normalização
        print(f"Atenção: Resposta inesperada do Groq após processamento: '{groq_raw_response}'. Retornando 'Irrelevante'.")
        final_answer_text = "Irrelevante"

    final_answer_audio = text_to_audio_bytes(final_answer_text)

    return final_answer_audio

# Exemplo de uso (para teste local)
"""
if __name__ == "__main__":
    test_audio_path = "caminho/para/seu/audio_pergunta.wav" # Altere para o seu arquivo de teste
    if not os.path.exists(test_audio_path):
        print(f"ERRO: Arquivo de áudio de teste não encontrado em '{test_audio_path}'. Crie um para testar.")
        # exit()

    riddle_example = "Sou leve como uma pena, mas nem o homem mais forte consegue me segurar por muito tempo. O que sou eu?"
    riddle_answer_example = "Respiração"

    print(f"\nTestando com áudio: {test_audio_path}")
    response = interpret_question_with_ai(
        test_audio_path,
        riddle_example,
        riddle_answer_example
    )
    print(f"Resposta final da Entidade: {response}")
"""