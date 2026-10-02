# -*- coding: utf-8 -*-
"""
PQ-OID4VC | Step 8 | comparison tables (from the script only; the ASP outputs were regenerated on 01.10.2026,
identical except for the duration fields).
Input : models/asp/sorgular/sonuc/{stratejiler,birincil,h1,a5,rapor_sayilari}.json,
        models/asp/sorgular/stratejiler_taslak.json (SHA-256 11b05877…; 25.09.2026 12:34Z, before the comparison)
Output: m1-m5.csv, pareto.png/.pdf, A2-politika.csv, H4-adil-duyarlilik.csv, A1-gereklilik.json,
        sayilar.json (for the report and the paper)
Usage: python models/comparison/adim8.py
"""
import csv, hashlib, io, itertools, json, os
from collections import Counter, defaultdict

K = os.path.dirname(os.path.abspath(__file__))
S = os.path.join(K, '..', 'asp', 'sorgular', 'sonuc')
L = lambda f: json.load(io.open(os.path.join(S, f), encoding='utf-8'))
out = {}

# ---- strategies: assignment and M1–M5 ----
taslak_yol = os.path.join(K, '..', 'asp', 'sorgular', 'stratejiler_taslak.json')
out['stratejiler_taslak_sha256'] = hashlib.sha256(open(taslak_yol, 'rb').read()).hexdigest()
st = L('stratejiler.json')
# The ASP run recorded the SHA-256 of the pre-run strategy draft (11b05877...). The free-text field `_aciklama`
# was later edited for wording only, so the assignment itself is checked with a canonical hash of every
# non-underscore field, computed from the pre-run file.
TASLAK_KANONIK = 'bc66d7ee0b9466c13842abc8b5d87548d2108af1ce27b02c1111154baea9f249'
taslak = json.load(io.open(taslak_yol, encoding='utf-8'))
kanonik = hashlib.sha256(json.dumps({k: v for k, v in taslak.items() if not k.startswith('_')}, sort_keys=True,
                                    ensure_ascii=False).encode('utf-8')).hexdigest()
assert st['taslak_sha256'].startswith('11b05877') and kanonik == TASLAK_KANONIK, 'strategy assignment changed'
out['stratejiler_taslak_kanonik_sha256'] = kanonik
rows = []
for key, v in sorted(st['olcut'].items()):
    s, w = key.split('|')
    m2 = v['M2']
    g = lambda ph, key, alt: m2[ph].get(key, m2[ph].get(alt, ''))
    rows.append(dict(strateji=s, webpki=w, M1=v['M1'], G5_saglanan=v.get('G5_saglanan'),
                     M2_f1=g('f1', 'dugum', 'max'), M2_f1_agirlikli=g('f1', 'agirlikli', 'agirlikli_max'),
                     M2_f3=g('f3', 'dugum', 'max'), M3_vekil=v.get('M3_vekil'), M4_yapisal=v.get('M4_yapisal'), M5=v.get('M5')))
with io.open(os.path.join(K, 'm1-m5.csv'), 'w', encoding='utf-8', newline='') as f:
    w_ = csv.DictWriter(f, fieldnames=rows[0].keys()); w_.writeheader(); w_.writerows(rows)
out['onceden_kayitli_sorular'] = st['onceden_kayitli_sorular']
out['h4_ozet'] = st['h4_ozet']
out['M1'] = {f"{r['strateji']}|{r['webpki']}": r['M1'] for r in rows}

# ---- Pareto (Φ1-weighted M2 against M1 cl) ----
try:
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    pts = [(r['strateji'], int(str(r['M1']).split('/')[0]), r['M2_f1_agirlikli']) for r in rows
           if r['webpki'] == 'cl' and isinstance(r['M2_f1_agirlikli'], (int, float))]
    fig, ax = plt.subplots(figsize=(4.2, 3.0))
    for n, m1, m2 in pts:
        ax.scatter(m2, m1, s=18, color='#1f5fa8' if n not in ('S7',) else '#c26a1b')
        ax.annotate(n, (m2, m1), textcoords='offset points', xytext=(3, 3), fontsize=7)
    ax.set_xlabel('M2: migrated node classes, Φ1 (LOTL-weighted)'); ax.set_ylabel('M1: cells secured (of 36)')
    ax.grid(alpha=.3); fig.tight_layout()
    for ext in ('png', 'pdf'): fig.savefig(os.path.join(K, f'pareto.{ext}'), dpi=200)
    out['pareto'] = 'pareto.png'
