"""LLM Provider interface for free AI services.

This module provides a unified interface to multiple free LLM providers:
- Cerebras: Ultra-fast inference (2100 tokens/sec)
- Google AI Studio: Gemini models with strong reasoning
- Groq: Fast inference with multiple model options

Features:
- Automatic fallback between providers
- Rate limiting and quota management
- Response caching
- Usage tracking
"""

import os
import asyncio
from typing import List, Dict, Optional, AsyncIterator, Union
from dotenv import load_dotenv
from atom.utils.logger import setup_logger
import time
from collections import deque

logger = setup_logger(__name__, 'llm.log')
load_dotenv()


class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, calls_per_minute: int = 30):
        self.calls_per_minute = calls_per_minute
        self.calls: deque = deque()
    
    def can_make_request(self) -> bool:
        """Check if we can make a request."""
        now = time.time()
        
        # Remove calls older than 1 minute
        while self.calls and self.calls[0] < now - 60:
            self.calls.popleft()
        
        return len(self.calls) < self.calls_per_minute
    
    def wait_if_needed(self):
        """Wait if rate limit reached."""
        while not self.can_make_request():
            logger.warning("Rate limit reached, waiting...")
            time.sleep(1)
        self.calls.append(time.time())


class CerebrasProvider:
    """Cerebras Cloud SDK provider."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('CEREBRAS_API_KEY')
        self.model = "llama3.1-8b"  # Using 8B model (faster, still capable)
        self.rate_limiter = RateLimiter(calls_per_minute=1000)
        
        if not self.api_key:
            logger.warning("Cerebras API key not found")
            self.client = None
        else:
            try:
                from cerebras.cloud.sdk import Cerebras
                self.client = Cerebras(api_key=self.api_key)
                logger.info("Cerebras provider initialized")
            except ImportError:
                logger.error("cerebras-cloud-sdk not installed. Run: pip install cerebras-cloud-sdk")
                self.client = None
    
    async def generate(self, messages: List[Dict], stream: bool = False, max_tokens: int = 1000) -> Union[str, AsyncIterator]:
        """Generate response from Cerebras."""
        if not self.client:
            raise Exception("Cerebras client not initialized")
        
        self.rate_limiter.wait_if_needed()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                stream=stream
            )
            
            if stream:
                return self._stream_response(response)
            else:
                return response.choices[0].message.content
                
        except Exception as e:
            logger.error(f"Cerebras error: {e}")
            raise
    
    async def _stream_response(self, response):
        """Stream response chunks."""
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class GoogleAIProvider:
    """Google AI Studio (Gemini) provider."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        self.model_name = 'gemini-flash-latest'  # Correct model name for free tier
        self.rate_limiter = RateLimiter(calls_per_minute=60)
        
        if not self.api_key:
            logger.warning("Google API key not found")
            self.model = None
        else:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.genai = genai
                self.model = genai.GenerativeModel(self.model_name)
                logger.info("Google AI provider initialized")
            except ImportError:
                logger.error("google-generativeai not installed. Run: pip install google-generativeai")
                self.model = None
    
    async def generate(self, messages: List[Dict], stream: bool = False, max_tokens: int = 1000) -> Union[str, AsyncIterator]:
        """Generate response from Gemini."""
        if not self.model:
            raise Exception("Google AI client not initialized")
        
        self.rate_limiter.wait_if_needed()
        
        try:
            # Convert messages to Gemini format
            prompt = self._convert_messages(messages)
            
            response = self.model.generate_content(
                prompt,
                stream=stream,
                generation_config=self.genai.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.7
                )
            )
            
            if stream:
                return self._stream_response(response)
            else:
                return response.text
                
        except Exception as e:
            logger.error(f"Google AI error: {e}")
            raise
    
    def _convert_messages(self, messages: List[Dict]) -> str:
        """Convert OpenAI-style messages to Gemini prompt."""
        prompt_parts = []
        for msg in messages:
            role = msg['role']
            content = msg['content']
            if role == 'system':
                prompt_parts.append(f"System Instructions: {content}\n")
            elif role == 'user':
                prompt_parts.append(f"User: {content}")
            elif role == 'assistant':
                prompt_parts.append(f"Assistant: {content}")
        return "\n".join(prompt_parts)
    
    async def _stream_response(self, response):
        """Stream response chunks."""
        for chunk in response:
            if chunk.text:
                yield chunk.text


