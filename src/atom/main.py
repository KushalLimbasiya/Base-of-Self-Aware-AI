"""Atom - Advanced AI Personal Assistant with LLM Integration.

Main module that coordinates all components:
- Speech recognition via atom.io.speech
- Natural language understanding via LLM (Cerebras/Google/Groq)
- Conversation memory and context
- Task execution  
- Text-to-speech

The assistant now uses advanced language models instead of simple intent classification.
"""

import asyncio
import uuid
from datetime import datetime
from atom.utils.logger import setup_logger, get_metrics_logger
from atom.core.config import get_config
from atom.core.llm_provider import UnifiedLLMProvider
from atom.memory.memory_system import MemorySystem, ConversationTurn
from atom.memory.user_profile import UserProfileManager
from atom.utils.name_detector import NameDetector
from atom.utils.personal_info_extractor import PersonalInfoExtractor
from atom.utils.validator import sanitize_query
from atom.io.speech.voice_assistant import Listen, Say, StopSpeaking, IsSpeaking
from atom.io.keyboard_listener import start_keyboard_listener, stop_keyboard_listener
from atom.tasks.task_executor import InputExecution, NonInputExecution
import time

logger = setup_logger(__name__, 'atom.log')
metrics = get_metrics_logger()
config = get_config()

# Initialize systems
logger.info("Initializing Atom AI Assistant...")

# Memory system
memory_system = MemorySystem(
    working_capacity=config.get('memory.working_memory_size', 20),
    db_path=config.get('memory.history_db_path', 'data/memory.db')
)

# User profile system
profile_manager = UserProfileManager(db_path='data/memory.db')
name_detector = NameDetector()
info_extractor = PersonalInfoExtractor()
user_profile = profile_manager.get_profile()
logger.info(f"User profile loaded: {user_profile.user_name or 'No name set'}")

# LLM provider (replaces neural network)
llm = UnifiedLLMProvider(default_provider='google')
logger.info("LLM provider initialized")

# Generate unique session ID
session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
logger.info(f"Session ID: {session_id}")

# User settings from config
USRNAME = config.get('bot.username', 'User')
BOTNAME = config.get('bot.name', 'Atom')

logger.info(f"Bot: {BOTNAME}, User: {USRNAME}")


async def process_with_llm(user_input: str) -> str:
    """Process user input with LLM and return response.
    
    Args:
        user_input: The sanitized user input text
        
    Returns:
        LLM generated response
    """
    try:
        # Get recent conversation context
        recent_convos = memory_system.get_recent_conversations(limit=5)
        recent_memory = ""
        if recent_convos:
            recent_memory = "\n".join([
                f"User: {turn.user_input}\n{BOTNAME}: {turn.response}"
                for turn in recent_convos[-3:]  # Last 3 turns
            ])
        
        # Build messages with context
        messages = llm.create_messages(
            user_input=user_input,
            user_profile=user_profile,
            recent_memory=recent_memory
        )
        
        # Generate response
        response = await llm.generate(messages, max_tokens=500)
        
        return response
        
    except Exception as e:
        logger.error(f"LLM processing error: {e}", exc_info=True)
        return "I'm having trouble processing that right now. Could you try again?"


def detect_task_intent(user_input: str, llm_response: str) -> dict:
    """Detect if user wants to execute a specific task.
    
    Returns dict with:
        - action: 'time', 'date', 'day', 'wikipedia', 'google', 'youtube', 'none'
        - query: search query if applicable
    """
    user_lower = user_input.lower()
    
    # Time/date/day
    if any(word in user_lower for word in ['time', 'clock', "what's the time", 'tell me the time']):
        return {'action': 'time', 'query': None}
    
    if any(word in user_lower for word in ['date', 'today', "what's the date", "what is the date"]):
        return {'action': 'date', 'query': None}
    
    if any(word in user_lower for word in ['day', "what day", 'which day']):
        return {'action': 'day', 'query': None}
    
    # Searches
    if 'wikipedia' in user_lower:
        # Extract search query after 'wikipedia'
        query = user_input.split('wikipedia', 1)[-1].strip()
        return {'action': 'wikipedia', 'query': query or user_input}
    
    if any(word in user_lower for word in ['google', 'search for', 'search']):
        query = user_input.replace('google', '').replace('search for', '').replace('search', '').strip()
        return {'action': 'google', 'query': query or user_input}
    
    if any(word in user_lower for word in ['play', 'youtube']):
        query = user_input.replace('play', '').replace('youtube', '').strip()
        return {'action': 'youtube', 'query': query or user_input}
    
    return {'action': 'none', 'query': None}


