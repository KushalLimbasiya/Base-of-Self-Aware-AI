"""Phase 1 Tests - Vector Memory & RAG"""

import pytest
import sys
sys.path.insert(0, '../../src')

from atom.memory.vector_memory import VectorMemory
from atom.memory.rag_engine import RAGEngine
from atom.memory.user_profile import UserProfile


def test_vector_memory_init():
    """Test vector memory initialization."""
    vm = VectorMemory(persist_directory='data/test_phase1_vector')
    stats = vm.get_stats()
    assert stats['total_conversations'] >= 0


def test_vector_memory_add():
    """Test adding conversations to vector memory."""
    vm = VectorMemory(persist_directory='data/test_phase1_vector')
    vm.add_conversation(
        'test_1',
        'Hello',
        'Hi there!',
        {'test': True}
    )
    stats = vm.get_stats()
    assert stats['total_conversations'] >= 1


def test_vector_memory_search():
    """Test semantic search."""
    vm = VectorMemory(persist_directory='data/test_phase1_vector')
    results = vm.search_similar('greeting', n_results=1)
    # Should return results or empty list
    assert isinstance(results, list)


def test_rag_engine_init():
    """Test RAG engine initialization."""
    vm = VectorMemory(persist_directory='data/test_phase1_vector')
    rag = RAGEngine(vm)
    assert rag.vector_memory is not None


def test_rag_context_building():
    """Test RAG context building."""
    vm = VectorMemory(persist_directory='data/test_phase1_vector')
    rag = RAGEngine(vm)
    profile = UserProfile(user_name="Test", location="TestCity")
    context = rag.build_context("Hello", profile)
    assert isinstance(context, str)


if __name__ == "__main__":
    # Run tests manually
    print("Running Phase 1 RAG Tests...")
    
    try:
        test_vector_memory_init()
        print("✓ Vector Memory Init Test Passed")
    except Exception as e:
        print(f"✗ Vector Memory Init Test Failed: {e}")
    
    try:
        test_vector_memory_add()
        print("✓ Vector Memory Add Test Passed")
    except Exception as e:
        print(f"✗ Vector Memory Add Test Failed: {e}")
    
    try:
        test_vector_memory_search()
        print("✓ Vector Memory Search Test Passed")
    except Exception as e:
        print(f"✗ Vector Memory Search Test Failed: {e}")
    
    try:
        test_rag_engine_init()
        print("✓ RAG Engine Init Test Passed")
    except Exception as e:
        print(f"✗ RAG Engine Init Test Failed: {e}")
    
    try:
        test_rag_context_building()
        print("✓ RAG Context Building Test Passed")
    except Exception as e:
        print(f"✗ RAG Context Building Test Failed: {e}")
