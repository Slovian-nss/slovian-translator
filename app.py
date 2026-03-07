import streamlit as st
import json
import os
import re
from collections import defaultdict
from groq import Groq

# ================== KONFIGURACJA ==================
st.set_page_config(page_title="Perkladačь slověnьskogo ęzyka", layout="centered")

st.markdown("""
<style>
.main {background:#0e1117}
.stTextArea textarea {background:#1a1a1a;color:#dcdcdc;font-size:1.1rem;}
</style>
""", unsafe_allow_html=True)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ================== ŁADOWANIE DANYCH ==================
@st.cache_data
def load_full_database():
    def load_json(name):
        if not os.path.exists(name): return []
        with open(name, "r", encoding="utf-8") as f: return json.load(f)
    # Łączymy wzory odmian i podstawy
    return load_json("vuzor.json") + load_json("osnova.json")

DATA = load_full_database()

def find_precise_matches(text):
    tokens = re.findall(r'\w+', text.lower())
    matches = []
    
    # Rozpoznawanie przyimków dla kontekstu
    case_context = {"w": "locative", "we": "locative", "na": "locative", "do": "genitive"}
    
    for i, word in enumerate(tokens):
        needed_case = case_context.get(tokens[i-1]) if i > 0 else None
        
        # Szukamy w bazie wszystkiego co pasuje do słowa lub rdzenia
        relevant_for_word = []
        for entry in DATA:
            pl = entry.get("polish", "").lower()
            # Szukamy dokładnego dopasowania lub po rdzeniu (min 4 litery)
            if word == pl or (len(word) >= 4 and pl.startswith(word[:4])):
                relevant_for_word.append(entry)
        
        # Sortujemy: najpierw te, które pasują do wymaganego przypadku i są rzeczownikami
        if needed_case:
            relevant_for_word.sort(key=lambda x: 1 if (needed_case in x.get("type and case", "").lower() and "noun" in x.get("type and case", "").lower()) else 0, reverse=True)
            
        matches.extend(relevant_for_word[:8]) # Przekazujemy tylko top 8 dopasowań na słowo
    return matches

# ================== INTERFEJS ==================
st.title("Perkladačь slověnьskogo ęzyka")
user_input = st.text_area("Vupiši rěčenьje:", placeholder="W moim ogrodzie są ludzie.", height=150)

if user_input:
    with st.spinner("Trwa rygorystyczne tłumaczenie bez halucynacji..."):
        dictionary_context = find_precise_matches(user_input)
        
        # Tworzymy rygorystyczny słownik dla AI
        formatted_db = "\n".join([
            f"- POLSKI: {m['polish']} | SŁOWIAŃSKI: {m['slovian']} | GRAMATYKA: {m.get('type and case', '')}"
            for m in dictionary_context
        ])

        system_prompt = f"""Jesteś procesorem tłumaczącym na język prasłowiański. 
ZAKAZ: Nie używaj wiedzy ogólnej. Używaj TYLKO danych z poniższej listy.

DANE SŁOWNIKOWE:
{formatted_db}

ZASADY TŁUMACZENIA, PRZYKŁAD POPRAWNY:
Input: W moim ogrodzie.
Output: Vu mojimь obgordě.

Input: W moim mieście.
Output: Vu mojimь gordě.

ZASADY BEZWZGLĘDNE:
1. Jeśli nie ma odmiany słowiańskiego słowa (lub jego podstawowej odmiany), to wtedy napisz w jego miejscu (ne najdeno slova) i tłumacz dalej to co możesz.
2. SZYK: Przymiotniki (oznaczone są one jako: adjective - pridavьnik) i przysłówki (oznaczone są one jako: adverb - prislovok) zawsze są przed rzeczownikami (oznaczone są one jako: noun - jimenьnik).
3. FORMAT: Zachowaj interpunkcję, odwzorowanie, wielkość liter, spacje, odstępy, znaki matematyczne, linkowanie i brak dodatkowego komentarza.

TWOJE ZADANIE: Przetłumacz zdanie użytkownika, zachowując powyższe zasady."""

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0 # Blokada kreatywności
            )
            
            translation = response.choices[0].message.content.strip()
            st.markdown("### Vynik perklada:")
            st.success(translation)
            
        except Exception as e:
            st.error(f"Błąd komunikacji z Groq: {e}")

    with st.expander("Zobacz bazę gramatyczną użytą do tego tłumaczenia"):
        st.write("Te dane zostały wysłane do AI jako jedyne źródło prawdy:")
        st.table(dictionary_context)
