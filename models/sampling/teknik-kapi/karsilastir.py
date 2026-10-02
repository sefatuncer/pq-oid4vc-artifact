# -*- coding: utf-8 -*-
"""
PQ-OID4VC | Technical gate (PR §2F) | AFTER the run: Tamarin verdict ↔ ASP prediction
==============================================================================
Input : tamarin_ham.csv (betik/calistir.sh), ceviri_plani.tsv, ../secim/secim.json, json/*.json
Output: sonuc.csv   satir_id, hedef, tur, asp_tahmini, tamarin_hukmu, lemma, sure_s, bellek, iyi_bicimlilik
        saglik.csv  `executable` per instance (honest acceptance reachable; the model is not empty)
        izler.csv   protocol rules and broken keys in the traces of falsified goal lemmas
        farklar.csv only if there is a disagreement: ASP witness and Tamarin trace side by side (NO CLASSIFICATION)
Rule (PR §2F item 1, P-16): agreement on the closed instances must be 100%; a difference is not classified and not corrected.
The gate count is made only over the 10 gate instances; the exploration instance is reported separately.
"""
import csv
import io
import json
import os

KOK = os.path.dirname(os.path.abspath(__file__))


def oku_csv(yol, ayirici=','):
    with io.open(yol, encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f, delimiter=ayirici))


def iz_kurallari(yol):
    """Extracts the protocol rules (excluding the adversary rules) and the broken keys from a JSON trace."""
    if not os.path.exists(yol):
        return '', ''
    d = json.load(io.open(yol, encoding='utf-8'))
    kurallar, kirik = [], []
    for g in d.get('graphs', []):
        for n in g.get('jgNodes', []):
            if n.get('jgnType') != 'isProtocolRule':
                continue
            ad = n.get('jgnLabel', '')
            kurallar.append(ad)
            for act in (n.get('jgnMetadata') or {}).get('jgnActs', []):
                if act.get('jgnFactName') == 'Broken':
                    kirik.append(act.get('jgnFactShow', '').replace('Broken( ', '').replace(' )', ''))
    return ' '.join(sorted(set(kurallar))), ' '.join(sorted(set(kirik)))


def main():
    s = json.load(io.open(os.path.join(KOK, '..', 'secim', 'secim.json'), encoding='utf-8'))
    ornekler = {o['satir_id']: ('kapi', o) for o in s['kapi_ornekleri']}
    ko = s['kesif_ornegi (kapı sayımına girmez)']
    ornekler[ko['satir_id']] = ('kesif', ko)
    plan = {r['satir_id']: r for r in oku_csv(os.path.join(KOK, 'ceviri_plani.tsv'), '\t')}
    ham = oku_csv(os.path.join(KOK, 'tamarin_ham.csv'))
    hedef_satir = {(r['satir_id'], r['lemma']): r for r in ham}

    sonuc, saglik, izler, farklar = [], [], [], []
    for sid in plan:
        gorev, o = ornekler[sid]
        lemma = plan[sid]['lemma']
        r = hedef_satir.get((sid, lemma))
        e = hedef_satir.get((sid, 'executable'))
        hukum = r['sonuc'] if r else 'yok'
        sonuc.append({'satir_id': sid, 'hedef': o['hedef'], 'tur': o['tur'], 'asp_tahmini': o['asp_tahmini'],
                      'tamarin_hukmu': hukum, 'lemma': lemma,
                      'sure_s': r['sure_s'] if r else 'NA', 'bellek': (r['bellek_MiB'] + ' MiB') if r else 'NA',
                      'iyi_bicimlilik': r['iyi_bicimlilik'] if r else 'NA'})
        saglik.append({'satir_id': sid, 'executable': e['sonuc'] if e else 'yok',
                       'adim': e['adim'] if e else 'NA', 'sure_s': e['sure_s'] if e else 'NA',
                       'bellek_MiB': e['bellek_MiB'] if e else 'NA'})
        kur, kir = ('', '')
        if hukum == 'falsified':
            kur, kir = iz_kurallari(os.path.join(KOK, 'json', '%s__%s.json' % (sid, lemma)))
            izler.append({'satir_id': sid, 'lemma': lemma, 'kirilan_anahtarlar': kir, 'iz_protokol_kurallari': kur})
        kapandi = hukum in ('verified', 'falsified')
        if kapandi and hukum != o['asp_tahmini']:
            farklar.append({'satir_id': sid, 'gorev': gorev, 'asp_tahmini': o['asp_tahmini'], 'tamarin_hukmu': hukum,
                            'asp_tanik_sahte_artefaktlar': ' '.join(o.get('tanik_sahte_artefaktlar', [])),
                            'asp_ihlal_edilen': ' '.join(o.get('ihlal_edilen', [])),
                            'tamarin_kirilan_anahtarlar': kir, 'tamarin_iz_protokol_kurallari': kur,
                            'ham_cikti': 'ham/%s__%s__b1.txt' % (sid, lemma)})

    def yaz(ad, satirlar, alanlar):
        with io.open(os.path.join(KOK, ad), 'w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=alanlar, lineterminator='\n')
            w.writeheader()
            w.writerows(satirlar)

    yaz('sonuc.csv', sonuc, ['satir_id', 'hedef', 'tur', 'asp_tahmini', 'tamarin_hukmu', 'lemma',
                             'sure_s', 'bellek', 'iyi_bicimlilik'])
    yaz('saglik.csv', saglik, ['satir_id', 'executable', 'adim', 'sure_s', 'bellek_MiB'])
    yaz('izler.csv', izler, ['satir_id', 'lemma', 'kirilan_anahtarlar', 'iz_protokol_kurallari'])
    fark_yolu = os.path.join(KOK, 'farklar.csv')
    if farklar:
        yaz('farklar.csv', farklar, list(farklar[0].keys()))
    elif os.path.exists(fark_yolu):
        os.remove(fark_yolu)

    kapi = [x for x in sonuc if ornekler[x['satir_id']][0] == 'kapi']
    kesif = [x for x in sonuc if ornekler[x['satir_id']][0] == 'kesif']
    kapanan = [x for x in kapi if x['tamarin_hukmu'] in ('verified', 'falsified')]
    uyumlu = [x for x in kapanan if x['tamarin_hukmu'] == x['asp_tahmini']]
    wf = [x for x in sonuc if x['iyi_bicimlilik'] != 'temiz']
    print('kapi ornegi: %d | kapanan: %d | uyumlu: %d | uyum: %s' % (
        len(kapi), len(kapanan), len(uyumlu),
        ('%.0f%%' % (100.0 * len(uyumlu) / len(kapanan))) if kapanan else 'NA'))
    for x in kesif:
        print('kesif ornegi (sayima girmez): %s asp=%s tamarin=%s' % (x['satir_id'], x['asp_tahmini'], x['tamarin_hukmu']))
    print('iyi bicimlilik uyarili kosum: %d | fark: %d | executable verified: %d/%d' % (
        len(wf), len(farklar), sum(1 for x in saglik if x['executable'] == 'verified'), len(saglik)))


if __name__ == '__main__':
    main()
