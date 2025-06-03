# test_pydub_ffmpeg.py
from pydub import AudioSegment
import os

print("Testando pydub e ffmpeg...")

# Crie um segmento de áudio simples (1 segundo de silêncio)
# Exemplo: 1 segundo (1000 ms) de áudio mono a 44100 Hz.
# Se o Piper estiver gerando em 22050 Hz, use 22050 aqui para simular.
sample_rate = 22050 # Altere para o sample_rate do seu modelo Piper
duration_ms = 1000 # 1 segundo

try:
    # Crie um AudioSegment com dados de áudio 'silenciosos'
    # Isso simula o 'raw_audio_data' que o Piper geraria
    # 16-bit mono = 2 bytes por amostra
    raw_silent_audio = b'\x00\x00' * int(sample_rate * (duration_ms / 1000)) 

    audio_segment = AudioSegment(
        raw_silent_audio,
        frame_rate=sample_rate,
        sample_width=2,
        channels=1
    )
    print(f"AudioSegment criado com sucesso: {audio_segment.duration_seconds} segundos, {audio_segment.frame_rate} Hz")

    output_file = "pydub_test_output.mp3"

    # Tente exportar para MP3
    audio_segment.export(output_file, format="mp3")
    print(f"Áudio exportado com sucesso para {output_file}!")

    # Verifique se o arquivo foi criado e tem tamanho
    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        print("Arquivo MP3 criado e não está vazio. Tente reproduzi-lo.")
    else:
        print("Erro: Arquivo MP3 não criado ou está vazio.")

except Exception as e:
    print(f"OCORREU UM ERRO AO TESTAR PYDUB/FFMPEG: {e}")
    if "No such file or directory" in str(e) or "ffmpeg" in str(e).lower():
        print("Isso geralmente indica que o FFmpeg não está no PATH ou não está funcionando corretamente.")