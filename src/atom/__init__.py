"""Atom - Advanced AI Personal Assistant.

A self-aware AI assistant with natural language understanding, memory, 
and intelligent task execution capabilities.
"""

__version__ = "2.0.0"
__author__ = "Kushal Limbasiya & Meett Paladiya"

from atom.core.llm_provider import UnifiedLLMProvider
from atom.memory.memory_system import MemorySystem
from atom.memory.user_profile import UserProfileManager

__all__ = [
    "UnifiedLLMProvider",
    "MemorySystem",
    "UserProfileManager",
]
