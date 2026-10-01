"""JWS (RFC 7515): compact, flattened ve general JSON serilestirme; politika tabanli dogrulama.

Dogrulayicinin varsayilan davranisi (BIZIM aracimiz; hedef kutuphane davranisi DEGIL):
  * semantics='all'  : mevcut TUM imzalar gecerli olmali (AND) ve en az bir imza olmali
    (RFC 7515 7.2 bunu uygulamaya birakir; asgari kosul 'en az biri' — semantics='any').
  * required_algs     : gerekli algoritma kumesi (L4). AND tek basina SOYMAYI yakalayamaz;
    soyma yalniz beklenen kume (L4) ile reddedilir.
  * bilinmeyen alg, 'none', izinli olmayan alg, anlasilmayan crit -> o imza gecersiz (fail-closed).
  * alg/crit/x5c/jwk/jku/x5u korumali baslikta olmali (katı politika; crit icin RFC 7515 4.1.11 zorunlu).
"""
from dataclasses import dataclass, field

from . import algs, composite, x509
from .keys import Key, default_alg, key_from_jwk
from .params import COMPOSITE, alg_class
from .util import FormatError, b64u_decode, b64u_encode, json_bytes, json_loads_strict

# RFC 7515 4.1 kayitli baslik parametreleri: 'crit' icinde listelenemez (4.1.11)
REGISTERED_PARAMS = frozenset({'alg', 'jku', 'jwk', 'kid', 'x5u', 'x5c', 'x5t', 'x5t#S256', 'typ', 'cty', 'crit'})
DEFAULT_PROTECTED = frozenset({'alg', 'crit', 'x5c', 'x5u', 'jwk', 'jku', 'x5t', 'x5t#S256'})


# ------------------------------------------------------------------ veri yapilari
@dataclass
class Signer:
    key: Key
    protected: dict = None
    header: dict = None      # korumasiz baslik (yalniz JSON serilestirme)
    alg: str = None


@dataclass
class SigEntry:
    protected_b64: str
    protected: dict
    header: dict
    signature_b64: str
    signature: bytes

    def params(self) -> dict:
        d = dict(self.header or {})
        d.update(self.protected or {})
        return d

    @property
    def alg(self):
        return self.params().get('alg')


@dataclass
class JWSObject:
    serialization: str
    payload_b64: str
    payload: bytes
    signatures: list

    def signing_input(self, e: SigEntry) -> bytes:
        return ((e.protected_b64 or '') + '.' + self.payload_b64).encode('ascii')

    def to_general(self) -> dict:
        sigs = []
        for e in self.signatures:
            d = {}
            if e.protected_b64:
                d['protected'] = e.protected_b64
            if e.header:
                d['header'] = e.header
            d['signature'] = e.signature_b64
            sigs.append(d)
        return {'payload': self.payload_b64, 'signatures': sigs}


# ------------------------------------------------------------------ imzalama
def _protected_with_alg(prot: dict, alg: str) -> dict:
    out = {'alg': alg}
    for k, v in (prot or {}).items():
        if k != 'alg':
            out[k] = v
    return out


def make_entry(payload_b64: str, s: Signer, deterministic: bool = False) -> SigEntry:
    alg = s.alg or (s.protected or {}).get('alg') or default_alg(s.key)
    if s.protected and 'alg' in s.protected and s.protected['alg'] != alg:
        raise ValueError('protected alg ile Signer.alg celisiyor')
    prot = _protected_with_alg(s.protected, alg)
    if s.header and set(s.header) & set(prot):
        raise ValueError('korumali ve korumasiz baslik adlari ayrik olmali (RFC 7515 7.2.1)')
    pb64 = b64u_encode(json_bytes(prot))
    sig = algs.sign(alg, s.key, (pb64 + '.' + payload_b64).encode('ascii'), deterministic)
    return SigEntry(pb64, prot, dict(s.header) if s.header else None, b64u_encode(sig), sig)


def sign(payload: bytes, signers, serialization: str = 'compact', deterministic: bool = False):
    if isinstance(signers, Signer):
        signers = [signers]
    pl = b64u_encode(payload)
    entries = [make_entry(pl, s, deterministic) for s in signers]
    return serialize(JWSObject(serialization, pl, payload, entries), serialization)


def serialize(obj: JWSObject, serialization: str):
    e = obj.signatures
    if serialization == 'compact':
        if len(e) != 1 or e[0].header:
            raise ValueError('compact: tek imza ve korumasiz baslik yok')
        return e[0].protected_b64 + '.' + obj.payload_b64 + '.' + e[0].signature_b64
    if serialization == 'flattened':
        if len(e) != 1:
            raise ValueError('flattened: tek imza')
        d = {'payload': obj.payload_b64}
        if e[0].protected_b64:
            d['protected'] = e[0].protected_b64
        if e[0].header:
            d['header'] = e[0].header
        d['signature'] = e[0].signature_b64
        return d
    if serialization == 'general':
        return obj.to_general()
    raise ValueError(serialization)


