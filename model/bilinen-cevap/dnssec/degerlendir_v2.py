# -*- coding: utf-8 -*-
"""Adım 6 | KAT-1 DNSSEC DÜZELTME SONRASI (v2) değerlendirmesi — degerlendir.py'den mekanik olarak türetildi
(yalnız yol ve etiket satırları farklı; mantık aynı). Tamarin: sonuc_v2/ (KAT1_DNSSEC_v2.spthy); ASP: ilk koşum
(sonuc/asp*.csv; ASP yeniden koşulmadı, çekirdeğe dokunulmadı). Çıktı: sonuc_v2/KAT_OZET.{json,md}.
Özgün açıklama: koşum çıktılarından geçme ölçütü (ÖK §4.19; ESLEME.md §1, §2.5, §2.6).
KOŞU YAPMAZ; yalnız okur. Girdi: sonuc/{asp,asp_mutasyon,tamarin,tamarin_mutasyon}.csv, sonuc/asp_ozet.json,
iyi_bicim/ozet.tsv, sonuc/alinti_denetimi.tsv. Çıktı: sonuc/KAT_OZET.json, sonuc/KAT_OZET.md.
Geçme (hepsi): ASP %100; Tamarin %100 ('belirsiz', 'gecersiz_wf' ya da 'yok' => KALDI) ve her koşuda executable
verified; ASP–Tamarin uyumu %100 (SALDIRI<->falsified, YOK<->verified; K1-01…K1-15); her mutasyon tanımlı
olduğu her motorda listelenen hücrelerden en az birini döndürür; çekirdek özeti önce = sonra = 45cbd0f.
Kullanım: python degerlendir.py (host ya da konteyner)
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
    # Katı dönme ölçütü (KAT-SPEC §6 "dönmeli"): mutasyonlu değer beklenen değerde VE mutasyonsuz temel koşunun
    # gözlenen değerinden farklı. Temel koşu: aynı adın 'MUTxx.' öneki atılmış hâli.
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
