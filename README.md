# Speech-to-Speech Therapist

The purpose of this tool is to democratize access to personalized mental health resources. The main difference between this implementation and a chatbot is the conversational aspect. Some people find it difficult to type their feelings, hence a speech-based AI therapist may provide significantly more comfort.

### Set up

1. Create a `.env` file and add your `GROQ_API_KEY`

2. Install dependencies using `pip install -r requirements.txt`
3. Install `ffmpeg` if not already installed. You can use `brew install ffmpeg` on macOS or download it from the [FFmpeg website](https://ffmpeg.org/download.html) for other platforms.

### Running the App

Run `streamlit run app.py` and the page should open in the browser. You might be prompted to give microphone permissions.

<i>I strongly recommend using headphones. The microphone sometimes picks up the text-to-speech as user input</i>

### Choosing the TTS Model

There are two options for the Text-to-Speech service used by the application.

|ElevenLabs|GTTS|
|---|---|
|Better quality and more human-like audio|Sounds little robotic and makes some mistakes with emphasis|
|User needs to provide an [API key](https://elevenlabs.io/app/settings/api-keys) (since the service is quite expensive)|Free|
|Extensive collection of voices to choose from|No choice of language|