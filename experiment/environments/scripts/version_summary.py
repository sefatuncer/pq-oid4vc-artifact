#!/usr/bin/env python3
"""Summary of version pinning (information): installed commit ↔ frame HEAD (FRAME.csv son_commit_sha) for the n+REF (34) targets.
Input: build-results.csv, records/target_list.csv, records/version_basis.csv. Output: records/version_summary.csv + screen."""
import csv, pathlib
K = pathlib.Path(__file__).resolve().parents[1]
ds = {r["id"]: r for r in csv.DictReader(open(K / "build-results.csv", encoding="utf-8"))}
hl = {r["id"]: r for r in csv.DictReader(open(K / "records/target_list.csv", encoding="utf-8"))}
sd = list(csv.DictReader(open(K / "records/version_basis.csv", encoding="utf-8")))
satir = []
for i, h in hl.items():
    if h["karar"] != "SECILDI":
        continue
    d = ds[i]
    tur = "commit-sabit (sürüm yok)" if not h["son_surum"] else ("sürüm=HEAD" if d["commit"] == h["son_commit_sha"] else "sürüm≠HEAD")
    satir.append(dict(id=i, tabaka=h["tabaka"], son_surum=h["son_surum"], kurulan_commit=d["commit"][:12],
                      cerceve_head=h["son_commit_sha"][:12], durum=tur, head_tarihi=h["son_commit"], surum_tarihi=h["son_surum_tarihi"]))
with open(K / "records/version_summary.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(satir[0].keys())); w.writeheader(); w.writerows(satir)
from collections import Counter
print(Counter(s["durum"] for s in satir))
print("sürüm≠HEAD:", ", ".join(s["id"] for s in satir if s["durum"] == "sürüm≠HEAD"))
print("ML-DSA dayanağı sürümde yok:", [(r["id"], r["sutun"]) for r in sd if r["karar"] == "SECILDI" and r["etiket_desen"] == "0"])
