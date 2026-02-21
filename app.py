import streamlit as st
import json
import os
import re
import time
from groq import Groq

# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="Perkladačь slověnьskogo ęzyka",
    layout="centered"
)

# ============================================================
# AUTO REFRESH (KLUCZ DO REALTIME)
# ============================================================

st.markdown(
    """
    <script>
    setTimeout(function(){
        window.parent.document.querySelector('section.main').dispatchEvent(new Event("click"))
    }, 300);
    </script>
    """,
    unsafe_allow_html=True
)

# ============================================================
# STYLE DEEPL
# ============================================================

st.markdown("""
<style>

textarea {
    background-color: #1a1d24 !important;
    color: white !important;
    font-size: 20px !important;
    border-radius: 12px !important;
}

.result-box {
    background-color: #1a1d24;
    padding: 20px;
    border-radius: 12px;
    font-size: 22px;
    margin-top: 10px;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# API
# ============================================================

GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)

MODEL = "openai/gpt-oss-120b"

# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_osnova():

    if not os.path.exists("osnova.json"):
        return {}

    with open("osnova.json", encoding="utf-8") as f:
        data = json.load(f)

    index = {}

    for entry in data:

        key = entry["polish"].lower()

        if key not in index:
            index[key] = []

        index[key].append(entry)

    return index


@st.cache_data
def load_vuzor():

    if not os.path.exists("vuzor.json"):
        return {}

    with open("vuzor.json", encoding="utf-8") as f:
        return json.load(f)


OSNOVA = load_osnova()
VUZOR = load_vuzor()

# ============================================================
# SESSION STATE
# ============================================================

if "input" not in st.session_state:
    st.session_state.input = ""

if "output" not in st.session_state:
    st.session_state.output = ""

if "processing" not in st.session_state:
    st.session_state.processing = False

# ============================================================
# PROMPT (PEŁNY, RYGORYSTYCZNY)
# ============================================================

SYSTEM_PROMPT = """
Jesteś absolutnie deterministycznym silnikiem tłumaczenia języka słowiańskiego.

ARCHITEKTURA:

pivot zawsze przez polski:

dowolny język → polski → słowiański

słowiański → polski → język interfejsu


ŹRÓDŁA PRAWDY:

osnova.json
vuzor.json


TWORZENIE ODMIAN:

jeśli forma nie istnieje:

użyj wyłącznie vuzor.json

nigdy nie zgaduj

stosuj palatalizacje:

k→c przed ě
g→dz przed ě
h→z przed ě


ZGODNOŚĆ:

przymiotnik zawsze przed rzeczownikiem

zgodność:

przypadek
rodzaj
liczba


ALFABET:

łaciński
ě ę ǫ ь

zakaz cyrylicy


BRAK:

(ne najdeno slova)


OUTPUT:

tylko tłumaczenie
"""

# ============================================================
# CONTEXT
# ============================================================

def get_context(text):

    words = re.findall(r'\w+', text.lower())

    results = []

    for word in words:

        if word in OSNOVA:

            results.extend(OSNOVA[word])

    unique = {}

    for r in results:

        unique[r["slovian"]] = r

    return list(unique.values())

# ============================================================
# TRANSLATE
# ============================================================

@st.cache_data(ttl=3600)
def translate(text, context_json, vuzor_json):

    completion = client.chat.completions.create(

        model=MODEL,

        temperature=0,

        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content":
                f"""
OSNOVA:
{context_json}

VUZOR:
{vuzor_json}

TEXT:
{text}
"""
            }
        ]
    )

    return completion.choices[0].message.content.strip()

# ============================================================
# UI
# ============================================================

st.title("Perkladačь")

user_input = st.text_area(
    "",
    value=st.session_state.input,
    height=150
)

# ============================================================
# REALTIME DETECTION
# ============================================================

if user_input != st.session_state.input and not st.session_state.processing:

    st.session_state.input = user_input

    st.session_state.processing = True

    if user_input.strip() == "":

        st.session_state.output = ""

    else:

        context = get_context(user_input)

        context_json = json.dumps(context, ensure_ascii=False)

        vuzor_json = json.dumps(VUZOR, ensure_ascii=False)

        try:

            result = translate(
                user_input,
                context_json,
                vuzor_json
            )

            st.session_state.output = result

        except Exception as e:

            st.session_state.output = str(e)

    st.session_state.processing = False

# ============================================================
# OUTPUT
# ============================================================

st.markdown(
    f'<div class="result-box">{st.session_state.output}</div>',
    unsafe_allow_html=True
)
