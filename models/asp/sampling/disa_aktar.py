# -*- coding: utf-8 -*-
"""Teknik kapı örneklem ÇERÇEVESİ dışa aktarımı (ön kayıt §4.18, §2F madde 2). ASP çalışması ÖRNEK SEÇMEZ.

cerceve.jsonl  : birincil yapılandırmada Q'nun her hücresi için
                 - her asgari küme ("asgari"; beklenti: Tamarin verified),
                 - her asgari kümeden tek elemanı eksik her küme ("bir-eksik"; beklenti: iz / falsified).
kesif_2x2.jsonl: §2D m.11 keşifsel 2×2 ızgarası {ca_baglama: ad, anahtar} × {ayni_ad_klasik_ca: yok, var}
                 (diger_ca = var, klasik_sabit) için aynı biçim + her hücrede birincil asgari kümelerin o hücredeki
                 hükmü ("birincil-kume"; ad/var hücresi UNSAT olduğundan zorunlu örnek bu türden seçilebilir).
Her satırın ASP tahmini, kümenin DEĞERLENDİRME kipinde (cekirdek.lp) koşulmasıyla hesaplanır; tanık olarak
ihlal edilen hedefler ve sahte artefaktlar verilir. Alt çizge ve bayrak eşlemesi SEMA.md'de tanımlıdır.
Kullanım: ./calistir.sh sampling/disa_aktar.py
"""
import hashlib, json, os, sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from sorgular.ortak import (parametreler, parametre_olgulari, _kontrol, OLGU_DOSYALARI, CEKIRDEK, KOK,
                            TAU_NOMINAL)

SON = os.path.join(KOK, 'sorgular', 'sonuc')
CIK = os.path.join(KOK, 'sampling')
HEDEF_AD = {'g1': 'G1', 'g2': 'G2', 'g3': 'G3', 'g4': 'G4', 'tum': 'tumu'}
ANA = ['g1', 'g2', 'g3', 'g4']
GOSTER = """
#show ihlal/2. #show sahte/2. #show beklenir/2. #show yolda/2. #show kabul_alti/2. #show kanal_etkin/2.
#show sabit_etkin/1. #show klasik_alt_s/2. #show pencere/2. #show zaman_uygun/1. #show tasima_etkin/2.
#show varyant_etkin/3. #show pencere_sinifi/2. #show dugum_e/2. #show pq/1. #show tasima_sahte/2.
"""
LEMMA = {'g1': 'G1_claims_unforgeability', 'g2': 'G2_presentation_unforgeability', 'g3': 'G3_status_soundness',
         'g4': 'G4_rp_authentication', 'tum': 'G1..G4 (dördü birlikte)'}


def degerlendir_ayrintili(prm, dugumler, tasilar, hedef):
    metin = parametre_olgulari(prm)
    metin += ''.join('pqd(%s).' % d for d in dugumler) + ''.join('tasi(%s,%s).' % tuple(ct) for ct in tasilar)
    for g in (ANA if hedef == 'tum' else [hedef]):
        metin += 'g5_degerlendir(%s).' % g
    metin += GOSTER
    ctl = _kontrol(OLGU_DOSYALARI + CEKIRDEK, metin, [])
    ctl.ground([('base', [])])
    at = defaultdict(set)
    with ctl.solve(yield_=True) as h:
        for m in h:
            for s in m.symbols(shown=True):
                at[s.name].add(tuple(str(a) for a in s.arguments))
            break
    return at


