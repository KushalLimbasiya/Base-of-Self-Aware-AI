"""Memory System for Jarvis - Multi-tier conversation history and context management.

This module implements a multi-tier memory system inspired by human cognition:
1. Working Memory: In-memory buffer for current conversation (short-term)
2. Long-term Memory: Persistent SQLite storage for conversation history
3. Context Manager: Retrieves relevant context for better responses

The system automatically stores all conversations and provides context-aware
retrieval for improved intent classification and responses.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from collections import deque
from Logger import setup_logger

logger = setup_logger(__name__, 'jarvis.log')


@dataclass
class ConversationTurn:
    """Represents a single conversation turn (user input + system response)."""
    session_id: str
    timestamp: str
    user_input: str
    intent_tag: str
    confidence: float
    response: str
    context: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationTurn':
        """Create from dictionary."""
        return cls(**data)


class WorkingMemory:
    """In-memory buffer for current conversation session.
    
    Maintains a limited-size buffer of recent conversation turns
    for quick access during active conversation.
    
    Attributes:
        capacity (int): Maximum number of turns to keep in memory
        turns (deque): Double-ended queue of conversation turns
    """
    
    def __init__(self, capacity: int = 20):
        """Initialize working memory.
        
        Args:
            capacity: Maximum number of conversation turns to store
        """
        self.capacity = capacity
        self.turns: deque[ConversationTurn] = deque(maxlen=capacity)
        logger.info(f"WorkingMemory initialized with capacity {capacity}")
    
    def add(self, turn: ConversationTurn):
        """Add a conversation turn to working memory.
        
        Args:
            turn: ConversationTurn object to store
        """
        self.turns.append(turn)
        logger.debug(f"Added turn to working memory: {turn.user_input[:50]}...")
    
    def get_recent(self, limit: int = 5) -> List[ConversationTurn]:
        """Get recent conversation turns.
        
        Args:
            limit: Maximum number of turns to retrieve
            
        Returns:
            List of recent ConversationTurn objects
        """
        return list(self.turns)[-limit:]
    
    def clear(self):
        """Clear all turns from working memory."""
        self.turns.clear()
        logger.info("Working memory cleared")
    
    def get_context_summary(self) -> str:
        """Generate a summary of current conversation context.
        
        Returns:
            String summary of recent conversation
        """
        if not self.turns:
            return "No conversation history"
        
        recent = self.get_recent(3)
        summary = "Recent conversation:\n"
        for turn in recent:
            summary += f"User: {turn.user_input}\n"
            summary += f"Response: {turn.response}\n"
        return summary


class LongTermMemory:
    """Persistent storage for conversation history using SQLite.
    
    Stores all conversation turns in a SQLite database for long-term
    retrieval and analysis. Supports querying by session, date, and content.
    
    Attributes:
        db_path (Path): Path to SQLite database file
        conn (sqlite3.Connection): Database connection
    """
    
    def __init__(self, db_path: str = "data/memory.db"):
        """Initialize long-term memory storage.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._create_tables()
        logger.info(f"LongTermMemory initialized at {self.db_path}")
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()
        
        # Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                user_input TEXT NOT NULL,
                intent_tag TEXT NOT NULL,
                confidence REAL NOT NULL,
                response TEXT NOT NULL,
                context TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Index for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_session_id 
            ON conversations(session_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON conversations(timestamp)
        ''')
        
        self.conn.commit()
        logger.debug("Database tables created/verified")
    
    def store(self, turn: ConversationTurn):
        """Store a conversation turn in the database.
        
        Args:
            turn: ConversationTurn object to store
        """
        try:
            cursor = self.conn.cursor()
            context_json = json.dumps(turn.context) if turn.context else None
            
            cursor.execute('''
                INSERT INTO conversations 
                (session_id, timestamp, user_input, intent_tag, confidence, response, context)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                turn.session_id,
                turn.timestamp,
                turn.user_input,
                turn.intent_tag,
                turn.confidence,
                turn.response,
                context_json
            ))
            
            self.conn.commit()
            logger.debug(f"Stored conversation turn in database: {turn.user_input[:50]}...")
            
        except sqlite3.Error as e:
            logger.error(f"Error storing conversation in database: {e}")
    
    def get_by_session(self, session_id: str, limit: int = 50) -> List[ConversationTurn]:
        """Retrieve conversation turns for a specific session.
        
        Args:
            session_id: Session identifier
            limit: Maximum number of turns to retrieve
            
        Returns:
            List of ConversationTurn objects
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT session_id, timestamp, user_input, intent_tag, 
                       confidence, response, context
                FROM conversations
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (session_id, limit))
            
            rows = cursor.fetchall()
            turns = []
            
            for row in rows:
                context = json.loads(row[6]) if row[6] else None
                turn = ConversationTurn(
                    session_id=row[0],
                    timestamp=row[1],
                    user_input=row[2],
                    intent_tag=row[3],
                    confidence=row[4],
                    response=row[5],
                    context=context
                )
                turns.append(turn)
            
            return turns
            
        except sqlite3.Error as e:
            logger.error(f"Error retrieving session conversations: {e}")
            return []
    
    def get_recent(self, limit: int = 10) -> List[ConversationTurn]:
        """Retrieve most recent conversation turns across all sessions.
        
        Args:
            limit: Maximum number of turns to retrieve
            
        Returns:
            List of ConversationTurn objects
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT session_id, timestamp, user_input, intent_tag, 
                       confidence, response, context
                FROM conversations
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            turns = []
            
            for row in rows:
                context = json.loads(row[6]) if row[6] else None
                turn = ConversationTurn(
                    session_id=row[0],
                    timestamp=row[1],
                    user_input=row[2],
                    intent_tag=row[3],
                    confidence=row[4],
                    response=row[5],
                    context=context
                )
                turns.append(turn)
            
            return turns
            
        except sqlite3.Error as e:
            logger.error(f"Error retrieving recent conversations: {e}")
            return []
    
    def search(self, query: str, limit: int = 10) -> List[ConversationTurn]:
        """Search conversations by content.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            List of matching ConversationTurn objects
        """
        try:
            cursor = self.conn.cursor()
            search_pattern = f"%{query}%"
            
            cursor.execute('''
                SELECT session_id, timestamp, user_input, intent_tag, 
                       confidence, response, context
                FROM conversations
                WHERE user_input LIKE ? OR response LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (search_pattern, search_pattern, limit))
            
            rows = cursor.fetchall()
            turns = []
            
            for row in rows:
                context = json.loads(row[6]) if row[6] else None
                turn = ConversationTurn(
                    session_id=row[0],
                    timestamp=row[1],
                    user_input=row[2],
                    intent_tag=row[3],
                    confidence=row[4],
                    response=row[5],
                    context=context
                )
                turns.append(turn)
            
            return turns
            
        except sqlite3.Error as e:
            logger.error(f"Error searching conversations: {e}")
            return []
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")


class ContextManager:
    """Manages conversation context for better intent understanding.
    
    Provides context-aware features like:
    - Retrieving relevant past conversations
    - Tracking conversation topics
    - Resolving references to previous exchanges
    
    Attributes:
        working_memory (WorkingMemory): In-memory conversation buffer
        long_term_memory (LongTermMemory): Persistent storage
    """
    
    def __init__(self, working_memory: WorkingMemory, long_term_memory: LongTermMemory):
        """Initialize context manager.
        
        Args:
            working_memory: WorkingMemory instance
            long_term_memory: LongTermMemory instance
        """
        self.working_memory = working_memory
        self.long_term_memory = long_term_memory
        logger.info("ContextManager initialized")
    
    def get_relevant_context(self, current_input: str, limit: int = 5) -> List[ConversationTurn]:
        """Get relevant context for current input.
        
        First checks working memory, then searches long-term memory if needed.
        
        Args:
            current_input: Current user input
            limit: Maximum number of context turns to retrieve
            
        Returns:
            List of relevant ConversationTurn objects
        """
        # First, get recent working memory context
        recent = self.working_memory.get_recent(limit)
        
        # If we need more context, search long-term memory
        if len(recent) < limit:
            additional = self.long_term_memory.get_recent(limit - len(recent))
            # Avoid duplicates
            existing_timestamps = {turn.timestamp for turn in recent}
            for turn in additional:
                if turn.timestamp not in existing_timestamps:
                    recent.append(turn)
        
        return recent[:limit]
    
    def has_recent_intent(self, intent_tag: str, within_turns: int = 5) -> bool:
        """Check if an intent was recently used.
        
        Args:
            intent_tag: Intent tag to check for
            within_turns: How many recent turns to check
            
        Returns:
            True if intent was used recently, False otherwise
        """
        recent = self.working_memory.get_recent(within_turns)
        return any(turn.intent_tag == intent_tag for turn in recent)
    
    def get_context_summary(self) -> str:
        """Generate a summary of current context.
        
        Returns:
            String summary of conversation context
        """
        return self.working_memory.get_context_summary()


class MemorySystem:
    """Main memory system integrating all memory tiers.
    
    This is the primary interface for storing and retrieving conversation
    history. It automatically manages both working and long-term memory.
    
    Usage:
        memory = MemorySystem()
        
        # Store a conversation
        turn = ConversationTurn(
            session_id="session_123",
            timestamp=datetime.now().isoformat(),
            user_input="hello",
            intent_tag="greeting",
            confidence=0.95,
            response="Hello Sir"
        )
        memory.store_conversation(turn)
        
        # Get recent conversations
        recent = memory.get_recent_conversations(limit=5)
    """
    
    def __init__(self, working_capacity: int = 20, db_path: str = "data/memory.db"):
        """Initialize the memory system.
        
        Args:
            working_capacity: Capacity of working memory
            db_path: Path to long-term memory database
        """
        self.working_memory = WorkingMemory(capacity=working_capacity)
        self.long_term_memory = LongTermMemory(db_path=db_path)
        self.context_manager = ContextManager(self.working_memory, self.long_term_memory)
        
        logger.info("MemorySystem fully initialized")
    
    def store_conversation(self, turn: ConversationTurn):
        """Store a conversation turn in both working and long-term memory.
        
        Args:
            turn: ConversationTurn object to store
        """
        self.working_memory.add(turn)
        self.long_term_memory.store(turn)
        logger.debug(f"Conversation stored: {turn.user_input[:50]}...")
    
    def get_recent_conversations(self, limit: int = 10) -> List[ConversationTurn]:
        """Get recent conversations from working memory.
        
        Args:
            limit: Maximum number of turns to retrieve
            
        Returns:
            List of recent ConversationTurn objects
        """
        return self.working_memory.get_recent(limit)
    
    def get_session_history(self, session_id: str, limit: int = 50) -> List[ConversationTurn]:
        """Get conversation history for a specific session.
        
        Args:
            session_id: Session identifier
            limit: Maximum number of turns to retrieve
            
        Returns:
            List of ConversationTurn objects for the session
        """
        return self.long_term_memory.get_by_session(session_id, limit)
    
    def search_conversations(self, query: str, limit: int = 10) -> List[ConversationTurn]:
        """Search for conversations containing specific content.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            List of matching ConversationTurn objects
        """
        return self.long_term_memory.search(query, limit)
    
    def get_context(self, current_input: str, limit: int = 5) -> List[ConversationTurn]:
        """Get relevant context for current input.
        
        Args:
            current_input: Current user input
            limit: Maximum context turns to retrieve
            
        Returns:
            List of relevant ConversationTurn objects
        """
        return self.context_manager.get_relevant_context(current_input, limit)
    
    def get_context_summary(self) -> str:
        """Get a summary of current conversation context.
        
        Returns:
            String summary of conversation
        """
        return self.context_manager.get_context_summary()
    
    def clear_working_memory(self):
        """Clear working memory (useful for new session)."""
        self.working_memory.clear()
    
    def close(self):
        """Close memory system and cleanup resources."""
        self.long_term_memory.close()
        logger.info("MemorySystem closed")


# Example usage and testing
if __name__ == "__main__":
    # Demo the memory system
    print("Memory System Demo")
    print("=" * 50)
    
    # Initialize
    memory = MemorySystem()
    session_id = f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Store some conversations
    conversations = [
        ("hello", "greeting", 0.95, "Hello Sir"),
        ("what is the time", "time", 0.88, "14:30"),
        ("who is Albert Einstein", "wikipedia", 0.92, "Albert Einstein was a physicist..."),
        ("play some music", "play", 0.85, "playing music"),
    ]
    
    for user_input, intent, confidence, response in conversations:
        turn = ConversationTurn(
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            user_input=user_input,
            intent_tag=intent,
            confidence=confidence,
            response=response
        )
        memory.store_conversation(turn)
        print(f"Stored: {user_input} -> {intent}")
    
    print("\n" + "=" * 50)
    print("Recent Conversations:")
    recent = memory.get_recent_conversations(limit=3)
    for turn in recent:
        print(f"  {turn.user_input} ({turn.intent_tag}, {turn.confidence:.2f})")
    
    print("\n" + "=" * 50)
    print("Context Summary:")
    print(memory.get_context_summary())
    
    print("\n" + "=" * 50)
    print("Search for 'Albert':")
    results = memory.search_conversations("Albert", limit=5)
    for turn in results:
        print(f"  {turn.user_input} -> {turn.response[:50]}...")
    
    # Cleanup
    memory.close()
    print("\n" + "=" * 50)
    print("Demo complete!")
