# sources/youtube_link.py
import subprocess
import tempfile
from pathlib import Path
from typing import Optional
from io import BytesIO

from pydub import AudioSegment

from utils.audio_pipeline import normalize_audio


def try_get_youtube_subtitles(url: str) -> Optional[str]:
    try:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)

            # Najpierw pobierz napisy (ręczne + auto)
            cmd = [
                "yt-dlp",
                "--cookies-from-browser", "firefox",  # lub "edge" / "firefox"
                "--skip-download",
                "--write-sub", "--write-auto-sub",
                "--sub-langs", "pl",
                "--convert-subs", "srt",
                "-o", str(tmp_path / "subs.%(ext)s"),
                url]
            # result = subprocess.run(cmd, check=False, timeout=120, capture_output=True, text=True)

            # print("yt-dlp exit code:", result.returncode)
            # print("stdout:", result.stdout)
            # print("stderr:", result.stderr)

            # if result.returncode != 0:
            #     return None
            subprocess.run(cmd, check=True, timeout=120, capture_output=True)

            srt_files = list(tmp_path.glob("*.srt"))
            if not srt_files:
                return None

            # Wybierz najlepszy plik (priorytet pl > en > auto)
            srt_path = min(srt_files, key=lambda p: 0 if 'pl' in p.name else 1 if 'en' in p.name else 2)

            with open(srt_path, encoding="utf-8", errors="replace") as f:
                content = f.read()

            # Usuwanie timestampów i numerów
            lines = []
            skip = False
            for line in content.splitlines():
                if "-->" in line or line.strip().isdigit():
                    skip = True
                    continue
                if skip and not line.strip():
                    skip = False
                    continue
                if not skip and line.strip():
                    lines.append(line.strip())

            text = " ".join(lines).strip()
            return text if len(text) > 80 else None

    except Exception as e:
        print(f"napisy YT → {e}")
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