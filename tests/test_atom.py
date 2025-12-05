"""
Atom AI - Comprehensive Test Suite with RAG

Updated to include Vector Memory and RAG Engine integration.
"""

import asyncio
import sys
import argparse
sys.path.insert(0, 'src')

from atom.core.llm_provider import UnifiedLLMProvider
from atom.memory.memory_system import MemorySystem, ConversationTurn
from atom.memory.user_profile import UserProfileManager
from atom.memory.vector_memory import VectorMemory
from atom.memory.rag_engine import RAGEngine
from atom.utils.name_detector import NameDetector
from atom.utils.personal_info_extractor import PersonalInfoExtractor
from datetime import datetime


class AtomTester:
    """Comprehensive test suite for Atom AI with RAG."""
    
    def __init__(self, test_db='data/memory_test.db', use_rag=True):
        # Initialize components
        self.llm = UnifiedLLMProvider(default_provider='groq')  # Use Groq as default (more stable)
        self.memory = MemorySystem(db_path=test_db)
        self.profile_mgr = UserProfileManager(db_path=test_db)
        self.name_detector = NameDetector()
        self.info_extractor = PersonalInfoExtractor()
        
        # Initialize RAG components
        self.use_rag = use_rag
        if use_rag:
            self.vector_memory = VectorMemory(persist_directory="data/vector_db")
            self.rag_engine = RAGEngine(self.vector_memory, self.memory)
            print(f"[RAG] Enabled with {self.vector_memory.get_stats()['total_conversations']} stored embeddings")
        else:
            self.vector_memory = None
            self.rag_engine = None
        
        self.test_results = []
    
    async def send_message(self, user_input: str, session_id: str) -> str:
        """Send message and get response with RAG."""
        profile = self.profile_mgr.get_profile()
        
        # Use RAG to build context if enabled
        if self.use_rag and self.rag_engine:
            messages = self.rag_engine.create_rag_prompt(user_input, profile)
        else:
            # Fallback to basic context
            recent_convos = self.memory.get_recent_conversations(limit=2)
            recent_memory = ""
            if recent_convos:
                recent_memory = "\n".join([
                    f"User: {turn.user_input}\nAtom: {turn.response}"
                    for turn in recent_convos[-2:]
                ])
            
            messages = self.llm.create_messages(
                user_input=user_input,
                user_profile=profile,
                recent_memory=recent_memory
            )
        
        # Generate response
        response = await self.llm.generate(messages, max_tokens=300)
        
        # Store in SQL memory
        turn = ConversationTurn(
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            user_input=user_input,
            intent_tag="conversation",
            confidence=1.0,
            response=response
        )
        self.memory.store_conversation(turn)
        
        # Store in vector memory
        if self.use_rag and self.vector_memory:
            self.vector_memory.add_conversation(
                conversation_id=f"{session_id}_{turn.timestamp}",
                user_input=user_input,
                response=response,
                metadata={"session_id": session_id}
            )
        
        # Detect and save user info
        detected_name = self.name_detector.extract_name(user_input)
        if detected_name and not profile.user_name:
            profile.user_name = detected_name
            self.profile_mgr.save_profile(profile)
            print(f"      [OK] Name saved: {detected_name}")
        
        info = self.info_extractor.extract_all(user_input)
        if info:
            if info.get('location') and not profile.location:
                profile.location = info['location']
                self.profile_mgr.save_profile(profile)
                print(f"      [OK] Location saved: {info['location']}")
            
            if info.get('interests'):
                for interest in info['interests']:
                    if interest not in profile.interests:
                        profile.interests.append(interest)
                        print(f"      [OK] Interest saved: {interest}")
                if info.get('interests'):
                    self.profile_mgr.save_profile(profile)
        
        # Update conversation count
        profile.total_conversations += 1
        profile.last_interaction = datetime.now().isoformat()
        if not profile.first_interaction:
            profile.first_interaction = profile.last_interaction
        self.profile_mgr.save_profile(profile)
        
        return response
    
    async def test_basic_llm(self):
        """Test 1: Basic LLM functionality."""
        print("\n" + "="*70)
        print("TEST 1: Basic LLM Provider")
        print("="*70)
        
        messages = [
            {"role": "system", "content": "You are Atom, a helpful assistant."},
            {"role": "user", "content": "Say hello in one sentence."}
        ]
        
        print("\n  Testing LLM generation...")
        try:
            response = await self.llm.generate(messages)
            print(f"  Response: {response[:80]}...")
            print("  [PASS] Basic LLM test")
            return True
        except Exception as e:
            print(f"  [FAIL] Error: {e}")
            return False
    
    async def test_rag_search(self):
        """Test 2: RAG semantic search."""
        if not self.use_rag:
            print("\n  [SKIP] RAG disabled")
            return True
        
        print("\n" + "="*70)
        print("TEST 2: RAG Semantic Search")
        print("="*70)
        
        # Add test conversations
        session_id = f"rag_test_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        test_convos = [
            ("What's the weather like?", "I don't have real-time weather data."),
            ("Tell me about Python", "Python is a high-level programming language."),
            ("How's Mumbai?", "Mumbai is a coastal city in India.")
        ]
        
        print("\n  Adding test conversations to vector memory...")
        for user_input, response in test_convos:
            self.vector_memory.add_conversation(
                f"test_{len(test_convos)}",
                user_input,
                response
            )
        
        # Test search
        print("\n  Testing semantic search...")
        query = "How's the climate today?"
        results = self.vector_memory.search_similar(query, n_results=2)
        
        if results:
            print(f"  Query: '{query}'")
            for result in results:
                print(f"    - Found: '{result['user_input']}' (similarity: {1-result['distance']:.2f})")
            print("  [PASS] RAG semantic search working")
            return True
        else:
            print("  [FAIL] No results found")
            return False
    
    async def run_all_tests(self):
        """Run complete test suite."""
        print("\n" + "="*70)
        print("ATOM AI - COMPREHENSIVE TEST SUITE WITH RAG")
        print("="*70)
        print(f"\nProvider: {self.llm.default_provider}")
        print(f"Available: {', '.join(self.llm.available_providers)}")
        print(f"RAG: {'Enabled' if self.use_rag else 'Disabled'}")
        
        results = []
        
        # Run tests
        results.append(await self.test_basic_llm())
        results.append(await self.test_rag_search())
        
        # Summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        test_names = ["Basic LLM", "RAG Search"]
        for name, passed in zip(test_names, results):
            status = "[PASS]" if passed else "[FAIL]"
            print(f"{status} {name}")
        
        total_passed = sum(results)
        print(f"\nTotal: {total_passed}/{len(results)} tests passed")
        
        if self.use_rag:
            stats = self.vector_memory.get_stats()
            print(f"\nVector Memory: {stats['total_conversations']} conversations stored")
        
        print("\n" + "="*70)
        if total_passed == len(results):
            print("SUCCESS: All tests passed!")
        else:
            print(f"WARNING: {len(results) - total_passed} test(s) failed")
        print("="*70 + "\n")
        
        self.memory.close()
        return total_passed == len(results)


