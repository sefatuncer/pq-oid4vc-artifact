"""Compare the conformance outputs with the expected acceptances (decision D9).

Per target only its relevant arms are read: the control-label arm (CONTROL-LABELS.csv) and, if the target passed the
ML-DSA-65 validity gate, the arm tedavi-ML-DSA-65. Every expected decision is an acceptance (expected.tsv).
Classes per row:
  uyumlu            sonuc_ham = kabul
  uygulanamaz       format not supported (B6, fixed in advance in the target's mapping)
  ifade-edilemedi   policy not expressible (fixed in advance in the target's mapping)
  sapma             any other outcome; every deviation is triaged in README.md (adapter defect or library behaviour)
The L4 form is derived as in analysis/analyze_c3.py: L4m if the L4 row of the two-signature mirror (T1K or COSE-K1K)
is not `uygulanamaz`, otherwise L4c.
Usage: python compare.py   (from experiment/runs/conformance)
"""
import csv
import json
import os
from collections import Counter, defaultdict

H = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.dirname(H)
labels = {r['target']: r['control_label'] for r in csv.DictReader(open(os.path.join(RUNS, 'CONTROL-LABELS.csv'), encoding='utf-8'))}
gate = {r['target']: r for r in csv.DictReader(open(os.path.join(RUNS, 'outputs', 'prefreeze-v1.4', 'GATE-SUMMARY.csv'), encoding='utf-8'))}
expected = {(r['vektor_id'], r['politika'], r['kol']): r for r in csv.DictReader(open(os.path.join(H, 'expected.tsv'), encoding='utf-8'), delimiter='\t')}
SUFFIX = {'EdDSA': '', 'ES384': '-ES384'}

rows, summary = [], []
for t in sorted(labels):
    p = os.path.join(H, 'outputs', t + '.jsonl')
    if not os.path.exists(p):
        summary.append({'target': t, 'note': 'no output'}); continue
    lab = labels[t]
    arms = (['kontrol-' + lab] if lab else ['kontrol-EdDSA']) + (['tedavi-ML-DSA-65'] if gate.get(t, {}).get('ML-DSA-65') == '1' else [])
    out = {}
    for line in open(p, encoding='utf-8'):
        if line.strip():
            o = json.loads(line); out[(o['vektor_id'], o['politika'], o['kol'])] = o
    cnt = Counter()
    for key, e in sorted(expected.items()):
        if key[2] not in arms:
            continue
        o = out.get(key)
        s = o['sonuc_ham'] if o else 'eksik'
        cls = {'kabul': 'uyumlu', 'uygulanamaz': 'uygulanamaz', 'ifade-edilemedi': 'ifade-edilemedi'}.get(s, 'sapma')
        cnt[cls] += 1
        rows.append({'target': t, 'vektor_id': key[0], 'politika': key[1], 'kol': key[2], 'beklenen': 'kabul', 'sonuc_ham': s,
                     'hata_sinifi': (o or {}).get('hata_sinifi') or '', 'hata_ozeti': ((o or {}).get('hata_ozeti') or '')[:160],
                     'sinif': cls, 'kaynak': e['kaynak']})
    arm_k = arms[0]
    sfx = SUFFIX.get(lab or 'EdDSA', '')
    multi_id = ('SYN-COSE-K1K_iki_gecerli' if t.startswith('COSE') else 'SYN-T1K_both_valid') + sfx
    m = out.get((multi_id, 'L4', arm_k), {}).get('sonuc_ham')
    form = 'L4c' if m in (None, 'uygulanamaz') else 'L4m'
    if form == 'L4m':
        det = m
    else:
        vx = ('SYN-COSE-VPLUS_EdDSA' if t.startswith('COSE') else 'SYN-VPLUS_EdDSA') + sfx
        det = out.get((vx, 'L4', arm_k), {}).get('sonuc_ham')
    summary.append({'target': t, 'arms': ';'.join(arms), 'rows': sum(cnt.values()), 'uyumlu': cnt['uyumlu'],
                    'uygulanamaz': cnt['uygulanamaz'], 'ifade_edilemedi': cnt['ifade-edilemedi'], 'sapma': cnt['sapma'],
                    'l4_form': form, 'l4_determining_row': det or 'eksik'})

os.makedirs(os.path.join(H, 'results'), exist_ok=True)
with open(os.path.join(H, 'results', 'conformance.csv'), 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
with open(os.path.join(H, 'results', 'SUMMARY.csv'), 'w', encoding='utf-8', newline='') as f:
    cols = ['target', 'arms', 'rows', 'uyumlu', 'uygulanamaz', 'ifade_edilemedi', 'sapma', 'l4_form', 'l4_determining_row', 'note']
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(summary)
for s in summary:
    print(s)
print('deviations:')
for r in rows:
    if r['sinif'] == 'sapma':
        print(r['target'], r['vektor_id'], r['politika'], r['kol'], r['sonuc_ham'], r['hata_sinifi'], r['hata_ozeti'][:100])
