# -*- coding: utf-8 -*-
"""Optimum göç sıraları (ön kayıt §4.9 S7 "asgari sıra"; pilot P2b amacı).
Bir asgari küme M (düğümler) ve taşıyıcıları sabitken, her adımda bir düğüm göç eder. Amaç (pilot P2b ile aynı):
    en büyükle  Σ_t |{ D ∈ önek_t : D'nin hedef yolundaki hiçbir artefaktı t anında etkin sahte değil }|
Çözüm: düğüm alt kümeleri üzerinde dinamik programlama (2^|M| önek). Güvenlik yüklemi iki bağımsız
değerlendiriciyle hesaplanır: ASP (cekirdek.lp, değerlendirme kipi) ve Jacobi (z3/py_degerlendirici.py);
iki DP'nin en iyi değeri ve en iyi sıra kümesi karşılaştırılır.
Regresyon: pilot P2b (referans/pilot/p2/order.lp) sırası yeniden üretilir.
Kullanım: ./calistir.sh sorgular/sira.py
"""
import itertools, json, os, sys
from functools import lru_cache
from multiprocessing import Pool
import clingo
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'z3'))
from sorgular.ortak import parametreler, degerlendir, KOK, kaydet_json
from py_degerlendirici import degerlendir_py
from yapi import Yapi, olgulari_oku

SON = os.path.join(KOK, 'sorgular', 'sonuc')
M2_AGIRLIK = {'a02': 107}


def en_iyi_siralar(dugumler, etkin_fn):
    """etkin_fn(frozenset S) -> {D ∈ S : etkin}. Dönüş: (en iyi değer, en iyi sıraların listesi)."""
    D = tuple(sorted(dugumler))
    n = len(D)
    bel = {}

    def f(S):
        # S: önek (göç etmiş düğümler); en iyi kalan toplam: S'den sonra kalan adımlar
        if S in bel:
            return bel[S]
        if len(S) == n:
            bel[S] = (0, [()])
            return bel[S]
        en, yollar = None, []
        for d in D:
            if d in S:
                continue
            S2 = S | {d}
            deger = len(etkin_fn(S2))
            alt, alt_yollar = f(S2)
            top = deger + alt
            if en is None or top > en:
                en, yollar = top, [(d,) + y for y in alt_yollar]
            elif top == en:
                yollar += [(d,) + y for y in alt_yollar]
        bel[S] = (en, yollar)
        return bel[S]

    return f(frozenset())


def yol_artefaktlari(prm, dugumler, tasi, hedef, O=None, dosyalar=None):
    """Hedef yolundaki (tam küme altında) artefakt → düğüm eşlemesi."""
    Y = Yapi(prm, O)
    return {a: Y.dugum[a] for a in Y.karar if Y.dugum[a] in dugumler}


def hucre_sira(is_):
    hid, degisen, hedef, dugumler, tasi = is_
    prm = parametreler(**degisen)
    Y = Yapi(prm)
    uyeler = {}
    for a in Y.karar:
        uyeler.setdefault(Y.dugum[a], []).append(a)
    hed = ['g1', 'g2', 'g3', 'g4'] if hedef == 'tum' else [hedef]

    def etkin_asp(S):
        r = degerlendir(prm, sorted(S), tasi, hedefler=hed, g5_kapsam=hed)
        sahte = {a for (s, a) in r['sahte'] if s == 'tum'}
        return frozenset(d for d in S if not any(a in sahte for a in uyeler.get(d, [])))

    def etkin_py(S):
        r = degerlendir_py(prm, sorted(S), tasi, hedefler=hed, g5_kapsam=hed)
        return frozenset(d for d in S if not any(a in r['sahte'] for a in uyeler.get(d, [])))

    ea, ya = en_iyi_siralar(dugumler, lru_cache(None)(etkin_asp))
    ep, yp = en_iyi_siralar(dugumler, lru_cache(None)(etkin_py))
    pozisyon = {d: sorted({y.index(d) + 1 for y in ya}) for d in dugumler}
    return {'hucre': hid, 'hedef': hedef, 'dugumler': sorted(dugumler), 'tasi': len(tasi), 'en_iyi_deger': ea,
            'en_iyi_sira_sayisi': len(ya), 'ornek_sira': list(ya[0]) if ya else [],
            'dugum_adim_araligi': {d: [min(v), max(v)] for d, v in pozisyon.items()},
            'asp_py_esit': (ea == ep) and (sorted(ya) == sorted(yp))}


