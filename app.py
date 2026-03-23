import streamlit as st
import json
import os
import re
from collections import defaultdict

st.set_page_config(page_title="Perkladačь slověnьskogo ęzyka", layout="centered")

st.markdown("""
<style>
.main {background:#0e1117}
.stTextArea textarea {background:#1a1a1a;color:#dcdcdc}
</style>
""", unsafe_allow_html=True)

# ================== ŁADOWANIE DANYCH ==================

@st.cache_data
def load_json(filename):
    if not os.path.exists(filename):
        return []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

osnova = load_json("osnova.json")

# ================== BUDOWA SŁOWNIKA LOKALNEGO ==================

@st.cache_data
def build_simple_dict(data):
    # Tworzymy mapowanie: polskie_slowo -> slowianskie_slowo
    dic = {}
    for entry in data:
        pol = entry.get("polish", "").lower().strip()
        slo = entry.get("slovian", "").strip()
        if pol and slo:
            # Jeśli jest kilka znaczeń, bierzemy pierwsze napotkane
            if pol not in dic:
                dic[pol] = slo
    return dic

dictionary = build_simple_dict(osnova)

# ================== LOGIKA TŁUMACZENIA BEZ API ==================

def local_translate(text, dic):
    # Reguła podziału zachowująca interpunkcję i spacje
    # Rozbijamy na słowa (\w+) i wszystko inne ([^\w\s] lub spacje)
    tokens = re.findall(r'\w+|[^\w\s]|\s+', text)
    
    translated_parts = []
    
    for token in tokens:
        # Sprawdzamy czy token to słowo
        if re.match(r'\w+', token):
            lower_token = token.lower()
            
            # 1. Szukamy dokładnego dopasowania
            if lower_token in dic:
                replacement = dic[lower_token]
            # 2. Szukamy po prefiksie (minimum 4 litery)
            else:
                replacement = "(ne najdeno slova)"
                if len(lower_token) >= 4:
                    pref = lower_token[:4]
                    for pol_word, slo_word in dic.items():
                        if pol_word.startswith(pref):
                            replacement = slo_word
                            break
            
            # Zachowanie wielkości liter (prosta logika)
            if token.istitle():
                replacement = replacement.capitalize()
            elif token.isupper():
                replacement = replacement.upper()
                
            translated_parts.append(replacement)
        else:
            # Jeśli to spacja lub interpunkcja, dodaj bez zmian
            translated_parts.append(token)
            
    return "".join(translated_parts)

# ================== INTERFEJS UŻYTKOWNIKA ==================

st.title("Perkladačь slověnьskogo ęzyka")
st.caption("Tryb lokalny (bez API) - tłumaczenie słownikowe")

user_input = st.text_area(
    "Vupiši slovo alibo rěčenьje:",
    placeholder="Np. W miastach siła.",
    height=150
)

if user_input:
    with st.spinner("Perkladajų..."):
        # Wywołujemy lokalną funkcję zamiast Groq
        result = local_translate(user_input, dictionary)
        
        st.markdown("### Vynik perklada:")
        st.success(result)

# Stopka informacyjna
st.divider()
st.info("💡 Tłumacz działa teraz w trybie 1:1 na podstawie pliku osnova.json. Nie wymaga połączenia z internetem ani kluczy API.")
