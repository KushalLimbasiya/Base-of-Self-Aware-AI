"""Vector Memory System using ChromaDB for semantic search.

This module provides persistent vector storage for conversation embeddings,
enabling semantic search across conversation history.
"""

import chromadb
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pathlib import Path
from atom.utils.logger import setup_logger
from sentence_transformers import SentenceTransformer

logger = setup_logger(__name__, 'atom.log')


class VectorMemory:
    """Manages vector embeddings for semantic conversation search.
    
    Uses ChromaDB for persistent vector storage and sentence-transformers
    for generating embeddings.
    """
    
    def __init__(
        self,
        persist_directory: str = "data/vector_db",
        collection_name: str = "conversations",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """Initialize vector memory system.
        
        Args:
            persist_directory: Directory for ChromaDB persistence
            collection_name: Name of the collection to store vectors
            embedding_model: Sentence transformer model name
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Ensure directory exists
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client (new API)
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Atom conversation embeddings"}
        )
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        
        logger.info(f"VectorMemory initialized with {self.collection.count()} stored embeddings")
    
    def add_conversation(
        self,
        conversation_id: str,
        user_input: str,
        response: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """Add a conversation to vector memory.
        
        Args:
            conversation_id: Unique identifier for this conversation
            user_input: User's message
            response: AI's response
            metadata: Additional metadata to store
        """
        # Combine user input and response for embedding
        combined_text = f"User: {user_input}\nAtom: {response}"
        
        # Generate embedding
        embedding = self.embedding_model.encode(combined_text).tolist()
        
        # Prepare metadata
        if metadata is None:
            metadata = {}
        
        metadata.update({
            "user_input": user_input,
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "conversation_id": conversation_id
        })
        
        # Add to collection
        self.collection.add(
            embeddings=[embedding],
            documents=[combined_text],
            metadatas=[metadata],
            ids=[conversation_id]
        )
        
        logger.debug(f"Added conversation {conversation_id} to vector memory")
    
    def search_similar(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """Search for similar conversations using semantic search.
        
        Args:
            query: Search query text
            n_results: Number of results to return
            filter_metadata: Optional metadata filters
        
        Returns:
            List of matching conversations with metadata and similarity scores
        """
        if self.collection.count() == 0:
            logger.debug("No conversations in vector memory yet")
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, self.collection.count()),
            where=filter_metadata
        )
        
        # Format results
        formatted_results = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'user_input': results['metadatas'][0][i].get('user_input', ''),
                    'response': results['metadatas'][0][i].get('response', ''),
                    'timestamp': results['metadatas'][0][i].get('timestamp', ''),
                    'distance': results['distances'][0][i] if 'distances' in results else None,
                    'metadata': results['metadatas'][0][i]
                })
        
        logger.debug(f"Found {len(formatted_results)} similar conversations for query: {query[:50]}...")
        return formatted_results
    
    def get_conversation_by_id(self, conversation_id: str) -> Optional[Dict]:
        """Retrieve a specific conversation by ID.
        
        Args:
            conversation_id: The conversation ID to retrieve
            
        Returns:
            Conversation dict or None if not found
        """
        try:
            result = self.collection.get(ids=[conversation_id])
            if result['ids']:
                return {
                    'id': result['ids'][0],
                    'user_input': result['metadatas'][0].get('user_input', ''),
                    'response': result['metadatas'][0].get('response', ''),
                    'timestamp': result['metadatas'][0].get('timestamp', ''),
                    'metadata': result['metadatas'][0]
                }
        except Exception as e:
            logger.error(f"Error retrieving conversation {conversation_id}: {e}")
        
        return None
    
    def delete_conversation(self, conversation_id: str) -> None:
        """Delete a conversation from vector memory.
        
        Args:
            conversation_id: ID of conversation to delete
        """
        try:
            self.collection.delete(ids=[conversation_id])
            logger.info(f"Deleted conversation {conversation_id}")
        except Exception as e:
            logger.error(f"Error deleting conversation {conversation_id}: {e}")
    
    def clear_all(self) -> None:
        """Clear all conversations from vector memory."""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "Atom conversation embeddings"}
        )
        logger.warning("Cleared all vector memory")
    
    def get_stats(self) -> Dict:
        """Get statistics about the vector memory.
        
        Returns:
            Dict with stats (count, model info, etc.)
        """
        return {
            'total_conversations': self.collection.count(),
            'collection_name': self.collection_name,
            'embedding_model': self.embedding_model.get_sentence_embedding_dimension(),
            'persist_directory': self.persist_directory
        }


if __name__ == "__main__":
    # Example usage
    print("VectorMemory Demo")
    print("=" * 50)
    
    # Initialize
    vm = VectorMemory(persist_directory="data/test_vector_db")
    
    # Add some test conversations
    vm.add_conversation(
        "conv_1",
        "What's the weather like?",
        "I don't have access to weather data, but you can check weather.com"
    )
    
    vm.add_conversation(
        "conv_2",
        "Tell me about Python programming",
        "Python is a high-level, interpreted programming language known for its simplicity"
    )
    
    # Search
    results = vm.search_similar("How's the climate today?", n_results=2)
    print(f"\nSearch results for 'How's the climate today?':")
    for result in results:
        print(f"  - {result['user_input'][:50]}... (distance: {result['distance']:.3f})")
    
    print(f"\nStats: {vm.get_stats()}")
