from sources.youtube_link import (
    try_get_youtube_subtitles,
    download_low_quality_audio_youtube,
)
from sources.tiktok_link import download_low_quality_audio_tiktok
from sources.local_file import (
    transcribe_whisper,
    summarize_gpt_mini,)


def process_url(url: str) -> str:

    #  YOUTUBE
    if "youtube.com" in url or "youtu.be" in url:
        text = try_get_youtube_subtitles(url)

        if not text:
            audio_io = download_low_quality_audio_youtube(url)
            if not audio_io:
                return "Nie udało się pobrać audio"

            text = transcribe_whisper(audio_io)
            if not text:
                return "Transkrypcja nie powiodła się"

    #  TIKTOK
    elif "tiktok.com" in url:
        audio_io = download_low_quality_audio_tiktok(url)
        if not audio_io:
            return "Nie udało się pobrać audio"

        text = transcribe_whisper(audio_io)
        if not text:
            return "Transkrypcja nie powiodła się"

    else:
        return "Nieobsługiwany link"

    summary = summarize_gpt_mini(text)
    return summary or "Błąd streszczenia"