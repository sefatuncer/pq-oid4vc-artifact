#!/usr/bin/env python3
"""Step 9 task 4a — effect of version pinning (information; not a behaviour measurement):
For targets whose ML-DSA / composite support is 'evet' (yes) or 'kısmi' (partial) in the inventory, does the evidence file (GitHub link with
the HEAD commit) exist at the commit of the release tag, and does it contain the ML-DSA/composite pattern? Anonymous raw.githubusercontent.com.
Output: kayit/surum_dayanak.csv"""
import csv, pathlib, re, urllib.request
K = pathlib.Path(__file__).resolve().parents[1]
ENV = K.parents[0] / "inventory"
cer = {r["id"]: r for r in csv.DictReader(open(ENV / "CERCEVE.csv", encoding="utf-8"))}
hed = {r["id"]: r for r in csv.DictReader(open(K / "kayit/hedef_listesi.csv", encoding="utf-8"))}
etk = {r["id"]: r for r in csv.DictReader(open(K / "kayit/surum_commit.csv", encoding="utf-8"))}
DESEN = {"ml_dsa_rfc9964": r"ML[-_]?DSA|MLDSA|\bAKP\b|Dilithium|dilithium",
         "composite_destegi": r"ML-?DSA-?(44|65|87)-(ES256|ES384|Ed25519|Ed448|RS256|PS256)|MLDSA(44|65|87)[-_]?(ES256|ES384|Ed25519|Ed448)|pq-composite|composite[-_ ]sig"}
def getir(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "pq-a09-ortam"}), timeout=30) as r:
            return r.status, r.read().decode("utf-8", "ignore")
    except Exception as e:
        return getattr(e, "code", 0) or 0, ""
satirlar = []
for i, h in hed.items():
    c = cer[i]
    for sutun, desen in DESEN.items():
        if c[sutun] not in ("evet", "kısmi"):
            continue
        tag_commit = etk.get(i, {}).get("etiket_commit", "")
        for d in re.findall(r"https://github\.com/[^\s;|]+", c[sutun + "_dayanak"]):
            m = re.match(r"https://github\.com/([^/]+/[^/]+)/blob/([0-9a-f]{40})/([^#]+)(#L(\d+)(-L(\d+))?)?", d)
            if not m:
                continue
            depo, head, yol = m.group(1), m.group(2), m.group(3)
            sonuc = dict(id=i, karar=h["karar"], sutun=sutun, envanter_degeri=c[sutun], dayanak=d, head_commit=head[:12],
                         surum=h["son_surum"], etiket_commit=tag_commit[:12], head_desen="", etiket_dosya="", etiket_desen="")
            s1, t1 = getir(f"https://raw.githubusercontent.com/{depo}/{head}/{yol}")
            sonuc["head_desen"] = str(len(re.findall(desen, t1))) if s1 == 200 else f"http {s1}"
            if tag_commit and tag_commit != head:
                s2, t2 = getir(f"https://raw.githubusercontent.com/{depo}/{tag_commit}/{yol}")
                sonuc["etiket_dosya"] = "var" if s2 == 200 else f"yok (http {s2})"
                sonuc["etiket_desen"] = str(len(re.findall(desen, t2))) if s2 == 200 else "0"
            elif tag_commit == head:
                sonuc["etiket_dosya"] = "etiket=HEAD"; sonuc["etiket_desen"] = sonuc["head_desen"]
            else:
                sonuc["etiket_dosya"] = "sürüm yok (commit sabit)"
            satirlar.append(sonuc)
            break   # the first evidence per column is enough
with open(K / "kayit/surum_dayanak.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(satirlar[0].keys())); w.writeheader(); w.writerows(satirlar)
for s in satirlar:
    print(s["id"], s["karar"], s["sutun"][:9], s["envanter_degeri"], "| HEAD", s["head_commit"], "desen", s["head_desen"],
          "| sürüm", s["surum"], s["etiket_commit"], "dosya", s["etiket_dosya"], "desen", s["etiket_desen"])
