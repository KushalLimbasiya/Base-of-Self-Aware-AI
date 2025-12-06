"""Text-to-speech module for Atom.

Handles converting text to speech and speaking to the user.
Now includes interrupt capability to stop speaking mid-sentence.
"""

import pyttsx3
import threading
from atom.utils.logger import setup_logger
from atom.core.config import get_config

logger = setup_logger(__name__, 'atom.log')
config = get_config()

# Global variables for interrupt control
is_speaking = False
should_stop = False
speech_lock = threading.Lock()

def Init():
    """Initialize the text-to-speech engine.
    
    Returns:
        pyttsx3.Engine: Initialized TTS engine
    """
    try:
        engine = pyttsx3.init('sapi5')
        voices = engine.getProperty('voices')
        
        # Get voice settings from config
        voice_index = config.get('bot.voice_index', 0)
        voice_rate = config.get('bot.voice_rate', 170)
        
        engine.setProperty('voice', voices[voice_index].id)
        engine.setProperty('rate', voice_rate)
        logger.debug("TTS engine initialized successfully")
        return engine
    except Exception as e:
        logger.error(f"Error initializing TTS engine: {e}")
        raise

# Initialize the global engine
engine = Init()

def Say(text):
    """Speak the given text using text-to-speech.
    
    This function can be interrupted by calling StopSpeaking() or pressing 'q'.
    
    Args:
        text: The text to speak
        
    Note:
        Uses pyttsx3 with SAPI5 voice engine
    """
    global is_speaking, should_stop
    
    bot_name = config.get('bot.name', 'Atom')
    
    with speech_lock:
        should_stop = False
        is_speaking = True
    
    try:
        logger.info(f"Speaking: {text[:50]}...")
        print("    ")
        print(f"{bot_name}: {text}")
        
        # Split text into sentences for better interruptibility
        sentences = text.replace('! ', '!|').replace('? ', '?|').replace('. ', '.|').split('|')
        
        for sentence in sentences:
            # Check if we should stop
            with speech_lock:
                if should_stop:
                    logger.info("Speech interrupted by user")
                    engine.stop()
                    break
            
            if sentence.strip():
                engine.say(sentence)
                engine.runAndWait()
        
        print("    ")
        
    except RuntimeError as e:
        if "run loop already started" in str(e):
            # Handle the specific error
            logger.warning("TTS run loop conflict, attempting recovery...")
            try:
                engine.stop()
            except:
                pass
        else:
            logger.error(f"Runtime error in TTS: {e}")
    except Exception as e:
        logger.error(f"Error in text-to-speech: {e}", exc_info=True)
    finally:
        with speech_lock:
            is_speaking = False
            should_stop = False

def StopSpeaking():
    """Interrupt and stop the current speech.
    
    This can be called from another thread to stop Atom from speaking.
    Can be triggered by pressing 'q' key.
    """
    global should_stop
    
    with speech_lock:
        if is_speaking:
            should_stop = True
            try:
                engine.stop()
                logger.info("Speech stopped by user request")
            except Exception as e:
                logger.error(f"Error stopping speech: {e}")
        else:
            logger.debug("No active speech to stop")

def IsSpeaking():
    """Check if Atom is currently speaking.
    
    Returns:
        bool: True if currently speaking, False otherwise
    """
    with speech_lock:
        return is_speaking

# Async version for future use
def SayAsync(text):
    """Speak text asynchronously in a separate thread.
    
    Args:
        text: The text to speak
        
    Returns:
        threading.Thread: The thread object
    """
    thread = threading.Thread(target=Say, args=(text,))
    thread.daemon = True
    thread.start()
    return thread
