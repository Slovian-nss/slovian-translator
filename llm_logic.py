import json
import os
import re

# --- KONFIGURACJA ---
DATABASE_FILE = "vuzor.json"
LEARNED_MODELS_FILE = "learned_models.json"

def load_json(file):
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                return data if isinstance(data, list) else []
            except: return []
    return []

class ProtoSlavicLearner:
    def __init__(self):
        self.raw_data = load_json(DATABASE_FILE)
        self.learned_cache = load_json(LEARNED_MODELS_FILE)
        self.endings_rules = self._derive_rules()

    def _detect_case(self, t):
        t = t.lower()
        mapping = {"nominative": "nom", "genitive": "gen", "accusative": "acc", 
                   "locative": "loc", "dative": "dat", "instrumental": "ins"}
        for k, v in mapping.items():
            if k in t: return v
        return "nom"

    def _detect_number(self, t):
        return "pl" if "plural" in t.lower() else "sg"

    def _derive_rules(self):
        """Analizuje vuzor.json, aby nauczyć się końcówek dla danych przypadków."""
        rules = {} # Format: { "loc_sg": [listy końcówek] }
        
        for e in self.raw_data:
            tag = e.get("type and case", "")
            slov = e.get("slovian", "").strip().lower()
            if not slov or '"' not in tag: continue
            
            lemma = tag.split('"')[1].strip().lower()
            case_key = f"{self._detect_number(tag)}_{self._detect_case(tag)}"
            
            # Ekstrakcja końcówki: jeśli slovian to 'domě', a lemma to 'dom', końcówka = 'ě'
            if slov.startswith(lemma[:-1]): # dopasowanie rdzenia (minus ostatnia litera dla bezpieczeństwa)
                common_part = os.path.commonprefix([lemma, slov])
                ending = slov[len(common_part):]
                
                if case_key not in rules: rules[case_key] = {}
                rules[case_key][ending] = rules[case_key].get(ending, 0) + 1
        
        return rules

    def get_best_ending(self, case_key):
        """Zwraca najczęstszą końcówkę z bazy dla danego przypadku."""
        if case_key in self.endings_rules:
            # Sortuj końcówki według popularności w vuzor.json
            return max(self.endings_rules[case_key], key=self.endings_rules[case_key].get)
        return ""

    def decline(self, polish_word, case, number):
        # 1. Sprawdź czy słowo jest bezpośrednio w bazie (vuzor lub learned)
        case_key = f"{number}_{case}"
        for e in self.raw_data:
            tag = e.get("type and case", "")
            if polish_word.lower() in tag.lower() and self._detect_case(tag) == case:
                return e.get("slovian")

        # 2. Jeśli nie ma, stwórz na podstawie osnowy (najczęstszej końcówki z bazy)
        ending = self.get_best_ending(case_key)
        
        # Prosta heurystyka: bierzemy polskie słowo, odcinamy końcówkę i dajemy prasłowiańską
        stem = polish_word.lower()
        if len(stem) > 3:
            stem = re.sub(r'[aueioyąęó]$', '', stem) # Usuń polską samogłoskę końcową
            
        return stem + ending

# --- PROCESOR ZDANIA ---

PREP_MAP = {
    "w": ("loc", "vu"), 
    "do": ("gen", "do"), 
    "na": ("loc", "na"),
    "z": ("ins", "su")
}

def process(text):
    learner = ProtoSlavicLearner()
    tokens = text.lower().replace(".", "").split()
    result = []
    i = 0
    
    while i < len(tokens):
        word = tokens[i]
        if word in PREP_MAP:
            case, sl_prep = PREP_MAP[word]
            result.append(sl_prep)
            if i + 1 < len(tokens):
                next_word = tokens[i+1]
                num = "sg" # domyślnie
                result.append(learner.decline(next_word, case, num))
                i += 1
        else:
            # Szukaj mianownika w bazie
            res = learner.decline(word, "nom", "sg")
            result.append(res if res else word)
        i += 1
        
    return " ".join(result).capitalize() + "."

if __name__ == "__main__":
    # Przykład: Jeśli w vuzor.json 'dom' ma loc_sg 'domě', 
    # to 'ogród' (nieobecny w bazie) też dostanie końcówkę 'ě' -> 'ogrodě'
    print(process("W domu"))
