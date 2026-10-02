# -*- coding: utf-8 -*-
"""
Produces the numerical tables for SUMMARY.md from izlenebilirlik.csv (every number comes from the script).
Output: kapsama_tablolari.md
  T1: artefact x document group (number of rows)
  T2: artefact x channel (number of rows) and the row ids supporting each channel
  T3: distributions of category, keyword and target
  T4: list of documents per artefact
"""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

KOK = Path(__file__).resolve().parent
KORPUS = KOK.parent / "spec-corpus"
satirlar = list(csv.DictReader(open(KOK / "izlenebilirlik.csv", encoding="utf-8", newline="")))
grup = {b["id"]: b["grup"] for b in json.loads((KORPUS / "korpus_kaynaklari.json").read_text(encoding="utf-8"))["belgeler"]}

GRUP_SIRA = ["OIDF", "IETF-OAuth", "IETF-JOSE", "IETF-COSE", "IETF-PQUIP", "IETF-LAMPS", "ARF", "ETSI", "AB-rehber", "BCT", "Akademik"]
ART = sorted({r["artefakt"] for r in satirlar if r["artefakt"] != "genel"}) + ["genel"]
KANAL = ["aktarilan", "cekilen", "sabitlenmis", "belirsiz"]

out = []
out.append("<!-- ozet_tablolari.py tarafindan uretildi; elle degistirmeyin -->")
out.append(f"Toplam satır: **{len(satirlar)}**; belge sayısı (matriste geçen): **{len({r['belge_id'] for r in satirlar})}**\n")

# T1
out.append("### T1. Artefakt × belge grubu (satır sayısı)\n")
out.append("| Artefakt | " + " | ".join(GRUP_SIRA) + " | Toplam |")
out.append("|---" * (len(GRUP_SIRA) + 2) + "|")
for a in ART:
    c = Counter(grup[r["belge_id"]] for r in satirlar if r["artefakt"] == a)
    out.append(f"| {a} | " + " | ".join(str(c.get(g, 0)) if c.get(g, 0) else "·" for g in GRUP_SIRA) + f" | {sum(c.values())} |")
tot = Counter(grup[r["belge_id"]] for r in satirlar)
out.append("| **Toplam** | " + " | ".join(str(tot.get(g, 0)) for g in GRUP_SIRA) + f" | {len(satirlar)} |\n")

# T2
out.append("### T2. Artefakt × kanal (satır sayısı)\n")
out.append("| Artefakt | " + " | ".join(KANAL) + " |")
out.append("|---" * (len(KANAL) + 1) + "|")
for a in ART:
    c = Counter(r["kanal"] for r in satirlar if r["artefakt"] == a)
    out.append(f"| {a} | " + " | ".join(str(c.get(k, 0)) for k in KANAL) + " |")
out.append("")

out.append("### T2b. Kanal dayanak satırları (artefakt başına, kanal sınıfına göre id'ler)\n")
for a in ART:
    if a == "genel":
        continue
    d = defaultdict(list)
    for r in satirlar:
        if r["artefakt"] == a:
            d[r["kanal"]].append(r["id"])
    parca = [f"{k}: {', '.join(v)}" for k, v in d.items()]
    out.append(f"- **{a}** — " + " · ".join(parca))
out.append("")

# T3
out.append("### T3. Kategori / anahtar sözcük / hedef dağılımı\n")
kc = Counter(r["kategori"] for r in satirlar)
out.append("| Kategori | Satır |\n|---|---|")
for k, v in kc.most_common():
    out.append(f"| {k} | {v} |")
out.append("")
hc = Counter()
for r in satirlar:
    for h in r["hedef"].split(";"):
        hc[h.strip()] += 1
out.append("| Hedef | Satır |\n|---|---|")
for k in sorted(hc):
    out.append(f"| {k} | {hc[k]} |")
out.append("")


def ana(k: str) -> str:
    k = k.upper()
    for anahtar in ["MUST NOT", "SHALL NOT", "MUST", "SHALL", "REQUIRED", "SHOULD NOT", "SHOULD", "RECOMMENDED", "MAY", "OPTIONAL"]:
        if anahtar in k:
            return anahtar
    return "bilgi/diğer"


ac = Counter(ana(r["anahtar_sozcuk"]) for r in satirlar)
out.append("| Anahtar sözcük (baskın) | Satır |\n|---|---|")
for k, v in ac.most_common():
    out.append(f"| {k} | {v} |")
out.append("")

# T4
out.append("### T4. Artefakt başına kaynak belgeler\n")
for a in ART:
    b = Counter(r["belge_id"] for r in satirlar if r["artefakt"] == a)
    out.append(f"- **{a}** ({sum(b.values())}): " + ", ".join(f"{k}×{v}" for k, v in sorted(b.items())))
out.append("")

(KOK / "kapsama_tablolari.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out[:40]))
