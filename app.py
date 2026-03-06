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
    .stTextInput > div > div > input { background-color: #1a1a1a; color: #dcdcdc; border: 1px solid #333; }
    .stTextArea > div > div > textarea { background-color: #1a1a1a; color: #dcdcdc; border: 1px solid #333; }
    .stSuccess { background-color: #050505; border: 1px solid #2e7d32; color: #dcdcdc; font-size: 1.2rem; white-space: pre-wrap; }
    </style>
    """, unsafe_allow_html=True)

# ============================================================
# 2. KONFIGURACJA KLIENTA GROQ
# ============================================================
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
# 4. PRECYZYJNA LOGIKA POBIERANIA KONTEKSTU (Słowa + Frazy)
# ============================================================
def get_strict_context(text, dic):
    # Wyciągamy słowa, ignorując interpunkcję dla wyszukiwania
    search_text = re.sub(r'[^\w\s]', ' ', text.lower())
    words = search_text.split()
    relevant_entries = []
    
    for word in words:
        if word in dic:
            relevant_entries.extend(dic[word])
    
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

# Używamy text_area zamiast text_input dla obsługi wielu linii
user_input = st.text_area("Vupiši slovo alibo rěčenьje:", placeholder="", height=200)

if user_input:
    with st.spinner("Przetwarzanie tekstu..."):
        matches = get_strict_context(user_input, dictionary)
        
        # Przygotowanie bardzo technicznej instrukcji mapowania
        mapping_rules = "\n".join([
            f"MAPUJ: '{m['polish']}' NA '{m['slovian']}'"
            for m in matches
        ])

        system_prompt = """
Jesteś deterministycznym silnikiem fleksyjnym dla rekonstruowanego języka słowiańskiego.

Twoim jedynym zadaniem jest generowanie poprawnych form gramatycznych na podstawie:
- osnova.json
- vuzor.json

Nie jesteś tłumaczem. Jesteś generatorem odmian.

--------------------------------------------------
STRUKTURA DANYCH
--------------------------------------------------

osnova.json
Zawiera słownik podstawowy:

{
  "polskie_slowo": {
      "rdzen": "slowianski_rdzen",
      "vuzor": "nazwa_wzoru"
  }
}

Przykład:

{
  "ogród": {
      "rdzen": "obgord",
      "vuzor": "gord"
  }
}

vuzor.json
Zawiera pełne paradygmaty odmiany dla wzorów.

Przykład struktury:

{
 "gord": {
   "singular": {
      "nom": "",
      "gen": "a",
      "dat": "u",
      "acc": "",
      "loc": "ě",
      "ins": "om"
   },
   "plural": {
      "nom": "y",
      "gen": "ov",
      "dat": "om",
      "acc": "y",
      "loc": "ěh",
      "ins": "ami"
   }
 }
}

Końcówki z vuzor.json są jedynym źródłem fleksji.

--------------------------------------------------
ALGORYTM (OBOWIĄZKOWY)
--------------------------------------------------

Dla każdego słowa wejściowego wykonaj dokładnie:

1. Podziel tekst na tokeny:
   słowa, liczby, interpunkcja.

2. Jeśli token jest przyimkiem (np. w, na, do, z, od, po):
   przetłumacz go tylko przez mapowanie słownikowe.
   NIE odmienia się.

3. Jeśli token jest rzeczownikiem / przymiotnikiem:

   a) znajdź go w osnova.json  
   b) pobierz:
      - rdzen
      - vuzor

4. Określ przypadek i liczbę z kontekstu zdania.

Przykłady:

w + LOC  
do + GEN  
z + GEN  
na + LOC/ACC  

5. W vuzor.json znajdź końcówkę:

vuzor → liczba → przypadek

6. Zbuduj słowo:

slowianski_rdzen + koncowka

Przykład:

rdzen: obgord  
loc singular końcówka: ě  

wynik:
obgordě

7. Zastąp token wynikiem.

--------------------------------------------------
SZYK
--------------------------------------------------

Przymiotnik zawsze przed rzeczownikiem.

--------------------------------------------------
ZASADY BEZWZGLĘDNE
--------------------------------------------------

1. NIE wolno kopiować polskich końcówek.
2. NIE wolno zgadywać form.
3. Jeśli słowo nie istnieje w osnova.json:

(ne najdeno slova)

4. Zachowuj:

- interpunkcję
- wielkie litery
- odstępy
- kolejność zdań

5. NIE dodawaj komentarzy ani wyjaśnień.
Zwracaj tylko wynikowy tekst.

--------------------------------------------------
PRZYKŁAD

Wejście:

"W ogrodzie."

Analiza:

w → vu  
ogród → obgord  
przypadek → loc singular  
końcówka → ě  

Wynik:

"Vu obgordě."
"""

        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"LISTA MAPOWANIA:\n{mapping_rules}\n\nTEKST ŹRÓDŁOWY:\n{user_input}"}
                ],
                model="openai/gpt-oss-120b",
                temperature=0.0
            )
            response_text = chat_completion.choices[0].message.content.strip()

            # Wyświetlanie wyniku
            st.markdown("### Vynik perklada:")
            st.success(response_text)

        except Exception as e:
            st.error(f"Błąd modelu: {e}")

        if matches:
            with st.expander("Użyte mapowanie z bazy"):
                for m in matches:
                    st.write(f"'{m['polish']}' → `{m['slovian']}`")












