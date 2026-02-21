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
# STYLE (DEEPL)
# ============================================================

st.markdown("""
<style>

textarea {
    background-color: #1a1d24 !important;
    color: white !important;
    font-size: 20px !important;
    border-radius: 12px !important;
}

.result {
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
# CACHE LOAD
# ============================================================

@st.cache_data
def load_osnova():

    if not os.path.exists("osnova.json"):
        return {}

    with open("osnova.json", encoding="utf-8") as f:
        data = json.load(f)

    index = {}

    for entry in data:

        pl = entry["polish"].lower()

        if pl not in index:
            index[pl] = []

        index[pl].append(entry)

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
# FAST CACHE RESULTS
# ============================================================

@st.cache_data(ttl=3600)
def cached_translate(text, context_str, vuzor_str):

    SYSTEM_PROMPT = """
Tłumacz deterministycznie.

Pivot zawsze przez polski.

Używaj wyłącznie osnova.json i vuzor.json.

Generuj odmiany tylko według vuzor.json.

Zwróć tylko tłumaczenie.
"""

    completion = client.chat.completions.create(

        model=MODEL,

        temperature=0,

        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"""
OSNOVA:
{context_str}

VUZOR:
{vuzor_str}

TEKST:
{text}
"""
            }
        ]

    )

    return completion.choices[0].message.content.strip()

# ============================================================
# FIND CONTEXT
# ============================================================

def get_context(text):

    words = re.findall(r'\w+', text.lower())

    found = []

    for word in words:

        if word in OSNOVA:

            found.extend(OSNOVA[word])

    unique = {}

    for f in found:

        unique[f["slovian"]] = f

    return list(unique.values())


# ============================================================
# REALTIME STATE
# ============================================================

if "last" not in st.session_state:
    st.session_state.last = ""

if "result" not in st.session_state:
    st.session_state.result = ""

if "last_time" not in st.session_state:
    st.session_state.last_time = 0


# ============================================================
# UI
# ============================================================

st.title("Perkladačь")

text = st.text_area(
    "",
    height=150,
    placeholder="Vupiši tekst..."
)

# ============================================================
# REALTIME ENGINE (DEBOUNCE 0.4s)
# ============================================================

now = time.time()

changed = text != st.session_state.last

debounce_ready = now - st.session_state.last_time > 0.4

if changed and debounce_ready:

    st.session_state.last = text

    st.session_state.last_time = now

    if text.strip() == "":

        st.session_state.result = ""

    else:

        context = get_context(text)

        context_str = "\n".join(
            f"{c['polish']}={c['slovian']}"
            for c in context
        )

        vuzor_str = json.dumps(VUZOR, ensure_ascii=False)

        try:

            result = cached_translate(
                text,
                context_str,
                vuzor_str
            )

            st.session_state.result = result

        except Exception as e:

            st.session_state.result = str(e)

# ============================================================
# OUTPUT
# ============================================================

st.markdown(
    f'<div class="result">{st.session_state.result}</div>',
    unsafe_allow_html=True
)
