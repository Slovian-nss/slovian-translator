import streamlit as st
import json
import os
import re
from groq import Groq

# ============================================================
# 1. KONFIGURACJA I STYLIZACJA
# ============================================================
st.set_page_config(page_title="Perkladačь slověnьskogo ęzyka", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTextInput > div > div > input { background-color: #1a1a1a; color: #dcdcdc; border: 1px solid #333; }
    .stSuccess { background-color: #050505; border: 1px solid #2e7d32; color: #dcdcdc; font-size: 1.2rem; }
    </style>
    """, unsafe_allow_html=True)

# ============================================================
# 2. KLIENT GROQ
# ============================================================
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

# ============================================================
# 3. ŁADOWANIE BAZY
# ============================================================
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

# ============================================================
# 4. LOGIKA RAG (Zwiększona precyzja)
# ============================================================
def get_relevant_context(text, dic):
    search_text = re.sub(r'[^\w\s]', '', text.lower())
    words = search_text.split()
    relevant_entries = []
    
    for word in words:
        if word in dic:
            relevant_entries.extend(dic[word])
    
    seen = set()
    unique_entries = []
    for e in relevant_entries:
        # Kluczem jest unikalność pary Polska-Słowiańska
        identifier = (e['polish'], e['slovian'])
        if identifier not in seen:
            seen.add(identifier)
            unique_entries.append(e)
            
    return unique_entries[:30]

# ============================================================
# 5. TŁUMACZENIE
# ============================================================
st.title("Perkladačь slověnьskogo ęzyka")

user_input = st.text_input("Vupiši slovo alibo rěčenьje:", placeholder="")

if user_input:
    with st.spinner("Analiza gramatyczna i dobór form..."):
        matches = get_relevant_context(user_input, dictionary)
        
        # Tworzymy bardzo czytelną listę mapowania dla AI
        context_str = "\n".join([
            f"JEŚLI POLSKIE SŁOWO TO: '{m['polish']}' -> UŻYJ DOKŁADNIE TEJ FORMY: '{m['slovian']}'"
            for m in matches
        ])

        system_prompt = """Jesteś rygorystycznym tłumaczem-transliteratorem. 
Twoim zadaniem jest zamiana polskich słów na słowiańskie odpowiedniki przy zachowaniu DOKŁADNYCH FORM z dostarczonej listy.

ZASADY:
1. MASZ CAŁKOWITY ZAKAZ modyfikowania końcówek słów podanych w liście mapowania.
2. ROZPOZNAWANIE FORM: 
   - Jeśli polskie słowo to 'jesteśmy' -> użyj formy przypisanej do 'jesteśmy' (np. esmy).
   - Jeśli polskie słowo to 'jestem' -> użyj formy przypisanej do 'jestem' (np. jesmь).
3. Nie uogólniaj zasad. Każde słowo z listy mapowania jest traktowane indywidualnie.
4. Zachowaj interpunkcję i wielkość liter wejścia.
5. Zwróć wyłącznie wynik końcowy."""

        try:
            # Używamy modelu wybranego przez Ciebie w Playground
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"LISTA MAPOWANIA:\n{context_str}\n\nDO TŁUMACZENIA: {user_input}"}
                ],
                model="openai/gpt-oss-120b",
                temperature=0.0
            )
            response_text = chat_completion.choices[0].message.content.strip()

            st.markdown("### Vynik perklada:")
            st.success(response_text)

        except Exception as e:
            st.error(f"Blǫd: {e}")

        if matches:
            with st.expander("Užito žerdlo jiz osnovy"):
                for m in matches:
                    st.write(f"**{m['polish']}** → `{m['slovian']}`")
