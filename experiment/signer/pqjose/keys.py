"""Anahtarlar ve JWK gosterimi.

* EC  (RFC 7518 6.2)  : P-256 / P-384
* OKP (RFC 8037)      : Ed25519 / Ed448
* AKP (RFC 9964 3)    : ML-DSA-44/65/87 — pub = FIPS 204 acik anahtar, priv = 32 baytlik tohum
* AKP composite (-04) : pub = mldsaPK || tradPK ; priv = mldsaSeed || tradSK
    - ECDSA : tradPK = X9.62 sikistirilmamis nokta (0x04||x||y); tradSK = ECPrivateKey (Tablo 4)
    - EdDSA : tradPK = ham 32/57 bayt; tradSK = ham 32/57 bayt tohum
Parmak izi (RFC 7638): EC {crv,kty,x,y}; OKP {crv,kty,x}; AKP {alg,kty,pub} (RFC 9964 6).
Belirlenimci anahtar turetme: HKDF-SHA256(IKM sabit, info=etiket) — ayni etiket ayni anahtari verir.
"""
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, ed448, ed25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from . import der, mldsa, openssl
from .params import COMPOSITE, EC_LEN, MLDSA, OKP_PUB_LEN
from .util import FormatError, b64u_decode, b64u_encode, json_bytes, sha256

_CURVES = {'P-256': ec.SECP256R1(), 'P-384': ec.SECP384R1()}
_ORDER = {
    'P-256': 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551,
    'P-384': int('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFC7634D81F4372DDF581A0DB248B0A77AECEC196ACCC52973', 16),
}

MASTER_IKM = b'PQ-OID4VC Adim 9b test vektorleri v1'
_DERIVE_SALT = b'pqjose/derive/v1'


class JWKError(FormatError):
    pass


def derive_bytes(label: str, n: int, ikm: bytes = MASTER_IKM) -> bytes:
    return HKDF(algorithm=hashes.SHA256(), length=n, salt=_DERIVE_SALT, info=label.encode('utf-8')).derive(ikm)


def _pem_pub(obj) -> bytes:
    return obj.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)


def _pem_priv(obj) -> bytes:
    return obj.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                             serialization.NoEncryption())


class Key:
    kty = None

    def __init__(self):
        self.kid = None

    def algs(self):
        raise NotImplementedError

    def has_private(self) -> bool:
        raise NotImplementedError

    def _pub_members(self) -> dict:
        raise NotImplementedError

    def _priv_members(self) -> dict:
        raise NotImplementedError

    def thumbprint_members(self) -> dict:
        raise NotImplementedError

    def thumbprint(self) -> str:
        m = self.thumbprint_members()
        return b64u_encode(sha256(json_bytes({k: m[k] for k in sorted(m)})))

    def public_jwk(self, kid=True) -> dict:
        j = {}
        if kid:
            j['kid'] = self.kid or self.thumbprint()
        j.update(self._pub_members())
        return j

    def private_jwk(self, kid=True) -> dict:
        if not self.has_private():
            raise JWKError('ozel anahtar yok')
        j = self.public_jwk(kid)
        j.update(self._priv_members())
        return j

    def public_only(self):
        raise NotImplementedError


class ECKey(Key):
    kty = 'EC'

    def __init__(self, crv, priv=None, pub=None):
        super().__init__()
        if crv not in _CURVES:
            raise JWKError('desteklenmeyen egri: %s' % crv)
        self.crv = crv
        self.priv = priv
        self.pub = pub if pub is not None else priv.public_key()

    @classmethod
    def from_d(cls, crv, d: int):
        return cls(crv, priv=ec.derive_private_key(d, _CURVES[crv]))

    @classmethod
    def from_point(cls, crv, point: bytes):
        der.x962_decode(point, crv)  # uzunluk/onek denetimi
        return cls(crv, pub=ec.EllipticCurvePublicKey.from_encoded_point(_CURVES[crv], point))

    def algs(self):
        return ('ES256',) if self.crv == 'P-256' else ('ES384',)

    def has_private(self):
        return self.priv is not None

    def xy(self):
        n = EC_LEN[self.crv]
        nums = self.pub.public_numbers()
        return nums.x.to_bytes(n, 'big'), nums.y.to_bytes(n, 'big')

    def point(self) -> bytes:
        x, y = self.xy()
        return der.x962_encode(x, y)

    def d_bytes(self) -> bytes:
        return self.priv.private_numbers().private_value.to_bytes(EC_LEN[self.crv], 'big')

    def _pub_members(self):
        x, y = self.xy()
        return {'kty': 'EC', 'crv': self.crv, 'x': b64u_encode(x), 'y': b64u_encode(y)}

    def _priv_members(self):
        return {'d': b64u_encode(self.d_bytes())}

    def thumbprint_members(self):
        m = self._pub_members()
        return {k: m[k] for k in ('crv', 'kty', 'x', 'y')}

    def public_pem(self):
        return _pem_pub(self.pub)

    def private_pem(self):
        return _pem_priv(self.priv)

    def public_only(self):
        k = ECKey(self.crv, pub=self.pub)
        k.kid = self.kid
        return k


