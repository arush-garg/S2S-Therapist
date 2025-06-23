import streamlit as st
import base64
import uuid

def autoplay_audio_component(audio_bytes, audio_format="mp3"):
    """
    Streamlit component to autoplay audio using a custom <audio> tag and JavaScript.
    Args:
        audio_bytes (bytes): The audio file as bytes.
        audio_format (str): The format of the audio (default: 'mp3').
    """
    if not audio_bytes:
        return
    audio_base64 = base64.b64encode(audio_bytes).decode()
    unique_id = str(uuid.uuid4())
    html = f"""
    <audio id="autoplay-audio-{unique_id}" controls autoplay style="display:block; margin-top: 10px;">
        <source src="data:audio/{audio_format};base64,{audio_base64}#t={unique_id}" type="audio/{audio_format}">
        Your browser does not support the audio element.
    </audio>
    <script>
        var audioElem = document.getElementById('autoplay-audio-{unique_id}');
        if (audioElem) {{
            audioElem.currentTime = 0;
            audioElem.play();
        }}
    </script>
    """
    st.components.v1.html(html, height=70, scrolling=False)