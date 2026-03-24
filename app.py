import streamlit as st
import json
import os
import re
from deep_translator import GoogleTranslator

st.set_page_config(page_title="Perkladačь slověnьskogo ęzyka", layout="centered")

st.markdown("""
<style>
.main {background:#0e1117}
.stTextArea textarea {background:#1a1a1a;color:#dcdcdc}
</style>
""", unsafe_allow_html=True)

# ================== ŁADOWANIE SŁOWNIKA ==================

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

# ================== SŁOWNIK POLSKI → SŁOWIAŃSKI ==================

@st.cache_data
def build_dict(data):
    dic = {}
    reverse_dic = {}

    for entry in data:
        pol = entry.get("polish", "").lower().strip()
        slo = entry.get("slovian", "").strip()

        if pol and slo:
            dic[pol] = slo
            reverse_dic[slo.lower()] = pol

    return dic, reverse_dic

pl_to_slo, slo_to_pl = build_dict(osnova)

# ================== PROSTE TŁUMACZENIE SŁOWNIKOWE ==================

def translate_pl_to_slo(text):
    tokens = re.findall(r'\w+|[^\w\s]|\s+', text)
    result = []

    for token in tokens:
        if re.match(r'\w+', token):
            lower = token.lower()
            translated = pl_to_slo.get(lower, token)

            if token.istitle():
                translated = translated.capitalize()
            elif token.isupper():
                translated = translated.upper()

            result.append(translated)
        else:
            result.append(token)

    return "".join(result)


def translate_slo_to_pl(text):
    tokens = re.findall(r'\w+|[^\w\s]|\s+', text)
    result = []

    for token in tokens:
        if re.match(r'\w+', token):
            lower = token.lower()
            translated = slo_to_pl.get(lower, token)

            if token.istitle():
                translated = translated.capitalize()
            elif token.isupper():
                translated = translated.upper()

            result.append(translated)
        else:
            result.append(token)

    return "".join(result)

# ================== GOOGLE TRANSLATE ==================

def google_translate(text, source, target):
    try:
        return GoogleTranslator(source=source, target=target).translate(text)
    except:
        return "(błąd tłumaczenia API)"

# ================== INTERFEJS ==================

st.title("Perkladačь slověnьskogo ęzyka")

mode = st.selectbox(
    "Tryb:",
    [
        "Dowolny → słowiański",
        "Słowiański → dowolny"
    ]
)

user_input = st.text_area(
    "Vupiši tekst:",
    height=150
)

target_lang = st.text_input("Kod języka docelowego (np. en, de, fr):", value="en")

if user_input:
    with st.spinner("Perkladajų..."):

        if mode == "Dowolny → słowiański":
            # 1. dowolny → polski
            pl = google_translate(user_input, "auto", "pl")

            # 2. polski → słowiański
            slo = translate_pl_to_slo(pl)

            st.markdown("### Polski (pośredni):")
            st.info(pl)

            st.markdown("### Słowiański:")
            st.success(slo)

        elif mode == "Słowiański → dowolny":
            # 1. słowiański → polski
            pl = translate_slo_to_pl(user_input)

            # 2. polski → docelowy
            out = google_translate(pl, "pl", target_lang)

            st.markdown("### Polski (pośredni):")
            st.info(pl)

            st.markdown("### Wynik końcowy:")
            st.success(out)

st.divider()
st.info("💡 Pipeline: Google → polski → prasłowiański (lub odwrotnie)")
