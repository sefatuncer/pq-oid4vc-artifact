"""Implementation A — Python standard library only (fractions, math.comb, decimal, statistics).

Exact tests are computed EXACTLY with rational numbers (Fraction). CIs are computed with Decimal (60 digits).
The roots of the conditional OR are searched with integer arithmetic on the exact rational value of ψ = exp(t):
- bisection in t continues down to floating-point resolution;
- every evaluation is an exact integer comparison.

This module does NOT IMPORT scipy/statsmodels/numpy (independence).
"""
from __future__ import annotations

import math
from decimal import Decimal, localcontext
from fractions import Fraction
from statistics import NormalDist
from typing import NamedTuple

from .yapilandirma import ALFA, GUVEN, HOLM_AILESI, NEWCOMBE_ESLESTIRILMIS_PHI

HASSASIYET = 60  # number of Decimal digits

_YARIM = Fraction(1, 2)


def _dogrula(n: int, *xs: int) -> None:
    if not isinstance(n, int) or n < 0:
        raise ValueError(f"n negatif olmayan tamsayı olmalı: {n!r}")
    for x in xs:
        if not isinstance(x, int):
            raise ValueError(f"tamsayı bekleniyordu: {x!r}")


def _hucreler(*xs: int) -> None:
    """Table cells must be non-negative integers."""
    for x in xs:
        if isinstance(x, bool) or not isinstance(x, int) or x < 0:
            raise ValueError(f"tablo hücresi negatif olmayan tamsayı olmalı: {x!r}")


# ---------------------------------------------------------------------------------------------
# Binomial
# ---------------------------------------------------------------------------------------------
def binom_cdf(x: int, n: int, p: Fraction = _YARIM) -> Fraction:
    """P(X ≤ x), X ~ Bin(n, p); exact."""
    _dogrula(n, x)
    if x < 0:
        return Fraction(0)
    if x >= n:
        return Fraction(1)
    p = Fraction(p)
    if p == _YARIM:
        return Fraction(sum(math.comb(n, k) for k in range(x + 1)), 2 ** n)
    q = 1 - p
    return sum((math.comb(n, k) * p ** k * q ** (n - k) for k in range(x + 1)), Fraction(0))


def binom_sf(x: int, n: int, p: Fraction = _YARIM) -> Fraction:
    """P(X ≥ x), X ~ Bin(n, p); exact."""
    _dogrula(n, x)
    if x <= 0:
        return Fraction(1)
    if x > n:
        return Fraction(0)
    return 1 - binom_cdf(x - 1, n, p)


def binom_alt_p(x: int, n: int) -> Fraction:
    """T1: one-sided (lower) exact binomial p-value, H0: p ≥ 0.5 => P(X' ≤ x), X' ~ Bin(n, 1/2)."""
    return binom_cdf(x, n)


def binom_ust_p(x: int, n: int) -> Fraction:
    """T5 (and the T1 falsification tail): one-sided (upper) exact binomial p-value => P(X' ≥ x)."""
    return binom_sf(x, n)


class KritikDeger(NamedTuple):
    c: int | None        # largest c with P(X ≤ c) ≤ α (None if there is none)
    u: int | None        # u = n − c
    P_c: Fraction | None  # P(X ≤ c)


def kritik_degerler(n: int, alfa: Fraction = ALFA) -> KritikDeger:
    """PR Annex A rule: c = max{c : P(X ≤ c) ≤ α}, u = n − c; p0 = 0.5."""
    _dogrula(n)
    alfa = Fraction(alfa)
    payda = 2 ** n
    toplam = 0
    c = None
    P_c = None
    for k in range(n + 1):
        toplam += math.comb(n, k)
        P = Fraction(toplam, payda)
        if P <= alfa:
            c, P_c = k, P
        else:
            break
    return KritikDeger(c, None if c is None else n - c, P_c)


# ---------------------------------------------------------------------------------------------
# McNemar and Fisher (exact, two-sided)
# ---------------------------------------------------------------------------------------------
def mcnemar_kesin(b: int, c: int) -> Fraction:
    """Exact (conditional) McNemar, two-sided: p = min(1, 2·P(Bin(b+c, 1/2) ≤ min(b, c))); b + c = 0 => 1."""
    _hucreler(b, c)
    m = b + c
    if m == 0:
        return Fraction(1)
    return min(Fraction(1), 2 * binom_cdf(min(b, c), m))


