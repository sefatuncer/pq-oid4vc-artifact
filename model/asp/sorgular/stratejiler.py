# -*- coding: utf-8 -*-
"""Stratejiler S0–S8 × M1–M5 ve H4 karşılaştırması (ÖN; taslak atama: stratejiler_taslak.json sürüm 2).
M1 hücreleri: G1–G4 × Φ1–Φ3 × τ{hızlı, orta, yavaş}; birincil yapılandırma (çıpa taze, WebPKI klasik);
H1 tasarımı için WebPKI PQ ayrıca. Her strateji değerlendirmesi ASP, z3 ve Jacobi ile üç yönlü denetlenir.
Kullanım: ./calistir.sh sorgular/stratejiler.py
"""
import json, os, sys, hashlib
from collections import defaultdict, Counter
from multiprocessing import Pool
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'z3'))
from sorgular.ortak import parametreler, degerlendir, KOK, TAU_NOMINAL, kaydet_json
from yapi import Yapi
from z3_kodlama import degerlendir_z3
from py_degerlendirici import degerlendir_py

TASLAK = os.path.join(KOK, 'sorgular', 'stratejiler_taslak.json')
SON = os.path.join(KOK, 'sorgular', 'sonuc')
M2_AGIRLIK = {'a02': 107}
FAZ = ['f1', 'f2', 'f3']
TAU3 = ['hizli', 'orta', 'yavas']
HEDEF4 = ['g1', 'g2', 'g3', 'g4']
KISA_PENCERE = {'a10', 'a09a'}          # birincil yapılandırmada kısa pencereli anahtar düğümleri (Ö3)


def taslak():
    b = open(TASLAK, 'rb').read()
    return json.loads(b.decode('utf-8')), hashlib.sha256(b).hexdigest()


def m2(dug):
    return sum(M2_AGIRLIK.get(d, 1) for d in dug)


def strateji_atamasi(T, sad, faz, prm):
    """Stratejinin bu hücredeki PQ düğüm kümesi ve taşıyıcı kümesi."""
    st = T['stratejiler'][sad]
    Y = Yapi(prm)
    etkin = [d for d in Y.dugumler if d not in Y.yasak_dugum]
    gr = T['gruplar']
    dug = set()
    for g in st['pq'][faz]:
        if g == 'HEPSI':
            dug |= set(etkin)
        elif g == 'HEPSI-OPERASYONEL':
            dug |= set(etkin) - set(gr['OPERASYONEL'])
        else:
            dug |= set(gr[g])
    dug &= set(etkin)
    tasi = []
    if st['tasi']:
        mekan = {'MF': ('m_f', 'm_f2'), 'MD': ('m_d',), 'MF_ME2': ('m_f', 'm_f2', 'm_e2')}[st['tasi']]
        for x, lst in Y.tasiyici.items():
            for c, m in lst:
                if m in mekan:
                    tasi.append((c, x))
    return sorted(dug), sorted(set(tasi))


def _deg(is_):
    sad, h, fz, t, w, dug, tasi, degisen = is_
    prm = parametreler(**degisen)
    a = degerlendir(prm, dug, tasi, hedefler=[h], g5_kapsam=[h])
    ai = {g for (_, g) in a['ihlal']}
    z = degerlendir_z3(prm, dug, tasi, hedefler=[h], g5_kapsam=[h])
    p = degerlendir_py(prm, dug, tasi, hedefler=[h], g5_kapsam=[h])
    uc = ((h in ai) == (h in z['ihlal']) == (h in p['ihlal'])) and \
         (('g5' in ai) == ('g5' in z['ihlal']) == ('g5' in p['ihlal']))
    return {'strateji': sad, 'hedef': h, 'faz': fz, 'tau': t, 'webpki': w, 'dugum': dug, 'tasi': len(tasi),
            'saglar': h not in ai, 'g5_saglar': 'g5' not in ai, 'uclu_esit': uc}


