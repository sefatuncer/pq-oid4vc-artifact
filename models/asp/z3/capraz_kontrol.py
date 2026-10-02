# -*- coding: utf-8 -*-
"""ASP ↔ z3: one-to-one comparison of the minimal sets in all query groups (pre-registration D2).
Input: sorgular/sonuc/<group>.json (ASP). Output: z3/sonuc/uyum_<group>.csv and z3/sonuc/uyum_ozet.json.
Usage: ./calistir.sh z3/capraz_kontrol.py ana k a5 h
"""
import csv, json, os, sys, time
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from z3_kodlama import asgari_kumeler_z3
from sorgular.ortak import parametreler, KOK


def _z3(q):
    prm = parametreler(**q['degisen'])
    kumeler, bilgi = asgari_kumeler_z3(prm, q['hedefler'])
    asp = sorted(tuple(k) for k in q['kumeler'])
    return {'id': q['id'], 'asp_n': len(asp), 'z3_n': len(kumeler), 'esit': asp == kumeler,
            'z3_s': bilgi['sure_s'], 'cegar': bilgi['cegar'],
            'sadece_asp': [list(k) for k in asp if k not in kumeler][:3],
            'sadece_z3': [list(k) for k in kumeler if k not in asp][:3]}


def main(gruplar):
    ozet_yol = os.path.join(KOK, 'z3', 'sonuc', 'uyum_ozet.json')
    ozet = json.load(open(ozet_yol, encoding='utf-8')) if os.path.exists(ozet_yol) else {}
    for g in gruplar:
        veri = json.load(open(os.path.join(KOK, 'sorgular', 'sonuc', g + '.json'), encoding='utf-8'))
        qs = veri['sorgular']
        t0 = time.perf_counter()
        with Pool(processes=int(os.environ.get('ISCI', '10'))) as havuz:
            sonuc = havuz.map(_z3, qs, chunksize=2)
        duvar = round(time.perf_counter() - t0, 2)
        yol = os.path.join(KOK, 'z3', 'sonuc', 'uyum_%s.csv' % g)
        os.makedirs(os.path.dirname(yol), exist_ok=True)
        with open(yol, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['id', 'asp_n', 'z3_n', 'esit', 'z3_s', 'cegar'])
            for r in sonuc:
                w.writerow([r['id'], r['asp_n'], r['z3_n'], 'EVET' if r['esit'] else 'HAYIR', r['z3_s'], r['cegar']])
        farklar = [r for r in sonuc if not r['esit']]
        ozet[g] = {'sorgu': len(sonuc), 'esit': len(sonuc) - len(farklar), 'fark': len(farklar),
                   'asgari_kume_asp': sum(r['asp_n'] for r in sonuc), 'asgari_kume_z3': sum(r['z3_n'] for r in sonuc),
                   'z3_duvar_s': duvar, 'z3_en_uzun_s': max(r['z3_s'] for r in sonuc),
                   'cegar_toplam': sum(r['cegar'] for r in sonuc), 'ilk_farklar': farklar[:5]}
        print(g, json.dumps({k: v for k, v in ozet[g].items() if k != 'ilk_farklar'}, ensure_ascii=False))
        for r in farklar[:5]:
            print('  FARK', r['id'], r['asp_n'], r['z3_n'], r['sadece_asp'][:1], r['sadece_z3'][:1])
    with open(ozet_yol, 'w', encoding='utf-8') as f:
        json.dump(ozet, f, ensure_ascii=False, indent=1, sort_keys=True)


if __name__ == '__main__':
    main(sys.argv[1:])
