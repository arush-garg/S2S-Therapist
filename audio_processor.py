import speech_recognition as sr
import io
import base64
import tempfile
from pydub import AudioSegment
import os


class AudioProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
        # Warm up recognize_faster_whisper to load models at instantiation
        silence = AudioSegment.silent(duration=100)
        with io.BytesIO() as buf:
            silence.export(buf, format="webm")
            buf.seek(0)
            silence_webm_bytes = buf.read()
        silence_webm_b64 = base64.b64encode(silence_webm_bytes).decode("utf-8")
        self.transcribe(silence_webm_b64)


    def transcribe(self, audio_data: str):
        """`audio_data`: Base64 from `audio_recorder` (representing audio in .webm format)"""

        audio_bytes = base64.b64decode(audio_data)
        
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as webm_file:
            webm_file.write(audio_bytes)
            webm_path = webm_file.name
        
        audio = AudioSegment.from_file(webm_path, format="webm")
            
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_file:
            audio.export(wav_file.name, format="wav")
            wav_path = wav_file.name
        
        try:
            with sr.AudioFile(wav_path) as source:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_faster_whisper(audio)
                print(text)
                return text
        except sr.UnknownValueError:
            return None
        finally:
            try:
                os.remove(webm_path)
                os.remove(wav_path)
            except:
                pass