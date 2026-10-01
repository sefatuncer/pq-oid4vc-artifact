"""Pre-freeze validity gate per target and algorithm (V+ accepted and V- rejected, JOSE or COSE form).
Usage: python gate_summary.py [outputs_dir]   (default: ../../outputs/prefreeze-v1.3) -> writes GATE-SUMMARY.csv there.
"""
import csv, glob, json, os, sys

D = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', '..', 'outputs', 'prefreeze-v1.3')
ARMS = [('ES256', 'VPLUS_ES256', 'VMINUS_ES256', 'tedavi-ML-DSA-65'),
        ('EdDSA', 'VPLUS_EdDSA', 'VMINUS_EdDSA', 'kontrol-EdDSA'),
        ('Ed25519', 'VPLUS_EdDSA-ED25519', 'VMINUS_EdDSA-ED25519', 'kontrol-Ed25519'),
        ('ML-DSA-65', 'VPLUS_ML-DSA-65', 'VMINUS_ML-DSA-65', 'tedavi-ML-DSA-65')]
rows = []
for f in sorted(glob.glob(os.path.join(D, '*.jsonl'))):
    target = os.path.basename(f)[:-6]
    d = {}
    for line in open(f, encoding='utf-8'):
        if line.strip():
            r = json.loads(line)
            d[(r['vektor_id'], r['kol'])] = r['sonuc_ham']
    row = {'target': target}
    for name, plus, minus, arm in ARMS:
        row[name] = int(any(d.get((p + plus, arm)) == 'kabul' and d.get((p + minus, arm)) == 'red' for p in ('', 'COSE-')))
    row['composite'] = int(any(d.get((a, 'tedavi-composite')) == 'kabul' and d.get((b, 'tedavi-composite')) == 'red'
                               for a, b in (('CMP00_gecerli_referans', 'CMP01_ml_bileseni_bozuk'),
                                            ('COSE-K6_composite_gecerli', 'COSE-K7_ml_bileseni_bozuk'))))
    rows.append(row)
out = os.path.join(D, 'GATE-SUMMARY.csv')
with open(out, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=['target', 'ES256', 'EdDSA', 'Ed25519', 'ML-DSA-65', 'composite'])
    w.writeheader(); w.writerows(rows)
tot = {k: sum(r[k] for r in rows) for k in ('ES256', 'EdDSA', 'Ed25519', 'ML-DSA-65', 'composite')}
print(len(rows), 'targets;', tot)
