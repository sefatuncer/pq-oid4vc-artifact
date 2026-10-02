"""C3 (H6) pre-registered analysis pipeline.

PR mapping (detailed traceability: FREEZE-INPUT.md §4):
  T1 (§3.7, §2B.5, §6.3, §6.6, §6.13, Annex A)  -> t1_karari, _t1
  H6 verdict, sensitivity (i)/(ii) (§6.10)      -> h6_hukmu, _t1_duyarliliklar
  pilot (§0.3, §6.10), delegation (§2B.9)       -> _t1_duyarliliklar, _t2 (delegating targets excluded)
  T2 (§6.6, §2B.7; only TK1+TK2)                -> _t2
  T3, T4 (§6.6)                                 -> _fisher_blok
  T5 (§6.6)                                     -> _t5
  Holm T2–T5 (§6.6)                             -> _holm
  Effect sizes (§6.7)                           -> _t1, _t2, _fisher_blok, _t5
  Wilson: every L and flag (§6.8)               -> _wilson_tablolari
  Cluster bootstrap (§6.9)                      -> _bootstrap
  Number of undecided cells (§6.11)             -> _tanimlayici
Every numerical output is produced by A (exact) and compared with B (library); a disagreement = invalid analysis.
"""
from __future__ import annotations

import glob
import hashlib
import json
import math
import os
import platform
from fractions import Fraction

from . import __version__, bootstrap, kesin, referans, sema
from . import yapilandirma as Y
from .karsilastir import Karsilastirici, holm_karsilastir, karar_ekle

_ALFA_F = float(Y.ALFA)


# ---------------------------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------------------------
def _p(kesin_deger: Fraction, ref_deger: float) -> dict:
    return {"kesin": str(kesin_deger), "deger": float(kesin_deger), "referans": ref_deger}


def _oran(x: int, n: int):
    return x / n if n else None


def _ids(hedefler) -> list[str]:
    return sorted(h["hedef_id"] for h in hedefler)


# ---------------------------------------------------------------------------------------------
# T1 and H6
# ---------------------------------------------------------------------------------------------
def t1_karari(X: int, n: int) -> dict:
    """PR §6.3: n_eff < 20 => 'tanimlayici'. Otherwise c(n), u = n − c by the Annex A rule:
    X ≤ c => 'destek'; X ≥ u => 'yanlislama'; in between => 'belirsiz' (PR §3.7, §2B.5, §6.13)."""
    kd = kesin.kritik_degerler(n)
    if n < Y.N_EFF_CIKARIMSAL_ALT_SINIR:
        karar = "tanimlayici"
    elif kd.c is not None and X <= kd.c:
        karar = "destek"
    elif kd.u is not None and X >= kd.u:
        karar = "yanlislama"
    else:
        karar = "belirsiz"
    return {"n_eff": n, "X": X, "c": kd.c, "u": kd.u, "P_c": None if kd.P_c is None else str(kd.P_c),
            "karar": karar}


def _t1(degerler: list[tuple[str, int]], k: Karsilastirici, etiket: str, aciklama: str) -> dict:
    n = len(degerler)
    X = sum(y for _, y in degerler)
    s = t1_karari(X, n)
    c_r, u_r, _ = referans.kritik_degerler(n)
    k.ekle(f"{etiket}.c", s["c"], c_r, "tam")
    k.ekle(f"{etiket}.u", s["u"], u_r, "tam")
    p_alt, p_ust = kesin.binom_alt_p(X, n), kesin.binom_ust_p(X, n)
    r_alt, r_ust = referans.binom_alt_p(X, n), referans.binom_ust_p(X, n)
    k.ekle(f"{etiket}.p_alt", p_alt, r_alt, "p")
    k.ekle(f"{etiket}.p_ust", p_ust, r_ust, "p")
    if n >= Y.N_EFF_CIKARIMSAL_ALT_SINIR:
        # The threshold decision and the reference p-value decision must agree (support ⇔ P(X' ≤ X) ≤ α; falsification ⇔ P(X' ≥ X) ≤ α)
        karar_ekle(k, f"{etiket}.karar_destek", s["karar"] == "destek", r_alt <= _ALFA_F, r_alt, _ALFA_F)
        karar_ekle(k, f"{etiket}.karar_yanlislama", s["karar"] == "yanlislama", r_ust <= _ALFA_F, r_ust, _ALFA_F)
    w, wr = kesin.wilson(X, n), referans.wilson(X, n)
    k.ekle(f"{etiket}.wilson", w, wr, "ga")
    s.update({
        "aciklama": aciklama,
        "p_alt": _p(p_alt, r_alt),
        "p_ust": _p(p_ust, r_ust),
        "oran": _oran(X, n),
        "wilson": list(w) if w else None,
        "fark_0_5": (X / n - 0.5) if n else None,
        "fark_0_5_ga": [w[0] - 0.5, w[1] - 0.5] if w else None,
        "holm_disi": True,
    })
    return s


