import unittest
import secrets
from mantis import Mantis


class TestMantis(unittest.TestCase):
    key = bytes.fromhex("92f09952c625e3e9d7a060f714c0292b")
    tweak = bytes.fromhex("ba912e6f1055fed2")
    plaintext = bytes.fromhex("3b5c77a4921f9718")

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