def fisher_iki_yonlu(a: int, b: int, c: int, d: int) -> Fraction:
    """Fisher exact test, two-sided: sum over the tables whose probability is not greater than the observed one (exact equality).
    If a row or column total is 0, p = 1."""
    _hucreler(a, b, c, d)
    r1, r2, c1, c2 = a + b, c + d, a + c, b + d
    if 0 in (r1, r2, c1, c2):
        return Fraction(1)
    lo, hi = max(0, c1 - r2), min(r1, c1)
    agirlik = {k: math.comb(r1, k) * math.comb(r2, c1 - k) for k in range(lo, hi + 1)}
    w_gozlenen = agirlik[a]
    return Fraction(sum(w for w in agirlik.values() if w <= w_gozlenen), math.comb(r1 + r2, c1))


# ---------------------------------------------------------------------------------------------
# Wilson and Newcombe (method 10)
# ---------------------------------------------------------------------------------------------
def z_degeri(guven: Fraction = GUVEN) -> float:
    """Φ⁻¹(1 − (1 − confidence)/2); the 0.975 quantile for 95% (statistics.NormalDist)."""
    return NormalDist().inv_cdf(float(1 - (1 - Fraction(guven)) / 2))


def _wilson_dec(x: int, n: int, z: Decimal) -> tuple[Decimal, Decimal]:
    nD, xD = Decimal(n), Decimal(x)
    z2 = z * z
    payda = nD + z2
    merkez = (xD + z2 / 2) / payda
    yarim = z * (xD * (nD - xD) / nD + z2 / 4).sqrt() / payda
    alt = Decimal(0) if x == 0 else merkez - yarim
    ust = Decimal(1) if x == n else merkez + yarim
    return alt, ust


def wilson(x: int, n: int, guven: Fraction = GUVEN) -> tuple[float, float] | None:
    """Wilson score CI (no continuity correction). n = 0 => None. x = 0 => lower = 0; x = n => upper = 1 (exact)."""
    _dogrula(n, x)
    if n == 0:
        return None
    if not 0 <= x <= n:
        raise ValueError("0 ≤ x ≤ n olmalı")
    with localcontext() as ctx:
        ctx.prec = HASSASIYET
        alt, ust = _wilson_dec(x, n, Decimal(z_degeri(guven)))
        return float(alt), float(ust)


def newcombe_bagimsiz(x1: int, n1: int, x2: int, n2: int,
                      guven: Fraction = GUVEN) -> tuple[float, float, float] | None:
    """Newcombe (1998) method 10 for the difference p1 − p2 of independent proportions: square-and-add
    combination of two Wilson intervals (no continuity correction). Returns: (difference, lower, upper)."""
    _dogrula(n1, x1)
    _dogrula(n2, x2)
    if n1 == 0 or n2 == 0:
        return None
    if not (0 <= x1 <= n1 and 0 <= x2 <= n2):
        raise ValueError("0 ≤ x ≤ n olmalı")
    with localcontext() as ctx:
        ctx.prec = HASSASIYET
        z = Decimal(z_degeri(guven))
        p1, p2 = Decimal(x1) / Decimal(n1), Decimal(x2) / Decimal(n2)
        l1, u1 = _wilson_dec(x1, n1, z)
        l2, u2 = _wilson_dec(x2, n2, z)
        fark = p1 - p2
        alt = fark - ((p1 - l1) ** 2 + (u2 - p2) ** 2).sqrt()
        ust = fark + ((u1 - p1) ** 2 + (p2 - l2) ** 2).sqrt()
        return float(fark), float(alt), float(ust)