def alt_cizge(at):
    """Hedef(ler)in yolundaki artefaktlar ve öznitelikleri (senaryo 'tum')."""
    yol = sorted(a for (s, a) in at['yolda'] if s == 'tum')
    kab = defaultdict(list)
    for a, b in at['kabul_alti']:
        kab[a].append(b)
    kanal = {a: k for a, k in at['kanal_etkin']}
    tas = defaultdict(list)
    for a, t in at['tasima_etkin']:
        tas[a].append(t)
    pen = {a: int(w) for a, w in at['pencere']}
    sinif = {a: c for a, c in at['pencere_sinifi']}
    dug = {a: d for a, d in at['dugum_e']}
    pq = {a for (a,) in at['pq']}
    sabit = {a for (a,) in at['sabit_etkin']}
    kalt = {a for (s, a) in at['klasik_alt_s'] if s == 'tum'}
    zaman = {a for (a,) in at['zaman_uygun']}
    sahte = {a for (s, a) in at['sahte'] if s == 'tum'}
    varyant = defaultdict(list)
    for s, a, av in at['varyant_etkin']:
        if s == 'tum':
            varyant[a].append(av)
    bek = {x for (s, x) in at['beklenir'] if s == 'tum'}
    tsahte = {t for (s, t) in at['tasima_sahte'] if s == 'tum'}
    dugler = []
    for a in yol:
        dugler.append({'artefakt': a, 'dugum': dug.get(a), 'pq': a in pq, 'sabit': a in sabit, 'kanal': kanal.get(a),
                       'tasima': sorted(tas.get(a, [])), 'tasima_sahtelenebilir': any(t in tsahte for t in tas.get(a, [])),
                       'tanitici': sorted(kab.get(a, [])), 'klasik_alternatif': a in kalt, 'beklenti_var': a in bek,
                       'pencere_s': pen.get(a), 'pencere_sinifi': sinif.get(a),
                       'klasikse_pencerede_kirilir': a in zaman, 'varyant': sorted(varyant.get(a, [])),
                       'sahte': a in sahte})
    return dugler


def tamarin_esleme(hedef, prm, alt, dugumler, tasilar):
    """R1–R7 düz Boole bayrakları (Tamarin çalışmasının şablonları; bkz. SEMA.md §4). Karar: ASP tahmini."""
    D = set(dugumler)
    kat = prm['kat']
    art = {x['artefakt']: x for x in alt}
    b = {}
    sab = []
    if any(a in art for a in ('a01_lotl', 'a02_tl', 'a02_lote_pid', 'a02_lote_erisim')):
        sab.append('R5')
        b.update({'LOTL_PQ': 'a01' in D, 'TL_PQ': 'a02' in D, 'PIN_TL': kat['capa'] == 'sabit',
                  'LOTE_OJEU_YOLU': 'a02_lote_pid' in art and 'a02_tl' in art,
                  'LOTL_KANAL_PQ': 'a13' in D, 'CEKILEN_TASIMA_PQ': 'a13' in D})
    if hedef in ('g1', 'g2', 'g3', 'tum'):
        sab.append('R1')
        b.update({'ROOT_PQ': 'a03' in D, 'CA_PQ': 'a04' in D, 'ISS_PQ': 'a07' in D})
        if hedef in ('g3', 'tum') and 'a08_durum' in art:
            b.update({'DURUM_YAPRAK_PQ': 'a08' in D, 'DURUM_CEKILEN_VIA_TLS': art['a08_durum']['kanal'] == 'cekilen'})
    if hedef in ('g2', 'tum'):
        sab.append('R4')
        b.update({'DEV_PQ': 'a10' in D, 'ISS_PQ': 'a07' in D, 'SINGLE_USE': kat['tek_kullanim'] != 'yok'})
    if hedef in ('g4', 'tum'):
        sab.append('R1(WRPAC)')
        b.update({'ACCESS_CA_PQ': 'a11' in D, 'RP_KEY_PQ': 'a12' in D,
                  'IMZASIZ_ISTEK_KABUL': kat['imzasiz_istek_kabul'] == 'var'})
    koex = [x for x in alt if x['klasik_alternatif'] and x['pq']]
    if koex:
        sab.append('R2/R3')
        b['COEXIST'] = True
        b['BEKLENTI'] = {x['dugum'] or x['artefakt']: x['beklenti_var'] for x in koex}
        b['BEKLENTI_TASIYICI_PQ'] = {ct[1]: ct[0] for ct in tasilar}
    else:
        b['COEXIST'] = False
    kisa = [x for x in alt if x['pencere_sinifi'] in ('donem', 'belirtec') and x['pencere_s'] is not None]
    if kisa:
        sab.append('R6/R6h5')
        tau = prm['say']['tau']
        b['R6'] = {x['artefakt']: {'sinif': x['pencere_sinifi'], 'pencere_s': x['pencere_s'],
                                   'tau_pencereden_uzun': not x['klasikse_pencerede_kirilir'], 'pq': x['pq']} for x in kisa}
        b['R6_tau_s'] = tau
    if kat['diger_ca'] == 'var':
        sab.append('R7hx')
        b.update({'CA_PQ': 'a04' in D, 'ALT_CA': True, 'NAME_BIND': kat['ca_baglama'] == 'ad',
                  'KEY_BIND': kat['ca_baglama'] == 'anahtar', 'ALT_SAME_NAME': kat['ayni_ad_klasik_ca'] == 'var',
                  'ALT_CA_KLASIK_SABIT': kat['diger_ca_rejimi'] == 'klasik_sabit'})
    return {'sablonlar': sab, 'spthy_onerisi': {'R1': 'R1_chain.spthy', 'R2/R3': 'R2_downgrade.spthy / R3_channel.spthy',
                                                'R4': 'R4_wscd.spthy', 'R5': 'R5_anchor.spthy',
                                                'R6/R6h5': 'R6_time.spthy / R6_h5.spthy', 'R7hx': 'R7_mh_x.spthy',
                                                'R1(WRPAC)': 'R1_chain.spthy (yaprak = istek)'},
            'bayraklar': b, 'lemma': LEMMA[hedef]}


