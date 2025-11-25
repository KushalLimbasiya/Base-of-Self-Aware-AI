import datetime
from Speak import Say
from Logger import setup_logger
from Validator import sanitize_search_query

logger = setup_logger(__name__, 'jarvis.log')


def Time():
    time = datetime.datetime.now().strftime("%H:%M")
    logger.info(f"Reporting time: {time}")
    Say(time)

def Date():
    date = datetime.date.today()
    logger.info(f"Reporting date: {date}")
    Say(date)

def Day():
    day = datetime.datetime.now().strftime("%A")
    logger.info(f"Reporting day: {day}")
    Say(day)

def NonInputExecution(query):

    query = str(query)

    if "time" in query:
        Time()

    elif "date" in query:
        Date()

    elif "day" in query:
        Day()



def InputExecution(tag, query):
    
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
            Say('playing' + song)
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
            
    elif "google" in tag:
        try:
            search_query = sanitized_query.replace("google", "").replace("search", "").strip()
            if not search_query:
                Say("Please specify what to search for.")
                return
            import pywhatkit
            logger.info(f"Performing Google search for: {search_query}")
            pywhatkit.search(search_query)
        except Exception as e:
            logger.error(f"Error performing Google search: {e}")
            Say("Sorry, I couldn't perform the search.")

    
    

    

    
