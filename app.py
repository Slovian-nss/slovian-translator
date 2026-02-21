import streamlit as st
import json
import os
import re
import sys
from openai import OpenAI

# ============================================================
# UTF-8 FIX (KLUCZOWE)
# ============================================================

os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

# ============================================================
# KONFIGURACJA
# ============================================================

st.set_page_config(
    page_title="Perkladačь slověnьskogo ęzyka",
    layout="centered"
)

st.markdown("""
<style>
.main { background-color: #0e1117; }
.stTextInput > div > div > input {
    background-color: #1a1a1a;
    color: #dcdcdc;
    border: 1px solid #333;
}
.stSuccess {
    background-color: #050505;
    border: 1px solid #2e7d32;
    color: #dcdcdc;
    font-size: 1.2rem;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# OPENAI CLIENT
# ============================================================

client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

MODEL = "gpt-4o-mini"

# ============================================================
# ŁADOWANIE SŁOWNIKA
# ============================================================

@st.cache_data
def load_dictionary():

    if not os.path.exists("osnova.json"):
        return {}

    with open("osnova.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    index = {}

    for entry in data:

        pl = entry.get("polish", "").lower().strip()

        if pl:
            if pl not in index:
                index[pl] = []

            index[pl].append(entry)

    return index


dictionary = load_dictionary()

# ============================================================
# RAG
# ============================================================

def get_relevant_context(text, dic):

    search_text = re.sub(r'[^\w\s]', '', text.lower())
    words = search_text.split()

    relevant_entries = []

    for word in words:

        if word in dic:
            relevant_entries.extend(dic[word])

        elif len(word) > 3:

            for key in dic.keys():

                if word.startswith(key[:4]):
                    relevant_entries.extend(dic[key])

    seen = set()
    unique = []

    for e in relevant_entries:

        identifier = (e['slovian'], e.get('type and case', ''))

        if identifier not in seen:

            seen.add(identifier)
            unique.append(e)

    return unique[:40]

# ============================================================
# PROMPT
# ============================================================

SYSTEM_PROMPT = """
Jesteś rygorystycznym silnikiem tłumaczącym z języka polskiego na język prasłowiański.

Używaj WYŁĄCZNIE alfabetu łacińskiego oraz znaków:
ě ę ǫ š č ž ь

Zwróć TYLKO tłumaczenie.
Bez komentarzy.
Bez wyjaśnień.
"""

# ============================================================
# FUNKCJA TŁUMACZENIA
# ============================================================

def translate(user_input, context_str):

    completion = client.chat.completions.create(

        model=MODEL,

        temperature=0,

        messages=[

            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },

            {
                "role": "user",
                "content": f"BAZA:\n{context_str}\n\nDO TŁUMACZENIA:\n{user_input}"
            }

        ]

    )

    return completion.choices[0].message.content.strip()


# ============================================================
# UI
# ============================================================

st.title("Perkladačь slověnьskogo ęzyka")

if "last" not in st.session_state:
    st.session_state.last = ""

if "result" not in st.session_state:
    st.session_state.result = ""

user_input = st.text_input(
    "Vupiši slovo abo rěčenьje:",
    placeholder=""
)

# AUTO TRANSLATE
if user_input != st.session_state.last:

    st.session_state.last = user_input

    if user_input:

        with st.spinner("Perklad..."):

            matches = get_relevant_context(
                user_input,
                dictionary
            )

            context_str = "\n".join([

                f"{m['polish']} → {m['slovian']} ({m.get('type and case','')})"

                for m in matches

            ])

            try:

                result = translate(
                    user_input,
                    context_str
                )

                st.session_state.result = result

            except Exception as e:

                st.session_state.result = f"ERROR: {str(e)}"


# OUTPUT
if st.session_state.result:

    st.markdown("### Vynik perklada:")

    st.success(st.session_state.result)
