# -*- coding: utf-8 -*-
"""Exploratory run of the 675 primary queries under a budget of two broken keys (k = 2).
Added in the revision of 28.10.2026 and not part of the pre-registered catalogue: the paper
reported k = 1 and k = 3 only. The script runs the primary queries with k_sinir = k2 and compares
every query with the unbounded primary result and with the k = 1 and k = 3 deviations of the
OAT group, in the format of sonuc/analiz/oat.json. As a regression check it also reruns k = 1 and
k = 3 with the same code and compares them query by query with the stored OAT results.
Usage: ./calistir.sh sorgular/k2.py
Output: sorgular/sonuc/k2.json (all queries) and sorgular/sonuc/analiz/k2.json (summary)
"""
import json, os, time
from collections import Counter, defaultdict
from multiprocessing import Pool
from sorgular import katalog
from sorgular.kos import _kos
from sorgular.ortak import KOK, kaydet_json

SON = os.path.join(KOK, 'sorgular', 'sonuc')
QANAHTAR = ('hedef', 'faz', 'tau', 'capa', 'politika')


def qhucre(q):
    return tuple(q['etiket'][k] for k in QANAHTAR)


def aile(q):
    return sorted(tuple(k) for k in q['kumeler'])


def yukle(g):
    return json.load(open(os.path.join(SON, g + '.json'), encoding='utf-8'))['sorgular']


def k_sorgulari(ks):
    yield from katalog._Q('k2', ks, {'k_sinir': ks}, {'tasarim': 'k2', 'sapma': ks})


def karsilastir(yeni, temel):
    """Queries whose family of minimal sets differs, as in the OAT summary of analiz.py."""
    fark = [k for k in sorted(yeni) if aile(yeni[k]) != aile(temel[k])]
    return {'fark_hucre': len(fark),
            'sat_unsat': sum(1 for k in fark if temel[k]['n'] and not yeni[k]['n']),
            'unsat_sat': sum(1 for k in fark if not temel[k]['n'] and yeni[k]['n']),
            'hedef': dict(Counter(k[0] for k in fark)),
            'ornek': [list(k) for k in fark[:3]]}


def main():
    qs = list(k_sorgulari('k2'))
    assert len(qs) == 675
    # Regression check: k = 1 and k = 3 are rerun with the same code and must reproduce the stored OAT results.
    rq = list(k_sorgulari('k1')) + list(k_sorgulari('k3'))
    t0 = time.perf_counter()
    with Pool(processes=int(os.environ.get('ISCI', '10'))) as havuz:
        sonuc = havuz.map(_kos, qs, chunksize=4)
        duvar = time.perf_counter() - t0
        rsonuc = havuz.map(_kos, rq, chunksize=4)
    en_uzun = max(sonuc, key=lambda r: r['bilgi']['ground_s'] + r['bilgi']['solve_s'])
    ozet = {'grup': 'k2', 'sorgu': len(sonuc), 'sat': sum(1 for r in sonuc if r['n'] > 0),
            'unsat': sum(1 for r in sonuc if r['n'] == 0), 'duvar_s': round(duvar, 2),
            'en_uzun': {'id': en_uzun['id'],
                        's': round(en_uzun['bilgi']['ground_s'] + en_uzun['bilgi']['solve_s'], 4)},
            'toplam_asgari_kume': sum(r['n'] for r in sonuc),
            'senaryo_sayisi': sorted(Counter(r['bilgi'].get('n_senaryo') for r in sonuc).items())}
    kaydet_json(os.path.join(SON, 'k2.json'), {'ozet': ozet, 'sorgular': sonuc})

    k2 = {qhucre(r): r for r in sonuc}
    birincil = {qhucre(q): q for q in yukle('birincil')}
    og = defaultdict(dict)
    for q in yukle('oat'):
        if q['etiket']['sapma'] in ('k1', 'k3'):
            og[q['etiket']['sapma']][qhucre(q)] = q
    assert set(k2) == set(birincil) == set(og['k1']) == set(og['k3'])
    regresyon = {}
    for ks in ('k1', 'k3'):
        yeni = {qhucre(r): r for r in rsonuc if r['etiket']['sapma'] == ks}
        assert set(yeni) == set(og[ks])
        regresyon[ks] = {'sorgu': len(yeni), 'farkli': sum(1 for k in yeni if aile(yeni[k]) != aile(og[ks][k]))}
    cikti = {'ozet': ozet, 'regresyon_k1_k3': regresyon,
             'k2_birincile_gore': karsilastir(k2, birincil),
             'k1_birincile_gore': karsilastir(og['k1'], birincil),
             'k3_birincile_gore': karsilastir(og['k3'], birincil),
             'k2_k1e_gore': karsilastir(k2, og['k1']),
             'k2_k3e_gore': karsilastir(k2, og['k3'])}
    kaydet_json(os.path.join(SON, 'analiz', 'k2.json'), cikti)
    print(json.dumps(cikti, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
