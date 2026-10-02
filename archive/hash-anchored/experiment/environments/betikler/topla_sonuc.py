#!/usr/bin/env python3
"""Adım 9 görev 4a — derleme-sonuc.csv'yi betikle üretir (elle sayı yazılmaz).
Girdiler: kayit/hedef_listesi.csv, kayit/surum_commit.csv, kayit/<id>.kosu.json(l), hedefler/<id>/cikti/sonuc.tsv,
          kayit/degisiklikler.csv (düşen -> yedek), kayit/notlar.csv (elle kurulum notları).
Sonuç değerleri: basarili / basarisiz / erisilemedi (henüz koşulmamış satır: bekliyor)."""
import csv, json, pathlib, sys
K = pathlib.Path(__file__).resolve().parents[1]
hedef = {r["id"]: r for r in csv.DictReader(open(K / "kayit/hedef_listesi.csv", encoding="utf-8"))}
etiket = {r["id"]: r for r in csv.DictReader(open(K / "kayit/surum_commit.csv", encoding="utf-8"))}
degis = list(csv.DictReader(open(K / "kayit/degisiklikler.csv", encoding="utf-8")))
notlar = {}
for r in csv.DictReader(open(K / "kayit/notlar.csv", encoding="utf-8")):
    notlar.setdefault(r["id"], []).append(r["not"])
yedek_yerine = {d["yedek_id"]: d["dusen_id"] for d in degis}

def tsv(i):
    p = K / "hedefler" / i / "cikti" / "sonuc.tsv"
    d = {}
    if p.exists():
        for s in p.read_text(encoding="utf-8").splitlines():
            if "\t" in s:
                a, b = s.split("\t", 1)
                d.setdefault(a, []).append(b)
    return {a: "; ".join(b) if a == "not" else b[-1] for a, b in d.items()}

def satir(i, yedek_mi):
    h = hedef[i]; e = etiket.get(i, {}); t = tsv(i)
    kos = K / "kayit" / f"{i}.kosu.json"
    kj = json.loads(kos.read_text(encoding="utf-8")) if kos.exists() else None
    denemeler = []
    kl = K / "kayit" / f"{i}.kosu.jsonl"
    if kl.exists():
        denemeler = [json.loads(x) for x in kl.read_text(encoding="utf-8").splitlines() if x.strip()]
    n = []
    # sürüm ve commit
    surum = t.get("kurulan_surum") or h["son_surum"] or ("git:" + h["son_commit_sha"][:12])
    commit, kaynak = t.get("commit", ""), t.get("commit_kaynagi", "")
    if not commit and e.get("etiket_commit"):
        commit, kaynak = e["etiket_commit"], f"git etiketi {e['etiket']}"
    if not commit and not h["son_surum"]:
        commit, kaynak = h["son_commit_sha"], "CERCEVE son_commit_sha (sürüm yok)"
    if commit:
        n.append(f"commit kaynağı: {kaynak}")
        if e.get("etiket_commit") and t.get("commit") and e["etiket_commit"] != t["commit"]:
            n.append(f"UYARI: kayıt commit'i git etiketinden farklı ({e['etiket']}={e['etiket_commit'][:12]})")
        if h["son_commit_sha"] and commit != h["son_commit_sha"]:
            n.append(f"çerçeve HEAD {h['son_commit_sha'][:12]} ≠ sürüm commit'i")
    if t.get("kilit_dosyasi"):
        n.append(f"kilit: {t['kilit_dosyasi']} sha256 {t.get('kilit_sha256','')[:16]}…")
    if t.get("bagimlilik_sayisi"):
        n.append(f"bağımlılık {t['bagimlilik_sayisi']}")
    if t.get("not"):
        n.append(t["not"])
    n += notlar.get(i, [])
    # sonuç
    if kj is None:
        sonuc = "bekliyor"
    elif t.get("sonuc") in ("erisilemedi", "basarisiz", "basarili"):
        sonuc = t["sonuc"]
    elif kj["cikis_kodu"] in (124, 137):
        sonuc = "basarisiz"; n.append("zaman aşımı")
    else:
        sonuc = "basarili" if (t.get("ice_aktar") == "basarili" and kj["cikis_kodu"] == 0) else "basarisiz"
    if len(denemeler) > 1:
        n.append(f"deneme {len(denemeler)}; toplam {sum(d['sure_s'] for d in denemeler)} s")
    return dict(id=i, ad=h["ad"], tabaka=h["tabaka"], dil_grubu=h["dil_grubu"], surum=surum, commit=commit,
                paket_ozeti=t.get("paket_ozeti", ""), imaj=(kj or {}).get("imaj", ""), sonuc=sonuc,
                sure_s=(kj or {}).get("sure_s", ""), **{"not": " | ".join(n)},
                yedek_mi="evet" if yedek_mi else "hayir", yerine_gectigi_id=yedek_yerine.get(i, ""))

rows = [satir(i, False) for i, h in hedef.items() if h["karar"] == "SECILDI"]
rows += [satir(i, True) for i in yedek_yerine]
alanlar = ["id", "ad", "tabaka", "dil_grubu", "surum", "commit", "paket_ozeti", "imaj", "sonuc", "sure_s", "not",
           "yedek_mi", "yerine_gectigi_id"]
gecici = K / "derleme-sonuc.csv.tmp"
with open(gecici, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=alanlar); w.writeheader(); w.writerows(rows)
gecici.replace(K / "derleme-sonuc.csv")
from collections import Counter
print(Counter(r["sonuc"] for r in rows if r["yedek_mi"] == "hayir"), "yedek:", len(yedek_yerine))
