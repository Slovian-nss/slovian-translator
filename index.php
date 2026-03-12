<?php
// Pozwól na zapytania z Twojej strony na GitHubie
header("Access-Control-Allow-Origin: *");

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $srcText = $_POST['text'] ?? '';
    $direction = $_POST['dir'] ?? 'pl_sl';

    // Wczytaj bazy danych
    $osnova = json_decode(file_get_contents('osnova.json'), true) ?: [];
    $vuzor = json_decode(file_get_contents('vuzor.json'), true) ?: [];
    $memory = json_decode(file_get_contents('memory.json'), true) ?: [];

    // Funkcja tłumacząca (taka sama jak wcześniej)
    function translateWord($word, $direction, $osnova, $vuzor, $memory) {
        $low = mb_strtolower($word, 'UTF-8');
        if (isset($memory[$low])) return $memory[$low];

        foreach ($osnova as $item) {
            $src = ($direction === 'pl_sl') ? $item['polish'] : $item['slovian'];
            $trg = ($direction === 'pl_sl') ? $item['slovian'] : $item['polish'];

            if (mb_strtolower($src, 'UTF-8') === $low) {
                $res = $trg;
                if ($direction === 'pl_sl' && !empty($item['vuzor'])) {
                    $suffix = $vuzor[$item['vuzor']]['nom'] ?? "";
                    $res .= $suffix;
                }
                return $res;
            }
        }
        return $word;
    }

    // Przetwarzanie całego zdania
    $tokens = preg_split('/(\W+)/u', $srcText, -1, PREG_SPLIT_DELIM_CAPTURE);
    $output = "";

    foreach ($tokens as $t) {
        if (preg_match('/^\W+$/u', $t)) {
            $output .= $t;
        } else {
            $trans = translateWord($t, $direction, $osnova, $vuzor, $memory);
            // Wielka litera
            if (mb_check_encoding($t, 'UTF-8') && ctype_upper(mb_substr($t, 0, 1, 'UTF-8'))) {
                $output .= mb_convert_case($trans, MB_CASE_TITLE, "UTF-8");
            } else {
                $output .= $trans;
            }
        }
    }

    echo $output;
}
?>
