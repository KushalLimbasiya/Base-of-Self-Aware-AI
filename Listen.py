import speech_recognition as sr 
from speech_recognition import Recognizer
import time
from Logger import setup_logger

logger = setup_logger(__name__, 'jarvis.log')


def Listen():

    r = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        logger.info("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source,0,4)
        r.adjust_for_ambient_noise(source)

    try:
        logger.debug("Recognizing speech...")
        query = r.recognize_google(audio,language="en-in")
        logger.info(f"You Said: {query}")
        query = str(query)
        return query.lower()

    except sr.UnknownValueError:
        logger.warning("Could not understand audio. Please speak clearly.")
        return ""
    
    except sr.RequestError as e:
        logger.error(f"Speech recognition service error: {e}")
        return ""
    
    except Exception as e:
        logger.error(f"Unexpected error in Listen: {e}")
        return ""

