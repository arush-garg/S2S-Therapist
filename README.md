# Speech-to-Speech Therapist

This tool aims to democratize access to personalized mental health resources. Unlike traditional chatbots, this application focuses on a conversational, speech-based experience. For many, speaking is more comfortable than typing, making a speech-driven AI therapist more accessible and comforting.

### Setup

1. Create a `.env` file and add your `GROQ_API_KEY`.
2. Install dependencies: `pip install -r requirements.txt`
3. Ensure `ffmpeg` is installed. On macOS, use `brew install ffmpeg`. For other platforms, download it from the [FFmpeg website](https://ffmpeg.org/download.html).

### Running the App

Start the app with:

```
streamlit run app.py
```

The app should open in your browser. You may be prompted to grant microphone permissions.

You can also try the app online [here](https://s2s-therapist.streamlit.app/) (you might need to reload the page if Streamlit gives an error).

*Tip: For best results, use headphones. The microphone may pick up the text-to-speech output as user input.*

### Choosing the TTS Model

There are two Text-to-Speech (TTS) options available:

| ElevenLabs | GTTS |
|---|---|
| High-quality, human-like audio | Slightly robotic, may misplace emphasis |
| Requires an [API key](https://elevenlabs.io/app/settings/api-keys) (service is paid) | Free |
| Wide selection of voices | No voice selection |
