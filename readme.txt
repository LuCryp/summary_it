summary_it – Transkrypcja, Podsumowanie i Audio z YouTube / TikTok / Pliku
=========================================================================

Telegram Bot + Streamlit app do pobierania audio z YouTube / TikToka, 
transkrypcji (Whisper), podsumowywania / analizy / odpowiedzi na pytania 
(GPT-4o-mini) oraz wysyłania wyników jako voice note, audio file lub tekst.

Dwie wersje:
- Telegram Bot     – szybki, mobilny dostęp (główny fokus)
- Streamlit Web App – interfejs przeglądarkowy do testów / dłuższych materiałów

FUNKCJONALNOŚCI
---------------

Podstawowe funkcje:
* Pobieranie audio z YouTube (link)
* Pobieranie audio z TikToka (link)
* Przesyłanie własnego pliku (głosówka, mp3, m4a, wav, webm, mp4 itp.)
* Automatyczna transkrypcja audio → tekst (OpenAI Whisper)
* Generowanie podsumowania / kluczowych punktów / odpowiedzi na pytania (GPT-4o-mini)
* Wysyłanie wyników:
  - voice note (z waveform – idealne do szybkiego odsłuchu)
  - audio file (mp3 / ogg)
  - wiadomość tekstowa (transkrypcja + podsumowanie)
* Pełna obsługa błędów + komunikaty po polsku

Zaawansowane opcje:
* Automatyczne cięcie długich materiałów (> limit Telegram ~50 MB voice / ~20 MB plik)
* Opcjonalne ograniczenie długości (np. tylko pierwsze 10–15 min)
* Cache wyników (ten sam link → szybsza odpowiedź z cache)
* Tryb Q&A – po transkrypcji możesz pytać o konkretne fragmenty
* Obsługa wielu języków (Whisper + GPT radzą sobie z PL/EN/DE itd.)

Sposób użycia:
Telegram: wklej link YT/TikTok lub prześlij plik → bot przetwarza i odsyła
Streamlit: uruchom lokalnie → wrzuć plik / link → przeglądaj transkrypcję + podsumowanie

WYMAGANIA
---------
- Python 3.11+
- Klucz API OpenAI (Whisper + GPT-4o-mini)
- Token bota Telegram (od @BotFather)
- ffmpeg (systemowo – apt install ffmpeg / brew install ffmpeg)
- Pakiety z requirements.txt

INSTALACJA LOKALNA
------------------
1. Sklonuj repozytorium
   git clone https://github.com/LuCryp/summary_it.git
   cd summary_it

2. Wirtualne środowisko (zalecane)
   python -m venv .venv
   source .venv/bin/activate          (Linux/Mac)
   .venv\Scripts\activate             (Windows)

3. Zainstaluj zależności
   pip install -r requirements.txt

4. Skonfiguruj klucze – utwórz plik .env
   TELEGRAM_BOT_TOKEN=123456:ABC-DEFxxxxxxxxxxxxxxxxxxxxxxxxxxx
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TELEGRAM_USER_IDS=123456789,987654321   (opcjonalnie – tylko wybrani użytkownicy)

URUCHOMIENIE
------------
Telegram Bot (główny tryb):
   python telegram_bot.py
   (bot nasłuchuje wiadomości – tryb polling)

Streamlit Web App (do testów / dłuższych plików):
   streamlit run app_main.py
   (otworzy się w przeglądarce: http://localhost:8501)

Na serwerze (Railway / Render / VPS):
1. Wrzuć na GitHub
2. Nowy serwis z repo
3. Zmienne środowiskowe:
   TELEGRAM_BOT_TOKEN
   OPENAI_API_KEY
   TELEGRAM_USER_IDS (opcjonalnie)
4. Build: pip install -r requirements.txt
5. Start: python telegram_bot.py
   (lub użyj gotowego Dockerfile – już jest w repo)

KOSZTY UŻYCIA (orientacyjnie – marzec 2026)
-------------------------------------------
Operacja              Model          Cena przybliżona                     Przykład (10 min audio)
-----------------------------------------------------------------------------------------------
Transkrypcja          Whisper        $0.006 / min                         ~$0.06
Podsumowanie / Q&A    GPT-4o-mini    $0.15 / 1M input + $0.60 / 1M output ~$0.005 – $0.03
Pobieranie YT/TikTok  yt-dlp         0 zł                                 darmowe
Całość (typowy film 10 min)         Whisper + GPT   ~0.07 – 0.10 zł

Najdroższy element: długie transkrypcje Whisper.
Rekomendacja: dodaj limit długości (np. max 30 min) + ostrzeżenie o koszcie.

STRUKTURA PROJEKTU
------------------
summary_it/
├── telegram_bot.py          Główny handler Telegrama
├── app_main.py              Główny plik Streamlit
├── utils/
│   ├── processing.py        Główna logika przetwarzania
│   ├── openai_client.py     Klient OpenAI + cache
│   └── audio_pipeline.py    Przetwarzanie audio (resampling, cięcie)
├── sources/
│   ├── youtube_link.py      Pobieranie YT
│   ├── tiktok.py            Pobieranie TikTok
│   └── local_file.py        Obsługa przesłanych plików
├── requirements.txt
├── .env.example
├── Dockerfile
├── .gitignore
└── README.txt               (ten plik)

TECHNOLOGIE
-----------
- pyTelegramBotAPI     → Telegram
- Streamlit            → webowy interfejs
- yt-dlp               → YouTube / TikTok
- pydub + ffmpeg       → audio processing
- OpenAI API           → Whisper (transkrypcja) + GPT-4o-mini (podsumowanie / Q&A)
- python-dotenv        → secrets

WAŻNE UWAGI
-----------
- Pliki przetwarzane tymczasowo – nic nie zapisuje na stałe
- Długie filmy (>15–20 min) mogą przekroczyć limit Telegram
- Masowe pobieranie chronionych treści → zabronione (prawa autorskie!)
- Monitoruj koszty OpenAI: https://platform.openai.com/usage
- yt-dlp → czasem blokada IP → proxy/VPN pomaga

LICENCJA
--------
MIT

AUTOR
-----
LuCryp / ŁukaszK
https://github.com/LuCryp
Zgłaszaj błędy i pomysły w Issues