<?php

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
        $num = intdiv(($num >> 1) & 0x7FFFFFFFFFFFFFFF, 29);
        $result = $alphabet[$rem] . $result;
    }

    assert($num == 0);

    return $result;
}

function decode(string $input) {
    $max_token = "jpXCZedGfVQ";
    $alphabet = [
        '1' => 0,
        '2' => 1,
        '3' => 2,
        '4' => 3,
        '5' => 4,
        '6' => 5,
        '7' => 6,
        '8' => 7,
        '9' => 8,
        'A' => 9,
        'B' => 10,
        'C' => 11,
        'D' => 12,
        'E' => 13,
        'F' => 14,
        'G' => 15,
        'H' => 16,
        'J' => 17,
        'K' => 18,
        'L' => 19,
        'M' => 20,
        'N' => 21,
        'P' => 22,
        'Q' => 23,
        'R' => 24,
        'S' => 25,
        'T' => 26,
        'U' => 27,
        'V' => 28,
        'W' => 29,
        'X' => 30,
        'Y' => 31,
        'Z' => 32,
        'a' => 33,
        'b' => 34,
        'c' => 35,
        'd' => 36,
        'e' => 37,
        'f' => 38,
        'g' => 39,
        'h' => 40,
        'i' => 41,
        'j' => 42,
        'k' => 43,
        'm' => 44,
        'n' => 45,
        'o' => 46,
        'p' => 47,
        'q' => 48,
        'r' => 49,
        's' => 50,
        't' => 51,
        'u' => 52,
        'v' => 53,
        'w' => 54,
        'x' => 55,
        'y' => 56,
        'z' => 57,
    ];
    
    if (strlen($input) !== 11) {
        throw new Exception("Expected token of length 11, got token of length " . strlen($input));
    }

    if ($input > $max_token) {
        throw new Exception("Token is too big to decode into a 64-bit integer");
    }

    $result = 0;

    for ($i = 0; $i < 11; $i++) {
        $result = ($result * 29) << 1;
        $index = $alphabet[$input[$i]];
        $result += $index;
    }

    return (int)$result;
}
