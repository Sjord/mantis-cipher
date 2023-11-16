<?php

function to_nibbles($val) {
    assert(is_int($val));

    return array(
        ($val >> 60) & 0xF,
        ($val >> 56) & 0xF,
        ($val >> 52) & 0xF,
        ($val >> 48) & 0xF,
        ($val >> 44) & 0xF,
        ($val >> 40) & 0xF,
        ($val >> 36) & 0xF,
        ($val >> 32) & 0xF,
        ($val >> 28) & 0xF,
        ($val >> 24) & 0xF,
        ($val >> 20) & 0xF,
        ($val >> 16) & 0xF,
        ($val >> 12) & 0xF,
        ($val >> 8) & 0xF,
        ($val >> 4) & 0xF,
        $val & 0xF
    );
}

function permutate($val, $p) {
    assert(is_int($val));

    $nibbles = to_nibbles($val);
    return (
        $nibbles[$p[0]] << 60
        | $nibbles[$p[1]] << 56
        | $nibbles[$p[2]] << 52
        | $nibbles[$p[3]] << 48
        | $nibbles[$p[4]] << 44
        | $nibbles[$p[5]] << 40
        | $nibbles[$p[6]] << 36
        | $nibbles[$p[7]] << 32
        | $nibbles[$p[8]] << 28
        | $nibbles[$p[9]] << 24
        | $nibbles[$p[10]] << 20
        | $nibbles[$p[11]] << 16
        | $nibbles[$p[12]] << 12
        | $nibbles[$p[13]] << 8
        | $nibbles[$p[14]] << 4
        | $nibbles[$p[15]]
    );
}

function to_int($value) {
    return unpack('J', $value)[1];
}

function to_bytes($value) {
    return pack('J', $value);
}

function ror($x, $n) {
    return ($x >> $n) | ($x << (64 - $n));
}

function unsigned($val) {
    return sprintf("%u", $val);
}

function hex_const($val) {
    return to_int(hex2bin($val));
}

final class Encryption {
    private $rc = [];
    private $a = 0x243F6A8885A308D3;

    private $h = [6, 5, 14, 15, 0, 1, 2, 3, 7, 12, 13, 4, 8, 9, 10, 11];
    private $h_inv = [4, 5, 6, 7, 11, 1, 0, 8, 12, 13, 14, 15, 9, 10, 2, 3];
    private $P = [0, 11, 6, 13, 10, 1, 12, 7, 5, 14, 3, 8, 15, 4, 9, 2];
    private $P_inv = [0, 5, 15, 10, 13, 8, 2, 7, 11, 14, 4, 1, 6, 3, 9, 12];

    private $k0;
    private $k0prime;
    private $k1;
    private $rounds;
    private $T;
    private $IS;

    public function __construct($k0, $k0prime, $k1, $rounds, $tweak, $message) {
        $this->k0 = $k0;
        $this->k0prime = $k0prime;
        $this->k1 = $k1;
        $this->rounds = $rounds;
        $this->T = $tweak;
        $this->IS = $message;

        $this->rc = [
            hex_const("13198A2E03707344"),
            hex_const("A4093822299F31D0"),
            hex_const("082EFA98EC4E6C89"),
            hex_const("452821E638D01377"),
            hex_const("BE5466CF34E90C6C"),
            hex_const("C0AC29B7C97C50DD"),
            hex_const("3F84D5B5B5470917"),
            hex_const("9216D5D98979FB1B"),
            hex_const("D1310BA698DFB5AC"),
            hex_const("2FFD72DBD01ADFB7"),
            hex_const("B8E1AFED6A267E96"),
            hex_const("BA7C9045F12C7F99"),
            hex_const("24A19947B3916CF7"),
            hex_const("0801F2E2858EFC16"),
            hex_const("636920D871574E69"),
        ];
    }

    public function run() {
        $this->add_tweakey($this->k0 ^ $this->k1 ^ $this->T);

        for ($r = 0; $r < $this->rounds; $r++) {
            $this->round($r);
        }
        $this->sub_cells();

        $this->mix_columns();

        $this->sub_cells();
        for ($r = $this->rounds - 1; $r >= 0; $r--) {
            $this->round_inverse($r);
        }

        $this->add_tweakey($this->k0prime ^ $this->k1 ^ $this->a ^ $this->T);
        return $this->IS;
    }

    private function round($r) {
        $this->sub_cells();
        $this->add_constant($r);
        $this->add_round_tweakey();
        $this->permutate_cells();
        $this->mix_columns();
    }

    private function round_inverse($r) {
        $this->mix_columns();
        $this->permutate_cells_inverse();
        $this->add_round_tweakey_inverse();
        $this->add_constant($r);
        $this->sub_cells();
    }

    private function sub_cells() {
        $sbox = [
            0xC, 0xA, 0xD, 0x3, 0xE, 0xB, 0xF, 0x7, 
            0x8, 0x9, 0x1, 0x5, 0x0, 0x2, 0x4, 0x6
        ];

        $result = 0;
        $nibbles = to_nibbles($this->IS);
        foreach ($nibbles as $nibble) {
            $result <<= 4;
            $result |= $sbox[$nibble];
        }

        $this->IS = $result;
    }

    private function add_constant($c) {
        $rc = $this->rc[$c];
        $this->IS ^= $rc;
    }

    private function add_round_tweakey() {
        $this->T = permutate($this->T, $this->h);
        $this->IS ^= $this->T ^ $this->k1;
    }

    private function add_round_tweakey_inverse() {
        $this->IS ^= $this->T ^ $this->k1 ^ $this->a;
        $this->T = permutate($this->T, $this->h_inv);
    }

    private function add_tweakey($tk) {
        $this->IS ^= $tk;
    }

    private function permutate_cells() {
        $this->IS = permutate($this->IS, $this->P);
    }

    private function permutate_cells_inverse() {
        $this->IS = permutate($this->IS, $this->P_inv);
    }

    private function mix_columns() {
        $rows = [
            ($this->IS >> 48) & 0xFFFF,
            ($this->IS >> 32) & 0xFFFF,
            ($this->IS >> 16) & 0xFFFF,
            ($this->IS >> 0) & 0xFFFF,
        ];

        $rows = [
            $rows[1] ^ $rows[2] ^ $rows[3],
            $rows[0] ^ $rows[2] ^ $rows[3],
            $rows[0] ^ $rows[1] ^ $rows[3],
            $rows[0] ^ $rows[1] ^ $rows[2],
        ];

        $this->IS = ($rows[0] << 48) | ($rows[1] << 32) | ($rows[2] << 16) | $rows[3];
    }
}

final class Mantis {
    private $a = 0x243F6A8885A308D3;
    private $k0;
    private $k1;
    private $k0prime;
    private $tweak;
    private $rounds;

    public function __construct($key, $tweak, $rounds) {
        $this->tweak = to_int($tweak);
        $this->rounds = $rounds;

        $this->k0 = to_int(substr($key, 0, 8));
        $this->k1 = to_int(substr($key, 8));
        $this->k0prime = ror($this->k0, 1) ^ (($this->k0 >> 63) & 1);
    }

    public function encrypt($plaintext) {
        $e = new Encryption(
            $this->k0, $this->k0prime, $this->k1, $this->rounds, $this->tweak, to_int($plaintext)
        );
        return to_bytes($e->run());
    }

    public function decrypt($ciphertext) {
        $d = new Encryption(
            $this->k0prime,
            $this->k0,
            $this->k1 ^ $this->a,
            $this->rounds,
            $this->tweak,
            to_int($ciphertext)
        );
        return to_bytes($d->run());
    }
}
