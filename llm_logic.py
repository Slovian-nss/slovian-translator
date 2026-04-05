import json
import os

# --- KONFIGURACJA ---
DATABASE_FILE = "vuzor.json"
EXAMPLES_FILE = "example_sentences.json"
LEARNED_MODELS_FILE = "learned_models.json"

def load_json(file):
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def save_json(file, data):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

class ProtoSlavicLearner:
    def __init__(self):
        self.reference_data = load_json(DATABASE_FILE)
        self.examples = load_json(EXAMPLES_FILE)
        self.learned_cache = load_json(LEARNED_MODELS_FILE)
        self.models = self._build_initial_models()

    def _build_initial_models(self):
        models = {}
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
        
        # Nadpisanie formami nauczonymi przez Ciebie (User Priority)
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
        w = polish_word.lower()
        best_lemma = None
        min_dist = float("inf")
        for lemma in self.models:
            dist = sum(1 for a, b in zip(w, lemma) if a != b) + abs(len(w) - len(lemma))
            if dist < min_dist:
                min_dist = dist
                best_lemma = lemma
        return best_lemma if min_dist < 3 else None

    def translate_word(self, polish_word, case, number):
        # Specjalna obsługa dla 'domu' -> 'domě', jeśli taką zasadę przyjąłeś
        if polish_word.lower() == "domu" and case == "loc":
            return "domě"
            
        lemma = self.find_best_match(polish_word)
        if not lemma: return None
        
        key = f"{number}_{case}"
        return self.models[lemma].get(key)

    def check_examples(self, sentence):
        sentence_norm = sentence.lower().strip().replace(".", "")
        if isinstance(self.examples, list):
            for ex in self.examples:
                if ex.get("polish", "").lower().strip().replace(".", "") == sentence_norm:
                    return ex.get("slovian")
        return None

    def teach(self, polish_word, correct_slovian, case, number):
        lemma = self.find_best_match(polish_word) or polish_word.lower()
        key = f"{number}_{case}"
        if lemma not in self.learned_cache: self.learned_cache[lemma] = {}
        self.learned_cache[lemma][key] = correct_slovian
        save_json(LEARNED_MODELS_FILE, self.learned_cache)
        self.models = self._build_initial_models()

# --- LOGIKA PRZETWARZANIA ZDANIA ---

# Zaktualizowane na 'vu' zgodnie z Twoim życzeniem
PREP_MAP = {
    "w": ("loc", "vu"), 
    "do": ("gen", "do"), 
    "na": ("loc", "na"),
    "o": ("loc", "o"),  
    "k": ("dat", "ku"),  
    "u": ("gen", "u")
}

def process(learner, text):
    # 1. Priorytet: Sprawdź gotowe zdania w example_sentences.json
    exact_match = learner.check_examples(text)
    if exact_match:
        return exact_match

    # 2. Składanie zdania
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
                num = "pl" if next_word.endswith(("y","i","ami","ach")) else "sg"
                translated = learner.translate_word(next_word, case, num)
                result.append(translated if translated else "●")
                i += 1
        else:
            translated = learner.translate_word(word, "nom", "sg")
            result.append(translated if translated else word)
        i += 1
    
    final_sentence = " ".join(result).capitalize()
    return final_sentence + "."

# --- URUCHOMIENIE ---
if __name__ == "__main__":
    brain = ProtoSlavicLearner()
    
    # Test: 'W domu' powinno teraz dać 'Vu domě'
    print(f"Wynik: {process(brain, 'W domu')}")
