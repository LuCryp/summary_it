# utils/openai_client.py
import os
from functools import lru_cache

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)  # wykonuje się przy imporcie modułu

@lru_cache(maxsize=1)
def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "Brak OPENAI_API_KEY\n\n"
            "Rozwiązania:\n"
            "  • plik .env w katalogu głównym: OPENAI_API_KEY=sk-...\n"
            "  • zmienna środowiskowa OPENAI_API_KEY\n"
            "  • Streamlit Cloud → Settings → Secrets"
        )

    return OpenAI(
        api_key=api_key,
        timeout=120.0,          # dłuższy timeout na Whisper i duże pliki
        max_retries=2,
    )