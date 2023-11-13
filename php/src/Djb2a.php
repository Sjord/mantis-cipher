<?php

function unsignedMultiply33($hash) {
    $s = ($hash << 5);

    $carry = $s & $hash;
    $result = $s ^ $hash;
    while ($carry != 0) {
        $shiftedcarry = $carry << 1;
        $carry = $result & $shiftedcarry;
        $result ^= $shiftedcarry;
    }
    return $result;

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

foreach ($argv as $arg) {
    printf("%s: %016x\n", $arg, djb2a($arg));
    // 36aab719f15c9fa7
}

