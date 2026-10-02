# -*- coding: utf-8 -*-
"""Sample selection for the technical gate (PR §2F item 2; maintainers; 25.09.2026).

Usage: python teknik_kapi_secim.py <cerceve.jsonl> <kesif_2x2.jsonl> <output.json>

Rule (pre-registered):
  * Frame: the frame of PR §4.18 (primary configuration; minimal and one-less sets). The file is pinned with
    SHA-256 before the selection; the digest is written to the output.
  * Strata: goal {G1,G2,G3,G4,tümü} × kind {asgari, bir-eksik}. One sample from every filled stratum; 10 in total.
    If the number of filled strata is < 10, the missing samples are completed from the whole frame; > 10 is impossible (5×2).
  * Seed 20260926 (PR Appendix C). SHA-256 ordering is used instead of randomness: the key of a row is
    sha256("20260926|<context>|<row_id>"); in a stratum the row with the smallest key is selected. This is a
    deterministic selection that is independent of the Python version and can be checked by hand.
  * Additional mandatory sample (NOT counted for the gate): from the exploratory grid, among the rows with ca_baglama=ad,
    ayni_ad_klasik_ca=var, the row with the smallest key sha256("20260926|kesif|<id>").
Expected row fields: "kimlik" (or "id"), "hedef", "tur"; in the exploration file also "ca_baglama",
"ayni_ad_klasik_ca". If the field names differ, the script raises an error; it does not guess silently.
"""
import hashlib, io, json, sys

TOHUM = "20260926"
HEDEFLER = ["G1", "G2", "G3", "G4", "tümü"]
TURLER = ["asgari", "bir-eksik"]

def ozet(yol):
    h = hashlib.sha256()
    with open(yol, "rb") as f:
        for p in iter(lambda: f.read(1 << 20), b""):
            h.update(p)
    return h.hexdigest()

def oku(yol):
    satirlar = []
    with io.open(yol, encoding="utf-8") as f:
        for i, s in enumerate(f, 1):
            s = s.strip()
            if not s:
                continue
            r = json.loads(s)
            k = r.get("kimlik", r.get("id", r.get("satir_id")))
            if k is None:
                raise SystemExit(f"{yol}:{i}: 'kimlik', 'id' ya da 'satir_id' alanı yok")
            r["_kimlik"] = str(k)
            satirlar.append(r)
    kimlikler = [r["_kimlik"] for r in satirlar]
    if len(set(kimlikler)) != len(kimlikler):
        raise SystemExit(f"{yol}: yinelenen satır kimliği var")
    return satirlar

def anahtar(baglam, kimlik):
    return hashlib.sha256(f"{TOHUM}|{baglam}|{kimlik}".encode("utf-8")).hexdigest()

def normal_hedef(h):
    h = str(h)
    return "tümü" if h.lower() in ("tümü", "tumu", "tum", "all", "hepsi") else h.upper()

def normal_tur(t):
    t = str(t).lower().replace("_", "-")
    if t in ("asgari", "minimal", "min"):
        return "asgari"
    if t in ("bir-eksik", "birreksik", "eksik", "minus-one", "bir eksik"):
        return "bir-eksik"
    raise SystemExit(f"tanınmayan tür: {t!r}")

def main(cerceve, kesif, cikti):
    c = oku(cerceve)
    katman = {}
    for r in c:
        for alan in ("hedef", "tur"):
            if alan not in r:
                raise SystemExit(f"çerçevede '{alan}' alanı yok (satır {r['_kimlik']})")
        katman.setdefault((normal_hedef(r["hedef"]), normal_tur(r["tur"])), []).append(r)
    secilen, kayit = [], []
    for h in HEDEFLER:
        for t in TURLER:
            aday = katman.get((h, t), [])
            if not aday:
                kayit.append({"katman": f"{h}/{t}", "aday": 0, "secilen": None})
                continue
            en = min(aday, key=lambda r: anahtar(f"katman:{h}/{t}", r["_kimlik"]))
            secilen.append(en)
            kayit.append({"katman": f"{h}/{t}", "aday": len(aday), "secilen": en["_kimlik"]})
    if len(secilen) < 10:
        kalan = [r for r in c if r not in secilen]
        kalan.sort(key=lambda r: anahtar("tamamlama", r["_kimlik"]))
        ek = kalan[: 10 - len(secilen)]
        secilen += ek
        kayit.append({"tamamlama": [r["_kimlik"] for r in ek]})
    k = oku(kesif)
    def alan(r, ad):  # the field can be at the top level of the row or inside the "hucre" object (SCHEMA.md)
        return r.get(ad, (r.get("hucre") or {}).get(ad))
    adv = [r for r in k if str(alan(r, "ca_baglama")) == "ad" and str(alan(r, "ayni_ad_klasik_ca")) == "var"]
    if not adv:
        raise SystemExit("keşif dosyasında ca_baglama=ad, ayni_ad_klasik_ca=var satırı yok")
    kesif_secim = min(adv, key=lambda r: anahtar("kesif", r["_kimlik"]))
    sonuc = {
        "kural": "ÖK §2F madde 2 (çapa 6 = 998276a)",
        "tohum": TOHUM,
        "cerceve": {"yol": cerceve, "sha256": ozet(cerceve), "satir": len(c)},
        "kesif": {"yol": kesif, "sha256": ozet(kesif), "satir": len(k), "ad_var_satir": len(adv)},
        "katmanlar": kayit,
        "kapi_ornekleri": [{kk: v for kk, v in r.items() if kk != "_kimlik"} | {"kimlik": r["_kimlik"]} for r in secilen],
        "kesif_ornegi (kapı sayımına girmez)": {kk: v for kk, v in kesif_secim.items() if kk != "_kimlik"} | {"kimlik": kesif_secim["_kimlik"]},
    }
    with io.open(cikti, "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=2)
    print(json.dumps({"kapi_ornek_sayisi": len(secilen), "cerceve_sha256": sonuc["cerceve"]["sha256"],
                      "kesif_ornegi": kesif_secim["_kimlik"]}, ensure_ascii=False))

if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    main(*sys.argv[1:])
