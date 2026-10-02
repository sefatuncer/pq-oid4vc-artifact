"""ML-DSA (FIPS 204) back ends.

* 'cryptography' (pyca, embedded OpenSSL): key from seed, hedged signature, verification
* 'openssl-cli'  (system OpenSSL 3.5.x) : deterministic signature (rnd = 0^32), cross-verification

RFC 9964: in JOSE ctx must be the EMPTY string; in composite -04 the ML-DSA component is called with ctx=Label.
"""
import functools

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import mldsa as _m

from . import openssl

# (public key, signature) sizes — FIPS 204 Table 2 / RFC 9964 Table 1
SIZES = {44: (1312, 2420), 65: (1952, 3309), 87: (2592, 4627)}
_PRIV = {44: _m.MLDSA44PrivateKey, 65: _m.MLDSA65PrivateKey, 87: _m.MLDSA87PrivateKey}
_PUB = {44: _m.MLDSA44PublicKey, 65: _m.MLDSA65PublicKey, 87: _m.MLDSA87PublicKey}


def pk_len(level):
    return SIZES[level][0]


def sig_len(level):
    return SIZES[level][1]


@functools.lru_cache(maxsize=512)
def _priv(level: int, seed: bytes):
    if len(seed) != 32:
        raise ValueError('ML-DSA tohumu 32 bayt olmali (RFC 9964 Bolum 4)')
    return _PRIV[level].from_seed_bytes(seed)


def public_from_seed(level: int, seed: bytes) -> bytes:
    return _priv(level, seed).public_key().public_bytes_raw()


def sign(level: int, seed: bytes, msg: bytes, ctx: bytes = b'', deterministic: bool = False) -> bytes:
    if len(ctx) > 255:
        raise ValueError('ctx en fazla 255 bayt')
    if deterministic:
        sig = openssl.mldsa_sign(level, seed, msg, ctx, deterministic=True)
    else:
        sig = _priv(level, seed).sign(msg, ctx if ctx else None)
    if len(sig) != sig_len(level):
        raise RuntimeError('beklenmeyen ML-DSA imza uzunlugu')
    return sig


def verify(level: int, pub: bytes, msg: bytes, sig: bytes, ctx: bytes = b'') -> bool:
    if len(pub) != pk_len(level) or len(sig) != sig_len(level):
        return False
    try:
        pk = _PUB[level].from_public_bytes(pub)
        pk.verify(sig, msg, ctx if ctx else None)
        return True
    except (InvalidSignature, ValueError):
        return False


def public_key_object(level: int, pub: bytes):
    return _PUB[level].from_public_bytes(pub)