def newcombe_eslestirilmis(a: int, b: int, c: int, d: int, guven: Fraction = GUVEN,
                           phi_turu: str = NEWCOMBE_ESLESTIRILMIS_PHI) -> tuple[float, float, float, float] | None:
    """Newcombe (1998) method 10 for the difference of paired proportions θ = (a+b)/N − (a+c)/N = (b − c)/N.

    Table layout (condition 1 = treatment T, condition 2 = control K):
      a = event under both conditions; b = only under condition 1; c = only under condition 2; d = under neither.
    L = θ − √(dl1² − 2φ·dl1·du2 + du2²),  U = θ + √(du1² − 2φ·du1·dl2 + dl2²)
      dl1 = p1 − l1, du1 = u1 − p1, dl2 = p2 − l2, du2 = u2 − p2 (Wilson bounds).
    Choice of φ:
      "newcombe_duzeltmeli" (method 10): φ* = max(ad − bc − N/2, 0)/√(efgh) if ad − bc > 0, otherwise φ̂;
      "duz": φ̂ = (ad − bc)/√(efgh);  "sifir": φ = 0.
      If the denominator (efgh) is 0, φ = 0.
    Returns: (difference, lower, upper, φ)."""
    _hucreler(a, b, c, d)
    N = a + b + c + d
    if N == 0:
        return None
    e, f, g, h = a + b, c + d, a + c, b + d
    with localcontext() as ctx:
        ctx.prec = HASSASIYET
        z = Decimal(z_degeri(guven))
        NN = Decimal(N)
        p1, p2 = Decimal(e) / NN, Decimal(g) / NN
        l1, u1 = _wilson_dec(e, N, z)
        l2, u2 = _wilson_dec(g, N, z)
        payda = e * f * g * h
        pay = a * d - b * c
        if phi_turu == "sifir" or payda == 0:
            phi = Decimal(0)
        elif phi_turu == "duz":
            phi = Decimal(pay) / Decimal(payda).sqrt()
        elif phi_turu == "newcombe_duzeltmeli":
            if pay > 0:
                phi = max(Decimal(pay) - NN / 2, Decimal(0)) / Decimal(payda).sqrt()
            else:
                phi = Decimal(pay) / Decimal(payda).sqrt()
        else:
            raise ValueError(f"bilinmeyen phi_turu: {phi_turu}")
        dl1, du1, dl2, du2 = p1 - l1, u1 - p1, p2 - l2, u2 - p2
        delta = max(dl1 * dl1 - 2 * phi * dl1 * du2 + du2 * du2, Decimal(0)).sqrt()
        eps = max(du1 * du1 - 2 * phi * du1 * dl2 + dl2 * dl2, Decimal(0)).sqrt()
        fark = Decimal(b - c) / NN
        return float(fark), float(fark - delta), float(fark + eps), float(phi)


# ---------------------------------------------------------------------------------------------
# Conditional MLE odds ratio and conditional exact CI (Fisher's noncentral hypergeometric)
# ---------------------------------------------------------------------------------------------
def _isaret(x: int) -> int:
    return (x > 0) - (x < 0)


def _terimler(w: list[int], t: float) -> list[int]:
    """ψ = exp(t) (exact fraction num/den of the floating-point value). term_j = w_j · num^j · den^(K−j): exact weights
    multiplied by the common denominator den^K (integers)."""
    num, den = math.exp(t).as_integer_ratio()
    K = len(w) - 1
    npow = [1] * (K + 1)
    dpow = [1] * (K + 1)
    for j in range(1, K + 1):
        npow[j] = npow[j - 1] * num
        dpow[j] = dpow[j - 1] * den
    return [w[j] * npow[j] * dpow[K - j] for j in range(K + 1)]


def _kok_bul(isaret) -> float:
    """isaret(t) ∈ {−1, 0, +1}, increasing in t. Finds the root by bisection down to floating-point resolution."""
    s0 = isaret(0.0)
    if s0 == 0:
        return 0.0
    adim = 1.0
    if s0 < 0:
        alt, ust = 0.0, adim
        while isaret(ust) < 0:
            alt, adim = ust, adim * 2
            ust = adim
            if ust > 700:
                raise ArithmeticError("kök ψ > e^700")
    else:
        alt, ust = -adim, 0.0
        while isaret(alt) > 0:
            ust, adim = alt, adim * 2
            alt = -adim
            if alt < -700:
                raise ArithmeticError("kök ψ < e^-700")
    while True:
        orta = (alt + ust) / 2
        if orta <= alt or orta >= ust:
            break
        s = isaret(orta)
        if s == 0:
            return orta
        if s < 0:
            alt = orta
        else:
            ust = orta
    return (alt + ust) / 2


