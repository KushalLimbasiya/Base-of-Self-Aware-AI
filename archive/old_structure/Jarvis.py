"""Jarvis - Voice-activated AI assistant.

Main module that coordinates all components:
- Speech recognition (Listen.py)
- Intent classification (Brain.py, NeuralNetwork.py)
- Task execution (Task.py)
- Text-to-speech (Speak.py)

Configuration is loaded from config.yaml.
Model must be trained first using Train.py.
"""

import random
import json
import torch
import uuid
from datetime import datetime
from Brain import NeuralNet
from NeuralNetwork import bag_of_words, tokenize
from Logger import setup_logger, get_metrics_logger
from Config import get_config
from MemorySystem import MemorySystem, ConversationTurn
from UserProfile import UserProfileManager
from NameDetector import NameDetector
from PersonalInfoExtractor import PersonalInfoExtractor
import time

logger = setup_logger(__name__, 'jarvis.log')
metrics = get_metrics_logger()
config = get_config()

# Initialize memory system
memory_system = MemorySystem(
    working_capacity=config.get('memory.working_memory_size', 20),
    db_path=config.get('memory.history_db_path', 'data/memory.db')
)

# Initialize user profile system
profile_manager = UserProfileManager(db_path='data/memory.db')
name_detector = NameDetector()
info_extractor = PersonalInfoExtractor()
user_profile = profile_manager.get_profile()
logger.info(f"User profile loaded: {user_profile.user_name or 'No name set'}")

# Generate unique session ID
session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
logger.info(f"Session ID: {session_id}")

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
logger.info(f"Using device: {device}")

# Load intents from config
intents_file = config.get('model.intents_file', 'intents.json')
try:
    with open(intents_file, 'r') as json_data:
        intents = json.load(json_data)
    logger.info(f"Successfully loaded {intents_file}")
except FileNotFoundError:
    logger.critical(f"Error: {intents_file} not found. Please ensure the file exists.")
    exit(1)
except json.JSONDecodeError as e:
    logger.critical(f"Error: Invalid JSON in {intents_file}: {e}")
    exit(1)

# Load model from config
FILE = config.get('model.model_file', 'TrainData.pth')
try:
    data = torch.load(FILE)
    logger.info(f"Successfully loaded model from {FILE}")
except FileNotFoundError:
    logger.critical(f"Error: {FILE} not found. Please run Train.py first to generate the model.")
    exit(1)
except Exception as e:
    logger.critical(f"Error loading model file: {e}")
    exit(1)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data["all_words"]
tags = data["tags"]
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

#--------------------------------------------------------
# Load user settings from config
USRNAME = config.get('bot.username', 'Meet')
BOTNAME = config.get('bot.name', 'Nirav')
CONFIDENCE_THRESHOLD = config.get('model.confidence_threshold', 0.75)

logger.info(f"Bot: {BOTNAME}, User: {USRNAME}, Confidence Threshold: {CONFIDENCE_THRESHOLD}")

from Listen import Listen
from Speak import Say, StopSpeaking
from Task import InputExecution
from Task import NonInputExecution
from Validator import sanitize_query, validate_intent_tag, validate_confidence
from KeyboardListener import start_keyboard_listener, stop_keyboard_listener

def Main():
    """Main execution loop for processing user commands.
    
    This function:
    1. Listens for voice input
    2. Validates and sanitizes the input
    3. Classifies the intent using the neural network
    4. Stores conversation in memory system
    5. Records performance metrics
    6. Executes the appropriate action based on intent
    
    The loop continues running until interrupted by user (Ctrl+C)
    or 'bye' command. Errors are caught and logged without stopping
    the main loop.
    
    Special commands:
        - "stop": Skip current iteration
        - "bye": Exit the program
    
    Raises:
        KeyboardInterrupt: Gracefully handled for shutdown
        Exception: Logged but execution continues
    """
    start_time = time.time()  # Track response time
    response = ""
    intent_tag = "unknown"
    confidence = 0.0
    
    try:
        sentence = Listen()
        
        # Validate and sanitize input
        sanitized_sentence = sanitize_query(sentence)
        if not sanitized_sentence:
            logger.warning("Invalid or potentially malicious input detected, skipping")
            return
        
        result = str(sanitized_sentence)

        if sanitized_sentence == "stop":
            return

        elif sanitized_sentence == "bye":
            response = "Goodbye!"
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
            exit()

        sentence_tokens = tokenize(sanitized_sentence)
        X = bag_of_words(sentence_tokens, all_words)
        X = X.reshape(1, X.shape[0])
        X = torch.from_numpy(X).to(device)

        output = model(X)

        _, predicted = torch.max(output, dim=1)

        tag = tags[predicted.item()]
        intent_tag = tag
        
        # Validate intent tag
        if not validate_intent_tag(tag, tags):
            logger.error(f"Invalid tag predicted: {tag}")
            return

        probs = torch.softmax(output, dim=1)
        prob = probs[0][predicted.item()]
        confidence = prob.item()
        
        # Validate confidence with threshold from config
        if validate_confidence(prob.item(), threshold=CONFIDENCE_THRESHOLD):
            for intent in intents['intents']:
                if tag == intent["tag"]:
                    reply = random.choice(intent["responses"])
                    response = reply

                    if "time" in reply:
                        NonInputExecution(reply)

                    elif "date" in reply:
                        NonInputExecution(reply)

                    elif "day" in reply:
                        NonInputExecution(reply)  

                    elif "wikipedia" in reply:
                        InputExecution(reply, result)

                    elif "google" in reply:
                        InputExecution(reply, result)
                    
                    elif "play" in reply:
                        InputExecution(reply, result)

                    else:
                        Say(reply)
        else:
            logger.warning(f"Low confidence ({prob.item():.2f}) for tag '{tag}' - Not executing command")
            response = f"Low confidence: {prob.item():.2f}"
        
        # Store conversation in memory system
        response_time = time.time() - start_time
        turn = ConversationTurn(
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            user_input=sanitized_sentence,
            intent_tag=intent_tag,
            confidence=confidence,
            response=response
        )
        memory_system.store_conversation(turn)
        
        # Record metrics
        metrics.record_query(
            intent=intent_tag,
            confidence=confidence,
            response_time=response_time,
            success=(confidence >= CONFIDENCE_THRESHOLD)
        )
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        Say("Goodbye!")
        # Finalize metrics and close memory system
        logger.info(metrics.get_session_summary())
        metrics.finalize_session()
        memory_system.close()
        exit()
    except Exception as e:
        logger.error(f"Error in Main: {e}", exc_info=True)
        # Continue running despite errors

if __name__ == "__main__":
    try:
        logger.info("="*50)
        logger.info("Atom is starting...")
        logger.info(f"Model loaded with {len(tags)} intents")
        logger.info(f"Session ID: {session_id}")
        logger.info(f"Memory system initialized")
        logger.info("="*50)
        
        # Start keyboard listener for speech interruption
        print("\n💡 Tip: Press 'q' during speech to interrupt Atom\n")
        start_keyboard_listener()
        while True:
            Main()
    except KeyboardInterrupt:
        logger.info("Shutting down Atom...")
        stop_keyboard_listener()  # Stop keyboard listener first
        Say("Goodbye!")
        # Print session summary
        logger.info("\n" + "="*50)
        logger.info("Session Summary:")
        logger.info(metrics.get_session_summary())
        logger.info("="*50)
        # Finalize and cleanup
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

