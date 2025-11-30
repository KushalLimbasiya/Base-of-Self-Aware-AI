# How to Get Real API Keys

The `.env` file currently has **placeholder values**. You need to replace them with **real API keys**.

## Step-by-Step Instructions

### Option 1: Google AI Studio (Easiest & Recommended) ⭐

1. **Visit**: [https://aistudio.google.com](https://aistudio.google.com)
2. **Sign in** with your Google account
3. Click **"Get API Key"** in the left sidebar
4. Click **"Create API Key"** button
5. **Copy the key** (starts with `AIza...`)
6. Open your `.env` file and replace:
   ```env
   GOOGLE_API_KEY=AIzaSy...your_actual_key_here
   ```

**Time**: ~2 minutes | **Free Tier**: 1500 requests/day

---

### Option 2: Groq (Fastest)

1. **Visit**: [https://console.groq.com](https://console.groq.com)
2. **Sign up** with email or Google
3. Go to **"API Keys"** section
4. Click **"Create API Key"**
5. Give it a name (e.g., "Jarvis")
6. **Copy the key** (starts with `gsk_...`)
7. Open your `.env` file and replace:
   ```env
   GROQ_API_KEY=gsk_...your_actual_key_here
   ```

**Time**: ~3 minutes | **Free Tier**: 14,400 requests/day

---

### Option 3: Cerebras (Ultra-Fast)

1. **Visit**: [https://cloud.cerebras.ai](https://cloud.cerebras.ai)
2. **Sign up** with email or GitHub
3. Navigate to **"API Keys"**
4. Click **"Create API Key"**
5. **Copy the key** (starts with `csk-...`)
6. Open your `.env` file and replace:
   ```env
   CEREBRAS_API_KEY=csk-...your_actual_key_here
   ```

**Time**: ~3 minutes | **Free Tier**: 1M tokens/day

---

## Your .env File Should Look Like:

```env
# At least ONE of these should have a real key
CEREBRAS_API_KEY=csk-abc123...your_real_key
GOOGLE_API_KEY=AIzaSyD...your_real_key
GROQ_API_KEY=gsk_xyz789...your_real_key
```

## Important Notes

⚠️ **Do NOT use placeholder values** like "your_cerebras_api_key_here"  
✅ **You only need ONE key** to get started  
🔒 **Keep your .env file private** (already in .gitignore)  
🔄 **Having all three provides automatic fallback**

---

## After Adding Keys

Run the test again:
```bash
python test_llm.py
```

You should see:
```
✓ Success!
Response: Hello! I'm Gemini, a large language model...
```

---

## Troubleshooting

**"Wrong API Key" error**: Make sure you copied the entire key  
**"API key not valid" error**: The key might be expired, create a new one  
**Still using placeholders?**: Check that you saved the .env file after editing
