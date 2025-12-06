"""Edge TTS - High-quality text-to-speech using Microsoft Edge voices.

Provides natural-sounding voices via Microsoft's Edge TTS service.
Supports barge-in (interrupt while speaking).
Falls back to pyttsx3 if Edge TTS fails.
"""

import asyncio
import tempfile
import threading
import edge_tts
from atom.utils.logger import setup_logger

logger = setup_logger(__name__, 'atom.log')

# Default voice
DEFAULT_VOICE = "en-US-AriaNeural"

# Available voices
VOICES = {
    "aria": "en-US-AriaNeural",      # US Female (friendly)
    "guy": "en-US-GuyNeural",        # US Male (casual)
    "sonia": "en-GB-SoniaNeural",    # UK Female
    "ryan": "en-GB-RyanNeural",      # UK Male
    "neerja": "en-IN-NeerjaNeural",  # Indian English Female
    "prabhat": "en-IN-PrabhatNeural" # Indian English Male
}

# Global state for speech control
_is_speaking = False
_stop_speaking = False
_speech_thread = None


def is_speaking() -> bool:
    """Check if currently speaking."""
    return _is_speaking


def stop_speaking():
    """Stop current speech."""
    global _stop_speaking
    _stop_speaking = True
    try:
        import pygame
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
    except:
        pass
    logger.info("Speech stopped by user")


async def _edge_speak_async(text: str, voice: str = DEFAULT_VOICE) -> str:
    """Generate speech using Edge TTS (async)."""
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        temp_path = f.name
    
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(temp_path)
    
    return temp_path


def _play_audio_thread(audio_path: str):
    """Play audio in a thread (allows interruption)."""
    global _is_speaking, _stop_speaking
    _is_speaking = True
    _stop_speaking = False
    
    try:
        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy() and not _stop_speaking:
            pygame.time.Clock().tick(10)
        
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        
    except ImportError:
        import soundfile as sf
        import sounddevice as sd
        data, samplerate = sf.read(audio_path)
        sd.play(data, samplerate)
        while sd.get_stream().active and not _stop_speaking:
            sd.sleep(100)
        sd.stop()
    
    finally:
        _is_speaking = False
        import os
        try:
            os.unlink(audio_path)
        except:
            pass


def edge_speak(text: str, voice: str = DEFAULT_VOICE, blocking: bool = True) -> None:
    """Speak text using Edge TTS.
    
    Args:
        text: Text to speak
        voice: Voice name (use VOICES dict or full name)
        blocking: If False, return immediately (non-blocking)
    """
    global _speech_thread
    
    try:
        if voice.lower() in VOICES:
            voice = VOICES[voice.lower()]
        
        logger.info(f"Edge TTS speaking: {text[:50]}...")
        
        # Generate audio
        audio_path = asyncio.run(_edge_speak_async(text, voice))
        
        if blocking:
            _play_audio_thread(audio_path)
        else:
            # Non-blocking: play in thread
            _speech_thread = threading.Thread(target=_play_audio_thread, args=(audio_path,))
            _speech_thread.daemon = True
            _speech_thread.start()
        
        logger.info("Edge TTS complete")
        
    except Exception as e:
        logger.error(f"Edge TTS error: {e}")
        logger.info("Falling back to pyttsx3")
        from atom.io.speech.speak import Say as OldSay
        OldSay(text)


def list_voices():
    """List available Edge TTS voices."""
    print("Available voices:")
    for name, voice_id in VOICES.items():
        print(f"  {name}: {voice_id}")


if __name__ == "__main__":
    import time
    print("Edge TTS Demo with Barge-in")
    print("=" * 50)
    
    print("\nTesting non-blocking speech (you can interrupt)...")
    edge_speak("Hello! I am Atom. This is a test of the barge-in feature. You can press Q to stop me at any time.", "aria", blocking=False)
    
    print("Speaking... (press Enter to stop)")
    input()
    stop_speaking()
    print("Done!")

