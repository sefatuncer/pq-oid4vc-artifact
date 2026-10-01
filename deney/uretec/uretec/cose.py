"""COSE (RFC 9052) COSE_Sign1 / COSE_Sign — uretim, ayristirma ve arac ici dogrulama (v1.3).

Kriptografik ilkeller pqjose'dan (algs, composite) gelir; burada yalniz COSE yapisi vardir.
  RFC 9052 §4.1 COSE_Sign (etiket 98), §4.2 COSE_Sign1 (etiket 18), §4.4 Sig_structure:
    COSE_Sign1 : ToBeSigned = CBOR(["Signature1", body_protected, external_aad, payload])
    COSE_Sign  : ToBeSigned = CBOR(["Signature",  body_protected, sign_protected, external_aad, payload])
  Bos korumali baslik = sifir uzunluklu bstr. external_aad = h'' (bos).
  ECDSA (RFC 9053 §2.1): imza r||s (ayni uzunlukta tamsayilar birlestirilir); EdDSA saf; ML-DSA (RFC 9964) ctx bos;
  composite (-04): ToBeSigned uzerinde composite imza (M' = Prefix||Label||0x00||PH(ToBeSigned)).
Algoritma ve etiket degerleri KORPUSTAN BIREBIR alinmistir; KAYNAK tablosu (MANIFEST id, satir, beklenen metin)
testte korpus satirlariyla yeniden karsilastirilir (T12). Tahmin YOK.
"""
from pqjose import algs
from pqjose.keys import CompositeKey, ECKey, MLDSAKey, OKPKey
from pqjose.params import COMPOSITE
from pqjose.util import b64u_decode

from . import cbor
from .cbor import Tag

# alg adi -> COSE degeri
ALG = {
    'ES256': -7, 'EdDSA': -8, 'Ed25519': -19,
    'ML-DSA-44': -48, 'ML-DSA-65': -49, 'ML-DSA-87': -50,
    'ML-DSA-44-ES256': -54, 'ML-DSA-65-ES256': -55, 'ML-DSA-87-ES384': -56,
    'ML-DSA-44-Ed25519': -57, 'ML-DSA-65-Ed25519': -58, 'ML-DSA-87-Ed448': -59,
}
ALG_AD = {v: k for k, v in ALG.items()}
KAYITLI_DEGIL = {'ML-DSA-44-ES256', 'ML-DSA-65-ES256', 'ML-DSA-87-ES384', 'ML-DSA-44-Ed25519', 'ML-DSA-65-Ed25519',
                 'ML-DSA-87-Ed448'}   # -04 §7.2: "TBD (request assignment ...)" — talep edilen, kayitli degil

