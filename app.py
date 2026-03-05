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
    """Per-character case: mATKA → mATI"""
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

def correct_spelling(text):
    corrections = {"bozej": "bożej", "pólnocy": "północy"}  # rozszerz wg potrzeb
    return ' '.join(corrections.get(w.lower(), w) for w in text.split())

def tokenize(text):
    return re.findall(r'\w+|[^\w\s]', text)

def reorder_grammar(words_with_info):
    """Przymiotnik ZAWSZE przed rzeczownikiem"""
    result = []
    i = 0
    while i < len(words_with_info):
        if i + 1 < len(words_with_info):
            w1, info1 = words_with_info[i]
            w2, info2 = words_with_info[i+1]
            if ("noun" in info1.get('type', '') and "adj" in info2.get('type', '')) or \
               ("adj" in info1.get('type', '') and "noun" in info2.get('type', '')):
                result.extend([w2 if "adj" in info1.get('type', '') else w1, w1 if "adj" in info1.get('type', '') else w2])
                i += 2
                continue
        result.append(words_with_info[i][0])
        i += 1
    return result

def custom_translate(text):
    text = correct_spelling(text)
    tokens = tokenize(text)
    processed = []
    found = []
    for token in tokens:
        if not re.match(r'^\w', token):
            processed.append((token, {'type': 'punct'}))
            continue
        clean = re.sub(r'[^\w]', '', token).lower()
        if clean in dictionary:
            entry = dictionary[clean][0]
            slov = entry.get('slovian', '')
            typ = entry.get('type and case', '').lower()
            final = match_case(token, slov)
            processed.append((final, {'type': typ}))
            found.append(entry)
        else:
            final = match_case(token, "(ne najdeno slova)")
            processed.append((final, {'type': 'unknown'}))
    return " ".join(reorder_grammar(processed)), found

st.title("Perkladačь slověnьskogo ęzyka")
st.caption("Tylko baza + reguły (zgodne z promptem)")
user_input = st.text_input("Vupiši rěčenьje:", placeholder="np. Wojsko Słowiańskie")
if user_input:
    with st.spinner("Przetwarzanie..."):
        result, matches = custom_translate(user_input)
        st.markdown("### Vynik perklada:")
        st.success(result)
        if matches:
            with st.expander("Užito jiz Twojej podstawy"):
                for m in matches:
                    st.write(f"**{m.get('polish','')}** → `{m.get('slovian','')}` ({m.get('type and case','')})")
