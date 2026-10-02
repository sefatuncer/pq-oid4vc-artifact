"""Cluster bootstrap (PR §6.9): unit = library (target), B = 10,000, percentile CI, seed 20260927.

Statistic: pooled proportion θ = Σ x_i / Σ m_i (x_i: cases of target i that disagree with the oracle; m_i: number of determinate cases).

Random stream (full definition; both implementations use the same stream):
  rng = random.Random(tohum)          # Mersenne Twister; Python guarantees the stability of the random() sequence
  clusters are ordered lexicographically by hedef_id; clusters with m_i = 0 are excluded beforehand (k = number remaining)
  for r = 1..B, for j = 1..k: indeks = floor(rng.random() * k)   (replication-major order)
Percentile CI: Hyndman–Fan type 7, q = 1/40 and 39/40.

`kume_bootstrap_saf`: standard library only (A).  `kume_bootstrap_numpy`: vectorised numpy (B).
The result carries the SHA-256 of the bootstrap distribution (binary '<d' representation of the sorted values); it must be
bit-identical in the two implementations.
"""
from __future__ import annotations

import hashlib
import random
import struct
from fractions import Fraction

from .kesin import yuzdelik_tip7
from .yapilandirma import BOOTSTRAP_ALT, BOOTSTRAP_B, BOOTSTRAP_TOHUM, BOOTSTRAP_UST


def indeks_akisi(k: int, adet: int, tohum: int = BOOTSTRAP_TOHUM) -> list[int]:
    rng = random.Random(tohum)
    return [int(rng.random() * k) for _ in range(adet)]


def _hazirla(kumeler):
    temiz = sorted(((str(i), int(x), int(m)) for i, x, m in kumeler), key=lambda t: t[0])
    for i, x, m in temiz:
        if not 0 <= x <= m:
            raise ValueError(f"küme {i}: 0 ≤ x ≤ m olmalı ({x}, {m})")
    dislanan = [i for i, _, m in temiz if m == 0]
    kalan = [t for t in temiz if t[2] > 0]
    return kalan, dislanan


def _dagilim_ozeti(sirali: list[float]) -> dict:
    farkli = sorted(set(sirali))
    oz = {"farkli_deger_sayisi": len(farkli), "min": sirali[0], "max": sirali[-1]}
    if len(farkli) <= 20:
        oz["farkli_degerler"] = farkli
        sayac: dict[str, int] = {}
        for v in sirali:
            sayac[repr(v)] = sayac.get(repr(v), 0) + 1
        oz["sikliklar"] = dict(sorted(sayac.items(), key=lambda kv: float(kv[0])))
    return oz


def _ozet(kalan, dislanan, dagilim_sirali, B, tohum, alt_q, ust_q, uygulama) -> dict:
    sx = sum(x for _, x, _ in kalan)
    sm = sum(m for _, _, m in kalan)
    h = hashlib.sha256(b"".join(struct.pack("<d", v) for v in dagilim_sirali)).hexdigest()
    return {
        "durum": "tamam",
        "uygulama": uygulama,
        "tahmin": sx / sm,
        "alt": yuzdelik_tip7(dagilim_sirali, alt_q) if uygulama == "saf" else None,
        "ust": yuzdelik_tip7(dagilim_sirali, ust_q) if uygulama == "saf" else None,
        "k": len(kalan),
        "toplam_vaka": sm,
        "uymayan_vaka": sx,
        "B": B,
        "tohum": tohum,
        "yuzdelikler": [str(alt_q), str(ust_q)],
        "dislanan_bos_kume": dislanan,
        "dagilim_sha256": h,
        "dagilim_ozeti": _dagilim_ozeti(dagilim_sirali),
    }


def _veri_yok(dislanan, B, tohum, uygulama) -> dict:
    return {"durum": "veri_yok", "uygulama": uygulama, "tahmin": None, "alt": None, "ust": None, "k": 0,
            "toplam_vaka": 0, "uymayan_vaka": 0, "B": B, "tohum": tohum, "dislanan_bos_kume": dislanan,
            "dagilim_sha256": None, "dagilim_ozeti": None}


def kume_bootstrap_saf(kumeler, B: int = BOOTSTRAP_B, tohum: int = BOOTSTRAP_TOHUM,
                       alt_q: Fraction = BOOTSTRAP_ALT, ust_q: Fraction = BOOTSTRAP_UST) -> dict:
    """kumeler: [(hedef_id, x_i, m_i), …]. Standard library only."""
    kalan, dislanan = _hazirla(kumeler)
    if not kalan:
        return _veri_yok(dislanan, B, tohum, "saf")
    k = len(kalan)
    xs = [x for _, x, _ in kalan]
    ms = [m for _, _, m in kalan]
    rng = random.Random(tohum)
    dagilim = []
    for _ in range(B):
        sx = sm = 0
        for _ in range(k):
            i = int(rng.random() * k)
            sx += xs[i]
            sm += ms[i]
        dagilim.append(sx / sm)
    dagilim.sort()
    return _ozet(kalan, dislanan, dagilim, B, tohum, alt_q, ust_q, "saf")


def kume_bootstrap_numpy(kumeler, B: int = BOOTSTRAP_B, tohum: int = BOOTSTRAP_TOHUM,
                         alt_q: Fraction = BOOTSTRAP_ALT, ust_q: Fraction = BOOTSTRAP_UST) -> dict:
    """The same stream as a vectorised numpy computation (implementation B); percentile numpy.quantile(method='linear')."""
    import numpy as np

    kalan, dislanan = _hazirla(kumeler)
    if not kalan:
        return _veri_yok(dislanan, B, tohum, "numpy")
    k = len(kalan)
    xs = np.array([x for _, x, _ in kalan], dtype=np.int64)
    ms = np.array([m for _, _, m in kalan], dtype=np.int64)
    rng = random.Random(tohum)
    U = np.array([rng.random() for _ in range(B * k)], dtype=np.float64).reshape(B, k)
    idx = np.floor(U * k).astype(np.int64)
    sx = xs[idx].sum(axis=1)
    sm = ms[idx].sum(axis=1)
    dagilim = np.sort(sx / sm)
    liste = [float(v) for v in dagilim]
    oz = _ozet(kalan, dislanan, liste, B, tohum, alt_q, ust_q, "numpy")
    oz["alt"] = float(np.quantile(dagilim, float(alt_q), method="linear"))
    oz["ust"] = float(np.quantile(dagilim, float(ust_q), method="linear"))
    return oz
