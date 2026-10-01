# -*- coding: utf-8 -*-
"""z3 ve Python değerlendiricisi için olgu okuyucu + parametreye bağlı YAPI katmanı.

Bağımsızlık notu: Bu modül ASP çekirdeğini (cekirdek.lp, pencereler.lp) OKUMAZ; yalnız zemin
olgu dosyalarını (artefaktlar/kenarlar/tasiyicilar/hedefler/parametreler) okur ve koşulları kendi
koduyla yorumlar. Pencere kuralları, faz kuralı, M-h baskınlık hesabı vb. burada yeniden yazılmıştır
(RAPOR §2'deki semantik tanımdan). Böylece ASP ile z3/Python arasında hem yapı hem değerlendirme
bağımsız kodlanır; z3 ile Python ise değerlendirme algoritmasında (sembolik özyineleme ↔ Jacobi
sabit nokta yinelemesi) ayrışır.
"""
import os, re
from collections import defaultdict

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOSYALAR = ['olgular/artefaktlar.lp', 'olgular/kenarlar.lp', 'olgular/tasiyicilar.lp',
            'olgular/hedefler.lp', 'olgular/parametreler.lp']
_OLGU = re.compile(r'([a-z_][A-Za-z0-9_]*)\(([^()]*)\)\s*\.')


def olgulari_oku(dosyalar=DOSYALAR, kok=KOK):
    """Yalnız zemin olgular (':-' içeren satırlar atlanır). Dönüş: ad -> [argüman demetleri]."""
    d = defaultdict(list)
    for f in dosyalar:
        with open(os.path.join(kok, f), encoding='utf-8') as fh:
            for satir in fh:
                satir = satir.split('%', 1)[0]
                if ':-' in satir or not satir.strip():
                    continue
                for ad, arg in _OLGU.findall(satir):
                    d[ad].append(tuple(x.strip() for x in arg.split(',')) if arg.strip() else ())
    return d


OLGU = None


def olgu():
    global OLGU
    if OLGU is None:
        OLGU = olgulari_oku()
    return OLGU


YAPRAK = None


