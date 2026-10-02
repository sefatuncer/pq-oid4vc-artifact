"""Girdi şeması `c3-istat-girdi/1.0` (SEMA.md): JSON ya da CSV yükleme ve katı doğrulama.

Doğrulama başarısızsa `GirdiHatasi` (bütün mesajlarla) fırlatılır; analiz başlamaz.
"""
from __future__ import annotations

import csv
import datetime as _dt
import hashlib
import io
import json
import os
from dataclasses import dataclass, field

from .yapilandirma import BELIRSIZ_NEDENLERI, DIGER_NEDENLER, SEMA_SURUMU, T4_KESIM_TARIHI

UST_ALANLAR = {"sema_surumu", "veri_turu", "aciklama", "hedefler", "vakalar"}
VERI_TURLERI = ("sentetik", "olcum")

ENUM = {
    "tabaka": ("JOSE", "SDJWT", "COSE", "REF"),
    "tk_sinifi": ("TK1", "TK2", "TK3"),
    "l4_bicimi": ("L4m", "L4c"),
    "kontrol_etiketi": ("EdDSA", "Ed25519"),
    "B1": ("red", "yok_sayma", "dogrulama_duser"),
    "B5": ("en_az_biri_gecerli", "mevcut_tumu_gecerli", "gerekli_kume", "diger"),
}
# Ölçüm alanları: null olabilir (nedeniyle)
OLCUM_IKILI = ("Y_L4", "F_K", "F_T", "D_soy", "B2", "B3", "B4_ozel_kod", "B6", "surum_8725bis_sonrasi")
OLCUM_ENUM = ("B1", "B5")
OLCUM_ALANLARI = OLCUM_IKILI + OLCUM_ENUM + ("L_duzeyi",)
# Zorunlu, null olamayan ikili alanlar
ZORUNLU_IKILI = ("adaptor_gecersiz", "pilot", "devralan")
HEDEF_ALANLARI = {
    "hedef_id", "tabaka", "adaptor_gecersiz", "adaptor_gecersiz_gerekce", "tk_sinifi", "l4_bicimi",
    "kontrol_etiketi", "Y_L4", "L_duzeyi", "F_K", "F_T", "D_soy", "B1", "B2", "B3", "B4_ozel_kod", "B4_satir",
    "B5", "B6", "surum_8725bis_sonrasi", "son_surum_tarihi", "pilot", "devralan", "devraldigi_hedef",
    "belirsiz_nedenleri",
}
HEDEF_ZORUNLU = {"hedef_id", "tabaka", "adaptor_gecersiz", "Y_L4", "L_duzeyi", "F_K", "F_T", "D_soy", "B1", "B2",
                 "B3", "B4_ozel_kod", "B5", "B6", "surum_8725bis_sonrasi", "pilot", "devralan"}
HEDEF_ZORUNLU_N = {"tk_sinifi", "l4_bicimi"}          # REF dışındakiler için
VAKA_ALANLARI = {"hedef_id", "vaka_id", "kol", "uyum", "belirsiz_neden"}
KOLLAR = ("K", "T", "diger")
TUM_NEDENLER = BELIRSIZ_NEDENLERI + DIGER_NEDENLER


class GirdiHatasi(Exception):
    def __init__(self, mesajlar: list[str]):
        self.mesajlar = list(mesajlar)
        super().__init__("; ".join(self.mesajlar[:20]) + (" …" if len(self.mesajlar) > 20 else ""))


@dataclass
class Girdi:
    sema_surumu: str
    veri_turu: str
    aciklama: str
    hedefler: list[dict]
    vakalar: list[dict]
    kaynak: dict = field(default_factory=dict)   # {"dosya": ad, "sha256": …} (belirlenimci; mutlak yol yok)


# ---------------------------------------------------------------------------------------------
def _ikili(deger):
    """0/1/True/False -> 0/1; başka her şey None (geçersiz). bool, int'in alt türüdür; ikisi de kabul."""
    if isinstance(deger, bool):
        return int(deger)
    if isinstance(deger, int) and deger in (0, 1):
        return deger
    return None


