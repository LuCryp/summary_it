import streamlit as st

from sources.local_file import (
    extract_low_quality_audio,
    transcribe_whisper,
    summarize_gpt_mini,
)
from utils.processing import process_url

st.title("Podsumowywarka v0.4")

# Klucz: reset przy zmianie źródła
if "last_source" not in st.session_state:
    st.session_state.last_source = None

source = st.radio("Źródło", ["Plik lokalny", "Link YouTube", "Link TikTok"], horizontal=True)

# Reset session_state przy zmianie źródła
if source != st.session_state.last_source:
    st.session_state.trans_txt = ""
    st.session_state.summary = ""
    st.session_state.last_source = source
    st.rerun()  # wymuś odświeżenie po resecie

# Inicjalizacja tylko raz
if "trans_txt" not in st.session_state:
    st.session_state.trans_txt = ""
if "summary" not in st.session_state:
    st.session_state.summary = ""

# ── Przetwarzanie lokalnego pliku ────────────────────────────────────────────────
if source == "Plik lokalny":
    uploaded = st.file_uploader(
        "Wgraj plik audio lub wideo",
        type=["mp3","wav","m4a","ogg","flac","aac","mp4","mov","avi","mkv","webm"],
        key="local_uploader"  # klucz, żeby nie resetował się przy rerun
    )

    if uploaded and st.button("Przetwórz plik", key="btn_local"):
        st.session_state.trans_txt = ""
        st.session_state.summary = ""

        with st.spinner("Wyodrębnianie audio..."):
            ext = uploaded.name.split('.')[-1]
            audio_io = extract_low_quality_audio(uploaded.getvalue(), ext)
            if not audio_io:
                st.error("Nie udało się wyciągnąć audio")
                st.stop()

        with st.spinner("Transkrypcja (Whisper)..."):
            text = transcribe_whisper(audio_io)
            if text:
                st.session_state.trans_txt = text
                st.success("Transkrypcja gotowa")
            else:
                st.error("Transkrypcja nie powiodła się")
                st.stop()

# ── Przetwarzanie YouTube ────────────────────────────────────────────────────────
elif source == "Link YouTube":
    url = st.text_input("Wklej link YouTube", key="yt_url")

    if url and st.button("Przetwórz", key="btn_yt"):
        with st.spinner("Przetwarzanie..."):
            summary = process_url(url)
            st.session_state.summary = summary

#----------------Tiktok------------

elif source == "Link TikTok":
    url = st.text_input("Wklej link TikTok")

    if url and st.button("Przetwórz", key="btn_tt"):
        with st.spinner("Przetwarzanie..."):
            summary = process_url(url)
            st.session_state.summary = summary


# ── Wspólne streszczenie – TYLKO jeśli jest nowa treść ────────────────────────────────
if st.session_state.trans_txt and not st.session_state.summary:
    with st.spinner("Tworzę streszczenie…"):
        summary = summarize_gpt_mini(st.session_state.trans_txt)
        if summary:
            st.session_state.summary = summary
        else:
            st.error("Nie udało się wygenerować streszczenia")

# Wyświetlenie wyniku
if st.session_state.summary:
    st.markdown("### Streszczenie")
    st.markdown(st.session_state.summary)

    with st.expander("Pełna transkrypcja"):
        st.text(st.session_state.trans_txt[:4000] + " … (skrócone)")

    # Przycisk resetu (opcjonalny)
    if st.button("Wyczyść wyniki"):
        st.session_state.trans_txt = ""
        st.session_state.summary = ""
        st.rerun()