# ------------------------------------------------------------------ ayristirma
def _decode_protected(pb64):
    if pb64 is None:
        return None, {}
    if not isinstance(pb64, str):
        raise FormatError('protected dize olmali')
    h = json_loads_strict(b64u_decode(pb64))
    if not isinstance(h, dict):
        raise FormatError('korumali baslik JSON nesnesi olmali')
    return pb64, h


def _entry(d) -> SigEntry:
    if not isinstance(d, dict):
        raise FormatError('imza nesnesi JSON nesnesi olmali')
    if 'signature' not in d or not isinstance(d['signature'], str):
        raise FormatError('signature uyesi yok')
    if 'protected' not in d and 'header' not in d:
        raise FormatError('protected ya da header gerekli (RFC 7515 7.2.1)')
    pb64, prot = _decode_protected(d.get('protected'))
    hdr = d.get('header')
    if hdr is not None and not isinstance(hdr, dict):
        raise FormatError('header JSON nesnesi olmali')
    if hdr and set(hdr) & set(prot):
        raise FormatError('korumali/korumasiz baslik adlari ayrik degil (RFC 7515 7.2.1)')
    return SigEntry(pb64, prot, hdr, d['signature'], b64u_decode(d['signature']))


def parse(jws) -> JWSObject:
    if isinstance(jws, (bytes, bytearray)):
        jws = bytes(jws).decode('utf-8')
    if isinstance(jws, str):
        s = jws.strip()
        if s.startswith('{'):
            jws = json_loads_strict(s)
        else:
            parts = s.split('.')
            if len(parts) != 3:
                raise FormatError('compact JWS 3 parcali olmali')
            pb64, prot = _decode_protected(parts[0])
            e = SigEntry(pb64, prot, None, parts[2], b64u_decode(parts[2]))
            return JWSObject('compact', parts[1], b64u_decode(parts[1]), [e])
    if not isinstance(jws, dict):
        raise FormatError('JWS: dize ya da JSON nesnesi bekleniyor')
    if 'payload' not in jws or not isinstance(jws['payload'], str):
        raise FormatError('payload uyesi yok (ayrik/kodlanmamis yuk desteklenmez)')
    pl = jws['payload']
    if 'signatures' in jws:
        if any(k in jws for k in ('protected', 'header', 'signature')):
            raise FormatError('general JSON ust duzeyde protected/header/signature icermemeli')
        sigs = jws['signatures']
        if not isinstance(sigs, list) or not sigs:
            raise FormatError('signatures bos olmayan dizi olmali')
        return JWSObject('general', pl, b64u_decode(pl), [_entry(d) for d in sigs])
    return JWSObject('flattened', pl, b64u_decode(pl), [_entry(jws)])


# ------------------------------------------------------------------ dogrulama
@dataclass
class Policy:
    semantics: str = 'all'                 # 'all' (AND) | 'any' (RFC 7515 asgarisi)
    allowed_algs: frozenset = None         # L1/L2 izin listesi (None: uygulanan tum alg'ler)
    required_algs: frozenset = None        # L4 gerekli algoritma kumesi
    keys: list = None                      # guvenilen anahtarlar (L3: anahtar-alg baglama)
    trust_anchors: list = None             # DER; verilirse x5c dogrulanir ve yaprak anahtari kullanilir
    attime: int = None                     # x5c dogrulama zamani (UNIX)
    x5c_pq_only: bool = False              # karisik/klasik zinciri reddet
    require_protected: frozenset = DEFAULT_PROTECTED
    understood_crit: frozenset = frozenset()
    allow_embedded_jwk: bool = False       # DPoP gibi: 'jwk' baslik anahtari ile dogrula
    expected_typ: str = None


@dataclass
class SigResult:
    index: int
    alg: object
    ok: bool
    reason: str
    kid: str = None
    key_source: str = None
    alg_class: str = None
    x5c: object = None
    components: dict = None

    def to_dict(self):
        d = {'index': self.index, 'alg': self.alg, 'ok': self.ok, 'reason': self.reason,
             'kid': self.kid, 'key_source': self.key_source, 'alg_class': self.alg_class}
        if self.components is not None:
            d['components'] = self.components
        if self.x5c is not None:
            d['x5c'] = {'ok': self.x5c.ok, 'reason': self.x5c.reason, 'chain_class': self.x5c.chain_class,
                        'chain': [{k: c[k] for k in ('subject', 'imza_alg', 'imza_sinif', 'anahtar_sinif')}
                                  for c in self.x5c.chain]}
        return d


@dataclass
class VerifyResult:
    valid: bool
    reason: str
    signatures: list = field(default_factory=list)
    payload: bytes = None
    serialization: str = None

    def to_dict(self):
        return {'valid': self.valid, 'reason': self.reason, 'serialization': self.serialization,
                'signatures': [s.to_dict() for s in self.signatures]}


