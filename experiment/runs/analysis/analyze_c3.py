"""C3 analysis: adapter outputs -> four-valued decisions -> oracle comparison -> per-target variables -> statistics input.

Written and frozen before any measurement run. Definitions: pre-registration sections 3.7, 4.13-4.15, 6.3-6.11,
adapter contract sections 3.1 and 5, decisions in ../DECISIONS-PREFREEZE.md (D1-D7, D4 = amendment 10).

Inputs
  --runs DIR        measurement outputs <target>.r1.jsonl, <target>.r2.jsonl, <target>.r3.jsonl
  --oracle FILE     merged oracle (../../oracle/birlesik/karar_v14.tsv)
  --labels FILE     control labels (../CONTROL-LABELS.csv)
  --tk FILE         ML-DSA arm TK assignment (../TK-ASSIGNMENT.csv)
  --inventory DIR   ../../inventory (CERCEVE.csv for release dates)
  --evidence FILE   optional: targets whose "not expressible" verdict satisfies the evidence rule (section 4.14)
Outputs (in --out)
  decisions.csv     one row per (target, vector, policy, arm): decisions r1-r3, stable decision, oracle, match
  targets.csv       per-target variables with the reason for every null
  c3-input-primary.json, c3-input-secondary-mldsa.json   statistics input (schema c3-istat-girdi/1.0)
Usage: python analyze_c3.py --runs ../outputs/measurement --out . [paths default to the repository layout]
"""
import argparse, csv, json, os
from collections import defaultdict

H = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument('--runs', default=os.path.join(H, '..', 'outputs', 'measurement'))
ap.add_argument('--oracle', default=os.path.join(H, '..', '..', 'oracle', 'birlesik', 'karar_v14.tsv'))
ap.add_argument('--labels', default=os.path.join(H, '..', 'CONTROL-LABELS.csv'))
ap.add_argument('--tk', default=os.path.join(H, '..', 'TK-ASSIGNMENT.csv'))
ap.add_argument('--inventory', default=os.path.join(H, '..', '..', 'inventory'))
ap.add_argument('--evidence', default=os.path.join(H, 'evidence-rule.csv'))
ap.add_argument('--out', default=H)
ap.add_argument('--data-type', default='olcum', choices=['olcum', 'sentetik'])
A = ap.parse_args()

PQ_ALGS = {'ML-DSA-44', 'ML-DSA-65', 'ML-DSA-87', 'ML-DSA-44-ES256', 'ML-DSA-65-ES256', 'ML-DSA-87-ES384',
           'ML-DSA-44-Ed25519', 'ML-DSA-65-Ed25519', 'ML-DSA-87-Ed448'}
PILOT = {'JOSE-009', 'SDJWT-015',                                  # pilot P3 (pre-registration section 12.5)
         'JOSE-033', 'JOSE-034', 'JOSE-065', 'JOSE-083', 'JOSE-084'}  # second pilot, targets in n (section 12.5)
DELEGATES = {'SDJWT-001': 'COSE-001', 'SDJWT-021': 'JOSE-001'}       # amendment 8 item 16
NO_INTEGRITY = {'SDJWT-002'}                                        # decision D1
RUNS = ('r1', 'r2', 'r3')

# ---------------------------------------------------------------- 1. decisions (contract section 3.1)
def decision(row, tk_arm):
    s = row['sonuc_ham']
    if s in ('red', 'istisna') and row.get('kol', '').startswith('kontrol-') and row.get('hata_sinifi') == 'alg-desteklenmiyor':
        return 'desteklenmiyor'                                     # amendment 11: incidental rejection, not enforcement
    if s == 'kabul':
        pq = any(a.get('alg') in PQ_ALGS and a.get('sonuc') == 'gecerli' for a in row.get('dogrulanan_algoritmalar') or [])
        return 'accept-hybrid' if pq and tk_arm == 'TK1' else 'accept-classical'
    if s in ('red', 'istisna'):
        return 'reject'
    if s in ('zaman-asimi', 'cokme'):
        return 'indeterminate'
    return s                                                        # uygulanamaz | ifade-edilemedi

