# -*- coding: utf-8 -*-
"""KAT N-version comparison: first work (KAT-SPEC (d) tables) ↔ blind work (BEKLENEN-KOR.tsv). Maintainers, 25.09.2026."""
import sys, io, re, csv
spec = io.open(sys.argv[1], encoding="utf-8").read().split("\n")
kor = list(csv.DictReader(io.open(sys.argv[2], encoding="utf-8"), delimiter="\t"))
A = {}
# KAT-1: "| Hücre | ASP sabitleri | Tamarin bayrakları | Beklenen ASP | Beklenen Tamarin (...) | Dayanak |" (table header of KAT-SPEC: cell, ASP constants, Tamarin flags, expected ASP, expected Tamarin, basis)
for s in spec:
    m = re.match(r"^\|\s*\**(K1-\d\d)\**\s*\|", s)
    if m:
        c = [x.strip().replace("*", "") for x in s.strip().strip("|").split("|")]
        A[(m.group(1), "ASP")] = c[3]; A[(m.group(1), "Tamarin:a_rrset_authentic")] = c[4]
# KAT-2a (merged rows expanded)
k2a = {"K2a-01": ("pqev=valid", "accept_classical"), "K2a-02": ("pqev=invalid", "accept_classical"),
       "K2a-03": ("pqev=valid", "accept_classical"), "K2a-04": ("pqev=invalid", "accept_classical"),
       "K2a-05": ("pqev=valid", "accept_classical"), "K2a-06": ("pqev=invalid", "accept_classical"),   # "aynı" (the same)
       "K2a-07": ("leafb=valid", "accept_classical"), "K2a-08": ("leafb=revoked", "accept_classical"),
       "K2a-09": ("pqev=valid", "accept_hybrid"), "K2a-10": ("pqev=invalid", "reject"), "K2a-11": ("pqev=absent", "accept_classical"),
       "K2a-12": ("pqev=valid", "accept_hybrid"), "K2a-13": ("pqev=invalid", "reject"), "K2a-14": ("pqev=absent", "reject"),
       "K2a-15": ("pqev=valid", "accept_hybrid"), "K2a-16": ("pqev=invalid", "reject"), "K2a-17": ("pqev=valid", "reject")}
for h, (k, v) in k2a.items(): A[(h, f"decision({k})")] = v
k2b = {"K2b-01": ("SALDIRI", "falsified"), "K2b-02": ("SALDIRI", "falsified"), "K2b-03": ("YOK", "verified"),
       "K2b-04": ("SALDIRI", None), "K2b-05": ("YOK", None), "K2b-06": ("YOK", "verified"),
       "K2b-07": ("SALDIRI", "falsified"), "K2b-08": ("YOK", None)}
for h, (a, t) in k2b.items():
    A[(h, "ASP")] = a
    if t: A[(h, "Tamarin:cert_authentic")] = t
for lb, (ig, rq) in {"revoked": ("accept_classical", "reject"), "expired": ("accept_classical", "reject"),
                     "unknown": ("accept_classical", "indeterminate"), "absent": ("accept_classical", "reject"),
                     "valid": ("accept_classical", "accept_hybrid")}.items():
    A[(f"K2c-{lb}", "karar(vb=ignore)")] = ig; A[(f"K2c-{lb}", "karar(vb=require)")] = rq
for h, (a, t) in {"K2d-01": ("accept_classical", "falsified"), "K2d-02": ("accept_classical", "falsified"),
                  "K2d-03": ("reject", "verified"), "K2d-04": ("reject", None), "K2d-05": ("accept_classical", None)}.items():
    A[(h, "ASP:karar")] = a
    if t: A[(h, "Tamarin")] = t
k3a = {"o1": ("pqc_protected", 1, 1), "o2": ("pqc_protected", 1, 1), "o3": ("classical_only", 0, 0), "o4": ("unsafe_mixed", 0, 0),
       "o5": ("hybrid_protected", 0, 1), "o6": ("unsafe_mixed", 0, 0), "o7": ("unknown", 0, 0), "o8": ("pqc_protected", 1, 1),
       "o9": ("invalid", 0, 0), "o10": ("unknown", 0, 0), "o11": ("hybrid_protected", 0, 1), "o12": ("classical_only", 0, 0)}
for h, (o, s, t) in k3a.items():
    A[(h, "out")] = o; A[(h, "accept_strict")] = str(s); A[(h, "accept_transitional")] = str(t)
for h, v in {"MIXED": "falsified", "PQ_ONLY": "verified", "HYBRID_KEM": "verified"}.items(): A[(h, "Tamarin:cek_secrecy")] = v
for h, (at, vi, tm) in {"V1": ("SALDIRI", 1, "falsified"), "V2": ("SALDIRI", 1, "falsified"), "V3": ("SALDIRI", 1, "falsified"),
                        "V4": ("YOK", 0, "verified"), "V5": ("YOK", 0, "verified"), "V6": ("SALDIRI", 1, "falsified")}.items():
    A[(h, "attack(qday=0)")] = at; A[(h, "violation(qday=0)")] = str(vi); A[(h, "attack(qday=200)")] = "YOK"; A[(h, "Tamarin:claims_unforgeability")] = tm
B = {(r["hucre"], r["turetilen_sutun"]): r["deger"] for r in kor}
anahtarlar = sorted(set(A) | set(B), key=lambda k: (k[0][:2], k[0], k[1]))
es = fark = yalnizA = yalnizB = bel = 0; satirlar = []
for k in anahtarlar:
    a, b = A.get(k), B.get(k)
    if a is None: yalnizB += 1; durum = "YALNIZ-KOR"
    elif b is None: yalnizA += 1; durum = "YALNIZ-ILK"
    elif b == "belirsiz": bel += 1; durum = "KOR-BELIRSIZ"
    elif a == b: es += 1; durum = "ESIT"
    else: fark += 1; durum = "FARKLI"
    satirlar.append((k[0], k[1], a, b, durum))
print(f"anahtar={len(anahtarlar)} ESIT={es} FARKLI={fark} KOR-BELIRSIZ={bel} YALNIZ-ILK={yalnizA} YALNIZ-KOR={yalnizB}")
for s in satirlar:
    if s[4] != "ESIT": print("  ", " | ".join(str(x) for x in s))
with io.open(sys.argv[3], "w", encoding="utf-8") as f:
    f.write("hucre\tsutun\tilk_ajan\tkor_ajan\tdurum\n")
    for s in satirlar: f.write("\t".join(str(x) for x in s) + "\n")