def Main():
    """Main execution loop for processing user commands.
    
    This function:
    1. Listens for voice input
    2. Validates and sanitizes the input
    3. Processes with LLM for natural language understanding
    4. Detects and executes tasks if needed
    5. Stores conversation in memory
    6. Generates and speaks response
    
    The loop continues until interrupted or 'bye' command.
    """
    start_time = time.time()
    response = ""
    
    try:
        # Listen for input
        sentence = Listen()
        
        # Validate and sanitize
        sanitized_sentence = sanitize_query(sentence)
        if not sanitized_sentence:
            logger.warning("Invalid input detected, skipping")
            return
        
        # Special commands
        if sanitized_sentence == "stop":
            return
        
        if sanitized_sentence.lower() in ["bye", "goodbye", "exit", "quit"]:
            response = "Goodbye! It was nice talking to you."
            Say(response)
            # Store conversation before exiting
            turn = ConversationTurn(
                session_id=session_id,
                timestamp=datetime.now().isoformat(),
                user_input=sanitized_sentence,
                intent_tag="bye",
                confidence=1.0,
                response=response
            )
            memory_system.store_conversation(turn)
            raise KeyboardInterrupt()  # Exit gracefully
        
        # Process with LLM
        logger.info(f"User: {sanitized_sentence}")
        response = asyncio.run(process_with_llm(sanitized_sentence))
        logger.info(f"{BOTNAME}: {response}")
        
        # Detect if user wants a specific task
        task_intent = detect_task_intent(sanitized_sentence, response)
        
        if task_intent['action'] == 'time':
            NonInputExecution("time")
        elif task_intent['action'] == 'date':
            NonInputExecution("date")
        elif task_intent['action'] == 'day':
            NonInputExecution("day")
        elif task_intent['action'] == 'wikipedia':
            InputExecution("wikipedia", task_intent['query'])
        elif task_intent['action'] == 'google':
            InputExecution("google", task_intent['query'])
        elif task_intent['action'] == 'youtube':
            InputExecution("play", task_intent['query'])
        else:
            # Just speak the LLM response
            Say(response)
        
        # Detect and update user profile info
        detected_name = name_detector.extract_name(sanitized_sentence)
        if detected_name and not user_profile.user_name:
            user_profile.user_name = detected_name
            profile_manager.save_profile(user_profile)
            logger.info(f"Detected and saved user name: {detected_name}")
        
        # Extract other personal info
        info = info_extractor.extract_all(sanitized_sentence)
        if info:
            profile_updated = False
            if info.get('location') and not user_profile.location:
                user_profile.location = info['location']
                profile_updated = True
            if info.get('interests'):
                user_profile.interests.extend(info['interests'])
                profile_updated = True
            if profile_updated:
                profile_manager.save_profile(user_profile)
        
        # Store conversation
        response_time = time.time() - start_time
        turn = ConversationTurn(
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            user_input=sanitized_sentence,
            intent_tag="llm_response",
            confidence=1.0,  # LLM always processes
            response=response
        )
        memory_system.store_conversation(turn)
        
        # Update profile conversation count
        user_profile.total_conversations += 1
        user_profile.last_interaction = datetime.now().isoformat()
        if not user_profile.first_interaction:
            user_profile.first_interaction = user_profile.last_interaction
        profile_manager.save_profile(user_profile)
        
        # Record metrics
        metrics.record_query(
            intent="llm_conversation",
            confidence=1.0,
            response_time=response_time,
            success=True
        )
    
    except KeyboardInterrupt:
        raise  # Let outer handler deal with it
    except Exception as e:
        logger.error(f"Error in Main: {e}", exc_info=True)
        Say("I encountered an error. Please try again.")


def main():
    """Entry point for the application."""
    try:
        logger.info("="*50)
        logger.info("Atom AI is starting...")
        logger.info(f"LLM Provider: {llm.default_provider}")
        logger.info(f"Available providers: {', '.join(llm.available_providers)}")
        logger.info(f"Session ID: {session_id}")
        logger.info(f"Memory system initialized")
        logger.info("="*50)
        
        # Start keyboard listener for speech interruption
        print("\n🤖 Atom AI Assistant v2.0")
        print(f"💬 Powered by: {llm.default_provider.capitalize()} (with auto-fallback)")
        print("💡 Tip: Press 'q' during speech to interrupt Atom")
        print("🗣️  Say 'bye' or 'goodbye' to exit\n")
        print("Listening...\n")
        
        start_keyboard_listener()
        
        while True:
            Main()
            
    except KeyboardInterrupt:
        logger.info("Shutting down Atom...")
        stop_keyboard_listener()
        Say("Goodbye!")
        
        # Print session summary
        logger.info("\n" + "="*50)
        logger.info("Session Summary:")
        logger.info(metrics.get_session_summary())
        logger.info("="*50)
        
        # Cleanup
        metrics.finalize_session()
        memory_system.close()
        
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        # Cleanup on error
        try:
            stop_keyboard_listener()
            metrics.finalize_session()
            memory_system.close()
        except:
            pass
        exit(1)


if __name__ == "__main__":
    main()
