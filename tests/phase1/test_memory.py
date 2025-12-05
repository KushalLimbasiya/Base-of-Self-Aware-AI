"""Phase 1 Tests - Memory Systems"""

import pytest
import sys
sys.path.insert(0, '../../src')

from atom.memory.memory_system import MemorySystem, ConversationTurn
from atom.memory.user_profile import UserProfileManager, UserProfile
from datetime import datetime


def test_memory_system_init():
    """Test memory system initialization."""
    memory = MemorySystem(db_path='data/test_phase1_memory.db')
    assert memory.working_memory is not None
    assert memory.long_term_memory is not None
    memory.close()


def test_store_conversation():
    """Test storing a conversation."""
    memory = MemorySystem(db_path='data/test_phase1_memory.db')
    turn = ConversationTurn(
        session_id='test_session',
        timestamp=datetime.now().isoformat(),
        user_input='test input',
        intent_tag='test',
        confidence=1.0,
        response='test response'
    )
    memory.store_conversation(turn)
    recent = memory.get_recent_conversations(limit=1)
    assert len(recent) >= 1
    memory.close()


def test_user_profile_creation():
    """Test user profile creation."""
    mgr = UserProfileManager(db_path='data/test_phase1_memory.db')
    profile = mgr.get_profile()
    assert profile is not None
    assert isinstance(profile, UserProfile)


def test_user_profile_save():
    """Test saving user profile."""
    mgr = UserProfileManager(db_path='data/test_phase1_memory.db')
    profile = mgr.get_profile()
    profile.user_name = "TestUser"
    profile.location = "TestCity"
    mgr.save_profile(profile)
    
    # Retrieve and verify
    loaded = mgr.get_profile()
    assert loaded.user_name == "TestUser"
    assert loaded.location == "TestCity"


if __name__ == "__main__":
    # Run tests manually
    print("Running Phase 1 Memory Tests...")
    
    try:
        test_memory_system_init()
        print("✓ Memory System Init Test Passed")
    except Exception as e:
        print(f"✗ Memory System Init Test Failed: {e}")
    
    try:
        test_store_conversation()
        print("✓ Store Conversation Test Passed")
    except Exception as e:
        print(f"✗ Store Conversation Test Failed: {e}")
    
    try:
        test_user_profile_creation()
        print("✓ User Profile Creation Test Passed")
    except Exception as e:
        print(f"✗ User Profile Creation Test Failed: {e}")
    
    try:
        test_user_profile_save()
        print("✓ User Profile Save Test Passed")
    except Exception as e:
        print(f"✗ User Profile Save Test Failed: {e}")