class OKPKey(Key):
    kty = 'OKP'
    _CLS = {'Ed25519': (ed25519.Ed25519PrivateKey, ed25519.Ed25519PublicKey),
            'Ed448': (ed448.Ed448PrivateKey, ed448.Ed448PublicKey)}

    def __init__(self, crv, priv_raw: bytes = None, pub_raw: bytes = None):
        super().__init__()
        if crv not in self._CLS:
            raise JWKError('desteklenmeyen OKP egrisi: %s' % crv)
        self.crv = crv
        pc, uc = self._CLS[crv]
        self.priv = pc.from_private_bytes(priv_raw) if priv_raw is not None else None
        if pub_raw is not None:
            if len(pub_raw) != OKP_PUB_LEN[crv]:
                raise JWKError('OKP x uzunlugu hatali')
            self.pub = uc.from_public_bytes(pub_raw)
            if self.priv is not None and self.priv.public_key().public_bytes_raw() != pub_raw:
                raise JWKError('OKP: d ile x uyusmuyor')
        else:
            self.pub = self.priv.public_key()

    def algs(self):
        return ('EdDSA', self.crv)

    def has_private(self):
        return self.priv is not None

    def raw_pub(self):
        return self.pub.public_bytes_raw()

    def raw_priv(self):
        return self.priv.private_bytes_raw()

    def _pub_members(self):
        return {'kty': 'OKP', 'crv': self.crv, 'x': b64u_encode(self.raw_pub())}

    def _priv_members(self):
        return {'d': b64u_encode(self.raw_priv())}

    def thumbprint_members(self):
        return self._pub_members()

    def public_pem(self):
        return _pem_pub(self.pub)

    def private_pem(self):
        return _pem_priv(self.priv)

    def public_only(self):
        k = OKPKey(self.crv, pub_raw=self.raw_pub())
        k.kid = self.kid
        return k


class MLDSAKey(Key):
    kty = 'AKP'

    def __init__(self, alg, seed: bytes = None, pub: bytes = None):
        super().__init__()
        if alg not in MLDSA:
            raise JWKError('ML-DSA alg degil: %s' % alg)
        self.alg = alg
        self.level = MLDSA[alg]
        if seed is not None and len(seed) != 32:
            raise JWKError('ML-DSA priv (tohum) 32 bayt olmali (RFC 9964 4)')
        self.seed = seed
        derived = mldsa.public_from_seed(self.level, seed) if seed is not None else None
        if pub is not None:
            if len(pub) != mldsa.pk_len(self.level):
                raise JWKError('AKP pub uzunlugu alg ile uyusmuyor (RFC 9964 5)')
            if derived is not None and derived != pub:
                raise JWKError('AKP pub/priv uyusmuyor (RFC 9964 7.4)')
            mldsa.public_key_object(self.level, pub)  # pkDecode denetimi
            self.pub = pub
        else:
            self.pub = derived

    def algs(self):
        return (self.alg,)

    def has_private(self):
        return self.seed is not None

    def _pub_members(self):
        return {'kty': 'AKP', 'alg': self.alg, 'pub': b64u_encode(self.pub)}

    def _priv_members(self):
        return {'priv': b64u_encode(self.seed)}

    def thumbprint_members(self):
        return self._pub_members()

    def public_pem(self):
        return _pem_pub(mldsa.public_key_object(self.level, self.pub))

    def private_pem(self):
        return openssl.mldsa_private_pem(self.level, self.seed)

    def public_only(self):
        k = MLDSAKey(self.alg, pub=self.pub)
        k.kid = self.kid
        return k


