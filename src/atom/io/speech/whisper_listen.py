"""Whisper-based speech recognition for Atom AI.

Uses OpenAI's Whisper model for high-quality local speech recognition.
Falls back to SpeechRecognition if Whisper fails.
"""

import tempfile
import sounddevice as sd
import soundfile as sf
import numpy as np
from atom.utils.logger import setup_logger

logger = setup_logger(__name__, 'atom.log')

# Whisper model (loaded on first use)
_whisper_model = None

def get_whisper_model(model_size: str = "base"):
    """Load Whisper model (cached).
    
    Automatically uses GPU (CUDA) if available for faster inference.
    """
    global _whisper_model
    if _whisper_model is None:
        try:
            import whisper
            import torch
            
            # Check for GPU
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Loading Whisper model: {model_size} on {device.upper()}")
            
            _whisper_model = whisper.load_model(model_size, device=device)
            logger.info(f"Whisper model loaded successfully on {device.upper()}")
        except Exception as e:
            logger.error(f"Failed to load Whisper: {e}")
            raise
    return _whisper_model


def record_audio(duration: float = 5.0, sample_rate: int = 16000) -> np.ndarray:
    """Record audio from microphone.
    
    Args:
        duration: Max recording duration in seconds
        sample_rate: Audio sample rate (16000 for Whisper)
        
    Returns:
        numpy array of audio data
    """
    logger.info(f"Recording audio for up to {duration}s...")
    print("🎤 Listening...")
    
    try:
        audio = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype='float32'
        )
        sd.wait()  # Wait until recording is finished
        return audio.flatten()
    except Exception as e:
        logger.error(f"Recording error: {e}")
        raise


def transcribe_audio(audio: np.ndarray, sample_rate: int = 16000) -> str:
    """Transcribe audio using Whisper.
    
    Args:
        audio: numpy array of audio data
        sample_rate: Audio sample rate
        
    Returns:
        Transcribed text
    """
    import whisper
    model = get_whisper_model()
    
    try:
        logger.info("Transcribing with Whisper...")
        
        # Whisper expects float32 audio normalized to [-1, 1]
        # Pad or trim to 30 seconds (Whisper's expected length)
        audio = whisper.pad_or_trim(audio)
        
        # Make log-Mel spectrogram
        mel = whisper.log_mel_spectrogram(audio).to(model.device)
        
        # Decode the audio
        options = whisper.DecodingOptions(language="en", fp16=False)
        result = whisper.decode(model, mel, options)
        
        text = result.text.strip()
        logger.info(f"Transcribed: {text}")
        return text
        
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise


def WhisperListen(duration: float = 5.0) -> str:
    """Listen and transcribe using Whisper.
    
    Args:
        duration: Max recording duration
        
    Returns:
        Transcribed text or empty string on error
    """
    try:
        audio = record_audio(duration)
        
        # Check if audio is mostly silence
        if np.abs(audio).max() < 0.01:
            logger.debug("No speech detected (silence)")
            return ""
        
        text = transcribe_audio(audio)
        return text
        
    except Exception as e:
        logger.error(f"WhisperListen error: {e}")
        return ""


# Fallback to old Listen if needed
def Listen(use_whisper: bool = True, duration: float = 5.0) -> str:
    """Unified listen function with Whisper support.
    
    Args:
        use_whisper: Use Whisper (True) or old SpeechRecognition (False)
        duration: Max recording duration for Whisper
        
    Returns:
        Transcribed text
    """
    if use_whisper:
        try:
            return WhisperListen(duration)
        except Exception as e:
            logger.warning(f"Whisper failed, falling back: {e}")
    
    # Fallback to old method
    from atom.io.speech.listen import Listen as OldListen
    return OldListen()


if __name__ == "__main__":
    print("Whisper Listen Demo")
    print("=" * 50)
    print("Speak something...")
    
    text = WhisperListen(duration=5.0)
    print(f"\nYou said: {text}")