def _dogrula_hedef(i: int, h: dict, hatalar: list[str]) -> dict:
    yer = f"hedefler[{i}]({h.get('hedef_id', '?')})"
    if not isinstance(h, dict):
        hatalar.append(f"{yer}: nesne değil")
        return {}
    for a in sorted(set(h) - HEDEF_ALANLARI):
        hatalar.append(f"{yer}: bilinmeyen alan '{a}'")
    zorunlu = set(HEDEF_ZORUNLU) | (HEDEF_ZORUNLU_N if h.get("tabaka") != "REF" else set())
    for a in sorted(zorunlu - set(h)):
        hatalar.append(f"{yer}: eksik zorunlu alan '{a}'")
    n = {k: h.get(k) for k in HEDEF_ALANLARI}
    n["belirsiz_nedenleri"] = dict(h.get("belirsiz_nedenleri") or {})

    if not isinstance(n["hedef_id"], str) or not n["hedef_id"]:
        hatalar.append(f"{yer}: hedef_id boş olmayan dize olmalı")
    for alan, secenekler in ENUM.items():
        v = n[alan]
        if alan in OLCUM_ENUM:
            if v is not None and v not in secenekler:
                hatalar.append(f"{yer}: {alan} tanımsız değer {v!r}")
        elif alan in ("tk_sinifi", "l4_bicimi", "kontrol_etiketi"):
            if v is None:
                continue  # zorunluluk yukarıda denetlendi (kontrol_etiketi isteğe bağlı)
            if v not in secenekler:
                hatalar.append(f"{yer}: {alan} tanımsız değer {v!r}")
        elif v not in secenekler:
            hatalar.append(f"{yer}: {alan} tanımsız değer {v!r}")
    for alan in ZORUNLU_IKILI:
        b = _ikili(n[alan])
        if b is None:
            hatalar.append(f"{yer}: {alan} 0/1 olmalı (null olamaz), bulunan {n[alan]!r}")
        n[alan] = b
    for alan in OLCUM_IKILI:
        if n[alan] is None:
            continue
        b = _ikili(n[alan])
        if b is None:
            hatalar.append(f"{yer}: {alan} 0/1 ya da null olmalı, bulunan {n[alan]!r}")
        n[alan] = b
    L = n["L_duzeyi"]
    if L is not None and (isinstance(L, bool) or not isinstance(L, int) or not 0 <= L <= 5):
        hatalar.append(f"{yer}: L_duzeyi 0…5 tamsayı ya da null olmalı, bulunan {L!r}")

    # null nedenleri
    nedenler = n["belirsiz_nedenleri"]
    for alan, neden in sorted(nedenler.items()):
        if alan not in OLCUM_ALANLARI:
            hatalar.append(f"{yer}: belirsiz_nedenleri bilinmeyen alan '{alan}'")
        elif n.get(alan) is not None:
            hatalar.append(f"{yer}: belirsiz_nedenleri '{alan}' için neden verilmiş ama değer null değil")
        if neden not in TUM_NEDENLER:
            hatalar.append(f"{yer}: belirsiz_nedenleri '{alan}' tanımsız neden {neden!r}")
        if neden == "olculmedi" and not (n["adaptor_gecersiz"] == 1 or n["tabaka"] == "REF"):
            hatalar.append(f"{yer}: '{alan}' için 'olculmedi' yalnız adaptor_gecersiz=1 ya da REF satırında kullanılır")
    for alan in OLCUM_ALANLARI:
        if n.get(alan) is None and alan not in nedenler:
            hatalar.append(f"{yer}: {alan} null ama belirsiz_nedenleri'nde nedeni yok")
    if n["Y_L4"] is None and nedenler.get("Y_L4") not in BELIRSIZ_NEDENLERI + ("olculmedi",):
        hatalar.append(f"{yer}: Y_L4 null ise nedeni ÖK §4.15 'belirsiz' nedenlerinden biri olmalı "
                       f"({', '.join(BELIRSIZ_NEDENLERI)}), bulunan {nedenler.get('Y_L4')!r}")

    # tutarlılık kuralları
    if n["tabaka"] != "REF" and n["adaptor_gecersiz"] == 0 and n.get("kontrol_etiketi") is None:
        hatalar.append(f"{yer}: kontrol_etiketi geçerli n hedeflerinde zorunlu (ÖK §2D-A.2, §2E.3: "
                       "kullanılan etiket hedef başına kaydedilir)")
    if n["adaptor_gecersiz"] == 1 and not n.get("adaptor_gecersiz_gerekce"):
        hatalar.append(f"{yer}: adaptor_gecersiz=1 ise adaptor_gecersiz_gerekce zorunlu")
    if n["devralan"] == 1 and not n.get("devraldigi_hedef"):
        hatalar.append(f"{yer}: devralan=1 ise devraldigi_hedef zorunlu")
    if n["devralan"] == 0 and n.get("devraldigi_hedef"):
        hatalar.append(f"{yer}: devralan=0 iken devraldigi_hedef verilmiş")
    b4, satir = n["B4_ozel_kod"], n["B4_satir"]
    if b4 == 1 and (isinstance(satir, bool) or not isinstance(satir, int) or satir < 1):
        hatalar.append(f"{yer}: B4_ozel_kod=1 ise B4_satir ≥ 1 tamsayı olmalı")
    if b4 != 1 and satir is not None:
        hatalar.append(f"{yer}: B4_satir yalnız B4_ozel_kod=1 iken verilir")
    tarih = n.get("son_surum_tarihi")
    if tarih is not None:
        try:
            t = _dt.date.fromisoformat(tarih)
            sonra = int(t > _dt.date.fromisoformat(T4_KESIM_TARIHI))
            if n["surum_8725bis_sonrasi"] is not None and n["surum_8725bis_sonrasi"] != sonra:
                hatalar.append(f"{yer}: son_surum_tarihi {tarih} ile surum_8725bis_sonrasi="
                               f"{n['surum_8725bis_sonrasi']} çelişiyor (sonra ⇔ tarih > {T4_KESIM_TARIHI})")
        except (TypeError, ValueError):
            hatalar.append(f"{yer}: son_surum_tarihi YYYY-MM-DD olmalı, bulunan {tarih!r}")
    return n


