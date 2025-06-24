from groq import Groq
import streamlit as st
import os
from dotenv import load_dotenv


LLM = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """
You are a trained therapist who helps people with their problems. 
The user will talk to you, and you should give conversational replies that will be read out to the user.
Note that the user will not see your replies, so you should not use any formatting or markdown.
You should not use any code blocks, and you should not use any special characters. Punctuation is good for adding emotion and you should use it.
"""


def get_response(prompt, t=0.5):
    st.session_state.message_history.append({"role": "user", "content": prompt})
    
    chat_completion = st.session_state.groq_client.chat.completions.create(
        messages=st.session_state.message_history,
        model=LLM,
        stream=False,
        temperature=t,
    )

    response = chat_completion.choices[0].message.content
    st.session_state.message_history.append({"role": "assistant", "content": response})
    return response