"""Name Detection Module for Atom.

Extracts user names from conversational text using pattern matching.
Detects introduction phrases like "My name is X", "I am X", "Call me X".
"""

import re
from typing import Optional
from Logger import setup_logger

logger = setup_logger(__name__, 'atom.log')

# Common words that are NOT names (to avoid false positives)
COMMON_WORDS = {
    'here', 'there', 'about', 'going', 'working', 'playing', 'doing',
    'fine', 'good', 'great', 'okay', 'yes', 'no', 'sure', 'maybe',
    'hello', 'hi', 'hey', 'thanks', 'please', 'sorry', 'excuse',
    'time', 'date', 'day', 'week', 'month', 'year', 'today', 'tomorrow',
    'atom', 'jarvis', 'assistant', 'sir', 'user', 'person'
}


class NameDetector:
    """Detects and extracts user names from conversational text."""
    
    # Patterns for name introduction
    PATTERNS = [
        r"(?:my name is|i am called|call me|i'm)\s+(\w+)",
        r"(?:this is|name's?)\s+(\w+)",
        r"i'm\s+(\w+)",  # "I'm Alice"
    ]
    
    def __init__(self):
        """Initialize name detector."""
        logger.debug("NameDetector initialized")
    
    def extract_name(self, text: str) -> Optional[str]:
        """Extract user name from text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Extracted name or None if not found
        """
        if not text:
            return None
        
        text = text.lower().strip()
        
        # Try each pattern
        for pattern in self.PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                potential_name = match.group(1)
                
                # Validate the name
                if self._is_valid_name(potential_name):
                    # Capitalize properly
                    name = potential_name.capitalize()
                    logger.info(f"Name detected: {name}")
                    return name
                else:
                    logger.debug(f"Rejected potential name: {potential_name}")
        
        return None
    
    def _is_valid_name(self, word: str) -> bool:
        """Check if word is likely a valid name.
        
        Args:
            word: Word to validate
            
        Returns:
            True if likely a name, False otherwise
        """
        word_lower = word.lower()
        
        # Must be letters only
        if not word.isalpha():
            return False
        
        # Must be reasonable length
        if len(word) < 2 or len(word) > 20:
            return False
        
        # Must not be a common word
        if word_lower in COMMON_WORDS:
            return False
        
        return True
    
    def contains_name_pattern(self, text: str) -> bool:
        """Check if text contains a name introduction pattern.
        
        Args:
            text: Input text
            
        Returns:
            True if pattern found, False otherwise
        """
        if not text:
            return False
        
        text = text.lower()
        
        # Check for introduction keywords
        keywords = ['my name is', 'i am', 'call me', "i'm", 'this is']
        return any(keyword in text for keyword in keywords)


# Example usage and testing
if __name__ == "__main__":
    print("NameDetector Demo")
    print("=" * 50)
    
    detector = NameDetector()
    
    # Test cases
    test_cases = [
        "Hello, my name is Alice",
        "Hi! I am Bob",
        "You can call me Charlie",
        "I'm David",
        "This is Emma speaking",
        "My name is fine",  # Should reject "fine" as common word
        "I am going to the store",  # Should reject "going"
        "Call me anytime",  # Should reject "anytime"
        "I'm really happy",  # Should reject "really"
    ]
    
    print("\nTesting name detection:\n")
    for test in test_cases:
        name = detector.extract_name(test)
        result = name if name else "❌ No name detected"
        print(f"  '{test}'")
        print(f"    → {result}\n")
    
    print("=" * 50)
    print("Demo complete!")
