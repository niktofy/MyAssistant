# voice.py
import sys
import os
import asyncio
import ctypes
import time

# Activăm encoding-ul UTF-8 pentru consolă ca să nu crape la diacritice românești
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stdin, 'reconfigure'):
    sys.stdin.reconfigure(encoding='utf-8')

# Încercăm să importăm edge-tts
try:
    import edge_tts
except ImportError:
    edge_tts = None

# Încercăm să importăm pyttsx3
try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

# Încercăm să importăm speech_recognition
try:
    import speech_recognition as sr
except ImportError:
    sr = None

# Configurații voci
EDGE_VOICE = "ro-RO-EmilNeural" # Voce neurală premium masculină
TEMP_AUDIO_FILE = "rick_speech_temp.mp3"

# Inițializare motor Text-to-Speech pyttsx3 (fallback offline)
pyttsx3_engine = None
if pyttsx3:
    try:
        pyttsx3_engine = pyttsx3.init()
        pyttsx3_engine.setProperty('rate', 175)
        pyttsx3_engine.setProperty('volume', 1.0)
        
        voices = pyttsx3_engine.getProperty('voices')
        ro_voice_found = False
        en_voice_id = None
        for voice in voices:
            if "english" in voice.name.lower() or "en-us" in voice.id.lower():
                en_voice_id = voice.id
            if "romanian" in voice.name.lower() or "ro-ro" in voice.id.lower() or "ro" in voice.languages:
                pyttsx3_engine.setProperty('voice', voice.id)
                ro_voice_found = True
                break
        
        if not ro_voice_found and en_voice_id:
            pyttsx3_engine.setProperty('voice', en_voice_id)
    except Exception:
        pyttsx3_engine = None

async def vorbeste_edge_async(text: str):
    """Corotină asincronă pentru generarea și redarea vocii prin Edge TTS."""
    if not edge_tts:
        raise ImportError("edge-tts nu este instalat")
    
    # Generează fișierul audio mp3
    communicate = edge_tts.Communicate(text, EDGE_VOICE)
    await communicate.save(TEMP_AUDIO_FILE)
    
    # Redă fișierul audio folosind Windows MCI (Media Control Interface) nativ
    abs_path = os.path.abspath(TEMP_AUDIO_FILE)
    try:
        # Descheiem fișierul în player
        ctypes.windll.winmm.mciSendStringW(f'open "{abs_path}" type mpegvideo alias rick_speech', None, 0, 0)
        # Redăm în mod blocant (wait) - se oprește exact când se termină sunetul
        ctypes.windll.winmm.mciSendStringW('play rick_speech wait', None, 0, 0)
        # Închidem player-ul pentru a elibera fișierul
        ctypes.windll.winmm.mciSendStringW('close rick_speech', None, 0, 0)
    finally:
        # Ștergem fișierul temporar
        if os.path.exists(TEMP_AUDIO_FILE):
            try:
                # O mică pauză ca să fim siguri că Windows a eliberat fișierul
                time.sleep(0.1)
                os.remove(TEMP_AUDIO_FILE)
            except Exception:
                pass

def vorbeste_pyttsx3_fallback(text: str):
    """Pronunță textul offline folosind pyttsx3."""
    if pyttsx3_engine:
        try:
            pyttsx3_engine.say(text)
            pyttsx3_engine.runAndWait()
        except Exception as e:
            print(f"Eroare fallback audio: {e}")

def vorbeste(text: str):
    """Pronunță textul oferit folosind Edge TTS premium, cu fallback pe pyttsx3."""
    if not text:
        return
        
    print(f"Rick (voce): {text}")
    
    if edge_tts:
        try:
            # Rulăm corotina asincronă în mod sincron
            asyncio.run(vorbeste_edge_async(text))
            return
        except Exception:
            # În caz de eroare (offline/probleme server), trecem la fallback
            pass
            
    vorbeste_pyttsx3_fallback(text)

def asculta() -> str:
    """Ascultă la microfon și returnează textul recunoscut în limba română."""
    if not sr:
        # Dacă biblioteca nu e instalată, cerem input la tastatură ca fallback
        return input("\nTu (tastatură): ")
        
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    recognizer.energy_threshold = 4000
    
    with sr.Microphone() as source:
        print("\n🎤 Ascult... (vorbește acum)")
        recognizer.adjust_for_ambient_noise(source, duration=0.8)
        
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
            print("⏳ Procesez vocea...")
            text = recognizer.recognize_google(audio, language="ro-RO")
            print(f"Ai spus: \"{text}\"")
            return text
            
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            print("Rick: Nu am înțeles clar ce ai spus. Poți repeta?")
            return ""
        except sr.RequestError as e:
            print(f"Rick: Serviciul de recunoaștere nu a răspuns: {e}")
            return input("\nTu (tastatură - fallback): ")
        except Exception as e:
            print(f"Eroare microfon: {e}")
            print("Asigură-te că ai instalat 'pyaudio' și că microfonul este conectat.")
            return input("\nTu (tastatură - fallback): ")

def semnal_activare():
    """Redă un semnal sonor dublu-beep (Jarvis style) pentru activare."""
    try:
        import winsound
        winsound.Beep(1000, 80)
        winsound.Beep(1400, 100)
    except Exception:
        pass

def semnal_dezactivare():
    """Redă un semnal sonor descendent pentru dezactivare/adormire."""
    try:
        import winsound
        winsound.Beep(1400, 80)
        winsound.Beep(900, 120)
    except Exception:
        pass

def detecteaza_cuvant_cheie(trigger_words=None) -> bool:
    """
    Ascultă în fundal și returnează True dacă detectează un cuvânt cheie de activare.
    Este optimizată pentru a fi rapidă și a nu bloca procesorul.
    """
    if trigger_words is None:
        trigger_words = ["rick", "ascultă", "asculta"]
        
    if not sr:
        return False
        
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    recognizer.energy_threshold = 2500 # Prag mai mic pentru sensibilitate mai mare la șoapte
    
    with sr.Microphone() as source:
        try:
            # Ascultă ferestre scurte de 2 secunde pentru reactivitate maximă
            audio = recognizer.listen(source, timeout=2, phrase_time_limit=2.5)
            text = recognizer.recognize_google(audio, language="ro-RO").lower().strip()
            
            # Verificăm dacă vreun cuvânt din trigger_words se regăsește în ce s-a spus
            for word in trigger_words:
                if word in text:
                    print(f"\n[Activare] S-a detectat: \"{text}\"")
                    return True
        except Exception:
            # Ignorăm erorile de timeout sau zgomot în standby ca să ascultăm continuu
            pass
            
    return False

# Test manual
if __name__ == "__main__":
    print("Testăm semnalele sonore...")
    semnal_activare()
    time.sleep(1)
    semnal_dezactivare()
    
    print("\nTestăm detecția cuvântului cheie. Spune 'Ascultă Rick'...")
    if detecteaza_cuvant_cheie():
        print("Succes! Cuvânt cheie detectat!")
        semnal_activare()
    else:
        print("Nu s-a detectat cuvântul cheie.")
