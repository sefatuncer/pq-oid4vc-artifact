# -*- coding: utf-8 -*-
"""
PQ-OID4VC | rest of Step 9 (maintainers, 01.10.2026) | merged oracle for v1.3
==============================================================================
Input : oracle-A/decisions.tsv (858 rows, v1.2), oracle-B/decisions.tsv (732 rows, v1.2),
        vector-generator/vectors/v1.3/MANIFEST.csv, vector-generator/BATTERY-MAPPING.md (case mapping)
Output: merged/decisions_v13.tsv  (vektor_id, politika, kol, karar, A, B, kaynak, not)
        merged/SUMMARY.json
Rules (PR §2H items 7–10, BEFORE the freeze):
  7  accept-hybrid ⇔ the acceptance rests on the PQ evidence (rejection when PQ is removed). Under P0, if both signatures are valid,
     accept-classical (the example in the PR). Under L4 an acceptance is accept-hybrid; acceptance with the PQ signature only is accept-hybrid.
  8  K5 (additional signature with an unrecognised algorithm: T7*, T4*, T6, UNK04/05) carries no single oracle decision → 'B1-bayragi'
     (does not enter F_K/F_T; the target behaviour is classified with the L4-S/L4-Y rows).
  9  K8/K9 arm-independent flag: the rows in the composite arm do not enter the measurement ('kol-bagimsiz').
  10 V± only under GEC.
 COSE and L4c (new in v1.3): since the oracle decision depends on the case and not on the serialization (BATTERY-MAPPING
 §3 "COSE Kn" ↔ §1 "Kn"), every COSE vector takes the decision of its JOSE counterpart in the same case and arm. L4c-3 (old
 issuer, ES256 only): the quotation in BATTERY-MAPPING §4 (the old issuer's classically signed document is accepted)
 → accept-classical in IZIN-AX and the L4 family; accept-classical in IZIN-A; accept-classical in GEC.
 Final decision: A = B → that value; present in one oracle only → that value ('tek-oracle'); different → 'indeterminate'.
"""
import csv, io, json, os, re, hashlib
K = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(K, '..', '..')
rd = lambda p: list(csv.DictReader(io.open(p, encoding='utf-8'), delimiter='\t'))
A = {(r['vektor_id'], r['politika'], r['kol']): r for r in rd(os.path.join(K, '..', 'oracle-A', 'decisions.tsv'))}
B = {(r['vektor_id'], r['politika'], r['kol']): r for r in rd(os.path.join(K, '..', 'oracle-B', 'decisions.tsv'))}
MAN = {r['id']: r for r in csv.DictReader(io.open(os.path.join(D, 'vector-generator', 'vectors', 'v1.3', 'MANIFEST.csv'), encoding='utf-8'))}

K5 = re.compile(r'^(T7|T4|T6|UNK04|UNK05)')
def norm7(vid, pol, karar):
    """Item 7: under P0 the class of an acceptance is accept-classical (even if both signatures are valid)."""
    if pol == 'P0' and karar == 'accept-hybrid' and vid.startswith(('T1', 'T7', 'VC07', 'VC08', 'VC09')):
        return 'accept-classical'
    return karar

def birlestir(key):
    vid, pol, kol = key
    a, b = A.get(key), B.get(key)
    ka = norm7(vid, pol, a['karar']) if a else None
    kb = norm7(vid, pol, b['karar']) if b else None
    if K5.match(vid) and pol in ('L4', 'L4-S', 'L4-Y'):
        return 'B1-bayragi', ka, kb, 'madde-8'
    if vid.startswith(('X5C04', 'X5C07')) and kol == 'tedavi-composite':
        return 'kol-bagimsiz', ka, kb, 'madde-9'
    if ka and kb:
        if ka == kb: return ka, ka, kb, 'A=B'
        if 'indeterminate' in (ka, kb): return 'indeterminate', ka, kb, 'A|B belirsiz'
        return 'indeterminate', ka, kb, 'A≠B'
    return (ka or kb), ka, kb, 'tek-oracle'

# ---- v1.2 rows ----
rows = {}
for key in set(A) | set(B):
    rows[key] = birlestir(key)

