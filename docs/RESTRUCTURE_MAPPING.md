# Codebase Restructure - File Mapping

## Old Structure → New Structure

### Core Files
- `LLMProvider.py` → `src/atom/core/llm_provider.py`
- `Brain.py` → `src/atom/core/brain.py`
- `Config.py` → `src/atom/core/config.py`
- `NeuralNetwork.py` → `src/atom/core/neural_network.py`

### Memory Files
- `MemorySystem.py` → `src/atom/memory/memory_system.py`
- `UserProfile.py` → `src/atom/memory/user_profile.py`

### I/O Files
- `Listen.py` → `src/atom/io/speech/listen.py`
- `Speak.py` → `src/atom/io/speech/speak.py`
- `KeyboardListener.py` → `src/atom/io/keyboard_listener.py`

### Task Files
- `Task.py` → `src/atom/tasks/task_executor.py`
- `WebSearch.py` → `src/atom/tasks/web_search.py`

### Utility Files
- `Logger.py` → `src/atom/utils/logger.py`
- `Validator.py` → `src/atom/utils/validator.py`
- `NameDetector.py` → `src/atom/utils/name_detector.py`
- `PersonalInfoExtractor.py` → `src/atom/utils/personal_info_extractor.py`

### Main Files
- `Jarvis.py` → `src/atom/main.py`
- `Train.py` → `src/train.py`

### Config Files
- `config.yaml` → `config/config.yaml`
- `intents.json` → `config/intents.json`

### Scripts
- `testllm.py` → `scripts/test_llm_providers.py`
- `check_gemini_models.py` → `scripts/check_gemini_models.py`

## Import Changes

### Old Imports
```python
from Logger import setup_logger
from Config import get_config
from MemorySystem import MemorySystem
```

### New Imports
```python
from atom.utils.logger import setup_logger
from atom.core.config import get_config
from atom.memory.memory_system import MemorySystem
```

## Installation

After restructure, install in development mode:
```bash
pip install -e .
```

Then you can run:
```bash
atom              # Run the assistant
atom-train        # Train the model
```

Or import as a package:
```python
from atom import UnifiedLLMProvider, MemorySystem
from atom.core import get_config
```
