import streamlit as st
import json
import os
import re
from collections import defaultdict
from groq import Groq

# ================== KONFIGURACJA STRONY ==================
st.set_page_config(page_title="Perkladačь slověnьskogo ęzyka", layout="wide")

st.markdown("""
<style>
    .main {background-color: #0e1117;}
    .stTextArea textarea {background-color: #1a1a1a; color: #dcdcdc; font-size: 1.1rem;}
    .stSuccess {background-color: #1e2a1e; color: #90ee90; border: 1px solid #4CAF50;}
</style>
""", unsafe_allow_html=True)

# ================== POŁĄCZENIE Z API ==================
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Błąd klucza API. Upewnij się, że GROQ_API_KEY jest w secrets.")
    st.stop()

# ================== ŁADOWANIE I INDEKSOWANIE DANYCH ==================
@st.cache_data
def load_data():
    def read_json(path):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    o_raw = read_json("osnova.json")
    v_raw = read_json("vuzor.json")
    
    dic = defaultdict(list)
    for entry in o_raw:
        pol = entry.get("polish", "").lower().strip()
        if pol:
            dic[pol].append(entry)
            
    return dic, v_raw, o_raw

dictionary, vuzor_list, osnova_raw = load_data()

# ================== LOGIKA WYDOBYWANIA DANYCH ==================
def get_grammatical_context(text, dic, vuzory):
    words = re.findall(r'\b\w+\b', text.lower())
    found_mappings = []
    relevant_forms = []
    seen_slovian_bases = set()

    for w in words:
        entries = []
        if w in dic:
            entries = dic[w]
        elif len(w) >= 4:
            pref = w[:4]
            for pol_key in dic:
                if pol_key.startswith(pref):
                    entries.extend(dic[pol_key])

        for e in entries:
            found_mappings.append(e)
            s_base = e.get("slovian")
            
            if s_base and s_base not in seen_slovian_bases:
                for v in vuzory:
                    v_case = v.get("type and case", "")
                    v_slov = v.get("slovian", "")
                    # Kluczowe dopasowanie: szukamy rdzenia słowa w opisie gramatycznym
                    if s_base == v_slov or f"'{s_base}'" in v_case or f": {s_base}" in v_case:
                        relevant_forms.append({"forma": v_slov, "info": v_case})
                seen_slovian_bases.add(s_base)

    return found_mappings, relevant_forms

# ================== INTERFEJS ==================
st.title("🏛️ Perkladačь slověnьskogo ęzyka")

user_input = st.text_area(
    "Vupiši slovo alibo rěčenьje (PL):",
    placeholder="W Słowianach siła.",
    height=150
)

if user_input:
    with st.spinner("Generowanie precyzyjnego tłumaczenia..."):
        mappings, grammar_pool = get_grammatical_context(user_input, dictionary, vuzor_list)

        grammar_str = "\n".join([f"FORMA: {i['forma']} | GRAMATYKA: {i['info']}" for i in grammar_pool])

        system_prompt = f"""Jesteś automatem tłumaczącym na język prasłowiański. 
Twoim jedynym zadaniem jest złożenie zdania z gotowych klocków dostarczonych poniżej. 

DANE WEJŚCIOWE:
{grammar_str}

ZASADY KRYTYCZNE:
1. ZAKAZ ZMIENIANIA KOŃCÓWEK. Używaj wyłącznie form wymienionych jako 'FORMA'.
2. PROCES DECYZYJNY:
   - Polskie zdanie: "W Słowianach siła"
   - Analiza: "W" -> "Vu", "Słowianach" -> (Miejscownik/Locative, l. mnoga/plural).
   - Szukasz w danych: FORMA dla 'locative' i 'plural'. 
   - Jeśli widzisz 'FORMA: slověnьnah | GRAMATYKA: ... locative | plural', MUSISZ użyć 'slověnьnah'.
3. Nie poprawiaj form, które wydają Ci się błędne. Twoje zdanie ma być identyczne z formami w tabeli.
4. Szyk: Przymiotnik przed rzeczownikiem.
5. Jeśli brakuje formy, napisz (ne najdeno).

TEKST DO ZŁOŻENIA: "{user_input}" """

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0,
                max_tokens=500
            )

            translation = response.choices[0].message.content.strip()
            st.markdown("### Vynik perklada:")
            st.success(translation)
            
            with st.expander("Dane użyte do budowy zdania"):
                st.text(grammar_str)

        except Exception as e:
            st.error(f"Błąd: {e}")

# ================== STOPKA ==================
st.divider()
st.caption(f"Baza danych: {len(osnova_raw)} słów | {len(vuzor_list)} form gramatycznych.")
