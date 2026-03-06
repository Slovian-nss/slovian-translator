import streamlit as st
import json
import os
import re
from groq import Groq

# ============================================================
# 1. KONFIGURACJA I STYLIZACJA
# ============================================================
st.set_page_config(page_title="Perkladačь slověnьskogo ęzyka", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTextArea > div > div > textarea { background-color: #1a1a1a; color: #dcdcdc; border: 1px solid #333; }
    .stSuccess { background-color: #050505; border: 1px solid #2e7d32; color: #dcdcdc; font-size: 1.2rem; white-space: pre-wrap; }
    </style>
    """, unsafe_allow_html=True)

# ============================================================
# 2. KONFIGURACJA KLIENTA GROQ
# ============================================================
# Upewnij się, że masz klucz API w Secrets
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

# ============================================================
# 3. ŁADOWANIE BAZY DANYCH
# ============================================================
@st.cache_data
def load_dictionary():
    if not os.path.exists("osnova.json"):
        return {}
    try:
        with open("osnova.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        index = {}
        for entry in data:
            pl = entry.get("polish", "").lower().strip()
            if pl:
                if pl not in index: index[pl] = []
                index[pl].append(entry)
        return index
    except Exception as e:
        st.error(f"Błąd bazy: {e}")
        return {}

dictionary = load_dictionary()

# ============================================================
# 4. USPRAWNIONA LOGIKA POBIERANIA KONTEKSTU (Fuzzy Matching)
# ============================================================
def get_strict_context(text, dic):
    search_text = re.sub(r'[^\w\s]', ' ', text.lower())
    words = search_text.split()
    relevant_entries = []
    
    all_polish_bases = dic.keys()

    for word in words:
        # 1. Szukamy dokładnego dopasowania (dla krótkich słów jak "w", "i")
        if word in dic:
            relevant_entries.extend(dic[word])
            continue
            
        # 2. Szukamy dopasowania rdzenia (Lematyzacja "na piechotę")
        # Jeśli słowo "miastach" zaczyna się tak samo jak "miasto" (pierwsze 4 litery)
        if len(word) >= 4:
            prefix = word[:4]
            for base in all_polish_bases:
                if base.startswith(prefix):
                    relevant_entries.extend(dic[base])
    
    # Deduplikacja wyników
    seen = set()
    unique_entries = []
    for e in relevant_entries:
        identifier = (e['polish'].lower(), e['slovian'].lower())
        if identifier not in seen:
            seen.add(identifier)
            unique_entries.append(e)
            
    return unique_entries

# ============================================================
# 5. INTERFEJS UŻYTKOWNIKA
# ============================================================
st.title("Perkladačь slověnьskogo ęzyka")

user_input = st.text_area("Vupiši slovo alibo rěčenьje:", placeholder="Np. W miastach siła.", height=150)

if user_input:
    with st.spinner("Przetwarzanie..."):
        matches = get_strict_context(user_input, dictionary)
        
        mapping_rules = "\n".join([
            f"POLSKI_LEMAT: '{m['polish']}' -> SŁOWIAŃSKI_RDZEŃ: '{m['slovian']}'"
            for m in matches
        ])

        system_prompt = f"""
Jesteś deterministycznym parserem języka słowiańskiego. 
Twoim zadaniem jest przekształcenie polskiego zdania na język słowiański, używając dostarczonych rdzeni.

--------------------------------------------------
ZASADY DZIAŁANIA:
1. Przeanalizuj polskie słowo (np. "miastach" -> miejscownik, l.mnoga, rodzaj nijaki, lemat: "miasto").
2. Znajdź odpowiedni SŁOWIAŃSKI_RDZEŃ dla tego lematu w dostarczonej liście.
3. Dobierz końcówkę fleksyjną ze swojej bazy wiedzy (vuzor.json), pasującą do przypadku, liczby i rodzaju.
4. Połącz: RDZEŃ + KOŃCÓWKA.

--------------------------------------------------
DANE MAPOWANIA (OSNOVA):
{mapping_rules}

--------------------------------------------------
ZASADY BEZWZGLĘDNE:
1. Jeśli polskiego słowa (lub jego lematu) nie ma na liście mapowania, zwróć: (ne najdeno slova).
2. Wyjątek: Przyimki (np. "w", "na", "z") i spójniki tłumacz automatycznie (np. w -> vu).
3. Zachowaj wielkie litery i interpunkcję.
4. Nie dopisuj żadnych wyjaśnień. Tylko wynik.
"""

        try:
            # Używamy modelu gpt-4o lub llama-3 (zależnie od tego co masz w Groq)
            # Podmień "openai/gpt-oss-120b" na właściwą nazwę modelu w Groq (np. "llama3-8b-8192")
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"TEKST DO KONWERSJI: {user_input}"}
                ],
                model="openai/gpt-oss-120b", 
                temperature=0.0
            )
            response_text = chat_completion.choices[0].message.content.strip()

            st.markdown("### Vynik perklada:")
            st.success(response_text)

        except Exception as e:
            st.error(f"Błąd modelu: {e}")

        if matches:
            with st.expander("Użyte mapowanie z bazy"):
                for m in matches:
                    st.write(f"'{m['polish']}' → `{m['slovian']}`")
