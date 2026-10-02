# -*- coding: utf-8 -*-
"""Step 6 | KAT-2 X.509 hybrid evaluation: pass criterion from the run outputs (PR §4.19; MAPPING.md §1, §3.5, §3.6).
DOES NOT RUN anything; only reads. Input: sonuc/{asp,asp_mutasyon,tamarin,tamarin_mutasyon,tamarin_ek}.csv, sonuc/asp_ozet.json,
iyi_bicim/ozet.tsv, sonuc/alinti_denetimi.tsv. Output: sonuc/KAT_OZET.json, sonuc/KAT_OZET.md.
Cells shared by ASP and Tamarin (MAPPING §3.5): K2b-01/02/03/06/07 'ASP' <-> 'Tamarin:cert_authentic' (SALDIRI<->falsified,
YOK<->verified); K2d-01/02/03 'ASP:karar' <-> 'Tamarin' (no_silent_promotion; accept_classical<->falsified,
reject<->verified, accept_hybrid<->verified). Additional (not a gate): sensitivity lemmas (ek_tamarin.tsv).
"""
import csv, json, os, sys
from collections import defaultdict

KOK = os.path.dirname(os.path.abspath(__file__))
KAT = 'KAT-2 X.509 hibrit'
ORTAK = [(('K2b-%02d' % i, 'ASP'), ('K2b-%02d' % i, 'Tamarin:cert_authentic'),
          {'SALDIRI': 'falsified', 'YOK': 'verified'}) for i in (1, 2, 3, 6, 7)] + \
        [(('K2d-%02d' % i, 'ASP:karar'), ('K2d-%02d' % i, 'Tamarin'),
          {'accept_classical': 'falsified', 'reject': 'verified', 'accept_hybrid': 'verified'}) for i in (1, 2, 3)]


def oku(ad, ayrac=','):
    yol = os.path.join(KOK, ad)
    if not os.path.exists(yol):
        return []
    with open(yol, encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f, delimiter=ayrac))


