# -*- coding: utf-8 -*-
"""PQ-OID4VC Step 3 — INDEPENDENT encoding of the same semantics with z3 (not a mechanical translation of the ASP).

Encoding: for every artefact the 'effective forgery' formula is built by memoised recursion over the dependency graph
(error if a cycle is detected). Decision variables pq_A and tasi_C_X; break variables brk_K
(K = A | ('alt',A) | 'p3_kanal'). With k unbounded brk ≡ true, in S1 brk ≡ false; with finite k
the condition ∀B(|B|≤k) is solved by CEGAR (a different method from the scenario enumeration of the ASP).
Minimal sets: find a model → reduce it to a subset-minimal one by removing elements one by one → block the supersets
(since the family of secure sets is upward closed, single-element minimality = subset minimality).
"""
import itertools, time
import z3
from yapi import Yapi


class Kodlayici:
    def __init__(self, Y, brk_kip, sabit_pq=()):
        """brk_kip: 'tum' | 'bos' | 'sembolik'; sabit_pq: fixed PQ assignment for artefacts outside the decisions
        (evaluation mode; the counterpart of the pq(x) fact in the ASP)."""
        self.Y = Y
        self.kip = brk_kip
        self.sabit_pq = set(sabit_pq)
        self.pqv = {d: z3.Bool('pq__' + d) for d in Y.dugumler}          # §2C: one decision per node
        pq_at, ta_at = Y.karar_atomlari()
        self.tav = {ct: z3.Bool('tasi__%s__%s' % ct) for ct in ta_at}
        self.brkv = {}
        if brk_kip == 'sembolik':
            for k in Y.anahtarlar():
                ad = 'brk__' + (k if isinstance(k, str) else 'alt_' + k[1])
                self.brkv[k] = z3.Bool(ad)
        self._bel = {}
        self._yigin = set()

    # ---------------- basic terms
    def brk(self, k):
        if self.kip == 'tum':
            return z3.BoolVal(True)
        if self.kip == 'bos':
            return z3.BoolVal(False)
        return self.brkv[k]

    def pq(self, a):
        Y = self.Y
        if a in Y.karar:
            return self.pqv[Y.dugum[a]]
        if a in Y.pq_sabit or a in self.sabit_pq:
            return z3.BoolVal(True)
        if a in Y.ayni:
            return self.pq(Y.ayni[a])
        return z3.BoolVal(False)

    def _memo(self, anahtar, kur):
        if anahtar in self._bel:
            return self._bel[anahtar]
        if anahtar in self._yigin:
            raise RuntimeError('bağımlılık döngüsü: %s' % (anahtar,))
        self._yigin.add(anahtar)
        v = kur()
        self._yigin.discard(anahtar)
        self._bel[anahtar] = v
        return v

    # ---------------- semantics
    def zaman(self, a):
        return z3.BoolVal(bool(self.Y.zaman.get(a, False)))

    def kirilir(self, a):
        Y = self.Y
        if a not in Y.imzali:
            return z3.BoolVal(False)
        return z3.And(self.brk(a), z3.Not(self.pq(a)), self.zaman(a))

    def klasik_alt_s(self, a):
        Y = self.Y
        terimler = []
        if a in Y.klasik_alt:
            terimler.append(z3.BoolVal(True))
        if a == 'a12_istek' and Y.crl_gunbatimi:
            terimler.append(self.etkin_sahte('e_crl'))
        return z3.Or(terimler) if terimler else z3.BoolVal(False)

    def kirilir_alt(self, a):
        Y = self.Y
        if a not in Y.imzali:
            return z3.BoolVal(False)
        return z3.And(self.brk(('alt', a)), self.pq(a), self.klasik_alt_s(a), self.zaman(a))

    def beklenir(self, x):
        def kur():
            Y = self.Y
            if not Y.beklenti_pol:
                return z3.BoolVal(False)
            pol = Y.kat['politika']
            kapsam_engeli = ('kapsam' in Y.mf_kapali) and Y.kat['faz'] in ('f1', 'f2')
            if kapsam_engeli:
                return z3.BoolVal(False)
            geri = ('tazelik' in Y.mf_kapali) and ('tekduzelik' in Y.mf_kapali)
            if geri:
                return z3.BoolVal(False)
            p3k = z3.And(self.brk('p3_kanal'), z3.BoolVal(Y.p3_zaman))
            yollar = []
            for c, m in Y.tasiyici[x]:
                if (c, x) not in Y.uygun:
                    continue
                t = z3.And(self.tav[(c, x)], z3.Not(self.etkin_sahte(c)))
                if pol == 'p3':
                    t = z3.And(t, z3.Not(p3k))
                yollar.append(t)
            return z3.Or(yollar) if yollar else z3.BoolVal(False)
        return self._memo(('bek', x), kur)

    def basar(self, a):
        def kur():
            Y = self.Y
            t = [self.kirilir(a)]
            if a not in Y.sabit:
                for b in sorted(Y.tanitici[a]):
                    t.append(self.etkin_sahte(b))
            t.append(z3.And(self.kirilir_alt(a), z3.Not(self.beklenir(a))))
            if a in Y.imzasiz:
                # unbound unsigned content; or PQ-bound but the unbound form is also accepted (coexistence)
                t.append(z3.Not(self.pq(a)))
                t.append(z3.And(self.pq(a), self.klasik_alt_s(a), z3.Not(self.beklenir(a))))
            return z3.Or(t)
        return self._memo(('basar', a), kur)

    def ulasir(self, a):
        Y = self.Y
        k = Y.kanal.get(a)
        if k in ('aktarilan', 'sunan_uc', 'kimliksiz'):
            return z3.BoolVal(True)
        if k in ('cekilen', 'yalniz_tasima'):
            t = [self.etkin_sahte(Y.tasima_anahtari[tt]) for tt in sorted(Y.tasima[a])]
            return z3.Or(t) if t else z3.BoolVal(False)
        return z3.BoolVal(False)          # anchored or without a channel

    def sahte(self, a):
        def kur():
            Y = self.Y
            if a in Y.ozgun:
                return z3.BoolVal(False)
            t = z3.And(self.basar(a), self.ulasir(a))
            if a in Y.imzasiz and a in Y.pq_baglar:        # if PQ-bound, the forgery of the artefact it is bound to
                t = z3.Or(t, z3.And(self.pq(a), self.etkin_sahte(Y.pq_baglar[a])))
            return t
        return self._memo(('sahte', a), kur)

    def varyant_etkin(self, a, av):
        return z3.Not(self.beklenir(a))

    def etkin_sahte(self, a):
        def kur():
            t = [self.sahte(a)]
            for av in self.Y.varyant[a]:
                t.append(z3.And(self.varyant_etkin(a, av), self.sahte(av)))
            return z3.Or(t)
        return self._memo(('es', a), kur)

    # ---------------- goals
    def ihlal(self, g):
        Y = self.Y
        if g == 'tum':
            return z3.Or([self.ihlal(h) for h in Y.ana])
        if g == 'g5':
            return self.g5_ihlal(Y.ana)
        t = [self.etkin_sahte(a) for a in sorted(Y.hedef[g])]
        if g in Y.politika_ihlali:
            t.append(z3.BoolVal(True))
        return z3.Or(t) if t else z3.BoolVal(False)

    def g5_ihlal(self, kapsam):
        """G5 (untimed): classical-only or unsigned acceptance of a migrated entity on the path."""
        Y = self.Y
        # build the 'yolda' relation downwards from the goals (reverse dependency; acyclic)
        ebeveyn = {}   # A -> [(X, kosul_ifadesi)]  A is on the path if it is on the path of X
        def ekle(a, x, kos):
            ebeveyn.setdefault(a, []).append((x, kos))
        for x in Y.mevcut:
            for b in Y.tanitici[x]:
                ekle(b, x, z3.BoolVal(True))
            for av in Y.varyant[x]:
                ekle(av, x, self.varyant_etkin(x, av))
            for c, m in Y.tasiyici[x]:
                if (c, x) in self.tav:
                    ekle(c, x, self.tav[(c, x)])
            for tt in Y.tasima[x]:
                ekle(Y.tasima_anahtari[tt], x, z3.BoolVal(True))
        hedef_kume = set()
        for g in kapsam:
            hedef_kume |= Y.hedef[g]
        bel, yig = {}, set()
        def yolda(a):
            if a in bel:
                return bel[a]
            if a in yig:
                raise RuntimeError('yolda döngüsü: %s' % a)
            yig.add(a)
            t = [z3.BoolVal(a in hedef_kume)]
            for x, kos in ebeveyn.get(a, []):
                t.append(z3.And(yolda(x), kos))
            yig.discard(a)
            bel[a] = z3.Or(t)
            return bel[a]
        t = []
        for a in sorted(Y.karar):
            ihl = [z3.And(self.klasik_alt_s(a), z3.Not(self.beklenir(a)))]
            for av in Y.varyant[a]:
                ihl.append(self.varyant_etkin(a, av))
            t.append(z3.And(yolda(a), self.pq(a), z3.Or(ihl)))
        return z3.Or(t) if t else z3.BoolVal(False)

    def hedef_formulu(self, hedefler):
        return z3.Or([self.ihlal(g) for g in hedefler])


