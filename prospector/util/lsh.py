import base64
import pickle
from typing import List

from datasketch import MinHash, MinHashLSH
from datasketch.lean_minhash import LeanMinHash

PERMUTATIONS = 128
THRESHOLD = 0.95


def get_encoded_minhash(string: str) -> str:
    """Compute a MinHash object from a string and encode it"""
    return encode_minhash(compute_minhash(string))


def string_encoder(string: str) -> List[bytes]:
    """Encode a string into a list of bytes (utf-8)"""
    return [w.encode("utf-8") for w in string.split()]


def encode_minhash(mhash: LeanMinHash) -> str:
    """Encode a LeanMinHash object into a string"""
    return base64.b64encode(pickle.dumps(mhash)).decode("utf-8")
    buf = bytearray(mhash.bytesize())
    mhash.serialize(buf)
    return buf


def decode_minhash(buf: str) -> LeanMinHash:
    """Decode a LeanMinHash object from a string"""
    return pickle.loads(base64.b64decode(buf.encode("utf-8")))


def compute_minhash(string: str) -> LeanMinHash:
    """Compute a MinHash object from a string"""
    m = MinHash(num_perm=PERMUTATIONS)
    for d in string_encoder(string):
        m.update(d)
    return LeanMinHash(m)


def compute_multiple_minhashes(strings: List[str]) -> List[LeanMinHash]:
    """Compute multiple MinHash objects from a list of strings"""
    return [
        LeanMinHash(mh)
        for mh in MinHash.bulk(
            [string_encoder(s) for s in strings], num_perm=PERMUTATIONS
        )
    ]


def create(threshold: float, permutations: int):
    return MinHashLSH(threshold=threshold, num_perm=permutations)


def insert(lsh: MinHashLSH, id: str, hash: LeanMinHash):
    lsh.insert(id, hash)


def build_lsh_index() -> MinHashLSH:
    return MinHashLSH(threshold=THRESHOLD, num_perm=PERMUTATIONS)


def create_lsh_from_data(ids: List[str], data: List[str]) -> MinHashLSH:
    """Create a MinHashLSH object from a list of strings"""
    lsh = MinHashLSH(threshold=THRESHOLD, num_perm=PERMUTATIONS)
    mhashes = compute_multiple_minhashes(data)
    for id, hash in zip(ids, mhashes):
        lsh.insert(id, hash)
    return lsh


def query_lsh(lsh: MinHashLSH, string: str) -> List[str]:
    """Query a MinHashLSH object with a string"""
    mhash = compute_minhash(string)
    return lsh.query(mhash)