def pilot_p2b():
    """Pilotun kendi order.lp'si ile yeni çekirdek + DP'nin karşılaştırması (coexist/pq/lotl/claims, ilk küme)."""
    pilot = os.environ.get('PILOT_P2', '/referans/pilot/p2')
    base = open(os.path.join(pilot, 'trustchain_base.lp'), encoding='utf-8').read()
    order = open(os.path.join(pilot, 'order.lp'), encoding='utf-8').read()
    ilk = ['convey(ca_iss,cred)', 'pq(ca_iss)', 'pq(cred)', 'pq(iss_cert)', 'pq(lotl)', 'pq(tl_pid)']
    facts = ''.join('target_pq(%s).' % a[3:-1] for a in ilk if a.startswith('pq('))
    facts += ''.join('conv(%s).' % a[7:-1] for a in ilk if a.startswith('convey('))
    ctl = clingo.Control(['0', '--opt-mode=optN', '-cphase=coexist', '-cwscd=pq', '-canchor=lotl', '--warn=none'])
    ctl.add('base', [], base + order + facts)
    ctl.ground([('base', [])])
    en_iyi = []
    ctl.solve(on_model=lambda m: en_iyi.append(tuple(x[1] for x in sorted((s.arguments[1].number, str(s.arguments[0]))
                                                                        for s in m.symbols(shown=True))))
              if m.optimality_proven else None)
    pilot_siralar = sorted(set(en_iyi))
    # yeni çekirdek: pilot örneği (regresyon/p2_ornegi.lp) üzerinde DP
    dosyalar = ['regresyon/p2_ornegi.lp', 'olgular/parametreler.lp', 'olgular/pencereler.lp']
    O = olgulari_oku(['regresyon/p2_ornegi.lp', 'olgular/parametreler.lp'])
    prm = parametreler(faz='f3', politika='p4', tau=600, capa='taze', wscd_pq='var')
    prm['kat']['pilot_faz'] = 'coexist'
    dug = ['ca_iss', 'cred', 'iss_cert', 'lotl', 'tl_pid']
    tasi = [('ca_iss', 'cred')]

    def etkin(S):
        r = degerlendir(prm, sorted(S), tasi, hedefler=['g1'], g5_kapsam=['g1'], dosyalar=dosyalar)
        sahte = {a for (s, a) in r['sahte'] if s == 'tum'}
        return frozenset(d for d in S if d not in sahte)

    deger, siralar = en_iyi_siralar(dug, lru_cache(None)(etkin))
    return {'pilot_siralar': [list(x) for x in pilot_siralar], 'yeni_siralar': [list(x) for x in sorted(siralar)],
            'esit': sorted(pilot_siralar) == sorted(siralar), 'yeni_en_iyi_deger': deger}


def main():
    birincil = json.load(open(os.path.join(SON, 'birincil.json'), encoding='utf-8'))['sorgular']
    isler = []
    for q in birincil:
        e = q['etiket']
        if e['capa'] != 'taze' or not q['kumeler']:
            continue
        if not (e['politika'] == 'p4' or (e['faz'] == 'f3' and e['politika'] == 'p0')):
            continue
        def anah(k):
            d = [a[3:-1] for a in k if a.startswith('pq(')]
            return (sum(M2_AGIRLIK.get(x, 1) for x in d), len(d), sorted(k))
        en = min(q['kumeler'], key=anah)
        dug = [a[3:-1] for a in en if a.startswith('pq(')]
        tasi = [tuple(a[5:-1].split(',')) for a in en if a.startswith('tasi(')]
        isler.append((q['id'], q['degisen'], q['hedefler'][0], dug, tasi))
    with Pool(processes=int(os.environ.get('ISCI', '10'))) as havuz:
        sonuc = havuz.map(hucre_sira, isler, chunksize=1)
    p2b = pilot_p2b()
    ozet = {'hucre': len(sonuc), 'asp_py_esit': sum(r['asp_py_esit'] for r in sonuc), 'pilot_p2b': p2b,
            'tek_en_iyi_sirali_hucre': sum(1 for r in sonuc if r['en_iyi_sira_sayisi'] == 1)}
    kaydet_json(os.path.join(SON, 'siralar.json'), {'ozet': ozet, 'hucreler': sonuc})
    print(json.dumps(ozet, ensure_ascii=False, indent=1))
    for r in sonuc[:12]:
        print(r['hucre'], r['en_iyi_sira_sayisi'], r['ornek_sira'], r['dugum_adim_araligi'])


if __name__ == '__main__':
    main()
