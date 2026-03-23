# sources/youtube_link.py
import subprocess
import tempfile
from pathlib import Path
from typing import Optional
from io import BytesIO
import subprocess
import time
import random

from utils.audio_pipeline import normalize_audio

def try_get_youtube_subtitles(url: str) -> Optional[str]:
    """
    Pobiera napisy z YT:
    1. Fast path: pl-orig > pl > en-orig > en (jedno wywołanie)
    2. Fallback: sekwencyjne próby (pl → pl-auto → en → en-auto)

    Zwraca czysty tekst lub None
    """

    def clean_srt(content: str) -> str:
        lines = []
        is_content_line = False

        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            if "-->" in line or line.isdigit():
                is_content_line = False
                continue
            if is_content_line or (line and "-->" not in line):
                lines.append(line)
                is_content_line = True

        return " ".join(lines).strip()

    # 🔥 NOWE: deduplikacja
    def deduplicate_text(text: str) -> str:
        words = text.split()
        result = []

        # 1. usuwa proste powtórzenia słów (AAA)
        for w in words:
            if len(result) >= 3 and result[-1] == w and result[-2] == w:
                continue
            result.append(w)

        # 2. usuwa powtarzające się frazy (sliding window)
        cleaned = []
        seen_phrases = set()
        window = 6  # długość frazy (dobry kompromis)

        i = 0
        while i < len(result):
            phrase = " ".join(result[i:i+window])

            if phrase in seen_phrases:
                i += window  # przeskakujemy duplikat
                continue

            seen_phrases.add(phrase)
            cleaned.append(result[i])
            i += 1

        return " ".join(cleaned)

    def get_priority(p: Path) -> int:
        name = p.stem.lower()

        if "pl-orig" in name:
            return 0
        if ".pl" in name or name.endswith("pl"):
            return 1
        if "en-orig" in name:
            return 2
        if ".en" in name or name.endswith("en"):
            return 3

        return 999

    def run_cmd(cmd, timeout=180):
        try:
            return subprocess.run(
                cmd,
                check=False,
                timeout=timeout,
                capture_output=True,
                text=True
            )
        except subprocess.TimeoutExpired:
            return None

    def anti_block_delay():
        time.sleep(random.uniform(0.8, 2.2))

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            output_template = tmp_path / "subs.%(ext)s"

            # =========================
            # 🔹 VARIANT 1 (FAST)
            # =========================
            cmd = [
                "yt-dlp",
                "--cookies-from-browser", "firefox",
                "--skip-download",
                "--write-sub",
                "--write-auto-sub",
                "--sub-langs", "pl-orig,pl,en-orig,en",
                "--convert-subs", "srt",
                "-o", str(output_template),
                url
            ]

            run_cmd(cmd, timeout=180)

            srt_files = list(tmp_path.glob("*.srt"))

            if srt_files:
                best_srt = min(srt_files, key=get_priority)

                content = best_srt.read_text(encoding="utf-8", errors="replace")
                text = clean_srt(content)
                text = deduplicate_text(text)  # 🔥 TU NOWOŚĆ

                if len(text) > 50:
                    return text

            # 🔻 fallback
            anti_block_delay()

            # =========================
            # 🔹 VARIANT 2+ (FALLBACK)
            # =========================
            attempts = [
                ["--write-sub", "--no-write-auto-sub", "--sub-langs", "pl"],
                ["--write-auto-sub", "--no-write-sub", "--sub-langs", "pl"],
                ["--write-sub", "--no-write-auto-sub", "--sub-langs", "en"],
                ["--write-auto-sub", "--no-write-sub", "--sub-langs", "en"],
            ]

            for flags in attempts:
                anti_block_delay()

                cmd = [
                    "yt-dlp",
                    "--cookies-from-browser", "firefox",
                    "--skip-download",
                    "--convert-subs", "srt",
                    "-o", str(output_template),
                    *flags,
                    url
                ]

                run_cmd(cmd, timeout=120)

                srt_files = list(tmp_path.glob("*.srt"))
                if not srt_files:
                    continue

                latest_srt = max(srt_files, key=lambda p: p.stat().st_mtime)

                content = latest_srt.read_text(encoding="utf-8", errors="replace")
                text = clean_srt(content)
                text = deduplicate_text(text)  # 🔥 TU TEŻ

                if len(text) > 50:
                    return text

            return None

    except Exception as e:
        print(f"napisy YT → {type(e).__name__}: {e}")
        return None

