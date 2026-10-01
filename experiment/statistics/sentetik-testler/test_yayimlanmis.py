"""Yayımlanmış örnek değerler (Wilson; Newcombe yöntem 10 bağımsız ve eşleştirilmiş).

Kaynak: data/yayimlanmis_ornekler.json ve kaynak/NEWCOMBE-KAYNAK.md. Birincil metin erişilemedi;
değerler açık erişimli ikincil kaynaktan (ratesci test3.R) BİREBİR aktarıldı.

Her örnek iki uygulamayla ayrı ayrı yeniden üretilir: kendi kesin uygulama (Decimal) ve
kütüphane (statsmodels; eşleştirilmişte numpy + statsmodels Wilson).
"""
from __future__ import annotations

import json
import os
import unittest
from decimal import ROUND_HALF_EVEN, Decimal

from _ortak import VERI_DIZINI, kesin, referans


def yuvarla(x: float, basamak: int) -> Decimal:
    # Yayımlanmış değerler R'nin round() çıktısıdır (IEC 60559, yarıda çifte). Sınırda olmayan değerlerde
    # yuvarlama kuralı sonucu değiştirmez; aşağıdaki test ayrıca sınıra uzaklığı denetler.
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
        # Hesaplanan değer, yuvarlama sınırına (…5) 1e-9'dan yakın olmamalı; aksi hâlde karşılaştırma kırılgandır.
        for o in ornekler():
            for deger in hesapla(o, kesin):
                with self.subTest(kod=o["kod"], deger=deger):
                    olcek = Decimal(10) ** o["ondalik"]
                    kesir = (Decimal(repr(deger)) * olcek) % 1
                    self.assertGreater(abs(abs(kesir) - Decimal("0.5")), Decimal("1e-9") * olcek)


class NewcombeTanimi(unittest.TestCase):
    """Yöntem 10'un tanımından elle doğrulanabilir özellikler (kaynak/NEWCOMBE-KAYNAK.md §3)."""

    def test_phi_duzeltmesi_y5(self):
        # (20, 12, 2, 16): ad − bc = 320 − 24 = 296 > 0; N = 50; φ* = (296 − 25)/√(32·18·22·28)
        from math import sqrt
        _, _, _, phi = kesin.newcombe_eslestirilmis(20, 12, 2, 16, phi_turu="newcombe_duzeltmeli")
        self.assertAlmostEqual(phi, (296 - 25) / sqrt(32 * 18 * 22 * 28), delta=1e-15)
        _, _, _, phi_duz = kesin.newcombe_eslestirilmis(20, 12, 2, 16, phi_turu="duz")
        self.assertAlmostEqual(phi_duz, 296 / sqrt(32 * 18 * 22 * 28), delta=1e-15)

    def test_phi_negatifte_duzeltme_yok(self):
        # ad − bc ≤ 0 ise φ* = φ̂ (düzeltme yalnız pozitif korelasyonda)
        for tablo in [(1, 7, 7, 1), (0, 5, 3, 2), (2, 6, 6, 2)]:
            with self.subTest(tablo=tablo):
                a, b, c, d = tablo
                self.assertLessEqual(a * d - b * c, 0)
                phi1 = kesin.newcombe_eslestirilmis(*tablo, phi_turu="newcombe_duzeltmeli")[3]
                phi2 = kesin.newcombe_eslestirilmis(*tablo, phi_turu="duz")[3]
                self.assertEqual(phi1, phi2)

    def test_phi_alt_sinir_sifir(self):
        # 0 < ad − bc ≤ N/2 => φ* = 0 (max(·, 0))
        a, b, c, d = 1, 1, 1, 2  # ad − bc = 1; N/2 = 2,5
        self.assertEqual(kesin.newcombe_eslestirilmis(a, b, c, d, phi_turu="newcombe_duzeltmeli")[3], 0.0)
        # Y7 (Fagerland örneği, 1, 1, 7, 12): ad − bc = 5 ≤ N/2 = 10,5 => φ* = 0, oysa φ̂ > 0.
        # Yayımlanmış değer (−0,507; −0,026) φ* ile üretiliyor (test_kendi_uygulama): düzeltme ayırt edici.
        self.assertEqual(kesin.newcombe_eslestirilmis(1, 1, 7, 12)[3], 0.0)
        self.assertGreater(kesin.newcombe_eslestirilmis(1, 1, 7, 12, phi_turu="duz")[3], 0.0)
        _, alt_duz, ust_duz, _ = kesin.newcombe_eslestirilmis(1, 1, 7, 12, phi_turu="duz")
        self.assertNotEqual((round(alt_duz, 3), round(ust_duz, 3)), (-0.507, -0.026))

    def test_phi_payda_sifir(self):
        # Bir marjinal toplam 0 ise φ = 0 (ör. hiç olay yok)
        self.assertEqual(kesin.newcombe_eslestirilmis(0, 0, 0, 9)[3], 0.0)
        self.assertEqual(kesin.newcombe_eslestirilmis(5, 0, 0, 0)[3], 0.0)


if __name__ == "__main__":
    unittest.main()
