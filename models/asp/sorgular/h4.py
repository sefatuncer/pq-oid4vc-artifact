# -*- coding: utf-8 -*-
"""H4 (ÖN): S5 (önce kök ve cihaz) ↔ S7 (hesaplanan asgari küme), ön kayıt §3.5, §4.21 (2a), Ö3, §2C 2.4.
Hücreler: (i) birincil yapılandırmanın 36 hücresi (G1–G4 × Φ × τ; çıpa taze; WebPKI klasik),
(ii) Ö3 adlandırılmış hücreleri (sorgular/sonuc/h4.json; kısa pencereli anahtarlar, G4, WebPKI, durum
delegasyonu) — H4 tasarımı yalnız bunlardır (§2C 2.4).
Sınıflama:
  yetersiz(beklenti) : S5 sağlamaz, S7 sağlar, S5e (S5 kümesi + P4 + M-f) sağlar  -> H3 kaynaklı (Ö2), (2a) değil
  yetersiz(dugum)    : S5e de sağlamaz; S7'nin her asgari kümesinde olup S5'te olmayan düğümler raporlanır
  israfli(tau)       : ikisi de sağlar; S5'in fazlası, aynı hücrenin τ=hızlı karşılığında gerekli olan kısa
                       pencereli bir anahtar düğümünü içerir (Ö3: sayılır)
  israfli(diger)     : fazlalık yalnız yol dışı ya da uzun ömürlü düğümler (Ö3: sayılmaz)
Her S5/S5e değerlendirmesi ASP, z3 ve Jacobi ile üç yönlü denetlenir.
"""
import json, os, sys
from collections import Counter
from multiprocessing import Pool
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'z3'))
from sorgular.ortak import parametreler, degerlendir, KOK, TAU_NOMINAL, kaydet_json
from sorgular.stratejiler import taslak, strateji_atamasi
from z3_kodlama import degerlendir_z3
from py_degerlendirici import degerlendir_py

SON = os.path.join(KOK, 'sorgular', 'sonuc')
KISA_PENCERE = {'a10', 'a09a', 'a07', 'a08'}     # kipine göre kısa pencereli olabilen imza anahtarları


def dug(k):
    return {a[3:-1] for a in k if a.startswith('pq(')}


def s_deg(T, sad, degisen, hedef):
    st = T['stratejiler'][sad]
    d = dict(degisen, politika=st['politika'])
    d.update(st.get('ek_parametre', {}))
    prm = parametreler(**d)
    pq, tasi = strateji_atamasi(T, sad, d['faz'], prm)
    a = degerlendir(prm, pq, tasi, hedefler=[hedef], g5_kapsam=[hedef])
    ai = {g for (_, g) in a['ihlal']}
    z = degerlendir_z3(prm, pq, tasi, hedefler=[hedef], g5_kapsam=[hedef])
    p = degerlendir_py(prm, pq, tasi, hedefler=[hedef], g5_kapsam=[hedef])
    uc = (hedef in ai) == (hedef in z['ihlal']) == (hedef in p['ihlal'])
    return set(pq), hedef not in ai, uc


def _hucre(is_):
    ad, hedef, degisen, kumeler, hizli_kumeler = is_
    T, _ = taslak()
    s5, s5_ok, uc1 = s_deg(T, 'S5', degisen, hedef)
    s5e, s5e_ok, uc2 = s_deg(T, 'S5e', degisen, hedef)
    s7_ok = bool(kumeler)
    if s7_ok:
        min7 = min(len(dug(k)) for k in kumeler)
        gerekli7 = set.intersection(*[dug(k) for k in kumeler])
        birlesim7 = set.union(*[dug(k) for k in kumeler])
    else:
        min7, gerekli7, birlesim7 = None, set(), set()
    hizli_gerekli = set.union(*[dug(k) for k in hizli_kumeler]) if hizli_kumeler else set()
    if s7_ok and not s5_ok:
        sinif = 'yetersiz(beklenti)' if s5e_ok else 'yetersiz(dugum)'
        fark = sorted(gerekli7 - s5)
    elif s7_ok and s5_ok:
        fazla = s5 - birlesim7
        if len(s5) - min7 >= 1:
            tau_kay = sorted((fazla & KISA_PENCERE) & hizli_gerekli)
            sinif = 'israfli(tau)' if tau_kay else 'israfli(diger)'
            fark = tau_kay if tau_kay else sorted(fazla)
        else:
            sinif, fark = 'esit', []
    elif not s7_ok and not s5_ok:
        sinif, fark = 'ikisi_de_saglamaz', []
    else:
        sinif, fark = 'S5_saglar_S7_saglamaz', []
    return {'hucre': ad, 'hedef': hedef, 'degisen': degisen, 'sinif': sinif, 'fark': fark, 'S5_dugum': len(s5),
            'S7_min_dugum': min7, 'S5e_saglar': s5e_ok, 'uclu_esit': uc1 and uc2}


