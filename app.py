import streamlit as st
import json
import os
import re

# ============================================================
# 1. ŁADOWANIE DANYCH
# ============================================================
@st.cache_data
def load_all_data():
    osnova, vuzor = [], {}
    try:
        if os.path.exists("osnova.json"):
            with open("osnova.json", "r", encoding="utf-8") as f:
                osnova = json.load(f)
        if os.path.exists("vuzor.json"):
            with open("vuzor.json", "r", encoding="utf-8") as f:
                vuzor = json.load(f)
    except Exception as e:
        st.error(f"Błąd w strukturze plików JSON: {e}")
    return osnova, vuzor

osnova, vuzor = load_all_data()

# ============================================================
# 2. LOGIKA ODMIAN (DOPASOWANA DO TWOJEJ STRUKTURY)
# ============================================================

def get_inflection(category, case, number="singular"):
    """
    Bezpiecznie wyciąga końcówkę z vuzor.json.
    Struktura: vuzor[category][number][case]
    """
    try:
        cat_data = vuzor.get(category, {})
        num_data = cat_data.get(number, {})
        return num_data.get(case, "")
    except Exception:
        return ""

def translate_word(polish_word, target_case="nominative"):
    pw = polish_word.lower().strip(",.?! ")
    
    # Szukanie w osnova.json
    entry = next((e for e in osnova if e['polish'].lower() == pw), None)
    
    # Prosta lematyzacja (np. ogrodzie -> ogród)
    if not entry:
        entry = next((e for e in osnova if pw.startswith(e['polish'].lower()[:4])), None)

    if not entry:
        return f"({polish_word}?)"

    slovian_nom = entry.get('slovian', '')
    category = entry.get('type and case', '') # np. "noun - o-stem - masculine"
    
    # Pobranie końcówki z vuzor.json
    suffix = get_inflection(category, target_case)
    
    # Rdzeń: usuwamy jery końcowe (ъ, ь)
    stem = slovian_nom.rstrip('ъь')
    final_word = stem + suffix
    
    # Palatalizacja (g -> dz, k -> c przed ě)
    if suffix.startswith('ě'):
        if stem.endswith('g'): final_word = stem[:-1] + "dz" + suffix
        elif stem.endswith('k'): final_word = stem[:-1] + "c" + suffix

    return final_word

def run_translator(text):
    if not text: return ""
    tokens = re.findall(r'\w+|[^\w\s]', text, re.UNICODE)
    result = []
    
    i = 0
    while i < len(tokens):
        token = tokens[i]
        low_token = token.lower()
        
        if low_token in ["w", "v", "we"]:
            result.append("vu")
            i += 1
            if i < len(tokens):
                result.append(translate_word(tokens[i], "locative"))
        elif low_token == "jestem":
            result.append("esmb")
        elif re.match(r'\w+', token):
            result.append(translate_word(token, "nominative"))
        else:
            result.append(token)
        i += 1
    return " ".join(result).replace(" .", ".").replace(" ,", ",")

# ============================================================
# 3. INTERFEJS
# ============================================================
st.title("Perkladačь (Valhyr Engine V5)")

if not osnova:
    st.warning("Baza osnova.json jest pusta lub nie istnieje.")
else:
    user_input = st.text_input("Wpisz zdanie:", value="Jestem w ogrodzie")
    if user_input:
        st.success(run_translator(user_input))
