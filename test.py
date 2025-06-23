from autoplay_audio_component import autoplay_audio_component
import streamlit as st


with open("response.mp3", "rb") as f:
    audio_bytes = f.read()

if st.button("Play Audio"):
    autoplay_audio_component(audio_bytes, audio_format="mp3")