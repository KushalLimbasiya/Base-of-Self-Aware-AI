"""Test script for free LLM providers.

This script tests all three free LLM providers:
- Cerebras
- Google AI Studio (Gemini)
- Groq

Usage:
    python test_llm.py
"""

import asyncio
import sys
import os

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from LLMProvider import UnifiedLLMProvider, CerebrasProvider, GoogleAIProvider, GroqProvider


async def test_individual_provider(provider_name: str, provider):
    """Test an individual provider."""
    print(f"\n{'='*60}")
    print(f"Testing {provider_name.upper()}")
    print(f"{'='*60}")
    
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "Say hello and introduce yourself in one sentence."}
    ]
    
    try:
        response = await provider.generate(messages, stream=False, max_tokens=100)
        print(f"✓ Success!")
        print(f"Response: {response}")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


async def test_unified_provider():
    """Test the unified provider with automatic fallback."""
    print(f"\n{'='*60}")
    print(f"Testing UNIFIED PROVIDER (with automatic fallback)")
    print(f"{'='*60}")
    
    llm = UnifiedLLMProvider()
    
    messages = [
        {"role": "system", "content": "You are Atom, an advanced AI assistant."},
        {"role": "user", "content": "What are your capabilities? Answer in 2-3 sentences."}
    ]
    
    try:
        response = await llm.generate(messages, stream=False, max_tokens=200)
        print(f"✓ Success!")
        print(f"Response: {response}")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


async def test_context_building():
    """Test context building with user profile."""
    print(f"\n{'='*60}")
    print(f"Testing CONTEXT BUILDING")
    print(f"{'='*60}")
    
    llm = UnifiedLLMProvider()
    
    # Mock user profile
    class MockProfile:
        user_name = "Test User"
        location = "Mumbai"
        interests = ["AI", "Technology", "Coding"]
        total_conversations = 5
    
    messages = llm.create_messages(
        "What's the weather like?",
        user_profile=MockProfile(),
        recent_memory="User asked about time earlier."
    )
    
    print("Generated messages:")
    for i, msg in enumerate(messages):
        print(f"\n  Message {i+1} ({msg['role']}):")
        print(f"  {msg['content'][:200]}..." if len(msg['content']) > 200 else f"  {msg['content']}")
    
    return True


async def check_api_keys():
    """Check which API keys are configured."""
    print(f"\n{'='*60}")
    print(f"API KEY STATUS")
    print(f"{'='*60}")
    
    keys = {
        'CEREBRAS_API_KEY': os.getenv('CEREBRAS_API_KEY'),
        'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
        'GROQ_API_KEY': os.getenv('GROQ_API_KEY')
    }
    
    configured = []
    for key_name, key_value in keys.items():
        status = "✓ Configured" if key_value else "✗ Not configured"
        print(f"{key_name}: {status}")
        if key_value:
            configured.append(key_name.replace('_API_KEY', '').lower())
    
    print(f"\nAvailable providers: {', '.join(configured) if configured else 'None'}")
    
    if not configured:
        print("\n⚠ WARNING: No API keys configured!")
        print("Please set at least one API key in your .env file.")
        print("\nInstructions:")
        print("1. Copy .env.example to .env")
        print("2. Add your API keys to the .env file")
        print("3. Get API keys from:")
        print("   - Cerebras: https://cloud.cerebras.ai")
        print("   - Google: https://aistudio.google.com")
        print("   - Groq: https://console.groq.com")
        return False
    
    return True


async def main():
    """Main test function."""
    print("\n" + "="*60)
    print("FREE LLM PROVIDER TEST SUITE")
    print("="*60)
    
    # Check API keys first
    if not await check_api_keys():
        return
    
    results = {}
    
    # Test individual providers if keys are available
    if os.getenv('CEREBRAS_API_KEY'):
        cerebras = CerebrasProvider()
        results['cerebras'] = await test_individual_provider('cerebras', cerebras)
    
    if os.getenv('GOOGLE_API_KEY'):
        google = GoogleAIProvider()
        results['google'] = await test_individual_provider('google', google)
    
    if os.getenv('GROQ_API_KEY'):
        groq = GroqProvider()
        results['groq'] = await test_individual_provider('groq', groq)
    
    # Test unified provider
    results['unified'] = await test_unified_provider()
    
    # Test context building
    results['context'] = await test_context_building()
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY")
    print(f"{'='*60}")
    
    for test_name, success in results.items():
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{test_name.capitalize()}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! Your LLM providers are working correctly.")
    else:
        print("\n⚠ Some tests failed. Check the error messages above.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
