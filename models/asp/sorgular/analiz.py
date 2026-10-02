# -*- coding: utf-8 -*-
"""Result tables (from the ASP outputs; produced by script, not transcribed by hand).
Input: sorgular/sonuc/<group>.json. Output: sorgular/sonuc/analiz/*.csv, *.json, *.md
Usage: ./calistir.sh sorgular/analiz.py
"""
import csv, json, os, re, itertools
from collections import defaultdict, Counter
from sorgular.ortak import KOK, TAU_NOMINAL, GUN

SON = os.path.join(KOK, 'sorgular', 'sonuc')
CIK = os.path.join(SON, 'analiz')
os.makedirs(CIK, exist_ok=True)
M2_AGIRLIK = {'a02': 107}
CEKILEN = ['a01', 'a02', 'a05', 'a06', 'a08', 'ejvi', 'ecrl']        # H1: pulled / transport-only nodes
AKTARILAN = ['a03', 'a04', 'a07', 'a09a', 'a09b', 'a10', 'a11', 'a12']
QANAHTAR = ('hedef', 'faz', 'tau', 'capa', 'politika')


def yukle(g):
    return json.load(open(os.path.join(SON, g + '.json'), encoding='utf-8'))['sorgular']


def dugumler(kume):
    return tuple(sorted(a[3:-1] for a in kume if a.startswith('pq(')))


def tasilar(kume):
    return tuple(sorted(a for a in kume if a.startswith('tasi(')))


def m2(kume):
    d = dugumler(kume)
    return sum(M2_AGIRLIK.get(x, 1) for x in d)


def aile(q):
    return sorted(tuple(k) for k in q['kumeler'])


def qhucre(q):
    return tuple(q['etiket'][k] for k in QANAHTAR)


def md_tablo(basliklar, satirlar):
    s = '| ' + ' | '.join(basliklar) + ' |\n|' + '---|' * len(basliklar) + '\n'
    for r in satirlar:
        s += '| ' + ' | '.join(str(x) for x in r) + ' |\n'
    return s


def gerekli_ve_olasi(q):
    """Nodes that occur in every minimal set of a cell (required) and in at least one (possible)."""
    ks = [set(dugumler(k)) for k in q['kumeler']]
    if not ks:
        return None, None
    return set.intersection(*ks), set.union(*ks)