labels = {r['target']: r['control_label'] for r in csv.DictReader(open(A.labels, encoding='utf-8'))}
tk_mldsa = {r['target']: r['tk_mldsa_primary'] for r in csv.DictReader(open(A.tk, encoding='utf-8'))} if os.path.exists(A.tk) else {}
tk_mldsa_sens = {r['target']: r['tk_mldsa_sensitivity'] for r in csv.DictReader(open(A.tk, encoding='utf-8'))} if os.path.exists(A.tk) else {}
oracle = {(r['vektor_id'], r['politika'], r['kol']): r for r in csv.DictReader(open(A.oracle, encoding='utf-8'), delimiter='\t')}
evidence_ok = set()
if os.path.exists(A.evidence):
    evidence_ok = {r['target'] for r in csv.DictReader(open(A.evidence, encoding='utf-8')) if r.get('rule_satisfied') == '1'}

def tk_of(target, kol, sensitivity=False):
    if kol == 'tedavi-ML-DSA-65':
        return (tk_mldsa_sens if sensitivity else tk_mldsa).get(target, 'TK3')
    return 'TK3' if kol == 'tedavi-composite' else 'TK1'            # control arms carry no PQ component

targets = sorted({f.rsplit('.', 2)[0] for f in os.listdir(A.runs) if f.endswith('.jsonl')})
obs = {}                                                            # target -> {(vid, pol, kol): stable decision}
raw = {}                                                            # target -> {(vid, pol, kol): row of r1}
dec_rows = []
for t in targets:
    per = defaultdict(dict)
    for r in RUNS:
        p = os.path.join(A.runs, '%s.%s.jsonl' % (t, r))
        if not os.path.exists(p):
            continue
        for line in open(p, encoding='utf-8'):
            if line.strip():
                o = json.loads(line)
                k = (o['vektor_id'], o['politika'], o['kol'])
                per[k][r] = decision(o, tk_of(t, o['kol']))
                raw.setdefault(t, {})[k] = o
    st = {}
    for k, d in per.items():
        vals = [d.get(r) for r in RUNS]
        stable = vals[0] if len(set(vals)) == 1 and vals[0] is not None else 'kararsiz'
        st[k] = stable
        orc = oracle.get(k, {}).get('karar', '')
        match = '' if stable in ('uygulanamaz', 'ifade-edilemedi', 'kararsiz', 'indeterminate') or orc not in ('accept-hybrid', 'accept-classical', 'reject')             else 0 if stable == 'desteklenmiyor' else int(stable == orc)
        dec_rows.append({'target': t, 'vektor_id': k[0], 'politika': k[1], 'kol': k[2], 'r1': vals[0], 'r2': vals[1], 'r3': vals[2],
                         'decision': stable, 'oracle': orc, 'match': match})
    obs[t] = st

