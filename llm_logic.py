import json
import os
from collections import defaultdict

def load_data(file):
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_data(data, file):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ========================
# 🔥 KLUCZ: ANALIZA WZORCA
# ========================

def detect_case(tag):
    tag = tag.lower()
    if "nominative" in tag: return "nom"
    if "genitive" in tag: return "gen"
    if "accusative" in tag: return "acc"
    if "locative" in tag: return "loc"
    if "dative" in tag: return "dat"
    if "instrumental" in tag: return "ins"
    if "vocative" in tag: return "voc"
    return "nom"

def detect_number(tag):
    return "pl" if "plural" in tag else "sg"

def detect_gender(tag):
    if "feminine" in tag: return "fem"
    if "neuter" in tag: return "neut"
    return "masc"

def detect_pattern(nom_form):
    """Typ odmiany na podstawie mianownika"""
    if nom_form.endswith("a"):
        return "a"        # obětьnica
    if nom_form.endswith("ь"):
        return "soft"     # mǫdrostь
    if nom_form.endswith("je"):
        return "je"       # bytьje
    if nom_form.endswith("ъ"):
        return "hard_m"   # (jeśli dodasz)
    return "other"

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

def get_grammar_map():
    vuzor = load_data('vuzor.json')

    # grupujemy: lemma -> wszystkie formy
    lemmas = defaultdict(list)

    for entry in vuzor:
        tag = entry.get("type and case", "")
        slov = entry.get("slovian", "")
        if not slov:
            continue

        # wyciągamy lemma z tagu ("obětьnica")
        if '"' in tag:
            lemma = tag.split('"')[1]
        else:
            lemma = slov

        lemmas[lemma].append({
            "form": slov,
            "case": detect_case(tag),
            "num": detect_number(tag),
            "gender": detect_gender(tag)
        })

    g_map = defaultdict(lambda: defaultdict(str))

    # 🔥 ANALIZA WZORCÓW
    for lemma, forms in lemmas.items():
        all_forms = [f["form"] for f in forms]

        stem = longest_common_prefix(all_forms)
        pattern = detect_pattern(lemma)
        gender = forms[0]["gender"]

        type_key = f"noun_{gender}_{pattern}"

        for f in forms:
            key = f"{f['num']}_{f['case']}"
            suffix = f["form"][len(stem):]

            # zapis tylko jeśli nie istnieje (żeby nie nadpisywać różnymi wariantami)
            if key not in g_map[type_key]:
                g_map[type_key][key] = suffix

    return dict(g_map)

# ========================
# 📚 UCZENIE RDZENI
# ========================

def learn():
    vuzor = load_data('vuzor.json')
    osnova = []

    lemmas = {}

    for entry in vuzor:
        tag = entry.get("type and case", "")
        slov = entry.get("slovian", "")
        pol = entry.get("polish", "").lower()

        if not slov or not pol:
            continue

        if '"' in tag:
            lemma = tag.split('"')[1]
        else:
            lemma = slov

        if lemma not in lemmas:
            lemmas[lemma] = {
                "forms": [],
                "polish": pol
            }

        lemmas[lemma]["forms"].append(slov)

    for lemma, data in lemmas.items():
        forms = data["forms"]
        stem = longest_common_prefix(forms)

        pattern = detect_pattern(lemma)

        osnova.append({
            "polish": data["polish"],
            "lemma": lemma,
            "stem": stem,
            "pattern": pattern
        })

    save_data(osnova, 'osnova.json')

# ========================
# 🔁 TŁUMACZENIE
# ========================

def translate_word_smart(polish_input):
    osnova = load_data('osnova.json')
    g_map = get_grammar_map()

    for item in osnova:
        if polish_input.startswith(item['polish'][:4]):
            stem = item['stem']
            pattern = item['pattern']

            # heurystyka PL → przypadek
            if polish_input.endswith("ów") or polish_input.endswith("y"):
                key = "pl_gen"
            elif polish_input.endswith("ami"):
                key = "pl_ins"
            elif polish_input.endswith("ach"):
                key = "pl_loc"
            elif polish_input.endswith("ę"):
                key = "sg_acc"
            else:
                key = "sg_nom"

            # znajdź odpowiedni typ
            for g_type in g_map:
                if pattern in g_type:
                    suffix = g_map[g_type].get(key, "")
                    return stem + suffix

    return polish_input

# ========================
# 🚀 START
# ========================

if __name__ == "__main__":
    learn()
    print(get_grammar_map())
