import streamlit as st
from style import apply_custom_style, render_header
from logic import translate_text, get_languages

# --- 1. KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="Tłumacz Języka Słowiańskiego",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Aplikujemy style CSS z pliku style.py
apply_custom_style()

# --- 2. INICJALIZACJA STANU SESJI ---
# Zapobiega to przeładowywaniu się danych przy każdym kliknięciu
if "input_text" not in st.session_state:
    st.session_state.input_text = ""
if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""
if "src_lang" not in st.session_state:
    st.session_state.src_lang = "pl"
if "tgt_lang" not in st.session_state:
    st.session_state.tgt_lang = "sl"

# Funkcja zamiany języków miejscami
def swap_langs():
    st.session_state.src_lang, st.session_state.tgt_lang = \
        st.session_state.tgt_lang, st.session_state.src_lang

# --- 3. INTERFEJS UŻYTKOWNIKA ---

# Nagłówek z style.py
render_header()

# Pobieramy listę języków z logic.py
LANGUAGES = get_languages()

# RZĄD 1: Wybór języków i przycisk zamiany
c1, c2, c3 = st.columns([10, 1.5, 10])

with c1:
    st.selectbox(
        "Z języka",
        options=list(LANGUAGES.keys()),
        format_func=lambda x: LANGUAGES[x],
        key="src_lang",
        label_visibility="collapsed"
    )

with c2:
    st.markdown('<div class="swap-btn-container" style="text-align:center;">', unsafe_allow_html=True)
    st.button("⇄", on_click=swap_langs, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c3:
    st.selectbox(
        "Na język",
        options=list(LANGUAGES.keys()),
        format_func=lambda x: LANGUAGES[x],
        key="tgt_lang",
        label_visibility="collapsed"
    )

# Odstęp pomocniczy
st.markdown('<div class="row-spacer"></div>', unsafe_allow_html=True)

# RZĄD 2: Przyciski akcji (Wklej, Tłumacz, Kopiuj)
b1, b_space, b2 = st.columns([10, 1.5, 10])

with b1:
    col_func1, col_func2 = st.columns([1, 1])
    with col_func1:
        # Przycisk wklejania (pusty placeholder lub obsługa JS)
        st.button("📋 Wklej tekst", use_container_width=True)
    with col_func2:
        # PRZYCISK TŁUMACZENIA - KLUCZOWY ELEMENT
        if st.button("🚀 TŁUMACZ", type="primary", use_container_width=True):
            if st.session_state.input_text.strip():
                with st.spinner('Trwa tłumaczenie...'):
                    # Wywołanie logiki z logic.py korzystającej z Twoich plików JSON
                    wynik = translate_text(
                        st.session_state.input_text,
                        st.session_state.src_lang,
                        st.session_state.tgt_lang
                    )
                    st.session_state.translated_text = wynik
            else:
                st.warning("Najpierw wpisz tekst do przetłumaczenia.")

with b2:
    st.button("📋 Kopiuj wynik", use_container_width=False)

# RZĄD 3: Pola tekstowe (Input i Output)
t1, t_space, t2 = st.columns([10, 1.5, 10])

with t1:
    # Pole wejściowe - aktualizuje input_text w sesji
    st.session_state.input_text = st.text_area(
        "Tekst źródłowy",
        value=st.session_state.input_text,
        height=300,
        placeholder="Wpisz słowa lub zdania...",
        label_visibility="collapsed"
    )

with t2:
    # Pole wynikowe - wyświetla przetłumaczony tekst ze stanu sesji
    st.text_area(
        "Wynik tłumaczenia",
        value=st.session_state.translated_text,
        height=300,
        label_visibility="collapsed",
        key="output_field"
    )

# --- STOPKA ---
st.markdown("---")
st.caption("System wykorzystuje bazy osnova.json oraz vuzor.json do generowania form prasłowiańskich.")
