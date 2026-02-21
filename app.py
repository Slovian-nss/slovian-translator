import streamlit as st
import json
import os
import re

# ============================================================
# 1. KONFIGURACJA
# ============================================================
st.set_page_config(page_title="Perkladačь (Local Engine)", layout="centered")

@st.cache_data
def load_data():
    osnova, vuzory = [], {}
    if os.path.exists("osnova.json"):
        with open("osnova.json", "r", encoding="utf-8") as f:
            osnova = json.load(f)
    if os.path.exists("vuzor.json"):
        with open("vuzor.json", "r", encoding="utf-8") as f:
            vuzory = json.load(f) # Zakładamy, że vuzor.json ma strukturę mapującą przypadki
    return osnova, vuzory

osnova_data, vuzory = load_data()

# ============================================================
# 2. SILNIK ODMIAN (Logika Valhyr)
# ============================================================

def find_lemma(polish_word):
    """Szuka formy podstawowej i typu odmiany w osnova.json."""
    pw = polish_word.lower()
    for entry in osnova_data:
        # Sprawdzamy czy polskie słowo pasuje do rdzenia lub formy w bazie
        if entry['polish'].lower() == pw:
            return entry
    return None

def apply_vuzor(lemma_entry, target_case):
    """Aplikuje końcówkę z vuzor.json na podstawie typu słowa."""
    slovian_base = lemma_entry['slovian']
    word_type = lemma_entry.get('type and case', '') # np. "noun - o-stem"

    # Logika szukania końcówki we wzorach
    # Zakładamy, że vuzory[word_type][target_case] zwraca końcówkę
    try:
        if word_type in vuzory and target_case in vuzory[word_type]:
            suffix = vuzory[word_type][target_case]
            # Uproszczona logika zamiany końcówki (usuwanie jerów itp.)
            base = slovian_base.rstrip('ъь') 
            return base + suffix
    except:
        pass
    
    return slovian_base

def translate_logic(text):
    # Prosta heurystyka przypadków dla języka polskiego
    # W pełnej wersji użyłbyś narzędzia typu SpaCy, tu robimy to "na sztywno" jak w leksemach
    words = text.lower().split()
    result = []
    
    i = 0
    while i < len(words):
        word = words[i]
        
        # Obsługa przyimków (np. "w" + miejscownik)
        target_case = "nominative"
        if word == "w" or word == "v":
            target_case = "locative"
            result.append("vu")
            i += 1
            if i >= len(words): break
            word = words[i]

        lemma = find_lemma(word)
        if lemma:
            # Rekonstrukcja słowa na podstawie wzorca
            translated = apply_vuzor(lemma, target_case)
            
            # Palatalizacja (Krytyczna zasada Valhyr)
            if target_case == "locative":
                if translated.endswith("gě"): translated = translated[:-2] + "dzě"
                if translated.endswith("kě"): translated = translated[:-2] + "cě"
            
            result.append(translated)
        else:
            result.append(f"({word}?)")
        i += 1
        
    return " ".join(result)

# ============================================================
# 3. INTERFEJS
# ============================================================
st.title("Perkladačь slověnьskogo ęzyka")

user_input = st.text_input("Vupiši slovo abo rěčenьje:", placeholder="np. w ogrodzie")

if user_input:
    # Symulacja działania lokalnego silnika
    with st.spinner("Analiza morfologiczna..."):
        output = translate_logic(user_input)
        
    st.markdown("### Vynik perklada:")
    st.success(output)
