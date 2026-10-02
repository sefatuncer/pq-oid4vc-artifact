"""Pre-registered analysis constants. The basis of every constant is written next to it.

PR = 00-on-kayit/ON-KAYIT-TASLAK.md (draft v0.6, anchor 5 `facbf26`). In case of conflict the PR prevails.
After the freeze this file does NOT change; an analysis made with a different value is reported only as "exploratory".
Interpretations on which the maintainers have to decide are numbered in `DECISION-NOTES.md` (N-…).
"""
from __future__ import annotations

from fractions import Fraction

SEMA_SURUMU = "c3-istat-girdi/1.0"                  # SCHEMA.md

# --- Significance, confidence level ------------------------------------------------------
ALFA = Fraction(1, 20)                              # PR §6.6: α = 0.05 (T1 uncorrected; T2–T5 Holm)
GUVEN = Fraction(95, 100)                           # PR §6.7–§6.8: 95% CI
P0 = Fraction(1, 2)                                 # PR §6.6: T1 H0 p ≥ 0.5; T5 p ≤ 0.5 (boundary 0.5)

# --- Sample ------------------------------------------------------------------------------
N_BEKLENEN = 31                                     # PR §2B.3 (E2 + quota 18/8/5)
N_EFF_CIKARIMSAL_ALT_SINIR = 20                     # PR §6.3: n_eff < 20 => descriptive only
TABAKALAR_N = ("JOSE", "SDJWT", "COSE")             # PR §2B.1; "REF" outside n (§2B.4)

# --- Test families -----------------------------------------------------------------------
HOLM_AILESI = ("T2", "T3", "T4", "T5")              # PR §6.6 (m = 4; in this order on ties)
T2_TK_KAPSAMI = ("TK1", "TK2")                      # PR §2B.7: T2 only TK1 + TK2
T3_TABAKALAR = ("SDJWT", "JOSE")                    # PR §6.6 T3: "specific to SD-JWT and general JOSE" (N-4: COSE excluded)
T3_TK_KAPSAMI = ("TK1", "TK2", "TK3")               # no TK restriction for T3 in the PR (N-4: maintainers' decision)
T4_L_ESIGI = 3                                      # PR §6.6 T4: "share with L ≥ 3"
T4_KESIM_TARIHI = "2026-08-21"                      # PR §6.6 T4: 8725bis-10 (21.08.2026); "after" = strictly greater (N-5)

# --- Effect sizes --------------------------------------------------------------------------
# Newcombe method 10 (paired): Wilson hybrid + Newcombe's corrected correlation φ*.
# Source and limitation: kaynak/NEWCOMBE-SOURCE.md; DECISION-NOTES N-3.
NEWCOMBE_ESLESTIRILMIS_PHI = "newcombe_duzeltmeli"

# --- Cluster bootstrap ---------------------------------------------------------------------
BOOTSTRAP_B = 10000                                 # PR §6.9
BOOTSTRAP_TOHUM = 20260927                          # PR §6.9, Annex C
BOOTSTRAP_ALT = Fraction(1, 40)                     # percentile CI 2.5% (PR §6.9 "percentile CI"; 95%)
BOOTSTRAP_UST = Fraction(39, 40)                    # percentile CI 97.5%
BOOTSTRAP_YUZDELIK_TIPI = 7                         # Hyndman–Fan type 7 (N-7)
BOOTSTRAP_RNG = "Python random.Random(tohum).random(); indeks = floor(U*k); replikasyon-öncelikli"  # N-7

# --- "Indeterminate" reasons (PR §4.15) --------------------------------------------------
BELIRSIZ_NEDENLERI = ("oracle_uyusmazligi", "kanit_kurali", "kararsiz_3_tekrar", "deneme_celiskisi")
DIGER_NEDENLER = ("uygulanamaz", "olculmedi")

# --- Tolerances for the comparison of the two implementations ----------------------------
# p   : exact fraction ↔ floating-point p-value (absolute)
# ga  : Wilson / Newcombe bounds (absolute; closed form)
# or  : conditional MLE and exact CI (root finding; relative + absolute)
# bootstrap : pure Python ↔ numpy (absolute)
TOLERANSLAR = {
    "p": 1e-10,
    "ga": 1e-10,
    "or_goreli": 1e-8,
    "or_mutlak": 1e-12,
    "bootstrap": 1e-12,
    "sinir": 1e-12,     # floating-point values this close to a decision threshold count as "borderline" (exact arithmetic is authoritative)
}


def ozet() -> dict:
    """Configuration summary written to the output (deterministic)."""
    return {
        "ALFA": str(ALFA),
        "GUVEN": str(GUVEN),
        "P0": str(P0),
        "N_BEKLENEN": N_BEKLENEN,
        "N_EFF_CIKARIMSAL_ALT_SINIR": N_EFF_CIKARIMSAL_ALT_SINIR,
        "HOLM_AILESI": list(HOLM_AILESI),
        "T2_TK_KAPSAMI": list(T2_TK_KAPSAMI),
        "T3_TABAKALAR": list(T3_TABAKALAR),
        "T3_TK_KAPSAMI": list(T3_TK_KAPSAMI),
        "T4_L_ESIGI": T4_L_ESIGI,
        "T4_KESIM_TARIHI": T4_KESIM_TARIHI,
        "NEWCOMBE_ESLESTIRILMIS_PHI": NEWCOMBE_ESLESTIRILMIS_PHI,
        "BOOTSTRAP_B": BOOTSTRAP_B,
        "BOOTSTRAP_TOHUM": BOOTSTRAP_TOHUM,
        "BOOTSTRAP_ALT": str(BOOTSTRAP_ALT),
        "BOOTSTRAP_UST": str(BOOTSTRAP_UST),
        "BOOTSTRAP_YUZDELIK_TIPI": BOOTSTRAP_YUZDELIK_TIPI,
        "BOOTSTRAP_RNG": BOOTSTRAP_RNG,
        "TOLERANSLAR": dict(TOLERANSLAR),
    }
