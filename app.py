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
.stSuccess {background-color: #1e2329; border: 1px solid #4caf50; font-size: 1.3rem;}
</style>
""", unsafe_allow_html=True)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ================== ŁADOWANIE BAZY ==================
@st.cache_data
def load_database():
    def load_json(name):
        if not os.path.exists(name): return []
        with open(name, "r", encoding="utf-8") as f: return json.load(f)
    return load_json("vuzor.json") + load_json("osnova.json")

DATA = load_database()

# ================== PRZYGOTOWANIE KONTEKSTU ==================
def get_precise_dictionary(text):
    # Wyciągamy tylko słowa (bez znaków specjalnych i linków) do szukania w bazie
    words = re.findall(r'\b\w+\b', text.lower())
    matches = []
    seen = set()

    for w in words:
        stem = w[:4] if len(w) >= 4 else w
        for entry in DATA:
            pl = entry.get("polish", "").lower()
            if w == pl or (len(w) >= 4 and pl.startswith(stem)):
                key = (entry['polish'], entry['slovian'], entry.get('type and case', ''))
                if key not in seen:
                    matches.append(entry)
                    seen.add(key)
    return matches

# ================== INTERFEJS I LOGIKA ==================
st.title("Perkladačь slověnьskogo ęzyka")
user_input = st.text_area("Vupiši tekst:", placeholder="W moim ogrodzie (100% poprawnie).", height=150)

if user_input:
    with st.spinner("Przetwarzanie tekstu z zachowaniem formatowania..."):
        dictionary = get_precise_dictionary(user_input)
        
        formatted_db = "\n".join([
            f"- PL: {m['polish']} | SL: {m['slovian']} | TAG: {m.get('type and case', '')}"
            for m in dictionary
        ])

        system_prompt = f"""Jesteś precyzyjnym tłumaczem. 
TWOJE ZADANIE: Przetłumacz słowa na język prasłowiański, ale ZACHOWAJ NIENARUSZONE:
1. Wielkość liter (jeśli polskie słowo jest z dużej, słowiańskie też musi być).
2. Interpunkcję (kropki, przecinki, nawiasy).
3. Znaki matematyczne (+, =, %, cyfry).
4. Linki i adresy URL.
5. Dokładne odstępy i znaki nowej linii.

DANE SŁOWNIKOWE:
{formatted_db}

ZASADY GRAMATYKI:
- 'w' -> 'Vu'
- Po 'Vu' szukaj formy 'noun' + 'locative' (np. 'obgordě' zamiast 'obgordjati').
- Słowo 'są' -> 'sǫtь'.
- Jeśli słowa nie ma w danych, zostaw polskie słowo w nawiasie (nie najdeno).

ODPOWIEDZ TYLKO PRZETŁUMACZONYM TEKSTEM."""

        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0
            )
            
            translation = response.choices[0].message.content.strip()
            st.markdown("### Vynik perklada:")
            st.success(translation)
            
        except Exception as e:
            st.error(f"Błąd: {e}")

    with st.expander("Szczegóły techniczne"):
        st.write("Wykryte słowa do tłumaczenia:")
        st.table(dictionary)

