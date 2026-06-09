# test_mci_errors.py
import sys
import ctypes
import os
import asyncio

try:
    import edge_tts
except ImportError:
    print("edge-tts nu este instalat.")
    sys.exit(1)

# UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def get_mci_error(code):
    buf = ctypes.create_unicode_buffer(256)
    ctypes.windll.winmm.mciGetErrorStringW(code, buf, 256)
    return buf.value

async def main():
    text = "Test de erori."
    filename = "test_err.mp3"
    
    # Generează
    communicate = edge_tts.Communicate(text, "ro-RO-EmilNeural")
    await communicate.save(filename)
    
    abs_path = os.path.abspath(filename)
    print(f"Calea fișierului: {abs_path}")
    print(f"Există fișierul? {os.path.exists(abs_path)}")
    print(f"Dimensiune fișier: {os.path.getsize(abs_path)} bytes")
    
    # Deschiere
    c1 = ctypes.windll.winmm.mciSendStringW(f'open "{abs_path}" type mpegvideo alias errplayer', None, 0, 0)
    print(f"Cod Open: {c1} -> Mesaj: {get_mci_error(c1)}")
    
    # Redare
    c2 = ctypes.windll.winmm.mciSendStringW('play errplayer wait', None, 0, 0)
    print(f"Cod Play: {c2} -> Mesaj: {get_mci_error(c2)}")
    
    # Închidere
    c3 = ctypes.windll.winmm.mciSendStringW('close errplayer', None, 0, 0)
    print(f"Cod Close: {c3} -> Mesaj: {get_mci_error(c3)}")
    
    if os.path.exists(filename):
        os.remove(filename)

if __name__ == "__main__":
    asyncio.run(main())