def _atomlar(K):
    atom = [(('pq', a), v) for a, v in sorted(K.pqv.items())]
    atom += [(('tasi', c, x), v) for (c, x), v in sorted(K.tav.items())]
    return atom


def _ad(a):
    return 'pq(%s)' % a[1] if a[0] == 'pq' else 'tasi(%s,%s)' % (a[1], a[2])


def asgari_kumeler_z3(prm, hedefler, en_fazla=100000, O=None):
    """Independent z3 counterpart of asgari_kumeler in the ASP. Returns: (kumeler, bilgi).
    O: fact dictionary (default: the ecosystem); the regression instances pass their own facts."""
    t0 = time.perf_counter()
    Y = Yapi(prm, O)
    kat = prm['kat']
    wscd_yok = kat['wscd_pq'] == 'yok'
    if kat['saldirgan'] == 's1':
        kip, k = 'bos', None
    elif kat['k_sinir'] == 'sinirsiz':
        kip, k = 'tum', None
    else:
        kip, k = 'sembolik', {'k1': 1, 'k3': 3}[kat['k_sinir']]
    K = Kodlayici(Y, kip)
    ihl = K.hedef_formulu(hedefler)
    atom = _atomlar(K)
    tum_v = [v for _, v in atom]
    yasak = set(Y.yasak_dugum) | (set(Y.wscd_dugum) if wscd_yok else set())
    ek = [z3.Not(K.pqv[d]) for d in sorted(yasak) if d in K.pqv]
    dis = z3.Solver()
    dis.add(ek)
    ic = None
    if kip == 'sembolik':
        ic = z3.Solver()
        bv = list(K.brkv.values())
        ic.add(z3.AtMost(*(bv + [k])))
        ic.add(ihl)
        ic.add(ek)
    else:
        dis.add(z3.Not(ihl))

    def secim_varsayimlari(dogru):
        return [v if a in dogru else z3.Not(v) for a, v in atom]

    def karsi_ornek(dogru):
        """In symbolic mode: is there an attack with |B|≤k for the set dogru? If so, return B."""
        if ic.check(secim_varsayimlari(dogru)) == z3.sat:
            m = ic.model()
            return {kk: z3.is_true(m.eval(v, model_completion=True)) for kk, v in K.brkv.items()}
        return None

    def guvenli(dogru):
        if kip == 'sembolik':
            if any(('pq', d) in dogru for d in yasak):
                return False
            return karsi_ornek(dogru) is None
        return dis.check(secim_varsayimlari(dogru)) == z3.sat

    kumeler, n_cegar = [], 0
    while len(kumeler) < en_fazla:
        if dis.check() != z3.sat:
            break
        m = dis.model()
        dogru = {a for a, v in atom if z3.is_true(m.eval(v, model_completion=True))}
        if kip == 'sembolik':
            ko = karsi_ornek(dogru)
            if ko is not None:
                n_cegar += 1
                yerine = [(K.brkv[kk], z3.BoolVal(val)) for kk, val in ko.items()]
                dis.add(z3.Not(z3.substitute(ihl, *yerine)))
                continue
        degisti = True
        while degisti:
            degisti = False
            for a in sorted(dogru):
                deneme = dogru - {a}
                if guvenli(deneme):
                    dogru = deneme
                    degisti = True
                    break
        kumeler.append(tuple(sorted(_ad(a) for a in dogru)))
        dis.add(z3.Or([z3.Not(v) for a, v in atom if a in dogru]) if dogru else z3.BoolVal(False))
    bilgi = {'sure_s': round(time.perf_counter() - t0, 4), 'n': len(kumeler), 'cegar': n_cegar}
    return sorted(set(kumeler)), bilgi


