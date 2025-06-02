from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment
import io

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
    
def text_to_audio_bytes(text: str, lang: str = 'pt') -> bytes:
    """
    Converts text to speech audio bytes (MP3 format) using gTTS.
    """
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer.getvalue() # Get bytes from the buffer
    except Exception as e:
        print(f"Erro ao gerar áudio de texto: {e}")
        return b"" # Return empty bytes on error
