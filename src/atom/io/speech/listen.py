"""Speech recognition module for Atom.

This module handles audio input from the microphone and converts
speech to text using Google's Speech Recognition API.
"""

import speech_recognition as sr 
from speech_recognition import Recognizer
import time
from atom.utils.logger import setup_logger

logger = setup_logger(__name__, 'atom.log')


def Listen():
    """Listen to microphone input and convert speech to text.
    
    Uses Google Speech Recognition to process audio from the default
    microphone. Includes ambient noise adjustment for better accuracy.
    
    Returns:
        str: The recognized text in lowercase, or empty string if:
            - Audio could not be understood
            - Speech recognition service failed
            - Any other error occurred
    
    Example:
        >>> query = Listen()
        >>> print(f"You said: {query}")
        You said: what is the time
    """

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

