"""Known-answer tests: PR Annex A (n = 20…40), §2B.5 (n = 31), §6.13 threshold table,
§6.6 T1-Holm note, §6.14 power note and the Wilson widths in Annex A.

The expected values were copied VERBATIM from the PR text (00-on-kayit/ON-KAYIT-TASLAK.md, draft v0.6).
Every value is reproduced both with our own exact implementation (fractions/math.comb) and with scipy.
"""
from __future__ import annotations

import unittest
from fractions import Fraction
from math import comb

from _ortak import kesin, referans

# PR Annex A table (lines 1212–1222): n -> (c, "P(X<=c)" to 4 decimals, u)
EK_A = {
    20: (5, "0.0207", 15), 21: (6, "0.0392", 15), 22: (6, "0.0262", 16), 23: (7, "0.0466", 16),
    24: (7, "0.0320", 17), 25: (7, "0.0216", 18), 26: (8, "0.0378", 18), 27: (8, "0.0261", 19),
    28: (9, "0.0436", 19), 29: (9, "0.0307", 20), 30: (10, "0.0494", 20), 31: (10, "0.0354", 21),
    32: (10, "0.0251", 22), 33: (11, "0.0401", 22), 34: (11, "0.0288", 23), 35: (12, "0.0448", 23),
    36: (12, "0.0326", 24), 37: (13, "0.0494", 24), 38: (13, "0.0365", 25), 39: (13, "0.0266", 26),
    40: (14, "0.0403", 26),
}


def yuvarlanmis_esit(deger, metin: str) -> bool:
    """Is `deger` equal to `metin` when rounded to the number of decimal places of `metin`?
    (|deger − metin| ≤ half a unit; with an exact fraction.)"""
    basamak = len(metin.split(".")[1]) if "." in metin else 0
    hedef = Fraction(metin)
    yarim = Fraction(1, 2 * 10 ** basamak)
    return abs(Fraction(deger) - hedef) <= yarim


class EkATablosu(unittest.TestCase):
    def test_ek_a_n20_40_kendi_uygulama(self):
        for n, (c, p_metin, u) in EK_A.items():
            with self.subTest(n=n):
                kd = kesin.kritik_degerler(n)
                self.assertEqual(kd.c, c)
                self.assertEqual(kd.u, u)
                self.assertTrue(yuvarlanmis_esit(kd.P_c, p_metin), (n, float(kd.P_c), p_metin))
                self.assertEqual(kd.u, n - kd.c)  # Annex A: u = n − c

    def test_ek_a_n20_40_scipy(self):
        for n, (c, p_metin, u) in EK_A.items():
            with self.subTest(n=n):
                c_r, u_r, p_r = referans.kritik_degerler(n)
                self.assertEqual((c_r, u_r), (c, u))
                self.assertTrue(yuvarlanmis_esit(p_r, p_metin), (n, p_r, p_metin))

    def test_ek_a_tanimi_en_buyuk_c(self):
        # c: the LARGEST value with P(X ≤ c) ≤ 0.05 => P(X ≤ c+1) > 0.05
        for n in EK_A:
            with self.subTest(n=n):
                kd = kesin.kritik_degerler(n)
                self.assertLessEqual(kesin.binom_cdf(kd.c, n), Fraction(1, 20))
                self.assertGreater(kesin.binom_cdf(kd.c + 1, n), Fraction(1, 20))

    def test_ek_a_simetri_ust_kuyruk(self):
        # u = n − c and P(X ≥ u) = P(X ≤ c) (symmetry at p0 = 0.5); the falsification tail is also ≤ 0.05
        for n in EK_A:
            with self.subTest(n=n):
                kd = kesin.kritik_degerler(n)
                self.assertEqual(kesin.binom_sf(kd.u, n), kd.P_c)
                self.assertLessEqual(kesin.binom_sf(kd.u, n), Fraction(1, 20))
                self.assertGreater(kesin.binom_sf(kd.u - 1, n), Fraction(1, 20))


class N31(unittest.TestCase):
    """PR §2B.5: for n_eff = 31, support X ≤ 10, falsification X ≥ 21; P = 0.0354."""

    def test_n31_esikler(self):
        kd = kesin.kritik_degerler(31)
        self.assertEqual((kd.c, kd.u), (10, 21))

    def test_n31_kesin_olasilik(self):
        beklenen = Fraction(sum(comb(31, k) for k in range(11)), 2 ** 31)
        kd = kesin.kritik_degerler(31)
        self.assertEqual(kd.P_c, beklenen)
        self.assertTrue(yuvarlanmis_esit(kd.P_c, "0.0354"))
        self.assertEqual(kesin.binom_alt_p(10, 31), beklenen)
        self.assertEqual(kesin.binom_ust_p(21, 31), beklenen)  # P(X ≥ 21) = P(X ≤ 10)

    def test_n31_bir_fazlasi_esigi_asar(self):
        self.assertGreater(kesin.binom_cdf(11, 31), Fraction(1, 20))
        self.assertGreater(kesin.binom_sf(20, 31), Fraction(1, 20))

    def test_n31_scipy(self):
        c, u, p = referans.kritik_degerler(31)
        self.assertEqual((c, u), (10, 21))
        self.assertAlmostEqual(p, float(kesin.kritik_degerler(31).P_c), delta=1e-12)
        self.assertAlmostEqual(referans.binom_alt_p(10, 31), p, delta=1e-12)


