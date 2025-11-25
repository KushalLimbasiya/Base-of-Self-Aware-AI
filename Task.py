import datetime
from Speak import Say



def Time():
    time = datetime.datetime.now().strftime("%H:%M")
    Say(time)

def Date():
    date = datetime.date.today()
    Say(date)

def Day():
    day = datetime.datetime.now().strftime("%A")
    Say(day)

def NonInputExecution(query):

    query = str(query)

    if "time" in query:
        Time()

    elif "date" in query:
        Date()

    elif "day" in query:
        Day()



def InputExecution(tag,query):

    if 'play' in tag:
        try:
            song = query.replace('play', '')
            import pywhatkit
            Say('playing' + song)
            pywhatkit.playonyt(song)
        except Exception as e:
            print(f"Error playing video: {e}")
            Say("Sorry, I couldn't play that video.")

    elif "wikipedia" in tag:
        try:
            name = str(query).replace("who is","").replace("about","").replace("what is","").replace("wikipedia","")
            import wikipedia
            result = wikipedia.summary(name, sentences=2)
            Say(result)
        except wikipedia.exceptions.DisambiguationError as e:
            print(f"Wikipedia disambiguation error: {e}")
            Say("There are multiple results. Please be more specific.")
        except wikipedia.exceptions.PageError:
            print(f"Wikipedia page not found: {name}")
            Say("Sorry, I couldn't find information about that.")
        except Exception as e:
            print(f"Error fetching Wikipedia data: {e}")
            Say("Sorry, I encountered an error searching Wikipedia.")
            
    elif "google" in tag:
        try:
            query = str(query).replace("google","")
            query = query.replace("search","")
            import pywhatkit
            pywhatkit.search(query)
        except Exception as e:
            print(f"Error performing Google search: {e}")
            Say("Sorry, I couldn't perform the search.")

    
    

    

    
