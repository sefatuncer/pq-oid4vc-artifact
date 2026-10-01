"""ECDSA kodlamalari — draft-ietf-jose-pq-composite-sigs-04 Bolum 4.5.

* Ecdsa-Sig-Value (RFC 3279)       : Bolum 4.5.1, Tablo 3 (katı DER; tek baytlık uzunluk)
* ECPrivateKey (RFC 5915)          : Bolum 4.5.2, Tablo 4 (sabit on/son ekler)
* X9.62 sıkıştırılmamış nokta      : Bolum 4.5.3 (0x04 || x || y)

JWS'teki klasik ES256/ES384 imzası ise RFC 7518 3.4'e göre ham r||s'dir; ikisi karıştırılmamalıdır.
"""
from .util import FormatError

CURVE_LEN = {'P-256': 32, 'P-384': 48}

# Tablo 4: d'nin önüne/arkasına gelen sabit baytlar
_ECPRIV_FIX = {
    'P-256': (bytes.fromhex('30310201010420'), bytes.fromhex('A00A06082A8648CE3D030107')),
    'P-384': (bytes.fromhex('303E0201010430'), bytes.fromhex('A00706052B81040022')),
}


def _der_int(v: bytes) -> bytes:
    """Tablo 3: ham (sabit uzunluklu, big-endian) değeri DER INTEGER'a çevirir."""
    t = v.lstrip(b'\x00') or b'\x00'
    if t[0] >= 0x80:
        t = b'\x00' + t
    if len(t) > 127:
        raise FormatError('DER INTEGER çok uzun')
    return b'\x02' + bytes([len(t)]) + t


def ecdsa_raw_to_der(raw: bytes, crv: str) -> bytes:
    n = CURVE_LEN[crv]
    if len(raw) != 2 * n:
        raise FormatError('ham ECDSA imzası %d bayt olmalı' % (2 * n))
    body = _der_int(raw[:n]) + _der_int(raw[n:])
    if len(body) > 127:
        raise FormatError('Ecdsa-Sig-Value çok uzun')
    return b'\x30' + bytes([len(body)]) + body


def _parse_der_int(buf: bytes, i: int, n: int):
    if i + 2 > len(buf) or buf[i] != 0x02:
        raise FormatError('DER: INTEGER etiketi yok')
    ln = buf[i + 1]
    if ln == 0 or ln >= 0x80:
        raise FormatError('DER: INTEGER uzunluğu geçersiz (uzun biçim/sıfır)')
    v = buf[i + 2:i + 2 + ln]
    if len(v) != ln:
        raise FormatError('DER: kesik INTEGER')
    if v[0] >= 0x80:
        raise FormatError('DER: negatif INTEGER')
    if v[0] == 0x00 and (ln == 1 or v[1] < 0x80):
        raise FormatError('DER: asgari olmayan INTEGER kodlaması')
    t = v.lstrip(b'\x00')
    if len(t) > n:
        raise FormatError('DER: INTEGER eğri uzunluğunu aşıyor')
    return t.rjust(n, b'\x00'), i + 2 + ln


def ecdsa_der_to_raw(der: bytes, crv: str) -> bytes:
    """Katı Ecdsa-Sig-Value çözümü; artık bayt, uzun biçim, asgari olmayan kodlama reddedilir."""
    n = CURVE_LEN[crv]
    if len(der) < 8 or der[0] != 0x30:
        raise FormatError('DER: SEQUENCE yok')
    ln = der[1]
    if ln >= 0x80:
        raise FormatError('DER: uzun biçim uzunluk (bu belgede tanımsız)')
    if 2 + ln != len(der):
        raise FormatError('DER: SEQUENCE uzunluğu tutarsız / artık bayt')
    r, i = _parse_der_int(der, 2, n)
    s, i = _parse_der_int(der, i, n)
    if i != len(der):
        raise FormatError('DER: artık bayt')
    return r + s


def ec_private_key_encode(d: bytes, crv: str) -> bytes:
    n = CURVE_LEN[crv]
    if len(d) != n:
        raise FormatError('d %d bayt olmalı' % n)
    pre, post = _ECPRIV_FIX[crv]
    return pre + d + post


def ec_private_key_decode(b: bytes, crv: str) -> bytes:
    n = CURVE_LEN[crv]
    pre, post = _ECPRIV_FIX[crv]
    if len(b) != len(pre) + n + len(post) or not b.startswith(pre) or not b.endswith(post):
        raise FormatError('ECPrivateKey: Tablo 4 biçimine uymuyor')
    return b[len(pre):len(pre) + n]


def ec_private_key_len(crv: str) -> int:
    pre, post = _ECPRIV_FIX[crv]
    return len(pre) + CURVE_LEN[crv] + len(post)


def x962_encode(x: bytes, y: bytes) -> bytes:
    return b'\x04' + x + y


def x962_decode(b: bytes, crv: str):
    n = CURVE_LEN[crv]
    if len(b) != 1 + 2 * n or b[0] != 0x04:
        raise FormatError('X9.62: sıkıştırılmamış nokta bekleniyor')
    return b[1:1 + n], b[1 + n:]
