import streamlit as st
import json
import os
import re
from collections import defaultdict
from groq import Groq

# ================== KONFIGURACJA STRONY ==================
st.set_page_config(page_title="Perkladačь slověnьskogo ęzyka", layout="wide")

# Stylizacja zgodna z Twoim interfejsem
st.markdown("""
<style>
    .main {background-color: #0e1117;}
    .stTextArea textarea {background-color: #1a1a1a; color: #dcdcdc; font-size: 1.1rem; border-radius: 10px;}
    .stSuccess {background-color: #152b1b; color: #4ade80; border: 1px solid #22c55e; border-radius: 10px; padding: 15px;}
</style>
""", unsafe_allow_html=True)

# ================== POŁĄCZENIE Z API ==================
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Błąd klucza API. Sprawdź st.secrets.")
    st.stop()

# ================== ŁADOWANIE DANYCH ==================
@st.cache_data
def load_data():
    def read_json(path):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    o_raw = read_json("osnova.json")
    v_raw = read_json("vuzor.json")
    
    # Słownik PL -> SL_BASE
    dic = defaultdict(list)
    for entry in o_raw:
        pol = entry.get("polish", "").lower().strip()
        if pol:
            dic[pol].append(entry)
    return dic, v_raw, o_raw

dictionary, vuzor_list, osnova_raw = load_data()

# ================== LOGIKA "RAG" (Dopasowanie Gramatyczne) ==================
def get_strict_context(text, dic, vuzory):
    words = re.findall(r'\b\w+\b', text.lower())
    found_mappings = []
    available_forms = []
    seen_bases = set()

    for w in words:
        entries = dic.get(w, [])
        # Fuzzy matching jeśli nie ma dokładnego
        if not entries and len(w) >= 4:
            pref = w[:4]
            for k in dic:
                if k.startswith(pref):
                    entries.extend(dic[k])

        for e in entries:
            found_mappings.append(e)
            s_base = e.get("slovian")
            if s_base and s_base not in seen_bases:
                # Szukamy absolutnie wszystkich form dla tego rdzenia
                for v in vuzory:
                    info = v.get("type and case", "")
                    forma = v.get("slovian", "")
                    # Szukamy rdzenia w cudzysłowie w kolumnie info (tak jak w Twoim arkuszu)
                    if f"'{s_base}'" in info or s_base == forma:
                        available_forms.append(f"FORM: {forma} | GRAMMAR: {info}")
                seen_bases.add(s_base)
    
    return found_mappings, available_forms

# ================== INTERFEJS ==================
st.title("🏛️ Perkladačь slověnьskogo ęzyka")
st.write("### Precyzyjne tłumaczenie z wykorzystaniem tabel odmian")

user_input = st.text_area("Vupiši slovo alibo rěčenьje (PL):", placeholder="W Słowianach siła.", height=150)

if user_input:
    with st.spinner("Weryfikacja form gramatycznych w bazie..."):
        mappings, grammar_pool = get_strict_context(user_input, dictionary, vuzor_list)
        
        grammar_context = "\n".join(grammar_pool)

        # PROMPT "ZERO-TOLERANCE" - Model staje się tylko parserem
        system_prompt = f"""Jesteś rygorystycznym kompilatorem języka słowiańskiego. 
Twoim zadaniem jest złożenie zdania wyłącznie z form podanych w DANYCH GRAMATYCZNYCH.

DANE GRAMATYCZNE:
{grammar_context}

INSTRUKCJA DZIAŁANIA:
1. Przeanalizuj polskie zdanie: "{user_input}"
2. Dla każdego słowa określ: PRZYPADEK (Case), LICZBĘ (Number), RODZAJ (Gender).
3. Znajdź w DANYCH GRAMATYCZNYCH formę, która DOKŁADNIE odpowiada tym cechom.
   PRZYKŁAD: "w Słowianach" -> potrzebujesz 'locative' + 'plural'. 
   Jeśli w danych jest "FORM: slověnьnah | GRAMMAR: ... locative | plural", MUSISZ użyć "slověnьnah".
4. Jeśli forma nie istnieje w danych, wstaw (brak_formy).
5. ZAKAZ: Nie zmieniaj końcówek, nie twórz własnych słów, nie używaj wiedzy ogólnej.
6. SZYK: Przymiotnik zawsze przed rzeczownikiem.
7. ZWRÓĆ TYLKO ZDANIE. BEZ KOMENTARZY."""

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": system_prompt}],
                temperature=0.0 # Całkowity brak kreatywności
            )

            result = response.choices[0].message.content.strip()
            
            st.write("### Vynik perklada:")
            st.success(result)
            
            with st.expander("Dane użyte przez AI (Weryfikacja tabel)"):
                st.code(grammar_context if grammar_context else "Nie znaleziono powiązanych form.")

        except Exception as e:
            st.error(f"Błąd: {e}")

# ================== STOPKA (Zmienne globalne) ==================
st.divider()
st.caption(f"Baza danych: {len(osnova_raw)} słów podstawowych | {len(vuzor_list)} form gramatycznych.")
