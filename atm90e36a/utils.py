
def split_bytes(word):
    return [word >> 8, word & 0xFF]

def uint_to_bytevec(num, byte_count = 0):
    result = []
    while num > 0 or byte_count > 0:
        result.insert(0, num & 0xFF)
        num = num >> 8
        byte_count -= 1
    return result

def bytevec_to_uint(bytelist):
    result = 0
    for byte in bytelist:
        result = result << 8
        result += byte
    return result

