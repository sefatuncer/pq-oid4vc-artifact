"""Test vector set v1.4 = v1.3 (byte-identical) + ES384 counterparts of the control-arm (EdDSA) vectors.

Why: the control arm measures policy expressibility with a second classical algorithm, separately from PQ
support. Some targets support neither EdDSA nor Ed25519. For them the control arm uses ES384, a second
classical algorithm (pre-registration amendment 10). Label order: EdDSA, then Ed25519, then ES384.

Construction (per kontrol-EdDSA vector of v1.3, except the DPoP proof):
  * every signature whose header algorithm is EdDSA is re-made with the issuer/ES384 key (P-384) and
    alg ES384 (COSE -35), kid of that key; the payload and every other signature stay byte-identical;
  * a signature recorded as corrupted ("bozuk: bayt N, bit B") is corrupted the same way;
  * K10 alg/key mismatch vectors keep their meaning: the X label becomes ES384
    (header ES384 + ES256 key; header ES256 + ES384 key).
Usage (in pq-a09-credgen:1.3, /work = experiment/vector-generator): python -m uretec.v14 /work
"""
import copy
import hashlib
import json
import os
import re
import shutil
import sys

from pqjose import algs
from pqjose.util import b64u_decode, b64u_encode, json_bytes

from . import cbor, cose
from .anahtar import AnahtarSeti
from .cbor import Tag

SRC, DST = 'v1.3', 'v1.4'
X_OLD, X_NEW, X_ROLE = 'EdDSA', 'ES384', 'issuer/ES384'
COSE_ES384 = -35
SKIP = {'DPOP02_EdDSA'}


def flip(b, i, bit=0):
    x = bytearray(b)
    x[i] ^= (1 << bit)
    return bytes(x)


def corruption(rec):
    m = re.search(r'bayt (\d+), bit (\d+)', rec.get('insa', '') or '')
    return (int(m.group(1)), int(m.group(2))) if m else None


def jws_resign(obj, recs, S):
    """obj: compact string or general/flattened JSON dict. Returns the new object and changed indices."""
    kES = S[X_ROLE]
    kES256 = S['issuer/ES256']
    if isinstance(obj, str):
        parts = obj.split('.')
        entries = [{'protected': parts[0], 'signature': parts[2]}]
        payload_b64 = parts[1]
    else:
        entries = obj['signatures'] if 'signatures' in obj else [obj]
        payload_b64 = obj['payload']
    changed = []
    for i, e in enumerate(entries):
        prot = json.loads(b64u_decode(e['protected']))
        rec = recs[i] if i < len(recs) else {}
        role = rec.get('anahtar_rolu')
        if prot.get('alg') == X_OLD and role == 'issuer/EdDSA':
            key, sign_alg, prot['alg'] = kES, X_NEW, X_NEW
            if 'kid' in prot:
                prot['kid'] = kES.kid
        elif prot.get('alg') == X_OLD and role == 'issuer/ES256':          # K10: label EdDSA, key ES256
            key, sign_alg, prot['alg'] = kES256, 'ES256', X_NEW
        elif prot.get('alg') == 'ES256' and role == 'issuer/EdDSA':        # K10: label ES256, key Ed25519
            key, sign_alg = kES, X_NEW
            if 'kid' in prot:
                prot['kid'] = kES.kid
        else:
            continue
        pb64 = b64u_encode(json_bytes(prot))
        sig = algs.sign(sign_alg, key, (pb64 + '.' + payload_b64).encode('ascii'), True)
        c = corruption(rec)
        if c:
            sig = flip(sig, *c)
        e['protected'], e['signature'] = pb64, b64u_encode(sig)
        changed.append(i)
    if isinstance(obj, str):
        return '.'.join((entries[0]['protected'], payload_b64, entries[0]['signature'])), changed
    return obj, changed


