# -*- coding: utf-8 -*-
"""Teknik kapının örneklem seçimi (ÖK §2F madde 2; yürütücü; 25.09.2026).

Kullanım: python teknik_kapi_secim.py <cerceve.jsonl> <kesif_2x2.jsonl> <cikti.json>

Kural (ön kayıtlı):
  * Çerçeve: ÖK §4.18 çerçevesi (birincil yapılandırma; asgari ve bir-eksik kümeler). Dosya seçimden
    önce SHA-256 ile sabitlenir; özet çıktıya yazılır.
  * Katmanlar: hedef {G1,G2,G3,G4,tümü} × tür {asgari, bir-eksik}. Her dolu katmandan 1 örnek; toplam 10.
    Dolu katman sayısı < 10 ise eksik kalan örnekler bütün çerçeveden tamamlanır; > 10 olamaz (5×2).
  * Tohum 20260926 (ÖK Ek C). Rastgelelik yerine SHA-256 sıralaması kullanılır: bir satırın anahtarı
    sha256("20260926|<bağlam>|<satır_kimliği>"); katmanda en küçük anahtarlı satır seçilir. Bu, Python
    sürümünden bağımsız ve elle denetlenebilir bir belirlenimci seçimdir.
  * Ek zorunlu örnek (kapı sayımına GİRMEZ): keşifsel ızgaradan ca_baglama=ad, ayni_ad_klasik_ca=var
    satırlarından en küçük sha256("20260926|kesif|<kimlik>") anahtarlı satır.
Beklenen satır alanları: "kimlik" (ya da "id"), "hedef", "tur"; keşif dosyasında ayrıca "ca_baglama",
"ayni_ad_klasik_ca". Alan adları farklıysa betik hata verir; sessizce tahmin etmez.
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
    def alan(r, ad):  # alan satırın üst düzeyinde ya da "hucre" nesnesinin içinde olabilir (SEMA.md)
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