class CompositeKey(Key):
    kty = 'AKP'

    def __init__(self, alg, ml: MLDSAKey, trad: Key):
        super().__init__()
        if alg not in COMPOSITE:
            raise JWKError('composite alg degil: %s' % alg)
        p = COMPOSITE[alg]
        if ml.level != p['ml']:
            raise JWKError('composite: ML-DSA duzeyi uyusmuyor')
        if p['trad'] == 'ECDSA' and not (isinstance(trad, ECKey) and trad.crv == p['crv']):
            raise JWKError('composite: ECDSA bileseni uyusmuyor')
        if p['trad'] == 'EdDSA' and not (isinstance(trad, OKPKey) and trad.crv == p['crv']):
            raise JWKError('composite: EdDSA bileseni uyusmuyor')
        self.alg = alg
        self.p = p
        self.ml = ml
        self.trad = trad

    # --- -04 4.1 serilestirme ---
    def trad_pub_bytes(self) -> bytes:
        return self.trad.point() if self.p['trad'] == 'ECDSA' else self.trad.raw_pub()

    def trad_priv_bytes(self) -> bytes:
        if self.p['trad'] == 'ECDSA':
            return der.ec_private_key_encode(self.trad.d_bytes(), self.p['crv'])
        return self.trad.raw_priv()

    @property
    def pub(self) -> bytes:
        return self.ml.pub + self.trad_pub_bytes()

    @property
    def priv(self) -> bytes:
        return self.ml.seed + self.trad_priv_bytes()

    def algs(self):
        return (self.alg,)

    def has_private(self):
        return self.ml.has_private() and self.trad.has_private()

    def _pub_members(self):
        return {'kty': 'AKP', 'alg': self.alg, 'pub': b64u_encode(self.pub)}

    def _priv_members(self):
        return {'priv': b64u_encode(self.priv)}

    def thumbprint_members(self):
        return self._pub_members()

    def public_only(self):
        k = CompositeKey(self.alg, self.ml.public_only(), self.trad.public_only())
        k.kid = self.kid
        return k

    @classmethod
    def from_bytes(cls, alg, pub: bytes = None, priv: bytes = None):
        p = COMPOSITE[alg]
        lvl = p['ml']
        mpk = mldsa.pk_len(lvl)
        ml_seed = trad = None
        if priv is not None:
            ml_seed, tsk = priv[:32], priv[32:]
            if p['trad'] == 'ECDSA':
                d = der.ec_private_key_decode(tsk, p['crv'])
                trad = ECKey.from_d(p['crv'], int.from_bytes(d, 'big'))
            else:
                if len(tsk) != OKP_PUB_LEN[p['crv']]:
                    raise JWKError('composite: EdDSA ozel anahtar uzunlugu hatali')
                trad = OKPKey(p['crv'], priv_raw=tsk)
        ml_pub = None
        if pub is not None:
            ml_pub, tpk = pub[:mpk], pub[mpk:]
            if p['trad'] == 'ECDSA':
                tp = ECKey.from_point(p['crv'], tpk)
            else:
                if len(tpk) != OKP_PUB_LEN[p['crv']]:
                    raise JWKError('composite: EdDSA acik anahtar uzunlugu hatali')
                tp = OKPKey(p['crv'], pub_raw=tpk)
            if trad is None:
                trad = tp
            elif (trad.point() if p['trad'] == 'ECDSA' else trad.raw_pub()) != tpk:
                raise JWKError('composite: klasik pub/priv uyusmuyor (RFC 9964 7.4)')
        ml = MLDSAKey('ML-DSA-%d' % lvl, seed=ml_seed, pub=ml_pub)
        return cls(alg, ml, trad)


# ---------------------------------------------------------------- JWK ice aktarma
def _b(j, name, required=True):
    if name not in j:
        if required:
            raise JWKError('JWK uyesi eksik: %s' % name)
        return None
    return b64u_decode(j[name])


def key_from_jwk(j: dict) -> Key:
    if not isinstance(j, dict) or 'kty' not in j:
        raise JWKError('JWK: kty yok')
    kty = j['kty']
    if kty == 'EC':
        crv = j.get('crv')
        if crv not in _CURVES:
            raise JWKError('JWK: desteklenmeyen crv')
        n = EC_LEN[crv]
        x, y = _b(j, 'x'), _b(j, 'y')
        if len(x) != n or len(y) != n:
            raise JWKError('JWK: x/y uzunlugu hatali')
        k = ECKey.from_point(crv, der.x962_encode(x, y))
        if 'd' in j:
            d = _b(j, 'd')
            if len(d) != n:
                raise JWKError('JWK: d uzunlugu hatali')
            k2 = ECKey.from_d(crv, int.from_bytes(d, 'big'))
            if k2.point() != k.point():
                raise JWKError('JWK: d ile x/y uyusmuyor')
            k = k2
        if 'alg' in j and j['alg'] not in k.algs():
            raise JWKError('JWK: alg anahtar tipiyle uyusmuyor')
    elif kty == 'OKP':
        crv = j.get('crv')
        k = OKPKey(crv, priv_raw=_b(j, 'd', False), pub_raw=_b(j, 'x'))
        if 'alg' in j and j['alg'] not in k.algs():
            raise JWKError('JWK: alg anahtar tipiyle uyusmuyor')
    elif kty == 'AKP':
        alg = j.get('alg')
        if alg is None:
            raise JWKError('AKP: alg ZORUNLU (RFC 9964 3)')
        pub, priv = _b(j, 'pub'), _b(j, 'priv', False)
        if alg in MLDSA:
            k = MLDSAKey(alg, seed=priv, pub=pub)
        elif alg in COMPOSITE:
            p = COMPOSITE[alg]
            exp_pub = mldsa.pk_len(p['ml']) + (1 + 2 * EC_LEN[p['crv']] if p['trad'] == 'ECDSA'
                                               else OKP_PUB_LEN[p['crv']])
            if len(pub) != exp_pub:
                raise JWKError('AKP composite: pub uzunlugu hatali')
            if priv is not None:
                exp_priv = 32 + (der.ec_private_key_len(p['crv']) if p['trad'] == 'ECDSA'
                                 else OKP_PUB_LEN[p['crv']])
                if len(priv) != exp_priv:
                    raise JWKError('AKP composite: priv uzunlugu hatali')
            k = CompositeKey.from_bytes(alg, pub=pub, priv=priv)
        else:
            raise JWKError('AKP: bilinmeyen alg %s' % alg)
    else:
        raise JWKError('JWK: desteklenmeyen kty %s' % kty)
    k.kid = j.get('kid')
    return k


