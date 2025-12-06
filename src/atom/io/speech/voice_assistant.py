"""Voice Assistant Module for Atom AI.

Features:
- Whisper STT (local, GPU accelerated)
- Edge TTS (consistent voice)
- Barge-in: Listen while speaking, can interrupt
- Auto silence detection
"""

import threading
import time
import numpy as np
import sounddevice as sd
from atom.utils.logger import setup_logger

logger = setup_logger(__name__, 'atom.log')


class VoiceAssistant:
    """Voice assistant with barge-in support.
    
    Listens continuously even while speaking, allowing user to interrupt.
    """
    
    # Fixed voice for consistency
    TTS_VOICE = "en-US-AriaNeural"
    
    def __init__(
        self,
        whisper_model: str = "small",
        silence_threshold: float = 0.01,
        silence_duration: float = 1.5,
        sample_rate: int = 16000
    ):
        self.whisper_model_size = whisper_model
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.sample_rate = sample_rate
        
        self._model = None
        self._is_listening = False
        self._is_speaking = False
        self._stop_speaking = False
        self._interrupt_text = None
        self._pygame_initialized = False
        
        logger.info("VoiceAssistant initialized")
    
    def _load_whisper(self):
        """Load Whisper model with GPU if available."""
        if self._model is None:
            import whisper
            import torch
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Loading Whisper {self.whisper_model_size} on {device}")
            self._model = whisper.load_model(self.whisper_model_size, device=device)
            logger.info("Whisper model ready")
        return self._model
    
    def listen(self, max_duration: float = 10.0) -> str:
        """Listen for speech with silence detection."""
        self._is_listening = True
        self._stop_speaking = False
        
        print("🎤 Listening...")
        logger.info("Listening started")
        
        try:
            audio = self._record_with_vad(max_duration)
            
            if audio is None or len(audio) < self.sample_rate * 0.5:
                return ""
            
            text = self._transcribe(audio)
            return text
            
        finally:
            self._is_listening = False
    
    def _record_with_vad(self, max_duration: float) -> np.ndarray:
        """Record with voice activity detection."""
        chunks = []
        silence_start = None
        has_speech = False
        
        def callback(indata, frames, time_info, status):
            if self._stop_speaking:
                raise sd.CallbackAbort()
            chunks.append(indata.copy())
        
        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype='float32',
            callback=callback
        ):
            start_time = time.time()
            
            while time.time() - start_time < max_duration:
                if self._stop_speaking:
                    break
                
                time.sleep(0.1)
                
                if not chunks:
                    continue
                
                latest = chunks[-1].flatten()
                level = np.abs(latest).max()
                
                if level > self.silence_threshold:
                    has_speech = True
                    silence_start = None
                elif has_speech:
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start > self.silence_duration:
                        break
        
        if not chunks:
            return None
        
        return np.concatenate(chunks).flatten()
    
    def _transcribe(self, audio: np.ndarray) -> str:
        """Transcribe audio using Whisper."""
        import whisper
        
        model = self._load_whisper()
        
        logger.info("Transcribing...")
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(model.device)
        
        # Always transcribe in English for consistency
        options = whisper.DecodingOptions(language="en", fp16=False)
        result = whisper.decode(model, mel, options)
        
        text = result.text.strip()
        logger.info(f"Transcribed: {text}")
        return text
    
    def speak(self, text: str, allow_interrupt: bool = True) -> str:
        """Speak text with barge-in support.
        
        Args:
            text: Text to speak
            allow_interrupt: If True, listen for interruption while speaking
            
        Returns:
            Interrupt text if user interrupted, else empty string
        """
        if not text:
            return ""
        
        self._is_speaking = True
        self._stop_speaking = False
        self._interrupt_text = None
        
        # Start speech in thread
        speech_thread = threading.Thread(target=self._speak_async, args=(text,))
        speech_thread.daemon = True
        speech_thread.start()
        
        # Start background listener for interrupt if enabled
        if allow_interrupt:
            interrupt_thread = threading.Thread(target=self._listen_for_interrupt)
            interrupt_thread.daemon = True
            interrupt_thread.start()
        
        # Wait for speech to complete
        speech_thread.join()
        
        return self._interrupt_text or ""
    
    def _speak_async(self, text: str) -> None:
        """Generate and play speech."""
        try:
            import asyncio
            import tempfile
            import edge_tts
            import pygame
            
            logger.info(f"Speaking: {text[:50]}...")
            print(f"🔊 Atom: {text}")
            
            # Generate TTS
            async def generate():
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                    communicate = edge_tts.Communicate(text, self.TTS_VOICE)
                    await communicate.save(f.name)
                    return f.name
            
            audio_path = asyncio.run(generate())
            
            # Play audio
            if not self._pygame_initialized:
                pygame.mixer.init()
                self._pygame_initialized = True
            
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            
            # Wait until done or interrupted
            while pygame.mixer.music.get_busy():
                if self._stop_speaking:
                    pygame.mixer.music.stop()
                    logger.info("Speech interrupted by user")
                    break
                pygame.time.Clock().tick(10)
            
            # Cleanup
            import os
            try:
                os.unlink(audio_path)
            except:
                pass
            
            logger.info("Speech complete")
            
        except Exception as e:
            logger.error(f"TTS error: {e}")
        finally:
            self._is_speaking = False
    
    def _listen_for_interrupt(self) -> None:
        """Background listener for barge-in."""
        try:
            # Wait a bit before starting to listen (let speech start)
            time.sleep(1.0)
            
            if not self._is_speaking:
                return
            
            # Quick record to check for speech
            chunks = []
            
            def callback(indata, frames, time_info, status):
                if not self._is_speaking:
                    raise sd.CallbackAbort()
                chunks.append(indata.copy())
            
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype='float32',
                callback=callback
            ):
                while self._is_speaking:
                    time.sleep(0.1)
                    
                    if not chunks:
                        continue
                    
                    # Check for speech
                    latest = chunks[-1].flatten()
                    level = np.abs(latest).max()
                    
                    if level > self.silence_threshold * 3:  # Higher threshold for interrupt
                        logger.info("User interrupt detected!")
                        self._stop_speaking = True
                        
                        # Get remaining audio and transcribe
                        if len(chunks) > 5:
                            audio = np.concatenate(chunks).flatten()
                            if len(audio) > self.sample_rate * 0.5:
                                self._interrupt_text = self._transcribe(audio)
                        break
                    
                    # Keep only last 2 seconds of audio
                    max_chunks = int(2.0 * self.sample_rate / 1024)
                    if len(chunks) > max_chunks:
                        chunks = chunks[-max_chunks:]
                        
        except Exception as e:
            logger.debug(f"Interrupt listener: {e}")
    
    def stop(self) -> None:
        """Stop speaking."""
        self._stop_speaking = True
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
    global _assistant
    if _assistant is None:
        _assistant = VoiceAssistant()
    return _assistant


def Listen(max_duration: float = 10.0) -> str:
    return get_assistant().listen(max_duration)


def Say(text: str, blocking: bool = True) -> None:
    get_assistant().speak(text, allow_interrupt=True)


def StopSpeaking() -> None:
    get_assistant().stop()


def IsSpeaking() -> bool:
    return get_assistant().is_speaking


if __name__ == "__main__":
    print("=" * 50)
    print("Voice Assistant with Barge-In")
    print("Speak while Atom is talking to interrupt!")
    print("Press Ctrl+C to exit")
    print("=" * 50)
    
    assistant = VoiceAssistant()
    
    try:
        while True:
            text = assistant.listen()
            if text:
                print(f"\nYou said: {text}")
                
                # Check for exit
                if any(word in text.lower() for word in ["bye", "goodbye", "exit", "quit"]):
                    assistant.speak("Goodbye!")
                    break
                
                # Echo response (can be replaced with LLM)
                response = f"You said: {text}"
                interrupt = assistant.speak(response)
                
                if interrupt:
                    print(f"\n[Interrupted with: {interrupt}]")
            else:
                print("(no speech)")
                
    except KeyboardInterrupt:
        print("\nGoodbye!")
        assistant.stop()
