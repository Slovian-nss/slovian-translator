import json
import os

def load_json_file(filename):
    """Bezpieczne wczytywanie plików JSON."""
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print(f"Błąd czytania pliku: {filename}")
                return []
    return []

def save_json_file(data, filename):
    """Zapisywanie danych do JSON z zachowaniem sortowania po polsku."""
    # Jeśli to osnova.json, sortujemy alfabetycznie po polskim kluczu
    if filename == 'osnova.json':
        data = sorted(data, key=lambda x: x.get('polish', '').lower())
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_stem(word):
    """
    Prosta funkcja wyciągająca rdzeń słowa prasłowiańskiego.
    Odcina typowe końcówki mianownika (ъ, a, o, e, ь).
    """
    endings = ['ъ', 'a', 'o', 'e', 'ь']
    for end in endings:
        if word.endswith(end):
            return word[:-len(end)]
    return word

def learn_from_example_sentences(example_file='example_sentences.json'):
    """
    Główny silnik uczący. Pobiera przykłady i aktualizuje bazę osnova.json.
    """
    examples = load_json_file(example_file)
    if not examples:
        print("Brak przykładów do nauki.")
        return

    osnova = load_json_file('osnova.json')
    vuzory = load_json_file('vuzor.json')

    # Tworzymy mapę istniejących słów po polsku dla szybkiego sprawdzenia
    existing_polish = {item.get('polish', '').lower(): item for item in osnova}

    new_entries_count = 0

    for ex in examples:
        p_word = ex.get('polish', '').lower().strip()
        s_word = ex.get('slovian', '').strip()

        if p_word and s_word:
            # Jeśli słowa nie ma w osnova, dodajemy je z automatycznym rdzeniem
            if p_word not in existing_polish:
                stem = get_stem(s_word)
                
                entry = {
                    "polish": p_word,
                    "slovian": s_word,
                    "stem": stem,
                    "type": ex.get("type", "noun"), # Domyślnie rzeczownik, jeśli nie podano
                    "context": ex.get("context", "z przykładu")
                }
                
                # Jeśli w przykładzie był podany przypadek (case), dodajemy go
                if "case" in ex:
                    entry["last_case"] = ex["case"]

                osnova.append(entry)
                existing_polish[p_word] = entry
                new_entries_count += 1

    save_json_file(osnova, 'osnova.json')
    print(f"Silnik Slovo: Przetworzono przykłady. Dodano {new_entries_count} nowych baz słownikowych.")

def apply_grammar(polish_word, target_case, target_number='singular'):
    """
    FUNKCJA TRANSLATORA: 
    Łączy rdzeń z osnova.json z końcówką z vuzor.json.
    """
    osnova = load_json_file('osnova.json')
    vuzory = load_json_file('vuzor.json') # Zakładamy, że vuzor to słownik wzorów

    word_data = next((item for item in osnova if item['polish'] == polish_word), None)
    
    if not word_data or 'stem' not in word_data:
        return polish_word # Fallback do polskiego, jeśli nie znamy rdzenia

    w_type = word_data.get('type', 'noun_masc_hard')
    
    # Próba znalezienia końcówki we wzorcach
    try:
        suffix = vuzory[w_type][target_number][target_case]
        return word_data['stem'] + suffix
    except (KeyError, TypeError):
        return word_data['slovian'] # Fallback do mianownika

if __name__ == "__main__":
    # Uruchomienie procesu uczenia
    learn_from_example_sentences()
