import streamlit as st
import json
import os
import re

# Ustawienia strony
st.set_page_config(page_title="Perkladačь slověnьskogo ęzyka", layout="wide")

# =========================
# STYL (Minimalizm DeepL)
# =========================
st.markdown("""
<style>
    .stApp { background-color: white; }
    h1, h2, h3, p, label { color: #1a1a1a !important; }
    .stTextArea textarea {
        background-color: #f8f9fa !important;
        color: #1a1a1a !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# LOGIKA DANYCH
# =========================

@st.cache_data
def load_all_data():
    # Ładowanie plików
    def read_json(path):
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        return {}

    osnova = read_json("osnova.json")
    memory = read_json("memory.json")

    # Budowanie słowników dwukierunkowych
    pl_to_sl = {}
    sl_to_pl = {}

    # 1. Dane z osnova.json
    if isinstance(osnova, list):
        for item in osnova:
            p = item.get("polish", "").lower().strip()
            s = item.get("slovian", "").lower().strip()
            if p and s:
                pl_to_sl[p] = s
                sl_to_pl[s] = p

    # 2. Dane z pamięci (nadpisują podstawę)
    for p, s in memory.items():
        pl_to_sl[p.lower()] = s
        sl_to_pl[s.lower()] = p

    return pl_to_sl, sl_to_pl

def save_memory(source, target, direction):
    # Prosta baza poprawek
    memory = {}
    if os.path.exists("memory.json"):
        with open("memory.json", encoding="utf-8") as f:
            memory = json.load(f)
    
    # Zapisujemy zawsze w relacji PL: SL dla spójności
    if direction == "PL -> SL":
        memory[source.lower()] = target
    else:
        memory[target.lower()] = source

    with open("memory.json", "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

# =========================
# SILNIK TŁUMACZĄCY
# =========================

def match_case(original, translated):
    if original.isupper():
        return translated.upper()
    if original and original[0].isupper():
        return translated.capitalize()
    return translated

def translate_engine(text, dictionary):
    if not text:
        return ""
    
    # Rozbijanie na słowa, zachowując znaki specjalne i spacje
    tokens = re.split(r'(\W+)', text)
    result = []

    for token in tokens:
        low_token = token.lower()
        if low_token in dictionary:
            translated_word = dictionary[low_token]
            result.append(match_case(token, translated_word))
        else:
            result.append(token)
            
    return "".join(result)

# =========================
# INTERFEJS UŻYTKOWNIKA
# =========================

pl_to_sl, sl_to_pl = load_all_data()

st.title("Perkladačь slověnьskogo ęzyka")

# Wybór kierunku
col_dir1, col_dir2 = st.columns([1, 4])
with col_dir1:
    direction = st.radio("Kierunek / Naprjamok:", ["PL -> SL", "SL -> PL"])

# Okna tekstu
col1, col2 = st.columns(2)

with col1:
    input_text = st.text_area("Tekst źródłowy:", height=250, placeholder="Wpisz tekst...")

# Wybór słownika na podstawie kierunku
current_dict = pl_to_sl if direction == "PL -> SL" else sl_to_pl

# Automatyczne tłumaczenie (opcjonalnie przyciskiem)
if input_text:
    output_text = translate_engine(input_text, current_dict)
else:
    output_text = ""

with col2:
    st.text_area("Tłumaczenie / Perklad:", output_text, height=250, disabled=False)

# =========================
# PANEL MODERATORA
# =========================
st.markdown("---")
with st.expander("Panel poprawek (Admin)"):
    pwd = st.text_input("Hasło", type="password")
    if pwd == "Rozeta*8":
        c1, c2 = st.columns(2)
        with c1:
            src_word = st.text_input("Słowo polskie")
        with c2:
            trg_word = st.text_input("Słowo słowiańskie")
        
        if st.button("Zaktualizuj bazę"):
            if src_word and trg_word:
                save_memory(src_word, trg_word, "PL -> SL")
                st.success("Dodano! Odśwież stronę (R), aby zastosować.")
                st.cache_data.clear()
    elif pwd != "":
        st.error("Błędne hasło")
