<?php


function divideBy58($num) {
    return intdiv(($num >> 1) & 0x7FFFFFFFFFFFFFFF, 29);
}

function encode(int $input) {
    $alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";
    
    assert(is_int($input));

    $result = "";
    $num = $input;

    for ($i = 0; $i < 11; $i++) {
        $rem = $num % 58;
        if ($num < 0) {
            $rem = ($rem + 24) % 58;
        }
        $num = divideBy58($num);
        $result = $alphabet[$rem] . $result;
    }

    assert($num == 0);

    return $result;
}

function decode(string $input) {
    $alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";
    $max_token = "jpXCZedGfVQ";
    
    if (strlen($input) !== 11) {
        throw new Exception("Expected token of length 11, got token of length " . strlen($input));
    }

    if ($input > $max_token) {
        throw new Exception("Token is too big to decode into a 64-bit integer");
    }

    $result = 0;

    for ($i = 0; $i < strlen($input); $i++) {
        $result = ($result * 29) << 1;
        $index = strpos($alphabet, $input[$i]);
        $result += $index;
    }

    return (int)$result;
}
