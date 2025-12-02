"""RAG (Retrieval-Augmented Generation) Engine for Atom AI.

Combines vector memory search with LLM generation to provide
context-aware responses based on conversation history.
"""

from typing import List, Dict, Optional
from atom.memory.vector_memory import VectorMemory
from atom.memory.memory_system import MemorySystem
from atom.memory.user_profile import UserProfile
from atom.utils.logger import setup_logger

logger = setup_logger(__name__, 'atom.log')


class RAGEngine:
    """Retrieval-Augmented Generation engine.
    
    Uses semantic search to find relevant past conversations
    and includes them in the LLM context for better responses.
    """
    
    def __init__(
        self,
        vector_memory: VectorMemory,
        memory_system: Optional[MemorySystem] = None,
        max_context_conversations: int = 3
    ):
        """Initialize RAG engine.
        
        Args:
            vector_memory: VectorMemory instance for semantic search
            memory_system: Optional MemorySystem for SQL-based memory
            max_context_conversations: Max number of past conversations to include
        """
        self.vector_memory = vector_memory
        self.memory_system = memory_system
        self.max_context_conversations = max_context_conversations
        
        logger.info("RAG Engine initialized")
    
    def build_context(
        self,
        user_input: str,
        user_profile: UserProfile,
        include_recent: bool = True,
        include_similar: bool = True
    ) -> str:
        """Build context from user profile, recent, and relevant conversations.
        
        Args:
            user_input: Current user input
            user_profile: User's profile
            include_recent: Whether to include recent conversations
            include_similar: Whether to include semantically similar conversations
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        # Add user profile info
        if user_profile.user_name:
            profile_context = f"User's name: {user_profile.user_name}"
            if user_profile.location:
                profile_context += f", Location: {user_profile.location}"
            if user_profile.interests:
                profile_context += f", Interests: {', '.join(user_profile.interests[:3])}"
            context_parts.append(profile_context)
        
        # Add recent conversations
        if include_recent and self.memory_system:
            recent = self.memory_system.get_recent_conversations(limit=2)
            if recent:
                recent_context = "Recent conversation:\n"
                for turn in recent[-2:]:
                    recent_context += f"User: {turn.user_input}\nAtom: {turn.response}\n"
                context_parts.append(recent_context.strip())
        
        # Add semantically similar conversations
        if include_similar:
            similar = self.vector_memory.search_similar(user_input, n_results=2)
            if similar and len(similar) > 0:
                # Only include if not too similar to recent (avoid duplication)
                similar_context = "Related past conversations:\n"
                for conv in similar[:2]:
                    if conv['distance'] < 1.0:  # Only include if reasonably similar
                        similar_context += f"User: {conv['user_input']}\nAtom: {conv['response']}\n"
                if similar_context != "Related past conversations:\n":
                    context_parts.append(similar_context.strip())
        
        # Combine all context
        if context_parts:
            full_context = "\n\n".join(context_parts)
            logger.debug(f"Built context with {len(context_parts)} components")
            return full_context
        
        return ""
    
    def create_rag_prompt(
        self,
        user_input: str,
        user_profile: UserProfile,
        system_prompt: str = None
    ) -> List[Dict[str, str]]:
        """Create LLM messages with RAG context.
        
        Args:
            user_input: Current user input
            user_profile: User's profile
            system_prompt: Optional base system prompt
            
        Returns:
            List of message dicts for LLM
        """
        # Build context
        context = self.build_context(user_input, user_profile)
        
        # Create system prompt with context
        if system_prompt is None:
            system_prompt = "You are Atom, an advanced AI assistant with memory and context awareness."
        
        if context:
            enhanced_prompt = f"{system_prompt}\n\nContext from past interactions:\n{context}"
        else:
            enhanced_prompt = system_prompt
        
        # Create messages
        messages = [
            {"role": "system", "content": enhanced_prompt},
            {"role": "user", "content": user_input}
        ]
        
        return messages
    
    def get_relevant_context_summary(self, user_input: str) -> str:
        """Get a summary of relevant context for debugging/logging.
        
        Args:
            user_input: User's input
            
        Returns:
            Summary string
        """
        similar = self.vector_memory.search_similar(user_input, n_results=3)
        
        if not similar:
            return "No relevant past conversations found"
        
        summary = f"Found {len(similar)} relevant conversations:\n"
        for i, conv in enumerate(similar, 1):
            summary += f"{i}. '{conv['user_input'][:40]}...' (similarity: {1-conv['distance']:.2f})\n"
        
        return summary


if __name__ == "__main__":
    # Example usage
    print("RAG Engine Demo")
    print("=" * 50)
    
    # Initialize components
    from atom.memory.user_profile import UserProfile
    
    vm = VectorMemory(persist_directory="data/test_vector_db")
    rag = RAGEngine(vm)
    
    # Create test profile
    profile = UserProfile(
        user_name="Alice",
        location="San Francisco",
        interests=["AI", "Python"]
    )
    
    # Add some conversations to vector memory
    vm.add_conversation(
        "conv_1",
        "What's machine learning?",
        "Machine learning is a subset of AI that enables systems to learn from data"
    )
    
    # Build context
    context = rag.build_context("Tell me about AI", profile)
    print(f"\nContext for 'Tell me about AI':\n{context}")
    
    # Create RAG prompt
    messages = rag.create_rag_prompt("Explain neural networks", profile)
    print(f"\nRAG prompt messages: {len(messages)} messages")
    for msg in messages:
        print(f"  - {msg['role']}: {msg['content'][:80]}...")
