# -*- coding: utf-8 -*-
"""
Recomputes and checks the SHA-256 digests and the sizes in MANIFEST.csv.

Checked (for every row):
  1) does kaynak/<file> exist; SHA-256 == sha256_orijinal; size in bytes == boyut_bayt
  2) does metin/<id>.txt exist; SHA-256 == sha256_metin; can it be decoded as UTF-8
The file name mapping is taken from korpus_kaynaklari.json. No network access.

Usage: python korpus_dogrula.py  -> writes korpus_dogrulama.txt; exit code 1 if there is an error.
"""
import csv
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blok in iter(lambda: f.read(1 << 16), b""):
            h.update(blok)
    return h.hexdigest()


def main() -> int:
    tanim = {b["id"]: b for b in json.loads((KOK / "korpus_kaynaklari.json").read_text(encoding="utf-8"))["belgeler"]}
    satirlar = list(csv.DictReader(open(KOK / "MANIFEST.csv", encoding="utf-8", newline="")))
    sonuc, hata = [], 0
    for s in satirlar:
        i = s["id"]
        if not s["sha256_orijinal"]:
            sonuc.append(f"{i:<11} ERISILEMEDI (MANIFEST'te ozet yok) -> atlandi")
            continue
        orj = KOK / "kaynak" / tanim[i]["dosya"]
        met = KOK / "metin" / f"{i}.txt"
        durum = []
        if not orj.exists():
            durum.append("orijinal YOK")
        else:
            if sha256(orj) != s["sha256_orijinal"]:
                durum.append("orijinal OZET UYUSMAZ")
            if str(orj.stat().st_size) != s["boyut_bayt"]:
                durum.append("boyut UYUSMAZ")
        if not met.exists():
            durum.append("metin YOK")
        else:
            if sha256(met) != s["sha256_metin"]:
                durum.append("metin OZET UYUSMAZ")
            try:
                met.read_bytes().decode("utf-8")
            except UnicodeDecodeError:
                durum.append("metin UTF-8 DEGIL")
        if durum:
            hata += 1
            sonuc.append(f"{i:<11} HATA: {'; '.join(durum)}")
        else:
            sonuc.append(f"{i:<11} OK  {s['sha256_orijinal'][:16]}…  metin {s['sha256_metin'][:16]}…  {s['boyut_bayt']} B")
    zaman = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rapor = [f"Korpus dogrulama (korpus_dogrula.py) — {zaman}",
             f"MANIFEST satiri: {len(satirlar)}; hatali: {hata}; dogrulanan: {len(satirlar) - hata}/{len(satirlar)}",
             ""] + sonuc
    (KOK / "korpus_dogrulama.txt").write_text("\n".join(rapor) + "\n", encoding="utf-8")
    print("\n".join(rapor[:2]))
    return 1 if hata else 0


if __name__ == "__main__":
    sys.exit(main())