def s7_tablosu():
    """S7 = birincil (cl) / h1-birincil (pq) P4 hücresinin ağırlıklı M2'si en küçük asgari kümesi."""
    out = {}
    kaynak = {'cl': json.load(open(os.path.join(SON, 'birincil.json'), encoding='utf-8'))['sorgular'],
              'pq': [q for q in json.load(open(os.path.join(SON, 'h1.json'), encoding='utf-8'))['sorgular']
                     if q['etiket']['kanal'] == 'birincil' and q['etiket']['webpki'] == 'pq']}
    for w, qs in kaynak.items():
        for q in qs:
            e = q['etiket']
            if e['capa'] != 'taze' or e['politika'] != 'p4':
                continue
            if not q['kumeler']:
                out[(e['hedef'], e['faz'], e['tau'], w)] = None
                continue
            def anah(k):
                d = [a[3:-1] for a in k if a.startswith('pq(')]
                return (m2(d), len(d), sorted(k))
            en = min(q['kumeler'], key=anah)
            out[(e['hedef'], e['faz'], e['tau'], w)] = {'dugum': sorted(a[3:-1] for a in en if a.startswith('pq(')),
                                                         'tasi': sorted(a for a in en if a.startswith('tasi(')),
                                                         'n_asgari': len(q['kumeler'])}
    return out


