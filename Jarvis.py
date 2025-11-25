import random
import json
import torch
from Brain import NeuralNet
from NeuralNetwork import bag_of_words ,tokenize
from Logger import setup_logger

logger = setup_logger(__name__, 'jarvis.log')

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
logger.info(f"Using device: {device}")

try:
    with open("intents.json",'r') as json_data:
        intents = json.load(json_data)
    logger.info("Successfully loaded intents.json")
except FileNotFoundError:
    logger.critical("Error: intents.json not found. Please ensure the file exists.")
    exit(1)
except json.JSONDecodeError as e:
    logger.critical(f"Error: Invalid JSON in intents.json: {e}")
    exit(1)

FILE = "TrainData.pth"
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

model = NeuralNet(input_size,hidden_size,output_size).to(device)
model.load_state_dict(model_state)
model.eval()

#--------------------------------------------------------
USRNAME = "Meet"
BOTNAME = "Nirav"

from Listen import Listen
from Speak import Say
from Task import InputExecution
from Task import NonInputExecution

def Main():
    try:
        sentence = Listen()
        result = str(sentence)

        if sentence == "stop":
            Main()

        elif sentence == "bye":
            Say("Goodbye!")
            exit()

        sentence = tokenize(sentence)
        X = bag_of_words(sentence,all_words)
        X = X.reshape(1,X.shape[0])
        X = torch.from_numpy(X).to(device)

        output = model(X)

        _ , predicted = torch.max(output,dim=1)

        tag = tags[predicted.item()]

        probs = torch.softmax(output,dim=1)
        prob = probs[0][predicted.item()]

        if prob.item() > 0.75:
            for intent in intents['intents']:
                if tag == intent["tag"]:
                    reply = random.choice(intent["responses"])

                    if "time" in reply:
                        NonInputExecution(reply)

                    elif "date" in reply:
                        NonInputExecution(reply)

                    elif "day" in reply:
                        NonInputExecution(reply)  

                    elif "wikipedia" in reply:
                        InputExecution(reply,result)

                    elif "google" in reply:
                        InputExecution(reply,result)
                    
                    elif "play" in reply:
                        InputExecution(reply, result)

                    else:
                        Say(reply)
        else:
            logger.warning(f"Low confidence ({prob.item():.2f}) for tag '{tag}' - Not executing command")
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        Say("Goodbye!")
        exit()
    except Exception as e:
        logger.error(f"Error in Main: {e}", exc_info=True)
        # Continue running despite errors

if __name__ == "__main__":
    try:
        logger.info("="*50)
        logger.info("Jarvis is starting...")
        logger.info(f"Model loaded with {len(tags)} intents")
        logger.info("="*50)
        while True:
            Main()
    except KeyboardInterrupt:
        logger.info("Shutting down Jarvis...")
        Say("Goodbye!")
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        exit(1)

