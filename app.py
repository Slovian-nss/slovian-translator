import streamlit as st
import json
import os
import re
from collections import defaultdict

# ================== KONFIGURACJA STRONY ==================

st.set_page_config(page_title="Perkladačь slověnьskogo ęzyka", layout="centered")

st.markdown("""
<style>
.main {background:#0e1117}
.stTextArea textarea {background:#1a1a1a;color:#dcdcdc;font-size:1.1rem;}
.stSuccess {background-color: #1e2329; border: 1px solid #4caf50;}
</style>
""", unsafe_allow_html=True)

# ================== ŁADOWANIE DANYCH ==================

@st.cache_data
def load_json(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

osnova = load_json("osnova.json")
vuzor  = load_json("vuzor.json")

# ================== INDEKS SŁOWNIKA ==================

@st.cache_data
def build_dictionary(data):
    # Mapujemy polskie słowa na listę rekordów słownikowych
    dic = defaultdict(list)
    for entry in data:
        key = entry.get("polish","").lower().strip()
        if key:
            dic[key].append(entry)
    return dic

dictionary = build_dictionary(osnova)

# ================== LOGIKA TŁUMACZENIA (SILNIK LOKALNY) ==================

def translate_text(input_text, dic):
    """
    Tłumaczy tekst zachowując interpunkcję, wielkość liter i spacje.
    Zastępuje AI bezpośrednim mapowaniem ze słownika.
    """
    # Tokenizacja: wyłapujemy słowa (\w+) oraz wszystko inne (spacje, znaki interpunkcyjne)
    tokens = re.findall(r'\w+|[^\w\s]|\s+', input_text)
    translated_output = []

    for token in tokens:
        # Jeśli to nie jest słowo (np. kropka, spacja, przecinek), dodaj bez zmian
        if not re.match(r'\w+', token):
            translated_output.append(token)
            continue
        
        lower_token = token.lower().strip()
        found_slovian = None

        # 1. Dokładne dopasowanie
        if lower_token in dic:
            # Wybieramy pierwsze znaczenie (można tu dodać logikę wyboru części mowy)
            found_slovian = dic[lower_token][0]["slovian"]
        
        # 2. Próba dopasowania po rdzeniu (min. 4 litery)
        elif len(lower_token) >= 4:
            pref = lower_token[:4]
            for base, entries in dic.items():
                if base.startswith(pref):
                    found_slovian = entries[0]["slovian"]
                    break
        
        # 3. Finalizacja wyniku
        if found_slovian:
            # Zachowanie wielkości liter (jeśli oryginał był z dużej)
            if token[0].isupper():
                found_slovian = found_slovian.capitalize()
            translated_output.append(found_slovian)
        else:
            # Zasada bezwzględna nr 1: ne najdeno slova
            translated_output.append("(ne najdeno slova)")

    return "".join(translated_output)

# ================== INTERFEJS UŻYTKOWNIKA ==================

st.title("Perkladačь slověnьskogo ęzyka")
st.subheader("Lokalny silnik tłumaczenia (bez AI)")

user_input = st.text_area(
    "Vupiši slovo alibo rěčenьje:",
    placeholder="Np. W miastach siła.",
    height=150
)

if user_input:
    with st.spinner("Przetwarzanie danych..."):
        # Wykonanie tłumaczenia lokalnie
        result = translate_text(user_input, dictionary)

    st.markdown("### Vynik perklada:")
    st.success(result)

    # Sekcja pomocnicza: podgląd słów użytych w tekście
    with st.expander("Analiza słownikowa użytych wyrazów"):
        words = re.findall(r'\w+', user_input.lower())
        found_any = False
        for w in set(words):
            if w in dictionary:
                found_any = True
                for entry in dictionary[w]:
                    st.write(f"📖 **{entry['polish']}** → `{entry['slovian']}` ({entry.get('type', '???')})")
        if not found_any:
            st.info("Nie znaleziono dopasowań w słowniku osnova.json.")

# Stopka
st.divider()
st.caption("Aplikacja działa w trybie offline (Local Logic). Wykorzystuje osnova.json jako bazę wiedzy.")
