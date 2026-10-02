"""Implementation B — libraries: scipy 1.17.1, statsmodels 0.15.0, numpy 2.4.6 (versions pinned in requirements.txt).

Same signatures as implementation A (`kesin`); the outputs are floating-point. There is no ready-made library function
for the paired Newcombe interval: the Wilson bounds are taken from statsmodels, the combination is written separately with numpy.
This module does NOT IMPORT the `kesin` module (independence).
"""
from __future__ import annotations

import math

import numpy as np
from scipy import stats
from scipy.stats.contingency import odds_ratio
from statsmodels.stats.contingency_tables import mcnemar
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import confint_proportions_2indep, proportion_confint

from .yapilandirma import NEWCOMBE_ESLESTIRILMIS_PHI

_ALFA = 0.05


def binom_alt_p(x: int, n: int) -> float:
    if n == 0:
        return 1.0
    return float(stats.binomtest(x, n, 0.5, alternative="less").pvalue)


def binom_ust_p(x: int, n: int) -> float:
    if n == 0:
        return 1.0
    return float(stats.binomtest(x, n, 0.5, alternative="greater").pvalue)


def kritik_degerler(n: int, alfa: float = _ALFA) -> tuple[int | None, int | None, float | None]:
    c, P = None, None
    for k in range(n + 1):
        v = float(stats.binom.cdf(k, n, 0.5))
        if v <= alfa:
            c, P = k, v
        else:
            break
    return c, (None if c is None else n - c), P


def mcnemar_kesin(b: int, c: int) -> float:
    return float(mcnemar(np.array([[0, b], [c, 0]]), exact=True).pvalue)


def fisher_iki_yonlu(a: int, b: int, c: int, d: int) -> float:
    return float(stats.fisher_exact(np.array([[a, b], [c, d]], dtype=np.int64), alternative="two-sided").pvalue)


def wilson(x: int, n: int) -> tuple[float, float] | None:
    if n == 0:
        return None
    alt, ust = proportion_confint(x, n, alpha=_ALFA, method="wilson")
    return float(alt), float(ust)


def newcombe_bagimsiz(x1: int, n1: int, x2: int, n2: int) -> tuple[float, float, float] | None:
    if n1 == 0 or n2 == 0:
        return None
    alt, ust = confint_proportions_2indep(x1, n1, x2, n2, method="newcomb", compare="diff", alpha=_ALFA)
    return float(x1 / n1 - x2 / n2), float(alt), float(ust)


def newcombe_eslestirilmis(a: int, b: int, c: int, d: int,
                           phi_turu: str = NEWCOMBE_ESLESTIRILMIS_PHI) -> tuple[float, float, float, float] | None:
    N = a + b + c + d
    if N == 0:
        return None
    n1p, np1 = a + b, a + c              # event counts of condition 1 (T) and condition 2 (K)
    n2p, np2 = c + d, b + d
    alt_w, ust_w = proportion_confint(np.array([n1p, np1]), np.array([N, N]), alpha=_ALFA, method="wilson")
    l1, l2 = float(alt_w[0]), float(alt_w[1])
    u1, u2 = float(ust_w[0]), float(ust_w[1])
    p1, p2 = n1p / N, np1 / N
    payda = float(n1p) * float(n2p) * float(np1) * float(np2)
    pay = float(a * d - b * c)
    if phi_turu == "sifir" or payda == 0.0:
        phi = 0.0
    elif phi_turu == "duz":
        phi = pay / math.sqrt(payda)
    elif phi_turu == "newcombe_duzeltmeli":
        phi = (max(pay - N / 2.0, 0.0) if pay > 0 else pay) / math.sqrt(payda)
    else:
        raise ValueError(phi_turu)
    fark = (b - c) / N
    alt = fark - np.sqrt(max(0.0, (p1 - l1) ** 2 + (u2 - p2) ** 2 - 2.0 * (p1 - l1) * (u2 - p2) * phi))
    ust = fark + np.sqrt(max(0.0, (u1 - p1) ** 2 + (p2 - l2) ** 2 - 2.0 * (u1 - p1) * (p2 - l2) * phi))
    return float(fark), float(alt), float(ust), float(phi)


def kosullu_or(a: int, b: int, c: int, d: int) -> tuple[float, float, float]:
    sonuc = odds_ratio(np.array([[a, b], [c, d]], dtype=np.int64), kind="conditional")
    ga = sonuc.confidence_interval(confidence_level=1 - _ALFA, alternative="two-sided")
    return float(sonuc.statistic), float(ga.low), float(ga.high)


def holm(p: dict) -> dict:
    anahtarlar = list(p)
    red, duz, _, _ = multipletests([float(p[k]) for k in anahtarlar], alpha=_ALFA, method="holm")
    return {k: {"p": float(p[k]), "p_duzeltilmis": float(duz[i]), "red": bool(red[i])}
            for i, k in enumerate(anahtarlar)}


def yuzdelik_tip7(dizi, q) -> float:
    return float(np.quantile(np.asarray(dizi, dtype=np.float64), float(q), method="linear"))