def main():
    rapor = {}
    birincil = {qhucre(q): q for q in yukle('birincil')}

    # ---------------------------------------------------------------- 1. primary table
    with open(os.path.join(CIK, 'birincil.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(list(QANAHTAR) + ['n_asgari', 'min_dugum', 'min_m2_agirlikli', 'gerekli_dugumler', 'asgari_kumeler'])
        for k in sorted(birincil):
            q = birincil[k]
            if q['n']:
                ger, _ = gerekli_ve_olasi(q)
                w.writerow(list(k) + [q['n'], min(len(dugumler(x)) for x in q['kumeler']),
                                      min(m2(x) for x in q['kumeler']), ' '.join(sorted(ger)),
                                      ' || '.join(' '.join(dugumler(x) + tasilar(x)) for x in q['kumeler'])])
            else:
                w.writerow(list(k) + [0, '', '', '', 'UNSAT'])
    # goal × phase × policy summary (over τ and anchor)
    ozet = defaultdict(lambda: Counter())
    for k, q in birincil.items():
        h, fz, t, c, p = k
        ozet[(h, fz, p)]['sat' if q['n'] else 'unsat'] += 1
    rapor['birincil_sat'] = sum(1 for q in birincil.values() if q['n'])
    rapor['birincil_unsat'] = sum(1 for q in birincil.values() if not q['n'])
    rapor['birincil_kume'] = sum(q['n'] for q in birincil.values())
    satirlar = []
    for h in ['g1', 'g2', 'g3', 'g4', 'tum']:
        for fz in ['f1', 'f2', 'f3']:
            satirlar.append([h, fz] + ['%d/9' % ozet[(h, fz, p)]['sat'] for p in ['p0', 'p1', 'p2', 'p3', 'p4']])
    rapor['birincil_md'] = md_tablo(['hedef', 'Φ', 'P0', 'P1', 'P2', 'P3', 'P4'], satirlar)
    # primary: fresh anchor, P0 and P4 minimal sets (nodes) for every τ
    satirlar = []
    for h in ['g1', 'g2', 'g3', 'g4', 'tum']:
        for fz in ['f1', 'f2', 'f3']:
            for t in ['hizli', 'orta', 'yavas']:
                for p in ['p0', 'p4']:
                    q = birincil[(h, fz, t, 'taze', p)]
                    if q['n']:
                        kume = ' ∣ '.join('{' + ','.join(dugumler(x)) + '}' + ('+%dT' % len(tasilar(x)) if tasilar(x) else '')
                                          for x in q['kumeler'])
                    else:
                        kume = 'UNSAT'
                    satirlar.append([h, fz, t, p, q['n'], kume])
    rapor['birincil_taze_md'] = md_tablo(['hedef', 'Φ', 'τ', 'politika', 'n', 'asgari kümeler (düğüm; +kT = k taşıyıcı)'], satirlar)

    # ---------------------------------------------------------------- 2. ca_baglama 2×2 and sanity
    cab = yukle('cab')
    grup = defaultdict(dict)
    for q in cab:
        e = q['etiket']
        grup[(e['tasarim'], e['ca_baglama'], e['ayni_ad_klasik_ca'])][qhucre(q)] = q
    cabsonuc = {}
    for anahtar, hucreler in sorted(grup.items()):
        esit_birincil = sum(1 for k, q in hucreler.items() if aile(q) == aile(birincil[k]))
        unsat = sum(1 for q in hucreler.values() if not q['n'])
        unsat_hedef = Counter(q['etiket']['hedef'] for q in hucreler.values() if not q['n'])
        cabsonuc['%s|%s|%s' % anahtar] = {'hucre': len(hucreler), 'birincil_ile_ayni': esit_birincil, 'unsat': unsat,
                                          'unsat_hedef': dict(unsat_hedef)}
    # sanity: is the result the same with the flag yok/var under diger_ca = var
    sd_y = grup[('cab_saglik_diger', 'yok', 'yok')]
    sd_v = grup[('cab_saglik_diger', 'yok', 'var')]
    cabsonuc['saglik_diger_bayrak_etkisiz'] = sum(1 for k in sd_y if aile(sd_y[k]) == aile(sd_v[k]))
    sb_v = grup[('cab_saglik_birincil', 'yok', 'var')]
    cabsonuc['saglik_birincil_bayrak_etkisiz'] = sum(1 for k in sb_v if aile(sb_v[k]) == aile(birincil[k]))
    # comparison with the expectations (beklenti_2x2.json)
    bek = {}
    def unsat_hepsi(anahtar, hedefler):
        return all(not q['n'] for q in grup[anahtar].values() if q['etiket']['hedef'] in hedefler)
    bek['ad/yok'] = cabsonuc['cab_2x2|ad|yok']['birincil_ile_ayni'] == 675
    bek['ad/var'] = unsat_hepsi(('cab_2x2', 'ad', 'var'), ['g1', 'g2', 'g3', 'tum', 'g4'])
    bek['anahtar/yok'] = cabsonuc['cab_2x2|anahtar|yok']['birincil_ile_ayni'] == 675
    bek['anahtar/var'] = cabsonuc['cab_2x2|anahtar|var']['birincil_ile_ayni'] == 675
    bek['saglik_yok_diger_var'] = (cabsonuc['saglik_diger_bayrak_etkisiz'] == 675 and
                                   unsat_hepsi(('cab_saglik_diger', 'yok', 'yok'), ['g1', 'g2', 'g3', 'tum']))
    bek['saglik_yok_diger_yok_birincil'] = cabsonuc['saglik_birincil_bayrak_etkisiz'] == 675
    cabsonuc['beklenti_tuttu'] = bek
    rapor['cab'] = cabsonuc
    json.dump(cabsonuc, open(os.path.join(CIK, 'cab_2x2.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    # ---------------------------------------------------------------- 3. mapping to the R6 window classes (A5 G3 + G1)
    a5 = yukle('a5')
    r6 = []
    for q in a5:
        e = q['etiket']
        if e['hedef'] not in ('g3', 'g1'):
            continue
        rej, omur, tau = e['rejim'], e['omur'], e['tau']
        pay = 300
        tok = omur                          # window of the token (V3)
        don = 86400 + omur                  # window of the period (V2)
        uzun = 31536000                     # V1 window = w_ihracci (primary 1 y)
        tls = 31536000                      # w_tls (primary 1 y)
        if e['hedef'] == 'g3' and tau >= tls + pay:
            sinif = 'TASIMA_KORUR'          # no transport in R6: a pulled token with τ > TLS window is protected by the transport
        elif tau >= uzun + pay:
            sinif = 'UZUN_OTESI'            # in R6 a long-lived key is not constrained in any regime
        elif rej == 'uzun':
            sinif = 'LONG'
        elif tau < tok + pay:
            sinif = 'FAST'
        elif tau < don + pay:
            sinif = 'MEDIUM'
        else:
            sinif = 'SLOW'
        dug = 'a08' if e['hedef'] == 'g3' else 'a07'
        ger, _ = gerekli_ve_olasi(q)
        asp_korur = dug not in ger          # can the signing key stay classical
        kimlik_pq = {'a03', 'a04'} <= ger   # is PQ required for the CA chain (ID)
        r6_tahmin = {'uzun': False, 'gunluk': sinif == 'SLOW', 'gecici': sinif in ('MEDIUM', 'SLOW')}[rej]
        if sinif in ('UZUN_OTESI', 'TASIMA_KORUR'):
            r6_tahmin = None                # outside the scope of R6 (reported separately)
        r6.append({'hedef': e['hedef'], 'kip': rej, 'omur_s': omur, 'tau_s': tau, 'r6_sinif': sinif,
                   'asp_imza_anahtari_klasik_kalabilir': asp_korur, 'asp_kimlik_pq_gerekli': kimlik_pq,
                   'r6_tahmini': r6_tahmin, 'uyum': (r6_tahmin is None) or (r6_tahmin == asp_korur)})
    with open(os.path.join(CIK, 'r6_esleme.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(r6[0].keys()))
        w.writeheader(); w.writerows(r6)
    kars = [r for r in r6 if r['r6_tahmini'] is not None]
    rapor['r6_kapsam_disi'] = dict(Counter(r['r6_sinif'] for r in r6 if r['r6_tahmini'] is None))
    rapor['r6'] = {'hucre': len(r6), 'karsilastirilan': len(kars), 'uyum': sum(r['uyum'] for r in kars),
                   'sinif_sayim': {'%s|%s' % k: v for k, v in Counter((r['kip'], r['r6_sinif']) for r in kars).items()},
                   'kimlik_pq_her_hucrede': all(r['asp_kimlik_pq_gerekli'] for r in kars)}
    # R6 classes of the nominal τ values (primary TTL 1 d, credential 30 d)
    nom = []
    for rej in ['uzun', 'gunluk', 'gecici']:
        for tad, tau in TAU_NOMINAL.items():
            for omur_ad, omur in [('durum TTL 1 g', GUN), ('kimlik bilgisi 30 g', 30 * GUN)]:
                tok, don = omur, 86400 + omur
                s = 'FAST' if tau < tok + 300 else ('MEDIUM' if tau < don + 300 else 'SLOW')
                if rej == 'uzun':
                    s2 = 'uzun ömürlü: her rejimde kırılır'
                else:
                    s2 = s
                nom.append([rej, tad, omur_ad, s2])
    rapor['r6_nominal_md'] = md_tablo(['kip', 'τ (nominal)', 'belirteç ömrü', 'R6 sembolik sınıfı'], nom)

    # ---------------------------------------------------------------- 4. H2′ design (mode × nominal τ)
    h2 = yukle('h2')
    h2t = defaultdict(lambda: Counter())
    for q in h2 + [dict(q, etiket=dict(q['etiket'], anahtar=a, kip='uzun')) for q in yukle('birincil')
                   for a in ('durum_anahtari', 'ihracci_anahtari')]:
        e = q['etiket']
        hedef = e['hedef']
        dug = 'a08' if e['anahtar'] == 'durum_anahtari' else 'a07'
        if (e['anahtar'] == 'durum_anahtari' and hedef not in ('g3',)) or \
           (e['anahtar'] == 'ihracci_anahtari' and hedef not in ('g1',)):
            continue
        ger, ola = gerekli_ve_olasi(q)
        durum = 'UNSAT' if ger is None else ('gerekli' if dug in ger else ('olasi' if dug in ola else 'gereksiz'))
        h2t[(e['anahtar'], e['kip'], e['tau'])][durum] += 1
    sat = []
    for an in ['durum_anahtari', 'ihracci_anahtari']:
        for kip in ['uzun', 'gunluk', 'gecici']:
            sat.append([an, kip] + ['%s' % dict(h2t[(an, kip, t)]) for t in ['hizli', 'orta', 'yavas']])
    rapor['h2_md'] = md_tablo(['anahtar', 'kip', 'τ hızlı', 'τ orta', 'τ yavaş'], sat)
    # H2′ falsification test (i): with the key window fixed (V1), does the token lifetime change the set? (A5)
    deg = defaultdict(set)
    for q in a5:
        e = q['etiket']
        if e['hedef'] in ('g3', 'g1') and e['rejim'] == 'uzun':
            deg[(e['hedef'], e['tau'])].add(tuple(aile(q)))
    rapor['h2_yanlislama_i'] = {'V1_sabit_pencere_hucre': len(deg),
                                'belirtec_omru_kumeyi_degistirdi': sum(1 for v in deg.values() if len(v) > 1)}
    # (ii): does the key window leave the set unchanged in every τ regime? -> change between nominal τ values in V2/V3
    deg2 = defaultdict(set)
    for q in h2:
        e = q['etiket']
        if (e['anahtar'], e['hedef']) in (('durum_anahtari', 'g3'), ('ihracci_anahtari', 'g1')):
            deg2[(e['anahtar'], e['kip'], e['faz'], e['capa'], e['politika'])].add(
                (e['tau'], tuple(aile(q))))
    degisen = sum(1 for v in deg2.values() if len({a for _, a in v}) > 1)
    rapor['h2_yanlislama_ii'] = {'V2V3_hucre_grubu': len(deg2), 'τ_ile_kume_degisen': degisen}

    # ---------------------------------------------------------------- 5. H1 design
    h1 = yukle('h1')
    h1g = defaultdict(dict)
    for q in h1:
        e = q['etiket']
        h1g[(e['webpki'], e['kanal'])][qhucre(q)] = q
    h1g[('cl', 'birincil')] = birincil
    # Transmission context (pre-registration §4.1: every form of transmission is a separate sub-state). Node × goal -> class:
    #  conveyed context: credential and its x5c (g1, g2), KB-JWT (g2), request + WRPAC (g4);
    #  pulled context: LOTL/TL/LoTE (every goal), status token and the x5c chain inside it (g3), metadata (carrier),
    #  Type Metadata and JVI (g1), CRL (g4). 'tum' is a mixed context; reported separately.
    BAGLAM = {}
    for d in ['a03', 'a04', 'a07']:
        for g in ['g1', 'g2']:
            BAGLAM[(d, g)] = 'aktarilan'
        BAGLAM[(d, 'g3')] = 'cekilen_icinde'      # the x5c chain (a03/a04) of the status token arrives with the pulled object
    BAGLAM[('a10', 'g2')] = 'aktarilan'
    for d in ['a11', 'a12']:
        BAGLAM[(d, 'g4')] = 'aktarilan'
    for d in ['a01', 'a02']:
        for g in ['g1', 'g2', 'g3', 'g4']:
            BAGLAM[(d, g)] = 'cekilen'
    BAGLAM[('a08', 'g3')] = 'cekilen'
    for g in ['g1', 'g2', 'g3']:
        BAGLAM[('a05', g)] = 'cekilen'
    BAGLAM[('a06', 'g1')] = 'cekilen'
    BAGLAM[('ejvi', 'g1')] = 'cekilen'
    BAGLAM[('ecrl', 'g4')] = 'cekilen'
    h1sat = []
    h1say = defaultdict(lambda: [0, 0])      # (channel, node, goal, context) -> [required in cl, substituted in pq]
    for kanal in sorted({k for _, k in h1g}):
        cl, pq = h1g[('cl', kanal)], h1g[('pq', kanal)]
        for k in cl:
            hedef = k[0]
            gcl, _ = gerekli_ve_olasi(cl[k])
            gpq, _ = gerekli_ve_olasi(pq[k])
            if gcl is None:
                continue
            for dug in gcl:
                bag = BAGLAM.get((dug, hedef), 'karisik' if hedef == 'tum' else 'diger')
                h1say[(kanal, dug, hedef, bag)][0] += 1
                if gpq is not None and dug not in gpq:
                    h1say[(kanal, dug, hedef, bag)][1] += 1
    for (kanal, dug, hedef, bag), (g, i) in sorted(h1say.items()):
        h1sat.append([kanal, dug, hedef, bag, g, i])
    rapor['h1_md'] = md_tablo(['kanal varyantı', 'düğüm', 'hedef', 'iletim bağlamı', 'WebPKI cl altında gerekli hücre',
                               'WebPKI pq altında ikame (pq(düğüm) içermeyen asgari küme var)'], h1sat)
    cek_ikame = sorted({(d, h) for (k, d, h, b), (g, i) in h1say.items() if b in ('cekilen', 'cekilen_icinde') and i > 0})
    akt_ikame = sorted({(k, d, h) for (k, d, h, b), (g, i) in h1say.items() if b == 'aktarilan' and i > 0})
    rapor['h1'] = {'cekilen_ikame_tutan': ['%s@%s' % x for x in cek_ikame],
                   'aktarilan_ikame_tutan (H1 yanlışlama koşulu)': ['%s:%s@%s' % x for x in akt_ikame],
                   'klasik_tasima_ikame_nominal_tau': 'yok (A13 WebPKI klasikken seçilemez; w_tls = 1 y > τ nominal)'}

    # ---------------------------------------------------------------- 6. H5 design (cnf 1 d / 30 d × τ) — G2
    h5 = {qhucre(q): q for q in yukle('h5')}
    h5sat = []
    for fz in ['f1', 'f2', 'f3']:
        for t in ['hizli', 'orta', 'yavas']:
            for p in ['p0', 'p4']:
                r = [fz, t, p]
                for kaynak in (birincil, h5):
                    q = kaynak[('g2', fz, t, 'taze', p)]
                    ger, ola = gerekli_ve_olasi(q)
                    r.append('UNSAT' if ger is None else ('a10 gerekli' if 'a10' in ger else 'a10 gereksiz'))
                h5sat.append(r)
    rapor['h5_md'] = md_tablo(['Φ', 'τ', 'politika', 'cnf 30 g (birincil)', 'cnf 1 g (ARF ≤24 sa)'], h5sat)
    # named single-use cells
    hq = {q['id']: q for q in yukle('h')}
    tk = []
    for tkv in ['yok', 'cuzdan', 'dogrulayici', 'kuresel_pasif']:
        r = [tkv]
        for kg in [GUN, 30 * GUN]:
            for t in ['hizli', 'orta', 'yavas']:
                q = hq['h|H5_%s_%d_%s' % (tkv, kg, t)]
                ger, _ = gerekli_ve_olasi(q)
                r.append('UNSAT' if ger is None else ('a10' if 'a10' in ger else '—'))
        tk.append(r)
    rapor['h5_tek_kullanim_md'] = md_tablo(['tek kullanım', '1g/hızlı', '1g/orta', '1g/yavaş', '30g/hızlı', '30g/orta',
                                            '30g/yavaş'], tk)

    # ---------------------------------------------------------------- 7. OAT summary
    oat = yukle('oat')
    og = defaultdict(dict)
    for q in oat:
        og[q['etiket']['sapma']][qhucre(q)] = q
    oatsat = []
    oatj = {}
    for sap, hucreler in sorted(og.items()):
        fark = [k for k in hucreler if aile(hucreler[k]) != aile(birincil[k])]
        sat2unsat = sum(1 for k in fark if birincil[k]['n'] and not hucreler[k]['n'])
        unsat2sat = sum(1 for k in fark if not birincil[k]['n'] and hucreler[k]['n'])
        hedefler = Counter(k[0] for k in fark)
        oatsat.append([sap, len(fark), sat2unsat, unsat2sat, dict(hedefler)])
        oatj[sap] = {'fark_hucre': len(fark), 'sat_unsat': sat2unsat, 'unsat_sat': unsat2sat,
                     'hedef': dict(hedefler), 'ornek': [list(k) for k in fark[:3]]}
    rapor['oat_md'] = md_tablo(['OAT sapması', 'asgari küme ailesi değişen hücre (/675)', 'SAT→UNSAT', 'UNSAT→SAT',
                                'değişen hücrelerin hedefleri'], oatsat)
    json.dump(oatj, open(os.path.join(CIK, 'oat.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    # ---------------------------------------------------------------- 8. τ sensitivity
    tq = yukle('tau')
    tsat = []
    tg = defaultdict(dict)
    for q in tq:
        tg[q['etiket']['tau']][qhucre(q)[:1] + qhucre(q)[1:2] + qhucre(q)[3:]] = q
    for tad in sorted(tg):
        rejim = tad.split('_')[0]
        ref = {k[:1] + k[1:2] + k[3:]: q for k, q in birincil.items() if k[2] == rejim}
        fark = sum(1 for k in tg[tad] if aile(tg[tad][k]) != aile(ref[k]))
        tsat.append([tad, len(tg[tad]), fark])
    rapor['tau_md'] = md_tablo(['τ değeri (rejim_saniye)', 'hücre', 'nominal τ ile asgari küme ailesi farklı'], tsat)

    json.dump({k: v for k, v in rapor.items() if not k.endswith('_md')}, open(os.path.join(CIK, 'ozet.json'), 'w',
              encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
    with open(os.path.join(CIK, 'tablolar.md'), 'w', encoding='utf-8') as f:
        for k, v in rapor.items():
            if k.endswith('_md'):
                f.write('\n### %s\n\n%s\n' % (k, v))
    print(json.dumps({k: v for k, v in rapor.items() if not k.endswith('_md')}, ensure_ascii=False, indent=1, default=str))


if __name__ == '__main__':
    main()
