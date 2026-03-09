import streamlit as st
import json
import os
import re
from collections import defaultdict
from groq import Groq

st.set_page_config(page_title="Perkladačь slověnьskogo ęzyka", layout="centered")

st.markdown("""
<style>
.main {background:#0e1117}
.stTextArea textarea {background:#1a1a1a;color:#dcdcdc}
</style>
""", unsafe_allow_html=True)

# ================== GROQ ==================

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ================== ŁADOWANIE ==================

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
    dic = defaultdict(list)

    for entry in data:
        key = entry.get("polish","").lower().strip()
        if key:
            dic[key].append(entry)

    return dic

dictionary = build_dictionary(osnova)

# ================== WYSZUKIWANIE ==================

def get_context(text, dic):

    words = re.findall(r'\w+', text.lower())
    results = []
    seen = set()

    for w in words:

        # dokładne dopasowanie
        if w in dic:
            for e in dic[w]:
                key = (e["polish"], e["slovian"])
                if key not in seen:
                    results.append(e)
                    seen.add(key)

        # prefix search
        elif len(w) >= 4:
            pref = w[:4]

            for base, entries in dic.items():
                if base.startswith(pref):

                    for e in entries:
                        key = (e["polish"], e["slovian"])

                        if key not in seen:
                            results.append(e)
                            seen.add(key)

    return results

# ================== INTERFEJS ==================

st.title("Perkladačь slověnьskogo ęzyka")

user_input = st.text_area(
    "Vupiši slovo alibo rěčenьje:",
    placeholder="Np. W miastach siła.",
    height=150
)

if user_input:

    with st.spinner("Przetwarzanie..."):

        matches = get_context(user_input, dictionary)

        mapping = "\n".join(
            f"PL '{m['polish']}' → SL '{m['slovian']}'"
            for m in matches
        )

        system_prompt = f"""
Jesteś precyzyjnym tłumaczem na język prasłowiański.

Używasz WYŁĄCZNIE słów z danych.

DANE SŁOWNIKOWE:
{mapping}

WZORY:
{json.dumps(vuzor[:20], ensure_ascii=False)}

ZASADY BEZWZGLĘDNE:
1. Jeśli nie ma odmiany słowiańskiego słowa (lub jego podstawowej odmiany), to wtedy napisz w jego miejscu (ne najdeno slova) i tłumacz dalej to co możesz.
2. SZYK: Przymiotniki (oznaczone są one jako: adjective - pridavьnik) i przysłówki (oznaczone są one jako: adverb - prislovok) zawsze są przed rzeczownikami (oznaczone są one jako: noun - jimenьnik).
3. FORMAT: Zachowaj interpunkcję, odwzorowanie, wielkość liter, spacje, odstępy, znaki matematyczne, linkowanie i brak dodatkowego komentarza."""

        try:

            chat = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role":"system","content":system_prompt},
                    {"role":"user","content":user_input}
                ],
                temperature=0,
                max_tokens=800
            )

            result = chat.choices[0].message.content.strip()

            st.markdown("### Vynik perklada:")
            st.success(result)

        except Exception as e:
            st.error(f"Blǫd perklada: {e}")