# ---- COSE: case mapping ----
def jose_esi(cid):
    s = cid[len('COSE-'):]
    m = {'K1K_iki_gecerli': 'T1K_both_valid', 'K2K_X_bozuk': 'T2K_second_tampered', 'K3_X_soyuldu': 'T3_stripped_to_ES256',
         'K4K_yalniz_X': 'T5K_only_EdDSA', 'K5K_arti_kayitsiz': 'T7K_plus_kayitsiz',
         'K1P_iki_gecerli': 'T1P_both_valid', 'K2P_X_bozuk': 'T2P_second_tampered', 'K4P_yalniz_X': 'T5P_only_ML-DSA-65',
         'K5P_arti_kayitsiz': 'T7P_plus_kayitsiz', 'K1C_iki_gecerli': 'T1C_both_valid', 'K2C_X_bozuk': 'T2C_second_tampered',
         'K4C_yalniz_X': 'T5C_only_ML-DSA-65-ES256', 'K5C_arti_kayitsiz': 'T7C_plus_kayitsiz',
         'K6_composite_gecerli': 'CMP00_gecerli_referans', 'K7_ml_bileseni_bozuk': 'CMP01_ml_bileseni_bozuk',
         'K7_ecdsa_bileseni_bozuk': 'CMP02_ecdsa_bileseni_bozuk', 'K8_x5chain_karisik': 'X5C04', 'K9_x5chain_korumasiz': 'X5C07'}
    suf = ''
    for t in ('-SIRA-ters-ED25519', '-SIRA-ters', '-ED25519'):
        if s.endswith(t): s, suf = s[:-len(t)], t; break
    if s.startswith(('VPLUS_', 'VMINUS_', 'K10')):
        base = s
    else:
        base = m.get(s)
    if base is None: return None
    # X5C ids carry a prefix
    if base in ('X5C04', 'X5C07'):
        base = next((v for v in MAN if v.startswith(base)), base)
    return base + suf

cose_eksik = []
for cid, mr in MAN.items():
    if mr['aile'] != 'COSE': continue
    j = jose_esi(cid)
    src = [k for k in rows if k[0] == j] if j else []
    if not src:
        cose_eksik.append(cid); continue
    for (jv, pol, kol) in src:
        karar, ka, kb, kay = rows[(jv, pol, kol)]
        rows[(cid, pol, kol)] = (karar, ka, kb, f'COSE←{jv} ({kay})')

# ---- L4c-3: old issuer ----
for vid in ('L4C-JOSE_eski_ES256', 'L4C-COSE_eski_ES256'):
    for kol in ('tedavi-ML-DSA-65', 'tedavi-composite', 'kontrol-EdDSA'):
        for pol in ('GEC', 'IZIN-A', 'IZIN-AX', 'L4', 'L4-S', 'L4-Y'):
            rows[(vid, pol, kol)] = ('accept-classical', None, None, 'L4c-3 (BATARYA-ESLEME §4 alıntısı)')

out = os.path.join(K, 'decisions_v13.tsv')
with io.open(out, 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f, delimiter='\t'); w.writerow(['vektor_id', 'politika', 'kol', 'karar', 'A', 'B', 'kaynak'])
    for key in sorted(rows):
        karar, ka, kb, kay = rows[key]; w.writerow([*key, karar, ka or '', kb or '', kay])
from collections import Counter
oz = {'satir': len(rows), 'karar_dagilimi': Counter(r[0] for r in rows.values()),
      'kaynak_dagilimi': Counter(r[3].split(' ')[0] if not r[3].startswith('COSE') else 'COSE-esleme' for r in rows.values()),
      'cose_esi_bulunamayan': cose_eksik,
      'A_sha256': hashlib.sha256(open(os.path.join(K, '..', 'oracle-A', 'decisions.tsv'), 'rb').read()).hexdigest(),
      'B_sha256': hashlib.sha256(open(os.path.join(K, '..', 'oracle-B', 'decisions.tsv'), 'rb').read()).hexdigest()}
json.dump(oz, io.open(os.path.join(K, 'SUMMARY.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=dict)
print(json.dumps(oz, ensure_ascii=False, indent=1, default=dict))
