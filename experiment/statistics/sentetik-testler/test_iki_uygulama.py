"""Comparison of the two independent implementations on every synthetic case.

A = own exact implementation (`c3istat.kesin`: fractions / math.comb / decimal; standard library only)
B = library implementation (`c3istat.referans`: scipy / statsmodels / numpy)

The tolerances are in `c3istat.yapilandirma.TOLERANSLAR`. A disagreement = an error.
The case grids are exhaustive (all tables up to the stated bound). Additional random cases are generated
with fixed TEST seeds (separate from the PR analysis seeds; FREEZE-INPUT.md §5).
"""
from __future__ import annotations

import itertools
import random
import unittest
from fractions import Fraction

from _ortak import SAYAC, bootstrap, karsilastir, kesin, referans, say

TEST_TOHUMU_FISHER = 910001
TEST_TOHUMU_OR = 910002
TEST_TOHUMU_HOLM = 910003
TEST_TOHUMU_BOOT = 910004
TEST_TOHUMU_NEWCOMBE = 910005


def tablolar(N_max: int):
    """All 2×2 tables (a, b, c, d) whose total does not exceed N_max."""
    for N in range(0, N_max + 1):
        for a in range(N + 1):
            for b in range(N - a + 1):
                for c in range(N - a - b + 1):
                    yield a, b, c, N - a - b - c


def rastgele_tablolar(rng: random.Random, adet: int, N_alt: int, N_ust: int):
    for _ in range(adet):
        N = rng.randint(N_alt, N_ust)
        kesimler = sorted(rng.randint(0, N) for _ in range(3))
        yield kesimler[0], kesimler[1] - kesimler[0], kesimler[2] - kesimler[1], N - kesimler[2]


