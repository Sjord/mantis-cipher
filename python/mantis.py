class Value:
    def __init__(self, val):
        try:
            self.val = int.from_bytes(val, "big")
        except TypeError:
            assert isinstance(val, int)
            self.val = val

    def __getitem__(self, index):
        assert isinstance(index, int)
        assert index >= 0
        assert index < 16

        shift = (15 - index) * 4
        return self.val >> shift & 0xF

    def __setitem__(self, index, nibble):
        assert isinstance(index, int)
        assert isinstance(nibble, int)
        assert index >= 0
        assert index < 16
        assert nibble >= 0
        assert nibble < 16

        shift = (15 - index) * 4
        mask = 0xF << shift
        self.val = (self.val & ~mask) | (nibble << shift)

    def __int__(self):
        return self.val

    def __xor__(self, other):
        return Value(self.val ^ other.val)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.val == other.val

    def __repr__(self):
        swapped = int.from_bytes(self.to_bytes(), "little")
        return f"0x{self.val:016x} ({swapped:016x})"

    def ror(self, rotations):
        rotate = self.val & ((1 << rotations) - 1)
        val = (self.val >> rotations) | rotate << (64 - rotations)
        return Value(val)

    def __rshift__(self, shifts):
        return Value(self.val >> shifts)

    def to_bytes(self):
        return self.val.to_bytes(8, "big")

    def to_nibbles(self):
        result = []
        val = self.val
        for i in range(16):
            nibble = (val & 0xF000000000000000) >> 60
            result.append(nibble)
            val <<= 4
        return result

    def clone(self):
        return Value(self.val)

    def sbox(self, sbox):
        val = self.val
        result = 0

        for i in range(16):
            result <<= 4
            nibble = (val & 0xF000000000000000) >> 60
            result |= sbox[nibble]
            val <<= 4

        return Value(result)

    def permutate(self, p):
        result = 0
        nibbles = self.to_nibbles()
        for i in range(16):
            result <<= 4
            result |= nibbles[p[i]]
        return Value(result)

    def mix_columns(self):
        def M(v):
            return [
                v[1] ^ v[2] ^ v[3],
                v[0] ^ v[2] ^ v[3],
                v[0] ^ v[1] ^ v[3],
                v[0] ^ v[1] ^ v[2],
            ]

        rows = [
            (self.val >> 48) & 0xFFFF,
            (self.val >> 32) & 0xFFFF,
            (self.val >> 16) & 0xFFFF,
            (self.val >> 0) & 0xFFFF,
        ]
        rows = M(rows)
        new_value = (rows[0] << 48) | (rows[1] << 32) | (rows[2] << 16) | rows[3]
        return Value(new_value)


class Mantis:
    rc = [
        Value(0x13198A2E03707344),
        Value(0xA4093822299F31D0),
        Value(0x082EFA98EC4E6C89),
        Value(0x452821E638D01377),
        Value(0xBE5466CF34E90C6C),
        Value(0xC0AC29B7C97C50DD),
        Value(0x3F84D5B5B5470917),
        Value(0x9216D5D98979FB1B),
    ]

    a = Value(0x243F6A8885A308D3)

    def __init__(self, key, tweak, rounds):
        self.T = Value(tweak)
        self.rounds = rounds

        self.k0 = Value(key[:8])
        self.k1 = Value(key[8:])
        self.k0prime = self.k0.ror(1) ^ self.k0 >> 63

    def encrypt(self, plaintext):
        self.IS = Value(plaintext)
        self.add_tweakey(self.k0 ^ self.k1 ^ self.T)

        for r in range(self.rounds):
            self.round(r)
        self.sub_cells()

        self.mix_columns()

        self.sub_cells()
        for r in range(self.rounds - 1, -1, -1):
            self.round_inverse(r)

        self.add_tweakey(self.k0prime ^ self.k1 ^ self.a ^ self.T)
        return self.IS.to_bytes()

    def decrypt(self, ciphertext):
        old_values = (self.k0, self.k0prime, self.k1)
        try:
            (self.k0, self.k0prime, self.k1) = (self.k0prime, self.k0, self.k1 ^ self.a)
            return self.encrypt(ciphertext)
        finally:
            (self.k0, self.k0prime, self.k1) = old_values

    def round(self, r):
        self.sub_cells()
        self.add_constant(r)
        self.add_round_tweakey()
        self.permutate_cells()
        self.mix_columns()

    def round_inverse(self, r):
        self.mix_columns()
        self.permutate_cells_inverse()
        self.add_round_tweakey_inverse()
        self.add_constant(r)
        self.sub_cells()

    def sub_cells(self):
        sbox = [
            0xC,
            0xA,
            0xD,
            0x3,
            0xE,
            0xB,
            0xF,
            0x7,
            0x8,
            0x9,
            0x1,
            0x5,
            0x0,
            0x2,
            0x4,
            0x6,
        ]
        self.IS = self.IS.sbox(sbox)

    def add_constant(self, c):
        rc = self.rc[c]
        self.IS ^= rc

    def add_round_tweakey(self):
        h = [6, 5, 14, 15, 0, 1, 2, 3, 7, 12, 13, 4, 8, 9, 10, 11]
        self.T = self.T.permutate(h)
        self.IS ^= self.T ^ self.k1

    def add_round_tweakey_inverse(self):
        self.IS ^= self.T ^ self.k1 ^ self.a
        h = [4, 5, 6, 7, 11, 1, 0, 8, 12, 13, 14, 15, 9, 10, 2, 3]
        self.T = self.T.permutate(h)

    def add_tweakey(self, tk):
        self.IS ^= tk

    def permutate_cells(self):
        P = [0, 11, 6, 13, 10, 1, 12, 7, 5, 14, 3, 8, 15, 4, 9, 2]
        self.IS = self.IS.permutate(P)

    def permutate_cells_inverse(self):
        P = [0, 5, 15, 10, 13, 8, 2, 7, 11, 14, 4, 1, 6, 3, 9, 12]
        self.IS = self.IS.permutate(P)

    def mix_columns(self):
        self.IS = self.IS.mix_columns()


if __name__ == "__main__":
    key = bytes.fromhex("92f09952c625e3e9d7a060f714c0292b")
    tweak = bytes.fromhex("ba912e6f1055fed2")
    plaintext = bytes.fromhex("3b5c77a4921f9718")
    expected = bytes.fromhex("d6522035c1c0c6c1")
    rounds = 5

    m = Mantis(key, tweak, rounds)
    ciphertext = m.encrypt(plaintext)
    print(ciphertext.hex(), expected.hex())
    assert ciphertext == expected