def degerlendir_z3(prm, pq=(), tasi=(), hedefler=('g1', 'g2', 'g3', 'g4'), kirik=None, g5_kapsam=None, O=None):
    """Violated goals and forged artefacts for a fixed assignment + a fixed set of broken keys.
    kirik: None => the mode in the parameters (tum/bos); a set => only these keys can be broken."""
    Y = Yapi(prm, O)
    kat = prm['kat']
    if kirik is None:
        kip = 'bos' if kat['saldirgan'] == 's1' else 'tum'
    else:
        kip = 'sembolik'
    K = Kodlayici(Y, kip, sabit_pq=[a for a in pq if a in Y.mevcut and a not in Y.karar])
    yerine = [(v, z3.BoolVal(a in pq)) for a, v in K.pqv.items()]
    yerine += [(v, z3.BoolVal(ct in tasi)) for ct, v in K.tav.items()]
    if kip == 'sembolik':
        yerine += [(v, z3.BoolVal(kk in kirik)) for kk, v in K.brkv.items()]
    def deger(f):
        return z3.is_true(z3.simplify(z3.substitute(f, *yerine)))
    ihlal = set()
    for g in list(hedefler) + ['tum']:
        if g in Y.ana or g == 'tum':
            if deger(K.ihlal(g)):
                ihlal.add(g)
    kap = [g for g in (g5_kapsam if g5_kapsam is not None else hedefler) if g in Y.ana]
    if kap and deger(K.g5_ihlal(kap)):
        ihlal.add('g5')
    if deger(K.ihlal('g2i')):
        ihlal.add('g2i')
    sahte = {a for a in sorted(Y.mevcut) if deger(K.sahte(a))}
    return {'ihlal': ihlal, 'sahte': sahte}
