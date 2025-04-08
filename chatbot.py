import requests

def generate_response(query, language="en"):
    try:
        response = requests.post("http://127.0.0.1:5000/query", json={"query": query}).json()
        return response
    except Exception as e:
        return {"response": f"Error: {str(e)}", "follow_up_needed": False}
import speech_recognition as sr  # Import SpeechRecognition

def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Sorry, I didn't understand that."
    except sr.RequestError:
        return "Error: Could not request results; check your internet connection."   



def text_to_speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()