def h6_hukmu(birincil: dict, duyarlilik_i: dict, duyarlilik_ii: dict | None = None) -> dict:
    """PR §6.10: 'destek' = primary AND (i) X ≤ c; primary only => 'kirilgan_destek'.
    Symmetric rule (Amendment 8 item 17): 'yanlislama' = primary AND (ii) X ≥ u; primary only =>
    'kirilgan_yanlislama'. n_eff < 20 => 'tanimlayici' (PR §6.3; no claim of a majority or of its absence is made)."""
    kb, ki = birincil["karar"], duyarlilik_i["karar"]
    kii = duyarlilik_ii["karar"] if duyarlilik_ii is not None else None
    if kb == "tanimlayici":
        return {"hukum": "tanimlayici", "birincil": kb, "duyarlilik_i": ki,
                "gerekce": "n_eff < 20: yalnız tanımlayıcı sonuç (Wilson GA) verilir (ÖK §6.3)"}
    if kb == "destek":
        if ki == "destek":
            return {"hukum": "destek", "birincil": kb, "duyarlilik_i": ki,
                    "gerekce": "birincil analiz ve duyarlılık (i) birlikte X ≤ c (ÖK §6.10)"}
        return {"hukum": "kirilgan_destek", "birincil": kb, "duyarlilik_i": ki,
                "gerekce": "yalnız birincil analiz X ≤ c; duyarlılık (i) değil (ÖK §6.10)"}
    if kb == "yanlislama":
        if kii is None or kii == "yanlislama":
            return {"hukum": "yanlislama", "birincil": kb, "duyarlilik_i": ki, "duyarlilik_ii": kii,
                    "gerekce": "birincil analiz ve duyarlılık (ii) birlikte X ≥ u (ÖK §3.7, §2B.5; Değişiklik 8 m.17)"}
        return {"hukum": "kirilgan_yanlislama", "birincil": kb, "duyarlilik_i": ki, "duyarlilik_ii": kii,
                "gerekce": "yalnız birincil analiz X ≥ u; duyarlılık (ii) değil (Değişiklik 8 m.17)"}
    return {"hukum": "belirsiz", "birincil": kb, "duyarlilik_i": ki, "gerekce": "c < X < u (ÖK §6.13)"}


def _t1_duyarliliklar(H_g: list[dict], k: Karsilastirici, gecersiz: list[dict] | None = None) -> dict:
    belirli = [h for h in H_g if h["Y_L4"] is not None]
    gecersiz = gecersiz or []
    belirsiz = [h for h in H_g if h["Y_L4"] is None]
    temel = [(h["hedef_id"], h["Y_L4"]) for h in belirli]
    ek1 = [(h["hedef_id"], 1) for h in belirsiz]
    ek0 = [(h["hedef_id"], 0) for h in belirsiz]
    pilot_haric = [(h["hedef_id"], h["Y_L4"]) for h in belirli if h["pilot"] != 1]
    devir_haric = [(h["hedef_id"], h["Y_L4"]) for h in belirli if h["devralan"] != 1]
    d = {
        "i_belirsiz_1": _t1(temel + ek1, k, "T1.dus_i", "ÖK §6.10 (i): belirsiz hedefler Y = 1 (H6 aleyhine)"),
        "ii_belirsiz_0": _t1(temel + ek0, k, "T1.dus_ii", "ÖK §6.10 (ii): belirsiz hedefler Y = 0"),
        "pilot_haric": _t1(pilot_haric, k, "T1.dus_pilot", "ÖK §0.3, §6.10, §12.5: P3 ve ikinci pilotta görülen kütüphaneler hariç"),
        "devralan_haric": _t1(devir_haric, k, "T1.dus_devir",
                              "ÖK §2B.9: devralan hedefler hariç; tanımlayıcı, Holm dışı"),
        "gecersiz_y0": _t1(temel + [(h["hedef_id"], 0) for h in gecersiz], k, "T1.dus_gecersiz",
                           "Değişiklik 10: adaptör geçersiz hedefler (SDJWT-021) Y = 0 sayılarak; eşikler kendi n'inden"),
    }
    d["gecersiz_y0"]["eklenen"] = _ids(gecersiz)
    d["i_belirsiz_1"]["eklenen"] = _ids(belirsiz)
    d["ii_belirsiz_0"]["eklenen"] = _ids(belirsiz)
    d["pilot_haric"]["dislanan"] = _ids(h for h in belirli if h["pilot"] == 1)
    d["devralan_haric"]["dislanan"] = _ids(h for h in belirli if h["devralan"] == 1)
    return d


