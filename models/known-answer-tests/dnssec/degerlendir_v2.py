# -*- coding: utf-8 -*-
"""Step 6 | evaluation of KAT-1 DNSSEC AFTER THE CORRECTION (v2) — derived mechanically from degerlendir.py
(only the path and label lines differ; the logic is the same). Tamarin: sonuc_v2/ (KAT1_DNSSEC_v2.spthy); ASP: first run
(sonuc/asp*.csv; ASP was not run again, the core was not touched). Output: sonuc_v2/KAT_OZET.{json,md}.
Original description: pass criterion from the run outputs (PR §4.19; MAPPING.md §1, §2.5, §2.6).
DOES NOT RUN anything; only reads. Input: sonuc/{asp,asp_mutasyon,tamarin,tamarin_mutasyon}.csv, sonuc/asp_ozet.json,
iyi_bicim/ozet.tsv, sonuc/alinti_denetimi.tsv. Output: sonuc/KAT_OZET.json, sonuc/KAT_OZET.md.
Pass (all of): ASP 100%; Tamarin 100% ('belirsiz', 'gecersiz_wf' or 'yok' => KALDI) and executable verified in every
run; ASP–Tamarin agreement 100% (SALDIRI<->falsified, YOK<->verified; K1-01…K1-15); every mutation flips at least one
of the listed cells in every engine where it is defined; core digest before = after = 45cbd0f.
Usage: python degerlendir.py (host or container)
"""
import csv, json, os, sys
from collections import defaultdict

KOK = os.path.dirname(os.path.abspath(__file__))
KAT = 'KAT-1 DNSSEC (düzeltme sonrası, v2)'
ESLE = {'SALDIRI': 'falsified', 'YOK': 'verified'}


def oku(ad, ayrac=','):
    yol = os.path.join(KOK, ad)
    if not os.path.exists(yol):
        return []
    with open(yol, encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f, delimiter=ayrac))


