# sources/youtube_link.py
import subprocess, tempfile, re
from pathlib import Path
from typing import Optional
from io import BytesIO
import unicodedata
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from youtube_transcript_api.formatters import TextFormatter

from urllib.parse import urlparse, parse_qs

from utils.audio_pipeline import normalize_audio

def normalize_polish(text: str) -> str:
    """Normalizuj polski tekst prawidłowo"""
    text = unicodedata.normalize('NFKD', text.lower())
    return re.sub(r'[^\w\s]', '', text)


def try_get_youtube_subtitles(url: str) -> Optional[str]:
    """
    Pobiera napisy z YouTube z priorytetem:
    ręczne pl > auto pl > ręczne en > auto en

    Zwraca oczyszczony tekst lub None
    """

    # ========================
    # 🎯 EXTRACT VIDEO ID
    # ========================
    def extract_video_id(url: str) -> Optional[str]:
        parsed = urlparse(url)

        if "youtu.be" in parsed.netloc:
            return parsed.path.strip("/")

        if "youtube.com" in parsed.netloc:
            if parsed.path == "/watch":
                return parse_qs(parsed.query).get("v", [None])[0]
            elif parsed.path.startswith("/shorts/"):
                return parsed.path.split("/")[2]
            elif parsed.path.startswith("/embed/"):
                return parsed.path.split("/")[2]

        return None

    video_id = extract_video_id(url)
    if not video_id:
        return None

    # ========================
    # 🧹 CLEAN + DEDUP
    # ========================
    def clean_and_deduplicate(text: str) -> str:
        if not text:
            return ""

        # usuń [Muzyka], [śmiech] itd.
        text = re.sub(r'\[.*?\]', '', text)

        # normalizacja spacji
        text = re.sub(r'\s+', ' ', text).strip()

        if len(text) < 40:
            return ""

        # podział na zdania
        sentences = re.split(r'(?<=[.!?])\s+', text)

        seen = set()
        unique = []

        for s in sentences:
            s = s.strip()
            if not s:
                continue

            # normalizacja z prawidłową obsługą polskich znaków
            norm = normalize_polish(s)

            if norm not in seen:
                seen.add(norm)
                unique.append(s)

        cleaned = " ".join(unique)

        # usuwanie fillerów (bez niszczenia słów)
        fillers = [
            "no ale", "no to", "proszę państwa", "tak naprawdę",
            "no właśnie", "znaczy", "wie pan", "wie pani",
            "słuchajcie", "dobra", "okej", "no", "yyy", "eee", "hmm"
        ]

        for f in fillers:
            cleaned = re.sub(rf'\b{re.escape(f)}\b', ' ', cleaned, flags=re.IGNORECASE)

        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        return cleaned

    # ========================
    # 📜 FETCH TRANSCRIPT
    # ========================
    try:
        api = YouTubeTranscriptApi()
        fetched_transcript = api.fetch(video_id, languages=['pl', 'en'])

        formatter = TextFormatter()
        text = formatter.format_transcript(fetched_transcript)

        final_text = clean_and_deduplicate(text)

        return final_text if len(final_text) > 40 else None

    except (NoTranscriptFound, TranscriptsDisabled):
        return None
    except Exception as e:
        print(f"[YT subtitles error] {type(e).__name__}: {e}")
        return None

def download_low_quality_audio_youtube(url: str) -> Optional[BytesIO]:
    try:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp) / "audio.%(ext)s"

            cmd = [
                "yt-dlp",
                "-f", "bestaudio[acodec=opus]/bestaudio/best",
                "--no-playlist",
                "-x", "--audio-format", "opus",
                "--audio-quality", "32K",
                "-o", str(tmp_path),
                url
            ]
            subprocess.run(cmd, check=True, timeout=600, capture_output=True)

            files = list(Path(tmp).glob("audio.*"))
            if not files:
                return None

            # Normalizacja przez audio_pipeline
            with open(files[0], "rb") as f:
                opus_bytes = f.read()

            return normalize_audio(opus_bytes, "opus", fmt="ogg")

    except Exception as e:
        print(f"[youtube audio] {e}")
        return None