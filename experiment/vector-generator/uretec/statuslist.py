"""Token Status List (draft-ietf-oauth-status-list-21) — JSON format and JWT token.

4.1  byte array: index i, block of width 'bits'; packing from LSB to MSB; DEFLATE+ZLIB,
     the highest compression level is RECOMMENDED (zlib 9).
4.2  {"bits": 1|2|4|8, "lst": base64url(compressed)}
5.1  JWT: typ=statuslist+jwt; sub (URI, mandatory), iat (mandatory), exp/ttl (recommended), status_list (mandatory)
6.2  Referenced token: "status": {"status_list": {"idx": i, "uri": U}}
HAIP 1.0 6.1: the public key that signs the Status List Token is in x5c; the trust anchor is not put into x5c.
"""
import zlib

from pqjose import jws
from pqjose.util import b64u_decode, b64u_encode, json_bytes

ALLOWED_BITS = (1, 2, 4, 8)


def encode(statuses: dict, size: int, bits: int = 1) -> str:
    """statuses: {index: value} (other indices 0 = VALID)."""
    if bits not in ALLOWED_BITS:
        raise ValueError('bits 1,2,4,8 olmali')
    per = 8 // bits
    arr = bytearray((size * bits + 7) // 8)
    for i, v in statuses.items():
        if not 0 <= v < (1 << bits) or not 0 <= i < size:
            raise ValueError('gecersiz durum/indeks')
        arr[i // per] |= v << ((i % per) * bits)
    return b64u_encode(zlib.compress(bytes(arr), 9))


def decode(lst: str, bits: int = 1) -> bytes:
    return zlib.decompress(b64u_decode(lst))


def get_status(lst: str, idx: int, bits: int = 1) -> int:
    b = decode(lst, bits)
    per = 8 // bits
    return (b[idx // per] >> ((idx % per) * bits)) & ((1 << bits) - 1)


def status_list_token(signer: jws.Signer, sub: str, iat: int, exp: int, ttl: int, lst: str, bits: int = 1,
                      deterministic=True) -> str:
    prot = dict(signer.protected or {})
    prot['typ'] = 'statuslist+jwt'
    claims = {'sub': sub, 'iat': iat, 'exp': exp, 'ttl': ttl, 'status_list': {'bits': bits, 'lst': lst}}
    return jws.sign(json_bytes(claims), jws.Signer(signer.key, prot, signer.header, signer.alg), 'compact',
                    deterministic)