def main():
    birincil = json.load(open(os.path.join(SON, 'birincil.json'), encoding='utf-8'))['sorgular']
    h4q = json.load(open(os.path.join(SON, 'h4.json'), encoding='utf-8'))['sorgular']
    isler = []
    # (i) birincil 36 hücre (P4 = S7'nin politikası)
    bi = {(q['etiket']['hedef'], q['etiket']['faz'], q['etiket']['tau'], q['etiket']['capa'], q['etiket']['politika']): q
          for q in birincil}
    for h in ['g1', 'g2', 'g3', 'g4']:
        for fz in ['f1', 'f2', 'f3']:
            for t in ['hizli', 'orta', 'yavas']:
                q = bi[(h, fz, t, 'taze', 'p4')]
                hq = bi[(h, fz, 'hizli', 'taze', 'p4')]
                isler.append(('birincil|%s|%s|%s' % (h, fz, t), h, {'faz': fz, 'tau': TAU_NOMINAL[t], 'capa': 'taze'},
                              q['kumeler'], hq['kumeler']))
    # (ii) Ö3 adlandırılmış hücreleri: S7 = hücrenin kendi asgari kümeleri (P4'lü hücreler) ya da politika P0 hücreleri
    ad2q = {q['id']: q for q in h4q}
    for q in h4q:
        if q['id'].startswith('h4|SADAKAT'):
            continue                                  # sadakat hücresi H4 değildir (Ö3); ayrı raporlanır
        d = dict(q['degisen'])
        d.pop('politika', None)
        hizli_id = None
        if '_orta' in q['id'] or '_yavas' in q['id']:
            hizli_id = q['id'].replace('_orta', '_hizli').replace('_yavas', '_hizli')
        hk = ad2q[hizli_id]['kumeler'] if hizli_id in ad2q else q['kumeler']
        isler.append((q['id'], q['hedefler'][0], d, q['kumeler'], hk))
    with Pool(processes=int(os.environ.get('ISCI', '10'))) as havuz:
        sonuc = havuz.map(_hucre, isler, chunksize=2)
    ozet = {'birincil': dict(Counter(r['sinif'] for r in sonuc if r['hucre'].startswith('birincil'))),
            'o3_adlandirilmis': dict(Counter(r['sinif'] for r in sonuc if r['hucre'].startswith('h4|'))),
            'uclu_esit': sum(r['uclu_esit'] for r in sonuc), 'degerlendirme': len(sonuc)}
    def kisa(r):
        d = r['degisen']
        k = set()
        if d.get('durum_anahtari') in ('gunluk', 'gecici'):
            k.add('a08')
        if d.get('ihracci_anahtari') in ('gunluk', 'gecici'):
            k.add('a07')
        if d.get('kimlik_gecerlilik', 30 * 86400) <= 86400:
            k.add('a10')
        return set(r['fark']) & k
    # Ö3: uzun ömürlü anahtar farkları (V1 a07/a08, a04, a03 ...) (2a) sayılmaz; öncelik kısa pencere, G4, WebPKI
    aday_2a = [r for r in sonuc if r['sinif'] == 'israfli(tau)' or
               (r['sinif'] == 'yetersiz(dugum)' and (r['hedef'] == 'g4' or 'a13' in r['fark'] or kisa(r)))]
    ozet['aday_2a_sayisi'] = len(aday_2a)
    kaydet_json(os.path.join(SON, 'h4_karsilastirma.json'), {'ozet': ozet, 'hucreler': sonuc, 'aday_2a': aday_2a})
    print(json.dumps(ozet, ensure_ascii=False, indent=1))
    for r in aday_2a:
        print('ADAY', r['hucre'], r['sinif'], r['fark'], 'S5=%d S7min=%s' % (r['S5_dugum'], r['S7_min_dugum']))


if __name__ == '__main__':
    main()
