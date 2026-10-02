# -*- coding: utf-8 -*-
"""Single source of the numbers in REPORT.md: collects the summary numbers from all result files.
Output: sorgular/sonuc/rapor_sayilari.json. Usage: ./calistir.sh sorgular/rapor_sayilari.py
"""
import json, os
from collections import Counter, defaultdict
from sorgular.ortak import KOK

SON = os.path.join(KOK, 'sorgular', 'sonuc')


def j(p):
    return json.load(open(os.path.join(KOK, p), encoding='utf-8'))


def main():
    out = {}
    gruplar = ['birincil', 'h1', 'h2', 'h5', 'h4', 'cab', 'oat', 'tau', 'a5', 'h']
    asp = {g: j('sorgular/sonuc/%s.json' % g)['ozet'] for g in gruplar}
    uy = j('z3/sonuc/uyum_ozet.json')
    out['asp'] = asp
    out['asp_toplam'] = {'sorgu': sum(a['sorgu'] for a in asp.values()), 'sat': sum(a['sat'] for a in asp.values()),
                         'unsat': sum(a['unsat'] for a in asp.values()),
                         'asgari_kume': sum(a['toplam_asgari_kume'] for a in asp.values()),
                         'duvar_s': round(sum(a['duvar_s'] for a in asp.values()), 1),
                         'ground_solve_cpu_s': round(sum(a['toplam_ground_solve_s'] for a in asp.values()), 1),
                         'en_uzun_sorgu': max((a['en_uzun'] for a in asp.values()), key=lambda x: x['s'])}
    out['z3'] = {g: {k: uy[g][k] for k in ('sorgu', 'esit', 'fark', 'asgari_kume_asp', 'asgari_kume_z3', 'z3_duvar_s',
                                          'z3_en_uzun_s', 'cegar_toplam')} for g in gruplar}
    out['z3_toplam'] = {'sorgu': sum(uy[g]['sorgu'] for g in gruplar), 'esit': sum(uy[g]['esit'] for g in gruplar),
                        'asgari_kume': sum(uy[g]['asgari_kume_z3'] for g in gruplar),
                        'cegar': sum(uy[g]['cegar_toplam'] for g in gruplar)}
    out['uclu_rastgele'] = {k: v for k, v in j('z3/sonuc/uclu_rastgele.json').items() if k != 'ilk_farklar'}
    out['tamarin44'] = j('regresyon/sonuc/tamarin_esdegerlik.json')['ozet']
    out['p2'] = j('regresyon/sonuc/p2_regresyon.json')['ozet']
    st = j('sorgular/sonuc/stratejiler.json')
    out['strateji'] = {'taslak_sha256': st['taslak_sha256'], 'degerlendirme': st['degerlendirme'],
                       'uclu_esit_degerlendirilen': sum(1 for r in st['sonuc'] if r['strateji'] != 'S7' and r['uclu_esit']),
                       'olcut': st['olcut'], 'sorular': st['onceden_kayitli_sorular']}
    h4 = j('sorgular/sonuc/h4_karsilastirma.json')
    out['h4'] = {'ozet': h4['ozet'], 'aday_2a': [{k: r[k] for k in ('hucre', 'sinif', 'fark', 'S5_dugum', 'S7_min_dugum')}
                                                 for r in h4['aday_2a']]}
    out['siralar'] = j('sorgular/sonuc/siralar.json')['ozet']
    out['disa_aktarim'] = j('sampling/disa_aktarim_ozeti.json')
    out['analiz'] = j('sorgular/sonuc/analiz/ozet.json')
    # A1 requirement matrix (from the primary frame): missing node -> number of rows and the goals that fail
    a1 = defaultdict(lambda: {'satir': 0, 'dusen': Counter()})
    for satir in open(os.path.join(KOK, 'sampling', 'cerceve.jsonl'), encoding='utf-8'):
        r = json.loads(satir)
        if r['tur'] != 'bir-eksik':
            continue
        for kay in r['kaynaklar'][:1]:
            e = kay['eksik']
            anah = '%s|%s' % (r['hedef'], e if e.startswith('pq(') else 'tasi(...)')
            a1[anah]['satir'] += 1
            for g in r['ihlal_edilen']:
                a1[anah]['dusen'][g] += 1
    out['a1'] = {k: {'satir': v['satir'], 'dusen': dict(v['dusen'])} for k, v in sorted(a1.items())}
    json.dump(out, open(os.path.join(SON, 'rapor_sayilari.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps({k: out[k] for k in ('asp_toplam', 'z3_toplam', 'tamarin44', 'p2', 'siralar')}, ensure_ascii=False,
                     indent=1))
    print(json.dumps(out['a1'], ensure_ascii=False))


if __name__ == '__main__':
    main()
