#!/usr/bin/env python3
# =====================================================================
#  PQ-OID4VC | Step 4 + 5A | evaluation of the Tamarin results
# =====================================================================
#  Runs in the container (needs clingo):
#     docker run --rm -v "<models/tamarin>:/work" -w /work pq-a02-solver:1.0 python betik/degerlendir.py
#  Input : betik/varyantlar.tsv, sonuc/ozet.csv, sonuc/json/*.json, sonuc/ham/*.txt, modeller/datalog/*.lp
#  Output: sonuc/degerlendirme.csv   expected / observed / agreement per lemma
#          sonuc/datalog_uyum.csv    Datalog (clingo) prediction / Tamarin verdict per security lemma
#                                    (only the rules that have a Datalog counterpart: R1–R5)
#          sonuc/izler.csv           rules and broken keys in the traces found (from the JSON)
#          sonuc/varyant_ozeti.csv   one row per variant
#          sonuc/metrikler.txt       acceptance criteria, mutation score, longest run, memory peak,
#                                    well-formedness scan; Step 4 and Step 5A in separate sections
#  Expectation rule: for a lemma named in column 7 of varyantlar.tsv (lemma_beklenen) the value given there;
#  for the others the default: sanity, M_ and X_ lemmas verified; security lemmas
#  according to G_beklenen; S1_downgrade_trace verified if G_beklenen is F.
#  All numbers are values computed by this script from the tool outputs.
import csv
import glob
import json
import os
import re
import sys

import clingo

GRUPLAR = [("Adım 4 (R1–R5)", ["R1", "R2", "R3", "R4", "R5"]),
           ("Adım 5A (R6, R6h5, R7, R7h; R7hx keşif)", ["R6", "R6h5", "R7", "R7h", "R7hx"])]
HEDEF = {"G1_claims_unforgeability": "g1",
         "G2_presentation_unforgeability": "g2",
         "G5_no_classical_acceptance": "g5"}
BILGI = {"S1_downgrade_trace", "first_contact_downgrade"}


def tur(lemma):
    if lemma.startswith("executable") or lemma.startswith("attack_needs_crqc"):
        return "saglik"
    if lemma.startswith("M_"):
        return "mutasyon"
    if lemma.startswith("X_"):
        return "ek-sinir"
    if lemma in BILGI:
        return "bilgi"
    if lemma.startswith("G") or lemma == "no_rollback":
        return "guvenlik"
    return "bilinmeyen"


def beklenen(lemma, gbek, lmap):
    if lemma in lmap:
        return "verified" if lmap[lemma] == "V" else "falsified"
    t = tur(lemma)
    if t in ("saglik", "mutasyon", "ek-sinir"):
        return "verified"
    if lemma == "S1_downgrade_trace" and gbek in ("V", "F"):
        return "verified" if gbek == "F" else "falsified"
    if t == "guvenlik" and gbek in ("V", "F"):
        return "verified" if gbek == "V" else "falsified"
    return "?"


def oku_varyantlar():
    v, sira = {}, []
    with open("betik/varyantlar.tsv", encoding="utf-8") as f:
        for line in f:
            if not line.strip() or line.startswith("#"):
                continue
            p = line.rstrip("\n").split("\t")
            kural, varyant, rol, dosya, bayraklar, gbek = p[:6]
            lmap = {}
            if len(p) > 6 and p[6] not in ("", "-"):
                for kv in p[6].split(";"):
                    a, b = kv.split("=")
                    lmap[a.strip()] = b.strip()
            flags = [] if bayraklar == "-" else bayraklar.split(",")
            v[(kural, varyant)] = dict(rol=rol, dosya=dosya, flags=flags, gbek=gbek, lmap=lmap)
            sira.append((kural, varyant))
    return v, sira


def lp_yolu(dosya):
    return "modeller/datalog/" + dosya.replace(".spthy", ".lp")


def datalog(dosya, flags, sem="class"):
    ctl = clingo.Control(["--warn=none", "-c", "sem=%s" % sem, "0"])
    ctl.load("modeller/datalog/core.lp")
    ctl.load(lp_yolu(dosya))
    ctl.add("base", [], "".join("flag(%s)." % f.lower() for f in flags))
    ctl.ground([("base", [])])
    modeller = []
    ctl.solve(on_model=lambda m: modeller.append([str(s) for s in m.symbols(shown=True)]))
    if len(modeller) != 1:
        raise RuntimeError("%s %s: beklenmeyen model sayısı %d" % (dosya, flags, len(modeller)))
    atoms = modeller[0]
    ihlal = sorted(a[len("violated("):-1] for a in atoms if a.startswith("violated("))
    sahte = sorted(a[len("forgeable("):-1] for a in atoms if a.startswith("forgeable("))
    return ihlal, sahte


