# Atom AI - Advanced Self-Aware Personal Assistant

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

*A foundational project exploring self-aware artificial intelligence with natural language understanding, memory systems, and intelligent task execution.*

[Features](#features) • [Installation](#installation) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Contributing](#contributing)

</div>

---

## 🎯 Overview

Atom is an advanced AI personal assistant that combines:
- **Free LLM Integration**: Uses Cerebras, Google AI Studio, and Groq (100% free)
- **Multi-Tier Memory**: Conversation history with semantic search  
- **Voice Interface**: Speech recognition and natural text-to-speech
- **Intelligent Tasks**: Web search, automation, and more
- **Self-Awareness**: Meta-cognition and performance tracking

## ✨ Features

### Current (v2.0)
- 🧠 **Advanced LLM Backend** - Gemini, Llama 3.3, with automatic fallback
- 🎤 **Voice Recognition** - OpenAI Whisper (offline, high accuracy)
- 🔊 **Text-to-Speech** - Edge TTS (natural Microsoft voices)
- 💾 **Memory System** - Remembers conversations and context
- 👤 **User Profiles** - Personalized interactions
- 🌐 **Web Integration** - Search, Wikipedia, YouTube
- 📊 **Logging & Metrics** - Performance tracking
- 🎯 **Intent Classification** - Neural network + LLM hybrid

### Roadmap (Phases 2-10)
- 🔮 **Proactive Intelligence** - Anticipate user needs  
- 👁️ **Computer Vision** - Screen awareness, OCR
- 🤖 **Task Automation** - File management, email, calendar
- 🔌 **Integrations** - Smart home, Spotify, cloud storage
- 🎭 **Emotional Intelligence** - Sentiment analysis, empathy
- 🧬 **Advanced Memory** - Episodic, semantic, procedural
- 👥 **Multi-Agent** - Specialized agents for complex tasks

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- Virtual environment (recommended)

### Quick Install

```bash
# Clone the repository  
git clone https://github.com/KushalLimbasiya/Base-of-Self-Aware-AI.git
cd Base-of-Self-Aware-AI

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install in development mode
pip install -e .

# Download NLTK data
python -c "import nltk; nltk.download('punkt_tab')"
```

### Configure API Keys

```bash
# Copy template
copy .env.example .env

# Edit .env and add at least ONE API key:
# - Cerebras: https://cloud.cerebras.ai
# - Google AI Studio: https://aistudio.google.com  ⭐ Recommended
# - Groq: https://console.groq.com
```

### Train Neural Network (Optional)

```bash
# If using the legacy neural network intent classifier
python src/train.py
```

## 🚀 Quick Start

### Run Atom

```bash
# Using console command
atom

# Or using Python
python -m atom.main
```

### Test LLM Providers

```bash
cd scripts
python test_llm_providers.py
```

### Use as a Package

```python
from atom import UnifiedLLMProvider, MemorySystem
from atom.memory import UserProfileManager

# Initialize components
llm = UnifiedLLMProvider(default_provider='google')
memory = MemorySystem()
profile = UserProfileManager()

# Generate response
messages = llm.create_messages("Hello, how are you?")
response = await llm.generate(messages)
```

## 📚 Documentation

- **[Quick Start](docs/QUICKSTART.md)** - Get up and running
- **[API Keys Guide](docs/setup/API_KEYS_GUIDE.md)** - Setting up LLM providers
- **[Implementation Plan](docs/implementation_plan.md)** - Full roadmap  
- **[Restructure Guide](docs/RESTRUCTURE_MAPPING.md)** - Package structure

## 🏗️ Project Structure

```
Base-of-Self-Aware-AI/
├── src/atom/              # Main package
│   ├── core/              # LLM providers, config, neural network
│   ├── memory/            # Memory systems & user profiles
│   ├── io/                # Speech recognition & synthesis
│   ├── tasks/             # Task execution & web search
│   ├── utils/             # Logging, validation, utilities
│   └── main.py            # Entry point
├── config/                # Configuration files
├── scripts/               # Utility scripts & tests
├── tests/                 # Test suite
├── docs/                  # Documentation
├── data/                  # Database & data storage
├── logs/                  # Log files
└── archive/               # Old structure (reference)
```

## 🛠️ Technology Stack

### Core AI
- **LLMs**: Cerebras (Llama 3.1), Google (Gemini), Groq (Llama 3.3)
- **Neural Network**: PyTorch for intent classification
- **NLP**: NLTK for tokenization
- **Memory**: ChromaDB (vector), SQLite (relational)

### I/O
- **Speech Recognition**: OpenAI Whisper (local, high-quality) + SpeechRecognition fallback
- **Text-to-Speech**: Edge TTS (natural Microsoft voices) + pyttsx3 fallback
- **Keyboard**: pynput

### Web & Utilities
- **Search**: DuckDuckGo, Wikipedia
- **HTTP**: aiohttp, requests
- **Config**: PyYAML, python-dotenv

## 🤝 Contributing

We welcome contributions! See [Contributors.md](Contributors.md) for current contributors.

### How to Contribute

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Star History

If this project helps you, please consider giving it a ⭐!

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/KushalLimbasiya/Base-of-Self-Aware-AI/issues)
- **Discussions**: [GitHub Discussions](https://github.com/KushalLimbasiya/Base-of-Self-Aware-AI/discussions)

## 👥 Authors

- **Kushal Limbasiya** - [@KushalLimbasiya](https://github.com/KushalLimbasiya)
- **Meett Paladiya** - [@MeettPaladiya](https://github.com/MeettPaladiya)

---

<div align="center">

**Made with ❤️ by the Atom Team**

[⬆ Back to Top](#atom-ai---advanced-self-aware-personal-assistant)

</div>
