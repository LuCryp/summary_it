import subprocess
from tempfile import TemporaryDirectory
from pathlib import Path
from typing import Optional
from io import BytesIO

from utils.audio_pipeline import normalize_audio

def download_low_quality_audio_tiktok(url: str) -> Optional[BytesIO]:
    try:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp) / "audio.%(ext)s"

            cmd = [
                "yt-dlp",
                "-f", "bestaudio/best",  # prefer audio
                "--no-playlist",
                "-x", "--audio-format", "opus",  # Opus dla niskiego bitrate
                "--audio-quality", "32K",
                "-o", str(tmp_path),
                url
            ]
            subprocess.run(cmd, check=True, timeout=600, capture_output=True)

            files = list(Path(tmp).glob("audio.*"))
            if not files:
                return None

            with open(files[0], "rb") as f:
                audio_bytes = f.read()

            return normalize_audio(audio_bytes, "opus", fmt="ogg")

    except Exception as e:
        print(f"[tiktok audio] {e}")
        return None