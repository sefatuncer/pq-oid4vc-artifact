# -*- coding: utf-8 -*-
"""
PQ-OID4VC | Step 7 | expected (anchor 8) ↔ observed comparison
=================================================================
Input : on_kayit_varyantlar.tsv (anchor 8; read only), sonuc/ozet.csv, sonuc/json/*.json
Output: sonuc/karsilastirma.csv  every (variant, lemma): expected, observed, agreement, ladder, duration, memory
        sonuc/beklenmeyen.csv    verdicts that do not agree + trace summary (protocol rules, broken keys)
        sonuc/izler.csv          trace summary for falsified all-traces lemmas and verified exists-trace lemmas
        sonuc/varyant_ozeti.csv  number of agreements per variant
Expectation rule (file header): the sanity lemmas not named in lemma_beklenen
(executable*, attack_needs_crqc*) are expected V. Any other lemma without an expectation is marked "kayitsiz".
NO classification is made: an unexpected verdict is a finding; the model is not changed.
"""
import csv
import io
import json
import os
import sys

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KOSULAN = {'mekanizma', 'kosul', 'tasiyici', 'ablasyon', '3b', '3a'}


def beklentiler():
    satirlar = {}
    with io.open(os.path.join(KOK, 'on_kayit_varyantlar.tsv'), encoding='utf-8') as f:
        for ln in f:
            ln = ln.rstrip('\n')
            if not ln or ln.startswith('#'):
                continue
            k = ln.split('\t')
            if len(k) != 7 or k[2] not in KOSULAN:
                continue
            bek = {}
            for x in k[6].split(';'):
                if '=' in x:
                    a, b = x.split('=', 1)
                    bek[a.strip()] = b.strip()
            satirlar[k[1]] = {'kural': k[0], 'rol': k[2], 'dosya': k[3], 'bayraklar': k[4], 'bek': bek}
    return satirlar


def iz_ozeti(yol):
    if not os.path.exists(yol):
        return '', ''
    try:
        d = json.load(io.open(yol, encoding='utf-8'))
    except ValueError:
        return '', ''
    kurallar, kirik = set(), set()
    for g in d.get('graphs', []):
        for n in g.get('jgNodes', []):
            if n.get('jgnType') != 'isProtocolRule':
                continue
            kurallar.add(n.get('jgnLabel', ''))
            for act in (n.get('jgnMetadata') or {}).get('jgnActs', []):
                if act.get('jgnFactName') == 'Broken':
                    kirik.add(act.get('jgnFactShow', '').replace('Broken( ', '').replace(' )', ''))
    return ' '.join(sorted(kurallar)), ' '.join(sorted(kirik))


def main():
    bek = beklentiler()
    with io.open(os.path.join(KOK, 'sonuc', 'ozet.csv'), encoding='utf-8', newline='') as f:
        gozlem = list(csv.DictReader(f))
    kars, beklenmeyen, izler = [], [], []
    vozet = {}
    for r in gozlem:
        v, l = r['varyant'], r['lemma']
        b = bek.get(v)
        if b is None:
            continue
        e = b['bek'].get(l)
        if e is None and (l.startswith('executable') or l.startswith('attack_needs_crqc')):
            e = 'V'
        g = {'verified': 'V', 'falsified': 'F'}.get(r['sonuc'], r['sonuc'])
        if e is None:
            uyum = 'kayitsiz'
        elif g not in ('V', 'F'):
            uyum = 'kapanmadi' if r['sonuc'] in ('kapanmadi', 'timeout', 'incomplete') else r['sonuc']
        else:
            uyum = 'evet' if g == e else 'HAYIR'
        satir = {'kural': b['kural'], 'varyant': v, 'rol': b['rol'], 'dosya': b['dosya'], 'bayraklar': b['bayraklar'],
                 'lemma': l, 'beklenen': e or '-', 'gozlenen': g, 'uyum': uyum, 'adim': r['adim'],
                 'sure_s': r['sure_s'], 'bellek_MiB': r['bellek_MiB'], 'merdiven': r['merdiven_basamagi'],
                 'iyi_bicimlilik': r['iyi_bicimlilik']}
        kars.append(satir)
        vo = vozet.setdefault(v, {'kural': b['kural'], 'varyant': v, 'rol': b['rol'], 'lemma': 0, 'uyum': 0,
                                  'hayir': 0, 'kapanmadi': 0, 'kayitsiz': 0})
        vo['lemma'] += 1
        vo['uyum'] += uyum == 'evet'
        vo['hayir'] += uyum == 'HAYIR'
        vo['kapanmadi'] += uyum not in ('evet', 'HAYIR', 'kayitsiz')
        vo['kayitsiz'] += uyum == 'kayitsiz'
        jyol = os.path.join(KOK, 'sonuc', 'json', '%s__%s.json' % (v, l))
        if g in ('V', 'F'):
            kur, kir = iz_ozeti(jyol)
            if kur:
                izler.append({'varyant': v, 'lemma': l, 'gozlenen': g, 'kirilan_anahtarlar': kir,
                              'iz_protokol_kurallari': kur})
        if uyum == 'HAYIR':
            kur, kir = iz_ozeti(jyol)
            beklenmeyen.append(dict(satir, kirilan_anahtarlar=kir, iz_protokol_kurallari=kur,
                                    ham='sonuc/ham/%s__%s__b%s.txt' % (v, l, r['merdiven_basamagi'])))

    def yaz(ad, satirlar, alanlar):
        with io.open(os.path.join(KOK, 'sonuc', ad), 'w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=alanlar, lineterminator='\n')
            w.writeheader()
            w.writerows(satirlar)

    alan = ['kural', 'varyant', 'rol', 'dosya', 'bayraklar', 'lemma', 'beklenen', 'gozlenen', 'uyum', 'adim',
            'sure_s', 'bellek_MiB', 'merdiven', 'iyi_bicimlilik']
    yaz('karsilastirma.csv', kars, alan)
    yaz('beklenmeyen.csv', beklenmeyen, alan + ['kirilan_anahtarlar', 'iz_protokol_kurallari', 'ham'])
    yaz('izler.csv', izler, ['varyant', 'lemma', 'gozlenen', 'kirilan_anahtarlar', 'iz_protokol_kurallari'])
    yaz('varyant_ozeti.csv', list(vozet.values()),
        ['kural', 'varyant', 'rol', 'lemma', 'uyum', 'hayir', 'kapanmadi', 'kayitsiz'])
    kosulacak = len(bek)
    tamam = sum(1 for v in bek if v in vozet)
    toplam = len(kars)
    print('varyant: %d/%d | lemma koşumu: %d | uyum: %d | HAYIR: %d | kapanmadı/diğer: %d | kayıtsız: %d' % (
        tamam, kosulacak, toplam, sum(x['uyum'] == 'evet' for x in kars), sum(x['uyum'] == 'HAYIR' for x in kars),
        sum(x['uyum'] not in ('evet', 'HAYIR', 'kayitsiz') for x in kars), sum(x['uyum'] == 'kayitsiz' for x in kars)))
    for x in beklenmeyen:
        print('  BEKLENMEYEN: %s %s beklenen=%s gozlenen=%s' % (x['varyant'], x['lemma'], x['beklenen'], x['gozlenen']))


if __name__ == '__main__':
    main()
