import streamlit as st
import json
import os
import re
from collections import defaultdict
from groq import Groq

# ================== KONFIGURACJA STRONY ==================
st.set_page_config(page_title="Perkladačь slověnьskogo ęzyka", layout="wide")

st.markdown("""
<style>
    .main {background-color: #0e1117;}
    .stTextArea textarea {background-color: #1a1a1a; color: #dcdcdc; font-size: 1.1rem;}
    .stSuccess {background-color: #1e2a1e; color: #90ee90; border: 1px solid #4CAF50;}
</style>
""", unsafe_allow_html=True)

# ================== POŁĄCZENIE Z API ==================
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Błąd klucza API. Upewnij się, że GROQ_API_KEY jest w secrets.")
    st.stop()

# ================== ŁADOWANIE I INDEKSOWANIE DANYCH ==================

@st.cache_data
def load_data():
    def read_json(path):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    osnova_raw = read_json("osnova.json")
    vuzor_raw = read_json("vuzor.json")
    
    # Indeksujemy słownik po polskim słowie dla szybkiego wyszukiwania
    dictionary = defaultdict(list)
    for entry in osnova_raw:
        pol = entry.get("polish", "").lower().strip()
        if pol:
            dictionary[pol].append(entry)
            
    return dictionary, vuzor_raw

dictionary, vuzor_list = load_data()

# ================== LOGIKA ESTRAKCJI KONTEKSTU ==================

def get_grammatical_context(text, dic, vuzory):
    # Wyciągamy słowa z tekstu użytkownika
    words = re.findall(r'\b\w+\b', text.lower())
    found_mappings = []
    relevant_forms = []
    seen_slovian_bases = set()

    for w in words:
        # 1. Szukamy słowa bazowego w osnova.json
        entries = []
        if w in dic:
            entries = dic[w]
        elif len(w) >= 4:
            # Prosty fuzzy matching (prefix)
            pref = w[:4]
            for pol_key in dic:
                if pol_key.startswith(pref):
                    entries.extend(dic[pol_key])

        for e in entries:
            found_mappings.append(e)
            s_base = e.get("slovian")
            
            # 2. Dla każdego znalezionego słowa szukamy WSZYSTKICH form w vuzor.json
            if s_base and s_base not in seen_slovian_bases:
                # Szukamy w vuzorze wierszy pasujących do słowa słowiańskiego
                for v in vuzory:
                    # Sprawdzamy czy słowo bazowe występuje w opisie lub kolumnie slovian
                    v_case = v.get("type and case", "")
                    v_slov = v.get("slovian", "")
                    
                    if s_base == v_slov or f"'{s_base}'" in v_case:
                        relevant_forms.append({
                            "forma": v_slov,
                            "gramatyka": v_case
                        })
                seen_slovian_bases.add(s_base)

    return found_mappings, relevant_forms

# ================== INTERFEJS UŻYTKOWNIKA ==================

st.title("🏛️ Perkladačь slověnьskogo ęzyka")
st.subheader("Precyzyjne tłumaczenie z wykorzystaniem tabel odmian")

user_input = st.text_area(
    "Vupiši slovo alibo rěčenьje (PL):",
    placeholder="Np. W Słowianach siła. Miasto jest wielkie.",
    height=150
)

if user_input:
    with st.spinner("Analiza gramatyczna i tłumaczenie..."):
        
        # Pobieramy dane słownikowe i tabele odmian dla słów w zdaniu
        mappings, grammar_pool = get_grammatical_context(user_input, dictionary, vuzor_list)

        # Przygotowanie kontekstu dla modelu
        mappings_str = "\n".join([f"- PL: {m.get('polish')} -> SL_BASE: {m.get('slovian')}" for m in mappings])
        
        grammar_str = ""
        for item in grammar_pool:
            grammar_str += f"Słowo: {item['forma']} | Opis: {item['gramatyka']}\n"

        system_prompt = f"""Jesteś ekspertem języka prasłowiańskiego i staro-cerkiewno-słowiańskiego.
Twoim celem jest przetłumaczyć zdanie na język słowiański, używając POPRAWNYCH FORM GRAMATYCZNYCH z dostarczonych tabel.

DANE SŁOWNIKOWE (PODSTAWOWE):
{mappings_str}

TABELE ODMIAN DLA SŁÓW W ZDANIU:
{grammar_str}

ZASADY TŁUMACZENIA:
1. Przeanalizuj kontekst zdania (przypadek, liczba, rodzaj, osoba).
2. Dopasuj formę ze zdania do opisu w "TABELE ODMIAN".
   Przykład: "W miastach" -> szukasz 'locative' + 'plural' dla słowa 'gord' (miasto). Wynik: 'gorděh'.
3. Jeśli w tabelach nie ma konkretnej formy, spróbuj ją stworzyć logicznie na podstawie innych odmian lub napisz (ne najdeno formy).
4. SZYK: Przymiotniki i przysłówki przed rzeczownikami.
5. Zwróć TYLKO czyste tłumaczenie. Nie dodawaj komentarzy.

TEKST DO PRZETŁUMACZENIA:
"{user_input}" """

        try:
            # Używamy najnowszego modelu Llama 3.3 dla najlepszej logiki
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0, # Zero, aby model był przewidywalny
                max_tokens=1000
            )

            translation = response.choices[0].message.content.strip()

            st.markdown("### Vynik perklada:")
            st.success(translation)
            
            with st.expander("Zobacz analizę gramatyczną"):
                st.write("**Znalezione formy w vuzor.json:**")
                st.code(grammar_str if grammar_str else "Nie znaleziono pasujących form we wzorach.")

        except Exception as e:
            st.error(f"Błąd tłumaczenia: {e}")

# Stopka danych
st.divider()
st.caption(f"Baza danych: {len(osnova_raw)} słów podstawowych | {len(vuzor_list)} form gramatycznych.")
