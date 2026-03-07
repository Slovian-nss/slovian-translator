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

# ================== OPTYMALIZACJA DANYCH ==================
@st.cache_data
def load_database():
    def load_json(name):
        if not os.path.exists(name): return []
        with open(name, "r", encoding="utf-8") as f: return json.load(f)
    return load_json("vuzor.json") + load_json("osnova.json")

DATA = load_database()

def get_mini_context(text):
    # Szukamy tylko konkretnych słów, ograniczając liczbę rekordów do minimum
    words = re.findall(r'\b\w+\b', text.lower())
    matches = []
    seen = set()

    for w in words:
        count = 0
        for entry in DATA:
            pl = entry.get("polish", "").lower()
            if w == pl:
                key = (entry['polish'], entry['slovian'], entry.get('type and case', ''))
                if key not in seen:
                    matches.append(entry)
                    seen.add(key)
                    count += 1
            if count >= 5: break # Max 5 form na jedno słowo, by nie zapchać limitu 413
    return matches

# ================== LOGIKA TŁUMACZENIA ==================

st.title("Perkladačь slověnьskogo ęzyka")
user_input = st.text_area("Vupiši tekst:", placeholder="W moim ogrodzie 10+5%.", height=150)

if user_input:
    with st.spinner("Tłumaczenie (optymalizacja limitów)..."):
        mini_dict = get_mini_context(user_input)
        
        # Tworzymy bardzo krótki słownik
        formatted_db = "\n".join([
            f"{m['polish']}={m['slovian']} ({m.get('type and case', '')})"
            for m in mini_dict
        ])

        system_prompt = f"""Jesteś tłumaczem. Przetłumacz tekst, zachowując ORYGINALNE SPACJE, WIELKOŚĆ LITER I INTERPUNKCJĘ.
Dane:
{formatted_db}

Zasady:
1. 'w'/'W' -> 'Vu'.
2. Po 'Vu' użyj formy 'noun' + 'locative' (np. 'obgordě').
3. Nie tłumacz linków ani matematyki.
4. Jeśli brak słowa, zostaw polskie.
Zwróć TYLKO wynik."""

        try:
            # Używamy mniejszego modelu, który ma wyższe limity TPM
            response = client.chat.completions.create(
                model="llama3-8b-8192", 
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0
            )
            
            st.markdown("### Vynik perklada:")
            st.success(response.choices[0].message.content.strip())
            
        except Exception as e:
            if "413" in str(e):
                st.error("Zbyt długi tekst! Skróć go lub usuń skomplikowane słowa.")
            else:
                st.error(f"Błąd: {e}")

    with st.expander("Użyte rekordy (max 5 na słowo)"):
        st.table(mini_dict)
