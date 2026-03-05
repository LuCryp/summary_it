# utils/audio_pipeline.py
from io import BytesIO
from typing import Optional
import subprocess
import tempfile
import os

def normalize_audio(file_bytes: bytes, file_ext: str, fmt: str = "ogg") -> Optional[BytesIO]:
    file_ext = file_ext.lower().lstrip('.')

    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp_in:
        tmp_in.write(file_bytes)
        input_path = tmp_in.name

    output_path = input_path + f"_conv.{fmt}"

    try:
        command = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-vn",
            "-ac", "1",
            "-ar", "16000",
            "-c:a", "libopus" if fmt == "ogg" else "pcm_s16le",
            "-b:a", "24k" if fmt == "ogg" else None,
            output_path
        ]
        # usuń None z listy jeśli bitrate niepotrzebny
        command = [arg for arg in command if arg is not None]

        result = subprocess.run(command, check=True, capture_output=True, text=True)

        with open(output_path, "rb") as f:
            audio_bytes = f.read()

        bio = BytesIO(audio_bytes)
        bio.name = f"audio.{fmt}"
        bio.seek(0)
        return bio

    except subprocess.CalledProcessError as e:
        print(f"[audio_pipeline] ffmpeg error: {e.stderr}")
        return None

    except Exception as e:
        print(f"[audio_pipeline] inny błąd: {str(e)}")
        return None

    finally:
        for p in [input_path, output_path]:
            try:
                os.unlink(p)
            except:
                pass