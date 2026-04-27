/* slovo_runtime_fixes.js
 * Runtime fixes for Slovo Translator.
 * 1) Tłumaczenie ma odpalać się także po wklejeniu tekstu z klawiatury, schowka i przycisku.
 * 2) Wyłącza agresywną sugestię korekty typu: grodach -> grozach.
 * 3) Dodatkowo koryguje polski miejscownik liczby mnogiej po w/we/na/po/przy
 *    dla typowych form: -ach/-ech -> slovian -ah/-ěh/-ih.
 */
(function () {
    "use strict";

    const INPUT_ID = "userInput";
    const OUTPUT_ID = "resultOutput";
    const SRC_ID = "srcLang";
    const TGT_ID = "tgtLang";
    const SUGGESTION_ID = "suggestionBox";

    const PL_LOC_PREPOSITIONS = new Set(["w", "we", "na", "po", "przy", "o"]);

    const PL_NOUN_OVERRIDES = new Map([
        ["grodach", "gorděh"],
        ["miastach", "gorděh"],
        ["ogrodach", "obgorděh"],
        ["wzorach", "vuzorěh"],
        ["wzorcach", "vuzorěh"],
        ["standardach", "vuzorěh"],
        ["prawopisach", "pravopisěh"],
        ["uśmiechach", "usměhěh"],
        ["usmiechach", "usměhěh"],
        ["dobrach", "dobrěh"],
        ["radościach", "radostih"],
        ["radosciach", "radostih"],
        ["mądrościach", "mǫdrostih"],
        ["madrościach", "mǫdrostih"],
        ["madrosciach", "mǫdrostih"],
        ["szczęściach", "sučęstih"],
        ["szczesciach", "sučęstih"],
        ["okolicach", "okolicah"],
        ["obietnicach", "obětьnicah"],
        ["bożnicach", "božьnicah"],
        ["boznicach", "božьnicah"],
        ["usługach", "uslugah"],
        ["uslugach", "uslugah"]
    ]);

    const PREP_PL_TO_SLO = new Map([
        ["w", "vu"],
        ["we", "vu"],
        ["na", "na"],
        ["po", "po"],
        ["przy", "pri"],
        ["o", "ob"]
    ]);

    function $(id) {
        return document.getElementById(id);
    }

    function normalizeKey(value) {
        return String(value || "")
            .normalize("NFC")
            .replace(/[’]/g, "'")
            .replace(/\s+/g, " ")
            .trim()
            .toLocaleLowerCase("pl");
    }

    function applyCaseLike(source, target) {
        const src = String(source || "");
        const out = String(target || "");
        if (!out) return out;
        if (src.length > 1 && src === src.toLocaleUpperCase("pl")) return out.toLocaleUpperCase("pl");
        if (src[0] && src[0] === src[0].toLocaleUpperCase("pl") && src[0] !== src[0].toLocaleLowerCase("pl")) {
            return out.charAt(0).toLocaleUpperCase("pl") + out.slice(1);
        }
        return out;
    }

    function hideBadSuggestionBox() {
        const box = $(SUGGESTION_ID);
        if (!box) return;
        const text = normalizeKey(box.textContent || "");
        if (!text) return;

        // Google/Chrome korekta potrafi tu niszczyć formy historyczne i fleksyjne.
        // Dla tłumacza ma pierwszeństwo silnik językowy, nie korekta pisowni.
        if (text.includes("grodach") || text.includes("grozach") || text.includes("sugestia poprawy")) {
            box.style.display = "none";
            box.innerHTML = "";
        }
    }

    function replaceLocativePluralPhrases(text) {
        let result = String(text || "");

        result = result.replace(/\b(w|we|na|po|przy|o)\s+([\p{L}\p{M}'’.-]+(?:ach|ech))\b/giu, function (match, prep, noun) {
            const nKey = normalizeKey(noun);
            const replacementNoun = PL_NOUN_OVERRIDES.get(nKey);
            if (!replacementNoun) return match;

            const newPrep = PREP_PL_TO_SLO.get(normalizeKey(prep)) || prep;
            return applyCaseLike(prep, newPrep) + " " + applyCaseLike(noun, replacementNoun);
        });

        return result;
    }

    function getOutputText() {
        const output = $(OUTPUT_ID);
        if (!output) return "";
        return output.value !== undefined ? output.value : output.textContent;
    }

    function setOutputText(text) {
        const output = $(OUTPUT_ID);
        if (!output) return;
        if (output.value !== undefined) output.value = text;
        else output.textContent = text;
    }

    function runNativeTranslation() {
        const candidates = [
            window.translateText,
            window.translate,
            window.performTranslation,
            window.updateTranslation,
            window.doTranslate,
            window.processTranslation,
            window.handleTranslation
        ].filter(fn => typeof fn === "function");

        for (const fn of candidates) {
            try {
                fn.call(window);
                return true;
            } catch (e) {
                // próbujemy następną nazwę, jeśli dana funkcja wymaga argumentów
            }
        }

        const input = $(INPUT_ID);
        if (input) {
            input.dispatchEvent(new Event("input", { bubbles: true }));
            input.dispatchEvent(new Event("change", { bubbles: true }));
            return true;
        }

        return false;
    }

    function scheduleTranslateAndPatch() {
        window.setTimeout(function () {
            hideBadSuggestionBox();
            runNativeTranslation();
            window.setTimeout(function () {
                hideBadSuggestionBox();
                const src = $(SRC_ID) ? $(SRC_ID).value : "";
                const tgt = $(TGT_ID) ? $(TGT_ID).value : "";
                if (src === "pl" && tgt === "slo") {
                    const patched = replaceLocativePluralPhrases(getOutputText());
                    if (patched && patched !== getOutputText()) setOutputText(patched);
                }
            }, 80);
        }, 0);
    }

    async function readClipboardText() {
        if (navigator.clipboard && typeof navigator.clipboard.readText === "function") {
            try { return await navigator.clipboard.readText(); } catch (e) {}
        }
        return "";
    }

    function insertIntoTextarea(textarea, text) {
        const value = textarea.value || "";
        const start = typeof textarea.selectionStart === "number" ? textarea.selectionStart : value.length;
        const end = typeof textarea.selectionEnd === "number" ? textarea.selectionEnd : value.length;
        textarea.value = value.slice(0, start) + text + value.slice(end);
        const pos = start + String(text).length;
        try { textarea.setSelectionRange(pos, pos); } catch (e) {}
        textarea.focus();
        textarea.dispatchEvent(new Event("input", { bubbles: true }));
        textarea.dispatchEvent(new Event("change", { bubbles: true }));
    }

    window.pasteText = async function () {
        const input = $(INPUT_ID);
        if (!input) return;
        const text = await readClipboardText();
        if (text) insertIntoTextarea(input, text);
        scheduleTranslateAndPatch();
    };

    document.addEventListener("paste", function (event) {
        const input = $(INPUT_ID);
        if (!input || event.target !== input) return;
        window.setTimeout(scheduleTranslateAndPatch, 0);
    }, true);

    document.addEventListener("input", function (event) {
        if (event.target && event.target.id === INPUT_ID) scheduleTranslateAndPatch();
    }, true);

    document.addEventListener("DOMContentLoaded", function () {
        hideBadSuggestionBox();
        const input = $(INPUT_ID);
        if (input) {
            input.addEventListener("paste", function () {
                window.setTimeout(scheduleTranslateAndPatch, 0);
            });
        }
        scheduleTranslateAndPatch();
    });
})();
