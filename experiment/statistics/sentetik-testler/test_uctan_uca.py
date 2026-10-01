"""Uçtan uca bilinen-cevap senaryoları (yalnız sentetik veri).

Beklenen değerler, analiz hattından BAĞIMSIZ olarak burada elle kurulan tablolardan
`math.comb`/`fractions` ile hesaplanır.
"""
from __future__ import annotations

import copy
import csv
import json
import math
import os
import tempfile
import unittest
from fractions import Fraction

from _ortak import (analiz, analiz_sozluk, hedef, kesin, n31_hedefleri, sema, veri_seti, y_ata)


def binom_alt(x, n):
    return Fraction(sum(math.comb(n, k) for k in range(x + 1)), 2 ** n)


def binom_ust(x, n):
    return Fraction(sum(math.comb(n, k) for k in range(x, n + 1)), 2 ** n)


def fisher_elle(a, b, c, d):
    r1, r2, c1 = a + b, c + d, a + c
    N = r1 + r2
    lo, hi = max(0, c1 - r2), min(r1, c1)
    P = {k: Fraction(math.comb(r1, k) * math.comb(r2, c1 - k), math.comb(N, c1)) for k in range(lo, hi + 1)}
    return sum(v for v in P.values() if v <= P[a])


class H6Hukmu(unittest.TestCase):
    """ÖK §6.10: destek = birincil VE (i) X ≤ c; yalnız birincil => kırılgan destek."""

    def test_destek(self):
        s = analiz_sozluk(veri_seti(y_ata(n31_hedefleri(), birler=8)))
        self.assertEqual((s["T1"]["n_eff"], s["T1"]["X"], s["T1"]["karar"]), (31, 8, "destek"))
        self.assertEqual(s["T1"]["p_alt"]["kesin"], str(binom_alt(8, 31)))
        self.assertEqual(s["H6_hukmu"]["hukum"], "destek")
        self.assertTrue(s["iki_uygulama"]["gecerli"])

    def test_kirilgan_destek(self):
        s = analiz_sozluk(veri_seti(y_ata(n31_hedefleri(), birler=9, belirsiz=2)))
        self.assertEqual((s["T1"]["n_eff"], s["T1"]["c"], s["T1"]["karar"]), (29, 9, "destek"))
        i = s["T1_duyarlilik"]["i_belirsiz_1"]
        self.assertEqual((i["n_eff"], i["X"], i["c"], i["karar"]), (31, 11, 10, "belirsiz"))
        ii = s["T1_duyarlilik"]["ii_belirsiz_0"]
        self.assertEqual((ii["n_eff"], ii["X"], ii["karar"]), (31, 9, "destek"))
        self.assertEqual(s["H6_hukmu"]["hukum"], "kirilgan_destek")

    def test_destek_belirsizle_saglam(self):
        # 1 belirsiz, X = 9: birincil n=30, c=10 → destek; (i) X=10, n=31, c=10 → destek => destek
        s = analiz_sozluk(veri_seti(y_ata(n31_hedefleri(), birler=9, belirsiz=1)))
        self.assertEqual(s["H6_hukmu"]["hukum"], "destek")

    def test_yanlislama(self):
        s = analiz_sozluk(veri_seti(y_ata(n31_hedefleri(), birler=21)))
        self.assertEqual(s["T1"]["karar"], "yanlislama")
        self.assertEqual(s["T1"]["p_ust"]["kesin"], str(binom_ust(21, 31)))
        self.assertEqual(s["H6_hukmu"]["hukum"], "yanlislama")

    def test_belirsiz(self):
        s = analiz_sozluk(veri_seti(y_ata(n31_hedefleri(), birler=15)))
        self.assertEqual(s["H6_hukmu"]["hukum"], "belirsiz")

    def test_tanimlayici(self):
        s = analiz_sozluk(veri_seti(y_ata(n31_hedefleri(), birler=3, gecersiz=12)))
        self.assertEqual(s["T1"]["n_eff"], 19)
        self.assertEqual(s["H6_hukmu"]["hukum"], "tanimlayici")
        self.assertIsNotNone(s["T1"]["wilson"])  # tanımlayıcı sonuçta Wilson GA verilir (ÖK §6.3)

    def test_etki_buyuklugu_t1(self):
        s = analiz_sozluk(veri_seti(y_ata(n31_hedefleri(), birler=8)))
        alt, ust = kesin.wilson(8, 31)
        self.assertEqual(s["T1"]["oran"], 8 / 31)
        self.assertEqual(s["T1"]["wilson"], [alt, ust])
        self.assertEqual(s["T1"]["fark_0_5"], 8 / 31 - 0.5)
        self.assertEqual(s["T1"]["fark_0_5_ga"], [alt - 0.5, ust - 0.5])


