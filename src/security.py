import random

from cryptography.hazmat.primitives import hashes


def xor(A: bytes, B: bytes) -> bytes:
    """XOR two byte strings.

    Args:
        A (bytes): The first byte string.
        B (bytes): The second byte string.

    Returns:
        bytes: The XORed byte string.
    """
    length = max(len(A), len(B))
    return bytes(
        a ^ b for a, b in zip(A.rjust(length, b"\00"), B.rjust(length, b"\00"))
    )

def sha(data: bytes) -> bytes:
    """Hash the given data with a SHA3 512 bit.

    Args:
        data (bytes): The data to hash.

    Returns:
        bytes: The hash.
    """
    digest = hashes.Hash(hashes.SHA3_512())
    digest.update(data)
    return digest.finalize()



def csprng(
    password: str, password_file: bytes, step: int
) -> bytes:
    """Generate a key at a given step via mersenne twister, given a password and a password file
    as seed, output a sha3 512bit as key.

    Args:
        password (str): Classical password string.
        password_file (bytes): Random bytes from a password file.
        step (int): The step in the mersenne twister sequence.

    Returns:
        bytes: sha512 as key.
    """
    # to prevent attacks against the password, we xor the password with the password file
    # to prevent attacks against the seed as a whole, we sha the seed
    SEED = sha(xor(password.encode("utf-8"), password_file))
    random.seed(SEED)
    randbits = random.getrandbits(256)
    for _ in range(step):
        randbits = random.getrandbits(256)
    # to prevent exposing any information on the randbits or the seed via the length,
    # we drop randomly (yet reproducibly) from the end of each part
    return sha(randbits.to_bytes(64, "big")[:-int(str(randbits)[0])] +
            SEED[:-int(str(randbits)[1])] +
            step.to_bytes(32, "big")[:-int(str(randbits)[2])])
