import streamlit as st
import json
import os
import re

st.set_page_config(page_title="Perkladačь slověnьskogo ęzyka", layout="centered")
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTextInput > div > div > input { background-color: #1a1a1a; color: #dcdcdc; border: 1px solid #333; }
    .stSuccess { background-color: #050505; border: 1px solid #2e7d32; color: #dcdcdc; font-size: 1.2rem; }
    .stCaption { color: #888; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_dictionary():
    if not os.path.exists("osnova.json"):
        return {}
    try:
        with open("osnova.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        index = {}
        for entry in data:
            pl = entry.get("polish", "").lower().strip()
            if pl:
                if pl not in index: index[pl] = []
                index[pl].append(entry)
        return index
    except Exception as e:
        st.error(f"Blǫd osnovy: {e}")
        return {}

dictionary = load_dictionary()

def get_relevant_context(text, dic):
    search_text = re.sub(r'[^\w\s]', '', text.lower())
    words = search_text.split()
    relevant_entries = []
    for word in words:
        if word in dic:
            relevant_entries.extend(dic[word])
        elif len(word) > 3:
            for key in dic.keys():
                if word.startswith(key[:4]) and len(key) > 3:
                    relevant_entries.extend(dic[key])
    seen = set()
    unique_entries = []
    for e in relevant_entries:
        identifier = (e['slovian'], e.get('type and case', ''))
        if identifier not in seen:
            seen.add(identifier)
            unique_entries.append(e)
    return unique_entries[:40]

def local_translate(text, dic):
    def replacer(match):
        word = match.group(0)
        lower_word = word.lower()
        if lower_word in dic and dic[lower_word]:
            base_slov = dic[lower_word][0].get('slovian', '')
            if len(word) == len(base_slov):
                translated = ''.join(
                    base_slov[i].upper() if word[i].isupper() else base_slov[i].lower()
                    for i in range(len(word))
                )
            elif word.isupper():
                translated = base_slov.upper()
            elif word and word[0].isupper():
                translated = (base_slov[0].upper() + base_slov[1:].lower()) if base_slov else ''
            else:
                translated = base_slov.lower() if base_slov else ''
            return translated
        else:
            if word.isupper():
                return "(NE NAJDENO SLOVA)"
            elif word and word[0].isupper():
                return "(Ne najdeno slova)"
            else:
                return "(ne najdeno slova)"
    word_pattern = r'(?u)\b\w+\b'
    return re.sub(word_pattern, replacer, text)

st.title("Perkladačь slověnьskogo ęzyka")
user_input = st.text_input("Vupiši slovo abo rěčenьje:", placeholder="")
if user_input:
    with st.spinner("Orzmyslь nad čęstьmi ęzyka i perklad..."):
        matches = get_relevant_context(user_input, dictionary)
        translated = local_translate(user_input, dictionary)
        st.markdown("### Vynik perklada:")
        st.success(translated)
        if matches:
            with st.expander("Užito žerdlo jiz osnovy"):
                for m in matches:
                    st.write(f"**{m['polish']}** → `{m['slovian']}` ({m.get('type and case','')})")