def _satir(is_):
    kaynak, hucre_id, etiket, degisen, hedef, tur, dugumler, tasilar, ek = is_
    prm = parametreler(**degisen)
    at = degerlendir_ayrintili(prm, dugumler, tasilar, hedef)
    ihl = sorted({g for (s, g) in at['ihlal'] if s == 'tum'})
    hedef_ihlal = (hedef in ihl) if hedef != 'tum' else any(g in ihl for g in ANA)
    alt = alt_cizge(at)
    return {'kaynak': kaynak, 'hucre_id': hucre_id, 'hucre': dict(etiket, tau_s=degisen['tau']),
            'hedef': HEDEF_AD[hedef], 'tur': tur, 'kume': {'pq_dugumler': sorted(dugumler),
                                                           'tasiyicilar': [list(x) for x in sorted(tasilar)]},
            'asp_tahmini': 'falsified' if hedef_ihlal else 'verified', 'ihlal_edilen': ihl,
            'tanik_sahte_artefaktlar': sorted(x['artefakt'] for x in alt if x['sahte']),
            'alt_cizge': alt, 'tamarin': tamarin_esleme(hedef, prm, alt, dugumler, tasilar), **ek}


def ayir(kume):
    d = [a[3:-1] for a in kume if a.startswith('pq(')]
    t = [tuple(a[5:-1].split(',')) for a in kume if a.startswith('tasi(')]
    return d, t


def isler_uret(qs, kaynak, birincil_ref=None):
    isler = []
    for q in qs:
        e = q['etiket']
        hedef = q['hedefler'][0]
        hid = q['id']
        gorulen = {}
        for i, kume in enumerate(q['kumeler']):
            d, t = ayir(kume)
            isler.append((kaynak, hid, e, q['degisen'], hedef, 'asgari', d, t, {'asgari_no': i}))
            elemanlar = [('pq', x) for x in d] + [('tasi', x) for x in t]
            for tip, x in elemanlar:
                d2 = [y for y in d if not (tip == 'pq' and y == x)]
                t2 = [y for y in t if not (tip == 'tasi' and y == x)]
                anahtar = (tuple(sorted(d2)), tuple(sorted(t2)))
                eksik = ('pq(%s)' % x) if tip == 'pq' else ('tasi(%s,%s)' % x)
                if anahtar in gorulen:
                    gorulen[anahtar].append({'asgari_no': i, 'eksik': eksik})
                    continue
                gorulen[anahtar] = [{'asgari_no': i, 'eksik': eksik}]
                isler.append((kaynak, hid, e, q['degisen'], hedef, 'bir-eksik', d2, t2,
                              {'kaynaklar': gorulen[anahtar]}))
        if birincil_ref is not None:
            ref = birincil_ref.get((e['hedef'], e['faz'], e['tau'], e['capa'], e['politika']))
            if ref:
                for i, kume in enumerate(ref['kumeler']):
                    d, t = ayir(kume)
                    isler.append((kaynak, hid, e, q['degisen'], hedef, 'birincil-kume', d, t, {'birincil_asgari_no': i}))
    return isler


