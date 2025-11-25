"""Personal Information Extractor for Atom.

Extracts personal information from conversational text including:
- Location (city, country)
- Occupation (job, profession)
- Interests (hobbies, topics of interest)
"""

import re
from typing import Optional, List
from Logger import setup_logger

logger = setup_logger(__name__, 'atom.log')


class PersonalInfoExtractor:
    """Extracts personal information from conversational text."""
    
    # Patterns for location
    LOCATION_PATTERNS = [
        r"(?:i live in|i'm from|i am from|i'm in|from)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        r"(?:my (?:home|city) is)\s+([A-Z][a-z]+)",
    ]
    
    # Patterns for occupation
    OCCUPATION_PATTERNS = [
        r"(?:i am a|i'm a|i work as|my job is)\s+(.+?)(?:\.|$|,)",
        r"(?:i'm an?|i am an?)\s+(\w+)",
    ]
    
    # Patterns for interests
    INTEREST_PATTERNS = [
        r"(?:i like|i love|i enjoy|i'm interested in)\s+(.+?)(?:\.|$|,)",
        r"(?:my (?:hobby|hobbies) (?:is|are))\s+(.+?)(?:\.|$|,)",
    ]
    
    def __init__(self):
        """Initialize extractor."""
        logger.debug("PersonalInfoExtractor initialized")
    
    def extract_location(self, text: str) -> Optional[str]:
        """Extract location mention from text.
        
        Args:
            text: Input text
            
        Returns:
            Location string or None
        """
        if not text:
            return None
        
        for pattern in self.LOCATION_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                location = match.group(1).strip().title()
                logger.info(f"Location detected: {location}")
                return location
        
        return None
    
    def extract_occupation(self, text: str) -> Optional[str]:
        """Extract occupation mention from text.
        
        Args:
            text: Input text
            
        Returns:
            Occupation string or None
        """
        if not text:
            return None
        
        text_lower = text.lower()
        
        for pattern in self.OCCUPATION_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                occupation = match.group(1).strip()
                # Clean up
                occupation = occupation.replace('a ', '').replace('an ', '')
                occupation = occupation.strip()
                
                if occupation and len(occupation) > 2:
                    logger.info(f"Occupation detected: {occupation}")
                    return occupation
        
        return None
    
    def extract_interests(self, text: str) -> List[str]:
        """Extract interest mentions from text.
        
        Args:
            text: Input text
            
        Returns:
            List of interests
        """
        if not text:
            return []
        
        interests = []
        text_lower = text.lower()
        
        for pattern in self.INTEREST_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                interest_text = match.group(1).strip()
                # Split by 'and' or commas
                items = re.split(r'\s+and\s+|,\s*', interest_text)
                
                for item in items:
                    item = item.strip()
                    if item and len(item) > 2:
                        interests.append(item)
        
        if interests:
            logger.info(f"Interests detected: {interests}")
        
        return interests
    
    def extract_all(self, text: str) -> dict:
        """Extract all personal information from text.
        
        Args:
            text: Input text
            
        Returns:
            Dict with location, occupation, interests
        """
        return {
            'location': self.extract_location(text),
            'occupation': self.extract_occupation(text),
            'interests': self.extract_interests(text)
        }


# Example usage and testing
if __name__ == "__main__":
    print("PersonalInfoExtractor Demo")
    print("=" * 50)
    
    extractor = PersonalInfoExtractor()
    
    # Test cases
    test_cases = [
        "I live in New York",
        "I'm from Tokyo",
        "I am a software engineer",
        "I work as a teacher",
        "I like programming and AI",
        "I love reading, hiking and photography",
        "I'm interested in machine learning",
        "My hobby is playing guitar",
    ]
    
    print("\nTesting information extraction:\n")
    for test in test_cases:
        info = extractor.extract_all(test)
        print(f"  '{test}'")
        if info['location']:
            print(f"    Location: {info['location']}")
        if info['occupation']:
            print(f"    Occupation: {info['occupation']}")
        if info['interests']:
            print(f"    Interests: {', '.join(info['interests'])}")
        if not any(info.values()) or not any(info['interests']):
            print(f"    (No info detected)")
        print()
    
    print("=" * 50)
    print("Demo complete!")
