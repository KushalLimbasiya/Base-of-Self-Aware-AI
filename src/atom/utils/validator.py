"""
Input validation and sanitization utilities for Atom.
Provides security against malicious inputs and data validation.
"""

import re
from atom.utils.logger import setup_logger

logger = setup_logger(__name__, 'atom.log')

def _get_max_length():
    """Get max input length from config, with fallback."""
    try:
        from atom.core.config import get_config
        return get_config().get('validation.max_input_length', 500)
    except:
        return 500

# Maximum allowed input length
MAX_INPUT_LENGTH = _get_max_length()

# Patterns that might indicate malicious input
DANGEROUS_PATTERNS = [
    r'[;&|`$]',  # Shell injection characters
    r'\.\./+',   # Path traversal
    r'<script',  # Script tags
    r'javascript:',  # JavaScript protocol
    r'eval\s*\(',  # Eval function
]

def sanitize_query(query):
    """
    Sanitize user input query string.
    
    Args:
        query: Raw user input string
        
    Returns:
        Sanitized query string or None if input is invalid
    """
    if not query or not isinstance(query, str):
        logger.warning("Invalid query: empty or not a string")
        return None
    
    # Strip whitespace
    query = query.strip()
    
    # Check length
    if len(query) > MAX_INPUT_LENGTH:
        logger.warning(f"Query too long: {len(query)} characters (max: {MAX_INPUT_LENGTH})")
        return None
    
    # Check for dangerous patterns
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, query, re.IGNORECASE):
            logger.warning(f"Potentially dangerous pattern detected in query: {pattern}")
            return None
    
    # Remove any null bytes
    query = query.replace('\x00', '')
    
    return query


def validate_intent_tag(tag, valid_tags):
    """
    Validate that the intent tag is in the list of valid tags.
    
    Args:
        tag: Intent tag from model prediction
        valid_tags: List of valid intent tags
        
    Returns:
        True if valid, False otherwise
    """
    if tag not in valid_tags:
        logger.error(f"Invalid intent tag: {tag}")
        return False
    return True


def sanitize_search_query(query):
    """
    Sanitize search queries for Wikipedia, Google, YouTube.
    More permissive than general query sanitization.
    
    Args:
        query: Search query string
        
    Returns:
        Sanitized search query or None if invalid
    """
    if not query or not isinstance(query, str):
        return None
    
    query = query.strip()
    
    # Check length
    if len(query) > MAX_INPUT_LENGTH or len(query) < 1:
        logger.warning(f"Search query length invalid: {len(query)}")
        return None
    
    # Remove dangerous characters but allow most punctuation for searches
    dangerous_chars = ['\x00', ';', '|', '`', '$', '&&']
    for char in dangerous_chars:
        query = query.replace(char, '')
    
    return query


def validate_confidence(confidence, threshold=0.75):
    """
    Validate model confidence score.
    
    Args:
        confidence: Model confidence score (0-1)
        threshold: Minimum acceptable confidence
        
    Returns:
        True if confidence meets threshold, False otherwise
    """
    if not isinstance(confidence, (int, float)):
        logger.error(f"Invalid confidence type: {type(confidence)}")
        return False
    
    if confidence < 0 or confidence > 1:
        logger.error(f"Confidence out of range: {confidence}")
        return False
    
    if confidence < threshold:
        logger.info(f"Confidence {confidence:.2f} below threshold {threshold}")
        return False
    
    return True