class Tablo613(unittest.TestCase):
    """PR §6.13 binomial threshold table and Annex A Wilson widths."""

    SATIRLAR = {25: (18, 7, "33"), 30: (20, 10, "31"), 40: (26, 14, "27")}   # n: (majority ≥, absence ≤, ≈width)
    GENISLIK_EK_A = {25: (18, "33.3"), 30: (21, "31.2"), 40: (28, "27.4")}   # n: (k, width in points)

    def test_esikler(self):
        for n, (ust, alt, _) in self.SATIRLAR.items():
            with self.subTest(n=n):
                kd = kesin.kritik_degerler(n)
                self.assertEqual(kd.c, alt)
                self.assertEqual(kd.u, ust)

    def test_wilson_genislikleri_ek_a(self):
        for n, (k, metin) in self.GENISLIK_EK_A.items():
            with self.subTest(n=n, k=k):
                alt, ust = kesin.wilson(k, n)
                self.assertTrue(yuvarlanmis_esit((ust - alt) * 100, metin), ((ust - alt) * 100, metin))
                a_r, u_r = referans.wilson(k, n)
                self.assertTrue(yuvarlanmis_esit((u_r - a_r) * 100, metin))

    def test_wilson_genislikleri_613_yaklasik(self):
        # §6.13: "(at the 70% level)" ≈33 / ≈31 / ≈27 points
        for n, (_, _, metin) in self.SATIRLAR.items():
            k = self.GENISLIK_EK_A[n][0]
            with self.subTest(n=n):
                alt, ust = kesin.wilson(k, n)
                self.assertTrue(yuvarlanmis_esit((ust - alt) * 100, metin))


class Not66Holm(unittest.TestCase):
    """PR §6.6: if T1 were included in Holm (5 tests), the n=30 threshold would be ≤8 / ≥22; P(X≤8)=0.0081; P(X≤9)=0.0214."""

    def test_holm_ile_n30(self):
        kd = kesin.kritik_degerler(30, alfa=Fraction(1, 100))   # α/5 = 0.01
        self.assertEqual((kd.c, kd.u), (8, 22))
        self.assertTrue(yuvarlanmis_esit(kesin.binom_cdf(8, 30), "0.0081"))
        self.assertTrue(yuvarlanmis_esit(kesin.binom_cdf(9, 30), "0.0214"))


class Not614Guc(unittest.TestCase):
    """PR §6.14: n=30, power for X ≤ 10 0.974 / 0.73 / 0.29; for X ≥ 20 (p=0.7) 0.73."""

    def test_guc(self):
        self.assertTrue(yuvarlanmis_esit(kesin.binom_cdf(10, 30, Fraction(1, 5)), "0.974"))
        self.assertTrue(yuvarlanmis_esit(kesin.binom_cdf(10, 30, Fraction(3, 10)), "0.73"))
        self.assertTrue(yuvarlanmis_esit(kesin.binom_cdf(10, 30, Fraction(2, 5)), "0.29"))
        self.assertTrue(yuvarlanmis_esit(kesin.binom_sf(20, 30, Fraction(7, 10)), "0.73"))

    def test_guc_scipy(self):
        from scipy import stats
        self.assertAlmostEqual(stats.binom.cdf(10, 30, 0.2), float(kesin.binom_cdf(10, 30, Fraction(1, 5))), delta=1e-12)
        self.assertAlmostEqual(stats.binom.sf(19, 30, 0.7), float(kesin.binom_sf(20, 30, Fraction(7, 10))), delta=1e-12)


class GenelKural(unittest.TestCase):
    """General properties of the Annex A rule (n = 1…100): both implementations agree; c(n+1) ≤ c(n) + 1; no c for small n."""

    def test_iki_uygulama_ve_monotonluk(self):
        onceki = None
        for n in range(1, 101):
            with self.subTest(n=n):
                kd = kesin.kritik_degerler(n)
                c_r, u_r, _ = referans.kritik_degerler(n)
                self.assertEqual((kd.c, kd.u), (c_r, u_r))
                if onceki is not None and kd.c is not None and onceki.c is not None:
                    self.assertLessEqual(kd.c, onceki.c + 1)
                    self.assertGreaterEqual(kd.c, onceki.c)
                onceki = kd

    def test_kucuk_n_esik_yok(self):
        # n ≤ 4: P(X ≤ 0) = 0.5^n > 0.05 => c undefined (support impossible)
        for n in range(1, 5):
            with self.subTest(n=n):
                self.assertIsNone(kesin.kritik_degerler(n).c)
                self.assertIsNone(kesin.kritik_degerler(n).u)
        self.assertEqual(kesin.kritik_degerler(5).c, 0)


if __name__ == "__main__":
    unittest.main()