class GroqProvider:
    """Groq Cloud provider."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        self.model = "llama-3.3-70b-versatile"  # Updated to current model
        self.rate_limiter = RateLimiter(calls_per_minute=30)
        
        if not self.api_key:
            logger.warning("Groq API key not found")
            self.client = None
        else:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
                logger.info("Groq provider initialized")
            except ImportError:
                logger.error("groq not installed. Run: pip install groq")
                self.client = None
    
    async def generate(self, messages: List[Dict], stream: bool = False, max_tokens: int = 1000) -> Union[str, AsyncIterator]:
        """Generate response from Groq."""
        if not self.client:
            raise Exception("Groq client not initialized")
        
        self.rate_limiter.wait_if_needed()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                stream=stream,
                temperature=0.7
            )
            
            if stream:
                return self._stream_response(response)
            else:
                return response.choices[0].message.content
                
        except Exception as e:
            logger.error(f"Groq error: {e}")
            raise
    
    async def _stream_response(self, response):
        """Stream response chunks."""
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class UnifiedLLMProvider:
    """Unified provider with automatic fallback between free LLM providers.
    
    This class manages multiple LLM providers and automatically handles:
    - Provider selection based on availability
    - Fallback when a provider fails
    - Rate limiting across providers
    - Context building from user profile and memory
    
    Usage:
        llm = UnifiedLLMProvider()
        response = await llm.generate(messages)
    """
    
    def __init__(self, default_provider: str = 'google'):
        """Initialize unified LLM provider.
        
        Args:
            default_provider: Default provider to use ('google', 'groq', or 'cerebras')
        """
        self.providers = {
            'cerebras': CerebrasProvider(),
            'google': GoogleAIProvider(),
            'groq': GroqProvider()
        }
        self.default_provider = default_provider
        
        # Fallback order: try Google first (best reasoning), then Groq (fast), then Cerebras
        self.provider_order = ['google', 'groq', 'cerebras']
        
        # Check which providers are available
        self.available_providers = []
        for name, provider in self.providers.items():
            if hasattr(provider, 'client') and provider.client is not None:
                self.available_providers.append(name)
            elif hasattr(provider, 'model') and provider.model is not None:
                self.available_providers.append(name)
        
        if not self.available_providers:
            logger.error("No LLM providers are available! Please set API keys.")
        else:
            logger.info(f"Available providers: {', '.join(self.available_providers)}")
            logger.info(f"Default provider: {default_provider}")
    
    async def generate(self, 
                      messages: List[Dict], 
                      stream: bool = False, 
                      max_tokens: int = 1000,
                      provider: str = 'auto') -> str:
        """Generate response with automatic provider selection and fallback.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            stream: Whether to stream the response (not fully supported yet)
            max_tokens: Maximum tokens to generate
            provider: Specific provider or 'auto' for automatic selection
            
        Returns:
            Generated text response
            
        Raises:
            Exception: If all providers fail
        """
        if provider == 'auto':
            provider = self.default_provider
        
        # Ensure provider is available
        if provider not in self.available_providers:
            logger.warning(f"Provider {provider} not available, using first available")
            provider = self.available_providers[0] if self.available_providers else None
        
        if not provider:
            raise Exception("No LLM providers available. Please configure API keys.")
        
        # Try primary provider
        try:
            logger.info(f"Using provider: {provider}")
            response = await self.providers[provider].generate(messages, stream, max_tokens)
            return response
        except Exception as e:
            logger.warning(f"Provider {provider} failed: {e}. Trying fallback...")
            
            # Try fallback providers
            for fallback in self.provider_order:
                if fallback != provider and fallback in self.available_providers:
                    try:
                        logger.info(f"Trying fallback provider: {fallback}")
                        response = await self.providers[fallback].generate(messages, stream, max_tokens)
                        return response
                    except Exception as e2:
                        logger.warning(f"Fallback provider {fallback} failed: {e2}")
                        continue
            
            # All providers failed
            logger.error("All LLM providers failed")
            raise Exception("All LLM providers failed. Please check your API keys and network connection.")
    
    def build_system_prompt(self, user_profile=None, recent_memory: str = "") -> str:
        """Build rich system prompt with user context.
        
        Args:
            user_profile: UserProfile object with user information
            recent_memory: String summary of recent conversation
            
        Returns:
            System prompt string
        """
        system_prompt = """You are Atom, an advanced AI assistant with enhanced intelligence and self-awareness.

You have the following capabilities:
- Natural conversation with context awareness
- Remembering past interactions and user preferences
- Providing accurate, helpful, and concise responses
- Admitting when you're uncertain about something
- Being proactive in suggesting relevant information

Guidelines:
- Be helpful, friendly, and professional
- Keep responses concise unless detail is requested
- Remember and use information from past conversations
- Ask clarifying questions when needed
- Provide accurate information and admit when unsure
"""
        
        if user_profile:
            profile_info = f"""
User Profile:
- Name: {user_profile.user_name or 'Not set'}
- Location: {user_profile.location or 'Not set'}
- Interests: {', '.join(user_profile.interests) if user_profile.interests else 'None yet'}
- Conversations: {user_profile.total_conversations}
"""
            system_prompt += profile_info
        
        if recent_memory:
            system_prompt += f"\n\nRecent conversation context:\n{recent_memory}\n"
        
        return system_prompt
    
    def create_messages(self, user_input: str, user_profile=None, recent_memory: str = "") -> List[Dict]:
        """Create message list for LLM.
        
        Args:
            user_input: User's input text
            user_profile: UserProfile object
            recent_memory: Recent conversation summary
            
        Returns:
            List of message dictionaries
        """
        system_prompt = self.build_system_prompt(user_profile, recent_memory)
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]


# Example usage
if __name__ == "__main__":
    async def test():
        """Test the LLM provider."""
        llm = UnifiedLLMProvider()
        
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": "Say hello and introduce yourself in one sentence."}
        ]
        
        print("Testing LLM providers...")
        print("=" * 50)
        
        try:
            response = await llm.generate(messages, stream=False)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")
    
    asyncio.run(test())
