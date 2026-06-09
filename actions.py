# actions.py
import os
import sys
import webbrowser
import subprocess

# Activăm encoding-ul UTF-8 pentru consolă ca să nu crape la diacritice românești
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stdin, 'reconfigure'):
    sys.stdin.reconfigure(encoding='utf-8')

from config import APPLICATIONS

def open_website(url: str) -> str:
    """Deschide un site web în browser-ul implicit."""
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    
    try:
        webbrowser.open(url)
        return f"Am deschis site-ul {url}."
    except Exception as e:
        return f"Eroare la deschiderea site-ului: {e}"

def find_shortcut(app_name: str) -> str:
    """
    Caută o comandă scurtătură (.lnk) pentru aplicație în Start Menu și pe Desktop.
    Returnează calea completă către scurtătură sau None dacă nu este găsită.
    """
    # Locațiile standard pe Windows pentru shortcut-uri
    search_dirs = [
        # Desktop-ul utilizatorului
        os.path.join(os.environ.get("USERPROFILE", "C:\\Users\\Glitch"), "Desktop"),
        # Desktop-ul utilizatorului redirectat prin OneDrive (foarte comun pe Windows)
        os.path.join(os.environ.get("USERPROFILE", "C:\\Users\\Glitch"), "OneDrive\\Desktop"),
        # Desktop-ul comun (Public)
        os.path.join(os.environ.get("PUBLIC", "C:\\Users\\Public"), "Desktop"),
        # Start Menu al utilizatorului curent
        os.path.join(os.environ.get("APPDATA", "C:\\Users\\Glitch\\AppData\\Roaming"), "Microsoft\\Windows\\Start Menu\\Programs"),
        # Start Menu global (al sistemului)
        os.path.join(os.environ.get("PROGRAMDATA", "C:\\ProgramData"), "Microsoft\\Windows\\Start Menu\\Programs")
    ]
    
    # Normalizăm numele căutat (eliminăm spațiile și facem litere mici)
    app_name_clean = app_name.lower().replace(" ", "")
    
    for base_dir in search_dirs:
        if not os.path.exists(base_dir):
            continue
        # Căutăm recursiv prin toate folderele
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.endswith(".lnk"):
                    file_clean = file.lower().replace(" ", "").replace(".lnk", "")
                    
                    # Căutăm potrivire exactă sau parțială a numelui
                    if app_name_clean == file_clean or app_name_clean in file_clean or file_clean in app_name_clean:
                        lnk_path = os.path.join(root, file)
                        return lnk_path
    return None

def open_app(app_name: str) -> str:
    """
    Deschide o aplicație locală.
    Caută întâi o scurtătură (.lnk) nativă în Windows, apoi o comandă din configurare.
    """
    app_name = app_name.lower().strip()
    
    # Tratăm cazul special pentru Antigravity (care este un proiect)
    if app_name == "antigravity":
        try:
            subprocess.Popen(APPLICATIONS["antigravity"], shell=True)
            return "Am deschis spațiul de lucru Antigravity în VS Code."
        except Exception as e:
            return f"Nu am putut deschide Antigravity: {e}"
            
    # Pasul 1: Căutăm dacă există o scurtătură (.lnk) pe Desktop sau în Start Menu
    lnk_path = find_shortcut(app_name)
    if lnk_path:
        try:
            # os.startfile acționează exact ca un dublu-click pe scurtătură
            os.startfile(lnk_path)
            return f"Am deschis aplicația prin scurtătura: {os.path.basename(lnk_path)}."
        except Exception as e:
            return f"Am găsit scurtătura '{os.path.basename(lnk_path)}', dar nu am putut-o lansa: {e}"
            
    # Pasul 2: Dacă nu s-a găsit o scurtătură, încercăm comanda înregistrată în config.py
    if app_name in APPLICATIONS:
        exe_name = APPLICATIONS[app_name]
        try:
            subprocess.Popen(exe_name, shell=True)
            return f"Am deschis aplicația {app_name} prin comandă înregistrată."
        except Exception as e:
            # Încercăm un ultim efort: să o rulăm cu comanda start din Windows
            try:
                subprocess.Popen(f"start {exe_name}", shell=True)
                return f"Am lansat {app_name} prin utilitarul Windows start."
            except Exception:
                return f"Nu am putut porni aplicația {app_name} prin comanda '{exe_name}': {e}"
                
    # Pasul 3: Dacă nu e în config și nu e nici scurtătură, încercăm să executăm numele direct
    try:
        subprocess.Popen(f"start {app_name}", shell=True)
        return f"Am încercat să lansez aplicația '{app_name}' direct din sistem."
    except Exception:
        return f"Aplicația '{app_name}' nu a putut fi găsită pe Desktop, în Start Menu sau prin comandă directă."

# Testare directă a modulului
if __name__ == "__main__":
    # Testăm căutarea
    print("Căutăm scurtătura pentru 'Brave'...")
    path = find_shortcut("brave")
    print(f"Găsit: {path}")
    
    print("\nÎncercăm să deschidem 'Brave'...")
    print(open_app("brave"))
