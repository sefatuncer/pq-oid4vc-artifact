# -*- coding: utf-8 -*-
"""Runs the query groups of the catalogue with ASP; writes every group to sorgular/sonuc/<group>.json.
Usage: ./calistir.sh sorgular/kos.py ana k a5 h
"""
import json, os, sys, time
from multiprocessing import Pool
from sorgular.ortak import asgari_kumeler, parametreler, pq_sayisi, kaydet_json, KOK
from sorgular import katalog


def _kos(q):
    prm = parametreler(**q['degisen'])
    kumeler, bilgi = asgari_kumeler(prm, q['hedefler'])
    return {'id': q['id'], 'grup': q['grup'], 'hedefler': q['hedefler'], 'degisen': q['degisen'],
            'etiket': q['etiket'], 'kumeler': [list(k) for k in kumeler], 'n': len(kumeler),
            'min_pq': min((pq_sayisi(k) for k in kumeler), default=None), 'bilgi': bilgi}


def main(gruplar):
    for g in gruplar:
        qs = list(katalog.GRUPLAR[g]())
        t0 = time.perf_counter()
        with Pool(processes=int(os.environ.get('ISCI', '10'))) as havuz:
            sonuc = havuz.map(_kos, qs, chunksize=4)
        duvar = time.perf_counter() - t0
        top_cozum = sum(r['bilgi']['ground_s'] + r['bilgi']['solve_s'] for r in sonuc)
        en_uzun = max(sonuc, key=lambda r: r['bilgi']['ground_s'] + r['bilgi']['solve_s'])
        ozet = {'grup': g, 'sorgu': len(sonuc), 'sat': sum(1 for r in sonuc if r['n'] > 0),
                'unsat': sum(1 for r in sonuc if r['n'] == 0), 'duvar_s': round(duvar, 2),
                'toplam_ground_solve_s': round(top_cozum, 2),
                'en_uzun': {'id': en_uzun['id'], 's': round(en_uzun['bilgi']['ground_s'] + en_uzun['bilgi']['solve_s'], 4)},
                'toplam_asgari_kume': sum(r['n'] for r in sonuc)}
        kaydet_json(os.path.join(KOK, 'sorgular', 'sonuc', g + '.json'), {'ozet': ozet, 'sorgular': sonuc})
        print(json.dumps(ozet, ensure_ascii=False))


if __name__ == '__main__':
    main(sys.argv[1:] or list(katalog.GRUPLAR))
