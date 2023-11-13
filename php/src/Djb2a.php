<?php

function unsignedMultiply33($hash) {
    $s = $hash << 5;
    $sum = PHP_INT_MIN + ($s & PHP_INT_MAX) + ($hash & PHP_INT_MAX);
    if (($s ^ $hash) < 0) {
        return $sum;
    }
    return $sum ^ PHP_INT_MIN;
}

function djb2a($str) {
    $hash = 5381;

    for ($i = 0; $i < strlen($str); $i++) {
        $char = ord($str[$i]);
        $hash = unsignedMultiply33($hash);
        $hash = $hash ^ $char;
    }

    return $hash;
}