async def interactive_chat():
    """Interactive chat mode with RAG."""
    print("="*70)
    print("ATOM AI - Interactive Chat Mode (with RAG)")
    print("="*70)
    
    tester = AtomTester(test_db='data/memory.db', use_rag=True)
    session_id = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    profile = tester.profile_mgr.get_profile()
    print(f"\nUser: {profile.user_name or 'Not set'}")
    print(f"Conversations: {profile.total_conversations}")
    print("\nType your messages. Type 'bye' to exit.\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['bye', 'exit', 'quit']:
                print("\nAtom: Goodbye!")
                break
            
            # Show RAG context if available
            if tester.rag_engine:
                context_summary = tester.rag_engine.get_relevant_context_summary(user_input)
                if "Found" in context_summary:
                    print(f"\n[RAG Context: Using semantic search results]\n")
            
            response = await tester.send_message(user_input, session_id)
            print(f"Atom: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\nAtom: Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()
            break
    
    tester.memory.close()


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Atom AI Test Suite')
    parser.add_argument('--chat', action='store_true', help='Interactive chat mode')
    parser.add_argument('--no-rag', action='store_true', help='Disable RAG')
    args = parser.parse_args()
    
    if args.chat:
        await interactive_chat()
    else:
        tester = AtomTester(use_rag=not args.no_rag)
        success = await tester.run_all_tests()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

