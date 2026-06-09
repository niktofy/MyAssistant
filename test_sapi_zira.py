# test_sapi_zira.py
import win32com.client
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

try:
    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    voices = speaker.GetVoices()
    
    # Găsim indexul pentru Zira
    zira_index = None
    for i in range(len(voices)):
        desc = voices.Item(i).GetDescription()
        print(f"Voce [{i}]: {desc}")
        if "zira" in desc.lower():
            zira_index = i
            
    if zira_index is not None:
        print(f"Setăm vocea pe Zira (index {zira_index})...")
        speaker.Voice = voices.Item(zira_index)
        print("Vorbesc prin SAPI cu Zira...")
        speaker.Speak("Hello! This is Zira. Testing if you can hear my voice.")
        speaker.Speak("Salut! Sunt Zira și citesc textul în limba română.")
        print("Test SAPI Zira finalizat.")
    else:
        print("Nu s-a găsit vocea Zira în sistem.")
except Exception as e:
    print(f"Eroare SAPI: {e}")
