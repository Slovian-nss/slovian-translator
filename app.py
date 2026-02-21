import streamlit as st
import json
import os
import re

# ============================================================
# 1. KONFIGURACJA
# ============================================================
st.set_page_config(page_title="Perkladačь slověnьskogo ęzyka", layout="centered")

@st.cache_data
def load_all_data():
    def load_json(path):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    return load_json("osnova.json"), load_json("vuzor.json")

osnova, vuzory = load_all_data()

# ============================================================
# 2. SILNIK LINGWISTYCZNY (LOGIKA TWARDA)
# ============================================================

def apply_palatalization(word):
    """Realizuje zasadę: k > c, g > dz, h > z przed 'ě'."""
    if word.endswith("gě"): return word[:-2] + "dzě"
    if word.endswith("kě"): return word[:-2] + "cě"
    if word.endswith("hě"): return word[:-2] + "zě"
    return word

def get_word_metadata(polish_word):
    """Szuka słowa w osnova.json i zwraca pełny obiekt."""
    search_word = polish_word.lower().strip()
    # Szukanie dokładne
    for entry in osnova:
        if entry.get("polish", "").lower() == search_word:
            return entry
    return None

def fix_case(original, target):
    """Zachowuje wielkość liter."""
    if original.isupper(): return target.upper()
    if original[0].isupper(): return target.capitalize()
    return target.lower()

# ============================================================
# 3. PROCES TŁUMACZENIA (PIPELINE)
# ============================================================

def translate_sentence(sentence):
    # 1. Rozbijanie na słowa i znaki interpunkcyjne
    tokens = re.findall(r"[\w']+|[.,!?;]", sentence)
    processed_tokens = []

    # 2. Mapowanie słów na dane z bazy
    for token in tokens:
        if re.match(r"[.,!?;]", token):
            processed_tokens.append({"word": token, "type": "punct", "orig": token})
            continue
        
        data = get_word_metadata(token)
        if data:
            slov = data['slovian']
            # Usuń cyrylicę jeśli została w bazie
            slov = re.sub(r'[а-яА-ЯёЁ]', '', slov)
            processed_tokens.append({
                "word": slov,
                "type": data.get("type and case", "").lower(),
                "orig": token
            })
        else:
            processed_tokens.append({
                "word": "(ne najdeno slova)",
                "type": "unknown",
                "orig": token
            })

    # 3. KOREKTA: Przymiotnik przed rzeczownikiem
    # Szukamy par: [Rzeczownik] [Przymiotnik] i zamieniamy
    i = 0
    while i < len(processed_tokens) - 1:
        curr = processed_tokens[i]
        nxt = processed_tokens[i+1]
        
        is_noun = "noun" in curr['type'] or "rzeczownik" in curr['type']
        is_adj = "adj" in nxt['type'] or "pridavьnik" in nxt['type']
        
        if is_noun and is_adj:
            processed_tokens[i], processed_tokens[i+1] = processed_tokens[i+1], processed_tokens[i]
            i += 1
        i += 1

    # 4. KOREKTA: Palatalizacja (lokalna logika)
    for tok in processed_tokens:
        tok['word'] = apply_palatalization(tok['word'])

    # 5. Składanie w całość z zachowaniem wielkości liter
    final_words = [fix_case(t['orig'], t['word']) for t in processed_tokens]
    
    # Naprawa spacji przed interpunkcją
    result = " ".join(final_words)
    result = re.sub(r'\s+([.,!?;])', r'\1', result)
    return result

# ============================================================
# 4. INTERFEJS
# ============================================================
st.title("Perkladačь slověnьskogo ęzyka")
st.subheader("Lokalny silnik bez API")

user_input = st.text_input("Wpisz tekst:", placeholder="np. Sługa Boży")

if user_input:
    output = translate_sentence(user_input)
    st.markdown("### Wynik:")
    st.success(output)

    with st.expander("Szczegóły analizy gramatycznej"):
        st.write("Skrypt wykonał następujące kroki:")
        st.write("1. Sprawdzenie słów w `osnova.json`.")
        st.write("2. Wykrycie części mowy (POS).")
        st.write("3. Automatyczna zmiana szyku (Przymiotnik <-> Rzeczownik).")
        st.write("4. Zastosowanie palatalizacji (np. g -> dz).")
