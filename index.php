<?php
// 1. ŁADOWANIE BAZ (JSON)
$osnova = json_decode(file_get_contents('osnova.json'), true) ?: [];
$vuzor = json_decode(file_get_contents('vuzor.json'), true) ?: [];
$memory = json_decode(file_get_contents('memory.json'), true) ?: [];

$translatedText = "";
$srcText = "";

// 2. LOGIKA TŁUMACZENIA W PHP
function translateWord($word, $direction, $osnova, $vuzor, $memory) {
    $lowWord = mb_strtolower($word, 'UTF-8');
    
    // Sprawdź pamięć
    if (isset($memory[$lowWord])) return $memory[$lowWord];

    // Szukaj w osnova
    foreach ($osnova as $item) {
        $src = ($direction === 'pl_sl') ? $item['polish'] : $item['slovian'];
        $trg = ($direction === 'pl_sl') ? $item['slovian'] : $item['polish'];

        if (mb_strtolower($src, 'UTF-8') === $lowWord) {
            $res = $trg;
            if ($direction === 'pl_sl' && !empty($item['vuzor']) && isset($vuzor[$item['vuzor']])) {
                $suffix = $vuzor[$item['vuzor']]['nom'] ?? "";
                $res .= $suffix;
            }
            return $res;
        }
    }
    return $word;
}

// 3. OBSŁUGA FORMULARZA
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['srcText'])) {
        $srcText = $_POST['srcText'];
        $direction = $_POST['dir'] ?? 'pl_sl';
        
        // Rozbijanie na tokeny (słowa i znaki)
        $tokens = preg_split('/(\W+)/u', $srcText, -1, PREG_SPLIT_DELIM_CAPTURE);
        
        foreach ($tokens as $t) {
            if (preg_match('/^\W+$/u', $t)) {
                $translatedText .= $t;
            } else {
                $trans = translateWord($t, $direction, $osnova, $vuzor, $memory);
                // Zachowanie wielkości liter
                if (ctype_upper(mb_substr($t, 0, 1, 'UTF-8'))) {
                    $translatedText .= mb_convert_case($trans, MB_CASE_TITLE, "UTF-8");
                } else {
                    $translatedText .= $trans;
                }
            }
        }
    }
}
?>

<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>Tłumacz PHP</title>
    <style>
        body { font-family: sans-serif; background: #f0f2f5; padding: 20px; text-align: center; }
        .box { background: white; padding: 20px; border-radius: 10px; max-width: 800px; margin: auto; }
        textarea { width: 100%; height: 150px; margin: 10px 0; border-radius: 5px; border: 1px solid #ccc; padding: 10px; }
        button { background: #0055ff; color: white; border: none; padding: 10px 20px; cursor: pointer; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="box">
        <h1>🌐 PHP Perkladačь</h1>
        <form method="POST">
            <label><input type="radio" name="dir" value="pl_sl" checked> PL ➔ SL</label>
            <label><input type="radio" name="dir" value="sl_pl"> SL ➔ PL</label>
            
            <textarea name="srcText" placeholder="Wpisz tekst..."><?php echo htmlspecialchars($srcText); ?></textarea>
            <button type="submit">🚀 TŁUMACZ</button>
            <textarea readonly placeholder="Wynik..."><?php echo htmlspecialchars($translatedText); ?></textarea>
        </form>
    </div>
</body>
</html>