def cose_resign(data, recs, S):
    kES = S[X_ROLE]
    kES256 = S['issuer/ES256']
    t = cbor.decode(data)
    bp, bu, pl, x = t.value
    changed = []
    if t.tag == cose.TAG_SIGN1:
        hdr = cbor.decode(bp) if bp else {}
        rec = recs[0]
        role = rec.get('anahtar_rolu')
        if hdr.get(cose.H_ALG) == cose.ALG['EdDSA'] and role == 'issuer/EdDSA':
            key, sign_alg = kES, X_NEW
            hdr[cose.H_ALG] = COSE_ES384
            if cose.H_KID in hdr:
                hdr[cose.H_KID] = cose.kid_bytes(kES)
        elif hdr.get(cose.H_ALG) == cose.ALG['EdDSA'] and role == 'issuer/ES256':
            key, sign_alg = kES256, 'ES256'
            hdr[cose.H_ALG] = COSE_ES384
        elif hdr.get(cose.H_ALG) == cose.ALG['ES256'] and role == 'issuer/EdDSA':
            key, sign_alg = kES, X_NEW
            if cose.H_KID in hdr:
                hdr[cose.H_KID] = cose.kid_bytes(kES)
        else:
            return data, changed
        nbp = cose.prot(hdr)
        sig = algs.sign(sign_alg, key, cose.sig_structure1(nbp, pl), True)
        c = corruption(rec)
        if c:
            sig = flip(sig, *c)
        changed.append(0)
        return cbor.encode(Tag(t.tag, [nbp, bu, pl, sig])), changed
    sigs = []
    for i, s in enumerate(x):
        sp, su, sg = s
        hdr = cbor.decode(sp) if sp else {}
        rec = recs[i] if i < len(recs) else {}
        if hdr.get(cose.H_ALG) == cose.ALG['EdDSA'] and rec.get('anahtar_rolu') == 'issuer/EdDSA':
            hdr[cose.H_ALG] = COSE_ES384
            if cose.H_KID in hdr:
                hdr[cose.H_KID] = cose.kid_bytes(kES)
            nsp = cose.prot(hdr)
            sg = algs.sign(X_NEW, kES, cose.sig_structure(bp, nsp, pl), True)
            c = corruption(rec)
            if c:
                sg = flip(sg, *c)
            sp = nsp
            changed.append(i)
        sigs.append([sp, su, sg])
    return cbor.encode(Tag(t.tag, [bp, bu, pl, sigs])), changed


def es384_cose_key_hex(S):
    # COSE_Key EC2 / P-384 (RFC 9053 section 7.1.1: crv 2 = P-384); cose.cose_key covers P-256 only
    k = S[X_ROLE]
    x, y = k.xy()
    return cbor.encode({1: 2, 2: cose.kid_bytes(k), -1: 2, -2: x, -3: y}).hex()


def meta(v, data, changed, S):
    e = copy.deepcopy(v)
    kES = S[X_ROLE]
    ext = v['dosya'].rsplit('.', 1)[1]
    e['id'] = v['id'] + '-ES384'
    e['dosya'] = '%s/%s.%s' % (v['aile'], e['id'], ext)
    e['sha256'] = hashlib.sha256(data).hexdigest()
    e['bayt'] = len(data)
    e['kol'] = 'kontrol-ES384'
    a = v.get('algler')
    if isinstance(a, list):
        e['algler'] = [X_NEW if x == X_OLD else x for x in a]
    elif isinstance(a, str) and a:
        e['algler'] = ';'.join(X_NEW if x == X_OLD else x for x in a.split(';'))
    e['aciklama'] = ('ES384 counterpart of v1.3 vector %s (amendment 10): signatures labelled EdDSA are re-made with the '
                     'issuer/ES384 key and label ES384; payload and all other signatures unchanged. Original description: %s'
                     % (v['id'], v.get('aciklama', '')))
    ins = e['insa']
    for i, s in enumerate(ins.get('imzalar', [])):
        if i in changed:
            if s.get('anahtar_rolu') == 'issuer/EdDSA':
                s['anahtar_rolu'], s['kid'] = X_ROLE, kES.kid
                if 'cose_kid_hex' in s:
                    s['cose_kid_hex'] = cose.kid_bytes(kES).hex()
            if s.get('alg') == X_OLD:
                s['alg'] = X_NEW
                if 'cose_alg' in s:
                    s['cose_alg'] = COSE_ES384
    if 'k10' in ins:
        k = ins['k10']
        if k.get('baslik_alg') == X_OLD:
            k['baslik_alg'] = X_NEW
        if k.get('anahtar_rolu') == 'issuer/EdDSA':
            k.update({'anahtar_rolu': X_ROLE, 'anahtar_turu': 'ES384', 'imza_uretim_alg': 'ES384', 'imza_bayt': 96})
    ins['v13_esi'] = v['id']
    g = e.get('dogrulama_girdileri') or {}
    old_kid = S['issuer/EdDSA'].kid
    if 'kid' in g:
        g['kid'] = [kES.kid if k == old_kid else k for k in g['kid']]
    if isinstance(g.get('jwk'), dict) and g['jwk'].get('kid') == old_kid:
        g['jwk'] = kES.public_jwk(kid=True)
    if 'alg_kid' in g and X_OLD in g['alg_kid']:
        g['alg_kid'][X_NEW] = kES.kid
    old_hex = cose.kid_bytes(S['issuer/EdDSA']).hex()
    if 'cose_kid_hex' in g:
        g['cose_kid_hex'] = [cose.kid_bytes(kES).hex() if h == old_hex else h for h in g['cose_kid_hex']]
    if isinstance(g.get('cose_key_hex'), dict):
        g['cose_key_hex'].pop(old_hex, None)
        g['cose_key_hex'][cose.kid_bytes(kES).hex()] = es384_cose_key_hex(S)
    return e