with open(os.path.join(A.out, 'decisions.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(dec_rows[0]) if dec_rows else ['target'])
    w.writeheader(); w.writerows(dec_rows)

# ---------------------------------------------------------------- 2. case vectors per arm
COSE = {'T1K_both_valid': 'COSE-K1K_iki_gecerli', 'T2K_second_tampered': 'COSE-K2K_X_bozuk', 'T3_stripped_to_ES256': 'COSE-K3_X_soyuldu',
        'T5K_only_EdDSA': 'COSE-K4K_yalniz_X', 'T7K_plus_kayitsiz': 'COSE-K5K_arti_kayitsiz', 'VPLUS_ES256': 'COSE-VPLUS_ES256',
        'VPLUS_EdDSA': 'COSE-VPLUS_EdDSA', 'K10K_alg-EdDSA_anahtar-ES256': 'COSE-K10K_alg-EdDSA_anahtar-ES256',
        'K10K_alg-ES256_anahtar-Ed25519': 'COSE-K10K_alg-ES256_anahtar-Ed25519', 'L4C-JOSE_eski_ES256': 'L4C-COSE_eski_ES256',
        'T1C_both_valid': 'COSE-K1C_iki_gecerli', 'T2C_second_tampered': 'COSE-K2C_X_bozuk', 'T5C_only_ML-DSA-65-ES256': 'COSE-K4C_yalniz_X',
        'T1P_both_valid': 'COSE-K1P_iki_gecerli', 'T2P_second_tampered': 'COSE-K2P_X_bozuk', 'T5P_only_ML-DSA-65': 'COSE-K4P_yalniz_X'}
X_SPECIFIC = {'T1K_both_valid', 'T2K_second_tampered', 'T5K_only_EdDSA', 'T7K_plus_kayitsiz', 'VPLUS_EdDSA',
              'K10K_alg-EdDSA_anahtar-ES256', 'K10K_alg-ES256_anahtar-Ed25519'}
SUFFIX = {'EdDSA': '', 'Ed25519': '-ED25519', 'ES384': '-ES384'}

def vid(t, base, label=None):
    v = COSE.get(base, base) if t.startswith('COSE') else base
    if label and base in X_SPECIFIC:
        v += SUFFIX[label]
    return v

def get(t, base, pol, kol, label=None):
    return obs[t].get((vid(t, base, label), pol, kol))

def ok(t, base, pol, kol, label=None):
    """1 = matches oracle, 0 = deviates, None = cannot be judged (with reason)."""
    v = vid(t, base, label)
    d = obs[t].get((v, pol, kol))
    o = oracle.get((v, pol, kol), {}).get('karar')
    if d is None:
        return None, 'olculmedi'
    if d == 'uygulanamaz':
        return None, 'uygulanamaz'
    if d == 'ifade-edilemedi':
        return 0, 'ifade-edilemedi'
    if d == 'desteklenmiyor':
        return 0, 'desteklenmiyor'                                  # amendment 11: never agrees with an oracle reject
    if d in ('kararsiz', 'indeterminate'):
        return None, 'kararsiz_3_tekrar'
    if o not in ('accept-hybrid', 'accept-classical', 'reject'):
        return None, 'oracle_uyusmazligi'
    return int(d == o), None

def all_ok(checks):
    vals = [c[0] for c in checks]
    reasons = [c[1] for c in checks if c[0] is None]
    if reasons:
        for r in ('kararsiz_3_tekrar', 'oracle_uyusmazligi', 'uygulanamaz', 'olculmedi'):
            if r in reasons:
                return None, r
    return int(all(v == 1 for v in vals)), None

# ---------------------------------------------------------------- 3. per-target variables
release = {}
cer = os.path.join(A.inventory, 'CERCEVE.csv')
if os.path.exists(cer):
    for r in csv.DictReader(open(cer, encoding='utf-8')):
        release[r['id']] = r.get('son_surum_tarihi') or None

def target_vars(t, secondary=False):
    lab = labels.get(t, '')
    kol_k = 'kontrol-' + lab if lab else None
    kol_t = 'tedavi-ML-DSA-65' if secondary else 'tedavi-composite'
    v = {'hedef_id': t, 'tabaka': t.split('-')[0], 'adaptor_gecersiz': 0, 'pilot': int(t in PILOT),
         'devralan': int(t in DELEGATES), 'devraldigi_hedef': DELEGATES.get(t), 'belirsiz_nedenleri': {}}
    rd = release.get(t)
    v['son_surum_tarihi'] = rd[:10] if rd else None
    v['surum_8725bis_sonrasi'] = (int(rd[:10] > '2026-08-21') if rd else None)
    if not lab:
        v.update({'adaptor_gecersiz': 1, 'adaptor_gecersiz_gerekce': 'no second classical algorithm passes the validity gate (amendment 10)'})
        for k in ('Y_L4', 'L_duzeyi', 'F_K', 'F_T', 'D_soy', 'B1', 'B2', 'B3', 'B4_ozel_kod', 'B5', 'B6'):
            v[k] = None
        v['B4_satir'] = None
        v['tk_sinifi'] = 'TK3'; v['l4_bicimi'] = 'L4c'
        return v
    v['kontrol_etiketi'] = lab
    v['tk_sinifi'] = tk_of(t, kol_t, sensitivity=False)
    multi = get(t, 'T1K_both_valid', 'L4', kol_k, lab) not in (None, 'uygulanamaz')
    v['l4_bicimi'] = 'L4m' if multi else 'L4c'
    # Y_L4 (section 4.13; contract section 5.2)
    if multi:
        y = all_ok([ok(t, b, 'L4', kol_k, lab) for b in ('T1K_both_valid', 'T2K_second_tampered', 'T3_stripped_to_ES256', 'T5K_only_EdDSA')])
    else:
        y = all_ok([ok(t, 'VPLUS_ES256', 'L4', kol_k), ok(t, 'VPLUS_EdDSA', 'L4', kol_k, lab), ok(t, 'L4C-JOSE_eski_ES256', 'L4', kol_k)])
    inexpressible = get(t, 'T1K_both_valid' if multi else 'VPLUS_ES256', 'L4', kol_k, lab) == 'ifade-edilemedi'
    if inexpressible and t not in evidence_ok:
        y = (None, 'kanit_kurali')                                   # section 4.14: verdict needs the evidence rule
    v['Y_L4'] = y[0]
    if y[0] is None:
        v['belirsiz_nedenleri']['Y_L4'] = y[1]
    # L ladder (descriptive)
    l1 = all_ok([ok(t, 'VPLUS_ES256', 'IZIN-A', kol_k), ok(t, 'VPLUS_EdDSA', 'IZIN-A', kol_k, lab),
                 ok(t, 'VPLUS_ES256', 'IZIN-AX', kol_k), ok(t, 'VPLUS_EdDSA', 'IZIN-AX', kol_k, lab)])[0]
    api = (raw.get(t, {}).get((vid(t, 'VPLUS_ES256'), 'IZIN-A', kol_k)) or {}).get('api_yolu', '') or ''
    per_call = l1 == 1 and 'register' not in api.lower() and 'genel kay' not in api.lower()
    k10 = all_ok([ok(t, 'K10K_alg-EdDSA_anahtar-ES256', 'IZIN-AX', kol_k, lab), ok(t, 'K10K_alg-ES256_anahtar-Ed25519', 'IZIN-AX', kol_k, lab)])[0]
    level = 0
    if l1 == 1:
        level = 2 if per_call else 1
    if level >= 1 and k10 == 1:
        level = 3
    if v['Y_L4'] == 1:
        level = 4
        # L5: the default configuration (P0 rows) already gives the L4 decisions on the L4 vectors
        if multi and all(get(t, b, 'P0', kol_k, lab) == oracle.get((vid(t, b, lab), 'L4', kol_k), {}).get('karar')
                         for b in ('T1K_both_valid', 'T2K_second_tampered', 'T3_stripped_to_ES256', 'T5K_only_EdDSA')):
            level = 5
    v['L_duzeyi'] = level if l1 is not None or v['Y_L4'] is not None else None
    if v['L_duzeyi'] is None:
        v['belirsiz_nedenleri']['L_duzeyi'] = 'kararsiz_3_tekrar'
    # F_K / F_T against the L4 rows (section 7.9, adapter contract section 9.4; descriptive after amendment 11)
    pol_best = 'L4'
    def fail(kol, bases, label):
        r = all_ok([ok(t, b, pol_best, kol, label) for b in bases])
        return (None, r[1]) if r[0] is None else (1 - r[0], None)
    fk = fail(kol_k, ('T1K_both_valid', 'T2K_second_tampered', 'T3_stripped_to_ES256'), lab)
    tb = ('T1P_both_valid', 'T2P_second_tampered', 'T3_stripped_to_ES256') if secondary else ('T1C_both_valid', 'T2C_second_tampered', 'T3_stripped_to_ES256')
    ft = fail(kol_t, tb, None)
    v['F_K'], v['F_T'] = fk[0], ft[0]
    if fk[0] is None: v['belirsiz_nedenleri']['F_K'] = fk[1]
    if ft[0] is None: v['belirsiz_nedenleri']['F_T'] = ft[1]
    # D_soy: default configuration accepts the stripped object (K3)
    d3 = get(t, 'T3_stripped_to_ES256', 'P0', kol_k)
    v['D_soy'] = (1 if d3 in ('accept-classical', 'accept-hybrid') else 0 if d3 == 'reject' else None)
    if v['D_soy'] is None: v['belirsiz_nedenleri']['D_soy'] = 'uygulanamaz' if d3 in (None, 'uygulanamaz') else 'kararsiz_3_tekrar'
    # B1: unknown additional algorithm (K5) under the L4 family
    b1 = None
    for pol in ('L4-S', 'L4-Y', 'L4'):
        d = get(t, 'T7K_plus_kayitsiz', pol, kol_k, lab)
        if d in ('accept-classical', 'accept-hybrid'):
            b1 = 'yok_sayma'; break
        if d == 'reject':
            cls = (raw.get(t, {}).get((vid(t, 'T7K_plus_kayitsiz', lab), pol, kol_k)) or {}).get('hata_sinifi') or ''
            b1 = 'red' if cls.startswith('alg-') or cls in ('imza-gecersiz', 'gerekli-kume-eksik') else 'dogrulama_duser'
            break
    v['B1'] = b1
    if b1 is None: v['belirsiz_nedenleri']['B1'] = 'uygulanamaz'
    # B2: path-class policy for mixed x5c (L4-YOL): not expressible by any target unless accepted rows show otherwise
    yol = [obs[t].get((x, 'L4-YOL', k)) for (x, p, k) in obs[t] if p == 'L4-YOL']
    v['B2'] = 1 if yol and all(d == 'reject' for d in yol) else 0 if yol else None
    if v['B2'] is None: v['belirsiz_nedenleri']['B2'] = 'uygulanamaz'
    # B3: unprotected x5c processed (X5C07/X5C08 accepted under GEC or L4)
    x5 = [d for (x, p, k), d in obs[t].items() if x.startswith(('X5C07', 'X5C08')) and p in ('GEC', 'L4')]
    v['B3'] = 1 if any(d in ('accept-classical', 'accept-hybrid') for d in x5) else 0 if any(d == 'reject' for d in x5) else None
    if v['B3'] is None: v['belirsiz_nedenleri']['B3'] = 'uygulanamaz'
    v['B4_ozel_kod'] = 0; v['B4_satir'] = None                         # no custom verification code in any adapter
    # B5: semantic class of the default configuration (P0 rows = library default)
    d1, d2, d3_, d7 = (get(t, b, 'P0', kol_k, lab) for b in ('T1K_both_valid', 'T2K_second_tampered', 'T3_stripped_to_ES256', 'T7K_plus_kayitsiz'))
    acc = lambda d: d in ('accept-classical', 'accept-hybrid')
    if None in (d1, d2, d3_) or 'uygulanamaz' in (d1, d2, d3_):
        v['B5'] = None; v['belirsiz_nedenleri']['B5'] = 'uygulanamaz'
    elif acc(d2):
        v['B5'] = 'en_az_biri_gecerli'
    elif d3_ == 'reject':
        v['B5'] = 'gerekli_kume'
    elif acc(d3_) and d7 == 'reject':
        v['B5'] = 'mevcut_tumu_gecerli'
    else:
        v['B5'] = 'diger'
    v['B6'] = int(any(d == 'uygulanamaz' for d in obs[t].values()))
    return v

def build(secondary):
    hs = [target_vars(t, secondary) for t in targets]
    for h in hs:
        if not h['belirsiz_nedenleri']:
            h['belirsiz_nedenleri'] = {}
        for k in ('adaptor_gecersiz_gerekce',):
            if h.get('adaptor_gecersiz') != 1:
                h.pop(k, None)
        if h.get('adaptor_gecersiz') == 1:
            h['belirsiz_nedenleri'] = {k: 'olculmedi' for k in ('Y_L4', 'L_duzeyi', 'F_K', 'F_T', 'D_soy', 'B1', 'B2', 'B3', 'B4_ozel_kod', 'B5', 'B6')}
            h.pop('kontrol_etiketi', None)
    return hs

def cases(hs):
    out = []
    for h in hs:
        if h['adaptor_gecersiz'] == 1:
            continue
        t, lab = h['hedef_id'], h['kontrol_etiketi']
        for (base, arm) in [(b, 'K') for b in ('T1K_both_valid', 'T2K_second_tampered', 'T3_stripped_to_ES256', 'T5K_only_EdDSA', 'VPLUS_ES256', 'VPLUS_EdDSA')] + \
                           [(b, 'T') for b in ('T1C_both_valid', 'T2C_second_tampered', 'T5C_only_ML-DSA-65-ES256')]:
            kol = 'kontrol-' + lab if arm == 'K' else 'tedavi-composite'
            m, why = ok(t, base, 'L4', kol, lab if arm == 'K' else None)
            if why in ('uygulanamaz', 'olculmedi'):
                continue
            out.append({'hedef_id': t, 'vaka_id': vid(t, base, lab if arm == 'K' else None), 'kol': arm,
                        'uyum': (None if m is None else int(m == 1)), 'belirsiz_neden': why if m is None else None})
    return out

for name, secondary in (('primary', False), ('secondary-mldsa', True)):
    hs = build(secondary)
    doc = {'sema_surumu': 'c3-istat-girdi/1.0', 'veri_turu': A.data_type,
           'aciklama': 'C3 measurement, battery v1.4, %s treatment arm' % ('ML-DSA-65 (secondary)' if secondary else 'composite (primary)'),
           'hedefler': hs, 'vakalar': cases(hs)}
    json.dump(doc, open(os.path.join(A.out, 'c3-input-%s.json' % name), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    if not secondary:
        cols = sorted({k for h in hs for k in h})
        with open(os.path.join(A.out, 'targets.csv'), 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            for h in hs:
                w.writerow({k: (json.dumps(v, ensure_ascii=False) if isinstance(v, dict) else v) for k, v in h.items()})
        y = [h['Y_L4'] for h in hs if h['adaptor_gecersiz'] == 0 and h['Y_L4'] is not None]
        print(json.dumps({'targets': len(hs), 'n_eff': len(y), 'X': sum(y)}, ensure_ascii=False))