# ---------------------------------------------------------------------------------------------
# T2 (exact McNemar) and paired effect
# ---------------------------------------------------------------------------------------------
def _ciftler_tablosu(hedefler: list[dict]) -> dict:
    t = {"a": 0, "b": 0, "c": 0, "d": 0}
    for h in hedefler:
        fk, ft = h["F_K"], h["F_T"]
        t["a" if (fk, ft) == (1, 1) else "b" if (fk, ft) == (0, 1) else "c" if (fk, ft) == (1, 0) else "d"] += 1
    return t


def _t2(hedefler: list[dict], k: Karsilastirici, etiket: str, holm_disi: bool, aciklama: str) -> dict:
    t = _ciftler_tablosu(hedefler)
    N = sum(t.values())
    p, pr = kesin.mcnemar_kesin(t["b"], t["c"]), referans.mcnemar_kesin(t["b"], t["c"])
    k.ekle(f"{etiket}.p", p, pr, "p")
    etki = None
    if N:
        e = kesin.newcombe_eslestirilmis(t["a"], t["b"], t["c"], t["d"])
        er = referans.newcombe_eslestirilmis(t["a"], t["b"], t["c"], t["d"])
        k.ekle(f"{etiket}.newcombe10", e, er, "ga")
        etki = {"fark": e[0], "alt": e[1], "ust": e[2], "phi": e[3], "tanim": "P(F_T=1) − P(F_K=1)",
                "yontem": "Newcombe (1998) yöntem 10, eşleştirilmiş (φ* düzeltmeli); ÖK §6.7",
                "referans": {"alt": er[1], "ust": er[2]}}
    return {"test": "T2", "aciklama": aciklama, "kapsam": list(Y.T2_TK_KAPSAMI), "n_cift": N, "tablo": t,
            "tablo_tanimi": "a=(F_K=1,F_T=1), b=(F_K=0,F_T=1), c=(F_K=1,F_T=0), d=(F_K=0,F_T=0)",
            "b": t["b"], "c": t["c"], "p": _p(p, pr), "etki": etki, "veri_yok": N == 0, "holm_disi": holm_disi,
            "hedefler": _ids(hedefler)}


# ---------------------------------------------------------------------------------------------
# T3, T4 (Fisher exact) and independent effect sizes
# ---------------------------------------------------------------------------------------------
def _fisher_blok(test: str, satirlar: list[str], sutunlar: list[str], tablo: list[list[int]],
                 k: Karsilastirici, aciklama: str) -> dict:
    (a, b), (c, d) = tablo
    p, pr = kesin.fisher_iki_yonlu(a, b, c, d), referans.fisher_iki_yonlu(a, b, c, d)
    k.ekle(f"{test}.p", p, pr, "p")
    o, orr = kesin.kosullu_or(a, b, c, d), referans.kosullu_or(a, b, c, d)
    k.ekle(f"{test}.or_kosullu", o, orr, "or")
    fark = None
    if a + b and c + d:
        f, fr = kesin.newcombe_bagimsiz(a, a + b, c, c + d), referans.newcombe_bagimsiz(a, a + b, c, c + d)
        k.ekle(f"{test}.newcombe10", f, fr, "ga")
        fark = {"fark": f[0], "alt": f[1], "ust": f[2], "tanim": f"p({satirlar[0]}) − p({satirlar[1]})",
                "yontem": "Newcombe (1998) yöntem 10, bağımsız; ÖK §6.7", "referans": {"alt": fr[1], "ust": fr[2]}}
    return {"test": test, "aciklama": aciklama, "satirlar": satirlar, "sutunlar": sutunlar, "tablo": [[a, b], [c, d]],
            "n": a + b + c + d, "p": _p(p, pr),
            "or": {"mle": o[0], "alt": o[1], "ust": o[2],
                   "yontem": "koşullu MLE + koşullu kesin GA (Fisher merkezsiz hipergeometrik); ÖK §6.7",
                   "referans": {"mle": orr[0], "alt": orr[1], "ust": orr[2]}},
            "fark": fark, "oranlar": {satirlar[0]: _oran(a, a + b), satirlar[1]: _oran(c, c + d)},
            "veri_yok": a + b + c + d == 0}