# (MANIFEST id, satir no, satirda gecmesi gereken metin) — T12 korpustan yeniden dogrular
KAYNAK = {
    'alg.ES256': ('RFC9053', 248, '| ES256 |   -7  |'),
    'alg.ES256.deprecated': ('RFC9864', 467, 'Recommended:  Deprecated'),
    'alg.ES256.haip': ('HAIP', 498, 'COSE algorithm identifier -7 or -9, as applicable'),
    'alg.EdDSA': ('RFC9053', 365, '| EdDSA |   -8  |'),
    'alg.EdDSA.deprecated': ('RFC9864', 491, 'Recommended:  Deprecated'),
    'alg.Ed25519': ('RFC9864', 225, '| Ed25519 | -19   |'),
    'alg.Ed25519.kayit': ('RFC9864', 439, 'Value:  -19'),
    'alg.ML-DSA-44': ('RFC9964', 351, 'Value:  -48'),
    'alg.ML-DSA-65': ('RFC9964', 367, 'Value:  -49'),
    'alg.ML-DSA-87': ('RFC9964', 383, 'Value:  -50'),
    'alg.ML-DSA-44-ES256': ('JOSECOMP', 1251, 'Value: TBD (request assignment -54)'),
    'alg.ML-DSA-65-ES256': ('JOSECOMP', 1268, 'Value: TBD (request assignment -55)'),
    'alg.ML-DSA-87-ES384': ('JOSECOMP', 1289, 'Value: TBD (request assignment -56)'),
    'alg.ML-DSA-44-Ed25519': ('JOSECOMP', 1306, 'Value: TBD (request assignment -57)'),
    'alg.ML-DSA-65-Ed25519': ('JOSECOMP', 1323, 'Value: TBD (request assignment -58)'),
    'alg.ML-DSA-87-Ed448': ('JOSECOMP', 1345, 'Value: TBD (request assignment -59)'),
    'hdr.alg': ('RFC9052', 751, '| alg     | 1     |'),
    'hdr.kid': ('RFC9052', 762, '| kid     | 4     |'),
    'hdr.x5chain': ('RFC9360', 296, '| x5chain | 33    |'),
    'etiket.COSE_Sign': ('RFC9052', 482, '| 98       | cose-sign     | COSE_Sign'),
    'etiket.COSE_Sign1': ('RFC9052', 485, '| 18       | cose-sign1    | COSE_Sign1'),
    'sig_structure.baglam': ('RFC9052', 1025, 'context : "Signature" / "Signature1",'),
    'sig_structure.Signature': ('RFC9052', 1001, '"Signature" for signatures using the COSE_Signature structure.'),
    'sig_structure.Signature1': ('RFC9052', 1003, '"Signature1" for signatures using the COSE_Sign1 structure.'),
    'imza.ecdsa_rs': ('RFC9053', 275, 'concatenated together to form a byte string'),
    'anahtar.kty': ('RFC9052', 1607, '| kty     | 1     |'),
    'anahtar.kid': ('RFC9052', 1610, '| kid     | 2     |'),
    'anahtar.alg': ('RFC9052', 1614, '| alg     | 3     |'),
    'kty.OKP': ('RFC9053', 1627, '| OKP       |   1   |'),
    'kty.EC2': ('RFC9053', 1629, '| EC2       |   2   |'),
    'kty.AKP': ('RFC9964', 405, 'Value:  7'),
    'crv.P-256': ('RFC9053', 1654, '| P-256   |   1   |   EC2'),
    'crv.Ed25519': ('RFC9053', 1664, '| Ed25519 |   6   |   OKP'),
    'ec2.crv': ('RFC9053', 1716, '|  2   | crv  |   -1  |'),
    'ec2.x': ('RFC9053', 1719, '|  2   |  x   |   -2  |'),
    'ec2.y': ('RFC9053', 1721, '|  2   |  y   |   -3  |'),
    'okp.crv': ('RFC9053', 1760, '| crv  |    1     |   -1  |'),
    'okp.x': ('RFC9053', 1763, '| x    |    1     |   -2  |'),
    'akp.pub': ('RFC9964', 427, 'Label:  -1'),
    'akp.priv': ('RFC9964', 441, 'Label:  -2'),
}

H_ALG, H_KID, H_X5CHAIN = 1, 4, 33
TAG_SIGN, TAG_SIGN1 = 98, 18


def alg_deger(alg):
    """Kayitli alg adi -> COSE tamsayisi; bilinmeyen/kayitsiz etiket tstr olarak kalir."""
    return ALG.get(alg, alg)


def alg_adi(v):
    return ALG_AD.get(v, v if isinstance(v, str) else 'bilinmeyen(%r)' % (v,))


def kaynak_etiketi(anahtar):
    mid, satir, metin = KAYNAK[anahtar]
    return '%s:%d' % (mid, satir)


def kid_bytes(key) -> bytes:
    """COSE kid = base64url-cozulmus JWK kid (RFC 7638 parmak izi, 32 B)."""
    return b64u_decode(key.kid)


def prot(hdr: dict) -> bytes:
    return cbor.encode(hdr) if hdr else b''


def sig_structure1(body_prot: bytes, payload: bytes, aad: bytes = b'') -> bytes:
    return cbor.encode(['Signature1', body_prot, aad, payload])


def sig_structure(body_prot: bytes, sign_prot: bytes, payload: bytes, aad: bytes = b'') -> bytes:
    return cbor.encode(['Signature', body_prot, sign_prot, aad, payload])


def sign1_yapi(payload, key, alg, prot_ek=None, unprot=None, imza_alg=None, deterministic=True):
    """COSE_Sign1 dizisi [prot, unprot, payload, sig] (etiketsiz); imza_alg verilirse imza o algoritmayla uretilir."""
    hdr = {H_ALG: alg_deger(alg)}
    hdr.update(prot_ek or {})
    pb = prot(hdr)
    sig = algs.sign(imza_alg or alg, key, sig_structure1(pb, payload), deterministic)
    return [pb, dict(unprot or {}), payload, sig]


def imzaci(body_prot, payload, key, alg, prot_ek=None, unprot=None, imza_alg=None, deterministic=True, imza=None):
    """COSE_Signature [sign_prot, unprot, sig]. imza verilirse (ör. kayitsiz etiket icin rastgele bayt) kullanilir."""
    hdr = {H_ALG: alg_deger(alg)}
    hdr.update(prot_ek or {})
    sp = prot(hdr)
    if imza is None:
        imza = algs.sign(imza_alg or alg, key, sig_structure(body_prot, sp, payload), deterministic)
    return [sp, dict(unprot or {}), imza]


