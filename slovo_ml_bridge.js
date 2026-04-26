/* slovo_ml_bridge.js
 * Bezpieczna warstwa ML do starego script.js.
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

    /*
     * WAŻNE:
     * false = tryb bezpieczny: nie zgaduje pojedynczych nieznanych słów.
     * true  = tryb eksperymentalny: model może zgadywać słowa spoza bazy.
     *
     * Przy twoim tłumaczu polecam zostawić false,
     * bo inaczej model może gubić ь, ъ, ę, ǫ itd.
     */
    const USE_GUESS_FALLBACK = false;

    /*
     * false = pojedyncze słowa bierze tylko z osnova/vuzor.
     * true  = pojedyncze słowa może brać też z modelu ML.
     *
     * Zostaw false, jeśli chcesz, aby końcówki były zgodne z plikami.
     */
    const TRUST_MODEL_SINGLE_WORD = false;

    const MAX_PHRASE_WORDS = 8;
    const TOKEN_RE = /([\p{L}\p{M}0-9'’.-]+|\s+|[^\s\p{L}\p{M}0-9'’.-]+)/gu;
    const WORD_RE = /^[\p{L}\p{M}0-9'’.-]+$/u;
    const URL_RE = /(https?:\/\/[^\s]+|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/g;

    function normalizeKey(text) {
        return String(text ?? "")
            .normalize("NFC")
            .replace(/\s+/g, " ")
            .trim()
            .toLocaleLowerCase("pl");
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

    function getLocalDict(direction) {
        try {
            if (direction === "slo2pl" && typeof sloToPl !== "undefined") return sloToPl || {};
            if (direction === "pl2slo" && typeof plToSlo !== "undefined") return plToSlo || {};
        } catch (e) {}
        return {};
    }

    function localLookup(text, direction) {
        const dict = getLocalDict(direction);
        const key = normalizeKey(text);

        if (!key) return null;

        if (Object.prototype.hasOwnProperty.call(dict, key)) {
            return dict[key];
        }

        return null;
    }

    function modelLookup(text, direction, allowSingleWord) {
        if (!slovoMLBridgeModel) return null;

        const wc = wordCount(text);
        if (wc <= 1 && !allowSingleWord) return null;

        try {
            const modelDirection = direction === "slo2pl" ? "slo2pl" : "pl2slo";
            const exact = slovoMLBridgeModel.lookup(text, modelDirection);
            if (exact && exact.target) return exact.target;
        } catch (e) {}

        return null;
    }

    function findBestLocalPhrase(tokens, startIndex, direction) {
        const dict = getLocalDict(direction);

        let phrase = "";
        let usedWords = 0;
        let best = null;

        for (let i = startIndex; i < tokens.length; i++) {
            const token = tokens[i];

            if (isWord(token)) {
                phrase += token;
                usedWords++;

                const value = dict[normalizeKey(phrase)];
                if (value) {
                    best = {
                        source: phrase,
                        target: value,
                        endIndex: i + 1,
                        words: usedWords
                    };
                }

                if (usedWords >= MAX_PHRASE_WORDS) break;
                continue;
            }

            if (isSpace(token)) {
                phrase += " ";
                continue;
            }

            break;
        }

        return best;
    }

    function translateByLocalDictionary(text, direction) {
        const protectedText = protectSpecialText(text);
        const tokens = protectedText.text.match(TOKEN_RE) || [protectedText.text];
        const out = [];

        let changed = false;

        for (let i = 0; i < tokens.length; i++) {
            const token = tokens[i];

            if (!isWord(token)) {
                out.push(token);
                continue;
            }

            const best = findBestLocalPhrase(tokens, i, direction);

            if (best && best.target) {
                out.push(applyCaseLike(best.source, best.target));
                i = best.endIndex - 1;
                changed = true;
                continue;
            }

            out.push(token);
        }

        const result = protectedText.restore(out.join(""));
        return {
            text: result,
            changed
        };
    }

    function maybeReorderSlovian(text) {
        if (typeof reorderSmart === "function") {
            try {
                return reorderSmart(text);
            } catch (e) {
                return text;
            }
        }
        return text;
    }

    function fixOutputSpacing(text) {
        return String(text ?? "")
            .replace(/\s+([,.;:!?])/g, "$1")
            .replace(/([([{])\s+/g, "$1")
            .replace(/\s+([)\]}])/g, "$1")
            .replace(/\s+/g, " ")
            .trim();
    }

    async function loadSlovoMLBridge() {
        if (slovoMLBridgeModel) return true;
        if (slovoMLBridgeLoading) return slovoMLBridgeLoading;

        slovoMLBridgeLoading = (async function () {
            const status = document.getElementById("dbStatus");

            try {
                if (typeof SlovoTranslator === "undefined") {
                    console.warn("Brak SlovoTranslator. Sprawdź kolejność skryptów w index.html.");
                    if (status) status.innerText = "Dictionary Engine Ready.";
                    return false;
                }

                slovoMLBridgeModel = await SlovoTranslator.loadFromUrl("model/slovo-model.json");

                console.log("Slovo ML model loaded.");
                if (status) status.innerText = "ML Engine Ready.";
                return true;

            } catch (e) {
                console.warn("Nie udało się załadować modelu ML:", e);
                slovoMLBridgeModel = null;

                if (status) status.innerText = "Dictionary Engine Ready.";
                return false;
            }
        })();

        return slovoMLBridgeLoading;
    }

    function translatePlToSloML(text) {
        const original = String(text ?? "");

        if (!original.trim()) return "";

        /*
         * 1. Najpierw dokładny wpis z osnova/vuzor.
         * To jest najważniejsze, bo tu są poprawne końcówki: ь, ъ, ǫ, ę itd.
         */
        const localExact = localLookup(original, "pl2slo");
        if (localExact) {
            return applyCaseLike(original, localExact);
        }

        /*
         * 2. Dla całych zdań/fraz można zaufać modelowi,
         * ale nie dla pojedynczych słów, jeśli TRUST_MODEL_SINGLE_WORD = false.
         */
        const allowSingleWordModel = TRUST_MODEL_SINGLE_WORD;
        const modelExact = modelLookup(original, "pl2slo", allowSingleWordModel);
        if (modelExact) {
            return applyCaseLike(original, modelExact);
        }

        /*
         * 3. Potem frazy i słowa z osnova/vuzor wewnątrz tekstu.
         */
        const localPhrase = translateByLocalDictionary(original, "pl2slo");
        if (localPhrase.changed) {
            return maybeReorderSlovian(fixOutputSpacing(localPhrase.text));
        }

        /*
         * 4. Dopiero potem model dla dłuższego tekstu.
         * Przy fallback: "copy" nie zgaduje nieznanych słów.
         */
        if (slovoMLBridgeModel) {
            const wc = wordCount(original);

            if (wc > 1 || USE_GUESS_FALLBACK) {
                try {
                    const result = slovoMLBridgeModel.translatePolishToSlovian(original, {
                        fallback: USE_GUESS_FALLBACK ? "guess" : "copy"
                    });

                    if (!sameNormalized(result, original) || USE_GUESS_FALLBACK) {
                        return maybeReorderSlovian(fixOutputSpacing(result));
                    }
                } catch (e) {
                    console.warn("Błąd tłumaczenia PL→SLO przez model:", e);
                }
            }
        }

        /*
         * 5. Jeżeli słowa nie ma w bazie, nie zgaduj.
         * To zapobiega błędom typu brak końcowego ь.
         */
        return original;
    }

    function translateSloToPlML(text) {
        const original = String(text ?? "");

        if (!original.trim()) return "";

        /*
         * 1. Najpierw dokładny wpis z odwróconego osnova/vuzor.
         */
        const localExact = localLookup(original, "slo2pl");
        if (localExact) {
            return applyCaseLike(original, localExact);
        }

        /*
         * 2. Model tylko dla zdań/fraz albo gdy jawnie pozwolisz na pojedyncze słowa.
         */
        const allowSingleWordModel = TRUST_MODEL_SINGLE_WORD;
        const modelExact = modelLookup(original, "slo2pl", allowSingleWordModel);
        if (modelExact) {
            return applyCaseLike(original, modelExact);
        }

        /*
         * 3. Frazy i słowa z lokalnego słownika.
         */
        const localPhrase = translateByLocalDictionary(original, "slo2pl");
        if (localPhrase.changed) {
            return fixOutputSpacing(localPhrase.text);
        }

        /*
         * 4. Model dla dłuższego tekstu, bez zgadywania nieznanych słów.
         */
        if (slovoMLBridgeModel) {
            const wc = wordCount(original);

            if (wc > 1 || USE_GUESS_FALLBACK) {
                try {
                    const result = slovoMLBridgeModel.translateSlovianToPolish(original, {
                        fallback: "copy"
                    });

                    if (!sameNormalized(result, original)) {
                        return fixOutputSpacing(result);
                    }
                } catch (e) {
                    console.warn("Błąd tłumaczenia SLO→PL przez model:", e);
                }
            }
        }

        return original;
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
                return;
            }

            if (!slovoMLBridgeModel) {
                await loadSlovoMLBridge();
            }

            try {
                let finalResult = "";

                if (src === "slo" && tgt === "pl") {
                    finalResult = translateSloToPlML(text);

                } else if (src === "pl" && tgt === "slo") {
                    finalResult = translatePlToSloML(text);

                } else if (src === "slo") {
                    const bridge = translateSloToPlML(text);
                    finalResult = typeof google === "function"
                        ? await google(bridge, "pl", tgt)
                        : bridge;

                } else if (tgt === "slo") {
                    const bridge = typeof google === "function"
                        ? await google(text, src, "pl")
                        : text;

                    finalResult = translatePlToSloML(bridge);

                } else {
                    finalResult = typeof google === "function"
                        ? await google(text, src, tgt)
                        : text;
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

    window.loadSlovoMLBridge = loadSlovoMLBridge;
    window.translatePlToSloML = translatePlToSloML;
    window.translateSloToPlML = translateSloToPlML;
})();
