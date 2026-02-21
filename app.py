import streamlit as st
import json
import os
import re
from groq import Groq

st.set_page_config(page_title="Perkladačь slověnьskogo ęzyka", layout="centered")
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTextInput > div > div > input { background-color: #1a1a1a; color: #dcdcdc; border: 1px solid #333; }
    .stSuccess { background-color: #050505; border: 1px solid #2e7d32; color: #dcdcdc; font-size: 1.2rem; }
    .stCaption { color: #888; }
    </style>
    """, unsafe_allow_html=True)

GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

@st.cache_data
def load_dictionary():
    if not os.path.exists("osnova.json"): return {}
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
    except: return {}

dictionary = load_dictionary()

@st.cache_data
def load_vuzor():
    if not os.path.exists("vuzor.json"): return {}
    try:
        with open("vuzor.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except: return {}
vuzor = load_vuzor()
vuzor_str = json.dumps(vuzor, ensure_ascii=False)[:4000]

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

st.title("Perkladačь slověnьskogo ęzyka")
target_lang = st.selectbox("Język wyjścia:", ["prasłowiański","polski","angielski","niemiecki","rosyjski","ukraiński","czeski","słowacki","hiszpański","francuski"], index=0)

user_input = st.text_input("Vupiši slovo abo rěčenьje:", placeholder="", key="live_input")

if user_input:
    with st.spinner("Orzmyslь nad čęstьmi..."):
        matches = get_relevant_context(user_input, dictionary)
        context_str = "\n".join([f"- POLSKIE: {m['polish']} | UŻYJ FORMY: {m['slovian']} | GRAMATYKA: {m.get('type and case','')}" for m in matches])
        
        system_prompt = """Jesteś rygorystycznym silnikiem tłumaczącym z dowolnego języka na prasłowiański i odwrotnie. Polski jest obowiązkowym pośrednikiem.

KROK 0 – DETEKCJA I POŚREDNIK:
1. Wykryj język wejścia.
2. Jeśli nie polski i nie prasłowiański (rozpoznaj po ěęǫь): przetłumacz dokładnie na polski (zachowaj case, format).
3. Jeśli prasłowiański: przetłumacz na polski.
4. Następnie:
   - target = prasłowiański → przetłumacz polski na prasłowiański.
   - target inny → przetłumacz polski na wybrany język.

KRYTYCZNA ZASADA ODMIAN (vuzor.json):
- ZAWSZE najpierw sprawdź osnova.json.
- Jeśli formy brak → znajdź podstawową w osnova + dokładnie pasujący wzór w vuzor.json (POS, przypadek, rodzaj, liczba).
- Zastosuj TYLKO końcówki i palatalizacje z vuzor (k→c/č przed ě, g→dz/ž, h→z itd. – bez wymyślania).
- Przymiotniki: zawsze wzór z "boži" lub "slověnьsky" + zawsze PRZED rzeczownikiem.
- Przymiotnik musi zgadzać się w rodzaju/przypadku/liczbie z rzeczownikiem.

Reszta zasad (ortografia, wielkość liter, kolejność przymiotnik-rzeczownik, alfabet tylko łaciński + ěęǫь, brak cyrylicy) bez zmian.
Zwróć TYLKO czyste tłumaczenie."""

        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"BAZA:\n{context_str}\n\nVUZOR:\n{vuzor_str}\n\nJĘZYK WYJŚCIA: {target_lang}\n\nDO TŁUMACZENIA: {user_input}"}
                ],
                model="openai/gpt-oss-120b",
                temperature=0.0
            )
            response_text = chat_completion.choices[0].message.content.strip()
            st.markdown("### Vynik perklada:")
            st.success(response_text)
            if matches:
                with st.expander("Užito žerdlo jiz osnovy"):
                    for m in matches:
                        st.write(f"**{m['polish']}** → `{m['slovian']}` ({m.get('type and case','')})")
        except Exception as e:
            st.error(f"Blǫd: {e}")
