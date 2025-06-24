import streamlit as st
from elevenlabs.client import ElevenLabs
import os
import atexit
import llm_util
import speech_recognition as sr
from audio_recorder import audio_recorder
from audio_processor import *
from autoplay_audio_component import autoplay_audio_component
from gtts import gTTS
from dotenv import load_dotenv
from groq import Groq


RESPONSE_PATH = "response.mp3"

#This is a very small subset of the voices offered by ElevenLabs.
VOICES = {
    "Charlie": "IKne3meq5aSn9XLyUdCD",
    "Alice": "Xb7hH8MSUJpSbSDYk0k2",
    "Liam": "TX3LPaxmHKxFdv7VOQHJ",
    "Matilda": "XrExE9yKIg1WjnnlVkGX"
}

MODEL_NAME = "eleven_flash_v2_5"

SILENCE_DURATION = 300  # milliseconds


def cleanup():
    if os.path.exists(RESPONSE_PATH):
        os.remove(RESPONSE_PATH)

atexit.register(cleanup)

def transcribe_and_respond(audio_data: str):
    """`audio_data`: Base64 from `audio_recorder` (representing audio in `.webm` format)"""
    try:
        transcription = st.session_state.processor.transcribe(audio_data)
            
        if transcription and transcription != "":
            system_reply = llm_util.get_response(transcription)

            if st.session_state.tts_provider == "ElevenLabs":
                tts_response = st.session_state.client.text_to_speech.convert(
                    voice_id=VOICES.get(st.session_state.selected_voice, 'Charlie'),
                    text=system_reply,
                    model_id=MODEL_NAME,
                )
                with open(RESPONSE_PATH, "wb") as f:
                    for chunk in tts_response:
                        f.write(chunk)
            else:
                tts = gTTS(text=system_reply, lang='en', slow=False)
                tts.save(RESPONSE_PATH)
            

            with open(RESPONSE_PATH, "rb") as audio_file:
                autoplay_audio_component(audio_file.read(), audio_format="mp3")
    except sr.UnknownValueError:
        st.warning("Could not understand audio")


if 'groq_client' not in st.session_state:
    try:
        load_dotenv()
        st.session_state.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    except:
        st.session_state.groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if 'message_history' not in st.session_state:
    st.session_state.message_history = [{"role": "system", "content": llm_util.SYSTEM_PROMPT}]

if 'processor' not in st.session_state:
    st.session_state.processor = AudioProcessor()

# Streamlit UI
st.title("Conversational Therapist")

st.write("Press the microphone button and talk normally. Once you pause, the reply will be spoken aloud. \n When you are done, press the microphone button again to stop recording.")

st.session_state.tts_provider = st.radio(
    "Select TTS Provider",
    ('ElevenLabs', 'Free TTS'),
    key='tts_provider_selector'
)

if st.session_state.tts_provider == "ElevenLabs":
    elevenlabs_api_key = st.text_input("Enter your ElevenLabs API Key:", type="password")
    if elevenlabs_api_key:
        st.session_state.client = ElevenLabs(api_key=elevenlabs_api_key)
        st.session_state.selected_voice = st.selectbox("Select TTS Voice", list(VOICES.keys()), key='voice_selector')
    else:
        st.session_state.selected_voice = None
        if 'client' in st.session_state:
            del st.session_state['client']
else:
    st.session_state.selected_voice = None
    if 'client' in st.session_state:
        del st.session_state['client']


# Disable recorder if ElevenLabs is selected but no API key is provided
if st.session_state.tts_provider == 'ElevenLabs' and 'client' not in st.session_state:
    st.warning("Please enter your ElevenLabs API key to start recording.")
else:
    result = audio_recorder(
        interval=50,
        threshold=-60,
        silenceTimeout=SILENCE_DURATION,
    )

    if result:
        if result.get('status') == 'stopped':
            audio_data = result.get('audioData')
            transcribe_and_respond(audio_data)