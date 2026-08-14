<h1 align="center">Neural Voice Assistant</h1>

<p align="center">
  A voice assistant with neural intent classification.
</p>

<p align="center">
  <a href="#about">About</a> •
  <a href="#how-it-works">How It Works</a> •
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#license">License</a>
</p>

---

## About

Neural Voice Assistant is a Python voice assistant that maps spoken commands to actions using a
small PyTorch neural network. Speech is transcribed, converted to a
bag-of-words vector, and classified into one of 14 intents — each of which
triggers a handler such as a Wikipedia lookup, a web search, or a YouTube
playback.

It is intentionally small and readable: a good starting point if you want to
understand how a classic intent-classification assistant works end to end,
without the abstraction of a large framework.

## How It Works

```
Microphone → Speech-to-Text → Tokenize + Stem → Bag-of-Words
          → Neural Network → Intent + Confidence → Task Handler → Text-to-Speech
```

The classifier (`Brain.py`) is a 3-layer feedforward network:

| Stage | Detail |
| --- | --- |
| Input | Bag-of-words vector over the vocabulary in `intents.json` |
| Hidden | 2 fully connected layers with ReLU activations |
| Output | Logits over 14 intent classes, softmax for confidence |

Training data lives in `intents.json`, so you can add new intents by editing
one file and re-running `python Train.py`.

**Supported intents:** `greeting`, `bye`, `stop`, `health`, `identity`, `time`,
`date`, `day`, `wikipedia`, `google`, `play`, `profile_query`, `introduce`,
`forget_me`

## Features

- 🧠 **Neural Intent Classification** — PyTorch feedforward network over bag-of-words features
- 🎤 **Voice Recognition** — Speech-to-text via the Google Speech API
- 🔊 **Text-to-Speech** — Spoken responses with `pyttsx3`
- 🌐 **Web Integration** — Wikipedia lookups, web search, YouTube playback
- 💾 **Conversation Memory** — SQLite-backed history with session tracking (`MemorySystem.py`)
- 👤 **User Profiles** — Remembers name and personal details, with a `forget_me` intent
- ⏰ **Utilities** — Time, date, and day queries
- 📦 **Modular Design** — Separate modules for the brain, listening, speaking, and tasks
- 🎯 **Configurable Intents** — Add new commands by editing `intents.json`
- 📊 **Logging & Metrics** — Structured logs and confidence metrics

## Installation

Requires **Python 3.9+** and a working microphone.

1. Clone the repository:

   ```bash
   git clone https://github.com/KushalLimbasiya/neural-voice-assistant.git
   ```

2. Navigate to the project directory:

   ```bash
   cd neural-voice-assistant
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Download required NLTK data:

   ```bash
   python -c "import nltk; nltk.download('punkt')"
   ```

5. Train the model (required before the first run):

   ```bash
   python Train.py
   ```

   This creates `TrainData.pth`, which the assistant loads at startup. The file
   is generated locally and is not tracked in git.

6. Start the assistant:

   ```bash
   python Jarvis.py
   ```

### Troubleshooting

**Error: `FileNotFoundError: TrainData.pth`**

- Run `python Train.py` first to generate the model file.

**Error: `LookupError: Resource punkt not found`**

- Download the NLTK data: `python -c "import nltk; nltk.download('punkt')"`

**Missing speech recognition modules**

- Install the audio stack: `pip install SpeechRecognition pyaudio pyttsx3`
- On Windows, if `pyaudio` fails to build, install a prebuilt wheel instead.

## Usage

Run `python Jarvis.py` and speak a command. Some examples:

| You say | Intent | Neural Voice Assistant does |
| --- | --- | --- |
| "hello" | `greeting` | Greets you back |
| "what is the time" | `time` | Reports the current time |
| "who is Albert Einstein" | `wikipedia` | Reads a Wikipedia summary |
| "search for python tutorials" | `google` | Runs a web search |
| "play lofi beats" | `play` | Opens the video on YouTube |
| "forget me" | `forget_me` | Clears your stored profile |

### Adding a New Intent

1. Add a new block to `intents.json` with a `tag`, some `patterns`, and `responses`.
2. Re-run `python Train.py` to retrain the classifier.
3. If the intent needs custom behaviour, add a handler in `Task.py`.

## Project Structure

| File | Purpose |
| --- | --- |
| `Jarvis.py` | Main loop — listens, classifies, dispatches |
| `Brain.py` | Neural network definition |
| `NeuralNetwork.py` | Tokenization, stemming, bag-of-words |
| `Train.py` | Trains the model and writes `TrainData.pth` |
| `Task.py` | Intent handlers |
| `Listen.py` / `Speak.py` | Speech input and output |
| `MemorySystem.py` | SQLite conversation memory |
| `UserProfile.py` | User detail storage |
| `intents.json` | Training data and intent definitions |

## Limitations

Worth being clear about what this is and isn't:

- Intent classification is **bag-of-words**, so word order is ignored. "Book a
  flight to Paris" and "Paris flight book a" look identical to the model.
- It handles only the 14 predefined intents — there is no open-ended generation.
- Speech recognition requires an internet connection (Google Speech API).
- Accuracy depends entirely on the patterns you supply in `intents.json`.

## Contributing

Contributions are welcome. To contribute:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/new-feature`
3. Make your changes and commit them.
4. Push to your fork: `git push origin feature/new-feature`
5. Open a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/KushalLimbasiya">Kushal Limbasiya</a> & <a href="https://github.com/MeettPaladiya">Meett Paladiya</a>
</p>
