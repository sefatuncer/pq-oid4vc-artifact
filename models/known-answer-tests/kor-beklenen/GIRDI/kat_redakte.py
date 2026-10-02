# Extracts the tables of the KAT-SPEC (d) sections in a form that contains no expected values (input of the blind N-version derivation).
import re, sys, io
yol = sys.argv[1]
satirlar = io.open(yol, encoding="utf-8").read().split("\n")
bolumler = []  # (heading, start, end)
basliklar = [(i, s) for i, s in enumerate(satirlar) if s.startswith("### (d)") or s.startswith("## ")]
for k, (i, s) in enumerate(basliklar):
    if s.startswith("### (d)"):
        son = basliklar[k+1][0] if k+1 < len(basliklar) else len(satirlar)
        # up to the next ### heading
        for j in range(i+1, son):
            if satirlar[j].startswith("### "):
                son = j; break
        bolumler.append((i, son))
DUSUR = re.compile(r"Beklenen|Dayanak|^\s*Not\s*$|accept strict|accept transitional|attack|violation|sonuç|Sonuç|hüküm|Hüküm", re.I)
cikti = []; atilan_sutunlar = {}
for (b, e) in bolumler:
    kat = next(s for s in reversed(satirlar[:b]) if s.startswith("## "))
    cikti.append(f"\n## {kat[3:]}\n")
    i = b
    while i < e:
        if satirlar[i].startswith("|"):
            tablo = []
            while i < e and satirlar[i].startswith("|"):
                tablo.append(satirlar[i]); i += 1
            hucreler = [[c.strip() for c in t.strip().strip("|").split("|")] for t in tablo]
            baslik = hucreler[0]
            tut = [k for k, h in enumerate(baslik) if not DUSUR.search(h) or h.startswith("Tamarin bayrakları")]
            for k, h in enumerate(baslik):
                if k not in tut:
                    degerler = sorted({r[k].replace("*","") for r in hucreler[2:] if k < len(r)})
                    atilan_sutunlar.setdefault(kat[3:40], []).append((h, degerler))
            for r_i, r in enumerate(hucreler):
                if r_i == 1:
                    cikti.append("|" + "|".join(["---"]*len(tut)) + "|"); continue
                yeni = []
                for k in tut:
                    c = r[k] if k < len(r) else ""
                    if "→" in c: c = c.split("→")[0].strip()
                    if r_i == 0 and "→" in baslik[k]: c = baslik[k].split("→")[0].strip()
                    yeni.append(c)
                cikti.append("| " + " | ".join(yeni) + " |")
            cikti.append("")
        else:
            i += 1
print("\n".join(cikti))
print("\n## Türetilecek (atılan) sütunlar ve olası değer kümeleri\n")
for kat, lst in atilan_sutunlar.items():
    for h, d in lst:
        if re.search(r"Dayanak|^\s*Not\s*$", h): continue
        print(f"- {kat} → **{h}**: olası değerler (sırasız küme, eşleme verilmez) = {{{', '.join(x for x in d if x)[:300]}}}")