def _t3(H_g: list[dict], k: Karsilastirici) -> dict:
    kapsam = [h for h in H_g if h["tabaka"] in Y.T3_TABAKALAR and h.get("tk_sinifi") in Y.T3_TK_KAPSAMI
              and h["F_K"] is not None and h["F_T"] is not None]
    tablo = []
    for tabaka in Y.T3_TABAKALAR:
        grup = [h for h in kapsam if h["tabaka"] == tabaka]
        pq = sum(1 for h in grup if h["F_T"] == 1 and h["F_K"] == 0)
        tablo.append([pq, len(grup) - pq])
    s = _fisher_blok("T3", list(Y.T3_TABAKALAR), ["PQ_ozgu=1", "PQ_ozgu=0"], tablo, k,
                     "ÖK §6.6 T3: PQ'ya özgü başarısızlık (F_T=1 ∧ F_K=0) oranı SD-JWT ve JOSE'de farklı mı? "
                     "Fisher kesin, iki yönlü; Holm (T2–T5)")
    s["tk_kapsami"] = list(Y.T3_TK_KAPSAMI)
    s["hedefler"] = _ids(kapsam)
    return s


def _t4(H_g: list[dict], k: Karsilastirici) -> dict:
    kapsam = [h for h in H_g if h["L_duzeyi"] is not None and h["surum_8725bis_sonrasi"] is not None]
    tablo = []
    for grup_deger in (1, 0):
        grup = [h for h in kapsam if h["surum_8725bis_sonrasi"] == grup_deger]
        ust = sum(1 for h in grup if h["L_duzeyi"] >= Y.T4_L_ESIGI)
        tablo.append([ust, len(grup) - ust])
    s = _fisher_blok("T4", ["8725bis_sonrasi=1", "8725bis_sonrasi=0"], [f"L>={Y.T4_L_ESIGI}", f"L<{Y.T4_L_ESIGI}"],
                     tablo, k, f"ÖK §6.6 T4: L ≥ {Y.T4_L_ESIGI} oranı, 8725bis-10'dan ({Y.T4_KESIM_TARIHI}) sonra "
                     "sürüm çıkaran ve çıkarmayan hedeflerde farklı mı? Fisher kesin, iki yönlü; Holm (T2–T5)")
    s["hedefler"] = _ids(kapsam)
    return s


# ---------------------------------------------------------------------------------------------
# T5
# ---------------------------------------------------------------------------------------------
def _t5(H_g: list[dict], k: Karsilastirici) -> dict:
    kapsam = [h for h in H_g if h["D_soy"] is not None]
    n = len(kapsam)
    X = sum(h["D_soy"] for h in kapsam)
    p, pr = kesin.binom_ust_p(X, n), referans.binom_ust_p(X, n)
    k.ekle("T5.p", p, pr, "p")
    w, wr = kesin.wilson(X, n), referans.wilson(X, n)
    k.ekle("T5.wilson", w, wr, "ga")
    return {"test": "T5", "aciklama": "ÖK §6.6 T5: varsayılan yapılandırmada soyulmuş belgeyi kabul oranı > 0,5 mi? "
                                      "Kesin binom, tek yönlü (üst); Holm (T2–T5)",
            "n": n, "X": X, "p": _p(p, pr), "oran": _oran(X, n), "wilson": list(w) if w else None,
            "veri_yok": n == 0, "hedefler": _ids(kapsam)}