def key_from_public_object(obj) -> Key:
    """cryptography acik anahtar nesnesi (ornegin sertifikadan) -> Key."""
    if isinstance(obj, ec.EllipticCurvePublicKey):
        crv = {'secp256r1': 'P-256', 'secp384r1': 'P-384'}.get(obj.curve.name)
        if crv is None:
            raise JWKError('desteklenmeyen egri')
        return ECKey(crv, pub=obj)
    if isinstance(obj, ed25519.Ed25519PublicKey):
        return OKPKey('Ed25519', pub_raw=obj.public_bytes_raw())
    if isinstance(obj, ed448.Ed448PublicKey):
        return OKPKey('Ed448', pub_raw=obj.public_bytes_raw())
    from cryptography.hazmat.primitives.asymmetric import mldsa as _m
    for alg, cls in (('ML-DSA-44', _m.MLDSA44PublicKey), ('ML-DSA-65', _m.MLDSA65PublicKey),
                     ('ML-DSA-87', _m.MLDSA87PublicKey)):
        if isinstance(obj, cls):
            return MLDSAKey(alg, pub=obj.public_bytes_raw())
    raise JWKError('desteklenmeyen acik anahtar tipi: %s' % type(obj).__name__)


# ---------------------------------------------------------------- belirlenimci turetme
def derive_key(kind: str, label: str, ikm: bytes = MASTER_IKM) -> Key:
    """kind: alg adi (ES256, ES384, EdDSA/Ed25519, Ed448, ML-DSA-*, composite) veya egri adi."""
    if kind in ('ES256', 'P-256', 'ES384', 'P-384'):
        crv = 'P-256' if kind in ('ES256', 'P-256') else 'P-384'
        nb = EC_LEN[crv] + 8  # FIPS 186-5 A.2.1 benzeri: fazla bit ile modulo yanliligini azalt
        d = int.from_bytes(derive_bytes(label + '|' + crv, nb, ikm), 'big') % (_ORDER[crv] - 1) + 1
        k = ECKey.from_d(crv, d)
    elif kind in ('EdDSA', 'Ed25519'):
        k = OKPKey('Ed25519', priv_raw=derive_bytes(label + '|Ed25519', 32, ikm))
    elif kind == 'Ed448':
        k = OKPKey('Ed448', priv_raw=derive_bytes(label + '|Ed448', 57, ikm))
    elif kind in MLDSA:
        k = MLDSAKey(kind, seed=derive_bytes(label + '|' + kind, 32, ikm))
    elif kind in COMPOSITE:
        p = COMPOSITE[kind]
        # -04 6.2: bilesen anahtarlari baska baglamda kullanilmaz -> ayri etiketlerle taze uretim
        ml = MLDSAKey('ML-DSA-%d' % p['ml'], seed=derive_bytes(label + '|' + kind + '|mldsa', 32, ikm))
        trad_kind = p['crv'] if p['trad'] == 'ECDSA' else p['crv']
        trad = derive_key(trad_kind, label + '|' + kind + '|trad', ikm)
        k = CompositeKey(kind, ml, trad)
    else:
        raise JWKError('bilinmeyen anahtar turu: %s' % kind)
    return k


def default_alg(key: Key) -> str:
    if isinstance(key, OKPKey):
        return 'EdDSA'
    return key.algs()[0]
