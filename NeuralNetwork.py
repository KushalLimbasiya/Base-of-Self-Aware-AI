"""Natural language processing utilities for Atom.

This module provides NLP functions for tokenization, stemming,
and bag-of-words conversion used in intent classification.
"""

import numpy as np 
import nltk 
from nltk.stem.porter import PorterStemmer

Stemmer = PorterStemmer()


def _ensure_nltk_punkt() -> None:
    """Ensure the NLTK 'punkt' tokenizer resource is available.

    Some environments install the NLTK package without its data resources.
    This attempts a quiet download of 'punkt' when missing.
    """
    try:
        nltk.data.find("tokenizers/punkt")
        return
    except LookupError:
        pass

    # Best-effort auto-download (no-op if already present)
    try:
        nltk.download("punkt", quiet=True)
    except Exception:
        pass

    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError as e:
        raise LookupError(
            "NLTK resource 'punkt' not found. Install it with: "
            "python -c \"import nltk; nltk.download('punkt')\"\n"
            "If you're offline, download it on another machine and set NLTK_DATA to the folder."
        ) from e

def tokenize(sentence):
    """Tokenize a sentence into individual words.
    
    Uses NLTK's word_tokenize to split a sentence into a list of words
    and punctuation marks.
    
    Args:
        sentence (str): The sentence to tokenize
    
    Returns:
        list: List of tokens (words and punctuation)
    
    Example:
        >>> tokenize("Hello, how are you?")
        ['Hello', ',', 'how', 'are', 'you', '?']
    """
    _ensure_nltk_punkt()
    return nltk.word_tokenize(sentence)

def stem(word):
    """Reduce a word to its root form using Porter Stemmer.
    
    Converts words to lowercase and applies stemming to reduce
    different forms of a word to a common base form.
    
    Args:
        word (str): The word to stem
    
    Returns:
        str: The stemmed word in lowercase
    
    Example:
        >>> stem("running")
        'run'
        >>> stem("better")
        'better'
    """
    return Stemmer.stem(word.lower())

def bag_of_words(tokenized_sentence, words):
    """Convert tokenized sentence to bag-of-words vector.
    
    Creates a binary vector where each position represents whether
    a word from the vocabulary appears in the sentence.
    
    Args:
        tokenized_sentence (list): List of tokens from the sentence
        words (list): Vocabulary list (all possible words)
    
    Returns:
        np.ndarray: Binary numpy array of shape (len(words),)
                   where 1 indicates word presence, 0 indicates absence
    
    Example:
        >>> tokenized = ['hello', 'world']
        >>> vocab = ['hello', 'world', 'goodbye']
        >>> bag_of_words(tokenized, vocab)
        array([1., 1., 0.])
    """
    sentence_word = [stem(word) for word in tokenized_sentence]
    bag = np.zeros(len(words),dtype=np.float32)

    for idx , w in enumerate(words):
        if w in sentence_word:
            bag[idx] = 1

    return bag

