/* slovo_ml_bridge.js
 * Warstwa ML + odmiana kontekstowa + interpunkcja do starego script.js.
 * v6: korekta + odmiana + poprawne rozpoznawanie pridavьnik i szyk grup.
 *
 * Ładuj w index.html dokładnie w tej kolejności:
 * <script src="slovo_model.js"></script>
 * <script src="script.js"></script>
 * <script src="slovo_ml_bridge.js"></script>
 */
(function () {
    "use strict";

    let slovoMLBridgeModel = null;
    let slovoMLBridgeLoading = null;

    const BRIDGE = {
        loaded: false,
        loading: null,
        pl2slo: new Map(),
        slo2pl: new Map(),
        sentPl2Slo: new Map(),
        sentSlo2Pl: new Map(),
        formsByLemmaPl2Slo: new Map(),
        formsByLemmaSlo2Pl: new Map(),
        stats: {
            entries: 0,
            sentences: 0,
            lemmaForms: 0
        }
    };

    /*
     * false = tryb bezpieczny: nie zgaduje pojedynczych nieznanych słów.
     * true  = tryb eksperymentalny: model może zgadywać nieznane wyrazy.
     */
    const USE_GUESS_FALLBACK = false;

    /*
     * false = pojedyncze słowa mają iść z osnova/vuzor, nie z modelu.
     * To chroni jery: ь, ъ oraz nosówki: ę, ǫ.
     */
    const TRUST_MODEL_SINGLE_WORD = false;

    /*
     * Stare reorderSmart zostaje jako opcja awaryjna, ale niżej jest własna
     * funkcja reorderSlovianAdjacentGroups(), która układa obok siebie:
     * liczebnik → przymiotnik → rzeczownik.
     */
    const USE_REORDER_SMART = false;

    const MAX_PHRASE_WORDS = 10;
    // --- KOREKTA WEJŚCIA PRZEZ GOOGLE TRANSLATE ---
    // Działa tylko wtedy, gdy język źródłowy NIE jest słowiański.
    // Przykład: EN -> EN jako korekta -> PL -> SLO.
    const ENABLE_GOOGLE_INPUT_CORRECTION = true;
    const AUTO_USE_GOOGLE_CORRECTION = true;
    const CORRECTION_MIN_LENGTH = 4;
    const correctionCache = new Map();
    let lastCorrectionKey = "";

    function normalizeCorrectionCompare(text) {
        return String(text || "")
            .normalize("NFC")
            .replace(/[“”„]/g, '"')
            .replace(/[’]/g, "'")
            .replace(/\s+/g, " ")
            .trim()
            .toLocaleLowerCase("pl");
    }

    function shouldCorrectInput(text, src, tgt) {
        if (!ENABLE_GOOGLE_INPUT_CORRECTION) return false;
        if (!text || !text.trim()) return false;
        if (src === "slo") return false;
        if (String(text).trim().length < CORRECTION_MIN_LENGTH) return false;
        return true;
    }


    const LOCAL_CORRECTION_MAX_DISTANCE = 2;
    const LOCAL_CORRECTION_MIN_WORD_LENGTH = 4;
    const localCorrectionIndexCache = new Map();

    function getLocalCorrectionDict(src) {
        try {
            if (src === "pl") {
                if (BRIDGE && BRIDGE.pl2slo && BRIDGE.pl2slo.size) {
                    const obj = Object.create(null);
                    BRIDGE.pl2slo.forEach(function (_, key) { obj[key] = true; });
                    return obj;
                }
                if (typeof plToSlo !== "undefined") return plToSlo || {};
            }
            if (src === "slo" && typeof sloToPl !== "undefined") return sloToPl || {};
        } catch (e) {}
        return null;
    }

    function buildLocalCorrectionIndex(src) {
        const cacheKey = src + "::" + (BRIDGE && BRIDGE.pl2slo ? BRIDGE.pl2slo.size : 0);
        if (localCorrectionIndexCache.has(cacheKey)) return localCorrectionIndexCache.get(cacheKey);
        const dict = getLocalCorrectionDict(src);
        const index = new Map();
        if (!dict) {
            localCorrectionIndexCache.set(cacheKey, index);
            return index;
        }
        Object.keys(dict).forEach(function (word) {
            const w = normalizeCorrectionCompare(word);
            if (!w || w.length < LOCAL_CORRECTION_MIN_WORD_LENGTH) return;
            if (!/^[\p{L}\p{M}0-9'’]+$/u.test(w)) return;
            const first = Array.from(w)[0] || "";
            const len = Array.from(w).length;
            const key = first + "|" + len;
            if (!index.has(key)) index.set(key, []);
            index.get(key).push(w);
        });
        localCorrectionIndexCache.set(cacheKey, index);
        return index;
    }

    function levenshteinLimited(a, b, limit) {
        const aa = Array.from(a);
        const bb = Array.from(b);
        if (Math.abs(aa.length - bb.length) > limit) return limit + 1;
        if (a === b) return 0;
        let prev = new Array(bb.length + 1);
        let curr = new Array(bb.length + 1);
        for (let j = 0; j <= bb.length; j++) prev[j] = j;
        for (let i = 1; i <= aa.length; i++) {
            curr[0] = i;
            let rowMin = curr[0];
            for (let j = 1; j <= bb.length; j++) {
                const cost = aa[i - 1] === bb[j - 1] ? 0 : 1;
                curr[j] = Math.min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + cost);
                if (curr[j] < rowMin) rowMin = curr[j];
            }
            if (rowMin > limit) return limit + 1;
            [prev, curr] = [curr, prev];
        }
        return prev[bb.length];
    }

    function applyOriginalWordCase(original, corrected) {
        const raw = String(original || "");
        const c = String(corrected || "");
        if (!c) return c;
        if (raw.length > 1 && raw === raw.toLocaleUpperCase("pl")) return c.toLocaleUpperCase("pl");
        if (raw[0] && raw[0] === raw[0].toLocaleUpperCase("pl") && raw[0] !== raw[0].toLocaleLowerCase("pl")) {
            return c.charAt(0).toLocaleUpperCase("pl") + c.slice(1);
        }
        return c;
    }

    function findClosestLocalWord(word, src) {
        const dict = getLocalCorrectionDict(src);
        if (!dict) return null;
        const normalized = normalizeCorrectionCompare(word);
        if (!normalized || normalized.length < LOCAL_CORRECTION_MIN_WORD_LENGTH) return null;
        if (Object.prototype.hasOwnProperty.call(dict, normalized)) return null;
        if (!/^[\p{L}\p{M}0-9'’]+$/u.test(normalized)) return null;
        const chars = Array.from(normalized);
        const first = chars[0] || "";
        const len = chars.length;
        const index = buildLocalCorrectionIndex(src);
        let best = null;
        let bestDist = LOCAL_CORRECTION_MAX_DISTANCE + 1;
        for (let l = len - LOCAL_CORRECTION_MAX_DISTANCE; l <= len + LOCAL_CORRECTION_MAX_DISTANCE; l++) {
            const candidates = index.get(first + "|" + l) || [];
            for (const candidate of candidates) {
                const dist = levenshteinLimited(normalized, candidate, LOCAL_CORRECTION_MAX_DISTANCE);
                if (dist < bestDist) {
                    bestDist = dist;
                    best = candidate;
                    if (dist === 1) break;
                }
            }
            if (bestDist === 1) break;
        }
        if (!best || bestDist > LOCAL_CORRECTION_MAX_DISTANCE) return null;
        return applyOriginalWordCase(word, best);
    }

    function localCorrectText(text, src) {
        const original = String(text || "");
        if (src !== "pl") return original;
        const tokens = original.match(/([\p{L}\p{M}0-9'’]+|\s+|[^\s\p{L}\p{M}0-9'’]+)/gu) || [original];
        let changed = false;
        const correctedTokens = tokens.map(function (token) {
            if (!/^[\p{L}\p{M}0-9'’]+$/u.test(token)) return token;
            const corrected = findClosestLocalWord(token, src);
            if (corrected && normalizeCorrectionCompare(corrected) !== normalizeCorrectionCompare(token)) {
                changed = true;
                return corrected;
            }
            return token;
        });
        return changed ? correctedTokens.join("") : original;
    }

    async function googleRawForCorrection(text, s, t) {
        try {
            if (typeof googleRaw === "function") {
                return await googleRaw(text, s, t);
            }

            if (typeof google === "function" && s !== t) {
                return await google(text, s, t);
            }

            const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=${s}&tl=${t}&dt=t&q=${encodeURIComponent(text)}`;
            const res = await fetch(url);
            const data = await res.json();

            if (!Array.isArray(data) || !Array.isArray(data[0])) return text;

            return data[0]
                .map(part => Array.isArray(part) ? (part[0] || "") : "")
                .join("");
        } catch (e) {
            console.warn("Google correction error:", e);
            return text;
        }
    }

    async function getGoogleCorrectedInput(text, lang) {
        const original = String(text || "");
        const key = `${lang}::${original}`;

        if (correctionCache.has(key)) return correctionCache.get(key);

        // Google Translate przy sl=pl&tl=pl często zwraca dokładnie to samo.
        // Dla polskiego używamy więc lokalnej bazy osnova/vuzor jako korektora.
        let corrected = localCorrectText(original, lang);

        if (normalizeCorrectionCompare(corrected) === normalizeCorrectionCompare(original)) {
            try {
                corrected = await googleRawForCorrection(original, lang, lang);
                if (!corrected || !corrected.trim()) corrected = original;
            } catch (e) {
                corrected = original;
            }
        }

        if (normalizeCorrectionCompare(corrected) === normalizeCorrectionCompare(original) && lang !== "pl") {
            try {
                const autoCorrected = await googleRawForCorrection(original, "auto", lang);
                if (autoCorrected && autoCorrected.trim()) corrected = autoCorrected;
            } catch (e) {}
        }

        correctionCache.set(key, corrected);
        return corrected;
    }

    function ensureCorrectionBox() {
        let box = document.getElementById("correctionSuggestionBox");
        if (box) return box;

        const input = document.getElementById("userInput");
        if (!input || !input.parentNode) return null;

        box = document.createElement("div");
        box.id = "correctionSuggestionBox";
        box.style.display = "none";
        box.style.margin = "8px 0 10px 0";
        box.style.padding = "10px 12px";
        box.style.border = "1px solid #d7e3ff";
        box.style.borderRadius = "12px";
        box.style.background = "#f4f8ff";
        box.style.color = "#1f2937";
        box.style.fontSize = "14px";
        box.style.lineHeight = "1.4";

        input.insertAdjacentElement("afterend", box);
        return box;
    }

    function hideCorrectionSuggestion() {
        const box = document.getElementById("correctionSuggestionBox");
        if (box) {
            box.style.display = "none";
            box.innerHTML = "";
        }
        lastCorrectionKey = "";
    }

    function showCorrectionSuggestion(original, corrected, lang) {
        const box = ensureCorrectionBox();
        if (!box) return;

        const key = `${lang}::${original}::${corrected}`;
        if (lastCorrectionKey === key) return;
        lastCorrectionKey = key;

        box.innerHTML = "";

        const label = document.createElement("span");
        label.textContent = "Sugestia poprawy: ";

        const suggestion = document.createElement("button");
        suggestion.type = "button";
        suggestion.textContent = corrected;
        suggestion.style.border = "none";
        suggestion.style.background = "transparent";
        suggestion.style.color = "#0b63ff";
        suggestion.style.fontWeight = "600";
        suggestion.style.cursor = "pointer";
        suggestion.style.padding = "0 4px";

        const useCorrection = function () {
            const input = document.getElementById("userInput");
            if (input) {
                input.value = corrected;
                hideCorrectionSuggestion();
                if (typeof translate === "function") translate();
            }
        };

        suggestion.onclick = useCorrection;

        const useBtn = document.createElement("button");
        useBtn.type = "button";
        useBtn.textContent = "Użyj";
        useBtn.style.marginLeft = "10px";
        useBtn.style.padding = "4px 10px";
        useBtn.style.border = "1px solid #0b63ff";
        useBtn.style.borderRadius = "8px";
        useBtn.style.background = "#ffffff";
        useBtn.style.color = "#0b63ff";
        useBtn.style.cursor = "pointer";
        useBtn.style.fontWeight = "600";
        useBtn.onclick = useCorrection;

        const ignoreBtn = document.createElement("button");
        ignoreBtn.type = "button";
        ignoreBtn.textContent = "Ignoruj";
        ignoreBtn.style.marginLeft = "6px";
        ignoreBtn.style.padding = "4px 10px";
        ignoreBtn.style.border = "1px solid #d1d5db";
        ignoreBtn.style.borderRadius = "8px";
        ignoreBtn.style.background = "#ffffff";
        ignoreBtn.style.color = "#374151";
        ignoreBtn.style.cursor = "pointer";
        ignoreBtn.onclick = hideCorrectionSuggestion;

        box.appendChild(label);
        box.appendChild(suggestion);
        box.appendChild(useBtn);
        box.appendChild(ignoreBtn);
        box.style.display = "block";
    }

    async function prepareInputForTranslation(text, src, tgt) {
        const original = String(text || "");

        if (!shouldCorrectInput(original, src, tgt)) {
            hideCorrectionSuggestion();
            return { text: original, corrected: false, suggestion: original };
        }

        const corrected = await getGoogleCorrectedInput(original, src);

        if (corrected && normalizeCorrectionCompare(corrected) !== normalizeCorrectionCompare(original)) {
            showCorrectionSuggestion(original, corrected, src);
            return {
                text: AUTO_USE_GOOGLE_CORRECTION ? corrected : original,
                corrected: true,
                suggestion: corrected
            };
        }

        hideCorrectionSuggestion();
        return { text: original, corrected: false, suggestion: original };
    }


    const DATA_FILES = [
        { url: "vuzor.json", source: "vuzor", priority: 400 },
        { url: "osnova.json", source: "osnova", priority: 300 }
    ];

    const EXAMPLE_SENTENCE_FILES = [
        { url: "example_sentences.json", source: "example_sentences", priority: 1000 }
    ];

    /*
     * Kropka i myślnik NIE mogą być częścią zwykłego słowa.
     * Poprzednia wersja traktowała "chleba." jako jeden token,
     * więc nie znajdowała hasła "chleba" w JSON-ach.
     * URL-e i e-maile są chronione wcześniej przez protectSpecialText().
     */
    const TOKEN_RE = /([\p{L}\p{M}0-9'’]+|\s+|[^\s\p{L}\p{M}0-9'’]+)/gu;
    const WORD_RE = /^[\p{L}\p{M}0-9'’]+$/u;
    const URL_RE = /(https?:\/\/[^\s]+|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/g;
    const TERMINAL_PUNCT_RE = /([.!?…]+)$/u;

    const CASE_BY_PREPOSITION = {
        "do": "genitive",
        "od": "genitive",
        "bez": "genitive",
        "dla": "genitive",
        "u": "genitive",
        "około": "genitive",
        "wokół": "genitive",
        "podczas": "genitive",
        "według": "genitive",
        "oprócz": "genitive",

        "ku": "dative",
        "dzięki": "dative",
        "wbrew": "dative",
        "przeciw": "dative",
        "przeciwko": "dative",

        "o": "locative",
        "w": "locative",
        "we": "locative",
        "na": "locative",
        "po": "locative",
        "przy": "locative",

        "z": "instrumental",
        "ze": "instrumental",
        "nad": "instrumental",
        "pod": "instrumental",
        "przed": "instrumental",
        "między": "instrumental",
        "pomiędzy": "instrumental",
        "za": "instrumental"
    };

    const ACCUSATIVE_VERBS = new Set([
        "mam", "masz", "ma", "mamy", "macie", "mają",
        "widzę", "widzisz", "widzi", "widzimy", "widzicie", "widzą",
        "znam", "znasz", "zna", "znamy", "znacie", "znają",
        "lubię", "lubisz", "lubi", "lubimy", "lubicie", "lubią",
        "kocham", "kochasz", "kocha", "kochamy", "kochacie", "kochają",
        "biorę", "bierzesz", "bierze", "bierzemy", "bierzecie", "biorą",
        "weź", "weźcie", "bierz", "bierzcie",
        "daj", "daje", "daję", "dajesz", "dajemy", "dają",
        "kupuję", "kupujesz", "kupuje", "kupujemy", "kupują",
        "robię", "robisz", "robi", "robimy", "robią",
        "piszę", "piszesz", "pisze", "piszemy", "piszą",
        "czytam", "czytasz", "czyta", "czytamy", "czytają",
        "buduję", "budujesz", "buduje", "budują"
    ]);

    function normalizeKey(text) {
        return String(text ?? "")
            .normalize("NFC")
            .replace(/[’]/g, "'")
            .replace(/\s+/g, " ")
            .trim()
            .toLocaleLowerCase("pl");
    }

    function stripTerminalPunct(text) {
        return String(text ?? "").trim().replace(TERMINAL_PUNCT_RE, "").trim();
    }

    function getTerminalPunct(text) {
        const m = String(text ?? "").trim().match(TERMINAL_PUNCT_RE);
        return m ? m[1] : "";
    }

    function normalizeSentenceKey(text) {
        return normalizeKey(stripTerminalPunct(text))
            .replace(/\s+([,.;:!?])/g, "$1")
            .replace(/\s+/g, " ");
    }

    function isWord(token) {
        return WORD_RE.test(token) && /[\p{L}\p{M}0-9]/u.test(token);
    }

    function isSpace(token) {
        return /^\s+$/.test(token);
    }

    function wordCount(text) {
        const tokens = String(text ?? "").match(TOKEN_RE) || [];
        return tokens.filter(isWord).length;
    }

    function sameNormalized(a, b) {
        return normalizeKey(a) === normalizeKey(b);
    }

    function getCaseType(text) {
        const s = String(text || "");
        const letters = Array.from(s).filter(ch => /\p{L}/u.test(ch));
        if (!letters.length) return "lower";

        const joined = letters.join("");
        if (
            joined === joined.toLocaleUpperCase("pl") &&
            joined !== joined.toLocaleLowerCase("pl") &&
            joined.length > 1
        ) {
            return "upper";
        }

        const first = letters[0];
        if (
            first === first.toLocaleUpperCase("pl") &&
            first !== first.toLocaleLowerCase("pl")
        ) {
            return "title";
        }

        return "lower";
    }

    function applyCaseLike(source, target) {
        const result = String(target ?? "");
        const caseType = getCaseType(source);

        if (caseType === "upper") {
            return result.toLocaleUpperCase("pl");
        }

        if (caseType === "title") {
            const chars = Array.from(result);
            if (!chars.length) return result;
            chars[0] = chars[0].toLocaleUpperCase("pl");
            return chars.join("");
        }

        return result;
    }

    function protectSpecialText(text) {
        const placeholders = [];
        const safe = String(text ?? "").replace(URL_RE, function (match) {
            const key = "__SLOVO_SPECIAL_" + placeholders.length + "__";
            placeholders.push(match);
            return key;
        });

        return {
            text: safe,
            restore(value) {
                return String(value ?? "").replace(/__SLOVO_SPECIAL_(\d+)__/g, function (_, id) {
                    return placeholders[Number(id)] || "";
                });
            }
        };
    }

    function parseMeta(typeCase) {
        const info = normalizeKey(typeCase || "");
        const meta = {
            raw: String(typeCase || ""),
            wordClass: "unknown",
            grammaticalCase: null,
            number: null,
            isPhrase: false,
            lemma: null
        };

        const lemmaMatch = String(typeCase || "").match(/jimenьnik\s*:\s*"([^"]+)"/i);
        if (lemmaMatch && lemmaMatch[1]) meta.lemma = normalizeKey(lemmaMatch[1]);

        if (info.includes("phrase") || info.includes("rěčen")) meta.isPhrase = true;
        if (info.includes("noun") || info.includes("jimenьnik") || info.includes("imenьnik") || info.includes("rzeczownik")) meta.wordClass = "noun";
        if (info.includes("adjective") || info.includes("priloga") || info.includes("pridavьnik") || info.includes("pridavnik") || info.includes("przymiotnik")) meta.wordClass = "adjective";
        if (info.includes("numeral") || info.includes("ličьnik") || info.includes("liczebnik")) meta.wordClass = "numeral";
        if (info.includes("verb") || info.includes("glagol") || info.includes("golgol") || info.includes("czasownik")) meta.wordClass = "verb";
        if (meta.isPhrase) meta.wordClass = "phrase";

        if (info.includes("nominative") || info.includes("jimenovьnik")) meta.grammaticalCase = "nominative";
        else if (info.includes("accusative") || info.includes("vinьnik")) meta.grammaticalCase = "accusative";
        else if (info.includes("genitive") || info.includes("rodilьnik")) meta.grammaticalCase = "genitive";
        else if (info.includes("locative") || info.includes("městьnik")) meta.grammaticalCase = "locative";
        else if (info.includes("dative") || info.includes("měrьnik")) meta.grammaticalCase = "dative";
        else if (info.includes("instrumental") || info.includes("orǫdьnik")) meta.grammaticalCase = "instrumental";
        else if (info.includes("vocative") || info.includes("zovanьnik")) meta.grammaticalCase = "vocative";

        if (info.includes("singular") || info.includes("poedinьna")) meta.number = "singular";
        else if (info.includes("plural") || info.includes("munoga")) meta.number = "plural";

        return meta;
    }

    function addToMap(map, source, target, data) {
        const src = String(source ?? "").trim();
        const tgt = String(target ?? "").trim();
        if (!src || !tgt) return;

        const key = normalizeKey(src);
        const list = map.get(key) || [];
        const meta = parseMeta(data.typeCase);

        const candidate = {
            source: src,
            target: tgt,
            context: data.context || "",
            typeCase: data.typeCase || "",
            sourceFile: data.source || "unknown",
            priority: data.priority || 0,
            meta
        };

        list.push(candidate);
        list.sort(compareCandidateStatic);
        map.set(key, list);
        BRIDGE.stats.entries++;

        addLemmaForm(map, candidate);
    }

    function lemmaFormKey(lemma, grammaticalCase, number) {
        return [normalizeKey(lemma), grammaticalCase || "", number || ""].join("|");
    }

    function addLemmaForm(map, candidate) {
        const meta = candidate && candidate.meta;
        if (!meta || !meta.lemma || !meta.grammaticalCase) return;
        if (meta.wordClass !== "noun" && meta.wordClass !== "adjective" && meta.wordClass !== "numeral") return;

        const lemmaMap = map === BRIDGE.slo2pl ? BRIDGE.formsByLemmaSlo2Pl : BRIDGE.formsByLemmaPl2Slo;
        const keys = [
            lemmaFormKey(meta.lemma, meta.grammaticalCase, meta.number || ""),
            lemmaFormKey(meta.lemma, meta.grammaticalCase, "")
        ];

        for (const key of keys) {
            const list = lemmaMap.get(key) || [];
            list.push(candidate);
            list.sort(compareCandidateStatic);
            lemmaMap.set(key, list);
            BRIDGE.stats.lemmaForms++;
        }
    }

    function lookupLemmaForm(candidate, wantedCase, direction) {
        if (!candidate || !candidate.meta || !candidate.meta.lemma || !wantedCase) return null;
        if (candidate.meta.wordClass !== "noun" && candidate.meta.wordClass !== "adjective" && candidate.meta.wordClass !== "numeral") return null;

        const lemmaMap = direction === "slo2pl" ? BRIDGE.formsByLemmaSlo2Pl : BRIDGE.formsByLemmaPl2Slo;
        const number = candidate.meta.number || "singular";
        const keys = [
            lemmaFormKey(candidate.meta.lemma, wantedCase, number),
            lemmaFormKey(candidate.meta.lemma, wantedCase, "singular"),
            lemmaFormKey(candidate.meta.lemma, wantedCase, "")
        ];

        for (const key of keys) {
            const list = lemmaMap.get(key);
            if (list && list.length) return list[0];
        }

        return null;
    }

    function inflectCandidateTarget(candidate, sourceText, tokens, startIndex, direction) {
        const wantedCase = inferWantedCase(tokens || [], startIndex || 0, sourceText, direction);
        if (!wantedCase || direction === "slo2pl") return candidate.target;

        const currentCase = candidate.meta && candidate.meta.grammaticalCase;
        if (currentCase === wantedCase) return candidate.target;

        const lemmaForm = lookupLemmaForm(candidate, wantedCase, direction);
        if (lemmaForm && lemmaForm.target) return lemmaForm.target;

        return candidate.target;
    }

    function addSentencePair(polish, slovian, data) {
        const pl = String(polish ?? "").trim();
        const slo = String(slovian ?? "").trim();
        if (!pl || !slo) return;

        const plKey = normalizeSentenceKey(pl);
        const sloKey = normalizeSentenceKey(slo);

        BRIDGE.sentPl2Slo.set(plKey, {
            source: pl,
            target: slo,
            priority: data.priority || 1000,
            sourceFile: data.source || "example_sentences"
        });

        BRIDGE.sentSlo2Pl.set(sloKey, {
            source: slo,
            target: pl,
            priority: data.priority || 1000,
            sourceFile: data.source || "example_sentences"
        });

        BRIDGE.stats.sentences++;
    }

    function compareCandidateStatic(a, b) {
        const pa = a.priority || 0;
        const pb = b.priority || 0;
        if (pb !== pa) return pb - pa;

        const aw = wordCount(a.source);
        const bw = wordCount(b.source);
        if (bw !== aw) return bw - aw;

        const an = a.meta && a.meta.grammaticalCase === "nominative" ? 1 : 0;
        const bn = b.meta && b.meta.grammaticalCase === "nominative" ? 1 : 0;
        if (bn !== an) return bn - an;

        const as = a.meta && a.meta.number === "singular" ? 1 : 0;
        const bs = b.meta && b.meta.number === "singular" ? 1 : 0;
        return bs - as;
    }

    function getPreviousWord(tokens, index, step) {
        let found = 0;
        for (let i = index - 1; i >= 0; i--) {
            if (isWord(tokens[i])) {
                found++;
                if (found === step) return normalizeKey(tokens[i]);
            } else if (!isSpace(tokens[i])) {
                if (found === 0) continue;
                break;
            }
        }
        return "";
    }

    function inferPolishCaseFromEnding(word) {
        const w = normalizeKey(word);
        if (!w) return null;

        if (/(ami|emi|mi)$/.test(w)) return "instrumental";
        if (/(ach|ech)$/.test(w)) return "locative";
        if (/(om)$/.test(w)) return "dative";
        if (/(ą)$/.test(w)) return "instrumental";
        if (/(ę)$/.test(w)) return "accusative";

        return null;
    }

    function inferWantedCase(tokens, startIndex, sourceText, direction) {
        if (direction === "slo2pl") return null;

        const src = normalizeKey(sourceText);
        const byEnding = inferPolishCaseFromEnding(src);

        const prev1 = getPreviousWord(tokens, startIndex, 1);
        const prev2 = getPreviousWord(tokens, startIndex, 2);

        if (prev1 && CASE_BY_PREPOSITION[prev1]) {
            if ((prev1 === "z" || prev1 === "ze") && byEnding === "genitive") return "genitive";
            return CASE_BY_PREPOSITION[prev1];
        }

        if (prev2 && prev1 && normalizeKey(prev2 + " " + prev1) === "z powodu") return "genitive";

        if (prev1 && ACCUSATIVE_VERBS.has(prev1)) return "accusative";

        if (byEnding) return byEnding;

        return "nominative";
    }


    function composeLiteralWordByWord(sourceText, direction) {
        /*
         * Bezpieczna kontrola jakości dla fraz typu "jaka jest cena".
         * Jeżeli każde słowo frazy ma jasny odpowiednik pojedynczy, a fraza z osnova
         * daje inną/zepsutą postać, obniżamy jej ranking i tłumaczymy słowo po słowie.
         */
        const tokens = String(sourceText ?? "").match(TOKEN_RE) || [];
        const out = [];
        let translatedAny = false;

        for (const token of tokens) {
            if (!isWord(token)) {
                out.push(token);
                continue;
            }

            const list = mapForDirection(direction).get(normalizeKey(token));
            if (!list || !list.length) return null;

            const single = list.find(c =>
                wordCount(c.source) === 1 &&
                (!c.meta || !c.meta.isPhrase)
            ) || list[0];

            if (!single || !single.target) return null;

            out.push(applyCaseLike(token, single.target));
            translatedAny = true;
        }

        if (!translatedAny) return null;
        return fixOutputSpacing(out.join(""));
    }

    function phraseConflictsWithSingleWords(candidate, direction) {
        if (!candidate || !candidate.meta || !candidate.meta.isPhrase) return false;
        if (candidate.sourceFile === "example_sentences") return false;

        const srcWords = wordCount(candidate.source);
        const tgtWords = wordCount(candidate.target);

        if (srcWords < 2 || srcWords > 6) return false;
        if (tgtWords < 1) return false;

        const literal = composeLiteralWordByWord(candidate.source, direction);
        if (!literal) return false;

        const phraseTarget = fixOutputSpacing(candidate.target);
        if (normalizeKey(literal) === normalizeKey(phraseTarget)) return false;

        /*
         * Nie kasujemy prawdziwych idiomów typu "z resztą" → "vu konьci".
         * Penalizujemy głównie wtedy, gdy fraza wygląda jak zwykłe złożenie słów
         * i różni się tylko podejrzaną pisownią/końcówką.
         */
        const litSet = new Set(normalizeKey(literal).split(/\s+/).filter(Boolean));
        const trgSet = new Set(normalizeKey(phraseTarget).split(/\s+/).filter(Boolean));
        let overlap = 0;
        for (const w of trgSet) {
            if (litSet.has(w)) overlap++;
        }

        const similarity = overlap / Math.max(1, Math.min(litSet.size, trgSet.size));
        if (similarity >= 0.5) return true;

        return false;
    }

    function candidateScore(candidate, sourceText, tokens, startIndex, direction) {
        let score = candidate.priority || 0;
        const wc = wordCount(candidate.source);
        score += wc * 40;

        if (candidate.meta && candidate.meta.isPhrase) {
            score += 80;

            /*
             * Nie pozwól wadliwej frazie z osnova.json przykryć poprawnych
             * pojedynczych form z osnova/vuzor, np. "jaka jest cena" nie może
             * dawać "cěnьa", jeżeli pojedyncze hasło "cena" daje "cěna".
             */
            if (phraseConflictsWithSingleWords(candidate, direction)) {
                score -= 10000;
            }
        }

        const wantedCase = inferWantedCase(tokens, startIndex, sourceText, direction);
        const cCase = candidate.meta && candidate.meta.grammaticalCase;

        if (wantedCase && cCase) {
            if (wantedCase === cCase) score += 90;
            else score -= 40;
        }

        if (!wantedCase && cCase === "nominative") score += 20;

        if (wc === 1 && cCase === "nominative" && candidate.meta && candidate.meta.number === "singular") {
            score += 25;
        }

        /*
         * Drobna preferencja: jeżeli wszystko inne równe, forma z jerem końcowym
         * częściej jest podstawowa w twojej bazie niż wersja obcięta.
         */
        if (/[ьъ]$/.test(candidate.target)) score += 3;

        return score;
    }

    function chooseCandidate(candidates, sourceText, tokens, startIndex, direction) {
        if (!candidates || !candidates.length) return null;
        let best = null;
        let bestScore = -Infinity;

        for (const cand of candidates) {
            const score = candidateScore(cand, sourceText, tokens || [], startIndex || 0, direction);
            if (score > bestScore) {
                best = cand;
                bestScore = score;
            }
        }

        return best;
    }

    async function fetchJsonMaybe(url) {
        try {
            const bust = url.includes("?") ? "&" : "?";
            const res = await fetch(url + bust + "v=" + Date.now(), { cache: "reload" });
            if (!res.ok) return null;
            return await res.json();
        } catch (e) {
            console.warn("Nie można pobrać:", url, e);
            return null;
        }
    }

    function absorbRows(rows, fileInfo) {
        if (!Array.isArray(rows)) return;

        for (const item of rows) {
            if (!item || typeof item !== "object") continue;

            const polish = item.polish;
            const slovian = item.slovian;

            if (polish && slovian) {
                const data = {
                    typeCase: item["type and case"] || item.type || "",
                    context: item.context || "",
                    source: fileInfo.source,
                    priority: fileInfo.priority
                };

                addToMap(BRIDGE.pl2slo, polish, slovian, data);
                addToMap(BRIDGE.slo2pl, slovian, polish, data);

                if (data.typeCase && (String(data.typeCase).includes("phrase") || String(data.typeCase).includes("rěčen"))) {
                    addSentencePair(polish, slovian, {
                        source: fileInfo.source,
                        priority: fileInfo.priority + 100
                    });
                }
            }
        }
    }

    async function loadBridgeData() {
        if (BRIDGE.loaded) return true;
        if (BRIDGE.loading) return BRIDGE.loading;

        BRIDGE.loading = (async function () {
            for (const fileInfo of EXAMPLE_SENTENCE_FILES) {
                const rows = await fetchJsonMaybe(fileInfo.url);
                if (Array.isArray(rows)) {
                    for (const row of rows) {
                        if (row && row.polish && row.slovian) {
                            addSentencePair(row.polish, row.slovian, fileInfo);
                        }
                    }
                }
            }

            for (const fileInfo of DATA_FILES) {
                const rows = await fetchJsonMaybe(fileInfo.url);
                absorbRows(rows, fileInfo);
            }

            /*
             * Awaryjnie wchłaniamy stare słowniki z script.js, jeżeli istnieją.
             * Mają niższy priorytet niż świeżo zbudowany indeks z plików.
             */
            try {
                if (typeof plToSlo !== "undefined") {
                    Object.keys(plToSlo || {}).forEach(function (pl) {
                        addToMap(BRIDGE.pl2slo, pl, plToSlo[pl], {
                            typeCase: "",
                            context: "",
                            source: "script.js/plToSlo",
                            priority: 100
                        });
                    });
                }
                if (typeof sloToPl !== "undefined") {
                    Object.keys(sloToPl || {}).forEach(function (slo) {
                        addToMap(BRIDGE.slo2pl, slo, sloToPl[slo], {
                            typeCase: "",
                            context: "",
                            source: "script.js/sloToPl",
                            priority: 100
                        });
                    });
                }
            } catch (e) {}

            BRIDGE.loaded = true;
            console.log("Slovo bridge data loaded:", BRIDGE.stats);
            return true;
        })();

        return BRIDGE.loading;
    }

    async function loadSlovoMLBridge() {
        if (slovoMLBridgeModel && BRIDGE.loaded) return true;
        if (slovoMLBridgeLoading) return slovoMLBridgeLoading;

        slovoMLBridgeLoading = (async function () {
            const status = document.getElementById("dbStatus");

            await loadBridgeData();

            try {
                if (typeof SlovoTranslator === "undefined") {
                    console.warn("Brak SlovoTranslator. Sprawdź kolejność skryptów w index.html.");
                    if (status) status.innerText = "Dictionary Engine Ready.";
                    return false;
                }

                slovoMLBridgeModel = await SlovoTranslator.loadFromUrl("model/slovo-model.json");

                console.log("Slovo ML model loaded.");
                if (status) status.innerText = "ML + Declension Engine Ready.";
                return true;

            } catch (e) {
                console.warn("Nie udało się załadować modelu ML, działa indeks z JSON:", e);
                slovoMLBridgeModel = null;

                if (status) status.innerText = "JSON Declension Engine Ready.";
                return true;
            }
        })();

        return slovoMLBridgeLoading;
    }

    function mapForDirection(direction) {
        return direction === "slo2pl" ? BRIDGE.slo2pl : BRIDGE.pl2slo;
    }

    function sentenceMapForDirection(direction) {
        return direction === "slo2pl" ? BRIDGE.sentSlo2Pl : BRIDGE.sentPl2Slo;
    }

    function lookupEntry(text, direction, tokens, startIndex) {
        const key = normalizeKey(text);
        const candidates = mapForDirection(direction).get(key);
        const best = chooseCandidate(candidates, text, tokens || [], startIndex || 0, direction);
        return best ? best.target : null;
    }

    function lookupSentence(text, direction) {
        const map = sentenceMapForDirection(direction);
        const key = normalizeSentenceKey(text);
        const hit = map.get(key);
        if (!hit) return null;

        return alignTerminalPunctuation(hit.target, text);
    }

    function alignTerminalPunctuation(target, source) {
        const sourcePunct = getTerminalPunct(source);
        let out = String(target ?? "").trim();

        if (sourcePunct) {
            out = stripTerminalPunct(out) + sourcePunct;
        } else {
            out = stripTerminalPunct(out);
        }

        return out;
    }

    function buildPhraseFromTokens(tokens, startIndex, maxWords) {
        let phrase = "";
        let usedWords = 0;
        let endIndex = startIndex;

        for (let i = startIndex; i < tokens.length; i++) {
            const token = tokens[i];

            if (isWord(token)) {
                phrase += token;
                usedWords++;
                endIndex = i + 1;

                if (usedWords >= maxWords) break;
                continue;
            }

            if (isSpace(token)) {
                phrase += " ";
                endIndex = i + 1;
                continue;
            }

            break;
        }

        return {
            phrase: phrase.trim(),
            words: usedWords,
            endIndex
        };
    }

    function findBestPhrase(tokens, startIndex, direction) {
        const map = mapForDirection(direction);
        let best = null;

        for (let max = MAX_PHRASE_WORDS; max >= 1; max--) {
            const built = buildPhraseFromTokens(tokens, startIndex, max);
            if (!built.phrase || built.words < 1) continue;

            const candidates = map.get(normalizeKey(built.phrase));
            if (!candidates || !candidates.length) continue;

            const candidate = chooseCandidate(candidates, built.phrase, tokens, startIndex, direction);
            if (!candidate) continue;

            const score = candidateScore(candidate, built.phrase, tokens, startIndex, direction) + built.words * 50;

            if (!best || score > best.score) {
                best = {
                    source: built.phrase,
                    target: inflectCandidateTarget(candidate, built.phrase, tokens, startIndex, direction),
                    endIndex: built.endIndex,
                    score,
                    words: built.words
                };
            }
        }

        return best;
    }

    function getSlovianWordType(token) {
        const key = normalizeKey(token);
        if (!key) return "";

        const candidates = BRIDGE.slo2pl.get(key);
        if (candidates && candidates.length) {
            for (const cand of candidates) {
                const type = cand && cand.meta && cand.meta.wordClass;
                if (type === "noun" || type === "adjective" || type === "numeral") return type;

                // Awaryjne rozpoznanie bezpośrednio po type and case,
                // gdy stary wpis nie został poprawnie sparsowany.
                const raw = normalizeKey((cand && cand.typeCase) || "");
                if (raw.includes("jimenьnik") || raw.includes("noun") || raw.includes("rzeczownik")) return "noun";
                if (raw.includes("pridavьnik") || raw.includes("pridavnik") || raw.includes("adjective") || raw.includes("priloga") || raw.includes("przymiotnik")) return "adjective";
                if (raw.includes("ličьnik") || raw.includes("numeral") || raw.includes("liczebnik")) return "numeral";
            }
        }

        try {
            if (typeof wordTypes !== "undefined" && wordTypes[key]) return wordTypes[key];
        } catch (e) {}

        return "";
    }

    function reorderSlovianAdjacentGroups(text) {
        const original = String(text ?? "");
        if (!original.trim()) return original;

        const protectedText = protectSpecialText(original);
        const tokens = protectedText.text.match(TOKEN_RE) || [protectedText.text];
        const out = [];
        const order = { numeral: 1, adjective: 2, noun: 3 };

        for (let i = 0; i < tokens.length; i++) {
            const token = tokens[i];
            const type = isWord(token) ? getSlovianWordType(token) : "";

            if (!(type === "noun" || type === "adjective" || type === "numeral")) {
                out.push(token);
                continue;
            }

            const group = [];
            let j = i;

            while (j < tokens.length) {
                if (isWord(tokens[j])) {
                    const t = getSlovianWordType(tokens[j]);
                    if (t === "noun" || t === "adjective" || t === "numeral") {
                        group.push({ val: tokens[j], type: t, originalIndex: group.length });
                        j++;
                        continue;
                    }
                    break;
                }

                if (isSpace(tokens[j])) {
                    let k = j + 1;
                    while (k < tokens.length && isSpace(tokens[k])) k++;
                    if (k < tokens.length && isWord(tokens[k])) {
                        const nt = getSlovianWordType(tokens[k]);
                        if (nt === "noun" || nt === "adjective" || nt === "numeral") {
                            j = k;
                            continue;
                        }
                    }
                    break;
                }

                break;
            }

            const hasNoun = group.some(g => g.type === "noun");
            const hasModifier = group.some(g => g.type === "adjective" || g.type === "numeral");

            if (group.length > 1 && hasNoun && hasModifier) {
                const firstCase = getCaseType(group[0].val);
                const sorted = group.slice().sort(function (a, b) {
                    const byType = (order[a.type] || 99) - (order[b.type] || 99);
                    if (byType !== 0) return byType;
                    return a.originalIndex - b.originalIndex;
                });

                const words = sorted.map(function (item, index) {
                    let word = item.val;
                    if (index === 0) {
                        word = applyCaseLike(group[0].val, word);
                    } else if (firstCase === "upper") {
                        word = word.toLocaleUpperCase("pl");
                    } else if (firstCase === "title") {
                        word = word.toLocaleLowerCase("pl");
                    }
                    return word;
                });

                out.push(words.join(" "));
                i = j - 1;
                continue;
            }

            out.push(token);
        }

        return protectedText.restore(out.join(""));
    }

    function maybeReorderSlovian(text) {
        // Własne porządkowanie działa zawsze dla sąsiadujących grup:
        // rzeczownik + przymiotnik -> przymiotnik + rzeczownik,
        // rzeczownik + liczebnik -> liczebnik + rzeczownik,
        // rzeczownik + przymiotnik + liczebnik -> liczebnik + przymiotnik + rzeczownik.
        let result = reorderSlovianAdjacentGroups(text);

        if (USE_REORDER_SMART && typeof reorderSmart === "function") {
            try {
                result = reorderSmart(result);
            } catch (e) {}
        }

        return fixOutputSpacing(result);
    }

    function fixOutputSpacing(text) {
        return String(text ?? "")
            .replace(/\s+([,.;:!?%])/g, "$1")
            .replace(/([([{„«])\s+/g, "$1")
            .replace(/\s+([)\]}”»])/g, "$1")
            .replace(/\s*—\s*/g, " — ")
            .replace(/([\p{L}\p{M}0-9ьъěęǫšžčćńłóśźż])\s*-\s*([\p{L}\p{M}0-9ьъěęǫšžčćńłóśźż])/gu, "$1 - $2")
            .replace(/\s+/g, " ")
            .trim();
    }

    function translateByIndexedData(text, direction) {
        const original = String(text ?? "");
        if (!original.trim()) return "";

        const sentenceHit = lookupSentence(original, direction);
        if (sentenceHit) return sentenceHit;

        const protectedText = protectSpecialText(original);
        const tokens = protectedText.text.match(TOKEN_RE) || [protectedText.text];
        const out = [];
        let changed = false;

        for (let i = 0; i < tokens.length; i++) {
            const token = tokens[i];

            if (!isWord(token)) {
                out.push(token);
                continue;
            }

            const best = findBestPhrase(tokens, i, direction);

            if (best && best.target) {
                out.push(applyCaseLike(best.source, best.target));
                i = best.endIndex - 1;
                changed = true;
                continue;
            }

            out.push(token);
        }

        const restored = protectedText.restore(out.join(""));
        return changed ? fixOutputSpacing(restored) : original;
    }

    function modelFallback(text, direction) {
        if (!slovoMLBridgeModel) return null;

        const wc = wordCount(text);
        if (wc <= 1 && !TRUST_MODEL_SINGLE_WORD && !USE_GUESS_FALLBACK) return null;

        try {
            if (direction === "slo2pl") {
                const result = slovoMLBridgeModel.translateSlovianToPolish(text, {
                    fallback: "copy"
                });
                return sameNormalized(result, text) ? null : result;
            }

            const result = slovoMLBridgeModel.translatePolishToSlovian(text, {
                fallback: USE_GUESS_FALLBACK ? "guess" : "copy"
            });

            return sameNormalized(result, text) ? null : result;
        } catch (e) {
            console.warn("Błąd fallbacku ML:", e);
            return null;
        }
    }

    function translateDirection(text, direction) {
        const original = String(text ?? "");
        if (!original.trim()) return "";

        const indexed = translateByIndexedData(original, direction);
        if (!sameNormalized(indexed, original)) {
            return direction === "pl2slo"
                ? maybeReorderSlovian(fixOutputSpacing(indexed))
                : fixOutputSpacing(indexed);
        }

        const model = modelFallback(original, direction);
        if (model) {
            return direction === "pl2slo"
                ? maybeReorderSlovian(fixOutputSpacing(alignTerminalPunctuation(model, original)))
                : fixOutputSpacing(alignTerminalPunctuation(model, original));
        }

        return original;
    }

    function translatePlToSloML(text) {
        return translateDirection(text, "pl2slo");
    }

    function translateSloToPlML(text) {
        return translateDirection(text, "slo2pl");
    }

    const oldLoadDictionaries = typeof loadDictionaries === "function" ? loadDictionaries : null;

    if (oldLoadDictionaries) {
        const patchedLoadDictionaries = async function () {
            await oldLoadDictionaries();
            await loadSlovoMLBridge();
        };

        try {
            loadDictionaries = patchedLoadDictionaries;
        } catch (e) {}

        window.loadDictionaries = patchedLoadDictionaries;
    } else {
        loadSlovoMLBridge();
    }

    const oldTranslate = typeof translate === "function" ? translate : null;

    if (oldTranslate) {
        const patchedTranslate = async function () {
            const input = document.getElementById("userInput");
            const out = document.getElementById("resultOutput");
            const srcSelect = document.getElementById("srcLang");
            const tgtSelect = document.getElementById("tgtLang");

            if (!input || !out || !srcSelect || !tgtSelect) return;

            const text = input.value;
            const src = srcSelect.value;
            const tgt = tgtSelect.value;

            if (!text.trim()) {
                out.innerText = "";
                hideCorrectionSuggestion();
                return;
            }

            await loadSlovoMLBridge();

            try {
                let finalResult = "";
                let workingText = text;

                if (src !== "slo" && typeof prepareInputForTranslation === "function") {
                    // Korekta nie może blokować tłumaczenia. Gdy Google albo sieć się zawiesi,
                    // po 1000 ms tłumaczymy tekst oryginalny.
                    const prepared = await Promise.race([
                        prepareInputForTranslation(text, src, tgt),
                        new Promise(resolve => setTimeout(() => resolve({ text: text }), 1000))
                    ]);
                    workingText = prepared.text || text;
                } else if (src === "slo") {
                    hideCorrectionSuggestion();
                }

                if (src === "slo" && tgt === "pl") {
                    finalResult = translateSloToPlML(text);

                } else if (src === "pl" && tgt === "slo") {
                    finalResult = translatePlToSloML(workingText);

                } else if (src === "slo") {
                    const bridge = translateSloToPlML(text);
                    finalResult = typeof google === "function"
                        ? await google(bridge, "pl", tgt)
                        : bridge;

                } else if (tgt === "slo") {
                    const bridge = typeof google === "function"
                        ? await google(workingText, src, "pl")
                        : workingText;

                    finalResult = translatePlToSloML(bridge);

                } else {
                    finalResult = typeof google === "function"
                        ? await google(workingText, src, tgt)
                        : workingText;
                }

                out.innerText = finalResult || "";

            } catch (e) {
                console.error("Błąd ML bridge, powrót do starego tłumacza:", e);
                return oldTranslate();
            }
        };

        try {
            translate = patchedTranslate;
        } catch (e) {}

        window.translate = patchedTranslate;
    }

    window.prepareInputForTranslation = prepareInputForTranslation;
    window.hideCorrectionSuggestion = hideCorrectionSuggestion;
    window.loadSlovoMLBridge = loadSlovoMLBridge;
    window.translatePlToSloML = translatePlToSloML;
    window.translateSloToPlML = translateSloToPlML;
    window.__slovoBridge = BRIDGE;
})();