def main():
    asp, am = oku('sonuc/asp.csv'), oku('sonuc/asp_mutasyon.csv')
    tam, tm, te = oku('sonuc/tamarin.csv'), oku('sonuc/tamarin_mutasyon.csv'), oku('sonuc/tamarin_ek.csv')
    wf, al = oku('iyi_bicim/ozet.tsv', '\t'), oku('sonuc/alinti_denetimi.tsv', '\t')
    oz = json.load(open(os.path.join(KOK, 'sonuc', 'asp_ozet.json'), encoding='utf-8'))
    A = {(r['hucre'], r['sutun']): r['gozlenen'] for r in asp}
    T = {(r['hucre'], r['sutun']): r['gozlenen'] for r in tam}
    ortak = [(a, t, e) for a, t, e in ORTAK if a in A and t in T]
    ort_uyum = [a for a, t, e in ortak if e.get(A[a]) == T[t]]
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
    wf_kapi = [w for w in wf if not w['ilk_kosu'].startswith('EK.')]
    k = {'asp': (sum(r['uyum'] == 'EVET' for r in asp), len(asp)),
         'tamarin': (sum(r['uyum'] == 'EVET' for r in tam), len(tam)),
         'asp_tamarin': (len(ort_uyum), len(ORTAK)),
         'mutasyon': (sum(all(d.values()) for d in mut.values()), len(mut))}
    kosullar = {'asp_yuzde100': k['asp'][0] == k['asp'][1] > 0,
                'tamarin_yuzde100': k['tamarin'][0] == k['tamarin'][1] > 0 and not kotu,
                'executable_hepsi_verified': not ex,
                'iyi_bicim_uyari0': bool(wf_kapi) and all(w['iyi_bicim'] == 'EVET' and w['uyari_sayisi'] == '0' for w in wf_kapi),
                'asp_tamarin_yuzde100': k['asp_tamarin'][0] == k['asp_tamarin'][1] > 0,
                'mutasyon_yuzde100': k['mutasyon'][0] == k['mutasyon'][1] > 0,
                'cekirdek_degismedi': bool(oz.get('cekirdek_commit_45cbd0f_ile_ayni'))}
    karar = 'GEÇTİ' if all(kosullar.values()) else 'KALDI'
    alinti = (sum(a['bulundu'] != 'BULUNAMADI' for a in al), len(al))
    ek = [(r['kosu'], r['beklenen'], r['gozlenen'], r['iyi_bicim']) for r in te]
    ozet = {'kat': KAT, 'karar_Vd': karar, 'kosullar': kosullar, 'sayilar': k, 'mutasyonlar': mut,
            'belirsiz_ya_da_gecersiz': kotu, 'executable_olmayan': ex, 'alinti_bulundu': alinti,
            'asp_tamarin_uyumsuz': [a for a, t, e in ortak if a not in ort_uyum],
            'asp_uyumsuz': [(r['hucre'], r['sutun'], r['beklenen'], r['gozlenen']) for r in asp if r['uyum'] != 'EVET'],
            'tamarin_uyumsuz': [(r['hucre'], r['beklenen'], r['gozlenen']) for r in tam if r['uyum'] != 'EVET'],
            'ek_duyarlilik_kapi_degil': ek}
    json.dump(ozet, open(os.path.join(KOK, 'sonuc', 'KAT_OZET.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    s = ['## %s — %s' % (KAT, karar), '', '| Koşul | Sonuç |', '|---|---|',
         '| ASP hücreleri | %d/%d |' % k['asp'], '| Tamarin hücreleri | %d/%d |' % k['tamarin'],
         '| executable (her Tamarin koşusu) | %s |' % ('hepsi verified' if not ex else 'DEĞİL: ' + ', '.join(ex)),
         '| İyi biçimlilik (uyarı 0) | %s |' % ('evet' if kosullar['iyi_bicim_uyari0'] else 'HAYIR'),
         '| ASP–Tamarin uyumu | %d/%d |' % k['asp_tamarin'], '| Mutasyonlar (KAT-SPEC §6) | %d/%d |' % k['mutasyon'],
         '| Çekirdek özeti önce = sonra = 45cbd0f | %s |' % ('evet' if kosullar['cekirdek_degismedi'] else 'HAYIR'),
         '| Birebir alıntılar | %d/%d |' % alinti, '',
         '| Hücre | Sütun | Beklenen | Gözlenen | Çekirdek dayanağı |', '|---|---|---|---|---|']
    for r in asp:
        s.append('| %s | %s | %s | %s | %s |' % (r['hucre'], r['sutun'], r['beklenen'], r['gozlenen'], r['cekirdek_dayanagi']))
    for r in tam:
        s.append('| %s | %s | %s | %s | Tamarin (%s) |' % (r['hucre'], r['sutun'], r['beklenen'], r['gozlenen'], r['bayraklar']))
    s += ['', '| Mutasyon | Motor: döndü mü |', '|---|---|']
    for m, d in mut.items():
        s.append('| %s | %s |' % (m, ', '.join('%s: %s' % (mot, 'evet' if v else 'HAYIR') for mot, v in sorted(d.items()))))
    if ek:
        s += ['', 'Ek (kapı hücresi değil; KAT-SPEC §3(d) duyarlılık lemmaları):', '',
              '| Koşu | Beklenen (KAT-SPEC) | Gözlenen | İyi biçimli |', '|---|---|---|---|']
        s += ['| %s | %s | %s | %s |' % e for e in ek]
    open(os.path.join(KOK, 'sonuc', 'KAT_OZET.md'), 'w', encoding='utf-8').write('\n'.join(s) + '\n')
    print(json.dumps({'kat': KAT, 'karar_Vd': karar, 'kosullar': kosullar, 'sayilar': k}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
