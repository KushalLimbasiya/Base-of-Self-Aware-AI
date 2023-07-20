import speech_recognition as sr 
from speech_recognition import Recognizer
import time


def Listen():

    r = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source,0,4)
        r.adjust_for_ambient_noise(source)

    try:
        print("Recognizing..")
        query = r.recognize_google(audio,language="en-in")
        print(f"You Said : {query}")

    except:
        return ""

    query = str(query)
    return query.lower()

