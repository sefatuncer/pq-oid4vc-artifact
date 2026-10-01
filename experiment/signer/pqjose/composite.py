"""Composite ML-DSA imzasi — draft-ietf-jose-pq-composite-sigs-04.

4.2 Composite-ML-DSA.Sign(sk, M):
    M'       = Prefix || Label || 0x00 || PH(M)
    mldsaSig = ML-DSA.Sign(mldsaSK, M', ctx=Label)          (saf ML-DSA; ctx = Label)
    tradSig  = Trad.Sign(tradSK, M')                        (ECDSA: DER Ecdsa-Sig-Value; EdDSA: ham)
    s        = mldsaSig || tradSig
4.3 Verify: her iki bilesen gecerliyse gecerli (AND); serilestirme/uzunluk hatasi -> gecersiz.
JOSE'de M = JWS Signing Input (ASCII). Uygulama baglami (ctx) BOS; 0x00 bu bos baglamin uzunlugudur.
"""
import hashlib

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

from . import der, mldsa
from .params import COMPOSITE, OKP_SIG_LEN, PREFIX

_MD = {'sha256': hashes.SHA256, 'sha384': hashes.SHA384}


def prehash(ph: str, m: bytes) -> bytes:
    if ph == 'sha256':
        return hashlib.sha256(m).digest()
    if ph == 'sha512':
        return hashlib.sha512(m).digest()
    if ph == 'shake256':
        return hashlib.shake_256(m).digest(64)  # -04 Ek A.1 (ML-DSA-87-Ed448) ile dogrulandi: 64 bayt
    raise ValueError(ph)


def message_representative(alg: str, m: bytes) -> bytes:
    p = COMPOSITE[alg]
    return PREFIX + p['label'] + b'\x00' + prehash(p['ph'], m)


def _trad_sign(p, key, mp: bytes, deterministic: bool) -> bytes:
    if p['trad'] == 'ECDSA':
        return key.trad.priv.sign(mp, ec.ECDSA(_MD[p['md']](), deterministic_signing=deterministic))
    return key.trad.priv.sign(mp)  # EdDSA (Ed25519/Ed448 saf)


def sign(alg: str, key, m: bytes, deterministic: bool = False) -> bytes:
    """key: keys.CompositeKey (ozel)."""
    p = COMPOSITE[alg]
    if key.alg != alg:
        raise ValueError('anahtar alg uyusmuyor')
    mp = message_representative(alg, m)
    ml_sig = mldsa.sign(p['ml'], key.ml.seed, mp, ctx=p['label'], deterministic=deterministic)
    trad_sig = _trad_sign(p, key, mp, deterministic)
    if p['trad'] == 'ECDSA':
        # cryptography DER uretir; -04 4.5.1 kurallarina gore yeniden kodla (asgari DER, ayni bayt)
        trad_sig = der.ecdsa_raw_to_der(der.ecdsa_der_to_raw(trad_sig, p['crv']), p['crv'])
    return ml_sig + trad_sig


def split_signature(alg: str, s: bytes):
    """(mldsaSig, tradSig) — uzunluk/tip hatasinda ValueError (4.3 adim 1)."""
    p = COMPOSITE[alg]
    n = mldsa.sig_len(p['ml'])
    if len(s) <= n:
        raise ValueError('composite imza kisa')
    ml_sig, trad_sig = s[:n], s[n:]
    if p['trad'] == 'ECDSA':
        der.ecdsa_der_to_raw(trad_sig, p['crv'])  # katı DER; artik bayt reddedilir
    elif len(trad_sig) != OKP_SIG_LEN[p['crv']]:
        raise ValueError('EdDSA bileseni uzunlugu hatali')
    return ml_sig, trad_sig


def verify_components(alg: str, key, m: bytes, s: bytes):
    """Bilesen bazinda sonuc: {'ml': bool, 'trad': bool, 'hata': str|None}. key: acik CompositeKey."""
    p = COMPOSITE[alg]
    if key.alg != alg:
        return {'ml': False, 'trad': False, 'hata': 'anahtar-alg-uyumsuz'}
    try:
        ml_sig, trad_sig = split_signature(alg, s)
    except ValueError as e:
        return {'ml': False, 'trad': False, 'hata': 'serilestirme: %s' % e}
    mp = message_representative(alg, m)
    ok_ml = mldsa.verify(p['ml'], key.ml.pub, mp, ml_sig, ctx=p['label'])
    try:
        if p['trad'] == 'ECDSA':
            key.trad.pub.verify(trad_sig, mp, ec.ECDSA(_MD[p['md']]()))
        else:
            key.trad.pub.verify(trad_sig, mp)
        ok_tr = True
    except InvalidSignature:
        ok_tr = False
    return {'ml': ok_ml, 'trad': ok_tr, 'hata': None}


def verify(alg: str, key, m: bytes, s: bytes) -> bool:
    r = verify_components(alg, key, m, s)
    return bool(r['ml'] and r['trad'])
