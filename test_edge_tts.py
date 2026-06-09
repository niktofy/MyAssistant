# test_edge_tts.py
import sys
import asyncio
import ctypes
import os
import time

# UTF-8 encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

try:
    import edge_tts
    print("Edge TTS este instalat.")
except ImportError:
    print("Edge TTS NU este instalat. Te rog rulează: pip install edge-tts")
    sys.exit(1)

# Vocea neurală în limba română
VOICE = "ro-RO-EmilNeural"
TEXT = "Salut! Sunt Rick, asistentul tău personal. Acum mă auzi mult mai bine, nu-i așa?"
OUTPUT_FILE = "test_speech_mci.mp3"

async def generate_speech():
    print(f"Generez fișierul audio cu vocea '{VOICE}'...")
    communicate = edge_tts.Communicate(TEXT, VOICE)
    await communicate.save(OUTPUT_FILE)
    print("Audio generat cu succes!")

def play_audio_mci(filename):
    print("Redez fișierul audio folosind Windows MCI (Media Control Interface)...")
    abs_path = os.path.abspath(filename)
    try:
        # Descheiem/pregătim fișierul
        ctypes.windll.winmm.mciSendStringW(f'open "{abs_path}" type mpegvideo alias mp3player', None, 0, 0)
        # Redăm fișierul în mod blocant (wait) - se va opri automat când se termină sunetul
        ctypes.windll.winmm.mciSendStringW('play mp3player wait', None, 0, 0)
        # Închidem player-ul pentru a elibera resursele
        ctypes.windll.winmm.mciSendStringW('close mp3player', None, 0, 0)
        print("Redare finalizată.")
    except Exception as e:
        print(f"Eroare la redarea MCI: {e}")
    finally:
        # Ștergem fișierul temporar
        if os.path.exists(filename):
            try:
                os.remove(filename)
                print("Fișierul temporar a fost șters.")
            except Exception as e:
                print(f"Nu s-a putut șterge fișierul temporar: {e}")

if __name__ == "__main__":
    asyncio.run(generate_speech())
    play_audio_mci(OUTPUT_FILE)