def model_kurallari(dosya):
    adlar = set()
    for line in open("modeller/" + dosya, encoding="utf-8"):
        m = re.match(r"^\s*rule\s+([A-Za-z0-9_]+)\s*:", line)
        if m:
            adlar.add(m.group(1))
    return adlar


def iz_kurallari(kural, varyant, lemma, dosya):
    p = "sonuc/json/%s__%s__%s.json" % (kural, varyant, lemma)
    if not os.path.exists(p) or os.path.getsize(p) == 0:
        return None
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception:
        return None
    protokol = model_kurallari(dosya)
    kurallar, kirilan = [], []
    for g in d.get("graphs", []):
        for n in g.get("jgNodes", []):
            lab = n.get("jgnLabel", "")
            if lab in protokol and lab not in kurallar:
                kurallar.append(lab)
            if lab.startswith("CRQC_") and lab not in kirilan:
                kirilan.append(lab)
    if not kurallar:
        return None
    return sorted(kurallar), sorted(kirilan)


def iyi_bicimlilik(kurallar):
    """Scan of sonuc/ham/*.txt: number of files per rule prefix, successful files and files with warnings."""
    toplam = basarili = uyarili = 0
    for p in glob.glob("sonuc/ham/*.txt"):
        k = os.path.basename(p).split("__")[0]
        if k not in kurallar:
            continue
        s = open(p, encoding="utf-8", errors="replace").read()
        toplam += 1
        if "All wellformedness checks were successful" in s:
            basarili += 1
        if "wellformedness check failed" in s:
            uyarili += 1
    return toplam, basarili, uyarili


