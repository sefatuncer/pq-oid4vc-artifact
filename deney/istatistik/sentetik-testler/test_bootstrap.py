"""Küme bootstrap (ÖK §6.9: birim kütüphane, B = 10.000, yüzdelik GA, tohum 20260927).

- Aynı tohum => bit düzeyinde aynı sonuç (aynı süreçte ve iki ayrı Python sürecinde).
- Saf Python ve numpy uygulamaları aynı dağılımı üretir (dağılımın SHA-256'sı eşit).
- Bilinen cevaplı vakalar: tek küme; bütün kümelerin oranı eşit; iki kümede kesin dağılım;
  m = 0 kümelerin dışlanması; yüzdelik tanımı (tip 7).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from fractions import Fraction

from _ortak import bootstrap, kesin, yapilandirma

ORNEK = [(f"S-{j:02d}", (3 * j) % 7, 8 + j % 5) for j in range(31)]


class Tekrarlanabilirlik(unittest.TestCase):
    def test_ayni_tohum_ayni_bitler(self):
        s1 = bootstrap.kume_bootstrap_saf(ORNEK)
        s2 = bootstrap.kume_bootstrap_saf(ORNEK)
        self.assertEqual(json.dumps(s1, sort_keys=True), json.dumps(s2, sort_keys=True))
        self.assertEqual(s1["dagilim_sha256"], s2["dagilim_sha256"])
        self.assertEqual(s1["B"], 10000)
        self.assertEqual(s1["tohum"], 20260927)

    def test_ayri_surecte_ayni_bitler(self):
        betik = (
            "import json,sys; sys.path.insert(0, sys.argv[1]);"
            "from _ortak import bootstrap;"
            "ORNEK=[(f'S-{j:02d}', (3*j)%7, 8+j%5) for j in range(31)];"
            "print(json.dumps(bootstrap.kume_bootstrap_saf(ORNEK), sort_keys=True))"
        )
        burasi = os.path.dirname(os.path.abspath(__file__))
        ciktilar = []
        for _ in range(2):
            r = subprocess.run([sys.executable, "-c", betik, burasi], capture_output=True, text=True, check=True,
                               env=dict(os.environ, PYTHONHASHSEED="0"))
            ciktilar.append(r.stdout.strip())
        self.assertEqual(ciktilar[0], ciktilar[1])
        self.assertEqual(json.loads(ciktilar[0]), json.loads(json.dumps(bootstrap.kume_bootstrap_saf(ORNEK), sort_keys=True)))

    def test_farkli_tohum_farkli_dagilim(self):
        s1 = bootstrap.kume_bootstrap_saf(ORNEK)
        s2 = bootstrap.kume_bootstrap_saf(ORNEK, tohum=20260928)
        self.assertNotEqual(s1["dagilim_sha256"], s2["dagilim_sha256"])

    def test_kume_sirasi_hedef_kimligine_gore(self):
        # Girdi sırası sonucu değiştirmez: kümeler hedef_id'ye göre sıralanır.
        ters = list(reversed(ORNEK))
        self.assertEqual(bootstrap.kume_bootstrap_saf(ORNEK)["dagilim_sha256"],
                         bootstrap.kume_bootstrap_saf(ters)["dagilim_sha256"])

    def test_rastgele_akis_tanimi(self):
        # İndeks = floor(U·k), U = random.Random(tohum).random() (Python'un kararlılık güvencesi random() için)
        import random
        rng = random.Random(20260927)
        beklenen = [int(rng.random() * 31) for _ in range(50)]
        self.assertEqual(bootstrap.indeks_akisi(31, 50, tohum=20260927), beklenen)
        self.assertTrue(all(0 <= i < 31 for i in bootstrap.indeks_akisi(31, 10000)))


class BilinenCevap(unittest.TestCase):
    def test_tek_kume(self):
        s = bootstrap.kume_bootstrap_saf([("S-01", 3, 12)])
        self.assertEqual((s["tahmin"], s["alt"], s["ust"]), (0.25, 0.25, 0.25))

    def test_esit_oranlar(self):
        s = bootstrap.kume_bootstrap_saf([(f"S-{i}", i, 4 * i) for i in range(1, 11)])
        self.assertEqual((s["tahmin"], s["alt"], s["ust"]), (0.25, 0.25, 0.25))

    def test_iki_kume_kesin_dagilim(self):
        # k = 2: yeniden örneklem 4 eşit olasılıklı sonuç; istatistik r1 (1/4), havuz (1/2), r2 (1/4).
        # %2,5 ve %97,5 yüzdelikleri (tip 7) min ve max oranlara düşer (olasılık ≈ 1; tohum sabit).
        s = bootstrap.kume_bootstrap_saf([("S-A", 1, 10), ("S-B", 6, 10)])
        self.assertEqual(s["alt"], 0.1)
        self.assertEqual(s["ust"], 0.6)
        self.assertEqual(s["tahmin"], 7 / 20)
        pay = s["dagilim_ozeti"]
        self.assertEqual(set(pay["farkli_degerler"]), {0.1, 0.35, 0.6})
        # Göreli sıklıklar beklenen 1/4, 1/2, 1/4'e yakın (B = 10.000; 5 standart hata içinde)
        self.assertLess(abs(pay["sikliklar"]["0.1"] / 10000 - 0.25), 5 * (0.25 * 0.75 / 10000) ** 0.5)
        self.assertLess(abs(pay["sikliklar"]["0.35"] / 10000 - 0.5), 5 * (0.25 / 10000) ** 0.5)

    def test_bos_kumeler_dislanir(self):
        s1 = bootstrap.kume_bootstrap_saf([("S-A", 1, 10), ("S-B", 6, 10)])
        s2 = bootstrap.kume_bootstrap_saf([("S-A", 1, 10), ("S-B", 6, 10), ("S-C", 0, 0)])
        self.assertEqual(s1["dagilim_sha256"], s2["dagilim_sha256"])
        self.assertEqual(s2["k"], 2)
        self.assertEqual(s2["dislanan_bos_kume"], ["S-C"])

    def test_hic_veri_yok(self):
        s = bootstrap.kume_bootstrap_saf([("S-C", 0, 0)])
        self.assertIsNone(s["tahmin"])
        self.assertIsNone(s["alt"])
        self.assertEqual(s["durum"], "veri_yok")

    def test_yuzdelik_tip7(self):
        # Hyndman–Fan tip 7: h = (B−1)q; Q = x[⌊h⌋] + (h − ⌊h⌋)(x[⌊h⌋+1] − x[⌊h⌋]) (0 tabanlı)
        x = [float(i) for i in range(10000)]
        self.assertAlmostEqual(kesin.yuzdelik_tip7(x, Fraction(1, 40)), 249.975, delta=1e-9)
        self.assertAlmostEqual(kesin.yuzdelik_tip7(x, Fraction(39, 40)), 9749.025, delta=1e-9)
        self.assertEqual(kesin.yuzdelik_tip7([2.0, 4.0], Fraction(1, 2)), 3.0)
        self.assertEqual(kesin.yuzdelik_tip7([5.0], Fraction(1, 40)), 5.0)

    def test_yapilandirma_ok_ile_ayni(self):
        self.assertEqual(yapilandirma.BOOTSTRAP_B, 10000)
        self.assertEqual(yapilandirma.BOOTSTRAP_TOHUM, 20260927)
        self.assertEqual((yapilandirma.BOOTSTRAP_ALT, yapilandirma.BOOTSTRAP_UST), (Fraction(1, 40), Fraction(39, 40)))


if __name__ == "__main__":
    unittest.main()