# ---------------------------------------------------------------------------------------------
# Holm
# ---------------------------------------------------------------------------------------------
def _holm(testler: dict, k: Karsilastirici) -> dict:
    p_kesin = {t: Fraction(testler[t]["p"]["kesin"]) for t in Y.HOLM_AILESI}
    p_ref = {t: testler[t]["p"]["referans"] for t in Y.HOLM_AILESI}
    h = kesin.holm(p_kesin, alfa=Y.ALFA, sira=Y.HOLM_AILESI)
    hr = referans.holm(p_ref)
    holm_karsilastir(k, h, hr, alfa=_ALFA_F)
    sonuclar = {}
    for t in Y.HOLM_AILESI:
        sonuclar[t] = {"sira": h[t]["sira"], "p": _p(h[t]["p"], p_ref[t]),
                       "p_duzeltilmis": _p(h[t]["p_duzeltilmis"], hr[t]["p_duzeltilmis"]),
                       "red": h[t]["red"], "red_referans": hr[t]["red"], "veri_yok": testler[t]["veri_yok"]}
    return {"aile": list(Y.HOLM_AILESI), "alfa": str(Y.ALFA), "m": len(Y.HOLM_AILESI),
            "not": "Veri yoksa p = 1 alınır ve aile boyutu m = 4 korunur; T1 aile dışıdır (ÖK §6.6).",
            "sonuclar": sonuclar}


# ---------------------------------------------------------------------------------------------
# Wilson tables (PR §6.8)
# ---------------------------------------------------------------------------------------------
def _w(x: int, n: int, k: Karsilastirici, ad: str) -> dict:
    w, wr = kesin.wilson(x, n), referans.wilson(x, n)
    k.ekle(ad, w, wr, "ga")
    return {"x": x, "n": n, "oran": _oran(x, n), "ga": list(w) if w else None}


def _wilson_tablolari(H_g: list[dict], k: Karsilastirici) -> dict:
    out: dict = {}
    L = [h["L_duzeyi"] for h in H_g if h["L_duzeyi"] is not None]
    nL = len(L)
    out["L_duzeyi"] = {"n": nL, **{f"L{d}": _w(sum(1 for v in L if v == d), nL, k, f"wilson.L{d}") for d in range(6)}}
    out["L_en_az"] = {"n": nL, "not": "tanımlayıcı ek (L ≥ k)",
                      **{f"L{d}": _w(sum(1 for v in L if v >= d), nL, k, f"wilson.L>={d}") for d in range(1, 6)}}
    bay: dict = {}
    for alan, kategoriler in (("B1", sema.ENUM["B1"]), ("B5", sema.ENUM["B5"])):
        degerler = [h[alan] for h in H_g if h[alan] is not None]
        bay[alan] = {"n": len(degerler),
                     **{kat: _w(sum(1 for v in degerler if v == kat), len(degerler), k, f"wilson.{alan}.{kat}")
                        for kat in kategoriler}}
    for alan in ("B2", "B3", "B4_ozel_kod", "B6"):
        degerler = [h[alan] for h in H_g if h[alan] is not None]
        bay[alan] = {"n": len(degerler), "1": _w(sum(degerler), len(degerler), k, f"wilson.{alan}")}
    out["bayraklar"] = bay
    yb = {}
    for bicim in sema.ENUM["l4_bicimi"]:
        g = [h["Y_L4"] for h in H_g if h.get("l4_bicimi") == bicim and h["Y_L4"] is not None]
        yb[bicim] = _w(sum(g), len(g), k, f"wilson.Y_L4.{bicim}")
    out["Y_L4_l4_bicimine_gore"] = dict(yb, **{"not": "tanımlayıcı (ÖK §2B.6: uygulanan biçim hedef başına raporlanır)"})
    return out


