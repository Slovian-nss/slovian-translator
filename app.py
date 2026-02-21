import streamlit as st
import json
import os
import re

# ============================================================
# 1. KONFIGURACJA I STYLIZACJA
# ============================================================
st.set_page_config(page_title="Perkladačь slověnьskogo ęzyka", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTextInput > div > div > input { background-color: #1a1a1a; color: #dcdcdc; border: 1px solid #333; }
    .stSuccess { background-color: #050505; border: 1px solid #2e7d32; color: #dcdcdc; font-size: 1.2rem; }
    .stCaption { color: #888; }
    </style>
    """, unsafe_allow_html=True)

# ============================================================
# 2. ŁADOWANIE BAZY DANYCH (LOKALNE)
# ============================================================
@st.cache_data
def load_data():
    def load_file(name):
        if os.path.exists(name):
            with open(name, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    osnova = load_file("osnova.json")
    vuzor = load_file("vuzor.json")
    
    # Tworzymy szybki indeks wyszukiwania
    index = {}
    for entry in osnova:
        pl = entry.get("polish", "").lower().strip()
        if pl:
            if pl not in index: index[pl] = []
            index[pl].append(entry)
            
    return index, vuzor

dictionary, vuzory = load_data()

# ============================================================
# 3. LOKALNY SILNIK LOGIKI (Zastępuje AI)
# ============================================================

def match_case(original, translated):
    """Zachowuje styl wielkości liter (Mati, MATI, mati)."""
    if original.isupper():
        return translated.upper()
    if original[0].isupper():
        return translated.capitalize()
    return translated.lower()

def apply_grammar_rules(words_with_meta):
    """
    Realizuje krytyczną zasadę: Przymiotnik ZAWSZE przed rzeczownikiem.
    Oraz łączenie słów w zdanie.
    """
    result = []
    i = 0
    n = len(words_with_meta)
    
    while i < n:
        current = words_with_meta[i]
        
        # Sprawdź czy to rzeczownik i czy następny to przymiotnik (do zamiany)
        if i + 1 < n:
            next_word = words_with_meta[i+1]
            is_curr_noun = "noun" in current['type'].lower()
            is_next_adj = "adjective" in next_word['type'].lower() or "pridavьnik" in next_word['type'].lower()
            
            if is_curr_noun and is_next_adj:
                # Zamiana miejscami
                result.append(next_word['word'])
                result.append(current['word'])
                i += 2
                continue
        
        result.append(current['word'])
        i += 1
    
    return " ".join(result)

def translate_local(text, dic):
    """Główna funkcja tłumacząca bez API."""
    # Czyszczenie i podział na słowa (zachowując interpunkcję w uproszczeniu)
    input_words = re.findall(r"[\w']+|[.,!?;]", text)
    translated_meta = []

    for word in input_words:
        if re.match(r"[.,!?;]", word):
            translated_meta.append({'word': word, 'type': 'punct'})
            continue
            
        low_word = word.lower()
        
        # 1. Szukanie w osnova.json
        if low_word in dic:
            entry = dic[low_word][0] # Bierzemy pierwsze dopasowanie
            slov = entry['slovian']
            # Usuwanie cyrylicy jeśli występuje (zgodnie z zasadą)
            slov = re.sub(r'[а-яА-ЯёЁ]', '', slov) if slov else "(error)"
            
            translated_meta.append({
                'word': match_case(word, slov),
                'type': entry.get('type and case', 'unknown')
            })
        else:
            # 2. Brak słowa
            translated_meta.append({
                'word': match_case(word, "(ne najdeno slova)"),
                'type': 'unknown'
            })

    # 3. Zastosowanie zasad składni (Przymiotnik przed Rzeczownikiem)
    return apply_grammar_rules(translated_meta)

# ============================================================
# 4. INTERFEJS UŻYTKOWNIKA
# ============================================================
st.title("Perkladačь slověnьskogo ęzyka")
st.caption("Tryb lokalny: Działa bez zewnętrznych serwerów i API")

user_input = st.text_input("Vupiši slovo abo rěčenьje:", placeholder="np. Wojsko Słowiańskie")

if user_input:
    with st.spinner("Prekladajǫ lokalno..."):
        # Tłumaczenie lokalne
        final_translation = translate_local(user_input, dictionary)
        
        st.markdown("### Vynik perklada:")
        st.success(final_translation)
        
        # Pokazanie źródeł (opcjonalnie)
        search_words = re.findall(r"\w+", user_input.lower())
        relevant_matches = [dictionary[w][0] for w in search_words if w in dictionary]
        
        if relevant_matches:
            with st.expander("Užito žerdlo jiz osnovy"):
                for m in relevant_matches:
                    st.write(f"**{m['polish']}** → `{m['slovian']}` ({m.get('type and case','')})")
