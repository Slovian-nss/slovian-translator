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

@st.cache_data
def load_json(filename):
    if not os.path.exists(filename): return []
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

osnova = load_json("osnova.json")

@st.cache_data
def build_dictionaries(data):
    pl_sl = defaultdict(list)
    sl_pl = defaultdict(list)
    for e in data:
        pl = e.get("polish","").lower().strip()
        sl = e.get("slovian","").lower().strip()
        if pl: pl_sl[pl].append(e.get("slovian",""))
        if sl: sl_pl[sl].append(e.get("polish",""))
    return pl_sl, sl_pl

pl_to_sl, sl_to_pl = build_dictionaries(osnova)

def translate(text):
    if not text.strip(): return text
    words = [w.lower() for w in re.findall(r'\w+', text)]
    pl_matches = sum(1 for w in words if w in pl_to_sl)
    sl_matches = sum(1 for w in words if w in sl_to_pl)
    to_sl = pl_matches >= sl_matches
    dic = pl_to_sl if to_sl else sl_to_pl
    def repl(m):
        w = m.group(0)
        lw = w.lower()
        if lw in dic and dic[lw]:
            t = dic[lw][0]
            if w.isupper(): return t.upper()
            if w[0].isupper(): return t.capitalize()
            return t
        else:
            return "(ne najdeno slova)" if to_sl else w
    return re.sub(r'\w+', repl, text)

st.title("Perkladačь slověnьskogo ęzyka")
user_input = st.text_area("Vupiši slovo alibo rěčenьje:", placeholder="Np. W miastach siła.", height=150)
if user_input:
    with st.spinner("Przetwarzanie..."):
        result = translate(user_input)
        st.markdown("### Vynik perklada:")
        st.success(result)