def main(root):
    S = AnahtarSeti()
    src = os.path.join(root, 'vektorler', SRC)
    dst = os.path.join(root, 'vektorler', DST)
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    m = json.load(open(os.path.join(src, 'MANIFEST.json'), encoding='utf-8'))
    new = []
    for v in m['vektorler']:
        if v['kol'] != 'kontrol-EdDSA' or v['id'] in SKIP:
            continue
        raw = open(os.path.join(src, v['dosya']), 'rb').read()
        recs = v['insa'].get('imzalar', [])
        if v['artefakt'] == 'cose':
            data, changed = cose_resign(raw, recs, S)
        else:
            txt = raw.decode('utf-8')
            obj = json.loads(txt) if txt.lstrip().startswith('{') else txt.strip()
            obj, changed = jws_resign(obj, recs, S)
            data = (json.dumps(obj, indent=1, ensure_ascii=False) + '\n').encode('utf-8') if isinstance(obj, dict) else obj.encode('ascii')
        if not changed:
            raise RuntimeError('no EdDSA signature replaced in ' + v['id'])
        e = meta(v, data, changed, S)
        os.makedirs(os.path.dirname(os.path.join(dst, e['dosya'])), exist_ok=True)
        open(os.path.join(dst, e['dosya']), 'wb').write(data)
        new.append(e)
    m2 = copy.deepcopy(m)
    m2['surum'] = DST
    m2['temel_surum'] = SRC
    m2['v1_3_vektor_sayisi'] = len(m['vektorler'])
    m2['es384_es_sayisi'] = len(new)
    m2['vektorler'] = m['vektorler'] + new
    m2['v1_3_capalari'] = {'MANIFEST.json': hashlib.sha256(open(os.path.join(src, 'MANIFEST.json'), 'rb').read()).hexdigest(),
                           'SHA256SUMS': hashlib.sha256(open(os.path.join(src, 'SHA256SUMS'), 'rb').read()).hexdigest()}
    with open(os.path.join(dst, 'MANIFEST.json'), 'w', encoding='utf-8') as f:
        json.dump(m2, f, indent=1, ensure_ascii=False)
        f.write('\n')
    import csv
    with open(os.path.join(src, 'MANIFEST.csv'), encoding='utf-8', newline='') as f:
        rd = csv.DictReader(f)
        cols = rd.fieldnames
        rows = list(rd)
    byid = {r['id']: r for r in rows}
    for e in new:
        r = dict(byid[e['ins_v13']] if 'ins_v13' in e else byid[e['insa']['v13_esi']])
        r.update({'id': e['id'], 'dosya': e['dosya'], 'sha256': e['sha256'], 'bayt': str(e['bayt']), 'kol': e['kol'],
                  'aciklama': e['aciklama']})
        if r.get('algler'):
            r['algler'] = ';'.join(X_NEW if x == X_OLD else x for x in r['algler'].split(';'))
        rows.append(r)
    with open(os.path.join(dst, 'MANIFEST.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    lines = []
    for dp, _, fs in os.walk(dst):
        for fn in fs:
            if fn == 'SHA256SUMS':
                continue
            p = os.path.join(dp, fn)
            lines.append('%s  %s' % (hashlib.sha256(open(p, 'rb').read()).hexdigest(), os.path.relpath(p, dst).replace(os.sep, '/')))
    with open(os.path.join(dst, 'SHA256SUMS'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(sorted(lines, key=lambda l: l.split('  ', 1)[1])) + '\n')
    print(json.dumps({'surum': DST, 'yeni': len(new), 'toplam': len(m2['vektorler'])}))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '.')
