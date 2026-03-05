import streamlit as st
import json
import os
import re
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="Perkladačь slověnьskogo ęzyka", layout="centered")
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTextInput > div > div > input { background-color: #1a1a1a; color: #dcdcdc; border: 1px solid #333; }
    .stSuccess { background-color: #050505; border: 1px solid #2e7d32; color: #dcdcdc; font-size: 1.2rem; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    def read_json(fn):
        if not os.path.exists(fn): return []
        with open(fn, "r", encoding="utf-8") as f: return json.load(f)
    osnova = read_json("osnova.json")
    vuzor = read_json("vuzor.json")
    dic = {}
    for entry in osnova:
        pl = entry.get("polish", "").lower().strip()
        if pl: dic.setdefault(pl, []).append(entry)
    return dic, vuzor

dictionary, vuzor_data = load_data()

def match_case(original, translated):
    if not translated: return original
    result = []
    t_idx = 0
    for o in original:
        if o.isalpha() and t_idx < len(translated):
            result.append(translated[t_idx].upper() if o.isupper() else translated[t_idx].lower())
            t_idx += 1
        else:
            result.append(o)
    return ''.join(result)

def get_declined_form(token, base_entry, vuzor):
    clean = re.sub(r'[^\w]', '', token).lower()
    for entry in vuzor:
        if entry.get("polish", "").lower() == clean and "slovian" in entry:
            return entry["slovian"]
    return base_entry.get("slovian", "") if base_entry else ""

def custom_translate(text):
    tokens = re.findall(r'\w+|[^\w\s]', text)
    processed = []
    found = []
    for token in tokens:
        if not re.match(r'^\w', token):
            processed.append((token, {'type': 'punct'}))
            continue
        clean = re.sub(r'[^\w]', '', token).lower()
        if clean in dictionary:
            entry = dictionary[clean][0]
            slov = get_declined_form(token, entry, vuzor_data) or entry.get('slovian', '')
            typ = entry.get('type and case', '').lower()
            final = match_case(token, slov)
            processed.append((final, {'type': typ}))
            found.append(entry)
        else:
            final = match_case(token, "(ne najdeno slova)")
            processed.append((final, {'type': 'unknown'}))
    return " ".join(w[0] for w in processed), found

st.title("Perkladačь slověnьskogo ęzyka")
st.caption("Tylko baza + vuzor (odmiany)")
user_input = st.text_input("Vupiši rěčenьje:", placeholder="np. Bez jasnego planu nas nie będzie.")
if user_input:
    with st.spinner("Przetwarzanie według vuzor..."):
        result, matches = custom_translate(user_input)
        st.markdown("### Vynik perklada:")
        st.success(result)
        if matches:
            with st.expander("Užito jiz Twojej podstawy"):
                for m in matches:
                    st.write(f"**{m.get('polish','')}** → `{m.get('slovian','')}` ({m.get('type and case','')})")
