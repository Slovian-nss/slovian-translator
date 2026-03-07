import streamlit as st
import json
import os
import re
from collections import defaultdict

# ================== KONFIGURACJA ==================
st.set_page_config(page_title="Perkladačь slověnьskogo ęzyka", layout="centered")

st.markdown("""
<style>
.main {background:#0e1117}
.stTextArea textarea {background:#1a1a1a;color:#dcdcdc;font-size:1.2rem;}
.stSuccess {background-color: #1e2329; border: 1px solid #4caf50; font-size: 1.3rem;}
</style>
""", unsafe_allow_html=True)

# ================== INDEKSOWANIE Z PRIORYTETAMI ==================
@st.cache_data
def load_data():
    def load_json(name):
        if not os.path.exists(name): return []
        with open(name, "r", encoding="utf-8") as f: return json.load(f)
    
    # Tworzymy bazę, gdzie pod jednym polskim słowem mamy listę wszystkich form
    db = defaultdict(list)
    for entry in load_json("vuzor.json") + load_json("osnova.json"):
        pl = entry.get("polish", "").lower().strip()
        if pl: db[pl].append(entry)
    return db

DB = load_data()

# ================== ZAAWANSOWANY SILNIK DOPASOWANIA ==================

# Rozszerzona lista przyimków i ich przypadków
RULES = {
    "w": "locative", "we": "locative", "o": "locative", "na": "locative",
    "do": "genitive", "z": "genitive", "dla": "genitive", "bez": "genitive",
    "ku": "dative", "przeciw": "dative",
    "między": "instrumental", "nad": "instrumental", "pod": "instrumental"
}

def find_perfect_word(pl_word, required_case=None):
    # 1. Szukamy dokładnego dopasowania słowa w bazie
    options = DB.get(pl_word, [])
    
    if options:
        # Jeśli szukamy konkretnego przypadku (np. locative)
        if required_case:
            for opt in options:
                if required_case in opt.get("type and case", "").lower():
                    return opt.get("slovian")
        # Jeśli nie ma wymogu lub nie znaleźliśmy przypadku, bierzemy pierwszy rekord (zazwyczaj mianownik)
        return options[0].get("slovian")

    # 2. Jeśli brak dokładnego słowa, szukamy po rdzeniu (min. 4 litery), 
    # ale wybieramy formę, która pasuje do przypadku!
    if len(pl_word) >= 4:
        stem = pl_word[:4]
        potential_matches = []
        for key, entries in DB.items():
            if key.startswith(stem):
                potential_matches.extend(entries)
        
        if potential_matches:
            if required_case:
                for pm in potential_matches:
                    if required_case in pm.get("type and case", "").lower():
                        return pm.get("slovian")
            return potential_matches[0].get("slovian")

    return None

def translate_logic(text):
    tokens = re.findall(r'\w+|[^\w\s]|\s+', text)
    output = []
    next_case = None

    for token in tokens:
        if not re.match(r'\w+', token):
            output.append(token)
            continue

        low = token.lower().strip()
        
        # Tłumaczymy słowo uwzględniając kontekst poprzedniego przyimka
        translated = find_perfect_word(low, next_case)
        
        # Ustawiamy przypadek dla następnego słowa
        next_case = RULES.get(low)

        if translated:
            if token[0].isupper(): translated = translated.capitalize()
            output.append(translated)
        else:
            output.append("(ne najdeno slova)")

    return "".join(output)

# ================== UI ==================
st.title("Perkladačь slověnьskogo ęzyka")
st.subheader("Silnik V3: Precyzyjna odmiana gramatyczna")

user_input = st.text_area("Vupiši rěčenьje:", placeholder="Np. W moim mieście.", height=150)

if user_input:
    res = translate_logic(user_input)
    st.markdown("### Vynik perklada:")
    st.success(res)
    
    with st.expander("Logika odmiany"):
        st.write("Silnik sprawdził przyimki i przeszukał plik vuzor.json pod kątem pasujących przypadków.")
