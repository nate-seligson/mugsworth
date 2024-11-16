#!/usr/bin/env python
from google.cloud import texttospeech
import google.generativeai as genai
import os
from datetime import datetime

now = datetime.now()

current_time = now.strftime("%H:%M")

genai.configure(api_key=open("api_key.txt", "r").read())
model = genai.GenerativeModel("gemini-1.5-flash")
def getSpeech():
    response = model.generate_content(f"you are a british talking coaster who can stir drinks. You were created by Nate Seligson at DePaul University. It is currently {current_time}. use this information to guide your response. in around ten-twenty words, give a nice compliment/greeting to the person who just used you to stire their drink. I.e \"have a wonderful sip, my friend\", \"have a nice late night, my good sir! remember to bring a jacket if youre going out! \" ")
    # Instantiate the Text-to-Speech client
    client = texttospeech.TextToSpeechClient()

    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=response.text)

    # Build the voice request with specified language and voice name
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-GB", name="en-GB-Journey-D"
    )

    # Set the audio configuration, including encoding and speaking rate
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
    )

    # Perform the Text-to-Speech request
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    return response.audio_content
