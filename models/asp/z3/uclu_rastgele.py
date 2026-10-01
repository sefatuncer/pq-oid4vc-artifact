# -*- coding: utf-8 -*-
"""Ön kayıt D2 ek denetimi: sorgu sınıfı başına 1000 rastgele yapılandırmada ASP, z3 ve bağımsız
Python (Jacobi) sabit-nokta değerlendiricisinin üç yönlü uyumu. Tohum 20260928 (Ek C).
Karşılaştırılan: ihlal edilen hedefler kümesi (g1..g4, tum, g5, g2i) ve sahte artefakt kümesi.
Rastgele: bütün kategorik parametreler (tam alan), sayısal parametreler (ızgaralardan), kırılma kipi
(k sınırsız | S1 | rastgele kırık anahtar kümesi), PQ ataması ve beklenti taşıma (tasi) seçimi.
"""
import json, os, random, sys, time
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from yapi import Yapi, olgu
from z3_kodlama import degerlendir_z3
from py_degerlendirici import degerlendir_py
from sorgular.ortak import (parametreler, degerlendir, KOK, TAU_GENIS, TAU_DUYARLILIK, PENCERE_IZGARA)

TOHUM = 20260928
SINIFLAR = ['g1', 'g2', 'g3', 'g4', 'tum', 'g5', 'g2i']
ANA = ['g1', 'g2', 'g3', 'g4']


def alanlar():
    d = {}
    for p, v in olgu()['param_alan']:
        d.setdefault(p, []).append(v)
    return d


def rastgele_yapilandirma(rng, sinif, alan):
    kat = {p: rng.choice(sorted(vs)) for p, vs in sorted(alan.items())}
    kip = rng.choice(['tum', 'bos', 'ozel'])
    if kip == 'tum':
        kat['saldirgan'], kat['k_sinir'] = 's2', 'sinirsiz'
    elif kip == 'bos':
        kat['saldirgan'], kat['k_sinir'] = 's1', 'sinirsiz'
    else:
        kat['saldirgan'], kat['k_sinir'] = 's2', 'k1'
    say = {'tau': rng.choice(sorted(set(TAU_GENIS) | {v for vs in TAU_DUYARLILIK.values() for v in vs})),
           'saat_payi': rng.choice([0, 60, 300, 600]),
           'kimlik_gecerlilik': rng.choice(PENCERE_IZGARA),
           'durum_ttl': rng.choice(PENCERE_IZGARA),
           'kbjwt_iat': rng.choice([60, 300, 600]),
           'w_kok': rng.choice(PENCERE_IZGARA), 'w_ca': rng.choice(PENCERE_IZGARA),
           'w_ihracci': rng.choice(PENCERE_IZGARA), 'w_rp': rng.choice(PENCERE_IZGARA),
           'w_tls': rng.choice(PENCERE_IZGARA), 'w_ka': rng.choice(PENCERE_IZGARA),
           'w_wia': rng.choice([3600, 86400])}
    prm = parametreler(**kat, **say)
    Y = Yapi(prm)
    pq_at, ta_at = Y.karar_atomlari()
    pq = [a for a in pq_at if rng.random() < 0.5]
    tasi = [ct for ct in ta_at if rng.random() < 0.5]
    kirik = None
    if kip == 'ozel':
        kirik = [k for k in Y.anahtarlar() if rng.random() < 0.3]
    if sinif in ANA:
        g5k = [sinif]
    elif sinif in ('tum', 'g5'):
        g5k = list(ANA)
    else:
        g5k = []
    return {'sinif': sinif, 'kat': kat, 'say': say, 'kip': kip, 'pq': pq, 'tasi': [list(x) for x in tasi],
            'kirik': kirik, 'g5k': g5k}


def _asp_ad(k):
    return k if isinstance(k, str) else 'alt(%s)' % k[1]


def _degerlendir(c):
    prm = parametreler(**c['kat'], **c['say'])
    tasi = [tuple(x) for x in c['tasi']]
    kirik = None if c['kirik'] is None else [k if isinstance(k, str) else tuple(k) for k in c['kirik']]
    # ASP
    if c['kip'] == 'ozel':
        a = degerlendir(prm, c['pq'], tasi, hedefler=ANA, g5_kapsam=c['g5k'],
                        ozel_kirik=[_asp_ad(k) for k in kirik])
    else:
        a = degerlendir(prm, c['pq'], tasi, hedefler=ANA, g5_kapsam=c['g5k'])
    a_ihl = {g for (_, g) in a['ihlal']}
    a_sah = {x for (_, x) in a['sahte']}
    # z3
    z = degerlendir_z3(prm, c['pq'], tasi, hedefler=ANA, kirik=(set(kirik) if kirik is not None else None),
                       g5_kapsam=c['g5k'])
    # Python (Jacobi)
    p = degerlendir_py(prm, c['pq'], tasi, hedefler=ANA, kirik=(set(kirik) if kirik is not None else None),
                       g5_kapsam=c['g5k'])
    esit = (a_ihl == z['ihlal'] == p['ihlal']) and (a_sah == z['sahte'] == p['sahte'])
    return {'sinif': c['sinif'], 'kip': c['kip'], 'esit': esit, 'asp': sorted(a_ihl), 'z3': sorted(z['ihlal']),
            'py': sorted(p['ihlal']), 'sahte_farki': sorted(a_sah ^ z['sahte']) + sorted(a_sah ^ p['sahte']),
            'hedef_ihlal': c['sinif'] in a_ihl, 'tur': p['tur'], 'yapilandirma': c if not esit else None}


def main(n=1000):
    rng = random.Random(TOHUM)
    alan = alanlar()
    yap = [rastgele_yapilandirma(rng, s, alan) for s in SINIFLAR for _ in range(n)]
    t0 = time.perf_counter()
    with Pool(processes=int(os.environ.get('ISCI', '10'))) as havuz:
        sonuc = havuz.map(_degerlendir, yap, chunksize=8)
    duvar = round(time.perf_counter() - t0, 2)
    ozet = {'tohum': TOHUM, 'yapilandirma': len(sonuc), 'esit': sum(r['esit'] for r in sonuc), 'duvar_s': duvar,
            'en_cok_jacobi_turu': max(r['tur'] for r in sonuc), 'siniflar': {}}
    for s in SINIFLAR:
        rs = [r for r in sonuc if r['sinif'] == s]
        ozet['siniflar'][s] = {'n': len(rs), 'esit': sum(r['esit'] for r in rs),
                               'hedef_ihlal_orani': round(sum(r['hedef_ihlal'] for r in rs) / len(rs), 3),
                               'kip': {k: sum(1 for r in rs if r['kip'] == k) for k in ('tum', 'bos', 'ozel')}}
    farklar = [r for r in sonuc if not r['esit']]
    ozet['ilk_farklar'] = farklar[:5]
    with open(os.path.join(KOK, 'z3', 'sonuc', 'uclu_rastgele.json'), 'w', encoding='utf-8') as f:
        json.dump(ozet, f, ensure_ascii=False, indent=1, sort_keys=True)
    print(json.dumps({k: v for k, v in ozet.items() if k != 'ilk_farklar'}, ensure_ascii=False))
    for r in farklar[:5]:
        print('FARK', r['sinif'], r['kip'], r['asp'], r['z3'], r['py'], r['sahte_farki'])


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 1000)
