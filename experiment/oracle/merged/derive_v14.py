"""Merged oracle for battery v1.4 (pre-registration amendment 10).

v1.4 = v1.3 + ES384 counterparts of the control-arm (EdDSA) vectors. The expected decision depends on the case,
not on which classical algorithm plays X, so every kontrol-EdDSA row of the v1.3 oracle is copied to the
kontrol-ES384 arm: the vector id becomes its ES384 counterpart when one exists (vectors that carry no X
signature, such as VPLUS_ES256 or the legacy-issuer vectors, keep their id). Rows of vectors without an ES384
counterpart that do carry an EdDSA signature (the DPoP proof) are not copied.
Input : decisions_v13.tsv, ../../vector-generator/vectors/v1.4/MANIFEST.json
Output: decisions_v14.tsv (v1.3 rows unchanged + kontrol-ES384 rows), SUMMARY_v14.json
Usage : python derive_v14.py
"""
import csv, io, json, os
from collections import Counter

K = os.path.dirname(os.path.abspath(__file__))
M = json.load(io.open(os.path.join(K, '..', '..', 'vector-generator', 'vectors', 'v1.4', 'MANIFEST.json'), encoding='utf-8'))
counterpart = {v['insa']['v13_esi']: v['id'] for v in M['vektorler'] if v['kol'] == 'kontrol-ES384'}
edDSA_vectors = {v['id'] for v in M['vektorler'] if v['kol'] == 'kontrol-EdDSA'}
rows = list(csv.DictReader(io.open(os.path.join(K, 'decisions_v13.tsv'), encoding='utf-8'), delimiter='\t'))
new, skipped = [], Counter()
for r in rows:
    if r['kol'] != 'kontrol-EdDSA':
        continue
    vid = r['vektor_id']
    if vid in counterpart:
        nid = counterpart[vid]
    elif vid in edDSA_vectors:
        skipped[vid] += 1
        continue
    else:
        nid = vid
    n = dict(r)
    n['vektor_id'], n['kol'] = nid, 'kontrol-ES384'
    n['kaynak'] = 'ES384<-%s (%s)' % (vid, r['kaynak'])
    new.append(n)
out = rows + new
with io.open(os.path.join(K, 'decisions_v14.tsv'), 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), delimiter='\t')
    w.writeheader()
    w.writerows(sorted(out, key=lambda r: (r['vektor_id'], r['politika'], r['kol'])))
oz = {'rows': len(out), 'v13_rows': len(rows), 'es384_rows': len(new),
      'es384_decisions': dict(Counter(r['karar'] for r in new)), 'not_copied': dict(skipped)}
json.dump(oz, io.open(os.path.join(K, 'SUMMARY_v14.json'), 'w', encoding='utf-8'), indent=1)
print(json.dumps(oz))
