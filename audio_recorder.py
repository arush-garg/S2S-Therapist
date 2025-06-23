"""
MIT License

Copyright (c) 2025 Soufiyane AIT MOULAY

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import os
import tempfile
import streamlit.components.v1 as components


def gencomponent(name, template="", script=""):
    def html():
        return f"""
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="UTF-8" />
                    <title>{name}</title>
                    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css" integrity="sha512-Evv84Mr4kqVGRNSgIGL/F/aIDqQb7xQ2vcrdIwxfjThSH8CSR7PBEakCr51Ck+w+/U6swU2Im1vVX0SVk9ABhg==" crossorigin="anonymous" referrerpolicy="no-referrer" />
                    <style>
                        body {{
                            background-color: transparent;
                            margin: 0;
                            padding: 0;
                        }}
                        #toggleBtn {{
                            padding: 10px 20px;
                            border-radius: 4px;
                            border: none;
                            cursor: pointer;
                            color: #282828;
                            font-size: 16px;
                        }}
                        #toggleBtn.recording {{
                            background-color: red;
                        }}
                    </style>
                    <script>
                        function sendMessageToStreamlitClient(type, data) {{
                            const outData = Object.assign({{
                                isStreamlitMessage: true,
                                type: type,
                            }}, data);
                            window.parent.postMessage(outData, "*");
                        }}

                        const Streamlit = {{
                            setComponentReady: function() {{
                                sendMessageToStreamlitClient("streamlit:componentReady", {{apiVersion: 1}});
                            }},
                            setFrameHeight: function(height) {{
                                sendMessageToStreamlitClient("streamlit:setFrameHeight", {{height: height}});
                            }},
                            setComponentValue: function(value) {{
                                sendMessageToStreamlitClient("streamlit:setComponentValue", {{value: value}});
                            }},
                            RENDER_EVENT: "streamlit:render",
                            events: {{
                                addEventListener: function(type, callback) {{
                                    window.addEventListener("message", function(event) {{
                                        if (event.data.type === type) {{
                                            event.detail = event.data
                                            callback(event);
                                        }}
                                    }});
                                }}
                            }}
                        }}
                    </script>
                </head>
                <body>
                    {template}
                </body>
                <script src="https://unpkg.com/hark@1.2.0/hark.bundle.js"></script>
                <script>
                    {script}
                </script>
            </html>
        """

    dir = f"{tempfile.gettempdir()}/{name}"
    if not os.path.isdir(dir): os.mkdir(dir)
    fname = f'{dir}/index.html'
    f = open(fname, 'w')
    f.write(html())
    f.close()
    func = components.declare_component(name, path=str(dir))
    def f(**params):
        component_value = func(**params)
        return component_value
    return f

template = """
    <button id="toggleBtn"><i class="fa-solid fa-microphone fa-lg" ></i></button>
