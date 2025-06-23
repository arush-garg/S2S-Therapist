import streamlit as st
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
import os
import atexit
import time
import llm_util
import speech_recognition as sr
from audio_recorder import audio_recorder
from audio_processor import *
from autoplay_audio_component import autoplay_audio_component


RESPONSE_PATH = "response.mp3"
TRANSCRIPT_PATH = "transcript.txt"

#This is a very small subset of the voices offered by ElevenLabs.
VOICES = {
    "Charlie": "IKne3meq5aSn9XLyUdCD",
    "Alice": "Xb7hH8MSUJpSbSDYk0k2",
    "Liam": "TX3LPaxmHKxFdv7VOQHJ"
}

MODEL_NAME = "eleven_flash_v2_5"

SILENCE_DURATION = 500  # milliseconds

def cleanup():
    if os.path.exists(RESPONSE_PATH):
        os.remove(RESPONSE_PATH)

atexit.register(cleanup)

def transcribe_and_respond(audio_data: str):
    """`audio_data`: Base64 from `audio_recorder` (representing audio in .webm format)"""
    try:
        transcription = st.session_state.processor.transcribe(audio_data)
            
        if transcription and transcription != "":
            timestamp = time.strftime("%H:%M:%S")
            st.session_state.transcriptions.append({'timestamp': timestamp, 'text': transcription})
            
            with open(TRANSCRIPT_PATH, "a") as f:
                f.write(f"[{timestamp}] - AGENT: {transcription}\n")
            
            system_reply = llm_util.get_response(transcription)

            with open(TRANSCRIPT_PATH, "a") as f:
                f.write(f"[{timestamp}] - CUSTOMER: {system_reply}\n")

            tts_response = st.session_state.client.text_to_speech.convert(
                voice_id=VOICES.get(st.session_state.selected_voice, 'Charlie'),
                text=system_reply,
                model_id=MODEL_NAME,
            )
            with open(RESPONSE_PATH, "wb") as f:
                for chunk in tts_response:
                    f.write(chunk)
            

            with open(RESPONSE_PATH, "rb") as audio_file:
                autoplay_audio_component(audio_file.read(), audio_format="mp3")
    except sr.UnknownValueError:
        st.warning("Could not understand audio")

# Streamlit UI
if 'client' not in st.session_state:
    cleanup()
    load_dotenv()
    st.session_state.client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
if 'transcriptions' not in st.session_state:
    st.session_state.transcriptions = []
if 'processor' not in st.session_state:
    st.session_state.processor = AudioProcessor()

st.title("Speech-to-Speech Agent Training")

selected_voice = st.selectbox("Select TTS Voice", list(VOICES.keys()), key='voice_selector')
st.session_state.selected_voice = selected_voice

audio_placeholder = st.empty()

result = audio_recorder(
    interval=50,
    threshold=-60,
    silenceTimeout=SILENCE_DURATION,
)

if result:
    if result.get('status') == 'stopped':
        audio_data = result.get('audioData')
        transcribe_and_respond(audio_data)

if st.session_state.transcriptions and len(st.session_state.transcriptions) > 0:
    st.subheader("📝 Conversation History")
    for item in st.session_state.transcriptions:
        st.text(f"[{item['timestamp']}] {item['text']}")

# Reset conversation button
if st.button("🗑️ Clear Conversation History"):
    st.session_state.transcriptions = []
    result = None
    with open(TRANSCRIPT_PATH, "w") as f:
        f.write("")
    st.success("Conversation history cleared!")