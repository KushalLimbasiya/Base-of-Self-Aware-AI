"""Phase 1 Tests - LLM Integration & RAG"""

import asyncio
import pytest
import sys
sys.path.insert(0, '../../src')

from atom.core.llm_provider import UnifiedLLMProvider


@pytest.mark.asyncio
async def test_llm_providers():
    """Test all LLM providers are initialized."""
    llm = UnifiedLLMProvider()
    assert len(llm.available_providers) >= 3
    assert 'groq' in llm.available_providers or 'google' in llm.available_providers


@pytest.mark.asyncio
async def test_llm_generation():
    """Test LLM can generate responses."""
    llm = UnifiedLLMProvider(default_provider='groq')
    messages = [{"role": "user", "content": "Say hello in one word"}]
    response = await llm.generate(messages, max_tokens=10)
    assert response is not None
    assert len(response) > 0


@pytest.mark.asyncio
async def test_llm_fallback():
    """Test LLM fallback mechanism."""
    llm = UnifiedLLMProvider()
    # Should have fallback enabled
    assert llm.available_providers is not None
    assert len(llm.available_providers) > 1


if __name__ == "__main__":
    # Run tests manually
    async def run_tests():
        print("Running Phase 1 LLM Tests...")
        try:
            await test_llm_providers()
            print("✓ LLM Providers Test Passed")
        except Exception as e:
            print(f"✗ LLM Providers Test Failed: {e}")
        
        try:
            await test_llm_generation()
            print("✓ LLM Generation Test Passed")
        except Exception as e:
            print(f"✗ LLM Generation Test Failed: {e}")
        
        try:
            await test_llm_fallback()
            print("✓ LLM Fallback Test Passed")
        except Exception as e:
            print(f"✗ LLM Fallback Test Failed: {e}")
    
    asyncio.run(run_tests())
