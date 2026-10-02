"""Generates a sample SYNTHETIC input (NOT a real measurement): veri/ornek_n31_sentetik.json and its CSV equivalent.

- 31 targets (JOSE 18, SDJWT 8, COSE 5; layout of PR §2B.3) + 2 REF rows; identifiers S-… (no real library name).
- 1 invalid adapter, 2 Y_L4 undetermined, 2 pilots, 1 delegating target, a mix of TK1/TK2/TK3, 100 cases per target.
- Deterministic: random.Random(TEST_TOHUMU). This is a TEST seed; it is separate from the PR analysis seeds.
Usage: python ornek_veri_uret.py [cikti_dizini]
"""
from __future__ import annotations

import csv
import json
import os
import random
import sys

TEST_TOHUMU = 910010
BURASI = os.path.dirname(os.path.abspath(__file__))


def uret() -> dict:
    rng = random.Random(TEST_TOHUMU)
    hedefler = []
    sira = 0
    for tabaka, kota in (("JOSE", 18), ("SDJWT", 8), ("COSE", 5)):
        for i in range(1, kota + 1):
            sira += 1
            L = rng.choice([0, 1, 1, 2, 2, 2, 3, 3, 4, 5])
            fk = int(rng.random() < 0.15)
            ft = int(fk or rng.random() < 0.45)
            h = {
                "hedef_id": f"S-{tabaka}-{i:02d}", "tabaka": tabaka, "adaptor_gecersiz": 0,
                "adaptor_gecersiz_gerekce": None,
                "tk_sinifi": rng.choice(["TK1", "TK2", "TK2", "TK3", "TK3"]),
                "l4_bicimi": "L4m" if rng.random() < 0.3 else "L4c",
                "kontrol_etiketi": "Ed25519" if rng.random() < 0.1 else "EdDSA",
                "Y_L4": int(L >= 4), "L_duzeyi": L, "F_K": fk, "F_T": ft,
                "D_soy": int(rng.random() < 0.7),
                "B1": rng.choice(["red", "yok_sayma", "dogrulama_duser"]),
                "B2": int(rng.random() < 0.2), "B3": int(rng.random() < 0.5),
                "B4_ozel_kod": 0, "B4_satir": None,
                "B5": rng.choice(["en_az_biri_gecerli", "mevcut_tumu_gecerli", "gerekli_kume", "diger"]),
                "B6": int(tabaka == "JOSE" and rng.random() < 0.5),
                "surum_8725bis_sonrasi": int(rng.random() < 0.35), "son_surum_tarihi": None,
                "pilot": 0, "devralan": 0, "devraldigi_hedef": None, "belirsiz_nedenleri": {},
            }
            if h["Y_L4"] == 0 and rng.random() < 0.4:
                h["B4_ozel_kod"] = 1
                h["B4_satir"] = rng.randint(8, 60)
            if tabaka == "COSE":
                h["B2"] = None
                h["B3"] = None
                h["belirsiz_nedenleri"].update({"B2": "uygulanamaz", "B3": "uygulanamaz"})
            hedefler.append(h)
    hedefler[3].update({"adaptor_gecersiz": 1, "adaptor_gecersiz_gerekce": "SENTETİK: V+/V− iki düzeltmeden sonra geçmedi"})
    hedefler[5]["Y_L4"] = None
    hedefler[5]["belirsiz_nedenleri"]["Y_L4"] = "kanit_kurali"
    hedefler[20]["Y_L4"] = None
    hedefler[20]["belirsiz_nedenleri"]["Y_L4"] = "oracle_uyusmazligi"
    hedefler[0]["pilot"] = 1
    hedefler[19]["pilot"] = 1
    hedefler[22].update({"devralan": 1, "devraldigi_hedef": "S-JOSE-07"})
    hedefler[9]["son_surum_tarihi"] = "2026-09-02" if hedefler[9]["surum_8725bis_sonrasi"] else "2026-05-11"
    for r in (1, 2):
        hedefler.append({
            "hedef_id": f"S-REF-{r:02d}", "tabaka": "REF", "adaptor_gecersiz": 0, "adaptor_gecersiz_gerekce": None,
            "tk_sinifi": None, "l4_bicimi": None, "kontrol_etiketi": None, "Y_L4": 0, "L_duzeyi": 2, "F_K": 0,
            "F_T": 1, "D_soy": 1, "B1": "red", "B2": 0, "B3": 1, "B4_ozel_kod": 0, "B4_satir": None, "B5": "diger",
            "B6": 0, "surum_8725bis_sonrasi": 1, "son_surum_tarihi": None, "pilot": 0, "devralan": 0,
            "devraldigi_hedef": None, "belirsiz_nedenleri": {},
        })
    vakalar = []
    for h in hedefler:
        if h["tabaka"] == "REF" or h["adaptor_gecersiz"] == 1:
            continue
        hata_k = rng.choice([0.0, 0.02, 0.05, 0.1])
        hata_t = hata_k + rng.choice([0.0, 0.05, 0.15, 0.3])
        for j in range(100):
            kol = "K" if j < 30 else ("T" if j < 70 else "diger")
            olasilik = hata_k if kol == "K" else (hata_t if kol == "T" else 0.1)
            v = {"hedef_id": h["hedef_id"], "vaka_id": f"SV{j:03d}", "kol": kol,
                 "uyum": 0 if rng.random() < olasilik else 1, "belirsiz_neden": None}
            if rng.random() < 0.01:
                v["uyum"] = None
                v["belirsiz_neden"] = "kararsiz_3_tekrar"
            vakalar.append(v)
    return {"sema_surumu": "c3-istat-girdi/1.0", "veri_turu": "sentetik",
            "aciklama": "SENTETIK ornek (gercek olcum DEGIL); ornek_veri_uret.py, test tohumu 910010",
            "hedefler": hedefler, "vakalar": vakalar}


def main() -> None:
    cikti = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BURASI, "veri")
    os.makedirs(cikti, exist_ok=True)
    veri = uret()
    with open(os.path.join(cikti, "ornek_n31_sentetik.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(veri, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    alanlar = list(veri["hedefler"][0].keys())
    with open(os.path.join(cikti, "ornek_n31_sentetik_hedefler.csv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# sema_surumu=c3-istat-girdi/1.0; veri_turu=sentetik\n")
        w = csv.DictWriter(f, fieldnames=alanlar, lineterminator="\n")
        w.writeheader()
        for h in veri["hedefler"]:
            satir = {}
            for k in alanlar:
                v = h[k]
                if k == "belirsiz_nedenleri":
                    v = ";".join(f"{a}:{b}" for a, b in sorted(v.items()))
                satir[k] = "" if v is None else v
            w.writerow(satir)
    with open(os.path.join(cikti, "ornek_n31_sentetik_vakalar.csv"), "w", encoding="utf-8", newline="\n") as f:
        w = csv.DictWriter(f, fieldnames=["hedef_id", "vaka_id", "kol", "uyum", "belirsiz_neden"], lineterminator="\n")
        w.writeheader()
        for v in veri["vakalar"]:
            w.writerow({k: ("" if vv is None else vv) for k, vv in v.items()})
    print("yazildi:", cikti)


if __name__ == "__main__":
    main()
