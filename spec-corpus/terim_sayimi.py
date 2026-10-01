# -*- coding: utf-8 -*-
"""
metin/ altindaki her belgede PQ ile ilgili terimlerin gecis sayisini sayar (buyuk/kucuk harf duyarsiz).
Cikti: terim_sayimi.csv (belge x terim) ve terim_sayimi.txt (ozet). Ag erisimi yoktur.
Terimler bilincli olarak kaba tutulmustur; 'quantum' sayimi 'post-quantum'u da kapsar.
"""
import csv
import re
from pathlib import Path

KOK = Path(__file__).resolve().parent
TERIMLER = {
    "quantum": r"quantum",
    "post-quantum": r"post[- ]?quantum",
    "PQC": r"\bPQC\b",
    "ML-DSA": r"ML-DSA",
    "SLH-DSA": r"SLH-DSA",
    "hybrid": r"hybrid",
    "composite": r"composite",
    "downgrade": r"downgrade",
    "stripping": r"stripping",
}

satirlar = []
for p in sorted((KOK / "metin").glob("*.txt")):
    t = p.read_text(encoding="utf-8")
    satir = {"belge_id": p.stem}
    for ad, desen in TERIMLER.items():
        satir[ad] = len(re.findall(desen, t, flags=re.IGNORECASE))
    satirlar.append(satir)

with open(KOK / "terim_sayimi.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["belge_id"] + list(TERIMLER))
    w.writeheader()
    w.writerows(satirlar)

arf = [s for s in satirlar if s["belge_id"].startswith("ARF-")]
ozet = ["Terim sayimi (terim_sayimi.py) — metin/ altindaki belgeler, buyuk/kucuk harf duyarsiz", ""]
ozet.append(f"ARF v3.0.0 ({len(arf)} dosya) toplam 'quantum': {sum(s['quantum'] for s in arf)}; "
            f"'ML-DSA': {sum(s['ML-DSA'] for s in arf)}; 'hybrid': {sum(s['hybrid'] for s in arf)}")
for b in ["OID4VCI", "OID4VP", "HAIP", "SDJWTVC", "SDJWTVC13", "RFC9901", "TSL", "ABCA", "RFC9449",
          "JWTBCP", "RFC8725", "TS119612", "TS119602", "TS119475", "TS119411-8", "TS119312"]:
    s = next((x for x in satirlar if x["belge_id"] == b), None)
    if s:
        ozet.append(f"{b:<11} " + "  ".join(f"{k}={s[k]}" for k in TERIMLER))
(KOK / "terim_sayimi.txt").write_text("\n".join(ozet) + "\n", encoding="utf-8")
print("\n".join(ozet))
