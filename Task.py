"""Task execution module for Jarvis.

This module handles executing various commands including:
- Time/date/day queries
- Wikipedia searches
- Web searches (enhanced with DuckDuckGo)
- YouTube video playback
"""

import datetime
from Speak import Say
from Logger import setup_logger
from Validator import sanitize_search_query
from WebSearch import WebSearch
from typing import Optional

logger = setup_logger(__name__, 'jarvis.log')

# Initialize web search module
web_search = WebSearch()


def Time():
    """Get and speak the current time.
   
    Formats current time as HH:MM (24-hour format) and speaks it.
    
    Example:
        >>> Time()
        # Speaks: "fourteen thirty" for 14:30
    """
    time = datetime.datetime.now().strftime("%H:%M")
    logger.info(f"Reporting time: {time}")
    Say(time)

def Date():
    """Get and speak the current date.
    
    Speaks the current date in YYYY-MM-DD format.
    
    Example:
        >>> Date()
        # Speaks: "2025-11-25"
    """
    date = datetime.date.today()
    logger.info(f"Reporting date: {date}")
    Say(date)

def Day():
    """Get and speak the current day of the week.
    
    Speaks the full day name (Monday, Tuesday, etc.).
    
    Example:
        >>> Day()
        # Speaks: "Monday"
    """
    day = datetime.datetime.now().strftime("%A")
    logger.info(f"Reporting day: {day}")
    Say(day)

def NonInputExecution(query):
    """Execute commands that don't require user input.
    
    Handles simple queries like time, date, and day that don't
    require additional parameters from the user.
    
    Args:
        query (str): The intent/command to execute
    
    Supported commands:
        - "time": Get current time
        - "date": Get current date  
        - "day": Get current day of week
    """

    query = str(query)

    if "time" in query:
        Time()

    elif "date" in query:
        Date()

    elif "day" in query:
        Day()



def InputExecution(tag, query):
    """Execute commands that require user input.
    
    Handles complex queries that need information from the user's
    voice input, such as search terms or video names. All inputs
    are sanitized before execution.
    
    Args:
        tag (str): The intent tag ('play', 'wikipedia', 'google', 'search')
        query (str): The user's raw input query
    
    Supported commands:
        - 'play': Play YouTube video
        - 'wikipedia': Search Wikipedia and read summary
        - 'google'/'search': Perform web search with results
    
    Returns:
        None: Function returns early if query is invalid
    
    Raises:
        Exceptions are caught and logged, with user feedback provided
    """
    
    # Sanitize the query before processing
    sanitized_query = sanitize_search_query(query)
    if not sanitized_query:
        logger.warning(f"Invalid search query rejected: {query}")
        Say("Sorry, that query is invalid.")
        return

    if 'play' in tag:
        try:
            song = sanitized_query.replace('play', '').strip()
            if not song:
                Say("Please specify what to play.")
                return
            import pywhatkit
            logger.info(f"Playing on YouTube: {song}")
            Say('playing ' + song)
            pywhatkit.playonyt(song)
        except Exception as e:
            logger.error(f"Error playing video: {e}")
            Say("Sorry, I couldn't play that video.")

    elif "wikipedia" in tag:
        try:
            name = sanitized_query.replace("who is", "").replace("about", "").replace("what is", "").replace("wikipedia", "").strip()
            if not name:
                Say("Please specify what to search for.")
                return
            import wikipedia
            logger.info(f"Searching Wikipedia for: {name}")
            result = wikipedia.summary(name, sentences=2)
            Say(result)
        except wikipedia.exceptions.DisambiguationError as e:
            logger.warning(f"Wikipedia disambiguation error: {e}")
            Say("There are multiple results. Please be more specific.")
        except wikipedia.exceptions.PageError:
            logger.warning(f"Wikipedia page not found: {name}")
            Say("Sorry, I couldn't find information about that.")
        except Exception as e:
            logger.error(f"Error fetching Wikipedia data: {e}")
            Say("Sorry, I encountered an error searching Wikipedia.")
            
    elif "google" in tag or "search" in tag:
        try:
            search_query = sanitized_query.replace("google", "").replace("search", "").strip()
            if not search_query:
                Say("Please specify what to search for.")
                return
            logger.info(f"Performing web search for: {search_query}")
            
            # Use WebSearch module for better results
            results = web_search.search(search_query, max_results=3)
            
            if results:
                # Get first result summary for quick answer
                summary = web_search.get_first_result_summary(results)
                if summary:
                    Say(summary)
                else:
                    # Fallback to opening browser
                    import pywhatkit
                    pywhatkit.search(search_query)
            else:
                Say("I couldn't find any results for that search.")
        except Exception as e:
            logger.error(f"Error performing web search: {e}")
            Say("Sorry, I couldn't perform the search.")


def WebSearchExecution(query: str) -> Optional[str]:
    """Execute a web search and return results.
    
    Performs web search using DuckDuckGo and speaks the results.
    
    Args:
        query: Search query string
    
    Returns:
        Summary of search results or None if search failed
    """
    sanitized_query = sanitize_search_query(query)
    if not sanitized_query:
        logger.warning(f"Invalid search query rejected: {query}")
        Say("Sorry, that query is invalid.")
        return None
    
    try:
        logger.info(f"Web search for: {sanitized_query}")
        results = web_search.search(sanitized_query, max_results=5)
        
        if results:
            # Get summary for speaking
            summary = web_search.get_summary(results, max_results=3)
            Say(summary)
            return summary
        else:
            Say("I couldn't find any results for that search.")
            return None
            
    except Exception as e:
        logger.error(f"Error in web search: {e}", exc_info=True)
        Say("Sorry, I encountered an error while searching.")
        return None