"""

script = """
    let mediaStream = null;
    let mediaRecorder = null;
    let audioChunks = [];
    let allChunks = [];
    let speechEvents = null;
    let silenceTimeout = null;
    let isRecording = false;
    let speechStarted = false;
    let stoppedBySilence = false;
    const toggleBtn = document.getElementById('toggleBtn');
    
    Streamlit.setComponentReady();
    Streamlit.setFrameHeight(60);

    // Full reset when user manually stops recording
    function fullResetRecordingState() {
        audioChunks = [];
        allChunks = [];
        speechStarted = false;
        stoppedBySilence = false;
        if (silenceTimeout) {
            clearTimeout(silenceTimeout);
            silenceTimeout = null;
        }
        if (speechEvents) {
            speechEvents.stop();
            speechEvents = null;
        }
        if (mediaStream) {
            mediaStream.getTracks().forEach(track => track.stop());
            mediaStream = null;
        }
        mediaRecorder = null;
        isRecording = false;
        toggleBtn.classList.remove('recording');
    }
    
    // Partial reset between silence-triggered recordings
    function partialResetRecordingState() {
        audioChunks = [];
        allChunks = [];
        speechStarted = false;
        stoppedBySilence = false;
        if (silenceTimeout) {
            clearTimeout(silenceTimeout);
            silenceTimeout = null;
        }
    }
    
    function blobToBase64(blob) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => {
                const base64String = reader.result.split(',')[1];
                resolve(base64String);
            };
            reader.onerror = reject;
            reader.readAsDataURL(blob);
        });
    }
    
    async function handleRecordingStopped() {
        try {
            if (stoppedBySilence && audioChunks.length > 0) {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                const base64Data = await blobToBase64(audioBlob);
                Streamlit.setComponentValue({
                    audioData: base64Data,
                    status: 'stopped'
                });
                
                // For silence-triggered stops, restart recording without fully resetting
                partialResetRecordingState();
                
                // Create a new media recorder using the existing stream
                if (mediaStream && isRecording) {
                    setupNewRecorder();
                }
            } else {
                // For manual stops, fully reset everything
                fullResetRecordingState();
            }
        } catch (err) {
            console.error('Error processing audio:', err);
            Streamlit.setComponentValue({
                error: 'Failed to process recording'
            });
            fullResetRecordingState();
        }
    }
    
    function setupNewRecorder() {
        if (!mediaStream) return;
        
        mediaRecorder = new MediaRecorder(mediaStream);
        
        mediaRecorder.ondataavailable = event => {
            if (event.data.size > 0) {
                allChunks.push(event.data);
                if (speechStarted) {
                    audioChunks.push(event.data);
                }
            }
        };
        
        mediaRecorder.onstop = () => {
            handleRecordingStopped().catch(err => {
                console.error('Error handling recording:', err);
                Streamlit.setComponentValue({
                    error: 'Failed to process recording'
                });
                fullResetRecordingState();
            });
        };
        
        mediaRecorder.start(100); // Set chunk size to 100ms
        
        // Setup hark speech detection
        if (speechEvents) {
            speechEvents.stop();
        }
        
        speechEvents = hark(mediaStream, {
            interval: window.harkConfig.interval,
            threshold: window.harkConfig.threshold,
            play: window.harkConfig.play
        });
        
        speechEvents.on('speaking', () => {
            if (!speechStarted) {
                speechStarted = true;
                audioChunks = allChunks.slice(0, 5); // Start with first few chunks
            }
            if (silenceTimeout) {
                clearTimeout(silenceTimeout);
                silenceTimeout = null;
            }
        });
        
        speechEvents.on('stopped_speaking', () => {
            silenceTimeout = setTimeout(() => {
                if (mediaRecorder && mediaRecorder.state === 'recording') {
                    stoppedBySilence = true;
                    mediaRecorder.stop();
                }
            }, window.harkConfig.silenceTimeout);
        });
    }
    
    function onRender(event) {
        const args = event.detail.args;
        window.harkConfig = {
            interval: args.interval || 50,
            threshold: args.threshold || -60,
            play: args.play !== undefined ? args.play : false,
            silenceTimeout: args.silenceTimeout || 1500
        };
        
        console.log("Hark configuration:", window.harkConfig);
    }
    
    Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);
    
    toggleBtn.addEventListener('click', async () => {
        if (!isRecording) {
            // Start a new recording session
            partialResetRecordingState();
            
            try {
                mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
                
                // Set up new recorder with this stream
                setupNewRecorder();
                
                isRecording = true;
                toggleBtn.classList.add('recording');
                
            } catch (err) {
                console.error('Error accessing microphone:', err);
                Streamlit.setComponentValue({
                    error: err.message
                });
                fullResetRecordingState();
            }
        } else {
            // Manual stop - don't send audio data
            stoppedBySilence = false; // Explicitly mark as manual stop
            
            if (mediaRecorder && mediaRecorder.state === 'recording') {
                mediaRecorder.stop();
            } else {
                // If recorder is already stopped, manually reset everything
                fullResetRecordingState();
            }
        }
    });
"""

def audio_recorder(interval=50, threshold=-60, play=False, silenceTimeout=1500):
    """
    Create a streamlit component for recording audio with silence detection.
    
    Parameters:
    -----------
    interval: int, optional (default=50)
        How often to check audio level in milliseconds
    threshold: int, optional (default=-60)
        Audio level threshold for speech detection in dB
    play: bool, optional (default=False)
        Whether to play the audio during recording
    silenceTimeout: int, optional (default=1500)
        Time in milliseconds to wait after silence before stopping recording
        
    Returns:
    --------
    dict or None
        A dictionary containing:
        - audioData: base64 encoded audio data (if recording was successful)
        - status: recording status (e.g. 'stopped')
        - error: error message (if an error occurred)
        Returns None if the component has not been interacted with
    """
    component_func = gencomponent('configurable_audio_recorder', template=template, script=script)
    return component_func(interval=interval, threshold=threshold, play=play, silenceTimeout=silenceTimeout)