# Atom AI - Quick Start

## Installation

1. **Install in development mode:**
   ```bash
   cd d:\Code\test\Base-of-Self-Aware-AI
   pip install -e .
   ```

2. **Configure API keys:**
   ```bash
   copy .env.example .env
   # Edit .env and add your API keys
   ```

3. **Test LLM providers:**
   ```bash
   cd scripts
   python test_llm_providers.py
   ```

4. **Run Atom:**
   ```bash
   atom
   ```

## Directory Structure

```
Base-of-Self-Aware-AI/
├── src/atom/              # Main package
│   ├── core/              # LLM, config, neural network
│   ├── memory/            # Memory systems
│   ├── io/                # Speech I/O
│   ├── tasks/             # Task execution
│   ├── utils/             # Utilities
│   └── main.py            # Entry point
├── config/                # Configuration files
├── scripts/               # Utility scripts
├── tests/                 # Test suite
├── docs/                  # Documentation
└── data/                  # Data storage
```

## Package Usage

```python
# Import as a package
from atom import UnifiedLLMProvider, MemorySystem
from atom.core import get_config
from atom.memory import UserProfileManager

# Use the components
llm = UnifiedLLMProvider()
memory = MemorySystem()
```

## Old vs New

**Before:** `python Jarvis.py`  
**After:** `atom` or `python -m atom.main`

**Before:** `python Train.py`  
**After:** `atom-train` or `python -m train`
