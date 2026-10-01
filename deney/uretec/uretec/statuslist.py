"""Token Status List (draft-ietf-oauth-status-list-21) — JSON bicimi ve JWT belirteci.

4.1  bayt dizisi: indeks i, 'bits' genisliginde blok; LSB'den MSB'ye paketleme; DEFLATE+ZLIB,
     en yuksek sikistirma duzeyi ONERILIR (zlib 9).
4.2  {"bits": 1|2|4|8, "lst": base64url(sikistirilmis)}
5.1  JWT: typ=statuslist+jwt; sub (URI, zorunlu), iat (zorunlu), exp/ttl (onerilen), status_list (zorunlu)
6.2  Referans belirteci: "status": {"status_list": {"idx": i, "uri": U}}
HAIP 1.0 6.1: Status List Token'i imzalayan acik anahtar x5c'de; guven capasi x5c'ye konmaz.
"""
import zlib

from pqjose import jws
from pqjose.util import b64u_decode, b64u_encode, json_bytes

ALLOWED_BITS = (1, 2, 4, 8)


def encode(statuses: dict, size: int, bits: int = 1) -> str:
    """statuses: {indeks: deger} (diger indeksler 0 = VALID)."""
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
