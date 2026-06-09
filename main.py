# main.py
import os
import sys

# Activăm encoding-ul UTF-8 pentru consolă ca să nu crape la diacritice românești
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stdin, 'reconfigure'):
    sys.stdin.reconfigure(encoding='utf-8')

from rick_brain import ask_rick
from actions import open_website, open_app
from config import ASSISTANT_NAME
from voice import vorbeste, asculta, semnal_activare, semnal_dezactivare, detecteaza_cuvant_cheie

# Coduri de culori ANSI pentru un terminal mai interactiv și plăcut (ADHD friendly)
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    DARK_GRAY = '\033[90m'

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    clear_terminal()
    
    print(f"{Colors.HEADER}{Colors.BOLD}==================================================")
    print(f"       🤖 {ASSISTANT_NAME} - Asistentul Tău Personal Windows 🤖")
    print(f"=================================================={Colors.ENDC}\n")
    
    # Selectare mod de operare la pornire (ADHD friendly, simplu)
    mod = input(f"{Colors.BOLD}Alege modul: Tastatură (T) sau Voce (V):{Colors.ENDC} ").strip().lower()
    use_voice = (mod == 'v')
    
    clear_terminal()
    print(f"{Colors.HEADER}{Colors.BOLD}==================================================")
    print(f"       🤖 {ASSISTANT_NAME} - Asistentul Tău Personal Windows 🤖")
    print(f"=================================================={Colors.ENDC}\n")
    
    start_msg = "Sistem online. Sunt pregătit. Cu ce te pot ajuta?"
    print(f"{Colors.GREEN}{ASSISTANT_NAME}:{Colors.ENDC} {start_msg}")
    vorbeste(start_msg)
    if not use_voice:
        print(f"{Colors.DARK_GRAY}(Scrie 'exit' sau 'stop' pentru a închide){Colors.ENDC}\n")
    
    # Istoricul conversației limitat pentru context
    history = []
    max_history_turns = 5 # Păstrăm ultimele 5 interacțiuni
    
    while True:
        try:
            # Preluare comandă (Voce vs Tastatură)
            if use_voice:
                # Starea de Așteptare (Standby) - ascultăm cuvântul cheie "Ascultă Rick" sau "Rick"
                print(f"{Colors.DARK_GRAY}[Așteptare: Spune \"Ascultă Rick\" ca să mă activezi...]{Colors.ENDC}", end="\r")
                if not detecteaza_cuvant_cheie():
                    continue
                
                # Semnal de activare (double-beep)
                semnal_activare()
                
                # Ascultăm comanda propriu-zisă
                user_input = asculta()
                
                # Dacă utilizatorul nu a spus nimic, redăm semnalul de adormire și ne întoarcem în standby
                if not user_input:
                    semnal_dezactivare()
                    continue
            else:
                user_input = input(f"{Colors.CYAN}{Colors.BOLD}Tu:{Colors.ENDC} ").strip()
                if not user_input:
                    continue
                
            if user_input.lower() in ["exit", "stop", "inchide", "pa"]:
                goodbye_msg = "Am plecat. O zi productivă în continuare!"
                print(f"\n{Colors.GREEN}{ASSISTANT_NAME}:{Colors.ENDC} {goodbye_msg}")
                vorbeste(goodbye_msg)
                if use_voice:
                    semnal_dezactivare()
                break
            
            # Afișăm în consolă ce a spus dacă suntem pe modul voce
            if use_voice:
                print(f"{Colors.CYAN}{Colors.BOLD}Tu (Voce):{Colors.ENDC} {user_input}")
                
            print(f"{Colors.DARK_GRAY}* {ASSISTANT_NAME} se gândește... *{Colors.ENDC}", end="\r")
            
            # Apelăm creierul asistentului
            result = ask_rick(user_input, history)
            
            # Ștergem linia de gândire pentru un aspect curat
            sys.stdout.write("\033[K")
            
            # Afișăm gândurile asistentului în mod discret (debug/context)
            if "thought" in result and result["thought"]:
                print(f"{Colors.DARK_GRAY}[Gând: {result['thought']}]{Colors.ENDC}")
            
            # Rick răspunde text/vocal
            speech = result.get("speech", "Nu știu ce să spun la asta.")
            print(f"{Colors.GREEN}{Colors.BOLD}{ASSISTANT_NAME}:{Colors.ENDC} {speech}")
            
            vorbeste(speech)
            
            # Executăm acțiunea decisă de Rick
            action = result.get("action")
            params = result.get("params", {})
            
            action_result = None
            if action == "open_website" and "url" in params:
                url = params["url"]
                print(f"{Colors.BLUE}➔ Rulăm acțiunea: Deschide site-ul {url}...{Colors.ENDC}")
                action_result = open_website(url)
            elif action == "open_app" and "app_name" in params:
                app = params["app_name"]
                print(f"{Colors.BLUE}➔ Rulăm acțiunea: Deschide aplicația {app}...{Colors.ENDC}")
                action_result = open_app(app)
            
            if action_result:
                print(f"{Colors.DARK_GRAY}({action_result}){Colors.ENDC}")
            
            # Adăugăm în istoricul conversației
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": speech})
            
            # Limităm lungimea istoricului pentru a nu depăși contextul LLM-ului
            if len(history) > max_history_turns * 2:
                history = history[-(max_history_turns * 2):]
                
            print() # Linie goală pentru lizibilitate
            
        except KeyboardInterrupt:
            exit_msg = "Închidere forțată. O zi bună!"
            print(f"\n{Colors.GREEN}{ASSISTANT_NAME}:{Colors.ENDC} {exit_msg}")
            vorbeste(exit_msg)
            break
        except Exception as e:
            print(f"\n{Colors.FAIL}Eroare în bucla principală: {e}{Colors.ENDC}\n")

if __name__ == "__main__":
    # Activăm culorile ANSI pe Windows în mod corect
    if os.name == 'nt':
        os.system('')
    main()
