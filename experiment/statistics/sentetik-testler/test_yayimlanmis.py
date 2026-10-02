"""Published example values (Wilson; Newcombe method 10, independent and paired).

Source: veri/yayimlanmis_ornekler.json and kaynak/NEWCOMBE-SOURCE.md. The primary text could not be accessed;
the values were copied VERBATIM from an open-access secondary source (ratesci test3.R).

Every example is reproduced separately with the two implementations: own exact implementation (Decimal) and
library (statsmodels; for the paired case numpy + statsmodels Wilson).
"""
from __future__ import annotations

import json
import os
import unittest
from decimal import ROUND_HALF_EVEN, Decimal

from _ortak import VERI_DIZINI, kesin, referans


def yuvarla(x: float, basamak: int) -> Decimal:
    # The published values are the output of R's round() (IEC 60559, round half to even). For values that are not
    # at a rounding boundary the rounding rule does not change the result; the test below also checks the distance to the boundary.
    return Decimal(repr(x)).quantize(Decimal(1).scaleb(-basamak), rounding=ROUND_HALF_EVEN)


def ornekler():
    with open(os.path.join(VERI_DIZINI, "yayimlanmis_ornekler.json"), encoding="utf-8") as f:
        return json.load(f)["ornekler"]


def hesapla(o: dict, uygulama) -> tuple[float, float]:
    if o["tur"] == "wilson":
        return uygulama.wilson(o["x"], o["n"])
    if o["tur"] == "newcombe_bagimsiz":
        _, alt, ust = uygulama.newcombe_bagimsiz(o["x1"], o["n1"], o["x2"], o["n2"])
        return alt, ust
    if o["tur"] == "newcombe_eslestirilmis":
        _, alt, ust, _ = uygulama.newcombe_eslestirilmis(o["a"], o["b"], o["c"], o["d"], phi_turu=o["phi_turu"])
        return alt, ust
    raise ValueError(o["tur"])


class YayimlanmisOrnekler(unittest.TestCase):
    def test_kendi_uygulama(self):
        for o in ornekler():
            with self.subTest(kod=o["kod"]):
                alt, ust = hesapla(o, kesin)
                self.assertEqual(yuvarla(alt, o["ondalik"]), Decimal(o["alt"]).quantize(Decimal(1).scaleb(-o["ondalik"])))
                self.assertEqual(yuvarla(ust, o["ondalik"]), Decimal(o["ust"]).quantize(Decimal(1).scaleb(-o["ondalik"])))

    def test_kutuphane_uygulamasi(self):
        for o in ornekler():
            with self.subTest(kod=o["kod"]):
                alt, ust = hesapla(o, referans)
                self.assertEqual(yuvarla(alt, o["ondalik"]), Decimal(o["alt"]).quantize(Decimal(1).scaleb(-o["ondalik"])))
                self.assertEqual(yuvarla(ust, o["ondalik"]), Decimal(o["ust"]).quantize(Decimal(1).scaleb(-o["ondalik"])))

    def test_yuvarlama_siniri_degil(self):
        # The computed value must not be closer than 1e-9 to a rounding boundary (…5); otherwise the comparison is fragile.
        for o in ornekler():
            for deger in hesapla(o, kesin):
                with self.subTest(kod=o["kod"], deger=deger):
                    olcek = Decimal(10) ** o["ondalik"]
                    kesir = (Decimal(repr(deger)) * olcek) % 1
                    self.assertGreater(abs(abs(kesir) - Decimal("0.5")), Decimal("1e-9") * olcek)


class NewcombeTanimi(unittest.TestCase):
    """Properties that can be checked by hand from the definition of method 10 (kaynak/NEWCOMBE-SOURCE.md §3)."""

    def test_phi_duzeltmesi_y5(self):
        # (20, 12, 2, 16): ad − bc = 320 − 24 = 296 > 0; N = 50; φ* = (296 − 25)/√(32·18·22·28)
        from math import sqrt
        _, _, _, phi = kesin.newcombe_eslestirilmis(20, 12, 2, 16, phi_turu="newcombe_duzeltmeli")
        self.assertAlmostEqual(phi, (296 - 25) / sqrt(32 * 18 * 22 * 28), delta=1e-15)
        _, _, _, phi_duz = kesin.newcombe_eslestirilmis(20, 12, 2, 16, phi_turu="duz")
        self.assertAlmostEqual(phi_duz, 296 / sqrt(32 * 18 * 22 * 28), delta=1e-15)

    def test_phi_negatifte_duzeltme_yok(self):
        # if ad − bc ≤ 0 then φ* = φ̂ (the correction applies only to a positive correlation)
        for tablo in [(1, 7, 7, 1), (0, 5, 3, 2), (2, 6, 6, 2)]:
            with self.subTest(tablo=tablo):
                a, b, c, d = tablo
                self.assertLessEqual(a * d - b * c, 0)
                phi1 = kesin.newcombe_eslestirilmis(*tablo, phi_turu="newcombe_duzeltmeli")[3]
                phi2 = kesin.newcombe_eslestirilmis(*tablo, phi_turu="duz")[3]
                self.assertEqual(phi1, phi2)

    def test_phi_alt_sinir_sifir(self):
        # 0 < ad − bc ≤ N/2 => φ* = 0 (max(·, 0))
        a, b, c, d = 1, 1, 1, 2  # ad − bc = 1; N/2 = 2.5
        self.assertEqual(kesin.newcombe_eslestirilmis(a, b, c, d, phi_turu="newcombe_duzeltmeli")[3], 0.0)
        # Y7 (Fagerland example, 1, 1, 7, 12): ad − bc = 5 ≤ N/2 = 10.5 => φ* = 0, whereas φ̂ > 0.
        # The published value (−0.507; −0.026) is reproduced with φ* (test_kendi_uygulama): the correction is decisive.
        self.assertEqual(kesin.newcombe_eslestirilmis(1, 1, 7, 12)[3], 0.0)
        self.assertGreater(kesin.newcombe_eslestirilmis(1, 1, 7, 12, phi_turu="duz")[3], 0.0)
        _, alt_duz, ust_duz, _ = kesin.newcombe_eslestirilmis(1, 1, 7, 12, phi_turu="duz")
        self.assertNotEqual((round(alt_duz, 3), round(ust_duz, 3)), (-0.507, -0.026))

    def test_phi_payda_sifir(self):
        # If a marginal total is 0, φ = 0 (e.g. no event at all)
        self.assertEqual(kesin.newcombe_eslestirilmis(0, 0, 0, 9)[3], 0.0)
        self.assertEqual(kesin.newcombe_eslestirilmis(5, 0, 0, 0)[3], 0.0)


if __name__ == "__main__":
    unittest.main()