def yaz(ad, satirlar):
    yol = os.path.join(CIK, ad)
    with open(yol, 'w', encoding='utf-8', newline='\n') as f:
        for i, r in enumerate(satirlar):
            r = dict(satir_id='%s-%06d' % (ad.split('.')[0].upper(), i + 1), **r)
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n')
    h = hashlib.sha256(open(yol, 'rb').read()).hexdigest()
    return yol, h


def katman(satirlar):
    c = Counter((r['hedef'], r['tur']) for r in satirlar)
    return {'%s|%s' % k: v for k, v in sorted(c.items())}


def main():
    birincil = json.load(open(os.path.join(SON, 'birincil.json'), encoding='utf-8'))['sorgular']
    cab = json.load(open(os.path.join(SON, 'cab.json'), encoding='utf-8'))['sorgular']
    cab2x2 = [q for q in cab if q['etiket']['tasarim'] == 'cab_2x2']
    bref = {(q['etiket']['hedef'], q['etiket']['faz'], q['etiket']['tau'], q['etiket']['capa'], q['etiket']['politika']): q
            for q in birincil}
    ozet = {}
    for ad, isler in [('cerceve.jsonl', isler_uret(birincil, 'birincil')),
                      ('kesif_2x2.jsonl', isler_uret(cab2x2, 'kesif_2x2', birincil_ref=bref))]:
        with Pool(processes=int(os.environ.get('ISCI', '10'))) as havuz:
            satirlar = havuz.map(_satir, isler, chunksize=8)
        # tutarlılık: asgari -> verified, bir-eksik -> falsified (asgarilik ve yukarı kapalılık gereği)
        tutarsiz = [r for r in satirlar if (r['tur'] == 'asgari' and r['asp_tahmini'] != 'verified') or
                    (r['tur'] == 'bir-eksik' and r['asp_tahmini'] != 'falsified')]
        yol, h = yaz(ad, satirlar)
        ozet[ad] = {'satir': len(satirlar), 'sha256': h, 'katman_hedef_x_tur': katman(satirlar),
                    'asgari_verified_birEksik_falsified_tutarsiz': len(tutarsiz),
                    'hucre_sayisi_satirli': len({r['hucre_id'] for r in satirlar})}
        if ad == 'kesif_2x2.jsonl':
            ozet[ad]['ad_var_birincil_kume_hukumleri'] = dict(Counter(
                r['asp_tahmini'] for r in satirlar if r['tur'] == 'birincil-kume'
                and r['hucre']['ca_baglama'] == 'ad' and r['hucre']['ayni_ad_klasik_ca'] == 'var'))
            ozet[ad]['kombinasyon_x_tur'] = {'%s/%s|%s' % k: v for k, v in sorted(Counter(
                (r['hucre']['ca_baglama'], r['hucre']['ayni_ad_klasik_ca'], r['tur']) for r in satirlar).items())}
    with open(os.path.join(CIK, 'disa_aktarim_ozeti.json'), 'w', encoding='utf-8') as f:
        json.dump(ozet, f, ensure_ascii=False, indent=1, sort_keys=True)
    print(json.dumps(ozet, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
