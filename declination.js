// declination.js
// FULL SENTENCE ENGINE v1

// =====================
// GLOBAL STATE
// =====================
let DECLENSIONS = {};
let LEMMA_MAP = {};

// =====================
// INIT
// =====================
async function initDeclination() {
    const [vuzorRes, osnovaRes] = await Promise.all([
        fetch('vuzor.json'),
        fetch('osnova.json')
    ]);

    const vuzorData = await vuzorRes.json();
    const osnovaData = await osnovaRes.json();

    DECLENSIONS = buildDeclensionMap(vuzorData);
    LEMMA_MAP = buildLemmaMap(osnovaData);
}

// =====================
// BUILDERS
// =====================
function buildDeclensionMap(data) {
    const map = {};

    data.forEach(entry => {
        const typeCase = entry["type and case"];
        const slovian = entry["slovian"];

        const lemmaMatch = typeCase.match(/"([^"]+)"/);
        if (!lemmaMatch) return;

        const lemma = lemmaMatch[1];
        const grammaticalCase = detectCase(typeCase);
        const number = detectNumber(typeCase);

        if (!map[lemma]) {
            map[lemma] = {
                singular: {},
                plural: {}
            };
        }

        map[lemma][number][grammaticalCase] = slovian;
    });

    return map;
}

function buildLemmaMap(data) {
    const map = {};

    data.forEach(entry => {
        const polish = entry["polish"]?.toLowerCase();
        const slovian = entry["slovian"];

        if (polish && slovian) {
            map[polish] = slovian;
        }
    });

    return map;
}

// =====================
// DETECTORS
// =====================
function detectCase(str) {
    if (str.includes("nominative")) return "nominative";
    if (str.includes("accusative")) return "accusative";
    if (str.includes("genitive")) return "genitive";
    if (str.includes("dative")) return "dative";
    if (str.includes("instrumental")) return "instrumental";
    if (str.includes("locative")) return "locative";
    if (str.includes("vocative")) return "vocative";
    return "nominative";
}

function detectNumber(str) {
    if (str.includes("plural")) return "plural";
    return "singular";
}

// =====================
// NLP CORE
// =====================

// liczba mnoga
function detectPlural(word) {
    return word.endsWith("y") || word.endsWith("i") || word.endsWith("e");
}

// przypadek (ulepszony)
function detectPolishCase(word, prevWord = "") {
    word = word.toLowerCase();
    prevWord = prevWord.toLowerCase();

    // PREPOZYCJE
    if (["do", "od", "bez"].includes(prevWord)) return "genitive";
    if (["dla", "ku"].includes(prevWord)) return "dative";
    if (["z", "ze"].includes(prevWord)) return "instrumental";
    if (["o", "na", "w"].includes(prevWord)) return "locative";

    // KOŃCÓWKI
    if (word.endsWith("ę")) return "accusative";
    if (word.endsWith("ą")) return "instrumental";
    if (word.endsWith("om")) return "dative";
    if (word.endsWith("ach")) return "locative";
    if (word.endsWith("ów")) return "genitive";

    return "nominative";
}

// bardzo prosty POS
function detectPOS(word) {
    if (LEMMA_MAP[word.toLowerCase()]) return "noun";
    if (word.endsWith("ć")) return "verb";
    return "unknown";
}

// =====================
// INFLECTION
// =====================
function inflect(lemma, grammaticalCase, number) {
    const entry = DECLENSIONS[lemma];
    if (!entry) return lemma;

    return (
        entry[number][grammaticalCase] ||
        entry[number]["nominative"] ||
        lemma
    );
}

// =====================
// WORD TRANSLATION
// =====================
function translateWord(word, prevWord = "") {
    const clean = word.toLowerCase();

    const lemma = LEMMA_MAP[clean];
    if (!lemma) return word;

    const grammaticalCase = detectPolishCase(clean, prevWord);
    const number = detectPlural(clean) ? "plural" : "singular";

    return inflect(lemma, grammaticalCase, number);
}

// =====================
// SENTENCE ENGINE
// =====================
function translateSentence(sentence) {
    const tokens = sentence.split(/\s+/);

    return tokens.map((word, index) => {
        const prev = index > 0 ? tokens[index - 1] : "";
        return translateWord(word, prev);
    }).join(" ");
}

// =====================
// ADVANCED (STRUCTURE)
// =====================
function analyzeSentence(sentence) {
    const tokens = sentence.split(/\s+/);

    return tokens.map((word, i) => {
        return {
            word,
            pos: detectPOS(word),
            case: detectPolishCase(word, tokens[i - 1] || ""),
            number: detectPlural(word) ? "plural" : "singular"
        };
    });
}

// =====================
// DEBUG
// =====================
function debugDeclension(lemma) {
    return DECLENSIONS[lemma] || null;
}

// =====================
// EXPORT
// =====================
export {
    initDeclination,
    translateSentence,
    translateWord,
    analyzeSentence,
    debugDeclension
};
