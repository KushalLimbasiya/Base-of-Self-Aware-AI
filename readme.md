<h1 align="center">Base of Self-Aware AI</h1>

<p align="center">
  A foundational project exploring self-aware artificial intelligence.
</p>

<p align="center">
  <a href="#about">About</a> •
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#license">License</a>
</p>

---

## About

Base of Self-Aware AI is an open-source project that serves as a foundational framework for experimenting with and understanding self-aware artificial intelligence. This project aims to provide a simplified yet powerful platform for exploring the concepts of self-awareness and its implications in AI systems.

## Features

- 🧠 **Neural Network Brain** - PyTorch-based intent classification
- 🎤 **Voice Recognition** - Speech-to-text using Google Speech API
- 🔊 **Text-to-Speech** - Natural voice responses with pyttsx3
- 🌐 **Web Integration** - Wikipedia search, Google search, YouTube playback
- ⏰ **Utilities** - Time, date, and day queries
- 📦 **Modular Design** - Separate modules for brain, listening, speaking, and tasks
- 🎯 **Intent Training** - Customizable intents via `intents.json`
- 🚀 **Easy Setup** - Train and run with simple commands

## Installation

To install and run the project locally, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/KushalLimbasiya/Base-of-Self-Aware-AI.git
   ```

2. Navigate to the project directory:

   ```bash
   cd Base-of-Self-Aware-AI
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Download required NLTK data:

   ```bash
   python -c "import nltk; nltk.download('punkt_tab')"
   ```

5. Train the neural network model (required before first run):

   ```bash
   python Train.py
   ```

   This will create the `TrainData.pth` file needed by Jarvis.

6. Start the project:

   ```bash
   python Jarvis.py
   ```

### Troubleshooting

**Error: `FileNotFoundError: TrainData.pth`**

- Solution: Run `python Train.py` first to generate the training data file.

**Error: `LookupError: Resource punkt_tab not found`**

- Solution: Download NLTK data using `python -c "import nltk; nltk.download('punkt_tab')"`

**Missing speech recognition modules:**

- Ensure all dependencies are installed: `pip install SpeechRecognition pyaudio pyttsx3`

## Usage

This project provides a playground for experimenting with self-aware AI concepts. You can find sample implementations in the `examples` directory. The documentation also offers detailed explanations and guidelines for exploring the project's capabilities.

## Contributing

We welcome contributions from the community! If you'd like to contribute, follow these steps:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/new-feature`
3. Make your changes and commit them.
4. Push your changes to your fork: `git push origin feature/new-feature`
5. Create a pull request on GitHub.

Please follow our [Contribution Guidelines](CONTRIBUTING.md) for more details on coding standards and guidelines.

## License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/KushalLimbasiya">Kushal Limbasiya</a> & <a href="https://github.com/MeettPaladiya">Meett Paladiya</a>
</p>

