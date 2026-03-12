# Dodaj po osnova = load_json("osnova.json")
selflearning = load_json("selflearning.json")
all_data = osnova + selflearning
pl_to_sl, sl_to_pl = build_dictionaries(all_data)

# Nowa funkcja (po translate)
def save_pair(polish, slovian):
    entry = {"polish": polish.strip(), "slovian": slovian.strip()}
    data = load_json("selflearning.json") + [entry]
    with open("selflearning.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    st.rerun()

# Po st.success(result) dodaj:
st.subheader("🧠 Naucz tłumacza")
col1, col2 = st.columns(2)
new_pl = col1.text_input("Słowo polskie")
new_sl = col2.text_input("Tłumaczenie słowiańskie")
if st.button("Zapisz do selflearning.json"):
    if new_pl and new_sl:
        save_pair(new_pl, new_sl)
