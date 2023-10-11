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

    def clone(self):
        return Value(self.val)

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
        print(self.k0)
        print(self.k0prime)
        print(self.k1)

    def encrypt(self, plaintext):
        self.IS = Value(plaintext)
        print("state", self.IS)
        self.add_tweakey(self.k0 ^ self.k1 ^ self.T)
        print("state", self.IS)
        print("tweak", self.T)

        for r in range(self.rounds):
            self.round(r, inverse=False)
        self.sub_cells()

        self.mix_columns()

        self.sub_cells()
        for r in range(self.rounds - 1, 0, -1):
            print("state", self.IS)
            self.round(r, inverse=True)
        
        self.add_tweakey(self.k0prime ^ self.k1 ^ self.a ^ self.T)
        return self.IS.to_bytes()

    def decrypt(self, ciphertext):
        self.IS = Value(ciphertext)
        pass

    def round(self, r, inverse):
        self.sub_cells()
        self.add_constant(r)
        self.add_round_tweakey(inverse)
        self.permutate_cells()
        self.mix_columns()

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
        for i in range(16):
            self.IS[i] = sbox[self.IS[i]]

    def add_constant(self, c):
        rc = self.rc[c]
        self.IS ^= rc

    def add_round_tweakey(self, inverse):
        h = [6, 5, 14, 15, 0, 1, 2, 3, 7, 12, 13, 4, 8, 9, 10, 11]
        T = self.T.clone()
        for i in range(16):
            self.T[i] = T[h[i]]

        if inverse:
            self.IS ^= self.T ^ self.k1 ^ self.a
        else:
            self.IS ^= self.T ^ self.k1

    def add_tweakey(self, tk):
        self.IS ^= tk

    def permutate_cells(self):
        P = [0, 11, 6, 13, 10, 1, 12, 7, 5, 14, 3, 8, 15, 4, 9, 2]
        state = self.IS.clone()
        for i in range(16):
            self.IS[i] = state[P[i]]

    def mix_columns(self):
        def M(v):
            return [
                v[1] ^ v[2] ^ v[3],
                v[0] ^ v[2] ^ v[3],
                v[0] ^ v[1] ^ v[3],
                v[0] ^ v[1] ^ v[2],
            ]

        for col in range(4):
            old_col = [
                self.IS[col],
                self.IS[col + 4],
                self.IS[col + 8],
                self.IS[col + 12],
            ]
            new_col = M(old_col)
            (
                self.IS[col],
                self.IS[col + 4],
                self.IS[col + 8],
                self.IS[col + 12],
            ) = new_col


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