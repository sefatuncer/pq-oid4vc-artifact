# -*- coding: utf-8 -*-
"""
PQ-OID4VC | Adım 9 kalanı (yürütücü, 01.10.2026) | v1.3 için birleşik oracle
==============================================================================
Girdi : oracle-A/karar.tsv (858 satır, v1.2), oracle-B/karar.tsv (732 satır, v1.2),
        uretec/vektorler/v1.3/MANIFEST.csv, uretec/BATARYA-ESLEME.md (vaka eşlemesi)
Çıktı : birlesik/karar_v13.tsv  (vektor_id, politika, kol, karar, A, B, kaynak, not)
        birlesik/OZET.json
Kurallar (ÖK §2H madde 7–10, dondurmadan ÖNCE):
  7  accept-hybrid ⇔ kabul PQ kanıtına dayanıyor (PQ kaldırılınca red). P0'da iki imza da geçerliyse
     accept-classical (ÖK'deki örnek). L4'te kabul accept-hybrid; yalnız PQ imzayla kabul accept-hybrid.
  8  K5 (tanınmayan algoritmalı ek imza: T7*, T4*, T6, UNK04/05) tek oracle kararı taşımaz → 'B1-bayragi'
     (F_K/F_T'ye girmez; hedef davranışı L4-S/L4-Y satırlarıyla sınıflanır).
  9  K8/K9 kol-bağımsız bayrak: composite kolundaki satırlar ölçüme girmez ('kol-bagimsiz').
  10 V± yalnız GEC altında.
 COSE ve L4c (v1.3'te yeni): oracle kararı serileştirmeye değil vakaya bağlı olduğundan (BATARYA-ESLEME
 §3 "COSE Kn" ↔ §1 "Kn"), her COSE vektörü aynı vaka ve koldaki JOSE eşinin kararını alır. L4c-3 (eski
 ihraççı, yalnız ES256): BATARYA-ESLEME §4'teki alıntı ("eski ihraççının klasik imzalı belgesi kabul edilir")
 → IZIN-AX ve L4 ailesinde accept-classical; IZIN-A'da accept-classical; GEC'de accept-classical.
 Son karar: A = B → o değer; tek oracle'da varsa → o değer ('tek-oracle'); farklıysa → 'indeterminate'.
"""
import csv, io, json, os, re, hashlib
K = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(K, '..', '..')
rd = lambda p: list(csv.DictReader(io.open(p, encoding='utf-8'), delimiter='\t'))
A = {(r['vektor_id'], r['politika'], r['kol']): r for r in rd(os.path.join(K, '..', 'oracle-A', 'karar.tsv'))}
B = {(r['vektor_id'], r['politika'], r['kol']): r for r in rd(os.path.join(K, '..', 'oracle-B', 'karar.tsv'))}
MAN = {r['id']: r for r in csv.DictReader(io.open(os.path.join(D, 'uretec', 'vektorler', 'v1.3', 'MANIFEST.csv'), encoding='utf-8'))}

K5 = re.compile(r'^(T7|T4|T6|UNK04|UNK05)')
def norm7(vid, pol, karar):
    """Madde 7: P0'da kabulün sınıfı accept-classical (iki imza da geçerli olsa bile)."""
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

# ---- v1.2 satırları ----
rows = {}
for key in set(A) | set(B):
    rows[key] = birlestir(key)

# ---- COSE: vaka eşlemesi ----
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
    # X5C kimlikleri öneklidir
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

# ---- L4c-3: eski ihraççı ----
for vid in ('L4C-JOSE_eski_ES256', 'L4C-COSE_eski_ES256'):
    for kol in ('tedavi-ML-DSA-65', 'tedavi-composite', 'kontrol-EdDSA'):
        for pol in ('GEC', 'IZIN-A', 'IZIN-AX', 'L4', 'L4-S', 'L4-Y'):
            rows[(vid, pol, kol)] = ('accept-classical', None, None, 'L4c-3 (BATARYA-ESLEME §4 alıntısı)')

out = os.path.join(K, 'karar_v13.tsv')
with io.open(out, 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f, delimiter='\t'); w.writerow(['vektor_id', 'politika', 'kol', 'karar', 'A', 'B', 'kaynak'])
    for key in sorted(rows):
        karar, ka, kb, kay = rows[key]; w.writerow([*key, karar, ka or '', kb or '', kay])
from collections import Counter
oz = {'satir': len(rows), 'karar_dagilimi': Counter(r[0] for r in rows.values()),
      'kaynak_dagilimi': Counter(r[3].split(' ')[0] if not r[3].startswith('COSE') else 'COSE-esleme' for r in rows.values()),
      'cose_esi_bulunamayan': cose_eksik,
      'A_sha256': hashlib.sha256(open(os.path.join(K, '..', 'oracle-A', 'karar.tsv'), 'rb').read()).hexdigest(),
      'B_sha256': hashlib.sha256(open(os.path.join(K, '..', 'oracle-B', 'karar.tsv'), 'rb').read()).hexdigest()}
json.dump(oz, io.open(os.path.join(K, 'OZET.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=dict)
print(json.dumps(oz, ensure_ascii=False, indent=1, default=dict))
