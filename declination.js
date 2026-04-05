// declination.js
// PROTO-SLAVIC DECLENSION ENGINE v3 (linguistic-grade)

// =====================
// GLOBAL
// =====================
let PATTERNS = {};
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

    PATTERNS = extractPatterns(vuzorData);
    LEMMA_MAP = buildLemmaMap(osnovaData);
}

// =====================
// LEMMA MAP
// =====================
function buildLemmaMap(data) {
    const map = {};

    data.forEach(entry => {
        const pl = entry["polish"]?.toLowerCase();
        const slo = entry["slovian"];

        if (pl && slo) {
            map[pl] = slo;
        }
    });

    return map;
}

// =====================
// DECLENSION CLASSES
// =====================
const ENDINGS = {
    a_feminine: {
        singular: {
            nominative: "a",
            accusative: "ǫ",
            genitive: "y",
            dative: "ě",
            instrumental: "ojǫ",
            locative: "ě",
            vocative: "o"
        },
        plural: {
            nominative: "y",
            accusative: "y",
            genitive: "",
            dative: "am",
            instrumental: "ami",
            locative: "ah",
            vocative: "y"
        }
    },

    o_neuter: {
        singular: {
            nominative: "o",
            accusative: "o",
            genitive: "a",
            dative: "u",
            instrumental: "om",
            locative: "ě",
            vocative: "o"
        },
        plural: {
            nominative: "a",
            accusative: "a",
            genitive: "",
            dative: "am",
            instrumental: "ami",
            locative: "ah",
            vocative: "a"
        }
    },

    consonant_masculine: {
        singular: {
            nominative: "",
            accusative: "",
            genitive: "a",
            dative: "u",
            instrumental: "om",
            locative: "ě",
            vocative: "e"
        },
        plural: {
            nominative: "y",
            accusative: "y",
            genitive: "ov",
            dative: "am",
            instrumental: "ami",
            locative: "ah",
            vocative: "y"
        }
    }
};

// =====================
// PATTERN EXTRACTION (fallback)
// =====================
function extractPatterns(data) {
    const patterns = {};

    data.forEach(entry => {
        const typeCase = entry["type and case"];
        const form = entry["slovian"];

        const lemmaMatch = typeCase.match(/"([^"]+)"/);
        if (!lemmaMatch) return;

        const lemma = lemmaMatch[1];

        const caseName = detectCase(typeCase);
        const number = detectNumber(typeCase);

        const type = getDeclensionType(lemma);
        const stem = getStem(lemma);

        const ending = form.replace(stem, "");

        if (!patterns[type]) {
            patterns[type] = { singular: {}, plural: {} };
        }

        patterns[type][number][caseName] = ending;
    });

    return patterns;
}

// =====================
// TYPE DETECTION
// =====================
function getDeclensionType(word) {
    if (word.endsWith("a")) return "a_feminine";
    if (word.endsWith("o")) return "o_neuter";
    return "consonant_masculine";
}

function getStem(word) {
    if (word.endsWith("a") || word.endsWith("o")) {
        return word.slice(0, -1);
    }
    return word;
}

// =====================
// DETECT CASE / NUMBER
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
// PHONOLOGY
// =====================
function applyPhonology(stem, ending) {
    let word = stem + ending;

    // k → c przed i/ě
    word = word.replace(/k([iě])/g, "c$1");

    // g → z przed i/ě
    word = word.replace(/g([iě])/g, "z$1");

    // h → s przed i/ě
    word = word.replace(/h([iě])/g, "s$1");

    return word;
}

// =====================
// INFLECTION ENGINE
// =====================
function inflect(lemma, grammaticalCase, number = "singular") {
    const type = getDeclensionType(lemma);
    const stem = getStem(lemma);

    // 1. reguły gramatyczne
    const endings = ENDINGS[type];
    let ending = endings?.[number]?.[grammaticalCase];

    // 2. fallback do vuzor (jeśli istnieje)
    if (!ending && PATTERNS[type]) {
        ending = PATTERNS[type][number][grammaticalCase];
    }

    if (ending === undefined) return lemma;

    return applyPhonology(stem, ending);
}

// =====================
// NLP (PL → CASE)
// =====================
function detectPolishCase(word, prevWord = "") {
    word = word.toLowerCase();
    prevWord = prevWord.toLowerCase();

    if (["do", "od", "bez"].includes(prevWord)) return "genitive";
    if (["dla", "ku"].includes(prevWord)) return "dative";
    if (["z", "ze"].includes(prevWord)) return "instrumental";
    if (["o", "na", "w"].includes(prevWord)) return "locative";

    if (word.endsWith("ę")) return "accusative";
    if (word.endsWith("ą")) return "instrumental";
    if (word.endsWith("om")) return "dative";
    if (word.endsWith("ach")) return "locative";
    if (word.endsWith("ów")) return "genitive";

    return "nominative";
}

function detectPlural(word) {
    return word.endsWith("y") || word.endsWith("i") || word.endsWith("e");
}

// =====================
// TRANSLATION
// =====================
function translateWord(plWord, prevWord = "") {
    const clean = plWord.toLowerCase();

    const lemma = LEMMA_MAP[clean];
    if (!lemma) return plWord;

    const grammaticalCase = detectPolishCase(clean, prevWord);
    const number = detectPlural(clean) ? "plural" : "singular";

    return inflect(lemma, grammaticalCase, number);
}

function translateSentence(sentence) {
    const tokens = sentence.split(/\s+/);

    return tokens.map((word, i) => {
        const prev = i > 0 ? tokens[i - 1] : "";
        return translateWord(word, prev);
    }).join(" ");
}

// =====================
// DEBUG
// =====================
function debugWord(lemma) {
    return {
        nom: inflect(lemma, "nominative"),
        acc: inflect(lemma, "accusative"),
        gen: inflect(lemma, "genitive"),
        dat: inflect(lemma, "dative"),
        ins: inflect(lemma, "instrumental"),
        loc: inflect(lemma, "locative")
    };
}

// =====================
// EXPORT
// =====================
export {
    initDeclination,
    inflect,
    translateWord,
    translateSentence,
    debugWord
};
