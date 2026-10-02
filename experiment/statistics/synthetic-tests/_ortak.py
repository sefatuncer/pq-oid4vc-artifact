"""Shared helpers of the synthetic tests.

- Sets the import path of the `c3istat` package (repository layout or image layout).
- Builders of synthetic data sets.
- Counters of the comparisons of the two implementations (`SAYAC`). `run_tests.py` writes these counters to the summary.

THIS FILE CONTAINS NO REAL MEASUREMENT DATA. All targets are synthetic (identifiers `S-...`).
"""
from __future__ import annotations

import copy
import os
import sys
from collections import defaultdict

_BURASI = os.path.dirname(os.path.abspath(__file__))
for _aday in (os.path.join(_BURASI, "..", "scripts"), os.path.join(_BURASI, "..")):
    if os.path.isdir(os.path.join(_aday, "c3istat")):
        sys.path.insert(0, os.path.abspath(_aday))
        break

from c3istat import analiz, bootstrap, kesin, karsilastir, referans, sema, yapilandirma  # noqa: E402,F401

VERI_DIZINI = os.path.join(_BURASI, "data")

# ---------------------------------------------------------------------------
# Counters of the comparisons of the two implementations (filled by the sweep tests)
#   SAYAC[aile] = {"vaka": int, "uyumlu_vaka": int, "nicelik": int, "uyumlu_nicelik": int, "en_buyuk_sapma": float}
# ---------------------------------------------------------------------------
SAYAC: dict[str, dict] = defaultdict(lambda: {"vaka": 0, "uyumlu_vaka": 0, "nicelik": 0,
                                              "uyumlu_nicelik": 0, "en_buyuk_sapma": 0.0,
                                              "ilk_uyusmazliklar": []})


def say(aile: str, k: "karsilastir.Karsilastirici") -> bool:
    """Records the comparator of a case in the family counter; returns True if the case agrees."""
    oz = k.ozet()
    s = SAYAC[aile]
    s["vaka"] += 1
    s["nicelik"] += oz["toplam"]
    # "sinirda" = floating-point value within TOLERANSLAR["sinir"] of a decision threshold; the exact arithmetic is authoritative (not counted as an error)
    s["uyumlu_nicelik"] += oz["uyumlu"] + oz["sinirda"]
    s.setdefault("sinirda", 0)
    s["sinirda"] += oz["sinirda"]
    s["en_buyuk_sapma"] = max(s["en_buyuk_sapma"], oz["en_buyuk_sapma"])
    tamam = oz["hata"] == 0
    if tamam:
        s["uyumlu_vaka"] += 1
    elif len(s["ilk_uyusmazliklar"]) < 5:
        s["ilk_uyusmazliklar"].append(oz["uyusmazliklar"][:3])
    return tamam


# ---------------------------------------------------------------------------
# Synthetic data builders
# ---------------------------------------------------------------------------
TABAKA_KOTASI = (("JOSE", 18), ("SDJWT", 8), ("COSE", 5))  # layout of PR §2B.3 (structure only; values are synthetic)


def hedef(hid: str, tabaka: str = "JOSE", **alanlar) -> dict:
    """A synthetic target record whose defaults are 'clean' (no null at all)."""
    kayit = {
        "hedef_id": hid,
        "tabaka": tabaka,
        "adaptor_gecersiz": 0,
        "adaptor_gecersiz_gerekce": None,
        "tk_sinifi": "TK2",
        "l4_bicimi": "L4c",
        "kontrol_etiketi": "EdDSA",
        "Y_L4": 0,
        "L_duzeyi": 2,
        "F_K": 0,
        "F_T": 0,
        "D_soy": 0,
        "B1": "red",
        "B2": 0,
        "B3": 0,
        "B4_ozel_kod": 0,
        "B4_satir": None,
        "B5": "diger",
        "B6": 0,
        "surum_8725bis_sonrasi": 0,
        "son_surum_tarihi": None,
        "pilot": 0,
        "devralan": 0,
        "devraldigi_hedef": None,
        "belirsiz_nedenleri": {},
    }
    for k, v in alanlar.items():
        if k not in kayit:
            raise KeyError(f"bilinmeyen alan: {k}")
        kayit[k] = v
    return kayit


def veri_seti(hedefler: list[dict], vakalar: list[dict] | None = None, aciklama: str = "") -> dict:
    return {
        "sema_surumu": yapilandirma.SEMA_SURUMU,
        "veri_turu": "sentetik",
        "aciklama": aciklama or "sentetik test verisi",
        "hedefler": copy.deepcopy(hedefler),
        "vakalar": copy.deepcopy(vakalar or []),
    }


def n31_hedefleri() -> list[dict]:
    """31 synthetic targets: JOSE 18, SDJWT 8, COSE 5 (layout of the PR §2B quota)."""
    liste = []
    for tabaka, kota in TABAKA_KOTASI:
        for i in range(1, kota + 1):
            liste.append(hedef(f"S-{tabaka}-{i:02d}", tabaka))
    return liste


def y_ata(hedefler: list[dict], birler: int, belirsiz: int = 0, gecersiz: int = 0,
          neden: str = "kanit_kurali") -> list[dict]:
    """In order: the first `gecersiz` targets have an invalid adapter; in the next `belirsiz` targets Y_L4 = null;
    in the next `birler` targets Y_L4 = 1; the rest 0."""
    h = copy.deepcopy(hedefler)
    i = 0
    for _ in range(gecersiz):
        h[i]["adaptor_gecersiz"] = 1
        h[i]["adaptor_gecersiz_gerekce"] = "sentetik: V+/V- iki düzeltmeden sonra geçmedi"
        i += 1
    for _ in range(belirsiz):
        h[i]["Y_L4"] = None
        h[i]["belirsiz_nedenleri"] = dict(h[i]["belirsiz_nedenleri"], Y_L4=neden)
        i += 1
    for _ in range(birler):
        h[i]["Y_L4"] = 1
        i += 1
    if i > len(h):
        raise ValueError("yeterli hedef yok")
    return h


def analiz_sozluk(veri: dict) -> dict:
    """Validates and analyses synthetic data given as a dictionary (without writing files)."""
    return analiz.analiz_et(sema.sozlukten(veri))
