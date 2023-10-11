import unittest
from mantis import Value

class TestValue(unittest.TestCase):
    def test_indexer(self):
        v = Value(0x123456789abcdef0)
        self.assertEqual(0x1, v[0])
        self.assertEqual(0x9, v[8])
        self.assertEqual(0x0, v[15])

        v[0] = 0xf
        v[14] = 0x3
        self.assertEqual(int(v), 0xf23456789abcde30)

    def test_xor(self):
        v1 = Value(0x123456789abcdef0)
        v2 = Value(0x0000010000100010)

        result = v1 ^ v2
        self.assertEqual(int(result), 0x123457789aacdee0)
    
    def test_bytes(self):
        v1 = Value(bytes.fromhex("123456789abcdef0"))
        v2 = Value(0x123456789abcdef0)
        self.assertEqual(v1, v2)

    def test_ror(self):
        v = Value(0x123456789abcdef3)
        v = v.ror(4)
        self.assertEqual(v, Value(0x3123456789abcdef))

    def test_shift(self):
        v = Value(0x123456789abcdef3)
        v = v >> 4
        self.assertEqual(v, Value(0x123456789abcdef))
