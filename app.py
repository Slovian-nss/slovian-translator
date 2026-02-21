import streamlit as st
import json
import os
import re
from groq import Groq

# ============================================================
# 1. KONFIGURACJA I STYLIZACJA (Styl DeepL)
# ============================================================
st.set_page_config(page_title="Perkladačь slověnьskogo ęzyka", layout="wide")

# Wykrywanie języka urządzenia/przeglądarki
try:
    browser_lang = st.query_params.get("lang", ["pl"])[0][:2].lower()
except:
    browser_lang = "pl"

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTextArea textarea { background-color: #1a1a1a; color: #dcdcdc; border: 1px solid #333; font-size: 1.1rem; height: 200px !important; }
    .output-container { background-color: #161616; border: 1px solid #2e7d32; border-radius: 5px; padding: 15px; min-height: 200px; color: #dcdcdc; font-size: 1.2rem; }
    .stCaption { color: #888; }
    </style>
    """, unsafe_allow_html=True)

# ============================================================
# 2. KLUCZ API
# ============================================================
GROQ_API_KEY = "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" 
client = Groq(api_key=GROQ_API_KEY)

# ============================================================
# 3. ŁADOWANIE BAZ DANYCH
# ============================================================
@st.cache_data
def load_json(filename):
    if not os.path.exists(filename): return {}
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

dictionary = load_json("osnova.json")
vuzory = load_json("vuzor.json")

def get_relevant_context(text, dic):
    search_text = re.sub(r'[^\w\s]', '', text.lower())
    words = search_text.split()
    relevant_entries = []
    for word in words:
        if word in dic:
            # Zakładając, że dictionary jest zaindeksowany po polsku (jako pośredniku)
            for entry in dic:
                if entry.get("polish", "").lower() == word:
                    relevant_entries.append(entry)
    return relevant_entries[:50]

# ============================================================
# 4. LOGIKA TŁUMACZENIA (PROMPT)
# ============================================================
def translate_text(input_text):
    if not input_text: return ""
    
    matches = get_relevant_context(input_text, dictionary)
    context_str = "\n".join([
        f"- POL: {m.get('polish')} | SLOV: {m.get('slovian')} | GRAM: {m.get('type and case','')}"
        for m in matches
    ])

    system_prompt = f"""Jesteś rygorystycznym silnikiem tłumaczącym. Twoim językiem pośrednim jest polski.
ZASADA MULTILANGUAGE:
1. Jeśli wejście jest w dowolnym języku (nie słowiańskim), najpierw wewnętrznie przetłumacz je na polski, a potem z polskiego na prasłowiański.
2. Jeśli wejście jest w języku słowiańskim, przetłumacz je na polski, a potem na język użytkownika (kod języka: {browser_lang}).

KRYTYCZNA ZASADA ODMIAN (vuzor.json):
- Twoim źródłem prawdy o końcówkach jest vuzor.json. Jeśli w osnova.json nie ma konkretnej formy (np. miejscownika), MUSISZ ją stworzyć na podstawie wzorców z vuzor.json.
- Przykład: rěka -> rěcě (k > c przed ě), sluga -> sludzě (g > dz przed ě). Stosuj palatalizację rygorystycznie!
- PRZYMIOTNIK ZAWSZE PRZED RZECZOWNIKIEM. "Wojsko Słowiańskie" -> "Slověnьsko Vojьsko". To jest absolutny wymóg.

ZASADA WIELKOŚCI LITER:
- Zachowaj format Case-by-Case (Mati, mati, MATI, mATI).

ALFABET:
- TYLKO łaciński + ě, ę, ǫ, ь.
- CAŁKOWITY ZAKAZ CYRYLICY (poza ь). Nie używaj ъ, а, б, в, г... tylko transkrypcja łacińska.

PROCEDURA:
1. Analiza błędów użytkownika i ich poprawa.
2. Identyfikacja POS (części mowy) i kontekstu.
3. Dopasowanie z osnova.json.
4. Zmiana kolejności (przymiotnik na przód).
5. Rekonstrukcja brakujących odmian na bazie vuzor.json.

Zwróć TYLKO czyste tłumaczenie."""

    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"BAZA:\n{context_str}\n\nWZORY ODMIAN:\n{str(vuzory)[:1000]}\n\nTEKST: {input_text}"}
            ],
            model="llama-3.3-70b-versatile", # Szybszy model dla natychmiastowego efektu
            temperature=0.0
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Błąd: {e}"

# ============================================================
# 5. INTERFEJS UŻYTKOWNIKA (Automatyczny)
# ============================================================
st.title("Perkladačь slověnьskogo ęzyka")

col1, col2 = st.columns(2)

with col1:
    # Wykorzystanie klucza w session_state do wykrywania zmian bez przycisku
    input_val = st.text_area("Vupiši tekst (dowolny język):", key="input_area", placeholder="Wpisz tutaj...")

with col2:
    st.write("Perklad (Slověnьsky / Wybrany język):")
    if input_val:
        with st.spinner("Translating..."):
            result = translate_text(input_val)
            st.markdown(f'<div class="output-container">{result}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="output-container"></div>', unsafe_allow_html=True)

# Automatyczne odświeżanie interfejsu przy każdej zmianie w text_area
if input_val:
    st.caption(f"Język interfejsu dopasowany do: {browser_lang}")
