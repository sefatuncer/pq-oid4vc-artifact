"""Control-arm label per target (pre-registration section 2D-A item 2, amendment 10).

Order: EdDSA if the EdDSA validity gate passes, else Ed25519, else ES384. A target that passes none has no second
classical algorithm and cannot express a two-algorithm required set. The SD-JWT target that does not enforce
signatures (decision D1) keeps the label of the algorithm it claims (EdDSA) and is flagged.
Input : ../../outputs/prefreeze-v1.4/*.jsonl (validity gate on battery v1.4)
Output: ../../CONTROL-LABELS.csv
"""
import csv, glob, json, os

H = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(H, '..', '..', 'outputs', 'prefreeze-v1.4')
GATES = [('EdDSA', 'VPLUS_EdDSA', 'VMINUS_EdDSA', 'kontrol-EdDSA'),
         ('Ed25519', 'VPLUS_EdDSA-ED25519', 'VMINUS_EdDSA-ED25519', 'kontrol-Ed25519'),
         ('ES384', 'VPLUS_EdDSA-ES384', 'VMINUS_EdDSA-ES384', 'kontrol-ES384')]
NO_INTEGRITY = {'SDJWT-002'}
rows = []
for f in sorted(glob.glob(os.path.join(D, '*.jsonl'))):
    t = os.path.basename(f)[:-6]
    d = {}
    for line in open(f, encoding='utf-8'):
        if line.strip():
            r = json.loads(line)
            d[(r['vektor_id'], r['kol'])] = r['sonuc_ham']
    passed = [name for name, p, m, arm in GATES
              if any(d.get((x + p, arm)) == 'kabul' and d.get((x + m, arm)) == 'red' for x in ('', 'COSE-'))]
    label = passed[0] if passed else ''
    note = 'first passing gate in the order EdDSA, Ed25519, ES384' if label else 'no second classical algorithm passes the gate'
    if t in NO_INTEGRITY:
        label, note = 'EdDSA', 'signature result not enforced (D1); claimed algorithm EdDSA; flagged integrity-failure'
    rows.append({'target': t, 'control_label': label, 'gates_passed': ';'.join(passed), 'note': note})
out = os.path.join(H, '..', '..', 'CONTROL-LABELS.csv')
with open(out, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=['target', 'control_label', 'gates_passed', 'note'])
    w.writeheader(); w.writerows(rows)
from collections import Counter
print(Counter(r['control_label'] or 'none' for r in rows))
print([r['target'] for r in rows if not r['control_label']])