# ---------------------------------------------------------------------------------------------
# Cluster bootstrap (PR §6.9)
# ---------------------------------------------------------------------------------------------
def _bootstrap(H_g: list[dict], vakalar: list[dict], k: Karsilastirici) -> dict:
    gecerli = {h["hedef_id"] for h in H_g}
    out = {}
    for kapsam in ("tum", "K", "T"):
        kume: dict[str, list[int]] = {}
        for v in vakalar:
            if v["hedef_id"] not in gecerli or (kapsam != "tum" and v["kol"] != kapsam):
                continue
            x_m = kume.setdefault(v["hedef_id"], [0, 0])
            if v["uyum"] is not None:
                x_m[0] += 1 - v["uyum"]
                x_m[1] += 1
        kumeler = [(hid, xm[0], xm[1]) for hid, xm in kume.items()]
        saf = bootstrap.kume_bootstrap_saf(kumeler)
        npy = bootstrap.kume_bootstrap_numpy(kumeler)
        for alan in ("tahmin", "alt", "ust"):
            k.ekle(f"bootstrap.{kapsam}.{alan}", saf[alan], npy[alan], "bootstrap")
        k.ekle(f"bootstrap.{kapsam}.dagilim_sha256", saf["dagilim_sha256"], npy["dagilim_sha256"], "tam")
        saf["referans"] = {"alt": npy["alt"], "ust": npy["ust"], "dagilim_sha256": npy["dagilim_sha256"]}
        saf["olcu"] = "oracle'a uymayan vaka oranı (havuzlanmış: Σ uymayan / Σ belirli vaka)"
        saf["kapsam"] = {"tum": "bütün vakalar", "K": "kontrol kolu", "T": "tedavi kolu"}[kapsam]
        out[kapsam] = saf
    return out


# ---------------------------------------------------------------------------------------------
# Descriptive statistics
# ---------------------------------------------------------------------------------------------
def _sayim(degerler) -> dict:
    s: dict = {}
    for v in degerler:
        anahtar = "kayitsiz" if v is None else str(v)
        s[anahtar] = s.get(anahtar, 0) + 1
    return dict(sorted(s.items()))


