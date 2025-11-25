"""Keyboard listener for interrupting Atom while speaking.

Press 'q' key to stop Atom from speaking.
This runs as a background thread.
"""

from pynput import keyboard
from Logger import setup_logger

logger = setup_logger(__name__, 'jarvis.log')

# Flag to control listener
listener_active = False
current_listener = None

def on_press(key):
    """Handle key press events.
    
    Args:
        key: The key that was pressed
    """
    try:
        # Check for 'q' key to stop speaking
        if hasattr(key, 'char') and key.char == 'q':
            from Speak import StopSpeaking, IsSpeaking
            if IsSpeaking():
                logger.info("'q' key pressed - stopping speech")
                StopSpeaking()
                print("\n[Speech interrupted]")
    
    except AttributeError:
        pass  # Special key pressed
    except Exception as e:
        logger.error(f"Error in keyboard listener: {e}")

def start_keyboard_listener():
    """Start the keyboard listener in background.
    
    Returns:
        keyboard.Listener: The active listener object
    """
    global listener_active, current_listener
    
    if listener_active:
        logger.debug("Keyboard listener already active")
        return current_listener
    
    try:
        listener = keyboard.Listener(on_press=on_press)
        listener.daemon = True
        listener.start()
        listener_active = True
        current_listener = listener
        logger.info("Keyboard listener started - Press 'q' to interrupt speech")
        return listener
    
    except Exception as e:
        logger.error(f"Failed to start keyboard listener: {e}")
        return None

def stop_keyboard_listener():
    """Stop the keyboard listener."""
    global listener_active, current_listener
    
    if current_listener:
        current_listener.stop()
        listener_active = False
        current_listener = None
        logger.info("Keyboard listener stopped")

# Example usage
if __name__ == "__main__":
    print("Keyboard Listener Demo")
    print("=" * 50)
    print("Press 'q' to test interrupt functionality")
    print("Press Ctrl+C to exit")
    
    listener = start_keyboard_listener()
    
    try:
        from Speak import Say
        import time
        
        # Test speech
        Say("This is a very long sentence that you can interrupt by pressing the q key at any time during the speech.")
        
        # Keep running
        time.sleep(5)
        
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        stop_keyboard_listener()