class Supurme(unittest.TestCase):
    def _bitir(self, aile):
        s = SAYAC[aile]
        self.assertGreater(s["vaka"], 0)
        self.assertEqual(s["uyumlu_vaka"], s["vaka"], f"{aile}: {s['ilk_uyusmazliklar']}")

    def test_binom_p_degerleri(self):
        for n in range(1, 61):
            for x in range(0, n + 1):
                k = karsilastir.Karsilastirici()
                k.ekle("alt_p", kesin.binom_alt_p(x, n), referans.binom_alt_p(x, n), "p")
                k.ekle("ust_p", kesin.binom_ust_p(x, n), referans.binom_ust_p(x, n), "p")
                say("binom_T1_T5", k)
        self._bitir("binom_T1_T5")

    def test_kritik_degerler(self):
        for n in range(1, 101):
            k = karsilastir.Karsilastirici()
            kd = kesin.kritik_degerler(n)
            c_r, u_r, p_r = referans.kritik_degerler(n)
            k.ekle("c", kd.c, c_r, "tam")
            k.ekle("u", kd.u, u_r, "tam")
            k.ekle("P_c", kd.P_c, p_r, "p")
            say("ek_a_kurali", k)
        self._bitir("ek_a_kurali")

    def test_mcnemar(self):
        for b in range(0, 41):
            for c in range(0, 41 - b):
                k = karsilastir.Karsilastirici()
                k.ekle("p", kesin.mcnemar_kesin(b, c), referans.mcnemar_kesin(b, c), "p")
                say("mcnemar_T2", k)
        self._bitir("mcnemar_T2")

    def test_fisher(self):
        vakalar = list(tablolar(20))
        vakalar += list(rastgele_tablolar(random.Random(TEST_TOHUMU_FISHER), 1000, 21, 40))
        for t in vakalar:
            k = karsilastir.Karsilastirici()
            k.ekle("p", kesin.fisher_iki_yonlu(*t), referans.fisher_iki_yonlu(*t), "p")
            say("fisher_T3_T4", k)
        self._bitir("fisher_T3_T4")

    def test_wilson(self):
        for n in range(0, 81):
            for x in range(0, n + 1):
                k = karsilastir.Karsilastirici()
                k.ekle("wilson", kesin.wilson(x, n), referans.wilson(x, n), "ga")
                say("wilson", k)
        self._bitir("wilson")

    def test_newcombe_bagimsiz(self):
        vakalar = [(x1, n1, x2, n2) for n1 in range(1, 16) for n2 in range(1, 16)
                   for x1 in range(n1 + 1) for x2 in range(n2 + 1)]
        rng = random.Random(TEST_TOHUMU_NEWCOMBE)
        for _ in range(2000):
            n1, n2 = rng.randint(1, 31), rng.randint(1, 31)
            vakalar.append((rng.randint(0, n1), n1, rng.randint(0, n2), n2))
        for v in vakalar:
            k = karsilastir.Karsilastirici()
            k.ekle("newcombe10_bagimsiz", kesin.newcombe_bagimsiz(*v), referans.newcombe_bagimsiz(*v), "ga")
            say("newcombe_bagimsiz_T3_T4", k)
        self._bitir("newcombe_bagimsiz_T3_T4")

    def test_newcombe_eslestirilmis(self):
        vakalar = [t for t in tablolar(18) if sum(t) > 0]
        vakalar += [t for t in rastgele_tablolar(random.Random(TEST_TOHUMU_NEWCOMBE + 1), 1500, 19, 31)]
        for t in vakalar:
            k = karsilastir.Karsilastirici()
            k.ekle("newcombe10_eslestirilmis", kesin.newcombe_eslestirilmis(*t), referans.newcombe_eslestirilmis(*t), "ga")
            k.ekle("phi_duz", kesin.newcombe_eslestirilmis(*t, phi_turu="duz"),
                   referans.newcombe_eslestirilmis(*t, phi_turu="duz"), "ga")
            say("newcombe_eslestirilmis_T2", k)
        self._bitir("newcombe_eslestirilmis_T2")

    def test_newcombe_eslestirilmis_phi0_statsmodels_bagimsiz(self):
        """Independent library check: at φ = 0 the paired formula must equal the independent 'newcomb'
        interval of statsmodels on the margins (n1 = n2 = N). This tests the combination step, the only
        part of the paired code path outside the library, against statsmodels."""
        for t in tablolar(16):
            if sum(t) == 0:
                continue
            a, b, c, d = t
            N = sum(t)
            k = karsilastir.Karsilastirici()
            k.ekle("phi0_vs_statsmodels", kesin.newcombe_eslestirilmis(a, b, c, d, phi_turu="sifir")[:3],
                   referans.newcombe_bagimsiz(a + b, N, a + c, N), "ga")
            say("newcombe_phi0_statsmodels", k)
        self._bitir("newcombe_phi0_statsmodels")

    def test_kosullu_or(self):
        vakalar = list(tablolar(10))
        vakalar += list(rastgele_tablolar(random.Random(TEST_TOHUMU_OR), 300, 11, 31))
        for t in vakalar:
            k = karsilastir.Karsilastirici()
            k.ekle("or_kosullu", kesin.kosullu_or(*t), referans.kosullu_or(*t), "or")
            say("kosullu_or_T3_T4", k)
        self._bitir("kosullu_or_T3_T4")

    def test_holm(self):
        rng = random.Random(TEST_TOHUMU_HOLM)
        # Discrete pool with boundary values and ties + continuous random values
        havuz = [0.0, 1e-6, 0.001, 0.005, 0.01, 0.0125, 0.05 / 3, 0.02, 0.025, 0.04, 0.05, 0.06, 0.1, 0.5, 1.0]
        vakalar = [tuple(v) for v in itertools.product([0.001, 0.0125, 0.025, 0.05], repeat=4)]
        for _ in range(3000):
            vakalar.append(tuple(rng.choice(havuz) if rng.random() < 0.5 else rng.random() ** 3 for _ in range(4)))
        for v in vakalar:
            p = dict(zip(("T2", "T3", "T4", "T5"), v))
            k = karsilastir.Karsilastirici()
            karsilastir.holm_karsilastir(k, kesin.holm({kk: Fraction(vv) for kk, vv in p.items()},
                                                       alfa=Fraction(0.05)), referans.holm(p))
            say("holm_T2_T5", k)
        self._bitir("holm_T2_T5")

    def test_bootstrap_numpy_ve_saf(self):
        rng = random.Random(TEST_TOHUMU_BOOT)
        veri_setleri = []
        for i in range(30):
            kk = rng.randint(1, 31)
            kumeler = []
            for j in range(kk):
                m = rng.randint(0, 20)
                kumeler.append((f"S-{j:02d}", rng.randint(0, m), m))
            veri_setleri.append((kumeler, 2000))
        veri_setleri.append(([(f"S-{j:02d}", j % 4, 10) for j in range(31)], 10000))
        veri_setleri.append(([(f"S-{j:02d}", (7 * j) % 11, 11 + j % 3) for j in range(25)], 10000))
        for kumeler, B in veri_setleri:
            if not any(m > 0 for _, _, m in kumeler):
                continue
            saf = bootstrap.kume_bootstrap_saf(kumeler, B=B)
            npy = bootstrap.kume_bootstrap_numpy(kumeler, B=B)
            k = karsilastir.Karsilastirici()
            for alan in ("tahmin", "alt", "ust"):
                k.ekle(alan, saf[alan], npy[alan], "bootstrap")
            k.ekle("dagilim_sha256", saf["dagilim_sha256"], npy["dagilim_sha256"], "tam")
            say("kume_bootstrap", k)
        self._bitir("kume_bootstrap")


if __name__ == "__main__":
    unittest.main()
