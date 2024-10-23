from gtts import gTTS
import os
def text_to_speech(text):

    res = gTTS(text=text, lang='en', tld='com.uy')

    filename = "output.mp3"

    res.save(filename)

    os.system(f"start {filename}")
if __name__ == "__main__":
    text = "Hello, I am GeeksforGeeks and I made a Speech Synthesis System With Python."
    text_to_speech(text)