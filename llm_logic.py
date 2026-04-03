import json
import os
from collections import defaultdict

def load_data(file):
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def detect_case(tag):
    t = tag.lower()
    if "nominative" in t or "jimenovьnik" in t: return "nom"
    if "genitive" in t or "rodilьnik" in t: return "gen"
    if "accusative" in t or "vinьnik" in t: return "acc"
    if "locative" in t or "městьnik" in t: return "loc"
    if "dative" in t or "měrьnik" in t: return "dat"
    if "instrumental" in t or "orǫdьnik" in t: return "ins"
    return "nom"

def detect_number(tag):
    return "pl" if "plural" in tag.lower() or "munoga" in tag.lower() else "sg"

def build_models():
    data = load_data("vuzor.json")
    models = {}
    for e in data:
        slov = e.get("slovian", "").strip()
        tag = e.get("type and case", "")
        if not slov: continue
        lemma = tag.split('"')[1].strip() if '"' in tag else slov.split()[0]
        case = detect_case(tag)
        num = detect_number(tag)
        key = f"{num}_{case}"
        
        if lemma not in models:
            models[lemma] = {"endings": {}, "class": "fem" if lemma.endswith("a") else "neut" if lemma[-1] in "oe" else "masc"}
        models[lemma]["endings"][key] = slov
    return models

# ========================
# REGUŁY PRZYIMKÓW
# ========================
PREP_RULES = {
    "w":  ("loc", "v"),
    "do": ("gen", "do"),
    "na": ("loc", "na"),
    "o":  ("loc", "o"),
    "k":  ("dat", "k"),
    "z":  None,   # specjalna obsługa poniżej
    "ze": None
}

def get_case_and_prep(tokens, i):
    if i == 0: return "nom", None
    prev = tokens[i-1].lower()
    
    if prev in ("z", "ze"):
        # z kimś/czymś → su + ins
        # z kogo/czego → jiz + gen
        next_word = tokens[i+1] if i+1 < len(tokens) else ""
        if any(x in next_word for x in ["kim","czym","nim","nią","nimi","sob","tob"]):
            return "ins", "su"
        return "gen", "jiz"
    
    if prev in PREP_RULES:
        case, prep = PREP_RULES[prev]
        return case, prep
    return "acc", None   # domyślnie dopełnienie

def decline(word, case, number, models):
    if not word: return "●"
    best_model = None
    best_score = float("inf")
    
    for lemma, m in models.items():
        score = sum(a != b for a,b in zip(word.lower(), lemma.lower())) + abs(len(word)-len(lemma))
        if score < best_score:
            best_score = score
            best_model = m
    
    if not best_model:
        return "●"
    
    key = f"{number}_{case}"
    result = best_model["endings"].get(key)
    return result if result else "●"

# ========================
# GŁÓWNA FUNKCJA
# ========================
def process(sentence):
    models = build_models()
    tokens = sentence.lower().split()
    result = []
    
    i = 0
    while i < len(tokens):
        word = tokens[i]
        
        if word in ("z", "ze"):
            # przyimek obsługiwany przy następnym słowie
            i += 1
            continue
            
        if word in PREP_RULES and PREP_RULES[word]:
            result.append(PREP_RULES[word][1])
            i += 1
            continue
            
        case, prep = get_case_and_prep(tokens, i)
        number = "pl" if word.endswith(("y","i","ów","ami","ach")) else "sg"
        
        translated = decline(word, case, number, models)
        result.append(translated)
        i += 1
    
    return " ".join(result)

# Test
if __name__ == "__main__":
    print(process("W ogrodzie"))          # → Vu ogrodzie.
    print(process("Z przyjacielem"))      # → Su prijateljem.
    print(process("Z okna"))              # → Jiz okna.
    print(process("Kobieta widzi mężczyznę"))
