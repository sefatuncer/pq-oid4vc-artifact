# -*- coding: utf-8 -*-
"""
Checks that every `birebir_alinti` in izlenebilirlik.csv occurs VERBATIM in the file
spec-corpus/metin/<belge_id>.txt given by `belge_id`.

Normalisation (whitespace only):
  D1: every whitespace sequence (including line breaks, tabs, form feeds) is reduced to one space.
  D2: D1 + "-<space>" -> "-" for hyphenated words split at a line end (the same transformation
      in the text and in the quotation). Example: "SD-\\n   JWT" -> "SD-JWT" in an IETF text.
No other transformation (case, quotation marks, ligatures) is made.

Output: alinti_dogrulama.txt (n/N, D1/D2 distribution, quotations not found, length violations).
Usage: python alinti_dogrula.py   (from the traceability/ folder or from anywhere)
"""
import csv
import re
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent
METIN = KOK.parent / "spec-corpus" / "metin"
CSV = KOK / "izlenebilirlik.csv"
RAPOR = KOK / "alinti_dogrulama.txt"
AZAMI = 300


def d1(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def d2(s: str) -> str:
    return re.sub(r"-\s+", "-", d1(s))


def main() -> int:
    onbellek = {}
    satirlar = list(csv.DictReader(open(CSV, encoding="utf-8", newline="")))
    n_d1 = n_d2 = 0
    bulunamayan, uzun, eksik_belge = [], [], []
    for r in satirlar:
        b = r["belge_id"]
        if b not in onbellek:
            p = METIN / f"{b}.txt"
            if not p.exists():
                onbellek[b] = None
            else:
                t = p.read_text(encoding="utf-8")
                onbellek[b] = (d1(t), d2(t))
        if onbellek[b] is None:
            eksik_belge.append(r["id"])
            continue
        a = r["birebir_alinti"]
        if len(a) > AZAMI:
            uzun.append((r["id"], len(a)))
        t1, t2 = onbellek[b]
        if d1(a) in t1:
            n_d1 += 1
        elif d2(a) in t2:
            n_d2 += 1
        else:
            bulunamayan.append((r["id"], b, a[:120]))
    N = len(satirlar)
    n = n_d1 + n_d2
    with open(RAPOR, "w", encoding="utf-8", newline="\n") as f:
        f.write("Alinti dogrulama raporu (izlenebilirlik.csv -> spec-corpus/metin)\n")
        f.write(f"Toplam satir (N): {N}\n")
        f.write(f"Dogrulanan (n): {n}  ->  {n}/{N}\n")
        f.write(f"  D1 (yalniz bosluk daraltma) ile: {n_d1}\n")
        f.write(f"  D2 (D1 + satir sonu tire birlestirme) ile: {n_d2}\n")
        f.write(f"Bulunamayan: {len(bulunamayan)}\n")
        for i, b, a in bulunamayan:
            f.write(f"  - {i} [{b}] {a}\n")
        f.write(f"{AZAMI} karakteri asan alinti: {len(uzun)}\n")
        for i, L in uzun:
            f.write(f"  - {i}: {L} karakter\n")
        f.write(f"Metin dosyasi bulunamayan satir: {len(eksik_belge)} {eksik_belge}\n")
    print(RAPOR.read_text(encoding="utf-8"))
    return 0 if (n == N and not uzun and not eksik_belge) else 1


if __name__ == "__main__":
    sys.exit(main())
