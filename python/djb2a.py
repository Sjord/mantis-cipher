def djb2a(input):
    hash = 5381
    for c in input:
        hash = ((hash * 33) ^ ord(c)) & 0xFFFFFFFFFFFFFFFF
    return hash

if __name__ == "__main__":
    import sys
    for f in sys.argv[1:]:
        print(f"{f}: {djb2a(f):016x}")
