alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def encode(input: int) -> str:
    result = ""
    num = input
    for i in range(11):
        num, rem = divmod(num, 58)
        result = alphabet[rem] + result
    return result


def decode(input: str) -> int:
    assert len(input) == 11
    result = 0
    for ch in input:
        result *= 58
        index = alphabet.index(ch)
        result += index
    return result
