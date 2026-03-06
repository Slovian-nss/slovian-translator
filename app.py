import streamlit as st
import json
import os
import re
from groq import Groq

# ============================================================
# 1. KONFIGURACJA I ŁADOWANIE DANYCH
# ============================================================
st.set_page_config(page_title="Perkladačь slověnьskogo ęzyka", layout="centered")

@st.cache_data
def load_json_file(filename):
    if not os.path.exists(filename):
        return None
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

# Wczytujemy oba pliki do pamięci
osnova_data = load_json_file("osnova.json")
vuzor_data = load_json_file("vuzor.json")

def find_in_osnova(word, data):
    if not data: return []
    word = word.lower()
    matches = []
    for entry in data:
        # Szukamy czy polskie słowo pasuje do bazy (lematyzacja)
        if word.startswith(entry.get("polish", "").lower()[:4]):
            matches.append(entry)
    return matches

# ============================================================
# 2. LOGIKA APKI
# ============================================================
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

st.title("Perkladačь slověnьskogo ęzyka")
user_input = st.text_area("Vupiši slovo alibo rěčenьje:", height=150)

if user_input:
    with st.spinner("Analiza gramatyczna..."):
        # Pobieramy kontekst z osnova.json dla słów użytkownika
        words = re.sub(r'[^\w\s]', ' ', user_input).split()
        relevant_osnova = []
        for w in words:
            relevant_osnova.extend(find_in_osnova(w, osnova_data))

        # Przygotowujemy dane dla modelu (wstrzykujemy zawartość plików!)
        osnova_ctx = json.dumps(relevant_osnova, ensure_ascii=False, indent=2)
        vuzor_ctx = json.dumps(vuzor_data, ensure_ascii=False, indent=2)

        system_prompt = f"""
Jesteś deterministycznym parserem i generatorem fleksji. 
Twoim zadaniem jest zamiana polskich form na słowiańskie WYŁĄCZNIE na podstawie dostarczonych danych.

DANE Z PLIKU OSNOVA.JSON (Rdzenie):
{osnova_ctx}

DANE Z PLIKU VUZOR.JSON (Wzorce odmiany):
{vuzor_ctx}

ALGORYTM DZIAŁANIA:
1. Dla każdego słowa w tekście określ jego polskie cechy: Przypadek, Liczba, Rodzaj, Żywotność.
2. Znajdź to słowo w powyższych danych OSNOVA.JSON, aby uzyskać słowiański RDZEŃ.
3. Znajdź w VUZOR.JSON słowo o najbardziej zbliżonej strukturze/odmianie (wzorzec).
4. Zastosuj końcówkę z wzorca VUZOR dla ustalonego Przypadku i Liczby do słowiańskiego RDZENIA.

ZASADY BEZWZGLĘDNE:
- Nie tłumacz słów, których nie ma w OSNOVA.JSON (zwróć wtedy: (ne najdeno slova)).
- Nie używaj własnej wiedzy o językach – tylko dane z JSON.
- Zachowaj interpunkcję i wielkie litery.
- Zwróć tylko wynikowy tekst.
"""

        try:
            # Używamy najnowszego modelu Llama 3.3
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"TEKST: {user_input}"}
                ],
                model="openai/gpt-oss-120b", 
                temperature=0.0
            )
            
            st.markdown("### Vynik perklada:")
            st.success(chat_completion.choices[0].message.content.strip())
            
        except Exception as e:
            st.error(f"Błąd modelu: {e}")

