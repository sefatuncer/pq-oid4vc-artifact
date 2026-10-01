# -*- coding: utf-8 -*-
"""Üçüncü bağımsız değerlendirici: Jacobi sabit-nokta yinelemesi (ön kayıt D2: 3 yönlü uyum).

z3 kodlayıcısı formülleri bellekli özyinelemeyle kurarken, bu modül bütün yüklemleri (sahte,
etkin_sahte, beklenir, basar, ulasir, yolda) her turda eşzamanlı olarak yeniden hesaplar ve değişim
kalmayınca durur. Bağımlılık grafiği döngüsüzse yineleme en uzun yol sayısı kadar turda tek çözüme
yakınsar; yakınsamama (salınım) döngü ya da tabakalanmamış olumsuzlama belirtisidir ve hata verir.
"""
from yapi import Yapi


def degerlendir_py(prm, pq=(), tasi=(), hedefler=('g1', 'g2', 'g3', 'g4'), kirik=None, g5_kapsam=None,
                   en_fazla_tur=500, O=None):
    Y = Yapi(prm, O)
    kat = prm['kat']
    pq = set(pq)
    tasi = set(tasi)
    if kirik is None:
        kirik_fn = (lambda k: False) if kat['saldirgan'] == 's1' else (lambda k: True)
    else:
        kirik = set(kirik)
        kirik_fn = lambda k: k in kirik

    def PQ(a):
        if a in Y.karar:                # karar: düğümü seçilmiş mi (§2C: düğüm başına tek karar)
            return Y.dugum[a] in pq
        if a in pq:                     # regresyon örnekleri: karar dışı artefakta sabit atama
            return True
        if a in Y.pq_sabit:
            return True
        if a in Y.ayni:
            return PQ(Y.ayni[a])
        return False

    arts = sorted(Y.mevcut)
    s = {a: False for a in arts}       # sahte
    es = {a: False for a in arts}      # etkin sahte
    bek = {a: False for a in arts}     # beklenir
    pol = kat['politika']
    kapsam_engeli = ('kapsam' in Y.mf_kapali) and kat['faz'] in ('f1', 'f2')
    geri = ('tazelik' in Y.mf_kapali) and ('tekduzelik' in Y.mf_kapali)
    p3k = kirik_fn('p3_kanal') and Y.p3_zaman

    def kalt(a, es_):
        v = a in Y.klasik_alt
        if a == 'a12_istek' and Y.crl_gunbatimi and es_.get('e_crl', False):
            v = True
        return v

    for tur in range(en_fazla_tur):
        yeni_bek = {}
        for x in arts:
            v = False
            if Y.beklenti_pol and not kapsam_engeli and not geri:
                for c, m in Y.tasiyici[x]:
                    if (c, x) in Y.uygun and (c, x) in tasi and not es[c]:
                        if pol == 'p4' or (pol == 'p3' and not p3k):
                            v = True
            yeni_bek[x] = v
        yeni_s, yeni_es = {}, {}
        for a in arts:
            zaman = Y.zaman.get(a, False)
            imz = a in Y.imzali
            basar = (imz and kirik_fn(a) and not PQ(a) and zaman)
            if not basar and a not in Y.sabit:
                basar = any(es[b] for b in Y.tanitici[a])
            if not basar:
                basar = (imz and kirik_fn(('alt', a)) and PQ(a) and kalt(a, es) and zaman and not bek[a])
            if not basar and a in Y.imzasiz:
                basar = (not PQ(a)) or (kalt(a, es) and not bek[a])
            k = Y.kanal.get(a)
            if k in ('aktarilan', 'sunan_uc', 'kimliksiz'):
                ulasir = True
            elif k in ('cekilen', 'yalniz_tasima'):
                ulasir = any(es[Y.tasima_anahtari[t]] for t in Y.tasima[a])
            else:
                ulasir = False
            v = basar and ulasir
            if not v and a in Y.imzasiz and a in Y.pq_baglar and PQ(a):
                v = es[Y.pq_baglar[a]]
            yeni_s[a] = v and a not in Y.ozgun
        for a in arts:
            v = yeni_s[a]
            if not v:
                v = any((not yeni_bek[a]) and yeni_s[av] for av in Y.varyant[a])
            yeni_es[a] = v
        if yeni_s == s and yeni_es == es and yeni_bek == bek:
            break
        s, es, bek = yeni_s, yeni_es, yeni_bek
    else:
        raise RuntimeError('Jacobi yinelemesi yakınsamadı (döngü?)')

    def ihl(g):
        if g in Y.politika_ihlali:
            return True
        return any(es[a] for a in Y.hedef[g])

    ihlal = set()
    for g in list(hedefler):
        if g in Y.ana and ihl(g):
            ihlal.add(g)
    if any(ihl(g) for g in Y.ana):
        ihlal.add('tum')
    if ihl('g2i'):
        ihlal.add('g2i')
    # G5: 'yolda' için de Jacobi (hedeflerden aşağı)
    kap = [g for g in (g5_kapsam if g5_kapsam is not None else hedefler) if g in Y.ana]
    if kap:
        hedef_kume = set().union(*[Y.hedef[g] for g in kap])
        yol = {a: a in hedef_kume for a in arts}
        for tur in range(en_fazla_tur):
            yeni = dict(yol)
            for x in arts:
                if not yol[x]:
                    continue
                for b in Y.tanitici[x]:
                    yeni[b] = True
                for av in Y.varyant[x]:
                    if not bek[x]:
                        yeni[av] = True
                for c, m in Y.tasiyici[x]:
                    if (c, x) in tasi and Y.beklenti_pol:
                        yeni[c] = True
                for t in Y.tasima[x]:
                    yeni[Y.tasima_anahtari[t]] = True
            if yeni == yol:
                break
            yol = yeni
        for a in arts:
            if yol[a] and a in Y.karar and PQ(a):
                if (kalt(a, es) and not bek[a]) or any(not bek[a] for av in Y.varyant[a]):
                    ihlal.add('g5')
    sahte = {a for a in arts if s[a]}
    return {'ihlal': ihlal, 'sahte': sahte, 'tur': tur + 1}
