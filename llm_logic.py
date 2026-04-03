import json
import os
from collections import defaultdict

# ========================
# 📂 IO
# ========================

def load_data(file):
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# ========================
# 🔤 LEVENSHTEIN
# ========================

def levenshtein(a, b):
    dp = [[i + j if i * j == 0 else 0 for j in range(len(b) + 1)] for i in range(len(a) + 1)]

    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            cost = 0 if a[i-1] == b[j-1] else 1
            dp[i][j] = min(
                dp[i-1][j] + 1,
                dp[i][j-1] + 1,
                dp[i-1][j-1] + cost
            )
    return dp[-1][-1]

# ========================
# 🧠 TAGI
# ========================

def detect_case(tag):
    tag = tag.lower()
    if "nominative" in tag: return "nom"
    if "genitive" in tag: return "gen"
    if "accusative" in tag: return "acc"
    if "locative" in tag: return "loc"
    if "dative" in tag: return "dat"
    if "instrumental" in tag: return "ins"
    return "nom"

def detect_number(tag):
    return "pl" if "plural" in tag else "sg"

def extract_lemma(tag, fallback):
    if '"' in tag:
        return tag.split('"')[1]
    return fallback

# ========================
# 🧱 RDZEŃ
# ========================

def longest_common_prefix(words):
    if not words:
        return ""
    prefix = words[0]
    for w in words[1:]:
        i = 0
        while i < len(prefix) and i < len(w) and prefix[i] == w[i]:
            i += 1
        prefix = prefix[:i]
    return prefix

# ========================
# 🧠 KLASY
# ========================

def classify_lemma(word):
    if word.endswith("a"):
        return "fem"
    if word.endswith(("o", "e")):
        return "neut"
    return "masc"

# ========================
# 🧠 MODELE
# ========================

def build_models():
    data = load_data("vuzor.json")
    lemmas = defaultdict(list)

    for e in data:
        slov = e.get("slovian", "")
        tag = e.get("type and case", "")

        if not slov:
            continue

        lemma = extract_lemma(tag, slov)

        lemmas[lemma].append({
            "form": slov,
            "case": detect_case(tag),
            "num": detect_number(tag)
        })

    models = []

    for lemma, forms in lemmas.items():
        base_forms = [f["form"] for f in forms]
        stem = longest_common_prefix(base_forms)

        endings = {}
        for f in forms:
            key = f"{f['num']}_{f['case']}"
            endings[key] = f["form"][len(stem):]

        models.append({
            "lemma": lemma,
            "stem": stem,
            "endings": endings,
            "class": classify_lemma(lemma)
        })

    return models

# ========================
# 🧠 WYBÓR MODELU
# ========================

def find_model(word, models):
    best = None
    best_score = float("inf")

    wclass = classify_lemma(word)

    for m in models:
        score = levenshtein(word, m["lemma"])
        if m["class"] != wclass:
            score += 2

        if score < best_score:
            best_score = score
            best = m

    return best

# ========================
# 🧠 POS TAGGING (heurystyka)
# ========================

def guess_pos(word):
    if word.endswith(("ć", "ł", "ła", "li")):
        return "verb"
    if word in ["w", "do", "z", "na", "o", "k", "ku"]:
        return "prep"
    return "noun"

# ========================
# 🧠 PARSER SKŁADNI
# ========================

def parse_sentence(tokens):
    structure = []

    verb_found = False

    for i, word in enumerate(tokens):
        pos = guess_pos(word)

        if pos == "verb":
            verb_found = True
            structure.append((word, "verb"))
        elif pos == "prep":
            structure.append((word, "prep"))
        else:
            if not verb_found:
                structure.append((word, "subject"))
            else:
                structure.append((word, "object"))

    return structure

# ========================
# 🧠 PRZYPADKI
# ========================

PREPOSITIONS = {
    "w": "loc",
    "do": "gen",
    "z": "ins",
    "na": "loc",
    "o": "loc",
    "k": "dat"
}

def assign_case(role, prev_word):
    if prev_word in PREPOSITIONS:
        return PREPOSITIONS[prev_word]

    if role == "subject":
        return "nom"
    if role == "object":
        return "acc"

    return "nom"

# ========================
# 🔁 ODMIANA
# ========================

def detect_number(word):
    if word.endswith(("y", "i", "ów", "ami", "ach")):
        return "pl"
    return "sg"

def strip_word(word):
    for suf in ["ami", "ach", "ów", "a", "y", "i", "ę"]:
        if word.endswith(suf):
            return word[:-len(suf)]
    return word

def decline(word, case, number, models):
    model = find_model(word, models)
    if not model:
        return word

    key = f"{number}_{case}"
    if key not in model["endings"]:
        return word

    base = strip_word(word)
    return base + model["endings"][key]

# ========================
# 🚀 PIPELINE
# ========================

def process(sentence):
    models = build_models()
    tokens = sentence.lower().split()

    parsed = parse_sentence(tokens)

    result = []

    for i, (word, role) in enumerate(parsed):
        if role == "prep":
            result.append("v" if word == "w" else word)
            continue

        prev = tokens[i-1] if i > 0 else ""
        case = assign_case(role, prev)
        number = detect_number(word)

        result.append(decline(word, case, number, models))

    return " ".join(result)

# ========================
# TESTY
# ========================

if __name__ == "__main__":
    print(process("Kobieta widzi mężczyznę"))
    print(process("W grodzie"))
    print(process("Do grodów"))
    print(process("Programista widzi kobietę"))
    print(process("Na komputerach"))
