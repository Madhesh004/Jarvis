import time
import pyttsx3
import speech_recognition as sr
import eel
import os
import traceback

def speak(text):
    text = str(text)
    driver = 'sapi5' if os.name == 'nt' else None
    engine = pyttsx3.init(driver)
    voices = engine.getProperty('voices')
    # print(voices)
    if voices:
        voice_index = 2 if len(voices) > 2 else 0
        engine.setProperty('voice', voices[voice_index].id)
    try:
        eel.DisplayMessage(text)
    except Exception:
        pass
    engine.say(text)
    engine.runAndWait()
    engine.setProperty('rate', 174)
    try:
        eel.receiverText(text)
    except Exception:
        pass

# Expose the Python function to JavaScript

def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("I'm listening...")
        eel.DisplayMessage("I'm listening...")
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source, 10, 8)

    try:
        print("Recognizing...")
        eel.DisplayMessage("Recognizing...")
        query = r.recognize_google(audio, language='en-US')
        print(f"User said: {query}\n")
        eel.DisplayMessage(query)
        
        
        speak(query)
    except Exception as e:
        print(f"Error: {str(e)}\n")
        return None

    return query.lower()



@eel.expose
def takeAllCommands(message=None):
    if message is None:
        query = takecommand()  # If no message is passed, listen for voice input
        if not query:
            speak("I did not catch that. Please repeat the command.")
            eel.ShowHood()
            return
        print(query)
        eel.senderText(query)
    else:
        query = message  # If there's a message, use it
        print(f"Message received: {query}")
        eel.senderText(query)

    # Normalize incoming command for consistent keyword checks.
    query = str(query).strip().lower()
    
    try:
        if query:
            if "open" in query:
                from backend.feature import openCommand
                openCommand(query)
            elif "send message" in query or "call" in query or "video call" in query:
                from backend.feature import findContact, whatsApp
                flag = ""
                Phone, name = findContact(query)
                if Phone != 0:
                    if "send message" in query:
                        flag = 'message'
                        speak("What message to send?")
                        query = takecommand()  # Ask for the message text
                        if not query:
                            speak("I could not hear the message text.")
                            eel.ShowHood()
                            return
                    elif "call" in query:
                        flag = 'call'
                    else:
                        flag = 'video call'
                    whatsApp(Phone, query, flag, name)
            elif "on youtube" in query:
                from backend.feature import PlayYoutube
                PlayYoutube(query)
            elif "news" in query or "briefing" in query:
                from backend.feature import newsBriefing
                newsBriefing()
            else:
                from backend.feature import chatBot
                chatBot(query)
        else:
            speak("No command was given.")
    except Exception as e:
        print(f"An error occurred while handling command '{query}': {e}")
        traceback.print_exc()
        speak("Sorry, something went wrong.")
    
    eel.ShowHood()