def main():
    varyantlar, sira = oku_varyantlar()
    satirlar = list(csv.DictReader(open("sonuc/ozet.csv", encoding="utf-8")))
    if not satirlar:
        print("ozet.csv boş"); sys.exit(1)
    kosulan = {(r["kural"], r["varyant"]) for r in satirlar}
    sira = [x for x in sira if x in kosulan]

    # ---------- 1) expected / observed ----------
    deg = []
    for r in satirlar:
        m = varyantlar[(r["kural"], r["varyant"])]
        b = beklenen(r["lemma"], m["gbek"], m["lmap"])
        deg.append(dict(kural=r["kural"], varyant=r["varyant"], rol=m["rol"], lemma=r["lemma"],
                        tur=tur(r["lemma"]), beklenen=b, gozlenen=r["sonuc"],
                        uyum="EVET" if b == r["sonuc"] else "HAYIR"))
    with open("sonuc/degerlendirme.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(deg[0].keys()))
        w.writeheader(); w.writerows(deg)
    dmap = {(d["kural"], d["varyant"], d["lemma"]): d for d in deg}

    # ---------- 2) Datalog (clingo) agreement: only the rules with a .lp counterpart ----------
    du, naive_farklar = [], []
    for (k, v) in sira:
        m = varyantlar[(k, v)]
        if not os.path.exists(lp_yolu(m["dosya"])):
            continue
        ihlal, sahte = datalog(m["dosya"], m["flags"])
        ihlal_naive, _ = datalog(m["dosya"], m["flags"], sem="naive")
        for r in satirlar:
            if (r["kural"], r["varyant"]) != (k, v) or r["lemma"] not in HEDEF:
                continue
            h = HEDEF[r["lemma"]]
            tahmin = "falsified" if h in ihlal else "verified"
            tahmin_n = "falsified" if h in ihlal_naive else "verified"
            du.append(dict(kural=k, varyant=v, rol=m["rol"], bayraklar="+".join(m["flags"]) or "-",
                           hedef=h, datalog_ihlal=("evet" if h in ihlal else "hayir"),
                           datalog_forgeable=" ".join(sahte) or "-",
                           datalog_tahmini=tahmin, tamarin=r["sonuc"],
                           uyum="EVET" if tahmin == r["sonuc"] else "HAYIR",
                           naive_tahmin=tahmin_n,
                           naive_uyum="EVET" if tahmin_n == r["sonuc"] else "HAYIR"))
            if tahmin_n != r["sonuc"]:
                naive_farklar.append("%s %s %s: naive=%s tamarin=%s" % (k, v, h, tahmin_n, r["sonuc"]))
    if du:
        with open("sonuc/datalog_uyum.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(du[0].keys()))
            w.writeheader(); w.writerows(du)

    # ---------- 3) trace contents ----------
    iz = []
    for r in satirlar:
        t = tur(r["lemma"])
        izli = (t == "guvenlik" and r["sonuc"] == "falsified") or \
               (t in ("mutasyon", "ek-sinir", "bilgi") and r["sonuc"] == "verified")
        if not izli:
            continue
        x = iz_kurallari(r["kural"], r["varyant"], r["lemma"], varyantlar[(r["kural"], r["varyant"])]["dosya"])
        iz.append(dict(kural=r["kural"], varyant=r["varyant"], lemma=r["lemma"],
                       kirilan=("(json yok)" if x is None else (" ".join(x[1]) or "-")),
                       kurallar=("(json yok)" if x is None else " ".join(x[0]))))
    if iz:
        with open("sonuc/izler.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(iz[0].keys()))
            w.writeheader(); w.writerows(iz)

    # ---------- 4) variant summary ----------
    ozet = []
    for (k, v) in sira:
        m = varyantlar[(k, v)]
        rs = [r for r in satirlar if (r["kural"], r["varyant"]) == (k, v)]
        ds = [dmap[(k, v, r["lemma"])] for r in rs]
        g = {r["lemma"]: r["sonuc"] for r in rs if tur(r["lemma"]) == "guvenlik"}
        mut = {r["lemma"]: r["sonuc"] for r in rs if tur(r["lemma"]) in ("mutasyon", "ek-sinir", "bilgi")}
        sag = {r["lemma"]: r["sonuc"] for r in rs if tur(r["lemma"]) == "saglik"}
        ozet.append(dict(kural=k, varyant=v, rol=m["rol"], bayraklar="+".join(m["flags"]) or "-",
                         G_beklenen=m["gbek"],
                         guvenlik=" ".join("%s=%s" % (a, b) for a, b in g.items()),
                         mutasyon_ek=" ".join("%s=%s" % (a, b) for a, b in mut.items()) or "-",
                         saglik_verified="%d/%d" % (sum(1 for b in sag.values() if b == "verified"), len(sag)),
                         lemma_sayisi=len(rs),
                         max_sure_s=max(float(r["sure_s"]) for r in rs),
                         max_bellek_MiB=max(float(r["bellek_MiB"]) for r in rs),
                         merdiven_max=max(int(r["merdiven_basamagi"]) for r in rs),
                         hepsi_beklenen_gibi="EVET" if all(d["uyum"] == "EVET" for d in ds) else "HAYIR"))
    with open("sonuc/varyant_ozeti.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(ozet[0].keys()))
        w.writeheader(); w.writerows(ozet)

    # ---------- 5) metrics (per group) ----------
    L = ["PQ-OID4VC Adım 4 + 5A — Tamarin kural şemaları: metrikler (betik/degerlendir.py çıktısı)",
         "clingo %s" % clingo.__version__, ""]
    for ad, kurallar in GRUPLAR:
        gs = [x for x in sira if x[0] in kurallar]
        if not gs:
            continue
        gr = [r for r in satirlar if r["kural"] in kurallar]
        gd = [d for d in deg if d["kural"] in kurallar]
        L.append("=" * 78)
        L.append(ad)
        L.append("=" * 78)
        L.append("Varyant sayısı: %d ; lemma koşumu (satır): %d" % (len(gs), len(gr)))
        uyumsuz = [d for d in gd if d["uyum"] != "EVET"]
        L.append("Beklenen/gözlenen uyumu: %d/%d" % (len(gd) - len(uyumsuz), len(gd)))
        for d in uyumsuz:
            L.append("   UYUMSUZ: %s %s %s beklenen=%s gozlenen=%s" % (d["kural"], d["varyant"], d["lemma"], d["beklenen"], d["gozlenen"]))
        # acceptance criterion: in the protected and mutant variants all lemmas as expected + executable verified
        L.append("")
        L.append("Kabul ölçütü (korumalı ve mutant varyantlarda bütün lemmalar beklenen gibi; executable verified):")
        for k in kurallar:
            ks = [x for x in gs if x[0] == k]
            if not ks:
                continue
            ok = True
            for x in ks:
                rol = varyantlar[x]["rol"]
                if not (rol == "korumali" or rol.startswith("mutant")):
                    continue
                xd = [d for d in gd if (d["kural"], d["varyant"]) == x]
                ok = ok and all(d["uyum"] == "EVET" for d in xd)
                ok = ok and any(d["lemma"] == "executable" and d["gozlenen"] == "verified" for d in xd)
            ek = [d for d in gd if d["kural"] == k and not (varyantlar[(k, d["varyant"])]["rol"] == "korumali"
                                                                or varyantlar[(k, d["varyant"])]["rol"].startswith("mutant"))]
            L.append("   %s: %s   (ek varyant lemmaları beklenen gibi: %d/%d)" %
                     (k, "GEÇTİ" if ok else "KALDI", sum(1 for d in ek if d["uyum"] == "EVET"), len(ek)))
        # mutation score
        L.append("")
        mutantlar = [x for x in gs if varyantlar[x]["rol"].startswith("mutant")]
        olduruldu = []
        for x in mutantlar:
            xd = [d for d in gd if (d["kural"], d["varyant"]) == x]
            g_bekF = [d for d in xd if d["tur"] == "guvenlik" and d["beklenen"] == "falsified"]
            m_bekV = [d for d in xd if d["tur"] == "mutasyon" and d["beklenen"] == "verified"]
            g_ok = len(g_bekF) > 0 and all(d["gozlenen"] == "falsified" for d in g_bekF)
            m_ok = len(m_bekV) > 0 and all(d["gozlenen"] == "verified" for d in m_bekV)
            olduruldu.append((x[0], x[1], varyantlar[x]["rol"], g_ok and m_ok, g_ok, m_ok))
        n_ol = sum(1 for o in olduruldu if o[3])
        L.append("Mutasyon skoru: %d/%d = %.0f%%  (öldürülme = F beklenen güvenlik lemmaları falsified VE V beklenen M_ lemmaları verified)"
                 % (n_ol, len(olduruldu), 100.0 * n_ol / max(1, len(olduruldu))))
        for k, v, rol, ok, g_ok, m_ok in olduruldu:
            L.append("   %-4s %-22s %-52s %s (G=%s, M=%s)" % (k, v, rol, "ÖLDÜ" if ok else "YAŞADI", g_ok, m_ok))
        # Datalog
        gdu = [d for d in du if d["kural"] in kurallar]
        L.append("")
        if gdu:
            L.append("Datalog (clingo, sem=class) ↔ Tamarin güvenlik hükmü uyumu: %d/%d" %
                     (sum(1 for d in gdu if d["uyum"] == "EVET"), len(gdu)))
            for d in gdu:
                if d["uyum"] != "EVET":
                    L.append("   UYUMSUZ: %s %s %s datalog=%s tamarin=%s" % (d["kural"], d["varyant"], d["hedef"], d["datalog_tahmini"], d["tamarin"]))
            nf = [x for x in naive_farklar if x.split()[0] in kurallar]
            L.append("Naif okuma (sem=naive: pq(L) yalnız gerçek ebeveyn) ile uyumsuzluklar: %d" % len(nf))
            for x in nf:
                L.append("   " + x)
        else:
            L.append("Datalog karşılaştırması: bu grupta .lp karşılığı yok (R6/R7 sayısal pencere ASP'de).")
        # source and well-formedness
        maxs = max(gr, key=lambda r: float(r["sure_s"]))
        maxm = max(gr, key=lambda r: float(r["bellek_MiB"]))
        kapanmayan = [r for r in gr if r["sonuc"] not in ("verified", "falsified")]
        merdivenli = [r for r in gr if int(r["merdiven_basamagi"]) > 1]
        L.append("")
        L.append("En uzun koşum: %s s (%s %s %s)" % (maxs["sure_s"], maxs["kural"], maxs["varyant"], maxs["lemma"]))
        L.append("En yüksek bellek: %s MiB (%s %s %s)" % (maxm["bellek_MiB"], maxm["kural"], maxm["varyant"], maxm["lemma"]))
        L.append("Merdivende 1'den yüksek basamak gereken koşum: %d" % len(merdivenli))
        for r in merdivenli:
            L.append("   %s %s %s basamak=%s sonuc=%s" % (r["kural"], r["varyant"], r["lemma"], r["merdiven_basamagi"], r["sonuc"]))
        L.append("Kapanmayan ya da geçersiz (verified/falsified dışı): %d" % len(kapanmayan))
        for r in kapanmayan:
            L.append("   %s %s %s sonuc=%s" % (r["kural"], r["varyant"], r["lemma"], r["sonuc"]))
        top, bas, uya = iyi_bicimlilik(kurallar)
        L.append("İyi biçimlilik taraması (sonuc/ham/*.txt): %d dosya; 'All wellformedness checks were successful' %d; uyarılı %d" % (top, bas, uya))
        L.append("")
    txt = "\n".join(L) + "\n"
    open("sonuc/metrikler.txt", "w", encoding="utf-8").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
