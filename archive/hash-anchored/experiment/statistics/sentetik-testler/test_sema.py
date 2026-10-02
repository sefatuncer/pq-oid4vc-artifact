"""Girdi şeması doğrulayıcısı (SEMA.md §6): hatalı girdi analize ULAŞMAMALI."""
from __future__ import annotations

import copy
import unittest

from _ortak import hedef, n31_hedefleri, sema, veri_seti, y_ata


class GecerliGirdi(unittest.TestCase):
    def test_temiz_veri_gecer(self):
        g = sema.sozlukten(veri_seti(n31_hedefleri()))
        self.assertEqual(len(g.hedefler), 31)
        self.assertEqual(g.veri_turu, "sentetik")

    def test_bool_ve_int_esdeger(self):
        h = n31_hedefleri()
        h[0]["pilot"] = True
        h[1]["Y_L4"] = False
        g = sema.sozlukten(veri_seti(h))
        self.assertEqual(g.hedefler[0]["pilot"], 1)
        self.assertEqual(g.hedefler[1]["Y_L4"], 0)


class HataliGirdi(unittest.TestCase):
    def _hata(self, veri, parca: str):
        with self.assertRaises(sema.GirdiHatasi) as cm:
            sema.sozlukten(veri)
        self.assertTrue(any(parca in m for m in cm.exception.mesajlar), cm.exception.mesajlar)

    def test_sema_surumu(self):
        v = veri_seti(n31_hedefleri())
        v["sema_surumu"] = "c3-istat-girdi/0.9"
        self._hata(v, "sema_surumu")

    def test_bilinmeyen_ust_alan(self):
        v = veri_seti(n31_hedefleri())
        v["ekstra"] = 1
        self._hata(v, "ekstra")

    def test_bilinmeyen_hedef_alani(self):
        h = n31_hedefleri()
        h[0]["Y_L5"] = 1
        self._hata(veri_seti(h), "Y_L5")

    def test_eksik_zorunlu_alan(self):
        h = n31_hedefleri()
        del h[0]["F_T"]
        self._hata(veri_seti(h), "F_T")

    def test_yinelenen_kimlik(self):
        h = n31_hedefleri()
        h[1]["hedef_id"] = h[0]["hedef_id"]
        self._hata(veri_seti(h), "yinelenen")

    def test_gecersiz_enum(self):
        for alan, deger in [("tabaka", "JWT"), ("tk_sinifi", "TK4"), ("l4_bicimi", "L4x"), ("B1", "belki"),
                            ("B5", "hepsi"), ("kontrol_etiketi", "ES256")]:
            with self.subTest(alan=alan):
                h = n31_hedefleri()
                h[0][alan] = deger
                self._hata(veri_seti(h), alan)

    def test_gecersiz_ikili_ve_duzey(self):
        for alan, deger in [("Y_L4", 2), ("F_K", -1), ("L_duzeyi", 6), ("L_duzeyi", "3"), ("pilot", None)]:
            with self.subTest(alan=alan, deger=deger):
                h = n31_hedefleri()
                h[0][alan] = deger
                self._hata(veri_seti(h), alan)

    def test_nedensiz_null(self):
        h = n31_hedefleri()
        h[0]["D_soy"] = None
        self._hata(veri_seti(h), "D_soy")

    def test_y_l4_uygulanamaz_olamaz(self):
        h = n31_hedefleri()
        h[0]["Y_L4"] = None
        h[0]["belirsiz_nedenleri"] = {"Y_L4": "uygulanamaz"}
        self._hata(veri_seti(h), "Y_L4")

    def test_gereksiz_neden(self):
        h = n31_hedefleri()
        h[0]["belirsiz_nedenleri"] = {"F_K": "kanit_kurali"}   # F_K null değil
        self._hata(veri_seti(h), "F_K")

    def test_devralan_hedefsiz(self):
        h = n31_hedefleri()
        h[0]["devralan"] = 1
        self._hata(veri_seti(h), "devraldigi_hedef")

    def test_tarih_bayrak_celiskisi(self):
        h = n31_hedefleri()
        h[0]["son_surum_tarihi"] = "2026-08-21"      # "sonra" DEĞİL (kesin büyük)
        h[0]["surum_8725bis_sonrasi"] = 1
        self._hata(veri_seti(h), "son_surum_tarihi")
        h2 = n31_hedefleri()
        h2[0]["son_surum_tarihi"] = "2026-08-22"
        h2[0]["surum_8725bis_sonrasi"] = 1
        sema.sozlukten(veri_seti(h2))   # tutarlı: geçer

    def test_b4_tutarsizligi(self):
        h = n31_hedefleri()
        h[0]["B4_ozel_kod"] = 1
        self._hata(veri_seti(h), "B4_satir")
        h2 = n31_hedefleri()
        h2[0]["B4_satir"] = 12
        self._hata(veri_seti(h2), "B4_satir")

    def test_adaptor_gecersiz_gerekcesiz(self):
        h = n31_hedefleri()
        h[0]["adaptor_gecersiz"] = 1
        self._hata(veri_seti(h), "adaptor_gecersiz_gerekce")

    def test_olculmedi_yalniz_gecersizde(self):
        h = n31_hedefleri()
        h[0]["F_K"] = None
        h[0]["belirsiz_nedenleri"] = {"F_K": "olculmedi"}
        self._hata(veri_seti(h), "olculmedi")
        h2 = y_ata(n31_hedefleri(), birler=0, gecersiz=1)
        h2[0]["F_K"] = None
        h2[0]["belirsiz_nedenleri"] = {"F_K": "olculmedi"}
        sema.sozlukten(veri_seti(h2))   # adaptör geçersizde geçer

    def test_vaka_hatalari(self):
        h = n31_hedefleri()
        iyi = {"hedef_id": h[0]["hedef_id"], "vaka_id": "V1", "kol": "K", "uyum": 1, "belirsiz_neden": None}
        for bozuk, parca in [
            (dict(iyi, hedef_id="S-YOK"), "hedef_id"),
            (dict(iyi, kol="X"), "kol"),
            (dict(iyi, uyum=None), "belirsiz_neden"),
            (dict(iyi, uyum=2), "uyum"),
        ]:
            with self.subTest(parca=parca):
                self._hata(veri_seti(h, [bozuk]), parca)
        self._hata(veri_seti(h, [iyi, copy.deepcopy(iyi)]), "yinelenen")

    def test_kontrol_etiketi_zorunlu(self):
        # ÖK §2D-A.2 ve §2E.3: kullanılan kontrol etiketi (EdDSA/Ed25519) hedef başına kaydedilir
        h = n31_hedefleri()
        h[0]["kontrol_etiketi"] = None
        self._hata(veri_seti(h), "kontrol_etiketi")
        h2 = y_ata(n31_hedefleri(), birler=0, gecersiz=1)
        h2[0]["kontrol_etiketi"] = None
        sema.sozlukten(veri_seti(h2))   # adaptör geçersiz hedefte zorunlu değil

    def test_veri_turu(self):
        v = veri_seti(n31_hedefleri())
        v["veri_turu"] = "gercek"
        self._hata(v, "veri_turu")


if __name__ == "__main__":
    unittest.main()