class Yapi:
    """Bir parametre ataması için statik (senaryodan bağımsız) yapı."""

    def __init__(self, prm, O=None):
        O = O or olgu()
        kat, say = prm['kat'], prm['say']
        self.kat, self.say = kat, say
        P = lambda a, v: kat.get(a) == v
        self.P = P
        sure = {a: int(b) for a, b in O['sure']}
        # --- varlık
        var_kos = defaultdict(list)
        for a, p, v in O['var_kosul']:
            var_kos[a].append((p, v))
        self.mevcut = {a for (a,) in O['artefakt'] if all(P(p, v) for p, v in var_kos[a])}
        M = self.mevcut
        self.imzali = {a for (a,) in O['imzali'] if a in M}
        self.imzasiz = {a for (a,) in O['imzasiz'] if a in M}
        self.sinif = {a: s for a, s in O['sinif']}
        # --- karar ve düğümler (§2C: 17 düğüm; dugum/2 yoksa artefakt kendi düğümüdür)
        self.karar = {a for (a,) in O['karar'] if a in M}
        self.karar |= {a for a, p, v in O['karar_kosullu'] if a in M and P(p, v)}
        dug = {a: d for a, d in O['dugum']}
        self.dugum = {a: dug.get(a, a) for a in self.karar}
        self.dugumler = sorted(set(self.dugum.values()))
        self.pq_yasak = {a for a, p, v in O['pq_yasak'] if a in M and P(p, v)}
        self.yasak_dugum = {self.dugum[a] for a in self.pq_yasak if a in self.dugum}
        self.pq_baglar = {a: b for a, b in O['pq_baglar'] if a in M}
        # --- kenarlar (bütün koşullar; 'degil' koşulları)
        kk, kd = defaultdict(list), defaultdict(list)
        for e, p, v in O['kenar_kosul']:
            kk[e].append((p, v))
        for e, p, v in O['kenar_kosul_degil']:
            kd[e].append((p, v))
        self.tanitici = defaultdict(set)   # A -> {B}
        for e, a, b in O['kenar']:
            if a in M and b in M and all(P(p, v) for p, v in kk[e]) and not any(P(p, v) for p, v in kd[e]):
                self.tanitici[a].add(b)
        # --- kanal
        kosullu = defaultdict(list)
        for a, k, p, v in O['kanal_kosullu']:
            kosullu[a].append((k, p, v))
        self.kanal = {}
        for a, k in O['kanal']:
            if a in M and not kosullu[a]:
                self.kanal[a] = k
        for a, lst in kosullu.items():
            if a in M:
                for k, p, v in lst:
                    if P(p, v):
                        assert a not in self.kanal, 'birden çok kanal: %s' % a
                        self.kanal[a] = k
        # --- taşıma
        tk = defaultdict(list)
        for a, t, p, v in O['tasima_kosullu']:
            tk[a].append((t, p, v))
        self.tasima = defaultdict(set)
        for a, t in O['tasima']:
            if a in M and not tk[a]:
                self.tasima[a].add(t)
        for a, lst in tk.items():
            if a in M:
                for t, p, v in lst:
                    if P(p, v):
                        self.tasima[a].add(t)
        self.tasima_anahtari = {t: a for t, a in O['tasima_anahtari']}
        # --- sabit
        self.sabit = {a for (a,) in O['sabit'] if a in M}
        self.sabit |= {a for a, p, v in O['sabit_kosullu'] if a in M and P(p, v)}
        # --- param. PQ ve aynı anahtar
        self.pq_sabit = {a for a, p, v in O['pq_kosullu'] if a in M and P(p, v)}
        self.ayni = {a: b for a, b in O['ayni_anahtar'] if a in M}
        # --- faz: klasik alternatif (imzalı ve PQ-bağlanabilir imzasız karar artefaktları)
        yaprak = {s for (s,) in O['yaprak_sinif']}
        self.klasik_alt = set()
        for a in self.karar:
            if P('faz', 'f1') or (P('faz', 'f2') and self.sinif.get(a) in yaprak):
                self.klasik_alt.add(a)
        self.klasik_alt |= {a for a, p, v in O['klasik_alt_zorla'] if a in M and P(p, v)}
        self.crl_gunbatimi = P('faz', 'f3') and P('gun_batimi', 'iptal') and 'a12_istek' in M \
            and 'a12_istek' in self.karar and 'e_crl' in M
        # --- pencereler (kendi yeniden yazımımız; pencereler.lp'yi okumaz; §2C 2.3)
        def w(ad):
            return say[ad] if ad in say else sure[ad]
        self.pencere = {}
        param_art = {'a07_kimlik', 'a08_durum', 'a10_kbjwt', 'a09c_ornek'}
        for a, ad in O['pencere_sabit']:
            if a in M and a not in param_art:
                self.pencere[a] = w(ad)
        uz = sure['uzun']
        kg, ttl, iat = say['kimlik_gecerlilik'], say['durum_ttl'], say['kbjwt_iat']
        wi = say['w_ihracci']
        tekrar = kat['anahtar_yeniden_kullanim'] == 'var'     # R6 KEY_REUSE: V2/V3 anahtarı dönmez
        self.pencere['a07_kimlik'] = wi if tekrar else {'uzun': wi, 'gunluk': 86400 + kg, 'gecici': kg}[kat['ihracci_anahtari']]
        self.pencere['a08_durum'] = wi if tekrar else {'uzun': wi, 'gunluk': 86400 + ttl, 'gecici': ttl}[kat['durum_anahtari']]
        if kat['cihaz_anahtari'] == 'kalici':
            self.pencere['a10_kbjwt'] = uz
        else:
            self.pencere['a10_kbjwt'] = iat if kat['tek_kullanim'] == 'kuresel_pasif' else kg
        self.pencere['a09c_ornek'] = say['w_wia'] if kat['wia_anahtari'] == 'wia_basi' else uz
        tau, pay = say['tau'], say['saat_payi']
        self.zaman = {a: (tau < w + pay) for a, w in self.pencere.items() if a in M}
        self.p3_zaman = tau < uz + pay
        # --- taşıyıcılar
        tkos = defaultdict(list)
        for c, x, p, v in O['tasiyabilir_kosul']:
            tkos[(c, x)].append((p, v))
        self.tasiyici = defaultdict(list)   # X -> [(C, M)]
        for c, x, m in O['tasiyabilir']:
            if c in M and x in M and all(P(p, v) for p, v in tkos[(c, x)]):
                self.tasiyici[x].append((c, m))
        self.ortak_ata = {(c, x) for c, x in O['ortak_ata']}
        # M-h baskınlık: C, X'ten köklere giden her kabul yolunda mı? (yol araması; sabit düğümde durur)
        self.uygun = set()
        for x, lst in self.tasiyici.items():
            for c, m in lst:
                if m != 'm_h':
                    self.uygun.add((c, x))
                elif (c, x) in self.ortak_ata and not self._c_disi_kok_yolu(x, c):
                    self.uygun.add((c, x))
        # --- varyantlar
        vk = defaultdict(list)
        for a, av, p, v in O['varyant_kosul']:
            vk[(a, av)].append((p, v))
        self.varyant = defaultdict(list)
        for a, av in O['varyant']:
            if a in M and av in M and all(P(p, v) for p, v in vk[(a, av)]):
                self.varyant[a].append(av)
        # --- özgün
        self.ozgun = {a for a, p, v in O['ozgun_kosullu'] if a in M and P(p, v)}
        if P('capa', 'onbellek') and P('onbellek_ufku', 'ilk_pencere'):
            self.ozgun |= {a for (a,) in O['onbellekli'] if a in M}
        # --- hedefler
        hk = defaultdict(list)
        for g, a, p, v in O['hedef_kosul']:
            hk[(g, a)].append((p, v))
        self.hedef = defaultdict(set)
        for g, a in O['hedef_artefakt']:
            if a in M and all(P(p, v) for p, v in hk[(g, a)]):
                self.hedef[g].add(a)
        pik = defaultdict(list)
        for i, p, v in O['politika_ihlal_kosul']:
            pik[i].append((p, v))
        self.politika_ihlali = {g for g, i in O['politika_ihlali'] if all(P(p, v) for p, v in pik[i])}
        self.ana = [g for (g,) in O['ana_hedef']]
        self.wscd = {a for (a,) in O['wscd_artefakt'] if a in M}
        self.wscd_dugum = {self.dugum[a] for a in self.wscd if a in self.dugum}
        self.beklenti_pol = kat['politika'] in ('p3', 'p4')
        self.mf_kapali = set()   # A3 kancası (varsayılan: bütün bileşenler açık)

    def _c_disi_kok_yolu(self, x, c):
        """X'ten C'ye uğramadan bir köke (sabit ya da tanıtıcısız düğüm) ulaşan kabul yolu var mı?"""
        yigin, gorulen = [x], set()
        while yigin:
            a = yigin.pop()
            if a in gorulen or a == c:
                continue
            gorulen.add(a)
            if a != x and (a in self.sabit or not self.tanitici[a]):
                return True
            if a == x and (a in self.sabit or not self.tanitici[a]):
                return True
            if a in self.sabit:
                continue
            yigin.extend(self.tanitici[a])
        return False

    def anahtarlar(self):
        """Kırılabilir anahtar kimlikleri: A (imzacı), ('alt',A), 'p3_kanal'."""
        ks = []
        for a in sorted(self.imzali):
            ks.append(a)
            ks.append(('alt', a))
        ks.append('p3_kanal')
        return ks

    def karar_atomlari(self):
        pq = list(self.dugumler)
        ta = sorted({(c, x) for x, lst in self.tasiyici.items() for c, _ in lst}) if self.beklenti_pol else []
        return pq, ta
