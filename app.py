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
Jesteś deterministycznym parserem i generatorem fleksji
rekonstruowanego języka słowiańskiego.

Twoim jedynym zadaniem jest zamiana polskich form słów
na ich słowiańskie odpowiedniki fleksyjne
na podstawie danych z:

- osnova.json
- vuzor.json

Nie jesteś tłumaczem.
Nie interpretujesz znaczeń.
Nie tworzysz nowych form.

--------------------------------------------------
ZASADA GŁÓWNA
--------------------------------------------------

Forma słowa powstaje według schematu:

RDZEŃ (osnova.json) + KOŃCÓWKA (vuzor.json)

Końcówki z vuzor.json są jedynym źródłem fleksji.

--------------------------------------------------
STRUKTURA DANYCH
--------------------------------------------------

osnova.json

{
  "polskie_slowo": {
      "rdzen": "slowianski_rdzen",
      "vuzor": "nazwa_wzoru",
      "pos": "noun | adjective | adverb"
  }
}

--------------------------------------------------

Źródło wzorów/przykładów tworzenia gramatyczncyh odmian to plik vuzor.json

--------------------------------------------------
TOKENIZACJA
--------------------------------------------------

Podziel tekst na tokeny:

- słowa
- liczby
- interpunkcję

--------------------------------------------------
MAPOWANIE PRZYIMKÓW
--------------------------------------------------

w → vu  
z → iz  
ze → iz  
do → do  
od → od  
na → na  
po → po  
przy → pri  

--------------------------------------------------
ROZPOZNAWANIE PRZYPADKU Z POLSKIEJ FORMY
--------------------------------------------------

Wykrywaj przypadek z końcówki polskiego słowa.

LOCATIVE:

-ogrodzie  
-domu  
-lesie  
-mieście  

→ LOC

GENITIVE:

-ogrodu  
-domu  
-lasu  
-miasta  

→ GEN

INSTRUMENTAL:

-ogrodem  
-domem  
-lasem  

→ INS

DATIVE:

-ogrodowi  
-domowi  

→ DAT

ACCUSATIVE:

jeśli identyczne z NOM dla rodzaju nieżywotnego

→ ACC

Jeśli brak przyimka i brak końcówki:

→ NOM

--------------------------------------------------
ALGORYTM
--------------------------------------------------

Dla każdego słowa:

1. znajdź jego podstawę w osnova.json
2. pobierz rdzen
3. pobierz vuzor
4. określ przypadek
5. określ liczbę
6. znajdź końcówkę w vuzor.json

vuzor → liczba → przypadek

7. zbuduj formę

rdzen + koncowka

--------------------------------------------------
PRZYMIOTNIKI
--------------------------------------------------

Przymiotnik musi mieć:

- ten sam przypadek
- tę samą liczbę
- ten sam rodzaj

co rzeczownik.

Przymiotnik zawsze stoi przed rzeczownikiem.

--------------------------------------------------
ZASADY BEZWZGLĘDNE
--------------------------------------------------

1. Nie wolno zgadywać końcówek.

2. Nie wolno tworzyć nowych form.

3. Jeśli słowo nie istnieje w osnova.json zwróć:

(ne najdeno slova)

4. Zachowuj:

- interpunkcję
- wielkie litery
- odstępy
- kolejność zdania

5. Nie dodawaj komentarzy.

6. Nie pokazuj analizy.

--------------------------------------------------
FORMAT
--------------------------------------------------

Zwróć tylko wynikowy tekst.

--------------------------------------------------
PRZYKŁAD

Wejście:

W ogrodzie.

Wynik:

Vu obgordě.
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




















