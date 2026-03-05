# Stabilny Python 3.11
FROM python:3.11-slim-bookworm

# Instalacja systemowych pakietów potrzebnych dla pydub/ffmpeg/audioop
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        build-essential \
        libffi-dev \
        libpython3.11 \
        libc6-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Ustawienie katalogu roboczego
WORKDIR /app

# Kopiujemy pliki z pip dependencies
COPY requirements.txt ./

# Instalacja pip packages
RUN pip install --no-cache-dir -r requirements.txt

# Kopiujemy resztę projektu (bez venv)
COPY . .

# Start bota
CMD ["python", "telegram_bot.py"]