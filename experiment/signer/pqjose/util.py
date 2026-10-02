"""Shared helpers: strict base64url, JSON (rejection of duplicate names), digests."""
import base64
import hashlib
import json
import re

_B64U_RE = re.compile(r'^[A-Za-z0-9_-]*$')
_B64_STD_RE = re.compile(r'^[A-Za-z0-9+/]*={0,2}$')


class FormatError(ValueError):
    """Format (serialization) error."""


def b64u_encode(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b'=').decode('ascii')


def b64u_decode(s: str, strict: bool = True) -> bytes:
    """RFC 7515 base64url (without padding). strict: only the canonical form is accepted."""
    if not isinstance(s, str):
        raise FormatError('base64url: dize bekleniyor')
    if not _B64U_RE.match(s) or len(s) % 4 == 1:
        raise FormatError('base64url: gecersiz karakter/uzunluk')
    b = base64.urlsafe_b64decode(s + '=' * (-len(s) % 4))
    if strict and b64u_encode(b) != s:
        raise FormatError('base64url: kanonik olmayan kodlama (dolgu bitleri)')
    return b


def b64_std_encode(b: bytes) -> str:
    """Standard base64 for x5c (RFC 7515 4.1.6; NOT base64url)."""
    return base64.b64encode(b).decode('ascii')


def b64_std_decode(s: str) -> bytes:
    if not isinstance(s, str) or not _B64_STD_RE.match(s) or len(s) % 4 != 0:
        raise FormatError('x5c: standart base64 bekleniyor')
    return base64.b64decode(s, validate=True)


def _no_dup_hook(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
            raise FormatError('JSON: yinelenen uye adi: %r' % k)
        d[k] = v
    return d


def json_loads_strict(b) -> object:
    """JSON decoder that rejects duplicate member names (RFC 7515 4 / RFC 7159 4)."""
    if isinstance(b, (bytes, bytearray)):
        try:
            b = bytes(b).decode('utf-8')
        except UnicodeDecodeError as e:
            raise FormatError('JSON: UTF-8 degil') from e
    try:
        return json.loads(b, object_pairs_hook=_no_dup_hook)
    except FormatError:
        raise
    except ValueError as e:
        raise FormatError('JSON cozulmedi: %s' % e) from e


def json_compact(obj) -> str:
    """Deterministic JSON without whitespace (insertion order kept)."""
    return json.dumps(obj, separators=(',', ':'), ensure_ascii=False)


def json_bytes(obj) -> bytes:
    return json_compact(obj).encode('utf-8')


def sha256(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()
