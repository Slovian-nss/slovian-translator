import streamlit as st
from openai import OpenAI
import sys

# WYMUSZENIE UTF-8
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

# OPENAI
client = OpenAI(api_key=st.secrets["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"])
MODEL = "gpt-4o-mini"

# PROMPT
SYSTEM_PROMPT = """
You are a scientific Proto-Slavic translator.

Translate Polish into reconstructed Proto-Slavic.

STRICT RULES:

• Use scientific reconstruction
• Use characters: ě, ę, ǫ, š, č, ž, ь, ъ
• Use infinitive for verbs
• Output ONLY translation
• No explanation
• No quotes
• No punctuation

Examples:

Polish: matka
Proto-Slavic: matь

Polish: dom
Proto-Slavic: domъ

Polish: usprawiedliwić
Proto-Slavic: opravьdati
"""

# CACHE (przyspiesza)
@st.cache_data(show_spinner=False)
def translate(text: str):

    if not text.strip():
        return ""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ],
        temperature=0,
        max_tokens=50
    )

    result = response.choices[0].message.content

    # wymuszenie string UTF-8
    return str(result)


# UI
st.set_page_config(page_title="Proto-Slavic Translator")

st.title("Proto-Slavic Translator")
st.caption("Scientific reconstruction")

# session state
if "input" not in st.session_state:
    st.session_state.input = ""

if "output" not in st.session_state:
    st.session_state.output = ""

# input
text = st.text_input(
    "Polish",
    placeholder="Matka jest w ogrodzie",
    label_visibility="collapsed"
)

# AUTO TRANSLATE
if text != st.session_state.input:

    st.session_state.input = text

    try:
        st.session_state.output = translate(text)
    except Exception as e:
        st.session_state.output = f"Error: {str(e)}"


# output
st.text_input(
    "Proto-Slavic",
    value=st.session_state.output,
    disabled=True,
    label_visibility="collapsed"
)
