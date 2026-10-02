# -*- coding: utf-8 -*-
"""Step 6 | KAT-3 S/MIME evaluation: pass criterion from the run outputs (PR §4.19; MAPPING.md §1, §4.4–§4.7).
DOES NOT RUN anything; only reads. Input: sonuc/{asp,asp_sondalar,asp_mutasyon,tamarin,tamarin_mutasyon,tamarin_ek}.csv,
sonuc/asp_ozet.json, iyi_bicim/ozet.tsv, sonuc/alinti_denetimi.tsv. Output: sonuc/KAT_OZET.json, sonuc/KAT_OZET.md.
Cells shared by ASP and Tamarin (MAPPING §4.6):
  KAT-3a: Tamarin MIXED <-> o4, PQ_ONLY <-> o1, HYBRID_KEM <-> o5; ASP value from the probe 'klasik' (only the classical key
          is broken; the threat model of Tamarin): E=1 <-> falsified, E=0 <-> verified.
  KAT-3b: V1–V6 'attack(qday=0)' <-> 'Tamarin:claims_unforgeability' (SALDIRI<->falsified, YOK<->verified).
Additional pass items of KAT-SPEC §4(d) (not in nsurum; reported separately): kat3a_fail empty; model_gap only o8.
Additional (not a gate): KAT-3b Tamarin with the ORIGINAL pilot model (with well-formedness warnings; MAPPING §4.5).
"""
import csv, json, os, sys
from collections import defaultdict

KOK = os.path.dirname(os.path.abspath(__file__))
KAT = 'KAT-3 S/MIME'
ESLE = {'SALDIRI': 'falsified', 'YOK': 'verified'}
ESLE3A = {'MIXED': 'o4', 'PQ_ONLY': 'o1', 'HYBRID_KEM': 'o5'}


def oku(ad, ayrac=','):
    yol = os.path.join(KOK, ad)
    if not os.path.exists(yol):
        return []
    with open(yol, encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f, delimiter=ayrac))


