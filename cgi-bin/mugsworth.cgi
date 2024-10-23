#!/usr/bin/env python
from google.cloud import texttospeech
# Instantiates a client
client = texttospeech.TextToSpeechClient()

# Set the text input to be synthesized
synthesis_input = texttospeech.SynthesisInput(text="Ahhhhhh, DePaul University, a fine institution, indeed! ...Though I daresay a bit chilly for this time of year. Do have a sip of your beverage, my friend, and I shall keep your tea nice and warm.")

# Build the voice request, select the language code ("en-US") and the ssml
# voice gender ("neutral")
voice = texttospeech.VoiceSelectionParams(
    language_code="en-GB", name = "en-GB-Standard-D"
)

# Select the type of audio file you want returned
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3,
    speaking_rate = 1.2,
)
# Perform the text-to-speech request on the text input with the selected
# voice parameters and audio file type
response = client.synthesize_speech(
    input=synthesis_input, voice=voice, audio_config=audio_config
)   

print(response.audio_content)