import unittest
import secrets
from mantis import Value, Mantis

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


class TestMantis(unittest.TestCase):
    key = bytes.fromhex("92f09952c625e3e9d7a060f714c0292b")
    tweak = bytes.fromhex("ba912e6f1055fed2")
    plaintext = bytes.fromhex("3b5c77a4921f9718")

    def test_permutate_cells_reflexive(self):
        m = Mantis(self.key, self.tweak, 5)
        m.encrypt(self.plaintext)

        state = m.IS.clone()
        m.permutate_cells()
        m.permutate_cells_inverse()
        self.assertEqual(state, m.IS)

    def test_add_round_tweakey_reflexive(self):
        m = Mantis(self.key, self.tweak, 5)
        m.encrypt(self.plaintext)

        tweak = m.T.clone()
        m.add_round_tweakey()
        m.add_round_tweakey_inverse()
        self.assertEqual(tweak, m.T)

    def test_vectors_encrypt(self):
        data = [
            (5, "3b5c77a4921f9718", "d6522035c1c0c6c1"),
            (6, "d6522035c1c0c6c1", "60e43457311936fd"),
            (7, "60e43457311936fd", "308e8a07f168f517"),
            (8, "308e8a07f168f517", "971ea01a86b410bb")
        ]
        for rounds, plaintext, expected in data:
            m = Mantis(self.key, self.tweak, rounds)
            ciphertext = m.encrypt(bytes.fromhex(plaintext))
            self.assertEqual(bytes.fromhex(expected), ciphertext)
        
    def test_vectors_decrypt(self):
        data = [
            (5, "3b5c77a4921f9718", "d6522035c1c0c6c1"),
            (6, "d6522035c1c0c6c1", "60e43457311936fd"),
            (7, "60e43457311936fd", "308e8a07f168f517"),
            (8, "308e8a07f168f517", "971ea01a86b410bb")
        ]
        for rounds, expected, ciphertext in data:
            m = Mantis(self.key, self.tweak, rounds)
            plaintext = m.decrypt(bytes.fromhex(ciphertext))
            self.assertEqual(bytes.fromhex(expected), plaintext)

    def test_encrypt_decrypt(self):
        key = secrets.token_bytes(16)
        tweak = secrets.token_bytes(8)
        plaintext = secrets.token_bytes(8)

        for rounds in range(5, 9):
            m = Mantis(self.key, self.tweak, rounds)
            encrypted = m.encrypt(plaintext)
            decrypted = m.decrypt(encrypted)
            self.assertEqual(plaintext, decrypted)
