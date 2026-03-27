import json
import os

def optimize_dictionary():
    files = ['osnova.json', 'vuzor.json']
    combined_data = []

    for file in files:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                combined_data.extend(data)

    # Przykład "nauki": usuwanie duplikatów i sortowanie alfabetyczne
    unique_data = {item['polish'].lower(): item['slovian'] for item in combined_data if 'polish' in item}
    
    # Zapisujemy "wyczyszczony" słownik do pliku, który odczyta index.html
    final_list = [{"polish": k, "slovian": v} for k, v in sorted(unique_data.items())]
    
    with open('processed_dict.json', 'w', encoding='utf-8') as f:
        json.dump(final_list, f, ensure_ascii=False, indent=2)
    
    print(f"Przetworzono {len(final_list)} słów.")

if __name__ == "__main__":
    optimize_dictionary()
