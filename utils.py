import speech_recognition as sr
from pydub import AudioSegment
import io
import os
import subprocess 
import tempfile   
import uuid 

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
    """
    Converts text to speech audio bytes using Piper TTS (offline).
    Calls the Piper executable via subprocess.
    """
    if not os.path.exists(PIPER_EXECUTABLE_PATH) or not os.path.exists(PIPER_VOICE_MODEL):
        print("Piper TTS não configurado corretamente. Não é possível gerar áudio.")
        return b""

    try:
        # Command to run Piper. Piper reads text from stdin and outputs raw audio to stdout.
        # We specify --output-raw to get PCM data, then specify sample rate and format
        # to pydub.
        command = [
            PIPER_EXECUTABLE_PATH,
            '--model', PIPER_VOICE_MODEL,
            '--output-raw'
        ]

        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Send text to Piper's stdin and read raw audio from its stdout
        raw_audio_data, stderr_output = process.communicate(input=text.encode('utf-8'))

        if process.returncode != 0:
            print(f"Erro ao executar Piper: {stderr_output.decode('utf-8')}")
            return b""

        # Piper outputs 16-bit mono PCM at the voice's sample rate (PIPER_SAMPLE_RATE).
        audio_segment = AudioSegment(
            raw_audio_data,
            frame_rate=PIPER_SAMPLE_RATE,
            sample_width=2, # 16-bit audio is 2 bytes per sample
            channels=1      # Mono
        )

        audio_buffer = io.BytesIO()
        audio_segment.export(audio_buffer, format="mp3") # Export as MP3
        audio_buffer.seek(0)
        return audio_buffer.getvalue()

    except FileNotFoundError:
        print(f"Erro: Piper executável não encontrado em '{PIPER_EXECUTABLE_PATH}'. Verifique o caminho.")
        return b""
    except Exception as e:
        print(f"Erro ao gerar áudio de texto com Piper: {e}")
        return b""
