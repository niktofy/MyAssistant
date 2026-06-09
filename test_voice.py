# test_voice.py
import sys
import win32com.client
import pyttsx3

# Activăm encoding-ul UTF-8 pentru terminal ca să nu crape la diacritice românești
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

print("--- Testare pyttsx3 ---")
try:
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    print(f"Număr voci găsite în pyttsx3: {len(voices)}")
    for i, v in enumerate(voices):
        print(f"[{i}] Name: {v.name} | Lang: {v.languages} | ID: {v.id}")
    
    print("Încerc să vorbesc cu pyttsx3...")
    engine.say("Salut, testăm vocea locală cu pyttsx3.")
    engine.runAndWait()
    print("pyttsx3 a rulat fără erori.")
except Exception as e:
    print(f"Eroare pyttsx3: {e}")

print("\n--- Testare Native Windows SAPI5 (win32com) ---")
try:
    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    # Listează vocile disponibile în SAPI
    voices = speaker.GetVoices()
    print(f"Număr voci găsite în SAPI: {len(voices)}")
    for i in range(len(voices)):
        v = voices.Item(i)
        print(f"[{i}] Description: {v.GetDescription()}")
    
    print("Încerc să vorbesc cu SAPI direct...")
    speaker.Speak("Salut! Aceasta este vocea nativă din Windows SAPI.")
    print("SAPI a rulat fără erori.")
except Exception as e:
    print(f"Eroare SAPI nativ: {e}")
