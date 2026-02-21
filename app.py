import streamlit as st
import json
import os
import re

# ============================================================
# 1. ŁADOWANIE DANYCH
# ============================================================
@st.cache_data
def load_all_data():
    try:
        with open("osnova.json", "r", encoding="utf-8") as f:
            osnova = json.load(f)
        with open("vuzor.json", "r", encoding="utf-8") as f:
            vuzor = json.load(f)
        return osnova, vuzor
    except Exception as e:
        st.error(f"Błąd ładowania plików: {e}")
        return [], {}

osnova, vuzor = load_all_data()

# ============================================================
# 2. SILNIK LINGWISTYCZNY (LOGIKA VALHYR)
# ============================================================

def get_stem(slovian_word):
    """Usuwa jery i końcówki, aby uzyskać czysty rdzeń do odmiany."""
    return slovian_word.rstrip('ъь')

def match_case_style(original, translated):
    """Zachowuje wielkość liter (np. Matka -> Mati)."""
    if original.isupper(): return translated.upper()
    if original[0].isupper(): return translated.capitalize()
    return translated.lower()

def translate_word(polish_word, target_case="nominative"):
    """
    1. Szuka słowa w osnova.json.
    2. Pobiera typ odmiany (np. noun - o-stem - masculine).
    3. Pobiera końcówkę z vuzor.json dla danego przypadku.
    """
    pw = polish_word.lower().strip(",.?!")
    
    # Szukanie w słowniku (najpierw dopasowanie dokładne, potem rdzeń)
    entry = next((e for e in osnova if e['polish'].lower() == pw), None)
    
    # Prosta lematyzacja, jeśli nie znaleziono (np. "ogrodzie" -> "ogród")
    if not entry and len(pw) > 3:
        entry = next((e for e in osnova if pw.startswith(e['polish'].lower()[:3])), None)

    if not entry:
        return f"({polish_word}?)"

    slovian_base_word = entry['slovian']
    word_category = entry.get('type and case') # np. "noun - o-stem - masculine"
    
    # Pobieranie wzorca z vuzor.json
    category_patterns = vuzor.get(word_category, {})
    suffix = category_patterns.get(target_case, "") 
    
    # Składanie słowa: rdzeń + końcówka z wzorca
    stem = get_stem(slovian_base_word)
    final_word = stem + suffix
    
    # Reguła palatalizacji (Krytyczna w starosłowiańskim): g->dz, k->c przed 'ě'
    if suffix.startswith('ě'):
        if stem.endswith('g'): final_word = stem[:-1] + "dz" + suffix
        elif stem.endswith('k'): final_word = stem[:-1] + "c" + suffix

    return match_case_style(polish_word, final_word)

def engine_v3(text):
    words = text.split()
    translated = []
    i = 0
    
    while i < len(words):
        word = words[i].lower()
        
        # Wykrywanie przyimków wymuszających przypadek (np. "w" -> miejscownik)
        if word in ["w", "v", "we"]:
            translated.append("vu")
            i += 1
            if i < len(words):
                translated.append(translate_word(words[i], "locative"))
        elif word == "jestem":
            translated.append("esmb") # Bezpośrednie tłumaczenie statyczne
        else:
            translated.append(translate_word(words[i], "nominative"))
        i += 1
        
    return " ".join(translated)

# ============================================================
# 3. INTERFEJS STREAMLIT
# ============================================================
st.title("Perkladačь (Valhyr Local Engine)")
st.markdown("---")

user_input = st.text_input("Wpisz tekst po polsku:", placeholder="np. Jestem w ogrodzie")

if user_input:
    result = engine_v3(user_input)
    
    st.markdown("### Vynik perklada:")
    st.success(result)
    
    # Sekcja debugowania (pokazuje co widzi silnik)
    with st.expander("Szczegóły analizy gramatycznej"):
        st.json({"Input": user_input, "Result": result})
