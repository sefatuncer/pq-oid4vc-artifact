"""T14: independent check of the ES384 control-arm counterparts in v1.4.

For every v1.4 vector with kol kontrol-ES384 and its v1.3 source:
  * the payload is byte-identical and every signature that was not re-made is byte-identical;
  * every re-made signature verifies under the key it was made with, unless the recipe records a corruption,
    in which case it must NOT verify;
  * the v1.3 part of the v1.4 set is byte-identical to v1.3 (SHA256SUMS of v1.3 re-checked).
Usage (in pq-a09-credgen:1.3): PYTHONPATH=/work python testler/t14_es384.py /work
"""
import hashlib
import json
import os
import sys

from pqjose import algs
from pqjose.util import b64u_decode

from uretec import cbor, cose
from uretec.anahtar import AnahtarSeti

root = sys.argv[1] if len(sys.argv) > 1 else '.'
V13, V14 = os.path.join(root, 'vektorler', 'v1.3'), os.path.join(root, 'vektorler', 'v1.4')
S = AnahtarSeti()
m14 = json.load(open(os.path.join(V14, 'MANIFEST.json'), encoding='utf-8'))
m13 = {v['id']: v for v in json.load(open(os.path.join(V13, 'MANIFEST.json'), encoding='utf-8'))['vektorler']}
res = []


def check(name, ok, detail=''):
    res.append((bool(ok), name, detail))


# v1.3 part unchanged
for line in open(os.path.join(V13, 'SHA256SUMS'), encoding='utf-8'):
    h, p = line.rstrip('\n').split('  ', 1)
    if p in ('MANIFEST.json', 'MANIFEST.csv'):   # extended by design (superset of v1.3)
        continue
    q = os.path.join(V14, p)
    check('v1.3 file identical: ' + p, os.path.exists(q) and hashlib.sha256(open(q, 'rb').read()).hexdigest() == h)

ROLE_KEY = {'issuer/ES384': S['issuer/ES384'], 'issuer/ES256': S['issuer/ES256']}
for v in m14['vektorler']:
    if v['kol'] != 'kontrol-ES384':
        continue
    src = m13[v['insa']['v13_esi']]
    a = open(os.path.join(V13, src['dosya']), 'rb').read()
    b = open(os.path.join(V14, v['dosya']), 'rb').read()
    check('sha256 recorded: ' + v['id'], hashlib.sha256(b).hexdigest() == v['sha256'])
    recs = v['insa']['imzalar']
    if v['artefakt'] == 'cose':
        ta, tb = cbor.decode(a), cbor.decode(b)
        check('payload identical: ' + v['id'], ta.value[2] == tb.value[2])
        pa, pb = cose.ayristir(a)['imzalar'], cose.ayristir(b)['imzalar']
        for i, (sa, sb) in enumerate(zip(pa, pb)):
            r = recs[i]
            changed = (sa['imza'] != sb['imza']) or (sa['sp_map'] != sb['sp_map'])
            if not changed:
                check('untouched signature identical: %s[%d]' % (v['id'], i), True)
                continue
            key = ROLE_KEY[r['anahtar_rolu']]
            alg = 'ES384' if r['anahtar_rolu'] == 'issuer/ES384' else 'ES256'
            ok = algs.verify(alg, key, sb['tbs'], sb['imza'])
            bad = 'bozuk' in (r.get('insa') or '')
            check('re-made signature %s: %s[%d]' % ('fails (corrupted)' if bad else 'verifies', v['id'], i), ok != bad)
    else:
        ta, tb = a.decode().strip(), b.decode().strip()
        if ta.startswith('{'):
            ja, jb = json.loads(ta), json.loads(tb)
            check('payload identical: ' + v['id'], ja['payload'] == jb['payload'])
            ea = ja['signatures'] if 'signatures' in ja else [ja]
            eb = jb['signatures'] if 'signatures' in jb else [jb]
            pl = jb['payload']
        else:
            pa_, pb_ = ta.split('.'), tb.split('.')
            check('payload identical: ' + v['id'], pa_[1] == pb_[1])
            ea, eb = [{'protected': pa_[0], 'signature': pa_[2]}], [{'protected': pb_[0], 'signature': pb_[2]}]
            pl = pb_[1]
        for i, (sa, sb) in enumerate(zip(ea, eb)):
            r = recs[i]
            if sa == sb:
                check('untouched signature identical: %s[%d]' % (v['id'], i), True)
                continue
            key = ROLE_KEY[r['anahtar_rolu']]
            alg = 'ES384' if r['anahtar_rolu'] == 'issuer/ES384' else 'ES256'
            ok = algs.verify(alg, key, (sb['protected'] + '.' + pl).encode('ascii'), b64u_decode(sb['signature']))
            bad = 'bozuk' in (r.get('insa') or '')
            hdr = json.loads(b64u_decode(sb['protected']))
            check('header label is ES384 or K10 ES256: %s[%d]' % (v['id'], i), hdr['alg'] in ('ES384', 'ES256'))
            check('re-made signature %s: %s[%d]' % ('fails (corrupted)' if bad else 'verifies', v['id'], i), ok != bad)

n_ok = sum(1 for r in res if r[0])
print('T14 ES384 COUNTERPARTS: %d/%d passed' % (n_ok, len(res)))
for r in res:
    if not r[0]:
        print('FAIL', r[1], r[2])
sys.exit(0 if n_ok == len(res) else 1)