def main():
    T, sha = taslak()
    isler = []
    for sad, st in T['stratejiler'].items():
        if st.get('hesaplanan'):
            continue
        for w in ['cl', 'pq']:
            for fz in FAZ:
                for t in TAU3:
                    degisen = dict(faz=fz, tau=TAU_NOMINAL[t], capa='taze', webpki=w, politika=st['politika'])
                    degisen.update(st.get('ek_parametre', {}))
                    prm = parametreler(**degisen)
                    dug, tasi = strateji_atamasi(T, sad, fz, prm)
                    for h in HEDEF4:
                        isler.append((sad, h, fz, t, w, dug, tasi, degisen))
    with Pool(processes=int(os.environ.get('ISCI', '10'))) as havuz:
        sonuc = havuz.map(_deg, isler, chunksize=2)
    s7 = s7_tablosu()
    for (h, fz, t, w), v in s7.items():
        sonuc.append({'strateji': 'S7', 'hedef': h, 'faz': fz, 'tau': t, 'webpki': w,
                      'dugum': v['dugum'] if v else None, 'tasi': len(v['tasi']) if v else 0,
                      'saglar': v is not None, 'g5_saglar': v is not None, 'uclu_esit': True})
    # ---------------- ölçütler
    olcut = {}
    for sad in list(T['stratejiler']):
        for w in ['cl', 'pq']:
            rs = [r for r in sonuc if r['strateji'] == sad and r['webpki'] == w]
            m1 = sum(r['saglar'] for r in rs)
            fazm2 = {}
            for fz in FAZ:
                ds = [r['dugum'] for r in rs if r['faz'] == fz and r['dugum'] is not None]
                if sad == 'S7':
                    fazm2[fz] = {'min': min((len(d) for d in ds), default=None), 'max': max((len(d) for d in ds), default=None),
                                 'agirlikli_max': max((m2(d) for d in ds), default=None)}
                else:
                    d = ds[0] if ds else []
                    fazm2[fz] = {'dugum': len(d), 'agirlikli': m2(d)}
            m3 = None if sad == 'S7' else len({'a09a', 'a09b'} & set(next((r['dugum'] for r in rs if r['faz'] == 'f3'), [])))
            st = T['stratejiler'][sad]
            m4 = None if sad == 'S7' else (0 if (st.get('tasi') and st['politika'] in ('p3', 'p4')) else
                                           (1 if next((r['dugum'] for r in rs if r['faz'] == 'f3'), []) else 0))
            if sad == 'S7':
                m5 = '%d/%d hücre' % (sum(1 for r in rs if r['dugum'] and 'a10' in r['dugum']),
                                      sum(1 for r in rs if r['dugum']))
            else:
                m5 = 'evet' if any('a10' in r['dugum'] for r in rs) else 'hayır'
            olcut['%s|%s' % (sad, w)] = {'M1': '%d/36' % m1, 'M2': fazm2, 'M3_vekil': m3, 'M4_yapisal': m4, 'M5': m5,
                                         'G5_saglanan': sum(r['g5_saglar'] for r in rs if r['saglar'])}
    # ---------------- H4: S5 (ve S5e) ↔ S7, birincil (cl) ve H1 tasarımı (pq)
    h4 = []
    for w in ['cl', 'pq']:
        for h in HEDEF4:
            for fz in FAZ:
                for t in TAU3:
                    r7 = next(r for r in sonuc if r['strateji'] == 'S7' and (r['hedef'], r['faz'], r['tau'], r['webpki']) == (h, fz, t, w))
                    for s5 in ['S5', 'S5e']:
                        r5 = next(r for r in sonuc if r['strateji'] == s5 and (r['hedef'], r['faz'], r['tau'], r['webpki']) == (h, fz, t, w))
                        if r7['saglar'] and not r5['saglar']:
                            sinif, fark = 'yetersiz', sorted(set(r7['dugum']) - set(r5['dugum']))
                        elif r7['saglar'] and r5['saglar']:
                            fark = sorted(set(r5['dugum']) - set(r7['dugum']))
                            sinif = 'israfli' if len(r5['dugum']) - len(r7['dugum']) >= 1 else 'esit'
                        elif not r7['saglar'] and not r5['saglar']:
                            sinif, fark = 'ikisi_de_saglamaz', []
                        else:
                            sinif, fark = 'S5_saglar_S7_saglamaz(!)', []
                        o3 = sorted(set(fark) & KISA_PENCERE) + (['G4'] if h == 'g4' else []) + (['WebPKI'] if 'a13' in fark else [])
                        h4.append({'webpki': w, 'strateji': s5, 'hedef': h, 'faz': fz, 'tau': t, 'sinif': sinif,
                                   'fark_dugum': fark, 'S7_tasi': r7['tasi'], 'O3_ilgili': o3})
    ozet_h4 = {}
    for w in ['cl', 'pq']:
        for s5 in ['S5', 'S5e']:
            ozet_h4['%s|%s' % (s5, w)] = dict(Counter(x['sinif'] for x in h4 if x['webpki'] == w and x['strateji'] == s5))
    sorular = {
        'S1': 'S5, S7nin sagladigi her hucreyi sagliyor mu?',
        'yanit1_cl': all(not (x['sinif'] == 'yetersiz') for x in h4 if x['webpki'] == 'cl' and x['strateji'] == 'S5'),
        'S2': 'S5 fazladan artefakt istiyor mu? (israfli hucre sayisi, cl)',
        'yanit2_cl': sum(1 for x in h4 if x['webpki'] == 'cl' and x['strateji'] == 'S5' and x['sinif'] == 'israfli'),
        'S3': 'S1 ve S2 Q-day sonrasi kac hucreyi sagliyor? (beklenen 0; saglik)',
        'yanit3_cl': {s: sum(r['saglar'] for r in sonuc if r['strateji'] == s and r['webpki'] == 'cl') for s in ['S1', 'S2']},
    }
    uclu = sum(1 for r in sonuc if r['uclu_esit'])
    cikti = {'taslak_sha256': sha, 'degerlendirme': len(isler), 'uclu_esit': uclu, 'olcut': olcut, 'h4_ozet': ozet_h4,
             'onceden_kayitli_sorular': sorular, 'h4': h4, 'sonuc': sonuc}
    kaydet_json(os.path.join(SON, 'stratejiler.json'), cikti)
    print(json.dumps({k: v for k, v in cikti.items() if k not in ('h4', 'sonuc')}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
