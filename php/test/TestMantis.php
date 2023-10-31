<?php

require_once __DIR__ . '/../src/Mantis.php';

class TestMantis extends PHPUnit\Framework\TestCase
{
    private $key;
    private $tweak;
    private $plaintext;

    protected function setUp(): void
    {
        $this->key = hex2bin("92f09952c625e3e9d7a060f714c0292b");
        $this->tweak = hex2bin("ba912e6f1055fed2");
        $this->plaintext = hex2bin("3b5c77a4921f9718");
    }

    public function testVectorsEncrypt()
    {
        $data = [
            [5, "3b5c77a4921f9718", "d6522035c1c0c6c1"],
            [6, "d6522035c1c0c6c1", "60e43457311936fd"],
            [7, "60e43457311936fd", "308e8a07f168f517"],
            [8, "308e8a07f168f517", "971ea01a86b410bb"]
        ];

        foreach ($data as $item) {
            list($rounds, $plaintext, $expected) = $item;
            $m = new Mantis($this->key, $this->tweak, $rounds);
            $ciphertext = $m->encrypt(hex2bin($plaintext));
            $this->assertEquals(hex2bin($expected), $ciphertext);
        }
    }

    public function testVectorsDecrypt()
    {
        $data = [
            [5, "3b5c77a4921f9718", "d6522035c1c0c6c1"],
            [6, "d6522035c1c0c6c1", "60e43457311936fd"],
            [7, "60e43457311936fd", "308e8a07f168f517"],
            [8, "308e8a07f168f517", "971ea01a86b410bb"]
        ];

        foreach ($data as $item) {
            list($rounds, $expected, $ciphertext) = $item;
            $m = new Mantis($this->key, $this->tweak, $rounds);
            $plaintext = $m->decrypt(hex2bin($ciphertext));
            $this->assertEquals(hex2bin($expected), $plaintext);
        }
    }

    public function testEncryptDecrypt()
    {
        $key = random_bytes(16);
        $tweak = random_bytes(8);
        $plaintext = random_bytes(8);

        for ($rounds = 5; $rounds <= 8; $rounds++) {
            $m = new Mantis($this->key, $this->tweak, $rounds);
            $encrypted = $m->encrypt($plaintext);
            $decrypted = $m->decrypt($encrypted);
            $this->assertEquals($plaintext, $decrypted);
        }
    }
}
