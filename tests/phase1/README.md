# Phase 1 Tests

Tests for Phase 1: Enhanced Core Intelligence

## Test Files

- `test_llm.py` - LLM provider tests
- `test_rag.py` - Vector memory & RAG tests  
- `test_memory.py` - Memory & profile tests

## Running Tests

### Individual test files:
```bash
python tests/phase1/test_llm.py
python tests/phase1/test_rag.py
python tests/phase1/test_memory.py
```

### With pytest:
```bash
pytest tests/phase1/
```

### All Phase 1 tests:
```bash
pytest tests/phase1/ -v
```