def _dogrula_vaka(i: int, v: dict, hedef_idleri: set, hatalar: list[str]) -> dict:
    yer = f"vakalar[{i}]"
    if not isinstance(v, dict):
        hatalar.append(f"{yer}: nesne değil")
        return {}
    for a in sorted(set(v) - VAKA_ALANLARI):
        hatalar.append(f"{yer}: bilinmeyen alan '{a}'")
    for a in sorted({"hedef_id", "vaka_id", "kol", "uyum"} - set(v)):
        hatalar.append(f"{yer}: eksik zorunlu alan '{a}'")
    n = {k: v.get(k) for k in VAKA_ALANLARI}
    if n["hedef_id"] not in hedef_idleri:
        hatalar.append(f"{yer}: hedef_id {n['hedef_id']!r} hedeflerde yok")
    if not isinstance(n["vaka_id"], str) or not n["vaka_id"]:
        hatalar.append(f"{yer}: vaka_id boş olmayan dize olmalı")
    if n["kol"] not in KOLLAR:
        hatalar.append(f"{yer}: kol tanımsız değer {n['kol']!r}")
    if n["uyum"] is None:
        if n["belirsiz_neden"] not in TUM_NEDENLER:
            hatalar.append(f"{yer}: uyum null ise belirsiz_neden zorunlu (tanımlı kod)")
    else:
        b = _ikili(n["uyum"])
        if b is None:
            hatalar.append(f"{yer}: uyum 0/1 ya da null olmalı, bulunan {n['uyum']!r}")
        n["uyum"] = b
        if n["belirsiz_neden"] is not None:
            hatalar.append(f"{yer}: uyum null değilken belirsiz_neden verilmiş")
    return n


def sozlukten(veri: dict, kaynak: dict | None = None) -> Girdi:
    hatalar: list[str] = []
    if not isinstance(veri, dict):
        raise GirdiHatasi(["üst düzey JSON nesnesi değil"])
    for a in sorted(set(veri) - UST_ALANLAR):
        hatalar.append(f"üst düzey: bilinmeyen alan '{a}'")
    if veri.get("sema_surumu") != SEMA_SURUMU:
        hatalar.append(f"sema_surumu '{SEMA_SURUMU}' olmalı, bulunan {veri.get('sema_surumu')!r}")
    if veri.get("veri_turu") not in VERI_TURLERI:
        hatalar.append(f"veri_turu {VERI_TURLERI} içinden olmalı, bulunan {veri.get('veri_turu')!r}")
    hedefler_ham = veri.get("hedefler")
    if not isinstance(hedefler_ham, list) or not hedefler_ham:
        raise GirdiHatasi(hatalar + ["hedefler boş olmayan dizi olmalı"])
    hedefler = [_dogrula_hedef(i, h, hatalar) for i, h in enumerate(hedefler_ham)]
    idler = [h.get("hedef_id") for h in hedefler]
    gorulen = set()
    for hid in idler:
        if hid in gorulen:
            hatalar.append(f"yinelenen hedef_id {hid!r}")
        gorulen.add(hid)
    vakalar_ham = veri.get("vakalar") or []
    if not isinstance(vakalar_ham, list):
        hatalar.append("vakalar dizi olmalı")
        vakalar_ham = []
    vakalar = [_dogrula_vaka(i, v, gorulen, hatalar) for i, v in enumerate(vakalar_ham)]
    ciftler = set()
    for v in vakalar:
        anahtar = (v.get("hedef_id"), v.get("vaka_id"))
        if anahtar in ciftler:
            hatalar.append(f"yinelenen (hedef_id, vaka_id) {anahtar!r}")
        ciftler.add(anahtar)
    if hatalar:
        raise GirdiHatasi(hatalar)
    return Girdi(veri["sema_surumu"], veri["veri_turu"], veri.get("aciklama") or "", hedefler, vakalar,
                 kaynak or {})


