"""Boundary cases (the known answers can be derived by hand).

- T1: X = c, c+1, u−1, u; variation of n_eff (20…31); n_eff < 20; all targets undetermined.
- McNemar: 0 discordant pairs; one-directional discordance.
- Fisher and conditional OR: empty cell, empty row/column, completely empty table.
- Holm: ordering, ties, the α/k boundary (exact arithmetic), permutation invariance, a test that cannot be computed.
- Wilson: end points x = 0 and x = n; n = 0.
- Newcombe: symmetry and transposition.
"""
from __future__ import annotations

import itertools
import math
import unittest
from fractions import Fraction

from _ortak import analiz, analiz_sozluk, kesin, n31_hedefleri, referans, veri_seti, y_ata


class T1Karari(unittest.TestCase):
    """analiz.t1_karari(X, n): PR §3.7, §2B.5, §6.3, §6.13."""

    def test_sinirlar_n20_31(self):
        for n in range(20, 32):
            kd = kesin.kritik_degerler(n)
            c, u = kd.c, kd.u
            beklenen = {c: "destek", c + 1: "belirsiz", u - 1: "belirsiz", u: "yanlislama"}
            for X, karar in beklenen.items():
                with self.subTest(n=n, X=X):
                    self.assertEqual(analiz.t1_karari(X, n)["karar"], karar)
            # p-value and threshold decision are consistent: support ⇔ P(X' ≤ X) ≤ 0.05; falsification ⇔ P(X' ≥ X) ≤ 0.05
            for X in range(0, n + 1):
                with self.subTest(n=n, X=X, tur="p-tutarlilik"):
                    k = analiz.t1_karari(X, n)
                    self.assertEqual(k["karar"] == "destek", kesin.binom_alt_p(X, n) <= Fraction(1, 20))
                    self.assertEqual(k["karar"] == "yanlislama", kesin.binom_ust_p(X, n) <= Fraction(1, 20))

    def test_n31_somut(self):
        self.assertEqual(analiz.t1_karari(10, 31)["karar"], "destek")
        self.assertEqual(analiz.t1_karari(11, 31)["karar"], "belirsiz")
        self.assertEqual(analiz.t1_karari(20, 31)["karar"], "belirsiz")
        self.assertEqual(analiz.t1_karari(21, 31)["karar"], "yanlislama")
        k = analiz.t1_karari(10, 31)
        self.assertEqual((k["c"], k["u"]), (10, 21))

    def test_n_eff_20_alti_tanimlayici(self):
        for n in (0, 1, 5, 19):
            for X in sorted({0, n // 2, n}):
                with self.subTest(n=n, X=X):
                    self.assertEqual(analiz.t1_karari(X, n)["karar"], "tanimlayici")

    def test_n_eff_degisimi_esikleri_yeniden_hesaplar(self):
        # Same X = 10: n_eff 31 → support; n_eff 29 → c(29) = 9 → undetermined
        h = n31_hedefleri()
        s31 = analiz_sozluk(veri_seti(y_ata(h, birler=10)))
        self.assertEqual(s31["T1"]["n_eff"], 31)
        self.assertEqual(s31["T1"]["karar"], "destek")
        s29 = analiz_sozluk(veri_seti(y_ata(h, birler=10, gecersiz=2)))
        self.assertEqual(s29["T1"]["n_eff"], 29)
        self.assertEqual((s29["T1"]["c"], s29["T1"]["u"]), (9, 20))
        self.assertEqual(s29["T1"]["karar"], "belirsiz")

    def test_butun_hedefler_belirsiz(self):
        h = y_ata(n31_hedefleri(), birler=0, belirsiz=31)
        s = analiz_sozluk(veri_seti(h))
        self.assertEqual(s["T1"]["n_eff"], 0)
        self.assertEqual(s["T1"]["karar"], "tanimlayici")
        self.assertIsNone(s["T1"]["wilson"])
        self.assertEqual(s["H6_hukmu"]["hukum"], "tanimlayici")
        # The sensitivity analyses are still computed: (i) X = 31/31 → falsification; (ii) X = 0/31 → support
        self.assertEqual(s["T1_duyarlilik"]["i_belirsiz_1"]["X"], 31)
        self.assertEqual(s["T1_duyarlilik"]["i_belirsiz_1"]["karar"], "yanlislama")
        self.assertEqual(s["T1_duyarlilik"]["ii_belirsiz_0"]["X"], 0)
        self.assertEqual(s["T1_duyarlilik"]["ii_belirsiz_0"]["karar"], "destek")


class McNemarSinir(unittest.TestCase):
    def test_uyumsuz_cift_yok(self):
        for b_c in [(0, 0)]:
            self.assertEqual(kesin.mcnemar_kesin(*b_c), Fraction(1))
            self.assertEqual(referans.mcnemar_kesin(*b_c), 1.0)

    def test_tek_yonlu_uyumsuzluk(self):
        # b = 0, c = k: p = min(1, 2 · 0.5^k)
        for k in range(1, 25):
            with self.subTest(k=k):
                beklenen = min(Fraction(1), 2 * Fraction(1, 2 ** k))
                self.assertEqual(kesin.mcnemar_kesin(0, k), beklenen)
                self.assertEqual(kesin.mcnemar_kesin(k, 0), beklenen)
                self.assertAlmostEqual(referans.mcnemar_kesin(0, k), float(beklenen), delta=1e-15)

    def test_esit_uyumsuzluk_p1(self):
        for k in range(0, 20):
            with self.subTest(k=k):
                self.assertEqual(kesin.mcnemar_kesin(k, k), Fraction(1))

    def test_t2_uyumsuzsuz_veri(self):
        # F_K = F_T for all TK1/TK2 targets => b = c = 0 => p = 1, difference = 0
        h = n31_hedefleri()
        for i, x in enumerate(h):
            x["tk_sinifi"] = "TK1" if i % 2 else "TK2"
            x["F_K"] = x["F_T"] = i % 3 == 0 and 1 or 0
        s = analiz_sozluk(veri_seti(h))
        self.assertEqual((s["T2"]["b"], s["T2"]["c"]), (0, 0))
        self.assertEqual(s["T2"]["p"]["kesin"], "1")
        self.assertEqual(s["T2"]["etki"]["fark"], 0.0)


class FisherSinir(unittest.TestCase):
    def test_bos_hucre(self):
        # [[0, 5], [5, 0]]: one-sided extreme table
        p = kesin.fisher_iki_yonlu(0, 5, 5, 0)
        self.assertEqual(p, Fraction(2, math.comb(10, 5)))
        self.assertAlmostEqual(referans.fisher_iki_yonlu(0, 5, 5, 0), float(p), delta=1e-15)

    def test_bos_satir_sutun_ve_tamamen_bos(self):
        for tablo in [(0, 0, 3, 4), (3, 4, 0, 0), (0, 3, 0, 4), (3, 0, 4, 0), (0, 0, 0, 0)]:
            with self.subTest(tablo=tablo):
                self.assertEqual(kesin.fisher_iki_yonlu(*tablo), Fraction(1))
                self.assertEqual(referans.fisher_iki_yonlu(*tablo), 1.0)
                mle, alt, ust = kesin.kosullu_or(*tablo)
                self.assertTrue(math.isnan(mle))
                self.assertEqual((alt, ust), (0.0, math.inf))
                mle_r, alt_r, ust_r = referans.kosullu_or(*tablo)
                self.assertTrue(math.isnan(mle_r))
                self.assertEqual((alt_r, ust_r), (0.0, math.inf))

    def test_or_uc_noktalari(self):
        # a at the lower end of the support => MLE = 0 and CI lower = 0; at the upper end => MLE = ∞ and CI upper = ∞
        mle, alt, ust = kesin.kosullu_or(0, 4, 3, 2)
        self.assertEqual((mle, alt), (0.0, 0.0))
        self.assertTrue(0 < ust < math.inf)
        mle, alt, ust = kesin.kosullu_or(4, 0, 2, 3)
        self.assertEqual((mle, ust), (math.inf, math.inf))
        self.assertTrue(0 < alt < math.inf)

    def test_or_bir_esit_marjinal_simetri(self):
        # Swapping the rows gives OR → 1/OR; CI → (1/upper, 1/lower)
        for tablo in [(3, 2, 1, 4), (5, 1, 2, 2), (7, 3, 3, 9)]:
            a, b, c, d = tablo
            with self.subTest(tablo=tablo):
                m1, a1, u1 = kesin.kosullu_or(a, b, c, d)
                m2, a2, u2 = kesin.kosullu_or(c, d, a, b)
                self.assertTrue(math.isclose(m1, 1 / m2, rel_tol=1e-12))
                self.assertTrue(math.isclose(a1, 1 / u2, rel_tol=1e-12))
                self.assertTrue(math.isclose(u1, 1 / a2, rel_tol=1e-12))

    def test_or_ga_p_tutarliligi(self):
        # The conditional exact CI excludes 1 exactly when twice the one-sided exact p ≤ 0.05 (not Fisher's two-sided p).
        for a, b, c, d in [(8, 2, 1, 9), (6, 4, 2, 8), (10, 0, 3, 7), (2, 8, 8, 2)]:
            with self.subTest(tablo=(a, b, c, d)):
                _, alt, ust = kesin.kosullu_or(a, b, c, d)
                r1, r2, c1 = a + b, c + d, a + c
                N = r1 + r2
                lo, hi = max(0, c1 - r2), min(r1, c1)
                P = {k: Fraction(math.comb(r1, k) * math.comb(r2, c1 - k), math.comb(N, c1)) for k in range(lo, hi + 1)}
                ust_kuyruk = sum(v for k, v in P.items() if k >= a)
                alt_kuyruk = sum(v for k, v in P.items() if k <= a)
                # ψ_L > 1 ⇔ P(X ≥ a; ψ=1) < α/2 ; ψ_U < 1 ⇔ P(X ≤ a; ψ=1) < α/2 (the tails are monotone in ψ)
                self.assertEqual(alt > 1, ust_kuyruk < Fraction(1, 40))
                self.assertEqual(ust < 1, alt_kuyruk < Fraction(1, 40))


class HolmSinir(unittest.TestCase):
    AILE = ("T2", "T3", "T4", "T5")

    def test_bilinen_ornek(self):
        p = {"T2": Fraction(1, 100), "T3": Fraction(4, 100), "T4": Fraction(3, 100), "T5": Fraction(5, 1000)}
        h = kesin.holm(p)
        # order: T5 (0.005) → ×4 = 0.02; T2 (0.01) → ×3 = 0.03; T4 (0.03) → ×2 = 0.06; T3 (0.04) → ×1 → max(0.06, 0.04) = 0.06
        self.assertEqual([k for k, _ in sorted(h.items(), key=lambda kv: kv[1]["sira"])], ["T5", "T2", "T4", "T3"])
        self.assertEqual(h["T5"]["p_duzeltilmis"], Fraction(2, 100))
        self.assertEqual(h["T2"]["p_duzeltilmis"], Fraction(3, 100))
        self.assertEqual(h["T4"]["p_duzeltilmis"], Fraction(6, 100))
        self.assertEqual(h["T3"]["p_duzeltilmis"], Fraction(6, 100))
        self.assertEqual({k: v["red"] for k, v in h.items()}, {"T5": True, "T2": True, "T4": False, "T3": False})

    def test_esitlikler(self):
        p = {"T2": Fraction(1, 50), "T3": Fraction(1, 50), "T4": Fraction(1, 50), "T5": Fraction(1, 2)}
        h = kesin.holm(p)
        # Equal p values: the adjusted values do not depend on the order: max(4p, 3p, 2p) = 4p = 0.08
        for k in ("T2", "T3", "T4"):
            self.assertEqual(h[k]["p_duzeltilmis"], Fraction(8, 100))
            self.assertFalse(h[k]["red"])
        # Ties are broken by the PR family order (T2 < T3 < T4)
        self.assertEqual([h[k]["sira"] for k in ("T2", "T3", "T4", "T5")], [1, 2, 3, 4])

    def test_alfa_bolu_k_siniri_kesin(self):
        # p_(1) = α/4 exactly at the boundary => reject (≤); p_(2) = α/3 exactly at the boundary => reject
        p = {"T2": Fraction(1, 80), "T3": Fraction(1, 60), "T4": Fraction(1, 2), "T5": Fraction(9, 10)}
        h = kesin.holm(p)
        self.assertTrue(h["T2"]["red"])
        self.assertTrue(h["T3"]["red"])
        self.assertEqual(h["T2"]["p_duzeltilmis"], Fraction(1, 20))
        self.assertEqual(h["T3"]["p_duzeltilmis"], Fraction(1, 20))
        self.assertFalse(h["T4"]["red"])
        # One step above the boundary => no rejection, and none of the following ones is rejected (step-down stops)
        p2 = dict(p, T2=Fraction(1, 80) + Fraction(1, 10 ** 12))
        h2 = kesin.holm(p2)
        self.assertFalse(h2["T2"]["red"])
        self.assertFalse(h2["T3"]["red"])  # T3 adjusted = max(4·p2, 3·(1/60)) > α

    def test_permutasyon_degismezligi(self):
        tabanlar = [Fraction(1, 100), Fraction(1, 100), Fraction(3, 100), Fraction(7, 10)]
        referans_sonuc = None
        for perm in itertools.permutations(tabanlar):
            p = dict(zip(self.AILE, perm))
            h = kesin.holm(p)
            imza = sorted((v["p"], v["p_duzeltilmis"], v["red"]) for v in h.values())
            if referans_sonuc is None:
                referans_sonuc = imza
            self.assertEqual(imza, referans_sonuc)

    def test_kutuphane_ile_ayni(self):
        p = {"T2": 0.01, "T3": 0.04, "T4": 0.03, "T5": 0.005}
        hk = kesin.holm({k: Fraction(v) for k, v in p.items()})
        hr = referans.holm(p)
        for k in p:
            self.assertAlmostEqual(float(hk[k]["p_duzeltilmis"]), hr[k]["p_duzeltilmis"], delta=1e-15)
            self.assertEqual(hk[k]["red"], hr[k]["red"])

    def test_hepsi_bir(self):
        h = kesin.holm({k: Fraction(1) for k in self.AILE})
        self.assertTrue(all(v["p_duzeltilmis"] == 1 and not v["red"] for v in h.values()))


class WilsonSinir(unittest.TestCase):
    def test_uc_noktalar_kesin(self):
        for n in range(1, 41):
            with self.subTest(n=n):
                alt0, ust0 = kesin.wilson(0, n)
                self.assertEqual(alt0, 0.0)
                altn, ustn = kesin.wilson(n, n)
                self.assertEqual(ustn, 1.0)
                # symmetry: W(x, n) = 1 − W(n − x, n) reversed
                for x in range(0, n + 1):
                    a1, u1 = kesin.wilson(x, n)
                    a2, u2 = kesin.wilson(n - x, n)
                    self.assertAlmostEqual(a1, 1 - u2, delta=1e-15)
                    self.assertAlmostEqual(u1, 1 - a2, delta=1e-15)

    def test_n_sifir(self):
        self.assertIsNone(kesin.wilson(0, 0))
        self.assertIsNone(referans.wilson(0, 0))


class NewcombeSinir(unittest.TestCase):
    def test_eslestirilmis_transpozisyon(self):
        # Swapping the conditions (b ↔ c): difference → −difference; CI → (−upper, −lower)
        for a, b, c, d in [(20, 12, 2, 16), (1, 1, 7, 12), (0, 3, 0, 5), (4, 0, 0, 4), (2, 5, 1, 0)]:
            with self.subTest(tablo=(a, b, c, d)):
                f1, a1, u1, _ = kesin.newcombe_eslestirilmis(a, b, c, d)
                f2, a2, u2, _ = kesin.newcombe_eslestirilmis(a, c, b, d)
                self.assertAlmostEqual(f1, -f2, delta=1e-15)
                self.assertAlmostEqual(a1, -u2, delta=1e-15)
                self.assertAlmostEqual(u1, -a2, delta=1e-15)

    def test_eslestirilmis_uyumsuzsuz_simetrik(self):
        # b = c = 0 => difference 0 and the CI is symmetric about 0
        for a, d in [(3, 5), (0, 9), (7, 0), (10, 10)]:
            with self.subTest(a=a, d=d):
                f, alt, ust, _ = kesin.newcombe_eslestirilmis(a, 0, 0, d)
                self.assertEqual(f, 0.0)
                self.assertAlmostEqual(alt, -ust, delta=1e-15)
                self.assertLessEqual(alt, 0.0)

    def test_bagimsiz_grup_degisimi(self):
        f1, a1, u1 = kesin.newcombe_bagimsiz(5, 56, 0, 29)
        f2, a2, u2 = kesin.newcombe_bagimsiz(0, 29, 5, 56)
        self.assertAlmostEqual(f1, -f2, delta=1e-15)
        self.assertAlmostEqual(a1, -u2, delta=1e-15)
        self.assertAlmostEqual(u1, -a2, delta=1e-15)

    def test_aralik_sinirlari(self):
        # stays within [−1, 1] and contains the point estimate
        for a, b, c, d in itertools.product(range(0, 4), repeat=4):
            if a + b + c + d == 0:
                continue
            f, alt, ust, _ = kesin.newcombe_eslestirilmis(a, b, c, d)
            self.assertTrue(-1 - 1e-15 <= alt <= f <= ust <= 1 + 1e-15, (a, b, c, d, alt, f, ust))

    def test_bos_tablo(self):
        self.assertIsNone(kesin.newcombe_eslestirilmis(0, 0, 0, 0))
        self.assertIsNone(kesin.newcombe_bagimsiz(0, 0, 3, 5))


class GecersizArguman(unittest.TestCase):
    def test_negatif_hucre_reddedilir(self):
        for islev, arg in [(kesin.mcnemar_kesin, (-1, 2)), (kesin.fisher_iki_yonlu, (1, -1, 2, 3)),
                           (kesin.kosullu_or, (1, 2, -3, 4)), (kesin.newcombe_eslestirilmis, (0, 1, 2, -1)),
                           (kesin.newcombe_bagimsiz, (5, 3, 1, 2)), (kesin.wilson, (4, 3))]:
            with self.subTest(islev=islev.__name__):
                with self.assertRaises(ValueError):
                    islev(*arg)


if __name__ == "__main__":
    unittest.main()