def sign_yapi(payload, imzacilar, body_prot=b'', body_unprot=None):
    return [body_prot, dict(body_unprot or {}), payload, list(imzacilar)]


def kodla(yapi, etiket) -> bytes:
    return cbor.encode(Tag(etiket, yapi))


# ------------------------------------------------------------------ ayristirma ve dogrulama
def ayristir(data: bytes) -> dict:
    t = cbor.decode(data)
    if not isinstance(t, Tag) or t.tag not in (TAG_SIGN, TAG_SIGN1) or not isinstance(t.value, list) or len(t.value) != 4:
        raise ValueError('etiketli COSE_Sign/COSE_Sign1 bekleniyor')
    bp, bu, pl, x = t.value
    if not isinstance(bp, bytes) or not isinstance(bu, dict) or not isinstance(pl, bytes):
        raise ValueError('COSE yapisi gecersiz')
    bpm = cbor.decode(bp) if bp else {}
    out = {'tur': 'COSE_Sign1' if t.tag == TAG_SIGN1 else 'COSE_Sign', 'etiket': t.tag, 'body_prot': bp,
           'body_prot_map': bpm, 'body_unprot': bu, 'payload': pl, 'imzalar': []}
    if t.tag == TAG_SIGN1:
        if not isinstance(x, bytes):
            raise ValueError('COSE_Sign1 imzasi bstr olmali')
        out['imzalar'].append({'sp': None, 'sp_map': bpm, 'unprot': bu, 'imza': x,
                               'tbs': sig_structure1(bp, pl)})
    else:
        if not isinstance(x, list) or not x:
            raise ValueError('COSE_Sign imzacilar dizisi bos olmamali')
        for s in x:
            if not (isinstance(s, list) and len(s) == 3 and isinstance(s[0], bytes) and isinstance(s[1], dict) and
                    isinstance(s[2], bytes)):
                raise ValueError('COSE_Signature yapisi gecersiz')
            spm = cbor.decode(s[0]) if s[0] else {}
            out['imzalar'].append({'sp': s[0], 'sp_map': spm, 'unprot': s[1], 'imza': s[2],
                                   'tbs': sig_structure(bp, s[0], pl)})
    for s in out['imzalar']:
        s['alg'] = s['sp_map'].get(H_ALG, s['unprot'].get(H_ALG))
        s['kid'] = s['sp_map'].get(H_KID, s['unprot'].get(H_KID))
    return out


def dogrula_imza(imza: dict, key, alg_adi_=None) -> bool:
    ad = alg_adi_ or alg_adi(imza['alg'])
    if not algs.is_supported(ad) or not algs.key_supports(key, ad):
        return False
    return algs.verify(ad, key, imza['tbs'], imza['imza'])


# ------------------------------------------------------------------ COSE_Key
def cose_key(key, kid: bytes = None) -> dict:
    """Acik COSE_Key (RFC 9052 §7; RFC 9053 §7.1; RFC 9964 §8.1.2-8.1.3; -04 §3 AKP composite)."""
    kid = kid if kid is not None else kid_bytes(key)
    if isinstance(key, ECKey):
        if key.crv != 'P-256':
            raise ValueError('yalniz P-256')
        x, y = key.xy()
        return {1: 2, 2: kid, -1: 1, -2: x, -3: y}
    if isinstance(key, OKPKey):
        if key.crv != 'Ed25519':
            raise ValueError('yalniz Ed25519')
        return {1: 1, 2: kid, -1: 6, -2: key.raw_pub()}
    if isinstance(key, (MLDSAKey, CompositeKey)):
        return {1: 7, 2: kid, 3: ALG[key.alg], -1: key.pub}
    raise ValueError('desteklenmeyen anahtar')


def key_from_cose(m: dict):
    """AKP COSE_Key (RFC 9964 / -04) -> pqjose anahtari (pub ve varsa priv)."""
    if m.get(1) != 7:
        raise ValueError('AKP bekleniyor')
    ad = alg_adi(m.get(3))
    if ad in ('ML-DSA-44', 'ML-DSA-65', 'ML-DSA-87'):
        return MLDSAKey(ad, seed=m.get(-2), pub=m.get(-1))
    if ad in COMPOSITE:
        return CompositeKey.from_bytes(ad, pub=m.get(-1), priv=m.get(-2))
    raise ValueError('desteklenmeyen AKP alg: %r' % (m.get(3),))
