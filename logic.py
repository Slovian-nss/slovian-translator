import json
import os

class SlovianLogic:
    def __init__(self):
        self.osnova = self._load_data('osnova.json')
        self.vuzor = self._load_data('vuzor.json')
        
        # Mapowanie fonetyczne do "zgadywania" słów spoza bazy
        self.phonetic_map = {
            'ą': 'ǫ', 'ę': 'ę', 'rz': 'rь', 'sz': 'š', 
            'cz': 'č', 'ż': 'ž', 'ć': 'cь', 'ś': 'sь'
        }

    def _load_data(self, filename):
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def get_inflection(self, pattern_id, form_key="m1"):
        """Pobiera końcówkę z vuzor.json (np. mianownik m1)"""
        pattern = self.vuzor.get(pattern_id, {})
        return pattern.get(form_key, "")

    def translate_word(self, word):
        w = word.lower().strip(".,!?:")
        
        # 1. Dokładne dopasowanie
        if w in self.osnova:
            data = self.osnova[w]
            if isinstance(data, dict):
                root = data.get("osnova", "")
                vuzor_id = data.get("vuzor", "")
                suffix = self.get_inflection(vuzor_id)
                return root + suffix
            return data # Jeśli to prosty string

        # 2. Inteligentne zgadywanie (Phonetic Reconstruction)
        # To jest uproszczony model 'zero-shot' dla nowych słów
        reconstructed = w
        for pl, psl in self.phonetic_map.items():
            reconstructed = reconstructed.replace(pl, psl)
        
        # Dodanie twardego znaku na końcu rzeczowników (stylizacja na prasłowiański)
        if reconstructed[-1] not in "aeiouyǫęьъ":
            reconstructed += "ъ"
            
        return reconstructed

    def full_translate(self, text):
        words = text.split()
        return " ".join([self.translate_word(w) for w in words])

translator = SlovianLogic()
