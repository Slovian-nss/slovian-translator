def translate_text(text, src_lang, tgt_lang):
    """
    Funkcja obsługująca logikę tłumaczenia.
    Na razie działa jako 'placeholder'.
    """
    if not text.strip():
        return ""
    
    # TUTAJ MOŻESZ DODAĆ WŁASNY SILNIK TŁUMACZENIA
    # Przykład prostego przetworzenia:
    result = f"[Przetłumaczono z {src_lang} na {tgt_lang}]: {text}"
    
    return result

def get_languages():
    """Zwraca słownik dostępnych języków."""
    return {
        "pl": "Polski",
        "sl": "Prasłowiański",
        "en": "Angielski",
        "de": "Niemiecki",
        "fr": "Francuski",
        "es": "Hiszpański",
        "ru": "Rosyjski"
    }
