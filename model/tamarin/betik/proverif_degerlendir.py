#!/usr/bin/env python3
# =====================================================================
#  PQ-OID4VC | Adım 5A | ProVerif ↔ Tamarin karşılaştırması (yalnız standart kitaplık)
# =====================================================================
#  Girdi : sonuc/proverif/ozet.csv (ProVerif sorgu sonuçları), sonuc/ozet.csv (Tamarin)
#  Çıktı : sonuc/proverif/karsilastirma.csv, sonuc/proverif/metrikler.txt
#  Eşleme:
#    reach (not event(E); Tamarin exists-trace):  ProVerif false -> verified, true -> falsified
#    corr  (karşılıklılık; Tamarin all-traces):    ProVerif true  -> verified, false -> falsified
#    neg   (not event(E); Tamarin all-traces):     ProVerif true  -> verified, false -> falsified
#    cannot_be_proved / timeout / yok -> "bilinmiyor" (kesin değil; uyum oranına girmez)
import csv

pv = list(csv.DictReader(open("sonuc/proverif/ozet.csv", encoding="utf-8")))
ta = {(r["kural"], r["varyant"], r["lemma"]): r["sonuc"]
      for r in csv.DictReader(open("sonuc/ozet.csv", encoding="utf-8"))}


def hukum(tur, sonuc):
    if sonuc not in ("true", "false"):
        return "bilinmiyor"
    if tur == "reach":
        return "verified" if sonuc == "false" else "falsified"
    return "verified" if sonuc == "true" else "falsified"


rows = []
for r in pv:
    h = hukum(r["tur"], r["proverif_sonuc"])
    t = ta.get((r["kural"], r["varyant"], r["lemma"]), "yok")
    if h == "bilinmiyor":
        u = "BILINMIYOR"
    else:
        u = "EVET" if h == t else "HAYIR"
    rows.append(dict(kural=r["kural"], varyant=r["varyant"], lemma=r["lemma"], tur=r["tur"],
                     proverif_ham=r["proverif_sonuc"], proverif_hukum=h, tamarin=t, uyum=u,
                     sure_s=r["sure_s"], bellek_MiB=r["bellek_MiB"]))

with open("sonuc/proverif/karsilastirma.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)

guv = [r for r in rows if r["tur"] != "reach"]
san = [r for r in rows if r["tur"] == "reach"]
kesin = [r for r in guv if r["uyum"] != "BILINMIYOR"]
uyan = [r for r in kesin if r["uyum"] == "EVET"]
bil = [r for r in guv if r["uyum"] == "BILINMIYOR"]
L = ["PQ-OID4VC Adım 5A — ProVerif 2.05 ikinci görüş (betik/proverif_degerlendir.py çıktısı)", ""]
L.append("Model (varyant) sayısı: %d" % len({(r["kural"], r["varyant"]) for r in rows}))
L.append("Güvenlik sorgusu (lemma) sayısı: %d" % len(guv))
L.append("  kesin sonuç: %d ; 'cannot be proved' / bilinmiyor: %d" % (len(kesin), len(bil)))
L.append("  kesin sonuçlarda Tamarin ile uyum: %d/%d" % (len(uyan), len(kesin)))
for r in kesin:
    if r["uyum"] != "EVET":
        L.append("   UYUMSUZ: %s %s %s proverif=%s tamarin=%s" % (r["kural"], r["varyant"], r["lemma"], r["proverif_hukum"], r["tamarin"]))
for r in bil:
    L.append("   BİLİNMİYOR: %s %s %s (ProVerif: %s; Tamarin: %s)" % (r["kural"], r["varyant"], r["lemma"], r["proverif_ham"], r["tamarin"]))
L.append("Sağlık (executable ulaşılabilirliği) sorgusu: %d ; Tamarin ile uyum %d/%d ; bilinmiyor %d" %
         (len(san), sum(1 for r in san if r["uyum"] == "EVET"),
          sum(1 for r in san if r["uyum"] != "BILINMIYOR"), sum(1 for r in san if r["uyum"] == "BILINMIYOR")))
sure = [float(r["sure_s"]) for r in rows if r["sure_s"]]
mem = [float(r["bellek_MiB"]) for r in rows if r["bellek_MiB"] not in ("", "NA")]
if sure:
    L.append("ProVerif koşum süresi (model başına): en çok %.3f s; bellek tepesi en çok %.1f MiB" % (max(sure), max(mem) if mem else float("nan")))
txt = "\n".join(L) + "\n"
open("sonuc/proverif/metrikler.txt", "w", encoding="utf-8").write(txt)
print(txt)