class Duyarliliklar(unittest.TestCase):
    def test_pilot_haric(self):
        h = y_ata(n31_hedefleri(), birler=10)
        h[0]["pilot"] = 1   # Y = 1
        h[20]["pilot"] = 1  # Y = 0
        s = analiz_sozluk(veri_seti(h))
        p = s["T1_duyarlilik"]["pilot_haric"]
        self.assertEqual((p["n_eff"], p["X"], p["c"], p["karar"]), (29, 9, 9, "destek"))
        self.assertEqual(p["dislanan"], sorted([h[0]["hedef_id"], h[20]["hedef_id"]]))

    def test_devralan_haric_t1_t2(self):
        h = y_ata(n31_hedefleri(), birler=10)
        for x in h:
            x["tk_sinifi"] = "TK1"
        # T2 için 6 uyumsuz çift (b): biri devralan
        for i in range(10, 16):
            h[i]["F_T"] = 1
        h[10]["devralan"] = 1
        h[10]["devraldigi_hedef"] = "S-DIS-HEDEF"   # n dışı bir hedefe devir de geçerli
        h[0]["devralan"] = 1
        h[0]["devraldigi_hedef"] = h[1]["hedef_id"]
        s = analiz_sozluk(veri_seti(h))
        d1 = s["T1_duyarlilik"]["devralan_haric"]
        self.assertEqual((d1["n_eff"], d1["X"]), (29, 9))
        self.assertTrue(d1["holm_disi"])
        self.assertEqual((s["T2"]["b"], s["T2"]["c"]), (6, 0))
        d2 = s["T2_devralan_haric"]
        self.assertEqual((d2["b"], d2["c"], d2["n_cift"]), (5, 0, 29))
        self.assertEqual(d2["p"]["kesin"], str(Fraction(2, 2 ** 5)))
        self.assertTrue(d2["holm_disi"])


class T2KapsamVeEtki(unittest.TestCase):
    def test_tk3_disarida(self):
        h = n31_hedefleri()
        for i, x in enumerate(h):
            x["tk_sinifi"] = "TK3" if i >= 20 else ("TK1" if i < 5 else "TK2")
        for i in range(0, 5):      # TK1/TK2: 5 çift F_K=0, F_T=1 (b)
            h[i]["F_T"] = 1
        for i in range(5, 7):      # TK1/TK2: 2 çift F_K=1, F_T=1 (a)
            h[i]["F_K"] = h[i]["F_T"] = 1
        for i in range(20, 31):    # TK3: 11 çift F_K=1, F_T=0 (T2'ye GİRMEMELİ)
            h[i]["F_K"] = 1
        s = analiz_sozluk(veri_seti(h))
        t2 = s["T2"]
        self.assertEqual(t2["n_cift"], 20)
        self.assertEqual(t2["tablo"], {"a": 2, "b": 5, "c": 0, "d": 13})
        self.assertEqual(t2["p"]["kesin"], str(Fraction(1, 16)))   # 2 · 0,5^5
        self.assertAlmostEqual(t2["etki"]["fark"], 5 / 20, delta=1e-15)
        f, alt, ust, phi = kesin.newcombe_eslestirilmis(2, 5, 0, 13)
        self.assertEqual([t2["etki"]["alt"], t2["etki"]["ust"]], [alt, ust])
        tk3 = s["TK3_tanimlayici"]
        self.assertEqual(tk3["n_cift"], 11)
        self.assertEqual(tk3["tablo"], {"a": 0, "b": 0, "c": 11, "d": 0})


