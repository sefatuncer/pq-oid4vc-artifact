# -*- coding: utf-8 -*-
"""Step 6 | KAT-1: first run (v1) and post-correction run (v2) SIDE BY SIDE (maintainers' decision 26.09.2026).
RUNS NOTHING; only reads: sonuc/{asp,asp_mutasyon,tamarin,tamarin_mutasyon}.csv, sonuc/KAT_OZET.json (v1),
sonuc_v2/{tamarin,tamarin_mutasyon}.csv, sonuc_v2/KAT_OZET.json (v2). Output: sonuc_v2/YANYANA.md (taken into RESULTS.md).
"""
import csv, json, os, sys

KOK = os.path.dirname(os.path.abspath(__file__))


def oku(ad):
    with open(os.path.join(KOK, ad), encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def main():
    asp = {r['hucre']: r for r in oku('sonuc/asp.csv')}
    t1 = {r['hucre']: r for r in oku('sonuc/tamarin.csv')}
    t2 = {r['hucre']: r for r in oku('sonuc_v2/tamarin.csv')}
    m1 = {r['kosu']: r for r in oku('sonuc/tamarin_mutasyon.csv')}
    m2 = {r['kosu']: r for r in oku('sonuc_v2/tamarin_mutasyon.csv')}
    am = {r['kosu']: r for r in oku('sonuc/asp_mutasyon.csv')}
    o1 = json.load(open(os.path.join(KOK, 'sonuc', 'KAT_OZET.json'), encoding='utf-8'))
    o2 = json.load(open(os.path.join(KOK, 'sonuc_v2', 'KAT_OZET.json'), encoding='utf-8'))
    s = ['## KAT-1 DNSSEC: ilk koşum ve düzeltme sonrası koşum (yan yana)', '',
         '**KAT kararı:**', '',
         '- ilk koşum (v1, `KAT1_DNSSEC.spthy`, commit `e4c1090`): **%s**' % o1['karar_Vd'],
         '- düzeltme sonrası (v2, `KAT1_DNSSEC_v2.spthy`; "sonuç görüldükten sonra düzeltme"): **%s**' % o2['karar_Vd'], '',
         '| Koşul | İlk koşum (v1) | Düzeltme sonrası (v2) |', '|---|---|---|']
    for ad, anahtar in (('ASP hücreleri', 'asp'), ('Tamarin hücreleri', 'tamarin'), ('ASP–Tamarin uyumu', 'asp_tamarin'),
                        ('Mutasyonlar (KAT-SPEC §6)', 'mutasyon')):
        s.append('| %s | %d/%d | %d/%d |' % ((ad,) + tuple(o1['sayilar'][anahtar]) + tuple(o2['sayilar'][anahtar])))
    for ad, anahtar in (('executable hepsi verified', 'executable_hepsi_verified'), ('İyi biçimlilik (uyarı 0)', 'iyi_bicim_uyari0'),
                        ('Çekirdek özeti önce = sonra = 45cbd0f', 'cekirdek_degismedi')):
        s.append('| %s | %s | %s |' % (ad, 'evet' if o1['kosullar'][anahtar] else 'HAYIR', 'evet' if o2['kosullar'][anahtar] else 'HAYIR'))
    s += ['', 'ASP ilk koşumdur; yeniden koşulmadı, `cekirdek.lp`\'ye dokunulmadı. v2 yalnız Tamarin tarafını değiştirir.', '',
          '| Hücre | ASP beklenen | ASP gözlenen | Tamarin beklenen | Tamarin ilk koşum (v1) | Tamarin düzeltme sonrası (v2) | v2 adım | v1→v2 |',
          '|---|---|---|---|---|---|---|---|']
    for h in sorted(asp):
        a, x, y = asp[h], t1.get(h, {}), t2.get(h, {})
        degis = 'aynı' if x.get('gozlenen') == y.get('gozlenen') else '**değişti**'
        s.append('| %s | %s | %s | %s | %s%s | %s%s | %s | %s |' % (
            h, a['beklenen'], a['gozlenen'], y.get('beklenen', x.get('beklenen', '–')),
            x.get('gozlenen', '–'), '' if x.get('uyum') == 'EVET' else ' ✗', y.get('gozlenen', '–'),
            '' if y.get('uyum') == 'EVET' else ' ✗', y.get('adim', '–'), degis))
    s += ['', '| Mutasyon koşusu | Beklenen | ASP (ilk koşum) | Tamarin v1 | Tamarin v2 | v2 temel hücreden farklı mı |',
          '|---|---|---|---|---|---|']
    for k in sorted(m2):
        r2, r1 = m2[k], m1.get(k, {})
        temel = t2.get(r2['temel'], {}).get('gozlenen')
        asp_k = am.get(k.replace('.tam', '.asp'), {})
        s.append('| %s | %s | %s | %s | %s | %s |' % (k, r2['beklenen'], asp_k.get('gozlenen', '–'), r1.get('gozlenen', '–'),
                                                      r2['gozlenen'], 'evet' if temel is not None and temel != r2['gozlenen'] else 'HAYIR'))
    s += ['', '| Mutasyon | İlk koşum (motor: döndü mü) | Düzeltme sonrası (motor: döndü mü) |', '|---|---|---|']
    for m in sorted(o2['mutasyonlar']):
        f = lambda d: ', '.join('%s: %s' % (mot, 'evet' if v else 'HAYIR') for mot, v in sorted(d.items()))
        s.append('| %s | %s | %s |' % (m, f(o1['mutasyonlar'].get(m, {})), f(o2['mutasyonlar'][m])))
    open(os.path.join(KOK, 'sonuc_v2', 'YANYANA.md'), 'w', encoding='utf-8').write('\n'.join(s) + '\n')
    print('\n'.join(s))
    return 0


if __name__ == '__main__':
    sys.exit(main())