# def try_get_youtube_subtitles(url: str) -> Optional[str]:
#     """
#     Pobiera napisy z YT:
#     1. Fast path: pl-orig > pl > en-orig > en (jedno wywołanie)
#     2. Fallback: sekwencyjne próby (pl → pl-auto → en → en-auto)

#     Zwraca czysty tekst lub None
#     """

#     def clean_srt(content: str) -> str:
#         lines = []
#         is_content_line = False

#         for line in content.splitlines():
#             line = line.strip()
#             if not line:
#                 continue
#             if "-->" in line or line.isdigit():
#                 is_content_line = False
#                 continue
#             if is_content_line or (line and "-->" not in line):
#                 lines.append(line)
#                 is_content_line = True

#         return " ".join(lines).strip()

#     def get_priority(p: Path) -> int:
#         name = p.stem.lower()

#         # dokładniejsze dopasowanie
#         if "pl-orig" in name:
#             return 0
#         if ".pl" in name or name.endswith("pl"):
#             return 1
#         if "en-orig" in name:
#             return 2
#         if ".en" in name or name.endswith("en"):
#             return 3

#         return 999

#     def run_cmd(cmd, timeout=180):
#         try:
#             return subprocess.run(
#                 cmd,
#                 check=False,
#                 timeout=timeout,
#                 capture_output=True,
#                 text=True
#             )
#         except subprocess.TimeoutExpired:
#             return None

#     def anti_block_delay():
#         time.sleep(random.uniform(0.8, 2.2))  # losowy delay

#     try:
#         with tempfile.TemporaryDirectory() as tmp_dir:
#             tmp_path = Path(tmp_dir)
#             output_template = tmp_path / "subs.%(ext)s"

#             # =========================
#             # 🔹 VARIANT 1 (FAST)
#             # =========================
#             cmd = [
#                 "yt-dlp",
#                 "--cookies-from-browser", "firefox",
#                 "--skip-download",
#                 "--write-sub",
#                 "--write-auto-sub",
#                 "--sub-langs", "pl-orig,pl,en-orig,en",
#                 "--convert-subs", "srt",
#                 "-o", str(output_template),
#                 url
#             ]

#             result = run_cmd(cmd, timeout=180)

#             srt_files = list(tmp_path.glob("*.srt"))

#             if srt_files:
#                 best_srt = min(srt_files, key=get_priority)

#                 content = best_srt.read_text(encoding="utf-8", errors="replace")
#                 text = clean_srt(content)
                
#                 #print(text) #sprawdzamy
                
#                 if len(text) > 50:
#                     return text

#             # 🔻 brak → fallback
#             anti_block_delay()

#             # =========================
#             # 🔹 VARIANT 2+ (FALLBACK)
#             # =========================
#             attempts = [
#                 ["--write-sub", "--no-write-auto-sub", "--sub-langs", "pl"],
#                 ["--write-auto-sub", "--no-write-sub", "--sub-langs", "pl"],
#                 ["--write-sub", "--no-write-auto-sub", "--sub-langs", "en"],
#                 ["--write-auto-sub", "--no-write-sub", "--sub-langs", "en"],
#             ]

#             for flags in attempts:
#                 anti_block_delay()

#                 cmd = [
#                     "yt-dlp",
#                     "--cookies-from-browser", "firefox",
#                     "--skip-download",
#                     "--convert-subs", "srt",
#                     "-o", str(output_template),
#                     *flags,
#                     url
#                 ]

#                 run_cmd(cmd, timeout=120)

#                 srt_files = list(tmp_path.glob("*.srt"))
#                 if not srt_files:
#                     continue

#                 # bierzemy najnowszy plik (bo katalog się kumuluje)
#                 latest_srt = max(srt_files, key=lambda p: p.stat().st_mtime)

#                 content = latest_srt.read_text(encoding="utf-8", errors="replace")
#                 text = clean_srt(content)
#                 #print(text) #sprawdzamy
                
#                 if len(text) > 50:
#                     return text

#             return None

#     except Exception as e:
#         print(f"napisy YT → {type(e).__name__}: {e}")
#         return None


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