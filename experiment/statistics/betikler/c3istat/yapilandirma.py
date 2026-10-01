"""Önceden kayıtlı analiz sabitleri. Her sabitin dayanağı yanında yazılıdır.

ÖK = 00-on-kayit/ON-KAYIT-TASLAK.md (taslak v0.6, çapa 5 `facbf26`). Çelişkide ÖK geçerlidir.
Dondurmadan sonra bu dosya DEĞİŞMEZ; farklı bir değerle yapılan analiz yalnız "keşifsel" olarak raporlanır.
Yürütücünün karar vermesi gereken yorumlar `KARAR-NOTLARI.md`'de numaralıdır (N-…).
"""
from __future__ import annotations

from fractions import Fraction

SEMA_SURUMU = "c3-istat-girdi/1.0"                  # SEMA.md

# --- Anlamlılık, güven düzeyi -------------------------------------------------------------
ALFA = Fraction(1, 20)                              # ÖK §6.6: α = 0,05 (T1 düzeltmesiz; T2–T5 Holm)
GUVEN = Fraction(95, 100)                           # ÖK §6.7–§6.8: %95 GA
P0 = Fraction(1, 2)                                 # ÖK §6.6: T1 H0 p ≥ 0,5; T5 p ≤ 0,5 (sınır 0,5)

# --- Örneklem -----------------------------------------------------------------------------
N_BEKLENEN = 31                                     # ÖK §2B.3 (E2 + kota 18/8/5)
N_EFF_CIKARIMSAL_ALT_SINIR = 20                     # ÖK §6.3: n_eff < 20 => yalnız tanımlayıcı
TABAKALAR_N = ("JOSE", "SDJWT", "COSE")             # ÖK §2B.1; "REF" n dışı (§2B.4)

# --- Test aileleri ------------------------------------------------------------------------
HOLM_AILESI = ("T2", "T3", "T4", "T5")              # ÖK §6.6 (m = 4; eşitlikte bu sıra)
T2_TK_KAPSAMI = ("TK1", "TK2")                      # ÖK §2B.7: T2 yalnız TK1 + TK2
T3_TABAKALAR = ("SDJWT", "JOSE")                    # ÖK §6.6 T3: "SD-JWT'ye özgü ve genel JOSE" (N-4: COSE dışarıda)
T3_TK_KAPSAMI = ("TK1", "TK2", "TK3")               # ÖK'de T3 için TK kısıtı yok (N-4: yürütücü kararı)
T4_L_ESIGI = 3                                      # ÖK §6.6 T4: "L ≥ 3 oranı"
T4_KESIM_TARIHI = "2026-08-21"                      # ÖK §6.6 T4: 8725bis-10 (21.08.2026); "sonra" = kesin büyük (N-5)

# --- Etki büyüklükleri --------------------------------------------------------------------
# Newcombe yöntem 10 (eşleştirilmiş): Wilson-hibrit + Newcombe'un düzeltilmiş korelasyonu φ*.
# Kaynak ve sınırlılık: kaynak/NEWCOMBE-KAYNAK.md; NOTLAR N-3.
NEWCOMBE_ESLESTIRILMIS_PHI = "newcombe_duzeltmeli"

# --- Küme bootstrap -----------------------------------------------------------------------
BOOTSTRAP_B = 10000                                 # ÖK §6.9
BOOTSTRAP_TOHUM = 20260927                          # ÖK §6.9, Ek C
BOOTSTRAP_ALT = Fraction(1, 40)                     # yüzdelik GA %2,5 (ÖK §6.9 "yüzdelik GA"; %95)
BOOTSTRAP_UST = Fraction(39, 40)                    # yüzdelik GA %97,5
BOOTSTRAP_YUZDELIK_TIPI = 7                         # Hyndman–Fan tip 7 (N-7)
BOOTSTRAP_RNG = "Python random.Random(tohum).random(); indeks = floor(U*k); replikasyon-öncelikli"  # N-7

# --- "Belirsiz" nedenleri (ÖK §4.15) ------------------------------------------------------
BELIRSIZ_NEDENLERI = ("oracle_uyusmazligi", "kanit_kurali", "kararsiz_3_tekrar", "deneme_celiskisi")
DIGER_NEDENLER = ("uygulanamaz", "olculmedi")

# --- İki uygulama karşılaştırma toleransları ----------------------------------------------
# p   : kesin kesir ↔ kayan nokta p-değeri (mutlak)
# ga  : Wilson / Newcombe sınırları (mutlak; kapalı biçim)
# or  : koşullu MLE ve kesin GA (kök bulma; göreli + mutlak)
# bootstrap : saf Python ↔ numpy (mutlak)
TOLERANSLAR = {
    "p": 1e-10,
    "ga": 1e-10,
    "or_goreli": 1e-8,
    "or_mutlak": 1e-12,
    "bootstrap": 1e-12,
    "sinir": 1e-12,     # karar eşiğine bu kadar yakın kayan nokta değerleri "sınırda" sayılır (kesin aritmetik esastır)
}


def ozet() -> dict:
    """Çıktıya yazılan yapılandırma özeti (belirlenimci)."""
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
