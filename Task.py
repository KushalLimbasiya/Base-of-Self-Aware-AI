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
        song = query.replace('play', '')
        import pywhatkit
        Say('playing' + song)
        pywhatkit.playonyt(song)

    elif "wikipedia" in tag:
        name = str(query).replace("who is","").replace("about","").replace("what is","").replace("wikipedia","")
        import wikipedia
        name = wikipedia.summary(query,2)
        result = wikipedia.summary(name)
        Say(result)
            
    elif "google" in tag:
        query = str(query).replace("google","")
        query = query.replace("search","")
        import pywhatkit
        pywhatkit.search(query)

    
    

    

    
