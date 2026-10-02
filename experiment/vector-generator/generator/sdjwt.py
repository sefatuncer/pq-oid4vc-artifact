"""SD-JWT (RFC 9901) — issuance, presentation (SD-JWT+KB) and self-verification; compact and JWS JSON (General).

Rules (RFC 9901):
  4.     compact: <Issuer-signed JWT>~<D.1>~...~<D.N>~[<KB-JWT>]
  4.1.1  _sd_alg (default sha-256)
  4.2.1  object property disclosure  [salt, name, value];  4.2.2 array element disclosure [salt, value]
  4.2.3  digest = base64url(H(ASCII(base64url disclosure)))
  4.2.4  _sd (object) / {"...": digest} (array);  4.2.5 decoy digests
  4.3    KB-JWT: typ=kb+jwt; iat, aud, nonce, sd_hash
  8.1    JSON: 'disclosures' and 'kb_jwt' in the unprotected header; sd_hash over a temporary compact form
  8.3    General: disclosures/kb_jwt ONLY in the first unprotected header
AMBIGUITY (8.1): in General JSON, the phrase "the signature" for sd_hash does not say which signature is to be used
with multiple signatures. This tool uses the FIRST signature (the disclosures are also in the first header) and states this
explicitly in the vector metadata.
"""
import hashlib

from pqjose import jws
from pqjose.keys import key_from_jwk
from pqjose.util import b64u_decode, b64u_encode, json_bytes, json_loads_strict

HASHES = {'sha-256': hashlib.sha256, 'sha-384': hashlib.sha384, 'sha-512': hashlib.sha512}


def digest(encoded: str, sd_alg: str = 'sha-256') -> str:
    return b64u_encode(HASHES[sd_alg](encoded.encode('ascii')).digest())


def disclosure(salt: str, name, value) -> str:
    arr = [salt, value] if name is None else [salt, name, value]
    return b64u_encode(json_bytes(arr))


