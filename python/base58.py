alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

max_int = 0xFFFFFFFFFFFFFFFF
max_token = "jpXCZedGfVQ"


def encode(input: int) -> str:
    if input < 0 or input > max_int:
        raise ValueError(f"Expected integer between 0 and {max_int}, got {input}")

    result = ""
    num = input
    for i in range(11):
        num, rem = divmod(num, 58)
        result = alphabet[rem] + result
    assert num == 0
    return result


def decode(input: str) -> int:
    if len(input) != 11:
        raise ValueError(
            f"Expected token of length 11, got token of length {len(input)}"
        )

    if input > max_token:
        raise ValueError("Token is too big to decode into a 64-bit integer")

    result = 0
    for ch in input:
        result *= 58
        index = alphabet.index(ch)
        result += index
    return result