def kosullu_or(a: int, b: int, c: int, d: int, guven: Fraction = GUVEN) -> tuple[float, float, float]:
    """Conditional MLE OR and conditional exact CI ([[a, b], [c, d]]; direction OR = (a·d)/(b·c)).
    - A row/column total of 0 => (nan, 0, ∞).
    - a at the lower end of the support => MLE = 0, lower = 0; at the upper end => MLE = ∞, upper = ∞.
    - Lower bound: P(X ≥ a; ψ) = (1 − confidence)/2; upper bound: P(X ≤ a; ψ) = (1 − confidence)/2.
    Returns: (mle, lower, upper)."""
    _hucreler(a, b, c, d)
    r1, r2, c1, c2 = a + b, c + d, a + c, b + d
    if 0 in (r1, r2, c1, c2):
        return (math.nan, 0.0, math.inf)
    lo, hi = max(0, c1 - r2), min(r1, c1)
    w = [math.comb(r1, k) * math.comb(r2, c1 - k) for k in range(lo, hi + 1)]
    ja = a - lo
    yarim_alfa = (1 - Fraction(guven)) / 2
    pa, qa = yarim_alfa.numerator, yarim_alfa.denominator

    if a == lo:
        mle = 0.0
    elif a == hi:
        mle = math.inf
    else:
        mle = math.exp(_kok_bul(lambda t: _isaret(sum((j - ja) * v for j, v in enumerate(_terimler(w, t))))))

    if a == lo:
        alt = 0.0
    else:
        def f_alt(t):
            T = _terimler(w, t)
            return _isaret(sum(T[ja:]) * qa - pa * sum(T))          # P(X ≥ a; ψ) − α/2 (increasing in ψ)
        alt = math.exp(_kok_bul(f_alt))

    if a == hi:
        ust = math.inf
    else:
        def f_ust(t):
            T = _terimler(w, t)
            return _isaret(pa * sum(T) - sum(T[:ja + 1]) * qa)      # α/2 − P(X ≤ a; ψ) (increasing in ψ)
        ust = math.exp(_kok_bul(f_ust))
    return (mle, alt, ust)


# ---------------------------------------------------------------------------------------------
# Holm (step-down), exact arithmetic
# ---------------------------------------------------------------------------------------------
def holm(p: dict, alfa: Fraction = ALFA, sira: tuple = HOLM_AILESI) -> dict:
    """Holm correction. Ties in p are broken by the order `sira` (PR family order); the adjusted values
    do not depend on this choice. p_adj(i) = max_{j ≤ i} min(1, (m − j + 1)·p(j)); reject ⇔ p_adj ≤ α."""
    alfa = Fraction(alfa)
    anahtarlar = sorted(p, key=lambda k: (Fraction(p[k]), sira.index(k) if k in sira else len(sira), k))
    m = len(anahtarlar)
    onceki = Fraction(0)
    sonuc = {}
    for i, k in enumerate(anahtarlar):
        pk = Fraction(p[k])
        onceki = max(onceki, min(Fraction(1), (m - i) * pk))
        sonuc[k] = {"sira": i + 1, "p": pk, "p_duzeltilmis": onceki, "red": onceki <= alfa}
    return sonuc


# ---------------------------------------------------------------------------------------------
# Percentile (Hyndman–Fan type 7)
# ---------------------------------------------------------------------------------------------
def yuzdelik_tip7(sirali: list[float], q: Fraction) -> float:
    """Type 7 percentile of a sorted sequence: h = (n − 1)q (0-based); x[⌊h⌋] + (h − ⌊h⌋)(x[⌊h⌋+1] − x[⌊h⌋])."""
    n = len(sirali)
    if n == 0:
        raise ValueError("boş dizi")
    h = (n - 1) * Fraction(q)
    i = math.floor(h)
    kesir = h - i
    if i >= n - 1:
        return float(sirali[n - 1])
    alt, ust = sirali[i], sirali[i + 1]
    if kesir == 0 or alt == ust:
        return float(alt)
    return alt + (ust - alt) * float(kesir)
