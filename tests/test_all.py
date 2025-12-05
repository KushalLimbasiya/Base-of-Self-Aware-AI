"""
Simple All-in-One Test for Atom AI

Quick test to verify everything is working.
Run: python tests/test_all.py
"""

import asyncio
import sys
sys.path.insert(0, 'src')

from atom.core.llm_provider import UnifiedLLMProvider
from atom.memory.memory_system import MemorySystem
from atom.memory.user_profile import UserProfileManager
from atom.memory.vector_memory import VectorMemory


async def test_all():
    """Quick test of all major components."""
    print("\n" + "="*60)
    print("ATOM AI - Quick System Test")
    print("="*60)
    
    passed = 0
    total = 0
    
    # Test 1: LLM Provider
    print("\n[1/4] Testing LLM Provider...")
    total += 1
    try:
        llm = UnifiedLLMProvider(default_provider='groq')
        messages = [{"role": "user", "content": "Say 'test OK' in 2 words"}]
        response = await llm.generate(messages, max_tokens=50)
        print(f"  [OK] LLM Response: {response[:50]}...")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] LLM Failed: {e}")
    
    # Test 2: Memory System
    print("\n[2/4] Testing Memory System...")
    total += 1
    try:
        memory = MemorySystem(db_path='data/test_memory.db')
        memory.close()
        print("  [OK] Memory System OK")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] Memory Failed: {e}")
    
    # Test 3: User Profile
    print("\n[3/4] Testing User Profile...")
    total += 1
    try:
        profile_mgr = UserProfileManager(db_path='data/test_memory.db')
        profile = profile_mgr.get_profile()
        print(f"  [OK] Profile OK (User: {profile.user_name or 'Not set'})")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] Profile Failed: {e}")
    
    # Test 4: Vector Memory (RAG)
    print("\n[4/4] Testing Vector Memory...")
    total += 1
    try:
        vm = VectorMemory(persist_directory='data/test_vector')
        stats = vm.get_stats()
        print(f"  [OK] Vector Memory OK ({stats['total_conversations']} stored)")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] Vector Memory Failed: {e}")
    
    # Results
    print("\n" + "="*60)
    if passed == total:
        print(f"[PASS] ALL TESTS PASSED ({passed}/{total})")
        print("="*60 + "\n")
        return True
    else:
        print(f"[FAIL] SOME TESTS FAILED ({passed}/{total} passed)")
        print("="*60 + "\n")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(test_all())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted.")
        sys.exit(1)
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)