class T3T4T5(unittest.TestCase):
    def _veri(self):
        h = n31_hedefleri()  # JOSE 0–17, SDJWT 18–25, COSE 26–30
        # T3: SDJWT'de 4/8 PQ'ya özgü (F_T=1, F_K=0); JOSE'de 1/18; COSE'da 3 (T3'e GİRMEMELİ)
        for i in (18, 19, 20, 21, 0, 26, 27, 28):
            h[i]["F_T"] = 1
        h[1]["F_K"] = h[1]["F_T"] = 1   # JOSE: iki kolda da başarısız => PQ'ya özgü değil
        # T4: 8725bis sonrası sürüm: 10 hedef, bunların 7'sinde L ≥ 3; öncesi 21 hedef, 5'inde L ≥ 3
        for i in range(10):
            h[i]["surum_8725bis_sonrasi"] = 1
            h[i]["L_duzeyi"] = 4 if i < 7 else 1
        for i in range(10, 15):
            h[i]["L_duzeyi"] = 3
        # T5: 25/31 D_soy = 1
        for i in range(25):
            h[i]["D_soy"] = 1
        return h

    def test_t3(self):
        s = analiz_sozluk(veri_seti(self._veri()))
        t3 = s["T3"]
        self.assertEqual(t3["satirlar"], ["SDJWT", "JOSE"])
        self.assertEqual(t3["tablo"], [[4, 4], [1, 17]])
        self.assertEqual(t3["p"]["kesin"], str(fisher_elle(4, 4, 1, 17)))
        self.assertAlmostEqual(t3["fark"]["fark"], 4 / 8 - 1 / 18, delta=1e-15)
        mle, alt, ust = kesin.kosullu_or(4, 4, 1, 17)
        self.assertEqual([t3["or"]["mle"], t3["or"]["alt"], t3["or"]["ust"]], [mle, alt, ust])

    def test_t4(self):
        s = analiz_sozluk(veri_seti(self._veri()))
        t4 = s["T4"]
        self.assertEqual(t4["tablo"], [[7, 3], [5, 16]])
        self.assertEqual(t4["p"]["kesin"], str(fisher_elle(7, 3, 5, 16)))

    def test_t5(self):
        s = analiz_sozluk(veri_seti(self._veri()))
        t5 = s["T5"]
        self.assertEqual((t5["n"], t5["X"]), (31, 25))
        self.assertEqual(t5["p"]["kesin"], str(binom_ust(25, 31)))
        self.assertEqual(t5["wilson"], list(kesin.wilson(25, 31)))

    def test_holm_butunlesik(self):
        s = analiz_sozluk(veri_seti(self._veri()))
        p = {t: Fraction(s[t]["p"]["kesin"]) for t in ("T2", "T3", "T4", "T5")}
        beklenen = kesin.holm(p)
        for t in p:
            self.assertEqual(s["holm"]["sonuclar"][t]["p_duzeltilmis"]["kesin"], str(beklenen[t]["p_duzeltilmis"]))
            self.assertEqual(s["holm"]["sonuclar"][t]["red"], beklenen[t]["red"])
        self.assertEqual(s["holm"]["m"], 4)
        self.assertNotIn("T1", s["holm"]["sonuclar"])   # T1 Holm dışında (ÖK §6.6)


class GenelYapi(unittest.TestCase):
    def test_ref_hedefler_disarida(self):
        h = y_ata(n31_hedefleri(), birler=8)
        s1 = analiz_sozluk(veri_seti(h))
        h2 = h + [hedef("S-REF-01", "REF", Y_L4=1, F_T=1, D_soy=1), hedef("S-REF-02", "REF", Y_L4=1)]
        s2 = analiz_sozluk(veri_seti(h2))
        for t in ("T1", "T2", "T3", "T4", "T5", "holm"):
            self.assertEqual(json.dumps(s1[t], sort_keys=True), json.dumps(s2[t], sort_keys=True))
        self.assertEqual(s2["orneklem"]["ref_hedefler"], ["S-REF-01", "S-REF-02"])

    def test_n_uyarisi(self):
        s = analiz_sozluk(veri_seti(n31_hedefleri()[:30]))
        self.assertEqual(s["orneklem"]["n"], 30)
        self.assertTrue(any("31" in u for u in s["orneklem"]["uyarilar"]))

    def test_wilson_l_duzeyleri(self):
        h = n31_hedefleri()
        dagilim = [0] * 3 + [1] * 4 + [2] * 10 + [3] * 7 + [4] * 5 + [5] * 2
        for x, L in zip(h, dagilim):
            x["L_duzeyi"] = L
        s = analiz_sozluk(veri_seti(h))
        w = s["wilson"]["L_duzeyi"]
        self.assertEqual(w["n"], 31)
        for L, adet in enumerate([3, 4, 10, 7, 5, 2]):
            self.assertEqual(w[f"L{L}"]["x"], adet)
            self.assertEqual(w[f"L{L}"]["ga"], list(kesin.wilson(adet, 31)))
        self.assertEqual(s["wilson"]["L_en_az"]["L3"]["x"], 14)

    def test_bootstrap_hatti(self):
        h = n31_hedefleri()
        vakalar = []
        for x in h:
            for j in range(10):
                vakalar.append({"hedef_id": x["hedef_id"], "vaka_id": f"V{j:02d}", "kol": "K" if j < 5 else "T",
                                "uyum": 0 if j in (0, 5) else 1, "belirsiz_neden": None})
        s = analiz_sozluk(veri_seti(h, vakalar))
        b = s["bootstrap"]
        self.assertEqual((b["tum"]["tahmin"], b["tum"]["alt"], b["tum"]["ust"]), (0.2, 0.2, 0.2))
        self.assertEqual((b["K"]["tahmin"], b["T"]["tahmin"]), (0.2, 0.2))
        self.assertEqual(b["tum"]["k"], 31)
        self.assertEqual(b["tum"]["B"], 10000)

    def test_iki_uygulama_hatti_gecerli(self):
        s = analiz_sozluk(veri_seti(T3T4T5()._veri()))
        self.assertTrue(s["iki_uygulama"]["gecerli"])
        self.assertGreater(s["iki_uygulama"]["karsilastirma"], 40)
        self.assertEqual(s["iki_uygulama"]["uyumlu"] + s["iki_uygulama"]["sinirda"], s["iki_uygulama"]["karsilastirma"])


