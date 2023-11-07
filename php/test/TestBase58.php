<?php

require_once __DIR__ . '/../src/Base58.php';

class TestBase58 extends PHPUnit\Framework\TestCase
{
    public function testEncodeFixed()
    {
        $this->assertEquals("11111111111", encode(0));
        $this->assertEquals("11111111112", encode(1));
        $this->assertEquals("11111111121", encode(58));
        $this->assertEquals("2121BWoLqHW", encode(0x05FAFAFAFAFAFAF5));
        $this->assertEquals("NQm6nKp8qFC", encode(9223372036854775807));
        $this->assertEquals("NQm6nKp8qFD", encode(-9223372036854775808));
        $this->assertEquals("jpXCZedGfVQ", encode(-1));
    }

    public function testDecodeFixed()
    {
        $this->assertEquals(0, decode("11111111111"));
        $this->assertEquals(1, decode("11111111112"));
        $this->assertEquals(58, decode("11111111121"));
        $this->assertEquals(0x05FAFAFAFAFAFAF5, decode("2121BWoLqHW"));
        $this->assertEquals(9223372036854775807, decode("NQm6nKp8qFC"));
        $this->assertEquals(-9223372036854775808, decode("NQm6nKp8qFD"));
        $this->assertEquals(-1, decode("jpXCZedGfVQ"));
    }

    public function testEncodeDecode()
    {
        for ($i = PHP_INT_MIN; $i < PHP_INT_MAX; $i += 0x1010101010101) {
            $this->assertEquals($i, decode(encode($i)));
        }
    }
}
