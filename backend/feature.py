# import playsound
# import eel


# @eel.expose
# def playAssistantSound():
#     music_dir = "frontend\\assets\\audio\\start_sound.mp3"
#     playsound(music_dir)


from compileall import compile_path
import os
import re
from shlex import quote
import struct
import subprocess
import time
import webbrowser
import eel
from hugchat import hugchat 
import pvporcupine
import pyaudio
import pyautogui
import pywhatkit as kit
try:
    import pygame
except Exception:
    pygame = None
from backend.command import speak
from backend.config import ASSISTANT_NAME
import sqlite3

from backend.helper import extract_yt_term, remove_words
conn = sqlite3.connect("jarvis.db")
cursor = conn.cursor()


def _ensure_command_tables():
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS sys_command(id integer primary key, name VARCHAR(100), path VARCHAR(1000))"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS web_command(id integer primary key, name VARCHAR(100), url VARCHAR(1000))"
    )
    conn.commit()
# Initialize pygame mixer
if pygame is not None:
    try:
        pygame.mixer.init()
    except Exception:
        pygame = None


def _project_path(*parts):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, *parts)

# Define the function to play sound
@eel.expose
def play_assistant_sound():
    sound_file = _project_path("frontend", "assets", "audio", "start_sound.mp3")
    if pygame is not None and os.path.exists(sound_file):
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()
    
    
def openCommand(query):
    _ensure_command_tables()

    # Normalize command text and remove assistant name/open keyword safely.
    query = str(query).lower().strip()
    assistant = ASSISTANT_NAME.lower().strip()
    if assistant:
        query = re.sub(rf"\b{re.escape(assistant)}\b", "", query).strip()
    query = re.sub(r"\bopen\b", "", query).strip()
    
    app_name = query.strip()

    if app_name != "":

        direct_web_map = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "gmail": "https://mail.google.com",
            "github": "https://github.com",
            "spotify": "https://open.spotify.com",
            "music": "https://open.spotify.com",
            "instagram": "https://www.instagram.com",
            "twitter": "https://www.twitter.com",
            "linkedin": "https://www.linkedin.com",
            "facebook": "https://www.facebook.com",
        }

        if app_name in direct_web_map:
            speak("Opening " + app_name)
            webbrowser.open(direct_web_map[app_name])
            return

        try:
            cursor.execute( 
                'SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
            results = cursor.fetchall()

            if len(results) != 0:
                speak("Opening "+query)
                if os.name == "nt":
                    os.startfile(results[0][0])
                else:
                    subprocess.run(["open", results[0][0]], check=False)

            elif len(results) == 0: 
                cursor.execute(
                'SELECT url FROM web_command WHERE name IN (?)', (app_name,))
                results = cursor.fetchall()
                
                if len(results) != 0:
                    speak("Opening "+query)
                    webbrowser.open(results[0][0])

                else:
                    speak("Opening "+query)
                    try:
                        if os.name == "nt":
                            os.system('start '+query)
                        else:
                            subprocess.run(["open", query], check=False)
                    except:
                        speak("not found")
        except Exception as e:
            print(f"openCommand error: {e}")
            speak("I could not open that right now.")


def PlayYoutube(query):
    search_term = extract_yt_term(query)
    speak("Playing "+search_term+" on YouTube")
    kit.playonyt(search_term)


def hotword():
    porcupine=None
    paud=None
    audio_stream=None
    try:
       
        # pre trained keywords    
        porcupine=pvporcupine.create(keywords=["jarvis","alexa"]) 
        paud=pyaudio.PyAudio()
        audio_stream=paud.open(rate=porcupine.sample_rate,channels=1,format=pyaudio.paInt16,input=True,frames_per_buffer=porcupine.frame_length)
        
        # loop for streaming
        while True:
            keyword=audio_stream.read(porcupine.frame_length)
            keyword=struct.unpack_from("h"*porcupine.frame_length,keyword)

            # processing keyword comes from mic 
            keyword_index=porcupine.process(keyword)

            # checking first keyword detetcted for not
            if keyword_index>=0:
                print("hotword detected")

                # pressing shorcut key win+j
                import pyautogui as autogui
                modifier = "win" if os.name == "nt" else "command"
                autogui.keyDown(modifier)
                autogui.press("j")
                time.sleep(2)
                autogui.keyUp(modifier)
                
    except:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if paud is not None:
            paud.terminate()


def findContact(query):
    
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'wahtsapp', 'video']
    query = remove_words(query, words_to_remove)

    try:
        query = query.strip().lower()
        cursor.execute("SELECT Phone FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
        results = cursor.fetchall()
        print(results[0][0])
        mobile_number_str = str(results[0][0])

        if not mobile_number_str.startswith('+91'):
            mobile_number_str = '+91' + mobile_number_str

        return mobile_number_str, query
    except:
        speak('not exist in contacts')
        return 0, 0
    
    
def whatsApp(Phone, message, flag, name):
    

    if flag == 'message':
        target_tab = 12
        jarvis_message = "message send successfully to "+name

    elif flag == 'call':
        target_tab = 7
        message = ''
        jarvis_message = "calling to "+name

    else:
        target_tab = 6
        message = ''
        jarvis_message = "staring video call with "+name


    # Encode the message for URL
    encoded_message = quote(message)
    print(encoded_message)
    # Construct the URL
    whatsapp_url = f"whatsapp://send?phone={Phone}&text={encoded_message}"

    # Construct the full command
    if os.name == "nt":
        full_command = f'start "" "{whatsapp_url}"'
        subprocess.run(full_command, shell=True)
    else:
        webbrowser.open(whatsapp_url)
    time.sleep(5)
    if os.name == "nt":
        subprocess.run(full_command, shell=True)
    else:
        webbrowser.open(whatsapp_url)
    
    pyautogui.hotkey('ctrl', 'f')

    for i in range(1, target_tab):
        pyautogui.hotkey('tab')

    pyautogui.hotkey('enter')
    speak(jarvis_message)


def newsBriefing():
    """Fetch and speak latest news headlines without authentication."""
    try:
        import requests
        # Using NewsAPI free endpoint (alternatively: BBC, Reuters, CNN)
        response = requests.get(
            "https://newsapi.org/v2/top-headlines",
            params={"country": "us", "pageSize": 5},
            timeout=5
        )
        if response.status_code == 200:
            articles = response.json().get('articles', [])
            if articles:
                speak("Here are today's top news headlines.")
                for idx, article in enumerate(articles[:3], 1):
                    headline = article.get('title', 'Headline unavailable')
                    speak(f"Number {idx}: {headline}")
                return "News briefing completed."
        # Fallback to Wikipedia trending or generic response
        speak("I could not fetch the news right now. Please check back later or try asking me something else.")
        return "News briefing unavailable."
    except Exception as e:
        print(f"newsBriefing error: {e}")
        speak("Unable to fetch news at the moment.")
        return "News briefing failed."


def chatBot(query):
    user_input = query.lower()
    try:
        cookie_path = _project_path("backend", "cookie.json")
        if not os.path.exists(cookie_path):
            raise FileNotFoundError(f"Missing cookie file: {cookie_path}")

        chatbot = hugchat.ChatBot(cookie_path=cookie_path)
        id = chatbot.new_conversation()
        chatbot.change_conversation(id)
        response = chatbot.chat(user_input)
        print(response)
        speak(response)
        return response
    except Exception as e:
        print(f"chatBot error: {e}")
        fallback = "I am unable to reach the online chat service right now. Please try an open or youtube command."
        speak(fallback)
        return fallback