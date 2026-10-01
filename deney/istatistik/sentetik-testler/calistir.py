"""Sentetik test takımını koşar; özeti JSON ve metin olarak yazar.

Kullanım:  python calistir.py [--cikti DIZIN]
Çıkış kodu: 0 = hepsi geçti; 1 = en az bir başarısızlık/hata.

Sayım:
- "test yöntemi": unittest test yöntemleri.
- "alt test": subTest blokları (her biri ayrıca sayılır).
- "iki uygulama": süpürme ailelerindeki vaka ve nicelik karşılaştırmaları (_ortak.SAYAC).
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
import unittest

BURASI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURASI)

import _ortak  # noqa: E402  (c3istat yolunu da kurar)


class SayanSonuc(unittest.TextTestResult):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.basarili_yontemler = []
        self.alt_test_basarili = 0
        self.alt_test_basarisiz = 0

    def addSuccess(self, test):
        super().addSuccess(test)
        self.basarili_yontemler.append(test.id())

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is None:
            self.alt_test_basarili += 1
        else:
            self.alt_test_basarisiz += 1


def surumler() -> dict:
    s = {"python": platform.python_version()}
    for paket in ("numpy", "scipy", "statsmodels", "pandas"):
        try:
            s[paket] = __import__(paket).__version__
        except Exception as e:  # pragma: no cover
            s[paket] = f"yok ({e})"
    from c3istat import __version__
    s["c3istat"] = __version__
    return s


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cikti", default=os.path.join(BURASI, "..", "sonuclar", "test"))
    ap.add_argument("--desen", default="test_*.py")
    arg = ap.parse_args()
    os.makedirs(arg.cikti, exist_ok=True)

    yukleyici = unittest.TestLoader()
    takim = yukleyici.discover(BURASI, pattern=arg.desen, top_level_dir=BURASI)
    t0 = time.time()
    kosucu = unittest.TextTestRunner(verbosity=1, resultclass=SayanSonuc, stream=sys.stdout)
    sonuc = kosucu.run(takim)
    sure = time.time() - t0

    basarisiz = [{"test": t.id(), "iz": iz[-2000:]} for t, iz in sonuc.failures]
    hatalar = [{"test": t.id(), "iz": iz[-2000:]} for t, iz in sonuc.errors]
    yontem_toplam = sonuc.testsRun
    yontem_basarili = len(sonuc.basarili_yontemler)

    iki = {}
    vaka_top = vaka_uyum = nic_top = nic_uyum = 0
    for aile, s in sorted(_ortak.SAYAC.items()):
        iki[aile] = dict(s)
        vaka_top += s["vaka"]
        vaka_uyum += s["uyumlu_vaka"]
        nic_top += s["nicelik"]
        nic_uyum += s["uyumlu_nicelik"]

    ozet = {
        "surumler": surumler(),
        "test_yontemi": {"toplam": yontem_toplam, "basarili": yontem_basarili},
        "alt_test": {"basarili": sonuc.alt_test_basarili, "basarisiz": sonuc.alt_test_basarisiz},
        "basarisizliklar": basarisiz,
        "hatalar": hatalar,
        "atlanan": [{"test": t.id(), "neden": n} for t, n in sonuc.skipped],
        "iki_uygulama": {
            "vaka": {"toplam": vaka_top, "uyumlu": vaka_uyum},
            "nicelik": {"toplam": nic_top, "uyumlu": nic_uyum},
            "aileler": iki,
        },
        "hepsi_gecti": sonuc.wasSuccessful() and yontem_basarili == yontem_toplam,
    }
    with open(os.path.join(arg.cikti, "test_ozeti.json"), "w", encoding="utf-8") as f:
        json.dump(ozet, f, ensure_ascii=False, indent=2, sort_keys=True)
    with open(os.path.join(arg.cikti, "calistirma_kaydi.json"), "w", encoding="utf-8") as f:
        json.dump({"sure_sn": round(sure, 2), "baslangic_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t0)),
                   "platform": platform.platform()}, f, ensure_ascii=False, indent=2)

    print()
    print(f"TEST YONTEMI: {yontem_basarili}/{yontem_toplam} gecti; alt test: {sonuc.alt_test_basarili} gecti, "
          f"{sonuc.alt_test_basarisiz} kaldi")
    print(f"IKI UYGULAMA: vaka {vaka_uyum}/{vaka_top}; nicelik {nic_uyum}/{nic_top}")
    for aile, s in sorted(_ortak.SAYAC.items()):
        print(f"  {aile:34s} vaka {s['uyumlu_vaka']:>6}/{s['vaka']:<6} en buyuk sapma {s['en_buyuk_sapma']:.3e}")
    print(f"SURE: {sure:.1f} s")
    return 0 if ozet["hepsi_gecti"] else 1


if __name__ == "__main__":
    sys.exit(main())
