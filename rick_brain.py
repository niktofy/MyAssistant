# rick_brain.py
import requests
import json
import re
from config import LM_STUDIO_URL, LLM_MODEL, SYSTEM_PROMPT

def clean_json_response(raw_response: str) -> dict:
    """
    Curăță răspunsul de la modelul LLM pentru a extrage un obiect JSON valid.
    Uneori LLM-ul adaugă tag-uri markdown de tip ```json sau alte caractere.
    """
    cleaned = raw_response.strip()
    
    # Elimină blocul markdown ```json ... ``` dacă există
    if cleaned.startswith("```"):
        # Caută prima acoladă și ultima acoladă
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(0)
            
    # Încercăm să curățăm textul din jurul JSON-ului dacă modelul a adăugat text introductiv
    if not cleaned.startswith("{"):
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(0)
        else:
            # Dacă tot nu începe cu {, încercăm să găsim doar de la prima acoladă
            first_brace = cleaned.find("{")
            if first_brace != -1:
                cleaned = cleaned[first_brace:]
    
    # Încercare de decodare normală
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        # Încercăm să auto-reparăm JSON-ul trunchiat adăugând acolade/ghilimele dacă lipsesc la final
        try:
            # Dacă lipsește doar acolada de închidere
            data = json.loads(cleaned + "}")
        except json.JSONDecodeError:
            try:
                # Dacă s-a tăiat în mijlocul valorii "speech" (lipsește ghilimeaua și acolada)
                data = json.loads(cleaned + '"}')
            except json.JSONDecodeError:
                # Dacă nu se poate repara, fallback pe text simplu
                return {
                    "thought": "Eroare la parsarea JSON. Am fallback-uit pe text simplu.",
                    "action": "talk",
                    "params": {},
                    "speech": raw_response
                }

    # Ne asigurăm că are cheile obligatorii
    if "action" not in data:
        data["action"] = "talk"
    if "params" not in data:
        data["params"] = {}
    if "speech" not in data:
        # Dacă lipsește speech dar avem thought, îl folosim
        data["speech"] = data.get("thought", raw_response)
        
    return data

def ask_rick(user_message: str, history: list = None) -> dict:
    """
    Trimite mesajul utilizatorului (și istoricul conversației) către LM Studio
    și returnează un dicționar cu acțiunea și răspunsul.
    """
    url = f"{LM_STUDIO_URL}/chat/completions"
    
    # Inițializăm lista de mesaje cu System Prompt-ul
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Adăugăm istoricul dacă există (pentru contextul conversației)
    if history:
        messages.extend(history)
        
    # Adăugăm mesajul curent
    messages.append({"role": "user", "content": user_message})
    
    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": 0.3, # Temperatură mai mică pentru răspunsuri determinate și stabile JSON
        "max_tokens": 256 # Limitează lungimea pentru a preveni trunchierea JSON-ului
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        raw_content = result['choices'][0]['message']['content']
        return clean_json_response(raw_content)
        
    except requests.exceptions.RequestException as e:
        return {
            "thought": "Eroare de conexiune.",
            "action": "talk",
            "params": {},
            "speech": f"Scuze, întâmpin probleme la conectarea cu LM Studio. Asigură-te că serverul local este pornit. Detalii eroare: {e}"
        }
    except Exception as e:
        return {
            "thought": "Eroare necunoscută.",
            "action": "talk",
            "params": {},
            "speech": f"A apărut o problemă neașteptată: {e}"
        }

# Test manual simplu
if __name__ == "__main__":
    print("Testăm conectarea la LM Studio cu o cerere simplă...")
    response_data = ask_rick("deschide google")
    print("Răspuns parsat de la Rick:")
    print(json.dumps(response_data, indent=2, ensure_ascii=False))
