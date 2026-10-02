"""Comparison of the two implementations (A = exact, B = library).

Kinds and tolerances (`yapilandirma.TOLERANSLAR`):
- "tam"       : exact equality (integers, decisions, digests)
- "p"         : absolute ≤ 1e-10
- "ga"        : absolute ≤ 1e-10 (Wilson/Newcombe; tuples element by element)
- "or"        : |A − B| ≤ max(1e-12, 1e-8·max(|A|, |B|)); ∞ and NaN must match exactly
- "bootstrap" : absolute ≤ 1e-12

Decisions are compared with "tam". A decision difference counts as "borderline" (sinirda) only if the reference value
is within TOLERANSLAR["sinir"] of the decision threshold. In that case the exact arithmetic (A) is authoritative and
the difference is reported. All other differences are ERRORS.
"""
from __future__ import annotations

import math
from fractions import Fraction

from .yapilandirma import TOLERANSLAR


def _goster(x):
    if isinstance(x, Fraction):
        return str(x)
    if isinstance(x, float):
        if math.isnan(x):
            return "nan"
        if math.isinf(x):
            return "inf" if x > 0 else "-inf"
        return x
    if isinstance(x, (tuple, list)):
        return [_goster(v) for v in x]
    return x


def yakin(kendi, ref, tur: str) -> tuple[bool, float]:
    """Returns (agreement, deviation). The deviation is relative for kind "or"."""
    if tur == "tam":
        return (kendi == ref, 0.0 if kendi == ref else math.inf)
    if kendi is None or ref is None:
        esit = kendi is None and ref is None
        return (esit, 0.0 if esit else math.inf)
    if isinstance(kendi, (tuple, list)) or isinstance(ref, (tuple, list)):
        if not (isinstance(kendi, (tuple, list)) and isinstance(ref, (tuple, list))) or len(kendi) != len(ref):
            return (False, math.inf)
        sonuclar = [yakin(k, r, tur) for k, r in zip(kendi, ref)]
        return (all(s[0] for s in sonuclar), max((s[1] for s in sonuclar), default=0.0))
    k, r = float(kendi), float(ref)
    if math.isnan(k) or math.isnan(r):
        esit = math.isnan(k) and math.isnan(r)
        return (esit, 0.0 if esit else math.inf)
    if math.isinf(k) or math.isinf(r):
        return (k == r, 0.0 if k == r else math.inf)
    sapma = abs(k - r)
    if tur == "p":
        return (sapma <= TOLERANSLAR["p"], sapma)
    if tur == "ga":
        return (sapma <= TOLERANSLAR["ga"], sapma)
    if tur == "bootstrap":
        return (sapma <= TOLERANSLAR["bootstrap"], sapma)
    if tur == "or":
        olcek = max(abs(k), abs(r))
        tol = max(TOLERANSLAR["or_mutlak"], TOLERANSLAR["or_goreli"] * olcek)
        return (sapma <= tol, sapma / olcek if olcek > 0 else sapma)
    raise ValueError(f"bilinmeyen tür: {tur}")


class Karsilastirici:
    def __init__(self) -> None:
        self.kayitlar: list[dict] = []

    def ekle(self, ad: str, kendi, ref, tur: str, sinir: bool = False) -> bool:
        uyum, sapma = yakin(kendi, ref, tur)
        self.kayitlar.append({
            "ad": ad, "tur": tur, "uyum": uyum, "sinirda": (not uyum) and sinir,
            "sapma": sapma if math.isfinite(sapma) else "inf",
            "kendi": _goster(kendi), "referans": _goster(ref),
        })
        return uyum or sinir

    def ozet(self) -> dict:
        uyumlu = sum(1 for k in self.kayitlar if k["uyum"])
        sinirda = sum(1 for k in self.kayitlar if k["sinirda"])
        hatalar = [k for k in self.kayitlar if not k["uyum"] and not k["sinirda"]]
        sonlu = [k["sapma"] for k in self.kayitlar if k["uyum"] and isinstance(k["sapma"], float)]
        return {
            "toplam": len(self.kayitlar),
            "uyumlu": uyumlu,
            "sinirda": sinirda,
            "hata": len(hatalar),
            "en_buyuk_sapma": max(sonlu, default=0.0),
            "uyusmazliklar": hatalar,
            "sinir_kayitlari": [k for k in self.kayitlar if k["sinirda"]],
        }


def _esige_yakin(deger: float, esik: float) -> bool:
    return abs(float(deger) - float(esik)) <= TOLERANSLAR["sinir"]


def karar_ekle(k: Karsilastirici, ad: str, kendi_karar, ref_karar, ref_deger: float, esik: float) -> bool:
    """Compares a decision; a difference is accepted as 'borderline' only if the reference value is very close to the threshold."""
    return k.ekle(ad, kendi_karar, ref_karar, "tam", sinir=_esige_yakin(ref_deger, esik))


def holm_karsilastir(k: Karsilastirici, kendi: dict, ref: dict, alfa: float = 0.05) -> None:
    for t in kendi:
        k.ekle(f"{t}.p_duzeltilmis", kendi[t]["p_duzeltilmis"], ref[t]["p_duzeltilmis"], "p")
        sinirda = _esige_yakin(ref[t]["p_duzeltilmis"], alfa) or _esige_yakin(float(kendi[t]["p_duzeltilmis"]), alfa)
        # statsmodels gives the rejection as p ≤ α/k; if this value is close to the threshold too, the case is borderline
        k.ekle(f"{t}.red", kendi[t]["red"], ref[t]["red"], "tam", sinir=sinirda)
