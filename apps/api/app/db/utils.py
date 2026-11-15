import os
import time
import uuid


def uuid7() -> uuid.UUID:
    """
    Generates a RFC 9562 UUIDv7 (time-ordered UUID).
    Uses millisecond timestamp in the most significant 48 bits,
    with version 7 and RFC 4122 variant.
    """
    ms = int(time.time() * 1000)
    rand_bytes = os.urandom(10)

    # 48-bit timestamp
    time_high = (ms >> 16) & 0xFFFFFFFF
    time_low = ms & 0xFFFF

    # random 12 bits for counter / random A + version 7
    rand_a = (rand_bytes[0] << 8 | rand_bytes[1]) & 0x0FFF
    version_and_rand = 0x7000 | rand_a

    # variant (10xx) + random 62 bits
    var_and_rand = 0x80 | (rand_bytes[2] & 0x3F)

    byte_arr = bytearray(16)
    byte_arr[0:4] = time_high.to_bytes(4, byteorder="big")
    byte_arr[4:6] = time_low.to_bytes(2, byteorder="big")
    byte_arr[6:8] = version_and_rand.to_bytes(2, byteorder="big")
    byte_arr[8] = var_and_rand
    byte_arr[9:16] = rand_bytes[3:10]

    return uuid.UUID(bytes=bytes(byte_arr))