def main():
    asp, son, am = oku('sonuc/asp.csv'), oku('sonuc/asp_sondalar.csv'), oku('sonuc/asp_mutasyon.csv')
    tam, tm, te = oku('sonuc/tamarin.csv'), oku('sonuc/tamarin_mutasyon.csv'), oku('sonuc/tamarin_ek.csv')
    wf, al = oku('iyi_bicim/ozet.tsv', '\t'), oku('sonuc/alinti_denetimi.tsv', '\t')
    oz = json.load(open(os.path.join(KOK, 'sonuc', 'asp_ozet.json'), encoding='utf-8'))
    A = {(r['hucre'], r['sutun']): r['gozlenen'] for r in asp}
    T = {(r['hucre'], r['sutun']): r['gozlenen'] for r in tam}
    E = {(r['hucre'], r['sonda']): r['E'] for r in son}
    ortak = []
    for f, o in ESLE3A.items():
        if (o, 'klasik') in E and (f, 'Tamarin:cek_secrecy') in T:
            ortak.append(('%s<->%s' % (f, o), 'falsified' if E[(o, 'klasik')] == '1' else 'verified',
                          T[(f, 'Tamarin:cek_secrecy')]))
    for i in range(1, 7):
        v = 'V%d' % i
        if (v, 'attack(qday=0)') in A and (v, 'Tamarin:claims_unforgeability') in T:
            ortak.append((v, ESLE.get(A[(v, 'attack(qday=0)')]), T[(v, 'Tamarin:claims_unforgeability')]))
    ort_uyum = [o for o in ortak if o[1] == o[2]]
    kotu = [r['kosu'] for r in tam + tm if r['gozlenen'] in ('belirsiz', 'gecersiz_wf', 'yok')]
    ex = [r['kosu'] for r in tam + tm if r['executable'] != 'verified']
    # Strict flip criterion (KAT-SPEC §6 "must flip"): the mutated value equals the expected value AND differs from the observed
    # value of the unmutated base run. Base run: the same name with the 'MUTxx.' prefix removed (in ASP the probe run).
    def temel_asp(kosu, grup, sonda):
        r = next((x for x in son if x['kosu'] == kosu), None)
        if r is None:
            return None
        e = r['E'] == '1'
        return ('0' if e else '1') if grup == 'KAT-3a' else ('SALDIRI' if e else 'YOK')
    TT = {r['kosu']: r['gozlenen'] for r in tam}
    M = defaultdict(lambda: defaultdict(list))
    for r in am:
        temel = temel_asp(r['kosu'].split('.', 1)[1], 'KAT-3a' if r['temel'].startswith('o') else 'KAT-3b', r['sonda'])
        M[r['mutasyon']]['asp'].append(r['dondu'] == 'EVET' and temel is not None and temel != r['gozlenen'])
    for r in tm:
        temel = TT.get(r['kosu'].split('.', 1)[1])
        M[r['mutasyon']]['tamarin'].append(r['uyum'] == 'EVET' and temel is not None and temel != r['gozlenen'])
    mut = {m: {mot: any(v) for mot, v in d.items()} for m, d in sorted(M.items())}
    wf_kapi = [w for w in wf if not w['ilk_kosu'].startswith('EK.')]
    k = {'asp': (sum(r['uyum'] == 'EVET' for r in asp), len(asp)),
         'tamarin': (sum(r['uyum'] == 'EVET' for r in tam), len(tam)),
         'asp_tamarin': (len(ort_uyum), 9),
         'mutasyon': (sum(all(d.values()) for d in mut.values()), len(mut))}
    kosullar = {'asp_yuzde100': k['asp'][0] == k['asp'][1] > 0,
                'tamarin_yuzde100': k['tamarin'][0] == k['tamarin'][1] > 0 and not kotu,
                'executable_hepsi_verified': not ex,
                'iyi_bicim_uyari0': bool(wf_kapi) and all(w['iyi_bicim'] == 'EVET' and w['uyari_sayisi'] == '0' for w in wf_kapi),
                'asp_tamarin_yuzde100': k['asp_tamarin'][0] == k['asp_tamarin'][1],
                'mutasyon_yuzde100': k['mutasyon'][0] == k['mutasyon'][1] > 0,
                'cekirdek_degismedi': bool(oz.get('cekirdek_commit_45cbd0f_ile_ayni'))}
    ek_madde = {'kat3a_fail_bos': oz.get('kat3a_fail') == [], 'model_gap_yalniz_o8': oz.get('model_gap') == ['o8']}
    karar = 'GEÇTİ' if all(kosullar.values()) else 'KALDI'
    alinti = (sum(a['bulundu'] != 'BULUNAMADI' for a in al), len(al))
    ek = [(r['kosu'], r['beklenen'], r['gozlenen'], r['iyi_bicim']) for r in te]
    ozet = {'kat': KAT, 'karar_Vd': karar, 'kosullar': kosullar, 'kat_spec_ek_maddeler': ek_madde, 'sayilar': k,
            'mutasyonlar': mut, 'asp_tamarin': ortak, 'belirsiz_ya_da_gecersiz': kotu, 'executable_olmayan': ex,
            'alinti_bulundu': alinti,
            'asp_uyumsuz': [(r['hucre'], r['sutun'], r['beklenen'], r['gozlenen']) for r in asp if r['uyum'] != 'EVET'],
            'tamarin_uyumsuz': [(r['hucre'], r['beklenen'], r['gozlenen']) for r in tam if r['uyum'] != 'EVET'],
            'ek_pilot_asli_kapi_degil': ek}
    json.dump(ozet, open(os.path.join(KOK, 'sonuc', 'KAT_OZET.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    s = ['## %s — %s' % (KAT, karar), '', '| Koşul | Sonuç |', '|---|---|',
         '| ASP hücre değerleri (3a: 36, 3b: 18) | %d/%d |' % k['asp'], '| Tamarin hücreleri | %d/%d |' % k['tamarin'],
         '| executable (her Tamarin koşusu) | %s |' % ('hepsi verified' if not ex else 'DEĞİL: ' + ', '.join(ex)),
         '| İyi biçimlilik (uyarı 0; kapı modelleri) | %s |' % ('evet' if kosullar['iyi_bicim_uyari0'] else 'HAYIR'),
         '| ASP–Tamarin uyumu | %d/%d |' % k['asp_tamarin'], '| Mutasyonlar (KAT-SPEC §6) | %d/%d |' % k['mutasyon'],
         '| Çekirdek özeti önce = sonra = 45cbd0f | %s |' % ('evet' if kosullar['cekirdek_degismedi'] else 'HAYIR'),
         '| KAT-SPEC §4(d) ek: kat3a_fail boş / model_gap yalnız o8 | %s / %s |' % (
             'evet' if ek_madde['kat3a_fail_bos'] else 'HAYIR', 'evet' if ek_madde['model_gap_yalniz_o8'] else 'HAYIR'),
         '| Birebir alıntılar | %d/%d |' % alinti, '',
         '| Hücre | Sütun | Beklenen | Gözlenen | Dayanak |', '|---|---|---|---|---|']
    for r in asp:
        s.append('| %s | %s | %s | %s | %s |' % (r['hucre'], r['sutun'], r['beklenen'], r['gozlenen'], r['dayanak']))
    for r in tam:
        s.append('| %s | %s | %s | %s | Tamarin (%s; %s) |' % (r['hucre'], r['sutun'], r['beklenen'], r['gozlenen'],
                                                               r['bayraklar'], r['model']))
    s += ['', '| ASP–Tamarin ortak hücre | ASP (Tamarin diliyle) | Tamarin |', '|---|---|---|']
    s += ['| %s | %s | %s |' % o for o in ortak]
    s += ['', '| Mutasyon | Motor: döndü mü |', '|---|---|']
    for m, d in mut.items():
        s.append('| %s | %s |' % (m, ', '.join('%s: %s' % (mot, 'evet' if v else 'HAYIR') for mot, v in sorted(d.items()))))
    if ek:
        s += ['', 'Ek (kapı hücresi değil): pilot ASLI ile KAT-3b Tamarin (iyi biçimlilik uyarılı):', '',
              '| Koşu | Beklenen (nsurum) | Gözlenen (ham) | İyi biçimli |', '|---|---|---|---|']
        s += ['| %s | %s | %s | %s |' % e for e in ek]
    open(os.path.join(KOK, 'sonuc', 'KAT_OZET.md'), 'w', encoding='utf-8').write('\n'.join(s) + '\n')
    print(json.dumps({'kat': KAT, 'karar_Vd': karar, 'kosullar': kosullar, 'ek': ek_madde, 'sayilar': k}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
