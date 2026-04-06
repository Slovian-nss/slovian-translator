import json
from typing import Optional

class SlovianDecliner:
    def __init__(self):
        with open('vuzor.json', encoding='utf-8') as f:
            self.vuzor = json.load(f)
        
        self.lookup = {}
        for e in self.vuzor:
            key = (e['polish'].lower(), e['type and case'])
            self.lookup[key] = e['slovian']

    def decline(self, polish: str, case_name: str, number: str = "singular", 
                word_type: str = "noun", gender: str = None) -> str:
        
        p = polish.lower()
        num = "munoga ličьba" if number == "plural" else "poedinьna ličьba"

        # 1. Dokładna forma z vuzor.json
        if word_type == "noun":
            g = gender or ("feminine (inanimate)" if p.endswith('a') else "masculine (inanimate)")
            key = f"noun - jimenьnik: \"{polish}\" | {case_name} | {num} | type {g}"
            if (p, key) in self.lookup:
                return self.lookup[(p, key)]

        # 2. Fallback z JSON (podobny przypadek)
        for (w, c), s in self.lookup.items():
            if w == p and case_name in c and num in c:
                return s

        # 3. Reguły fallback dla wszystkich typów (nawet gdy nie ma w JSON)

        if word_type == "noun":
            if number == "singular":
                if case_name == "městьnik":      # locative
                    if p.endswith('a'): return p[:-1] + "ě"
                    else: return p + "ě"
                elif case_name == "orǫdьnik":    # instrumental
                    if p.endswith('a'): return p[:-1] + "ojǫ"
                    else: return p + "omь"
                elif case_name == "vinьnik":     # accusative
                    return polish
                elif case_name == "rodilьnik":   # genitive
                    if p.endswith('a'): return p[:-1] + "y"
                    else: return p + "a"
                elif case_name == "měrьnik":     # dative
                    if p.endswith('a'): return p[:-1] + "ě"
                    else: return p + "u"
                elif case_name == "zovanьnik":   # vocative
                    if p.endswith('a'): return p[:-1] + "o"
                    else: return p + "e"
            else:  # plural
                if case_name in ("jimenovьnik", "vinьnik", "zovanьnik"):
                    if p.endswith('a'): return p[:-1] + "i"
                    else: return p + "i"
                elif case_name == "rodilьnik":
                    return p + "ov" if not p.endswith('a') else p[:-1]
                elif case_name == "městьnik":
                    return p + "ah"
                elif case_name == "měrьnik":
                    return p + "am"
                elif case_name == "orǫdьnik":
                    return p + "ami"

        elif word_type == "adjective":
            base = polish
            if number == "singular":
                if gender == "feminine":
                    if case_name == "vinьnik": return base + "ǫ"
                    if case_name in ("rodilьnik", "městьnik", "měrьnik"): return base + "eji"
                    if case_name == "orǫdьnik": return base + "ejǫ"
                    return base + "a"
                else:  # masculine / neuter
                    if case_name == "rodilьnik": return base + "ogo"
                    if case_name == "měrьnik": return base + "omu"
                    if case_name in ("městьnik", "orǫdьnik"): return base + "ymь"
                    return base
            else:  # plural
                if case_name in ("rodilьnik", "městьnik"): return base + "yh"
                if case_name == "měrьnik": return base + "ymь"
                if case_name == "orǫdьnik": return base + "ymi"
                return base + "e" if gender == "feminine" else base + "i"

        return f"[{polish} - brak formy]"

# ===================== UŻYCIE W TŁUMACZU =====================
decliner = SlovianDecliner()

# Przykłady (testuj w aplikacji)
print(decliner.decline("ogród", "městьnik"))                    # → obgordě
print(decliner.decline("obietnica", "vinьnik"))                 # → obětьnicǫ
print(decliner.decline("równy", "vinьnik", "singular", "adjective", "feminine"))  # → orvьnǫ
print(decliner.decline("gord", "orǫdьnik", "plural"))           # → gordy