def main():
    asp, am = oku('sonuc/asp.csv'), oku('sonuc/asp_mutasyon.csv')
    tam, tm = oku('sonuc_v2/tamarin.csv'), oku('sonuc_v2/tamarin_mutasyon.csv')
    wf, al = oku('sonuc_v2/iyi_bicim/ozet.tsv', '\t'), oku('sonuc/alinti_denetimi.tsv', '\t')
    oz = json.load(open(os.path.join(KOK, 'sonuc', 'asp_ozet.json'), encoding='utf-8'))
    A = {r['hucre']: r['gozlenen'] for r in asp}
    T = {r['hucre']: r['gozlenen'] for r in tam}
    ortak = sorted(set(A) & set(T))
    ort_uyum = [h for h in ortak if ESLE.get(A[h]) == T[h]]
    kotu = [r['kosu'] for r in tam + tm if r['gozlenen'] in ('belirsiz', 'gecersiz_wf', 'yok')]
    ex = [r['kosu'] for r in tam + tm if r['executable'] != 'verified']
    # Strict flip criterion (KAT-SPEC §6 "must flip"): the mutated value equals the expected value AND differs from the observed
    # value of the unmutated base run. Base run: the same name with the 'MUTxx.' prefix removed.
    TA = {r['kosu']: r['gozlenen'] for r in asp}
    TT = {r['kosu']: r['gozlenen'] for r in tam}
    M = defaultdict(lambda: defaultdict(list))
    for r in am:
        temel = TA.get(r['kosu'].split('.', 1)[1])
        M[r['mutasyon']]['asp'].append(r['dondu'] == 'EVET' and temel is not None and temel != r['gozlenen'])
    for r in tm:
        temel = TT.get(r['kosu'].split('.', 1)[1])
        M[r['mutasyon']]['tamarin'].append(r['uyum'] == 'EVET' and temel is not None and temel != r['gozlenen'])
    mut = {m: {mot: any(v) for mot, v in d.items()} for m, d in sorted(M.items())}
    k = {'asp': (sum(r['uyum'] == 'EVET' for r in asp), len(asp)),
         'tamarin': (sum(r['uyum'] == 'EVET' for r in tam), len(tam)),
         'asp_tamarin': (len(ort_uyum), len(ortak)),
         'mutasyon': (sum(all(d.values()) for d in mut.values()), len(mut))}
    kosullar = {'asp_yuzde100': k['asp'][0] == k['asp'][1] > 0,
                'tamarin_yuzde100': k['tamarin'][0] == k['tamarin'][1] > 0 and not kotu,
                'executable_hepsi_verified': not ex,
                'iyi_bicim_uyari0': bool(wf) and all(w['iyi_bicim'] == 'EVET' and w['uyari_sayisi'] == '0' for w in wf),
                'asp_tamarin_yuzde100': k['asp_tamarin'][0] == k['asp_tamarin'][1] > 0,
                'mutasyon_yuzde100': k['mutasyon'][0] == k['mutasyon'][1] > 0,
                'cekirdek_degismedi': bool(oz.get('cekirdek_commit_45cbd0f_ile_ayni'))}
    karar = 'GEÇTİ' if all(kosullar.values()) else 'KALDI'
    alinti = (sum(a['bulundu'] != 'BULUNAMADI' for a in al), len(al))
    ozet = {'kat': KAT, 'karar_Vd': karar, 'kosullar': kosullar, 'sayilar': k, 'mutasyonlar': mut,
            'belirsiz_ya_da_gecersiz': kotu, 'executable_olmayan': ex, 'alinti_bulundu': alinti,
            'asp_tamarin_uyumsuz': [h for h in ortak if h not in ort_uyum],
            'asp_uyumsuz': [(r['hucre'], r['beklenen'], r['gozlenen']) for r in asp if r['uyum'] != 'EVET'],
            'tamarin_uyumsuz': [(r['hucre'], r['beklenen'], r['gozlenen']) for r in tam if r['uyum'] != 'EVET']}
    json.dump(ozet, open(os.path.join(KOK, 'sonuc_v2', 'KAT_OZET.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    s = ['## %s — %s' % (KAT, karar), '',
         '| Koşul | Sonuç |', '|---|---|',
         '| ASP hücreleri | %d/%d |' % k['asp'], '| Tamarin hücreleri | %d/%d |' % k['tamarin'],
         '| executable (her Tamarin koşusu) | %s |' % ('hepsi verified' if not ex else 'DEĞİL: ' + ', '.join(ex)),
         '| İyi biçimlilik (uyarı 0) | %s |' % ('evet' if kosullar['iyi_bicim_uyari0'] else 'HAYIR'),
         '| ASP–Tamarin uyumu | %d/%d |' % k['asp_tamarin'], '| Mutasyonlar (KAT-SPEC §6) | %d/%d |' % k['mutasyon'],
         '| Çekirdek özeti önce = sonra = 45cbd0f | %s |' % ('evet' if kosullar['cekirdek_degismedi'] else 'HAYIR'),
         '| Birebir alıntılar | %d/%d |' % alinti, '',
         '| Hücre | ASP beklenen | ASP gözlenen | Tamarin beklenen | Tamarin gözlenen |', '|---|---|---|---|---|']
    TB = {r['hucre']: r for r in tam}
    for r in asp:
        t = TB.get(r['hucre'], {})
        s.append('| %s | %s | %s | %s | %s |' % (r['hucre'], r['beklenen'], r['gozlenen'], t.get('beklenen', '–'),
                                                  t.get('gozlenen', '–')))
    s += ['', '| Mutasyon | Motor: döndü mü |', '|---|---|']
    for m, d in mut.items():
        s.append('| %s | %s |' % (m, ', '.join('%s: %s' % (mot, 'evet' if v else 'HAYIR') for mot, v in sorted(d.items()))))
    open(os.path.join(KOK, 'sonuc_v2', 'KAT_OZET.md'), 'w', encoding='utf-8').write('\n'.join(s) + '\n')
    print(json.dumps({'kat': KAT, 'karar_Vd': karar, 'kosullar': kosullar, 'sayilar': k}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
