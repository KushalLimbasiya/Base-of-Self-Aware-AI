"""Voice Assistant Module for Atom AI.

Provides a unified voice interface that works like real voice assistants:
- Continuous listening with automatic speech detection
- Smart silence detection to know when user stops speaking
- Non-blocking responses (speak while ready to listen)
- Natural conversation flow

Uses Whisper for STT and Edge TTS for natural speech output.
"""

import threading
import queue
import time
import numpy as np
import sounddevice as sd
from atom.utils.logger import setup_logger

logger = setup_logger(__name__, 'atom.log')

# Global state
_is_listening = False
_is_speaking = False
_stop_requested = False
_audio_queue = queue.Queue()
_whisper_model = None


class VoiceAssistant:
    """Voice assistant with natural conversation flow.
    
    Features:
    - Continuous listening with VAD (Voice Activity Detection)
    - Auto speech end detection (silence threshold)
    - Non-blocking TTS (can interrupt)
    - Listen while speaking (barge-in ready)
    """
    
    def __init__(
        self,
        whisper_model: str = "small",
        tts_voice: str = "en-US-AriaNeural",
        silence_threshold: float = 0.01,
        silence_duration: float = 1.0,
        sample_rate: int = 16000
    ):
        """Initialize voice assistant.
        
        Args:
            whisper_model: Whisper model size (tiny/base/small/medium)
            tts_voice: Edge TTS voice name
            silence_threshold: Audio level to detect silence
            silence_duration: Seconds of silence to stop recording
            sample_rate: Audio sample rate
        """
        self.whisper_model_size = whisper_model
        self.tts_voice = tts_voice
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.sample_rate = sample_rate
        
        # Language-specific TTS voices
        self.tts_voices = {
            "en": "en-US-AriaNeural",      # English
            "hi": "hi-IN-SwaraNeural",      # Hindi
            "gu": "gu-IN-DhwaniNeural"      # Gujarati
        }
        
        self._model = None
        self._is_listening = False
        self._is_speaking = False
        self._stop_flag = False
        self._last_detected_lang = "en"  # Default to English
        
        logger.info("VoiceAssistant initialized (EN/HI/GU supported)")
    
    def _load_whisper(self):
        """Load Whisper model (lazy loading)."""
        if self._model is None:
            import whisper
            import torch
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Loading Whisper {self.whisper_model_size} on {device}")
            self._model = whisper.load_model(self.whisper_model_size, device=device)
            logger.info("Whisper model ready")
        return self._model
    
    def listen(self, max_duration: float = 10.0) -> str:
        """Listen for speech with automatic end detection.
        
        Starts recording when sound detected, stops when silence detected.
        
        Args:
            max_duration: Maximum recording duration
            
        Returns:
            Transcribed text
        """
        self._is_listening = True
        self._stop_flag = False
        
        print("🎤 Listening...")
        logger.info("Listening started")
        
        try:
            # Record with silence detection
            audio = self._record_with_vad(max_duration)
            
            if audio is None or len(audio) < self.sample_rate * 0.5:  # Less than 0.5s
                logger.debug("No speech detected")
                return ""
            
            # Transcribe
            text = self._transcribe(audio)
            return text
            
        finally:
            self._is_listening = False
    
    def _record_with_vad(self, max_duration: float) -> np.ndarray:
        """Record audio with Voice Activity Detection.
        
        Args:
            max_duration: Maximum duration to record
            
        Returns:
            Audio array or None if no speech
        """
        chunks = []
        silence_start = None
        has_speech = False
        
        # Recording callback
        def callback(indata, frames, time_info, status):
            if self._stop_flag:
                raise sd.CallbackAbort()
            chunks.append(indata.copy())
        
        # Start recording
        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype='float32',
            callback=callback
        ):
            start_time = time.time()
            
            while time.time() - start_time < max_duration:
                if self._stop_flag:
                    break
                
                time.sleep(0.1)
                
                if not chunks:
                    continue
                
                # Check latest chunk for speech
                latest = chunks[-1].flatten()
                level = np.abs(latest).max()
                
                if level > self.silence_threshold:
                    has_speech = True
                    silence_start = None
                elif has_speech:
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start > self.silence_duration:
                        logger.debug("Silence detected, stopping recording")
                        break
        
        if not chunks:
            return None
        
        return np.concatenate(chunks).flatten()
    
    def _transcribe(self, audio: np.ndarray) -> tuple:
        """Transcribe audio using Whisper with auto language detection.
        
        Returns:
            Tuple of (transcribed_text, detected_language)
        """
        import whisper
        
        model = self._load_whisper()
        
        logger.info("Transcribing with auto language detection...")
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(model.device)
        
        # Detect language first
        _, probs = model.detect_language(mel)
        detected_lang = max(probs, key=probs.get)
        
        # Only allow en, hi, gu - default to en for others
        if detected_lang not in ["en", "hi", "gu"]:
            detected_lang = "en"
        
        logger.info(f"Detected language: {detected_lang}")
        
        # Transcribe in detected language
        options = whisper.DecodingOptions(language=detected_lang, fp16=False)
        result = whisper.decode(model, mel, options)
        
        text = result.text.strip()
        logger.info(f"Transcribed ({detected_lang}): {text}")
        
        # Store for TTS to use same language
        self._last_detected_lang = detected_lang
        
        return text
    
    def speak(self, text: str, blocking: bool = True) -> None:
        """Speak text using Edge TTS.
        
        Args:
            text: Text to speak
            blocking: Wait for speech to finish if True
        """
        if not text:
            return
        
        self._is_speaking = True
        
        if blocking:
            self._speak_sync(text)
        else:
            thread = threading.Thread(target=self._speak_sync, args=(text,))
            thread.daemon = True
            thread.start()
    
    def _speak_sync(self, text: str) -> None:
        """Synchronous speech output with auto language voice."""
        try:
            import asyncio
            import tempfile
            import edge_tts
            import pygame
            
            # Select voice based on detected language
            voice = self.tts_voices.get(self._last_detected_lang, self.tts_voice)
            logger.info(f"Speaking ({self._last_detected_lang}): {text[:50]}...")
            
            # Generate TTS
            async def generate():
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                    communicate = edge_tts.Communicate(text, voice)
                    await communicate.save(f.name)
                    return f.name
            
            audio_path = asyncio.run(generate())
            
            # Play
            pygame.mixer.init()
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy() and not self._stop_flag:
                pygame.time.Clock().tick(10)
            
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            
            # Cleanup
            import os
            os.unlink(audio_path)
            
            logger.info("Speech complete")
            
        except Exception as e:
            logger.error(f"TTS error: {e}")
        finally:
            self._is_speaking = False
    
    def stop(self) -> None:
        """Stop listening and speaking."""
        self._stop_flag = True
        try:
            import pygame
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
        except:
            pass
    
    @property
    def is_listening(self) -> bool:
        return self._is_listening
    
    @property
    def is_speaking(self) -> bool:
        return self._is_speaking


# Simple interface functions
_assistant = None

def get_assistant() -> VoiceAssistant:
    """Get or create voice assistant instance."""
    global _assistant
    if _assistant is None:
        _assistant = VoiceAssistant()
    return _assistant


def Listen(max_duration: float = 10.0) -> str:
    """Listen for speech (simple interface)."""
    return get_assistant().listen(max_duration)


def Say(text: str, blocking: bool = True) -> None:
    """Speak text (simple interface)."""
    get_assistant().speak(text, blocking)


def StopSpeaking() -> None:
    """Stop speaking."""
    get_assistant().stop()


def IsSpeaking() -> bool:
    """Check if speaking."""
    return get_assistant().is_speaking


if __name__ == "__main__":
    print("Voice Assistant Demo")
    print("=" * 50)
    print("Speak naturally - I'll detect when you stop.")
    print("Press Ctrl+C to exit.\n")
    
    assistant = VoiceAssistant()
    
    try:
        while True:
            text = assistant.listen()
            if text:
                print(f"\nYou said: {text}")
                response = f"You said: {text}"
                assistant.speak(response)
                print()
            else:
                print("(no speech detected)")
    except KeyboardInterrupt:
        print("\nGoodbye!")
        assistant.stop()
