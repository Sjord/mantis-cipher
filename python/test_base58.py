import unittest
from base58 import encode, decode


class TestBase58(unittest.TestCase):
    def test_encode_fixed(self):
        self.assertEqual("11111111111", encode(0))
        self.assertEqual("11111111112", encode(1))
        self.assertEqual("11111111121", encode(58))
        self.assertEqual("2121BWoLqHW", encode(0x05FAFAFAFAFAFAF5))
        self.assertEqual("jpXCZedGfVQ", encode(0xFFFFFFFFFFFFFFFF))

    def test_encode_decode(self):
        for i in range(0, 0xFFFFFFFFFFFFFFFF, 0x1010101010101):
            self.assertEqual(i, decode(encode(i)))
