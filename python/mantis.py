def to_nibbles(val: int):
    assert isinstance(val, int)
    assert 0 <= val < 1 << 64

    return (
        val >> 60 & 0xF,
        val >> 56 & 0xF,
        val >> 52 & 0xF,
        val >> 48 & 0xF,
        val >> 44 & 0xF,
        val >> 40 & 0xF,
        val >> 36 & 0xF,
        val >> 32 & 0xF,
        val >> 28 & 0xF,
        val >> 24 & 0xF,
        val >> 20 & 0xF,
        val >> 16 & 0xF,
        val >> 12 & 0xF,
        val >> 8 & 0xF,
        val >> 4 & 0xF,
        val & 0xF,
    )


def permutate(val: int, p: list[int]):
    assert isinstance(val, int)
    assert 0 <= val < 1 << 64

    nibbles = to_nibbles(val)
    return (
        nibbles[p[0]] << 60
        | nibbles[p[1]] << 56
        | nibbles[p[2]] << 52
        | nibbles[p[3]] << 48
        | nibbles[p[4]] << 44
        | nibbles[p[5]] << 40
        | nibbles[p[6]] << 36
        | nibbles[p[7]] << 32
        | nibbles[p[8]] << 28
        | nibbles[p[9]] << 24
        | nibbles[p[10]] << 20
        | nibbles[p[11]] << 16
        | nibbles[p[12]] << 12
        | nibbles[p[13]] << 8
        | nibbles[p[14]] << 4
        | nibbles[p[15]]
    )


def to_int(val):
    return int.from_bytes(val, "big")


def to_bytes(val):
    return val.to_bytes(8, "big")


def ror(val: int, rotations: int):
    assert isinstance(val, int)
    assert 0 <= val < 1 << 64

    rotate = val & ((1 << rotations) - 1)
    val = (val >> rotations) | rotate << (64 - rotations)
    return val


class Encryption:
    rc = [
        0x13198A2E03707344,
        0xA4093822299F31D0,
        0x082EFA98EC4E6C89,
        0x452821E638D01377,
        0xBE5466CF34E90C6C,
        0xC0AC29B7C97C50DD,
        0x3F84D5B5B5470917,
        0x9216D5D98979FB1B,
    ]

    a = 0x243F6A8885A308D3

    h = (6, 5, 14, 15, 0, 1, 2, 3, 7, 12, 13, 4, 8, 9, 10, 11)
    h_inv = (4, 5, 6, 7, 11, 1, 0, 8, 12, 13, 14, 15, 9, 10, 2, 3)
    P = (0, 11, 6, 13, 10, 1, 12, 7, 5, 14, 3, 8, 15, 4, 9, 2)
    P_inv = (0, 5, 15, 10, 13, 8, 2, 7, 11, 14, 4, 1, 6, 3, 9, 12)

    def __init__(
        self, k0: int, k0prime: int, k1: int, rounds: int, tweak: int, message: int
    ):
        self.k0 = k0
        self.k0prime = k0prime
        self.k1 = k1
        self.rounds = rounds
        self.T = tweak
        self.IS = message

    def run(self):
        self.add_tweakey(self.k0 ^ self.k1 ^ self.T)

        for r in range(self.rounds):
            self.round(r)
        self.sub_cells()

        self.mix_columns()

        self.sub_cells()
        for r in range(self.rounds - 1, -1, -1):
            self.round_inverse(r)

        self.add_tweakey(self.k0prime ^ self.k1 ^ self.a ^ self.T)
        return self.IS

    def round(self, r: int):
        self.sub_cells()
        self.add_constant(r)
        self.add_round_tweakey()
        self.permutate_cells()
        self.mix_columns()

    def round_inverse(self, r: int):
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
        val = self.IS
        result = 0

        for i in range(16):
            result <<= 4
            nibble = (val & 0xF000000000000000) >> 60
            result |= sbox[nibble]
            val <<= 4

        self.IS = result

    def add_constant(self, c: int):
        rc = self.rc[c]
        self.IS ^= rc

    def add_round_tweakey(self):
        self.T = permutate(self.T, self.h)
        self.IS ^= self.T ^ self.k1

    def add_round_tweakey_inverse(self):
        self.IS ^= self.T ^ self.k1 ^ self.a
        self.T = permutate(self.T, self.h_inv)

    def add_tweakey(self, tk: int):
        self.IS ^= tk

    def permutate_cells(self):
        self.IS = permutate(self.IS, self.P)

    def permutate_cells_inverse(self):
        self.IS = permutate(self.IS, self.P_inv)

    def mix_columns(self):
        rows = [
            (self.IS >> 48) & 0xFFFF,
            (self.IS >> 32) & 0xFFFF,
            (self.IS >> 16) & 0xFFFF,
            (self.IS >> 0) & 0xFFFF,
        ]
        rows = [
            rows[1] ^ rows[2] ^ rows[3],
            rows[0] ^ rows[2] ^ rows[3],
            rows[0] ^ rows[1] ^ rows[3],
            rows[0] ^ rows[1] ^ rows[2],
        ]
        self.IS = (rows[0] << 48) | (rows[1] << 32) | (rows[2] << 16) | rows[3]


class Mantis:
    a = 0x243F6A8885A308D3

    def __init__(self, key, tweak, rounds: int):
        self.tweak = to_int(tweak)
        self.rounds = rounds

        self.k0 = to_int(key[:8])
        self.k1 = to_int(key[8:])
        self.k0prime = ror(self.k0, 1) ^ self.k0 >> 63

    def encrypt(self, plaintext):
        e = Encryption(
            self.k0, self.k0prime, self.k1, self.rounds, self.tweak, to_int(plaintext)
        )
        return to_bytes(e.run())

    def decrypt(self, ciphertext):
        d = Encryption(
            self.k0prime,
            self.k0,
            self.k1 ^ self.a,
            self.rounds,
            self.tweak,
            to_int(ciphertext),
        )
        return to_bytes(d.run())


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