except Exception as e:
    out['pareto'] = f'cizilmedi: {e}'

# ---- A2: policy steps (primary; τ × anchor = 9 cells) ----
b = L('birincil.json')['sorgular']
a2 = defaultdict(lambda: [0, 0])
for q in b:
    e = q['etiket']; k = (e['hedef'], e['faz'], e['politika'])
    a2[k][1] += 1; a2[k][0] += 1 if q['n'] > 0 else 0
with io.open(os.path.join(K, 'A2-politika.csv'), 'w', encoding='utf-8', newline='') as f:
    f.write('hedef,faz,politika,SAT,hucre\n')
    for (h, ph, p), (s_, n) in sorted(a2.items()): f.write(f'{h},{ph},{p},{s_},{n}\n')
out['A2'] = {f'{h}|{ph}|{p}': f'{s_}/{n}' for (h, ph, p), (s_, n) in sorted(a2.items())}

# ---- H4 fair sensitivity (K-4): unnecessary root migrations relative to the union over the goal vector ----
# WebPKI PQ cells (H1 design, basic channel variant) and primary (WebPKI classical), P4, taze/sabit/onbellek.
KOK = {'a01', 'a02'}
h1 = L('h1.json')['sorgular']
def zorunlu(sorgular):
    """A root is mandatory only if it is in ALL minimal sets of a goal. Because of upward closure, if one minimal set
    without the root is chosen per goal, their union satisfies all goals."""
    z = set()
    for q in sorgular:
        kes = None
        for k in q['kumeler']:
            ks = {a[3:-1] for a in k if a.startswith('pq(')}
            kes = ks if kes is None else kes & ks
        z |= (kes or set())
    return z
grp = defaultdict(list)
for q in h1:
    e, d = q['etiket'], q['degisen']
    if e['politika'] != 'p4' or set(d) - {'capa', 'faz', 'politika', 'tau', 'webpki'}:
        continue   # only the basic channel variant (only WebPKI changed)
    grp[(e['webpki'], e['faz'], e['tau'], e['capa'])].append(q)
for q in b:
    e = q['etiket']
    if e['politika'] == 'p4': grp[('cl-birincil', e['faz'], e['tau'], e['capa'])].append(q)
hr = []
for (w, ph, t, c), qs in sorted(grp.items()):
    sat = [q for q in qs if q['n'] > 0]
    u = zorunlu(sat)
    hr.append(dict(webpki=w, faz=ph, tau=t, capa=c, sat_hedef=len(sat), gerekli_kokler=' '.join(sorted(KOK & u)),
                   gereksiz_kokler=' '.join(sorted(KOK - u)) if sat else ''))
with io.open(os.path.join(K, 'H4-adil-duyarlilik.csv'), 'w', encoding='utf-8', newline='') as f:
    w_ = csv.DictWriter(f, fieldnames=hr[0].keys()); w_.writeheader(); w_.writerows(hr)
cnt = Counter((r['webpki'], bool(r['gereksiz_kokler'])) for r in hr if r['sat_hedef'])
out['H4_adil'] = {f'{w}|kok_gereksiz={g}': n for (w, g), n in sorted(cnt.items())}

# ---- A1 ----
rs = L('rapor_sayilari.json')
out['A1'] = rs.get('a1', 'yok')
json.dump(rs.get('a1', {}), io.open(os.path.join(K, 'A1-gereklilik.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

json.dump(out, io.open(os.path.join(K, 'sayilar.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps({k: out[k] for k in ('onceden_kayitli_sorular', 'H4_adil', 'pareto')}, ensure_ascii=False, indent=1))