def _check_crit(e: SigEntry, p: dict, policy: Policy):
    if 'crit' not in p:
        return None
    if 'crit' not in (e.protected or {}):
        return 'crit-korumasiz'
    c = p['crit']
    if not isinstance(c, list) or not c or not all(isinstance(x, str) for x in c):
        return 'crit-gecersiz-bicim'
    if len(set(c)) != len(c) or any(x in REGISTERED_PARAMS for x in c):
        return 'crit-gecersiz-ad'
    if any(x not in p for x in c):
        return 'crit-listelenen-parametre-yok'
    if any(x not in policy.understood_crit for x in c):
        return 'crit-anlasilmadi'
    return None


def _resolve_keys(p: dict, alg: str, policy: Policy):
    """(anahtar listesi, kaynak, x5c sonucu, hata)"""
    if 'x5c' in p and policy.trust_anchors is not None:
        r = x509.validate_x5c(p['x5c'], policy.trust_anchors, policy.attime or 0, policy.x5c_pq_only)
        if not r.ok:
            return [], 'x5c', r, r.reason
        return [r.leaf_key], 'x5c', r, None
    if policy.keys:
        cand = [k for k in policy.keys if algs.key_supports(k, alg)]
        kid = p.get('kid')
        if kid is not None:
            cand = [k for k in cand if k.kid == kid or k.thumbprint() == kid]
        if not cand:
            return [], 'keys', None, 'anahtar-yok-ya-da-alg-uyumsuz'
        return cand, 'keys', None, None
    if 'jwk' in p and policy.allow_embedded_jwk:
        j = p['jwk']
        if not isinstance(j, dict) or any(m in j for m in ('d', 'priv', 'p', 'q', 'dp', 'dq', 'qi', 'k')):
            return [], 'jwk', None, 'jwk-ozel-anahtar-iceriyor'
        try:
            k = key_from_jwk(j)
        except Exception as ex:  # noqa: BLE001
            return [], 'jwk', None, 'jwk-gecersiz: %s' % ex
        if not algs.key_supports(k, alg):
            return [], 'jwk', None, 'anahtar-alg-uyumsuz'
        return [k], 'jwk', None, None
    return [], None, None, 'anahtar-yok'


def _verify_one(obj: JWSObject, e: SigEntry, i: int, policy: Policy) -> SigResult:
    p = e.params()
    alg = p.get('alg')
    kid = p.get('kid')

    def fail(reason, **kw):
        return SigResult(i, alg, False, reason, kid=kid if isinstance(kid, str) else None,
                         alg_class=alg_class(alg) if isinstance(alg, str) else None, **kw)

    if alg is None:
        return fail('alg-yok')
    if not isinstance(alg, str):
        return fail('alg-gecersiz')
    if alg == 'none':
        return fail('alg-none')
    if not algs.is_supported(alg):
        return fail('alg-bilinmiyor')
    if policy.allowed_algs is not None and alg not in policy.allowed_algs:
        return fail('alg-izinli-degil')
    for name in policy.require_protected:
        if e.header and name in e.header:
            return fail('korumasiz-parametre:%s' % name)
    r = _check_crit(e, p, policy)
    if r:
        return fail(r)
    if policy.expected_typ is not None and (e.protected or {}).get('typ') != policy.expected_typ:
        return fail('typ-uyusmuyor')
    keys, src, x5r, err = _resolve_keys(p, alg, policy)
    if err:
        return fail(err, key_source=src, x5c=x5r)
    tbs = obj.signing_input(e)
    comp = None
    for k in keys:
        if not algs.key_supports(k, alg):
            continue
        if alg in COMPOSITE:
            comp = composite.verify_components(alg, k, tbs, e.signature)
            ok = comp['ml'] and comp['trad']
        else:
            ok = algs.verify(alg, k, tbs, e.signature)
        if ok:
            return SigResult(i, alg, True, 'ok', kid=kid, key_source=src, alg_class=alg_class(alg),
                             x5c=x5r, components=comp)
    reason = 'imza-gecersiz'
    if comp is not None:
        reason += (':' + comp['hata']) if comp.get('hata') else ':bilesen(ml=%s,trad=%s)' % (comp['ml'], comp['trad'])
    return fail(reason, key_source=src, x5c=x5r, components=comp)


def verify(jws, policy: Policy = None) -> VerifyResult:
    policy = policy or Policy()
    try:
        obj = parse(jws)
    except (FormatError, ValueError, UnicodeDecodeError) as ex:
        return VerifyResult(False, 'bicim-hatasi: %s' % ex)
    res = [_verify_one(obj, e, i, policy) for i, e in enumerate(obj.signatures)]
    if policy.semantics == 'all':
        ok = bool(res) and all(r.ok for r in res)
        reason = 'ok' if ok else 'imzalardan-en-az-biri-gecersiz'
    elif policy.semantics == 'any':
        ok = any(r.ok for r in res)
        reason = 'ok' if ok else 'gecerli-imza-yok'
    else:
        raise ValueError('semantics: all|any')
    if ok and policy.required_algs:
        valid_algs = {r.alg for r in res if r.ok}
        missing = sorted(set(policy.required_algs) - valid_algs)
        if missing:
            ok, reason = False, 'gerekli-alg-eksik:' + ','.join(missing)
    return VerifyResult(ok, reason, res, obj.payload if ok else None, obj.serialization)
