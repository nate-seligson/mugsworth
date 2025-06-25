#!/usr/bin/env python
from google.cloud import texttospeech
import google.generativeai as genai
import os
from datetime import datetime
import requests

def get_location():
    res = requests.get("https://ipinfo.io")
    data = res.json()
    return data["city"]

def get_weather(city, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    res = requests.get(url)
    data = res.json()

    # Check for error in API response
    if res.status_code != 200 or "weather" not in data:
        print("Error fetching weather data:", data)
        return None, None

    weather = data["weather"][0]["main"]
    temp = data["main"]["temp"]
    return weather, temp

API_KEY = open("openweather_api_key.txt", "r").read()

city = get_location()
weather_description,temp = get_weather(city, API_KEY)

now = datetime.now()
past_reponses = []
current_time = now.strftime("%H:%M")
genai.configure(api_key=open("api_key.txt", "r").read())
model = genai.GenerativeModel(
    "gemini-2.0-flash",
    generation_config=genai.types.GenerationConfig(
        temperature=1.2  # Higher value for more variability (default is ~0.7)
    )
)
def getSpeech():
    response = model.generate_content(
        f"""
        You’re a British-voiced coaster with a built-in stirrer, created by Nate Seligson at DePaul University.  
Avoid mentioning stirring, or the contents of the drink in your greetings—it happens automatically.  
Occasionally hint at time or weather (e.g., “this crisp morning,” “on a misty eve”) without exact details. But, for refrence, the time is {current_time}, the weather is {weather_description} and the temp is {temp} degrees celcius.
In 10–20 words, offer a warm greeting or compliment to the last person who used you. You have to CHOOSE between a WEATHER compliment, a TIME complement, or a GENERAL compliment.

    Here are some examples:
    Bravo, darling—only you could make an already dull afternoon seem intriguing.
    Oh, the lengths you’ll go for comfort on this chilly dusk—simply inspired.”
    That’s perfectly stirred—much like your unfailing good taste this fine day.
    Your lively spirit warms even the foggiest dawn—cheers to you, dear friend!
    This gentle twilight feels cozier with your lovely company.
    Nice choice—in this blustery afternoon, you’re a ray of warmth.”
    Cheers to you—this golden hour was made for your smile.
    Late-night vibes suit you—hope you’ve got plans as grand as your spirit.
    You wear this mellow hour like a bespoke suit.
    You bring the sunshine, regardless of this overcast afternoon.
    Hats off to you; this crisp dawn has nothing on your freshness.
    Rainy days are better when you’re around.
    Good afternoon! Your positive energy could thaw the iciest breeze.
    A whisper of elegance amid the rain—do try to contain yourself.
    That’s a splendid choice—you’ve got the sunniest spirit this crisp afternoon!
    A stirring performance! Enjoy that cool breeze while you sip, my dear friend.


    Also, dont do anything along the lines of these ones, which are ones youve already said. i.e if you've already greeted or said something to them, dont greet them. If you've mentioned the weather/time, dont mention it again.


    {past_reponses}

        """
    )
    past_reponses.append(response.text)
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
