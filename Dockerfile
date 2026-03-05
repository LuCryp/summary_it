# Używamy stabilnej wersji Pythona 3.11-slim
FROM python:3.11-slim

# Aktualizacja apt i instalacja pakietów systemowych potrzebnych dla pydub i ffmpeg
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg build-essential libffi-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Ustawienie katalogu roboczego
WORKDIR /app

# Kopiujemy pliki z dependencies
COPY requirements.txt packages.txt ./

# Instalacja pakietów pip
RUN pip install --no-cache-dir -r requirements.txt

# Kopiujemy cały projekt
COPY . .

# Start komendy bota
CMD ["python", "telegram_bot.py"]