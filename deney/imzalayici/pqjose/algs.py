"""JWS algoritma kaydi: imzalama ve dogrulama ilkelleri.

ES256/ES384 : RFC 7518 3.4 — imza HAM r||s (64/96 bayt); DER DEGIL.
EdDSA       : RFC 8037 (egri anahtardan); Ed25519/Ed448: RFC 9864 tam belirtilmis adlar.
ML-DSA-*    : RFC 9964 — saf ML-DSA, ctx bos.
composite   : -04 (bkz. composite.py).
"""
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature, encode_dss_signature

from . import composite, mldsa
from .keys import CompositeKey, ECKey, MLDSAKey, OKPKey
from .params import ALL_ALGS, CLASSICAL, COMPOSITE, EC_LEN, MLDSA, OKP_SIG_LEN

_MD = {'sha256': hashes.SHA256, 'sha384': hashes.SHA384}


class AlgError(ValueError):
    pass


def is_supported(alg) -> bool:
    return alg in ALL_ALGS


def key_supports(key, alg) -> bool:
    """Anahtar-alg baglama (RFC 8725 3.1 / 8725bis 3.1): anahtar tipi ve parametresi alg ile uyumlu mu?"""
    if alg in CLASSICAL:
        kty, crv, _ = CLASSICAL[alg]
        if kty == 'EC':
            return isinstance(key, ECKey) and key.crv == crv
        if crv is None:  # EdDSA
            return isinstance(key, OKPKey)
        return isinstance(key, OKPKey) and key.crv == crv
    if alg in MLDSA:
        return isinstance(key, MLDSAKey) and key.alg == alg
    if alg in COMPOSITE:
        return isinstance(key, CompositeKey) and key.alg == alg
    return False


def sign(alg: str, key, msg: bytes, deterministic: bool = False) -> bytes:
    if not is_supported(alg):
        raise AlgError('desteklenmeyen alg: %s' % alg)
    if not key_supports(key, alg):
        raise AlgError('anahtar %s ile kullanilamaz' % alg)
    if not key.has_private():
        raise AlgError('ozel anahtar yok')
    if alg in CLASSICAL:
        kty, crv, md = CLASSICAL[alg]
        if kty == 'EC':
            d = key.priv.sign(msg, ec.ECDSA(_MD[md](), deterministic_signing=deterministic))
            r, s = decode_dss_signature(d)
            n = EC_LEN[key.crv]
            return r.to_bytes(n, 'big') + s.to_bytes(n, 'big')
        return key.priv.sign(msg)
    if alg in MLDSA:
        return mldsa.sign(key.level, key.seed, msg, b'', deterministic)
    return composite.sign(alg, key, msg, deterministic)


def verify(alg: str, key, msg: bytes, sig: bytes) -> bool:
    if not is_supported(alg) or not key_supports(key, alg):
        return False
    if alg in CLASSICAL:
        kty, crv, md = CLASSICAL[alg]
        if kty == 'EC':
            n = EC_LEN[key.crv]
            if len(sig) != 2 * n:
                return False
            r, s = int.from_bytes(sig[:n], 'big'), int.from_bytes(sig[n:], 'big')
            if r == 0 or s == 0:
                return False
            try:
                key.pub.verify(encode_dss_signature(r, s), msg, ec.ECDSA(_MD[md]()))
                return True
            except InvalidSignature:
                return False
        if len(sig) != OKP_SIG_LEN[key.crv]:
            return False
        try:
            key.pub.verify(sig, msg)
            return True
        except InvalidSignature:
            return False
    if alg in MLDSA:
        return mldsa.verify(key.level, key.pub, msg, sig, b'')
    return composite.verify(alg, key, msg, sig)
