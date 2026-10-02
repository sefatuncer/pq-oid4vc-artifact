#!/usr/bin/env python3
"""Step 9 task 4a — merges the target list (SECILDI + YEDEK, E2) with FRAME.csv and
re-derives the reserve type (5.3-4-i within the group / 5.3-4-ii general) with the secim() logic of collect.py.
Output: records/target_list.csv. Uses no network."""
import csv, json, pathlib
KOK = pathlib.Path(__file__).resolve().parents[3]          # project root
ENV = KOK / "experiment" / "inventory"
CIKTI = KOK / "experiment" / "environments" / "records" / "target_list.csv"
sec = list(csv.DictReader(open(ENV / "SELECTION.csv", encoding="utf-8")))
cer = {r["id"]: r for r in csv.DictReader(open(ENV / "FRAME.csv", encoding="utf-8"))}
kayit = json.load(open(ENV / "collect_record.json", encoding="utf-8"))["secim"]
kayit = kayit.get("E2", kayit)
grup = {r["id"]: r["dil_grubu"] for r in sec}
satirlar = []
for tabaka, s in kayit.items():
    secilen, yedek = s["secilen"], s["yedek"]
    secilen_gruplar = list(dict.fromkeys(grup[i] for i in secilen))
    # collect.py secim(): the reserve list first gets the within-group reserves in the order of the selected groups (5.3-4-i),
    # then the first 2 unselected eligible candidates of the general order (5.3-4-ii). Parsed by an ordered walk.
    tur, kullanilan, konum, genel_kip = {}, set(), 0, False
    for i in yedek:
        g = grup[i]
        if (not genel_kip and tabaka != "REF" and g in secilen_gruplar[konum:] and g not in kullanilan):
            konum = secilen_gruplar.index(g) + 1
            kullanilan.add(g)
            tur[i] = ("i", g)
        else:
            genel_kip = True
            tur[i] = ("ii", "genel")
    for sira, i in enumerate(secilen, 1):
        c = cer[i]
        satirlar.append(dict(id=i, tabaka=tabaka, karar="SECILDI", sira=sira, yedek_turu="", yedek_grubu="",
                             ad=c["ad"], dil=c["dil"], dil_grubu=grup[i], paket_ekosistemi=c["paket_ekosistemi"],
                             paket_adi=c["paket_adi"], depo_url=c["depo_url"], alt_dizin=c["alt_dizin"],
                             son_surum=c["son_surum"], son_surum_tarihi=c["son_surum_tarihi"],
                             son_commit_sha=c["son_commit_sha"], son_commit=c["son_commit"], lisans=c["lisans"]))
    for sira, i in enumerate(yedek, 1):
        c = cer[i]
        satirlar.append(dict(id=i, tabaka=tabaka, karar="YEDEK", sira=sira, yedek_turu=tur[i][0], yedek_grubu=tur[i][1],
                             ad=c["ad"], dil=c["dil"], dil_grubu=grup[i], paket_ekosistemi=c["paket_ekosistemi"],
                             paket_adi=c["paket_adi"], depo_url=c["depo_url"], alt_dizin=c["alt_dizin"],
                             son_surum=c["son_surum"], son_surum_tarihi=c["son_surum_tarihi"],
                             son_commit_sha=c["son_commit_sha"], son_commit=c["son_commit"], lisans=c["lisans"]))
# consistency check with karar_E2 of SELECTION.csv
e2 = {r["id"]: r["karar_E2"] for r in sec}
for r in satirlar:
    assert e2[r["id"]] == r["karar"], (r["id"], e2[r["id"]], r["karar"])
assert sum(1 for r in satirlar if r["karar"] == "SECILDI") == 34
assert sum(1 for r in satirlar if r["karar"] == "YEDEK") == 21
CIKTI.parent.mkdir(parents=True, exist_ok=True)
with open(CIKTI, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(satirlar[0].keys()))
    w.writeheader(); w.writerows(satirlar)
for r in satirlar:
    if r["karar"] == "YEDEK":
        print(r["tabaka"], r["id"], r["dil_grubu"], r["yedek_turu"], r["yedek_grubu"], r["ad"])
print("yazıldı:", CIKTI, len(satirlar))
