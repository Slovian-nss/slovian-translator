import json
from typing import Dict, Tuple, Optional

class SlovianDecliner:
    def __init__(self):
        with open('vuzor.json', encoding='utf-8') as f:
            self.vuzor = json.load(f)
        
        self.lookup: Dict[Tuple[str, str], str] = {}
        for entry in self.vuzor:
            polish = entry['polish'].lower()
            case_str = entry['type and case']
            self.lookup[(polish, case_str)] = entry['slovian']

    # === GŁÓWNA METODA: automatyczne odmienianie przez przypadek ===
    def decline(self, polish_word: str, case_name: str, number: str = "singular", 
                word_type: str = "noun", gender: str = None, context: str = None) -> Optional[str]:
        
        polish_lower = polish_word.lower()
        
        # 1. Najpierw próbujemy dokładny wpis z kontekstem
        if context:
            for e in self.vuzor:
                if (e['polish'].lower() == polish_lower and 
                    e.get('context', '').lower() == context.lower()):
                    base_case = e['type and case']
                    # Budujemy klucz przypadku
                    full_case = base_case.replace("poedinьna ličьba", 
                        "munoga ličьba" if number == "plural" else "poedinьna ličьba")
                    full_case = full_case.replace("jimenovьnik", case_name)  # zamiana na żądany przypadek
                    result = self.lookup.get((polish_lower, full_case))
                    if result:
                        return result

        # 2. Standardowe budowanie klucza przypadku
        num_str = "munoga ličьba" if number == "plural" else "poedinьna ličьba"
        
        if word_type == "noun":
            prefix = f"noun - jimenьnik: \"{polish_word}\" | "
            if gender is None:
                # Automatyczne zgadywanie na podstawie znanych wzorów
                if polish_word.lower().endswith('a'):
                    gender_part = "type feminine (inanimate) - rod'ajь ženьsky (neživotьny)"
                else:
                    gender_part = "type masculine (inanimate) - rod'ajь mǫžьsky (neživotьny)"
            else:
                gender_part = f"type {gender} - rod'ajь"
            
            case_key = f"{prefix}{case_name} | {num_str} | {gender_part}"
            
        elif word_type == "adjective":
            prefix = f"adjective - pridavьnik: \"{polish_word}\" | "
            g = gender or "masculine"
            gender_part = f"type {g} - rod'ajь mǫžьsky" if g == "masculine" else \
                          f"type {g} - rod'ajь ženьsky" if g == "feminine" else \
                          f"type {g} - rod'ajь nijaky"
            case_key = f"{prefix}{case_name} | {num_str} | {gender_part}"
        
        else:
            return None

        # Szukanie dokładnego dopasowania
        result = self.lookup.get((polish_lower, case_key))
        if result:
            return result

        # Fallback: szukanie podobnego przypadku (np. tylko zmiana liczby lub przypadku)
        for key, val in self.lookup.items():
            if key[0] == polish_lower and case_name in key[1] and num_str in key[1]:
                return val

        return None  # Nie znaleziono formy

# ===================== PRZYKŁAD UŻYCIA =====================
decliner = SlovianDecliner()

# Testy
print(decliner.decline("ogród", "městьnik", "singular", "noun", context="garden"))   # → vu ogrodě / vu obgordě
print(decliner.decline("obietnica", "vinьnik", "singular"))                       # → obětьnicǫ
print(decliner.decline("równy", "vinьnik", "singular", "adjective", "feminine")) # → orvьnǫ
