import streamlit as st
import json
import os
import re
from groq import Groq

# ================== KONFIGURACJA ==================
st.set_page_config(page_title="Perkladačь slověnьskogo ęzyka", layout="wide")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("Błąd API. Sprawdź klucz w secrets.")
    st.stop()

# ================== SILNIK DANYCH ==================
@st.cache_data
def load_full_db():
    def rj(p):
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f: return json.load(f)
        return []
    return rj("osnova.json"), rj("vuzor.json")

osnova, vuzor = load_full_db()

# ================== LOGIKA TŁUMACZENIA (Ekspercka) ==================

def translate_expert(text):
    # KROK 1: Analiza morfologiczna zdania przez LLM
    # Model nie tłumaczy, tylko rozbija polskie zdanie na parametry
    analysis_prompt = f"""Przeanalizuj gramatycznie polskie zdanie. 
Dla każdego słowa (z wyjątkiem spójników) wypisz: polskie_slowo | przypadek | liczba | rodzaj.
Używaj angielskich nazw: nominative, genitive, dative, accusative, instrumental, locative, vocative.
Liczba: singular, plural. Rodzaj: masculine, feminine, neuter.

Zdanie: {text}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": analysis_prompt}],
        temperature=0
    )
    analysis = response.choices[0].message.content
    
    # KROK 2: Wyszukiwanie w Twojej bazie (Hard-match)
    translated_words = []
    lines = analysis.split('\n')
    
    debug_info = []

    for line in lines:
        if "|" not in line: continue
        parts = [p.strip().lower() for p in line.split('|')]
        if len(parts) < 4: continue
        
        pl_word, case, num, gender = parts[0], parts[1], parts[2], parts[3]
        
        # Znajdź słowo słowiańskie (rdzeń)
        slov_base = next((item['slovian'] for item in osnova if item['polish'].lower() == pl_word), None)
        
        if slov_base:
            # Szukaj konkretnej formy w vuzor.json
            # Sprawdzamy czy w 'type and case' są wszystkie wymagane tagi
            found_form = None
            for v in vuzor:
                info = v.get("type and case", "").lower()
                if slov_base in info and case in info and num in info:
                    found_form = v.get("slovian")
                    break
            
            if found_form:
                translated_words.append(found_form)
                debug_info.append(f"✅ {pl_word} -> {found_form} ({case}, {num})")
            else:
                translated_words.append(f"({slov_base}?)")
                debug_info.append(f"⚠️ Brak formy dla {slov_base} ({case}, {num})")
        else:
            # Obsługa przyimków (np. w -> vu)
            prepositions = {"w": "vu", "na": "na", "z": "iz", "za": "za"}
            translated_words.append(prepositions.get(pl_word, pl_word))

    return " ".join(translated_words), debug_info

# ================== INTERFEJS ==================
st.title("🏛️ Ekspercki Perkladačь")
st.markdown("Algorytm mapowania morfologicznego (Logic: Hoenir-inspired)")

user_input = st.text_area("Wpisz tekst po polsku:", placeholder="W Słowianach siła.")

if user_input:
    with st.spinner("Analiza morfologiczna..."):
        result, debug = translate_expert(user_input)
        
        st.subheader("Wynik:")
        st.success(result)
        
        with st.expander("Analiza Machine Learning (Krok po kroku)"):
            for d in debug:
                st.write(d)

st.divider()
st.caption(f"Status bazy: {len(osnova)} rdzeni | {len(vuzor)} form odmiany.")
