/* slovo_ml_bridge.js
 * Warstwa ML do starego script.js.
 * Ładuj w index.html po slovo_model.js i po script.js:
 * <script src="slovo_model.js"></script>
 * <script src="script.js"></script>
 * <script src="slovo_ml_bridge.js"></script>
 */
(function () {
    "use strict";

    let slovoMLBridgeModel = null;
    let slovoMLBridgeLoading = null;

    async function loadSlovoMLBridge() {
        if (slovoMLBridgeModel) return true;
        if (slovoMLBridgeLoading) return slovoMLBridgeLoading;

        slovoMLBridgeLoading = (async function () {
            const status = document.getElementById("dbStatus");
            try {
                if (typeof SlovoTranslator === "undefined") {
                    console.warn("Brak SlovoTranslator. Sprawdź, czy slovo_model.js jest załadowany przed slovo_ml_bridge.js.");
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
        if (!slovoMLBridgeModel) return null;

        const exact = slovoMLBridgeModel.lookup(text, "pl2slo");
        if (exact && exact.target) return exact.target;

        const result = slovoMLBridgeModel.translatePolishToSlovian(text, {
            fallback: "guess"
        });

        if (typeof reorderSmart === "function") {
            return reorderSmart(result);
        }
        return result;
    }

    function translateSloToPlML(text) {
        if (!slovoMLBridgeModel) return null;
        return slovoMLBridgeModel.translateSlovianToPolish(text, {
            fallback: "copy"
        });
    }

    const oldLoadDictionaries = typeof loadDictionaries === "function" ? loadDictionaries : null;
    if (oldLoadDictionaries) {
        loadDictionaries = async function () {
            await oldLoadDictionaries();
            await loadSlovoMLBridge();
        };
    }

    const oldTranslate = typeof translate === "function" ? translate : null;
    if (oldTranslate) {
        translate = async function () {
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
                const loaded = await loadSlovoMLBridge();
                if (!loaded) return oldTranslate();
            }

            try {
                let finalResult = "";

                if (src === "slo" && tgt === "pl") {
                    finalResult = translateSloToPlML(text);

                } else if (src === "pl" && tgt === "slo") {
                    finalResult = translatePlToSloML(text);

                } else if (src === "slo") {
                    const bridge = translateSloToPlML(text);
                    finalResult = await google(bridge, "pl", tgt);

                } else if (tgt === "slo") {
                    const bridge = await google(text, src, "pl");
                    finalResult = translatePlToSloML(bridge);

                } else {
                    finalResult = await google(text, src, tgt);
                }

                out.innerText = finalResult || "";
            } catch (e) {
                console.error(e);
                return oldTranslate();
            }
        };
    }

    window.loadSlovoMLBridge = loadSlovoMLBridge;
    window.translatePlToSloML = translatePlToSloML;
    window.translateSloToPlML = translateSloToPlML;
})();
