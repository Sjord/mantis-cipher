<?php

require_once __DIR__ . '/../src/Djb2a.php';

final class TestDjb2a extends PHPUnit\Framework\TestCase
{
    public function testDbj2a() {
        $this->assertEquals(0x0000000000001505, djb2a(""));
        $this->assertEquals(0x000000000b8737a3, djb2a("foo"));
        $this->assertEquals(0x39e29dc44b089e05, djb2a("aaaaaaaaaaaaaaaa"));
        $this->assertEquals(0x648f0cff90c4f705, djb2a("zzzzzzzzzzzzzzzz"));
        $this->assertEquals(0x551ff1cbef4bc885, djb2a("AaZz35AaZz35AaZz35AaZz35AaZz35AaZz35"));
    }
}
