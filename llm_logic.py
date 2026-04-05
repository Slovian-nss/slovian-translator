import json
import os

# --- KONFIGURACJA ---
DATABASE_FILE = "vuzor.json"
LEARNED_MODELS_FILE = "learned_models.json"

def load_json(file):
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

class ProtoSlavicLearner:
    def __init__(self):
        # Dane wzorcowe (statyczne)
        self.reference_data = load_json(DATABASE_FILE)
        # Baza nauczona (dynamiczna)
        self.learned_cache = load_json(LEARNED_MODELS_FILE)
        self.models = self._build_initial_models()

    def _build_initial_models(self):
        """Buduje bazę wiedzy na starcie."""
        models = {}
        # Łączymy dane wzorcowe z tym, czego algorytm już się nauczył
        all_entries = self.reference_data if isinstance(self.reference_data, list) else []
        
        for e in all_entries:
            tag = e.get("type and case", "")
            slov = e.get("slovian", "").strip()
            if not slov or '"' not in tag: continue
            
            lemma = tag.split('"')[1].strip().lower()
            case_key = f"{self._detect_number(tag)}_{self._detect_case(tag)}"
            
            if lemma not in models:
                models[lemma] = {}
            models[lemma][case_key] = slov
        
        # Nadpisujemy danymi "nauczonymi" przez użytkownika (wyższy priorytet)
        for lemma, forms in self.learned_cache.items():
            if lemma not in models: models[lemma] = {}
            models[lemma].update(forms)
            
        return models

    def _detect_case(self, t):
        t = t.lower()
        mapping = {"nominative": "nom", "genitive": "gen", "accusative": "acc", 
                   "locative": "loc", "dative": "dat", "instrumental": "ins"}
        for k, v in mapping.items():
            if k in t: return v
        return "nom"

    def _detect_number(self, t):
        return "pl" if "plural" in t.lower() else "sg"

    def find_best_match(self, polish_word):
        """Logika rozmytego dopasowania (Fuzzy Matching)."""
        w = polish_word.lower()
        best_lemma = None
        min_dist = float("inf")
        
        for lemma in self.models:
            # Uproszczona odległość Levenshteina dla rdzeni
            dist = sum(1 for a, b in zip(w, lemma) if a != b) + abs(len(w) - len(lemma))
            if dist < min_dist:
                min_dist = dist
                best_lemma = lemma
        
        return best_lemma if min_dist < 3 else None

    def translate(self, polish_word, case, number):
        lemma = self.find_best_match(polish_word)
        if not lemma:
            return "●"
        
        key = f"{number}_{case}"
        return self.models[lemma].get(key, "●")

    def teach(self, polish_word, correct_slovian, case, number):
        """Metoda nauki - wywoływana, gdy użytkownik poprawi algorytm."""
        lemma = self.find_best_match(polish_word) or polish_word.lower()
        key = f"{number}_{case}"
        
        if lemma not in self.learned_cache:
            self.learned_cache[lemma] = {}
        
        self.learned_cache[lemma][key] = correct_slovian
        save_json(LEARNED_MODELS_FILE, self.learned_cache)
        # Odśwież modele w pamięci RAM
        self.models = self._build_initial_models()
        print(f"DEBUG: Nauczono formy '{correct_slovian}' dla lematu '{lemma}' ({key})")

# --- LOGIKA PRZETWARZANIA ZDANIA ---

PREP_MAP = {
    "w": ("loc", "vъ"), "do": ("gen", "do"), "na": ("loc", "na"),
    "o": ("loc", "o"),  "k": ("dat", "kъ"),  "u": ("gen", "u")
}

def process_sentence(learner, text):
    tokens = text.lower().split()
    result = []
    i = 0
    while i < len(tokens):
        word = tokens[i]
        
        # Obsługa przyimków
        if word in PREP_MAP:
            case, sl_prep = PREP_MAP[word]
            result.append(sl_prep)
            if i + 1 < len(tokens):
                # Prymitywne wykrywanie liczby
                num = "pl" if tokens[i+1].endswith(("y","i","ami","ach")) else "sg"
                result.append(learner.translate(tokens[i+1], case, num))
                i += 1
        elif word in ("z", "ze"):
            # Specyficzna logika dla prasłowiańskiego 'jiz' / 'sъ'
            if i + 1 < len(tokens):
                next_w = tokens[i+1]
                case, prep = ("ins", "sъ") if next_w.endswith(("em", "ą", "ami")) else ("gen", "jiz")
                num = "pl" if next_w.endswith(("y","i","ami")) else "sg"
                result.append(prep)
                result.append(learner.translate(next_w, case, num))
                i += 1
        else:
            result.append(learner.translate(word, "nom", "sg"))
        i += 1
    return " ".join(result)

# --- TESTY ---
if __name__ == "__main__":
    brain = ProtoSlavicLearner()
    
    # 1. Próba tłumaczenia
    print("Przed nauką:", process_sentence(brain, "W domu"))
    
    # 2. Algorytm się myli lub nie wie (zwraca ●), więc go uczymy
    # Zakładamy, że użytkownik wprowadza poprawną formę naukową:
    brain.teach("domu", "domou", "loc", "sg")
    
    # 3. Kolejna próba - algorytm już pamięta
    print("Po nauce:", process_sentence(brain, "W domu"))