# ---------------------------------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------------------------------
_CSV_TAMSAYI = set(ZORUNLU_IKILI) | set(OLCUM_IKILI) | {"L_duzeyi", "B4_satir"}


def _csv_deger(alan: str, metin: str):
    metin = metin.strip()
    if metin == "":
        return None
    if alan in _CSV_TAMSAYI:
        try:
            return int(metin)
        except ValueError:
            return metin   # doğrulayıcı reddeder
    return metin


def _csv_oku(metin: str) -> tuple[dict, list[dict]]:
    ust = {}
    satirlar = metin.splitlines()
    govde = []
    for s in satirlar:
        if s.startswith("#"):
            for parca in s[1:].split(";"):
                if "=" in parca:
                    k, v = parca.split("=", 1)
                    ust[k.strip()] = v.strip()
        else:
            govde.append(s)
    okuyucu = csv.DictReader(io.StringIO("\n".join(govde)))
    return ust, list(okuyucu)


def _csv_hedefler(metin: str) -> tuple[dict, list[dict]]:
    ust, satirlar = _csv_oku(metin)
    hedefler = []
    for s in satirlar:
        h = {}
        for alan, deger in s.items():
            if alan == "belirsiz_nedenleri":
                d = {}
                for parca in (deger or "").split(";"):
                    if parca.strip():
                        a, _, b = parca.partition(":")
                        d[a.strip()] = b.strip()
                h[alan] = d
            else:
                h[alan] = _csv_deger(alan, deger or "")
        hedefler.append(h)
    return ust, hedefler


def _csv_vakalar(metin: str) -> list[dict]:
    _, satirlar = _csv_oku(metin)
    out = []
    for s in satirlar:
        v = {k: _csv_deger(k, d or "") for k, d in s.items()}
        if v.get("uyum") is not None:
            try:
                v["uyum"] = int(v["uyum"])
            except (TypeError, ValueError):
                pass
        out.append(v)
    return out


def _oku_bayt(yol: str) -> bytes:
    with open(yol, "rb") as f:
        return f.read()


def yukle(yol: str, vakalar_yolu: str | None = None) -> Girdi:
    """JSON (`.json`) ya da CSV (`hedefler.csv` [+ `vakalar.csv`]) girdisini yükler ve doğrular."""
    ham = _oku_bayt(yol)
    kaynak = {"dosya": os.path.basename(yol), "sha256": hashlib.sha256(ham).hexdigest()}
    if yol.lower().endswith(".json"):
        if vakalar_yolu:
            raise GirdiHatasi(["JSON girdisinde vakalar aynı dosyada verilir"])
        veri = json.loads(ham.decode("utf-8"))
        return sozlukten(veri, kaynak)
    if yol.lower().endswith(".csv"):
        ust, hedefler = _csv_hedefler(ham.decode("utf-8-sig"))
        vakalar = []
        if vakalar_yolu:
            vb = _oku_bayt(vakalar_yolu)
            kaynak["vakalar_dosya"] = os.path.basename(vakalar_yolu)
            kaynak["vakalar_sha256"] = hashlib.sha256(vb).hexdigest()
            vakalar = _csv_vakalar(vb.decode("utf-8-sig"))
        veri = {"sema_surumu": ust.get("sema_surumu"), "veri_turu": ust.get("veri_turu"),
                "aciklama": ust.get("aciklama", ""), "hedefler": hedefler, "vakalar": vakalar}
        return sozlukten(veri, kaynak)
    raise GirdiHatasi([f"desteklenmeyen uzantı: {yol}"])
