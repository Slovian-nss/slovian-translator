def get_case_and_prep(tokens, i):
    if i == 0: 
        return "nom", None
    prev = tokens[i-1].lower()
    
    if prev in ("z", "ze"):
        # Z + narzędnik (z kim/czym, z ogrodem, z przyjemnością...) → su + ins
        # Z + dopełniacz (z okna, z domu, z czego...) → jiz + gen
        if i+1 < len(tokens):
            nxt = tokens[i+1].lower()
            # Jeśli następne słowo wygląda na narzędnik (końcówki -em, -ą, -im itp. lub typowe słowa)
            if nxt.endswith(("em", "ą", "im", "ami", "ą", "przyjacielem", "ogrodem", "nim", "nią")):
                return "ins", "su"
        return "gen", "jiz"   # domyślnie dopełniacz
    
    if prev in PREP_RULES:
        return PREP_RULES[prev]
    return "acc", None


def decline(word, case, number, models):
    if not word: 
        return "●"
    
    best_model = None
    best_score = float("inf")
    
    for lemma, m in models.items():
        score = sum(a != b for a, b in zip(word.lower(), lemma.lower())) + abs(len(word) - len(lemma)) * 1.5
        if score < best_score:
            best_score = score
            best_model = m
    
    if not best_model:
        return "●"
    
    key = f"{number}_{case}"
    return best_model["endings"].get(key, "●")   # czerwona kropka jeśli brak formy