class CsvJsonEsdegerlik(unittest.TestCase):
    def test_ayni_sonuc(self):
        h = y_ata(n31_hedefleri(), birler=9, belirsiz=2)
        h[3]["B2"] = None
        h[3]["belirsiz_nedenleri"] = dict(h[3]["belirsiz_nedenleri"], B2="uygulanamaz")
        h[4]["B4_ozel_kod"] = 1
        h[4]["B4_satir"] = 20
        h[5]["devralan"] = 1
        h[5]["devraldigi_hedef"] = "S-JOSE-07"
        vakalar = [{"hedef_id": x["hedef_id"], "vaka_id": "V1", "kol": "K", "uyum": 1, "belirsiz_neden": None} for x in h]
        vakalar[0]["uyum"] = None
        vakalar[0]["belirsiz_neden"] = "kararsiz_3_tekrar"
        veri = veri_seti(h, vakalar)
        s_json = analiz_sozluk(veri)
        with tempfile.TemporaryDirectory() as d:
            hy = os.path.join(d, "hedefler.csv")
            vy = os.path.join(d, "vakalar.csv")
            alanlar = list(h[0].keys())
            with open(hy, "w", encoding="utf-8", newline="") as f:
                f.write(f"# sema_surumu={veri['sema_surumu']}; veri_turu=sentetik\n")
                w = csv.DictWriter(f, fieldnames=alanlar)
                w.writeheader()
                for x in h:
                    satir = {}
                    for k in alanlar:
                        v = x[k]
                        if k == "belirsiz_nedenleri":
                            v = ";".join(f"{a}:{b}" for a, b in sorted(v.items()))
                        satir[k] = "" if v is None else v
                    w.writerow(satir)
            with open(vy, "w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(vakalar[0].keys()))
                w.writeheader()
                for v in vakalar:
                    w.writerow({k: ("" if vv is None else vv) for k, vv in v.items()})
            s_csv = analiz.analiz_et(sema.yukle(hy, vakalar_yolu=vy))
        for k in ("T1", "T1_duyarlilik", "H6_hukmu", "T2", "T3", "T4", "T5", "holm", "wilson", "bootstrap", "tanimlayici"):
            self.assertEqual(json.dumps(s_json[k], sort_keys=True), json.dumps(s_csv[k], sort_keys=True), k)


class Belirlenimcilik(unittest.TestCase):
    def test_cikti_dosyalari_bayt_ayni(self):
        veri = veri_seti(T3T4T5()._veri())
        with tempfile.TemporaryDirectory() as d:
            girdi = os.path.join(d, "girdi.json")
            with open(girdi, "w", encoding="utf-8") as f:
                json.dump(veri, f, ensure_ascii=False)
            ozetler = []
            for i in range(2):
                cikti = os.path.join(d, f"c{i}")
                kod = analiz.calistir(girdi, cikti)
                self.assertEqual(kod, 0)
                with open(os.path.join(cikti, "sonuc.json"), "rb") as f:
                    b1 = f.read()
                with open(os.path.join(cikti, "sonuc.md"), "rb") as f:
                    b2 = f.read()
                ozetler.append((b1, b2))
            self.assertEqual(ozetler[0], ozetler[1])


if __name__ == "__main__":
    unittest.main()
