# Archive - Old Project Structure

This directory contains the original Python files from before the v2.0 restructure.

These files are kept for reference but are **no longer used**. The active codebase is now in `src/atom/`.

## What Happened

On 2025-12-06, the project was restructured from a flat file structure to a proper Python package:

- **Old**: All `.py` files in root directory
- **New**: Organized into `src/atom/` with subpackages (core, memory, io, tasks, utils)

## Files in This Archive

### Core
- `Brain.py` → `src/atom/core/brain.py`
- `Config.py` → `src/atom/core/config.py`
- `NeuralNetwork.py` → `src/atom/core/neural_network.py`
- `LLMProvider.py` → `src/atom/core/llm_provider.py`

### Memory
- `MemorySystem.py` → `src/atom/memory/memory_system.py`
- `UserProfile.py` → `src/atom/memory/user_profile.py`

### I/O
- `Listen.py` → `src/atom/io/speech/listen.py`
- `Speak.py` → `src/atom/io/speech/speak.py`
- `KeyboardListener.py` → `src/atom/io/keyboard_listener.py`

### Tasks
- `Task.py` → `src/atom/tasks/task_executor.py`
- `WebSearch.py` → `src/atom/tasks/web_search.py`

### Utilities
- `Logger.py` → `src/atom/utils/logger.py`
- `Validator.py` → `src/atom/utils/validator.py`
- `NameDetector.py` → `src/atom/utils/name_detector.py`
- `PersonalInfoExtractor.py` → `src/atom/utils/personal_info_extractor.py`

### Main
- `Jarvis.py` → `src/atom/main.py`
- `Train.py` → `src/train.py`

## Why Archive?

- **Reference**: In case we need to check old implementation details
- **History**: Preserve the project's evolution
- **Safety**: Don't delete work, just organize it

## Using the New Structure

See the main [README.md](../README.md) for current usage instructions.

All old imports like:
```python
from Logger import setup_logger
```

Should now be:
```python
from atom.utils.logger import setup_logger
```