def _tanimlayici(H_n: list[dict], H_g: list[dict], ref: list[dict], vakalar: list[dict]) -> dict:
    nedenler: dict = {}
    for h in H_g:
        for alan, neden in h["belirsiz_nedenleri"].items():
            nedenler.setdefault(alan, {}).setdefault(neden, 0)
            nedenler[alan][neden] += 1
    b4 = sorted(h["B4_satir"] for h in H_g if h["B4_ozel_kod"] == 1 and h["B4_satir"] is not None)
    medyan = None
    if b4:
        m = len(b4)
        medyan = b4[m // 2] if m % 2 else (b4[m // 2 - 1] + b4[m // 2]) / 2
    gecerli = {h["hedef_id"] for h in H_g}
    vaka_neden = _sayim(v["belirsiz_neden"] for v in vakalar if v["uyum"] is None and v["hedef_id"] in gecerli)
    tk3 = [h for h in H_g if h.get("tk_sinifi") == "TK3" and h["F_K"] is not None and h["F_T"] is not None]
    t3tab = _ciftler_tablosu(tk3)
    return {
        "tabaka": _sayim(h["tabaka"] for h in H_n),
        "tk_sinifi": _sayim(h.get("tk_sinifi") for h in H_g),
        "l4_bicimi": _sayim(h.get("l4_bicimi") for h in H_g),
        "kontrol_etiketi": _sayim(h.get("kontrol_etiketi") for h in H_g),
        "belirsiz_nedenleri": dict(sorted((a, dict(sorted(v.items()))) for a, v in nedenler.items())),
        "vaka_belirsiz_nedenleri": vaka_neden,
        "kararsiz_hucre_sayisi": vaka_neden.get("kararsiz_3_tekrar", 0),
        "B4_satir": {"n": len(b4), "medyan": medyan, "min": b4[0] if b4 else None, "max": b4[-1] if b4 else None},
        "devralanlar": [{"hedef_id": h["hedef_id"], "devraldigi_hedef": h["devraldigi_hedef"]}
                        for h in sorted(H_g, key=lambda x: x["hedef_id"]) if h["devralan"] == 1],
        "pilotlar": _ids(h for h in H_g if h["pilot"] == 1),
        "TK3": {"n_cift": sum(t3tab.values()), "tablo": t3tab,
                "not": "ÖK §2B.7: TK3 ayrı ve tanımlayıcı raporlanır (T2'ye girmez)"},
        "REF": [{"hedef_id": h["hedef_id"], "Y_L4": h["Y_L4"], "L_duzeyi": h["L_duzeyi"], "F_K": h["F_K"],
                 "F_T": h["F_T"], "D_soy": h["D_soy"]} for h in sorted(ref, key=lambda x: x["hedef_id"])],
    }


# ---------------------------------------------------------------------------------------------
# main function
# ---------------------------------------------------------------------------------------------
def _betik_ozetleri() -> dict:
    burasi = os.path.dirname(os.path.abspath(__file__))
    out = {}
    for yol in sorted(glob.glob(os.path.join(burasi, "*.py"))):
        with open(yol, "rb") as f:
            out[os.path.basename(yol)] = hashlib.sha256(f.read()).hexdigest()
    return out


def _surumler() -> dict:
    s = {"c3istat": __version__, "python": platform.python_version()}
    for paket in ("numpy", "scipy", "statsmodels"):
        s[paket] = __import__(paket).__version__
    return s


def analiz_et(girdi: sema.Girdi) -> dict:
    k = Karsilastirici()
    H_n = [h for h in girdi.hedefler if h["tabaka"] in Y.TABAKALAR_N]
    ref = [h for h in girdi.hedefler if h["tabaka"] == "REF"]
    H_g = [h for h in H_n if h["adaptor_gecersiz"] != 1]
    uyarilar = []
    if len(H_n) != Y.N_BEKLENEN:
        uyarilar.append(f"n = {len(H_n)}; ÖK §2B.3 n = {Y.N_BEKLENEN} bekliyor (eşikler n_eff'ten Ek A kuralıyla "
                        "yeniden hesaplanır)")
    if girdi.veri_turu != "sentetik":
        uyarilar.append("veri_turu = olcum: bu çalıştırma yalnız dondurulmuş ön kayıttan SONRA geçerlidir (ÖK §10)")

    belirli = [(h["hedef_id"], h["Y_L4"]) for h in H_g if h["Y_L4"] is not None]
    T1 = _t1(belirli, k, "T1", "ÖK §3.7, §6.6 T1 (birincil, H6): tek yönlü (alt) kesin binom; Holm dışı; "
                               "eşikler Ek A kuralıyla n_eff'ten")
    dus = _t1_duyarliliklar(H_g, k, [h for h in H_n if h["adaptor_gecersiz"] == 1])

    t2_kapsam = [h for h in H_g if h.get("tk_sinifi") in Y.T2_TK_KAPSAMI and h["F_K"] is not None
                 and h["F_T"] is not None]
    T2 = _t2(t2_kapsam, k, "T2", False, "ÖK §6.6 T2, §2B.7: kesin McNemar (F_K, F_T), iki yönlü; yalnız TK1 + TK2; "
                                        "Holm (T2–T5)")
    T2d = _t2([h for h in t2_kapsam if h["devralan"] != 1], k, "T2.dus_devir", True,
              "ÖK §2B.9: devralan hedefler hariç T2; tanımlayıcı, Holm dışı")
    T2d["dislanan"] = _ids(h for h in t2_kapsam if h["devralan"] == 1)
    T3 = _t3(H_g, k)
    T4 = _t4(H_g, k)
    T5 = _t5(H_g, k)
    holm = _holm({"T2": T2, "T3": T3, "T4": T4, "T5": T5}, k)

    sonuc = {
        "arac": {"surumler": _surumler(), "betik_sha256": _betik_ozetleri()},
        "girdi": {"sema_surumu": girdi.sema_surumu, "veri_turu": girdi.veri_turu, "aciklama": girdi.aciklama,
                  "kaynak": girdi.kaynak, "hedef_kaydi": len(girdi.hedefler), "vaka_kaydi": len(girdi.vakalar)},
        "yapilandirma": Y.ozet(),
        "orneklem": {
            "n": len(H_n), "n_beklenen": Y.N_BEKLENEN, "uyarilar": uyarilar,
            "adaptor_gecersiz": [{"hedef_id": h["hedef_id"], "gerekce": h["adaptor_gecersiz_gerekce"]}
                                 for h in sorted(H_n, key=lambda x: x["hedef_id"]) if h["adaptor_gecersiz"] == 1],
            "ref_hedefler": _ids(ref),
            "Y_L4_belirsiz": _ids(h for h in H_g if h["Y_L4"] is None),
            "n_eff": len(belirli),
        },
        "T1": T1,
        "T1_duyarlilik": dus,
        "H6_hukmu": h6_hukmu(T1, dus["i_belirsiz_1"], dus["ii_belirsiz_0"]),
        "betimleyici_testler": {"testler": ["T2", "T2_devralan_haric", "T3", "T4", "T5", "holm"],
                                "not": "Değişiklik 11 (01.10.2026): T2–T5 betimleyicidir; çıkarımsal iddia yapılmaz, "
                                       "Holm ailesi raporlanır ama karar için kullanılmaz"},
        "T2": T2,
        "T2_devralan_haric": T2d,
        "TK3_tanimlayici": None,
        "T3": T3,
        "T4": T4,
        "T5": T5,
        "holm": holm,
        "wilson": _wilson_tablolari(H_g, k),
        "bootstrap": _bootstrap(H_g, girdi.vakalar, k),
    }
    sonuc["tanimlayici"] = _tanimlayici(H_n, H_g, ref, girdi.vakalar)
    sonuc["TK3_tanimlayici"] = sonuc["tanimlayici"]["TK3"]
    oz = k.ozet()
    sonuc["iki_uygulama"] = {"karsilastirma": oz["toplam"], "uyumlu": oz["uyumlu"], "sinirda": oz["sinirda"],
                             "hata": oz["hata"], "en_buyuk_sapma": oz["en_buyuk_sapma"],
                             "uyusmazliklar": oz["uyusmazliklar"], "sinir_kayitlari": oz["sinir_kayitlari"],
                             "gecerli": oz["hata"] == 0}
    sonuc["_karsilastirma_kayitlari"] = k.kayitlar
    return sonuc


# ---------------------------------------------------------------------------------------------
# file outputs
# ---------------------------------------------------------------------------------------------
def _json_temiz(x):
    """Strict JSON: NaN/∞ -> string; Fraction -> string."""
    if isinstance(x, float):
        if math.isnan(x):
            return "nan"
        if math.isinf(x):
            return "inf" if x > 0 else "-inf"
        return x
    if isinstance(x, Fraction):
        return str(x)
    if isinstance(x, dict):
        return {str(kk): _json_temiz(v) for kk, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_json_temiz(v) for v in x]
    return x


def json_yaz(yol: str, veri) -> None:
    with open(yol, "w", encoding="utf-8", newline="\n") as f:
        json.dump(_json_temiz(veri), f, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
        f.write("\n")


def calistir(girdi_yolu: str, cikti_dizini: str, vakalar_yolu: str | None = None) -> int:
    """Exit codes: 0 = ok; 2 = the two implementations disagree (analysis invalid); 3 = input could not be validated."""
    from . import rapor

    os.makedirs(cikti_dizini, exist_ok=True)
    try:
        girdi = sema.yukle(girdi_yolu, vakalar_yolu)
    except sema.GirdiHatasi as e:
        json_yaz(os.path.join(cikti_dizini, "dogrulama_hatalari.json"), {"hatalar": e.mesajlar})
        print(f"GIRDI DOGRULANAMADI ({len(e.mesajlar)} hata): {e.mesajlar[:5]}")
        return 3
    sonuc = analiz_et(girdi)
    kayitlar = sonuc.pop("_karsilastirma_kayitlari")
    json_yaz(os.path.join(cikti_dizini, "sonuc.json"), sonuc)
    json_yaz(os.path.join(cikti_dizini, "karsilastirma.json"), {"ozet": sonuc["iki_uygulama"], "kayitlar": kayitlar})
    with open(os.path.join(cikti_dizini, "sonuc.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(rapor.markdown(sonuc))
    iu = sonuc["iki_uygulama"]
    print(f"H6: {sonuc['H6_hukmu']['hukum']} | n_eff={sonuc['T1']['n_eff']} X={sonuc['T1']['X']} "
          f"c={sonuc['T1']['c']} u={sonuc['T1']['u']} | iki uygulama {iu['uyumlu'] + iu['sinirda']}/{iu['karsilastirma']}"
          f" (hata {iu['hata']})")
    return 0 if iu["gecerli"] else 2
