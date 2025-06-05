import speech_recognition as sr
from pydub import AudioSegment
import pyttsx3 
import os
import io
import tempfile

PIPER_EXECUTABLE_PATH = os.path.join(os.path.dirname(__file__), 'voices', 'piper.exe')
PIPER_VOICE_MODEL = os.path.join(os.path.dirname(__file__), 'voices', 'pt_BR-faber-medium.onnx')

PIPER_SAMPLE_RATE = 22050

# --- Initial checks for Piper files ---
if not os.path.exists(PIPER_EXECUTABLE_PATH):
    print(f"ERRO: Executável do Piper TTS não encontrado em '{PIPER_EXECUTABLE_PATH}'. Verifique seu caminho.")
if not os.path.exists(PIPER_VOICE_MODEL):
    print(f"ERRO: Modelo de voz do Piper TTS não encontrado em '{PIPER_VOICE_MODEL}'. Verifique seu caminho.")

def convert_audio_to_wav(audio_file_path: str) -> io.BytesIO:
    try:
        audio = AudioSegment.from_file(audio_file_path)
        wav_buffer = io.BytesIO()
        audio.export(wav_buffer, format="wav")
        wav_buffer.seek(0) # Voltar ao início do buffer
        return wav_buffer
    except Exception as e:
        raise Exception(f"Erro ao converter áudio para WAV: {e}. Certifique-se de que ffmpeg está instalado e no PATH.")

def audio_to_text(audio_file_path: str) -> str:
    r = sr.Recognizer()
    question = ""

    if not audio_file_path.lower().endswith('.wav'):
        try:
            wav_buffer = convert_audio_to_wav(audio_file_path)
            audio_source = sr.AudioFile(wav_buffer)
        except Exception as e:
            print(f"Erro na conversão de áudio, tentando abrir diretamente: {e}")
            audio_source = sr.AudioFile(audio_file_path) # Tenta abrir diretamente se a conversão falhar
    else:
        audio_source = sr.AudioFile(audio_file_path)
    
    try:
        with audio_source as source:
            r.adjust_for_ambient_noise(source) # Ajusta para o ruído ambiente
            audio = r.record(source) # Lê o arquivo de áudio inteiro
        text = r.recognize_google(audio, language="pt-BR") # Usando Google Web Speech API
        print(f"Áudio transcrito: {text}")
        return text
    except sr.UnknownValueError:
        print("Speech Recognition não conseguiu entender o áudio.")
        return ""
    except sr.RequestError as e:
        print(f"Erro no serviço de Speech Recognition; {e}")
        return ""
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante a transcrição: {e}")
        return ""
    
def text_to_audio_bytes(text: str) -> bytes:
    engine = pyttsx3.init()

    # --- Verificação e Seleção de Vozes ---
    voices = engine.getProperty('voices')

    # Opcional: Imprimir todas as vozes disponíveis para você escolher no console
    # print("Vozes disponíveis:")
    # for i, voice in enumerate(voices):
    #     print(f"{i}: ID={voice.id}, Nome={voice.name}, Lang={voice.languages}, Gênero={voice.gender}")

    # Tentar encontrar uma voz em Português do Brasil (pt-BR) ou Português (pt)
    selected_voice_id = None
    for voice in voices:
        # Tenta encontrar uma voz em pt-BR primeiro, depois pt
        if "pt-BR" in voice.languages or "pt_BR" in voice.id: # pt_BR-edresson-medium (se for o caso)
             selected_voice_id = voice.id
             break
        elif "pt" in voice.languages: # Ou uma voz portuguesa genérica
            selected_voice_id = voice.id
            # Não break ainda, para tentar achar pt-BR primeiro
    # --- Fim da Seleção de Vozes ---

    # Configurar taxa de fala (opcional)
    # engine.setProperty('rate', 175) # Ex: 175 palavras por minuto (padrão ~200)

    audio_buffer = io.BytesIO()

    # pyttsx3 precisa salvar em um arquivo temporário primeiro, depois lemos os bytes
    # O mesmo truque que usamos para o Piper
    try:
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as fp:
            temp_audio_path = fp.name

        engine.save_to_file(text, temp_audio_path)
        engine.runAndWait() # ESPERA A FALA SER GERADA E SALVA NO ARQUIVO

        if not os.path.exists(temp_audio_path) or os.path.getsize(temp_audio_path) == 0:
            print("ERRO: pyttsx3 não conseguiu criar ou salvar o arquivo de áudio temporário.")
            return b""

        with open(temp_audio_path, "rb") as f:
            audio_bytes = f.read()
        return audio_bytes

    except Exception as e:
        print(f"Erro ao gerar áudio com pyttsx3 (salvando/lendo): {e}")
        return b""
    finally:
        if 'temp_audio_path' in locals() and os.path.exists(temp_audio_path):
            os.remove(temp_audio_path) # Limpa o arquivo temporário