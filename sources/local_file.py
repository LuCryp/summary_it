# sources/local_file.py
import os
import tempfile
from io import BytesIO
from typing import Optional
import subprocess

from utils.openai_client import get_openai_client
from utils.audio_pipeline import normalize_audio

def extract_low_quality_audio(file_bytes: bytes, file_ext: str):
    return normalize_audio(file_bytes, file_ext, fmt="ogg")

def transcribe_whisper(audio_data) -> Optional[str]:
    """
    Wysyła audio do Whisper i zwraca transkrypcję.
    """
    if audio_data is None:
        print("[whisper] audio_data is None")
        return None

    # normalizacja do BytesIO
    if isinstance(audio_data, bytes):
        audio_file = BytesIO(audio_data)
    elif isinstance(audio_data, BytesIO):
        audio_file = audio_data
        audio_file.seek(0)
    else:
        print(f"[whisper] Nieprawidłowy typ: {type(audio_data)}")
        return None

    size = audio_file.getbuffer().nbytes
    if size < 100:
        print(f"[whisper] Za mały plik: {size} bajtów")
        return None

    audio_file.name = "audio.ogg"

    try:
        client = get_openai_client()
        result = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1",
            response_format="text",
            language="pl",
            timeout=900,
        )
        text = result.strip()
        #print(f"[whisper] Sukces, długość tekstu: {len(text)} znaków")
        return text
    except Exception as e:
        print(f"[whisper] Błąd: {str(e)}")
        return None


def summarize_gpt_mini(text: str) -> Optional[str]:
    """
    Generuje 5–8-punktowe streszczenie po polsku przez gpt-4o-mini.
    """
    if not text or len(text.strip()) < 50:
        return "Treść zbyt krótka do sensownego podsumowania."

    try:
        client = get_openai_client()

        prompt = f"""Jesteś ekspertem od zwięzłych i konkretnych podsumowań nagrań audio/video.

Podsumuj treść w dokładnie 5–8 punktach bullet list.
- Jeśli któryś punkt naturalnie wymaga rozwinięcia (lista cech, kroki, argumenty), użyj podpunktów (• lub -).
- Maksymalnie jeden poziom podpunktów.
- Zachowuj liczby, daty, nazwy własne, marki, konkretne cytaty w „ ”.
- Każdy główny punkt maksymalnie jedna linijka.
- Nie uogólniaj tam, gdzie precyzja jest ważna.
- Nie dodawaj wstępów ani zakończeń typu "Podsumowując", "Ogólnie" itp.
- Odpowiadaj wyłącznie po polsku.

Treść transkrypcji:
{text[:30000]}"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Tworzysz bardzo konkretne, czytelne podsumowania."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=800,
            timeout=120,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Błąd w summarize_gpt_mini: {str(e)}")
        return None