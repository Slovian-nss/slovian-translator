import streamlit as st
import json
import os
import re
import requests
import base64
from collections import defaultdict

# --- KONFIGURACJA GITHUB (Wypełnij to!) ---
GITHUB_TOKEN = "TWÓJ_TOKEN_PERSONAL_ACCESS_TUTAJ"
REPO_OWNER = "Slovian-nss"
REPO_NAME = "slovian-translator"
FILE_PATH = "selflearning.json"
BRANCH = "main"

st.set_page_config(page_title="Perkladačь slověnьskogo ęzyka", layout="centered")
st.markdown("""
<style>
.main {background:#0e1117}
.stTextArea textarea {background:#1a1a1a;color:#dcdcdc}
</style>
""", unsafe_allow_html=True)

# Funkcja pomocnicza do pobierania danych z GitHub API
def get_github_file():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        content = base64.b64decode(data['content']).decode('utf-8')
        return json.loads(content), data['sha']
    return [], None

@st.cache_data
def load_all_data():
    # Ładujemy podstawę z lokalnego pliku
    if os.path.exists("osnova.json"):
        with open("osnova.json", "r", encoding="utf-8") as f:
            osnova = json.load(f)
    else:
        osnova = []
    
    # Ładujemy selflearning bezpośrednio z GitHuba, żeby mieć najnowsze dane
    selflearning, _ = get_github_file()
    return osnova + selflearning

all_data = load_all_data()

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

pl_to_sl, sl_to_pl = build_dictionaries(all_data)

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

def save_pair_to_github(polish, slovian):
    # 1. Pobierz aktualny stan i SHA
    current_data, sha = get_github_file()
    
    # 2. Dodaj nowy wpis
    new_entry = {"polish": polish.strip(), "slovian": slovian.strip()}
    current_data.append(new_entry)
    
    # 3. Przygotuj dane do wysłania
    updated_json = json.dumps(current_data, ensure_ascii=False, indent=2)
    encoded_content = base64.b64encode(updated_json.encode('utf-8')).decode('utf-8')
    
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    payload = {
        "message": f"Nauka: {polish} -> {slovian}",
        "content": encoded_content,
        "branch": BRANCH,
        "sha": sha
    }
    
    # 4. Wyślij do GitHub
    res = requests.put(url, headers=headers, json=payload)
    if res.status_code in [200, 201]:
        st.cache_data.clear() # Czyścimy cache, by przeładować dane
        st.success("Zapisano w chmurze GitHub!")
        st.rerun()
    else:
        st.error(f"Błąd zapisu: {res.text}")

# --- UI APLIKACJI ---
st.title("Perkladačь slověnьskogo ęzyka")
user_input = st.text_area("Vupiši slovo alibo rěčenьje:", placeholder="Np. W miastach siła.", height=150)

if user_input:
    result = translate(user_input)
    st.markdown("### Vynik perklada:")
    st.success(result)

st.divider()
st.subheader("🧠 Naucz tłumacza")
col1, col2 = st.columns(2)
new_pl = col1.text_input("Słowo polskie")
new_sl = col2.text_input("Tłumaczenie słowiańskie")

if st.button("Zapisz do selflearning.json"):
    if new_pl and new_sl:
        with st.spinner("Wysyłanie do GitHub..."):
            save_pair_to_github(new_pl, new_sl)
    else:
        st.warning("Wypełnij oba pola!")
