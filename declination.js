// declination.js

let plToSlo = {}, sloToPl = {};
let wordTypes = {};

// --- Wczytywanie słowników ---
async function loadDictionaries() {
    try {
        const files = ['osnova.json', 'vuzor.json'];
        for (const file of files) {
            const res = await fetch(file);
            if (!res.ok) continue;
            const data = await res.json();
            data.forEach(item => {
                if (item.polish && item.slovian) {
                    const pl = item.polish.toLowerCase().trim();
                    const slo = item.slovian.toLowerCase().trim();
                    plToSlo[pl] = item.slovian.trim();
                    sloToPl[slo] = item.polish.trim();

                    if (item["type and case"]) {
                        const info = item["type and case"].toLowerCase();
                        if (info.includes("jimenьnik") || info.includes("noun")) wordTypes[slo] = "noun";
                        if (info.includes("priloga") || info.includes("adjective")) wordTypes[slo] = "adjective";
                        if (info.includes("ličьnik") || info.includes("numeral")) wordTypes[slo] = "numeral";
                    }
                }
            });
        }
        console.log("Dictionaries loaded");
    } catch (e) {
        console.error("Error loading dictionaries:", e);
    }
}

// --- Funkcje pomocnicze dla wielkości liter ---
function getCase(word) {
    if (!word) return "lower";
    if (word === word.toUpperCase() && word.length > 1) return "upper";
    if (word[0] === word[0].toUpperCase()) return "title";
    return "lower";
}

function applyCase(word, caseType) {
    if (!word) return "";
    switch (caseType) {
        case "upper": return word.toUpperCase();
        case "title": return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
        default: return word.toLowerCase();
    }
}

// --- Podstawowe tłumaczenie ze słownika ---
function dictReplace(text, dict) {
    if (!text) return "";
    return text.replace(/[a-ząćęłńóśźżěьъ']+/gi, (word) => {
        const lowWord = word.toLowerCase();
        if (dict[lowWord]) {
            return applyCase(dict[lowWord], getCase(word));
        }
        return `__MISSING__${word}__`;
    });
}

// --- Reorder dla grup (numeral + adjective + noun) ---
function reorderSmart(text) {
    if (!text) return "";
    const tokens = text.split(/(\s+|[.,!?;:()=+\-%*/]+)/g).filter(t => t !== "" && t !== undefined);
    const result = [];

    for (let i = 0; i < tokens.length; i++) {
        let token = tokens[i];
        let lowToken = token.toLowerCase();

        if (/^[\s.,!?;:()=+\-%*/]+$/.test(token)) {
            result.push(token);
            continue;
        }

        if (wordTypes[lowToken]) {
            let group = [];
            let currentIdx = i;
            let firstWordCase = getCase(tokens[i]);

            while (currentIdx < tokens.length) {
                let currentToken = tokens[currentIdx];
                let currentLow = currentToken.toLowerCase();

                if (/^[\s]+$/.test(currentToken)) {
                    currentIdx++;
                    continue;
                }

                let type = wordTypes[currentLow];
                if (type === "noun" || type === "adjective" || type === "numeral") {
                    group.push({ val: currentToken, type: type });
                    i = currentIdx;
                    currentIdx++;
                } else {
                    break;
                }
            }

            if (group.length > 1) {
                const order = { "numeral": 1, "adjective": 2, "noun": 3 };
                group.sort((a, b) => (order[a.type] || 99) - (order[b.type] || 99));

                group.forEach((word, index) => {
                    let formattedWord = word.val.toLowerCase();
                    if (index === 0) formattedWord = applyCase(word.val, firstWordCase);
                    else if (firstWordCase === "upper") formattedWord = word.val.toUpperCase();
                    result.push(formattedWord);
                    if (index < group.length - 1) result.push(" ");
                });
                continue;
            } else if (group.length === 1) {
                result.push(token);
                continue;
            }
        }

        result.push(token);
    }
    return result.join("");
}

// --- Hybrydowa funkcja tłumaczenia z Ollamą ---
async function translateWithDeclination(text, src = 'pl', tgt = 'slo') {
    if (!text) return "";

    // 1. Próba tłumaczenia słownikowego
    let translated = dictReplace(text, src === 'pl' ? plToSlo : sloToPl);

    // 2. Jeśli występują brakujące słowa, wywołujemy Ollama lokalnie
    if (translated.includes("__MISSING__")) {
        try {
            const res = await fetch("http://localhost:11434/api/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    model: "qwen",
                    prompt: `Translate to Slovian preserving grammatical cases and order: ${text}`
                })
            });
            const data = await res.json();
            translated = data.response || translated;
        } catch (e) {
            console.warn("Ollama API failed, returning partial translation:", e);
        }
    }

    // 3. Popraw szyk słów dla grup: numeral + adjective + noun
    translated = reorderSmart(translated);

    return translated;
}

// --- Eksport funkcji ---
export { loadDictionaries, translateWithDeclination };
