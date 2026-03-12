<?php
// --- LOGIKA BACKENDU (Zapisywanie słów) ---
$statusMsg = "";
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'add_word') {
    if ($_POST['pass'] === 'Rozeta*8') {
        $pl = trim($_POST['newPl']);
        $sl = trim($_POST['newSl']);
        
        if (!empty($pl) && !empty($sl)) {
            $memFile = 'memory.json';
            $currentMem = file_exists($memFile) ? json_decode(file_get_contents($memFile), true) : [];
            
            // Dodajemy słowo (dwukierunkowo)
            $currentMem[mb_strtolower($pl)] = $sl;
            
            if (file_put_contents($memFile, json_encode($currentMem, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT))) {
                $statusMsg = "<div class='status success'>Dodano pomyślnie do bazy!</div>";
            } else {
                $statusMsg = "<div class='status error'>Błąd zapisu pliku. Sprawdź uprawnienia.</div>";
            }
        }
    } else {
        $statusMsg = "<div class='status error'>Błędne hasło admina!</div>";
    }
}
?>

<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Perkladačь slověnьskogo ęzyka (PHP Edition)</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #0055ff; --bg: #f3f6f9; --text: #1a1a1a; --border: #d1d9e0; }
        body { font-family: 'Inter', sans-serif; background-color: var(--bg); color: var(--text); margin: 0; display: flex; flex-direction: column; align-items: center; padding: 20px; }
        .container { max-width: 1100px; width: 100%; background: white; padding: 30px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); }
        h1 { font-weight: 600; text-align: center; margin-bottom: 30px; }
        .translator-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .label-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; font-weight: 600; }
        textarea { width: 100%; height: 250px; padding: 15px; border: 1px solid var(--border); border-radius: 12px; font-size: 16px; resize: none; box-sizing: border-box; outline: none; }
        textarea:focus { border-color: var(--primary); }
        .btn-small { background: #eee; border: none; padding: 5px 12px; border-radius: 6px; cursor: pointer; font-size: 13px; }
        .main-btn { grid-column: span 2; padding: 15px; background: var(--primary); color: white; border: none; border-radius: 12px; font-size: 18px; font-weight: 600; cursor: pointer; margin-top: 10px; }
        .admin-panel { margin-top: 50px; padding-top: 30px; border-top: 1px solid #eee; width: 100%; }
        .admin-grid { display: grid; grid-template-columns: 2fr 2fr 1fr; gap: 10px; margin-top: 10px; }
        .input-admin { padding: 10px; border: 1px solid var(--border); border-radius: 8px; }
        .status { padding: 10px; border-radius: 8px; margin-top: 10px; text-align: center; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>

<div class="container">
    <h1>🌐 Perkladačь slověnьskogo ęzyka</h1>

    <?php echo $statusMsg; ?>

    <div style="margin-bottom: 20px; text-align: center;">
        <label><input type="radio" name="dir" value="pl_sl" checked id="dir_pl_sl"> PL ➔ SL</label>
        <label style="margin-left: 20px;"><input type="radio" name="dir" value="sl_pl" id="dir_sl_pl"> SL ➔ PL</label>
    </div>

    <div class="translator-grid">
        <div class="input-group">
            <div class="label-bar">
                <span>Tekst źródłowy</span>
                <button class="btn-small" id="btnPaste">📋 Wklej</button>
            </div>
            <textarea id="srcText" placeholder="Wpisz tekst..."></textarea>
        </div>

        <div class="input-group">
            <div class="label-bar">
                <span>Wynik</span>
                <button class="btn-small" id="btnCopy">✂️ Kopiuj</button>
            </div>
            <textarea id="resText" readonly></textarea>
        </div>

        <button class="main-btn" id="runTranslate">🚀 TŁUMACZ</button>
    </div>

    <div class="admin-panel">
        <h3>🛠️ Zarządzaj bazą (Trwały zapis)</h3>
        <form method="POST">
            <input type="hidden" name="action" value="add_word">
            <input type="password" name="pass" class="input-admin" placeholder="Hasło admina" required>
            <div class="admin-grid">
                <input type="text" name="newPl" class="input-admin" placeholder="Słowo PL" required>
                <input type="text" name="newSl" class="input-admin" placeholder="Słowo SL" required>
                <button type="submit" class="main-btn" style="margin:0;">✅ Dodaj na stałe</button>
            </div>
        </form>
    </div>
</div>

<script>
// Logika JS pozostaje do błyskawicznego tłumaczenia (bez przeładowania strony)
let osnova = [];
let vuzor = {};
let memory = {};

async function loadData() {
    try {
        const cacheBuster = '?v=' + Date.now();
        const [o, v, m] = await Promise.all([
            fetch('osnova.json' + cacheBuster).then(r => r.json()),
            fetch('vuzor.json' + cacheBuster).then(r => r.json()),
            fetch('memory.json' + cacheBuster).then(r => r.json()).catch(() => ({}))
        ]);
        osnova = o; vuzor = v; memory = m;
        console.log("Bazy załadowane.");
    } catch (e) { console.error("Błąd ładowania danych:", e); }
}

function processWord(word, direction) {
    let low = word.toLowerCase();
    if (memory[low]) return memory[low];

    for (let item of osnova) {
        let src = direction === 'pl_sl' ? item.polish : item.slovian;
        let trg = direction === 'pl_sl' ? item.slovian : item.polish;

        if (src && src.toLowerCase() === low) {
            let res = trg;
            if (direction === 'pl_sl' && item.vuzor && vuzor[item.vuzor]) {
                let suffix = vuzor[item.vuzor].nom || "";
                res = res + suffix;
            }
            return res;
        }
    }
    return word;
}

document.getElementById('runTranslate').onclick = function() {
    const text = document.getElementById('srcText').value;
    const dir = document.querySelector('input[name="dir"]:checked').value;
    const tokens = text.split(/(\W+)/);
    const translated = tokens.map(t => {
        if (/^\W+$/.test(t)) return t; 
        let result = processWord(t, dir);
        if (t === t.toUpperCase()) return result.toUpperCase();
        if (t[0] === t[0].toUpperCase()) return result.charAt(0).toUpperCase() + result.slice(1);
        return result;
    });
    document.getElementById('resText').value = translated.join("");
};

// Kopiowanie i Wklejanie
document.getElementById('btnCopy').onclick = () => {
    navigator.clipboard.writeText(document.getElementById('resText').value);
    alert("Skopiowano do schowka!");
};

document.getElementById('btnPaste').onclick = async () => {
    const text = await navigator.clipboard.readText();
    document.getElementById('srcText').value = text;
};

loadData();
</script>

</body>
</html>