class Builder:
    """Deterministic SD payload builder. salt_fn(label)->str, decoy_fn(label)->digest."""

    def __init__(self, salt_fn, decoy_fn, sd_alg='sha-256'):
        self.salt_fn = salt_fn
        self.decoy_fn = decoy_fn
        self.sd_alg = sd_alg
        self.disclosures = []   # (label, encoded)

    def sd_prop(self, obj: dict, name: str, value, label: str):
        d = disclosure(self.salt_fn(label), name, value)
        self.disclosures.append((label, d))
        obj.setdefault('_sd', []).append(digest(d, self.sd_alg))

    def sd_elem(self, value, label: str) -> dict:
        d = disclosure(self.salt_fn(label), None, value)
        self.disclosures.append((label, d))
        return {'...': digest(d, self.sd_alg)}

    def decoys(self, obj: dict, n: int, label: str):
        for i in range(n):
            obj.setdefault('_sd', []).append(self.decoy_fn('%s/decoy/%d' % (label, i)))

    @staticmethod
    def finalize(obj):
        """Sorts the _sd arrays (RFC 9901 4.2.4.1: the order must not leak information)."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                Builder.finalize(v)
            if '_sd' in obj:
                obj['_sd'] = sorted(obj['_sd'])
        elif isinstance(obj, list):
            for v in obj:
                Builder.finalize(v)
        return obj


# ------------------------------------------------------------------ issuance
def issue_compact(payload: dict, disclosures, signer: jws.Signer, deterministic=True) -> str:
    jwt = jws.sign(json_bytes(payload), signer, 'compact', deterministic)
    return jwt + '~' + ''.join(d + '~' for d in disclosures)


def issue_general(payload: dict, disclosures, signers, deterministic=True) -> dict:
    """RFC 9901 8.3: disclosures only in the unprotected header of the first signature."""
    signers = list(signers)
    first = signers[0]
    hdr = dict(first.header or {})
    hdr['disclosures'] = list(disclosures)
    signers[0] = jws.Signer(first.key, first.protected, hdr, first.alg)
    return jws.sign(json_bytes(payload), signers, 'general', deterministic)


# ------------------------------------------------------------------ presentation
def sd_hash_compact(issuer_jwt: str, disclosures, sd_alg='sha-256') -> str:
    s = issuer_jwt + '~' + ''.join(d + '~' for d in disclosures)
    return b64u_encode(HASHES[sd_alg](s.encode('ascii')).digest())


def make_kb_jwt(holder_key, holder_alg, aud, nonce, iat, sd_hash, deterministic=True) -> str:
    claims = {'iat': iat, 'aud': aud, 'nonce': nonce, 'sd_hash': sd_hash}
    return jws.sign(json_bytes(claims), jws.Signer(holder_key, {'typ': 'kb+jwt'}, alg=holder_alg), 'compact',
                    deterministic)


def present_compact(sdjwt: str, keep_labels, all_labeled, holder_key=None, holder_alg=None, aud=None, nonce=None,
                    iat=None, sd_alg='sha-256', deterministic=True) -> str:
    """keep_labels: labels of the disclosures to be opened; all_labeled: [(label, disclosure)]."""
    issuer_jwt = sdjwt.split('~')[0]
    sel = [d for (lab, d) in all_labeled if lab in keep_labels]
    base = issuer_jwt + '~' + ''.join(d + '~' for d in sel)
    if holder_key is None:
        return base
    kb = make_kb_jwt(holder_key, holder_alg, aud, nonce, iat, sd_hash_compact(issuer_jwt, sel, sd_alg), deterministic)
    return base + kb


def present_general(gj: dict, keep_labels, all_labeled, holder_key=None, holder_alg=None, aud=None, nonce=None,
                    iat=None, sd_alg='sha-256', sd_hash_sig_index=0, deterministic=True) -> dict:
    """RFC 9901 8.1/8.3. sd_hash_sig_index: the signature used for the temporary compact form (ambiguity; default 0)."""
    import copy
    out = copy.deepcopy(gj)
    sel = [d for (lab, d) in all_labeled if lab in keep_labels]
    h0 = dict(out['signatures'][0].get('header') or {})
    h0['disclosures'] = sel
    if holder_key is not None:
        s = out['signatures'][sd_hash_sig_index]
        issuer_jwt = s['protected'] + '.' + out['payload'] + '.' + s['signature']
        h0['kb_jwt'] = make_kb_jwt(holder_key, holder_alg, aud, nonce, iat,
                                   sd_hash_compact(issuer_jwt, sel, sd_alg), deterministic)
    out['signatures'][0]['header'] = h0
    return out


# ------------------------------------------------------------------ self-verification (consistency inside the tool)
def _collect_digests(obj, acc):
    if isinstance(obj, dict):
        for d in obj.get('_sd', []):
            acc.append(d)
        for k, v in obj.items():
            if k != '_sd':
                _collect_digests(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            if isinstance(v, dict) and set(v) == {'...'}:
                acc.append(v['...'])
            else:
                _collect_digests(v, acc)


def _resolve(obj, dmap, used):
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k in ('_sd', '_sd_alg'):
                continue
            out[k] = _resolve(v, dmap, used)
        for dg in obj.get('_sd', []):
            if dg in dmap:
                arr = dmap[dg]
                if len(arr) != 3:
                    raise ValueError('nesne ifsasi 3 elemanli olmali')
                if arr[1] in out or arr[1] in ('_sd', '...'):
                    raise ValueError('ifsa adi cakisiyor')
                used.add(dg)
                out[arr[1]] = _resolve(arr[2], dmap, used)
        return out
    if isinstance(obj, list):
        out = []
        for v in obj:
            if isinstance(v, dict) and set(v) == {'...'}:
                dg = v['...']
                if dg in dmap:
                    arr = dmap[dg]
                    if len(arr) != 2:
                        raise ValueError('dizi ifsasi 2 elemanli olmali')
                    used.add(dg)
                    out.append(_resolve(arr[1], dmap, used))
            else:
                out.append(_resolve(v, dmap, used))
        return out
    return obj


def verify_sdjwt(obj, policy: jws.Policy, require_kb=False, kb_aud=None, kb_nonce=None, sd_hash_sig_index=0):
    """RFC 9901 7.1/7.3 (inside the tool). Returns: (valid, reason, decoded_claims, detail)."""
    if isinstance(obj, str) and not obj.lstrip().startswith('{'):
        parts = obj.split('~')
        issuer_jwt, discl, kb = parts[0], [p for p in parts[1:-1]], parts[-1]
        r = jws.verify(issuer_jwt, policy)
        jws_issuer = issuer_jwt
    else:
        gj = obj if isinstance(obj, dict) else json_loads_strict(obj)
        h0 = gj['signatures'][0].get('header') or {}
        discl = h0.get('disclosures', [])
        kb = h0.get('kb_jwt', '')
        stripped = {'payload': gj['payload'], 'signatures': []}
        for s in gj['signatures']:
            e = {k: v for k, v in s.items() if k != 'header'}
            hh = {k: v for k, v in (s.get('header') or {}).items() if k not in ('disclosures', 'kb_jwt')}
            if hh:
                e['header'] = hh
            stripped['signatures'].append(e)
        r = jws.verify(stripped, policy)
        s = gj['signatures'][sd_hash_sig_index]
        jws_issuer = s['protected'] + '.' + gj['payload'] + '.' + s['signature']
    if not r.valid:
        return False, 'ihracci-imzasi: ' + r.reason, None, r.to_dict()
    payload = json_loads_strict(r.payload)
    sd_alg = payload.get('_sd_alg', 'sha-256')
    dmap = {}
    for d in discl:
        dg = digest(d, sd_alg)
        if dg in dmap:
            return False, 'yinelenen-ifsa', None, None
        dmap[dg] = json_loads_strict(b64u_decode(d))
    all_dg = []
    _collect_digests(payload, all_dg)
    if len(all_dg) != len(set(all_dg)):
        return False, 'yinelenen-ozet', None, None
    used = set()
    claims = _resolve(payload, dmap, used)
    if used != set(dmap):
        return False, 'referanssiz-ifsa', None, None
    if require_kb or kb:
        if not kb:
            return False, 'kb-jwt-yok', None, None
        cnf = payload.get('cnf', {}).get('jwk')
        if cnf is None:
            return False, 'cnf-yok', None, None
        hk = key_from_jwk(cnf)
        rk = jws.verify(kb, jws.Policy(keys=[hk], expected_typ='kb+jwt'))
        if not rk.valid:
            return False, 'kb-jwt: ' + rk.reason, None, rk.to_dict()
        kc = json_loads_strict(rk.payload)
        exp_hash = sd_hash_compact(jws_issuer, discl, sd_alg)
        if kc.get('sd_hash') != exp_hash:
            return False, 'sd_hash-uyusmuyor', None, None
        if kb_aud is not None and kc.get('aud') != kb_aud:
            return False, 'aud-uyusmuyor', None, None
        if kb_nonce is not None and kc.get('nonce') != kb_nonce:
            return False, 'nonce-uyusmuyor', None, None
    return True, 'ok', claims, r.to_dict()
