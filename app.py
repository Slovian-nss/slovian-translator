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

# ================== ŁADOWANIE ==================

@st.cache_data
def load_json(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

osnova = load_json("osnova.json")

# ================== SŁOWNIKI ==================

@st.cache_data
def build_dict(data):
    pl_to_slo = {}
    slo_to_pl = {}

    for entry in data:
        pol = entry.get("polish", "").lower().strip()
        slo = entry.get("slovian", "").strip()

        if pol and slo:
            pl_to_slo[pol] = slo
            slo_to_pl[slo.lower()] = pol

    return pl_to_slo, slo_to_pl

pl_to_slo, slo_to_pl = build_dict(osnova)

# ================== TŁUMACZENIE ==================

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

def google_translate(text, source, target):
    try:
        return GoogleTranslator(source=source, target=target).translate(text)
    except:
        return "(błąd tłumaczenia)"

# ================== UI ==================

st.title("Perkladačь slověnьskogo ęzyka")

mode = st.selectbox(
    "Tryb:",
    [
        "Dowolny → słowiański",
        "Słowiański → dowolny"
    ]
)

user_input = st.text_area("Vupiši tekst:", height=150)

target_lang = st.text_input("Kod języka docelowego:", value="en")

# ================== LOGIKA ==================

if user_input:
    with st.spinner("Perkladajų..."):

        if mode == "Dowolny → słowiański":
            pl = google_translate(user_input, "auto", "pl")
            result = translate_pl_to_slo(pl)

        else:
            pl = translate_slo_to_pl(user_input)
            result = google_translate(pl, "pl", target_lang)

        st.markdown("### Vynik perklada:")
        st.success(result)
