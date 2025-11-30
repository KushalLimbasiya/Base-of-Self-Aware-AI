# Quick Start Guide - Phase 1: LLM Integration

## What We've Built

You now have a powerful LLM provider system that replaces your simple neural network with state-of-the-art language models!

**New Files:**
- `LLMProvider.py` - Unified interface for 3 free LLM providers
- `.env.example` - Template for API keys
- `test_llm.py` - Test suite for providers
- Updated `requirements.txt` - New dependencies

---

## Setup Instructions (5 minutes)

### Step 1: Install Dependencies

```bash
cd d:\Code\test\Base-of-Self-Aware-AI
pip install -r requirements.txt
```

This installs:
- `cerebras-cloud-sdk` - Cerebras API
- `google-generativeai` - Google Gemini
- `groq` - Groq API
- `python-dotenv` - Environment variables
- `chromadb` & `sentence-transformers` - For vector memory (Phase 1.2)

### Step 2: Get API Keys (Choose at least ONE)

#### Option A: Google AI Studio (Recommended - Easiest)
1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Sign in with Google account
3. Click "Get API Key" → "Create API Key"
4. Copy the key

#### Option B: Groq (Fastest inference)
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up/Sign in
3. Go to API Keys → Create API Key
4. Copy the key

#### Option C: Cerebras (Ultra-fast)
1. Go to [cloud.cerebras.ai](https://cloud.cerebras.ai)
2. Sign up/Sign in
3. Navigate to API Keys → Create
4. Copy the key

### Step 3: Configure API Keys

```bash
# Copy the template
copy .env.example .env

# Edit .env file and paste your API key(s)
# You only need ONE, but having all three provides fallback
```

Example `.env` file:
```env
GOOGLE_API_KEY=AIzaSyD...your_actual_key_here
GROQ_API_KEY=gsk_...your_actual_key_here  
CEREBRAS_API_KEY=csk...your_actual_key_here
```

### Step 4: Test Your Setup

```bash
python test_llm.py
```

Expected output:
```
============================================================
API KEY STATUS
============================================================
CEREBRAS_API_KEY: ✗ Not configured
GOOGLE_API_KEY: ✓ Configured
GROQ_API_KEY: ✓ Configured

Available providers: google, groq

============================================================
Testing GOOGLE
============================================================
✓ Success!
Response: Hello! I'm Gemini, a large language model created by Google...

...

🎉 All tests passed! Your LLM providers are working correctly.
```

---

## Next Steps

### Option 1: Quick Test with Minimal Integration
Try using the LLM in a simple script to see it in action.

### Option 2: Full Integration into Jarvis.py
Replace the neural network with LLM for much better understanding.

### Option 3: Continue Phase 1
Add vector memory and RAG for semantic search capabilities.

**Which would you like to do next?**
