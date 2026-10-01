#!/usr/bin/env python3
"""COSE-036 wolfCOSE adaptör sürücüsü (C3 sözleşmesi 1.0 / KOSUCU §1–§3).

Doğrulamayı YALNIZ wolfCOSE yapar (kopru.c → wc_CoseKey_Decode + wc_CoseSign1_Verify / wc_CoseSign_Verify; ctypes ile
aynı süreçte). Bu sürücü yalnız iş dosyasını/manifesti okur, kid'e göre COSE_Key seçer ve çıktı satırını yazar.
Politika: wolfCOSE'ta izin listesi API'si yok; belgeli mekanizma anahtarın `alg` iğnesidir (WOLFCOSE_KEY.alg;
sign1.c "Honour the key->alg pin on the verify path"). Manifestten yalnız dogrulama_girdileri okunur. Ağ yok.
"""
import ctypes, json, os, sys, time

COSE_ID = {"ES256": -7, "ES384": -35, "EdDSA": -8, "Ed25519": -19, "ML-DSA-44": -48, "ML-DSA-65": -49, "ML-DSA-87": -50,
           "ML-DSA-65-ES256": -55}
AD = {v: k for k, v in COSE_ID.items()}
# wolfcose.h WOLFCOSE_ALG_*: ES256/384/512, ESP256/384/512, EdDSA, Ed25519, Ed448, PS*, ML-DSA-44/65/87, HSS-LMS
KUTUPHANE = ["ES256", "ES384", "EdDSA", "Ed25519", "ML-DSA-44", "ML-DSA-65", "ML-DSA-87"]
X_KOL = {"kontrol-EdDSA": "EdDSA", "kontrol-Ed25519": "Ed25519", "kontrol-ES384": "ES384", "tedavi-ML-DSA-65": "ML-DSA-65",
         "tedavi-composite": "ML-DSA-65-ES256"}
HATA = {-9000: "INVALID_ARG", -9001: "BUFFER_TOO_SMALL", -9002: "CBOR_MALFORMED", -9003: "CBOR_TYPE", -9004: "CBOR_OVERFLOW",
        -9006: "CBOR_DEPTH", -9010: "COSE_BAD_TAG", -9011: "COSE_BAD_ALG", -9012: "COSE_SIG_FAIL", -9014: "COSE_BAD_HDR",
        -9015: "COSE_KEY_TYPE", -9020: "CRYPTO", -9021: "UNSUPPORTED", -9023: "DETACHED_PAYLOAD"}
API = ("wc_CoseKey_PeekInfo/Init/Set{Ecc,Ed25519,MlDsa}/Decode(COSE_Key); key.alg = pin(W); "
       "wc_CoseSign1_Verify | wc_CoseSign_Verify(key, signerIndex, ...)")
lib = ctypes.CDLL("/opt/a/libkopru.so")
lib.a10_dogrula.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_int,
                            ctypes.c_int32, ctypes.c_long, ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_int)]


# --- asgari CBOR okuyucu (yalnız yapı: etiket, kid, imzacı sayısı; doğrulama yapmaz) ---
def cbor(b, i=0):
    ib = b[i]; mt, ai = ib >> 5, ib & 31; i += 1
    if ai < 24: n = ai
    elif ai in (24, 25, 26, 27):
        k = 1 << (ai - 24); n = int.from_bytes(b[i:i + k], "big"); i += k
    else: raise ValueError("belirsiz uzunluk desteklenmiyor")
    if mt == 0: return n, i
    if mt == 1: return -1 - n, i
    if mt in (2, 3): v = b[i:i + n]; return (v if mt == 2 else v.decode()), i + n
    if mt == 4:
        out = []
        for _ in range(n): v, i = cbor(b, i); out.append(v)
        return out, i
    if mt == 5:
        out = {}
        for _ in range(n):
            k, i = cbor(b, i); v, i = cbor(b, i); out[k if not isinstance(k, list) else str(k)] = v
        return out, i
    if mt == 6: v, i = cbor(b, i); return ("etiket", n, v), i
    if mt == 7: return {20: False, 21: True, 22: None}.get(n, n), i
    raise ValueError(mt)


def basliklar(korumali, korumasiz):
    k = cbor(korumali)[0] if korumali else {}
    return k, (korumasiz or {})


def girdi(vid, _m={}):
    if not _m:
        y = "/v/MANIFEST.json" if os.path.exists("/v/MANIFEST.json") else "/v/v1.3/MANIFEST.json"
        for e in json.load(open(y, encoding="utf-8"))["vektorler"]:
            _m[e["id"]] = e.get("dogrulama_girdileri") or {}   # `insa` OKUNMAZ
    return _m[vid]


def vektor_yolu(d):
    for y in ("/v/" + d, "/v/" + d[5:] if d.startswith("v1.3/") else "/v/" + d):
        if os.path.exists(y): return y
    return "/v/" + d


def politika(isx):
    taban = isx["politika"].split("|")[0].split("@")[0]; x = X_KOL.get(isx["kol"])  # ekler yalnız oracle'ı böler
    if taban in ("GEC", "P0", "P1", "P2", "VARSAYILAN"): return taban, None, []      # pin yok = kütüphane varsayılanı
    if taban == "IZIN-A": return taban, ["ES256"], []
    if x is None: raise ValueError("kol icin X tanimsiz")
    if taban == "IZIN-AX": return taban, ["ES256", x], []
    if taban in ("L4", "L4-S", "L4-Y", "L4-YOL"): return taban, ["ES256", x], [x]
    raise ValueError("bilinmeyen politika " + isx["politika"])


def dogal_alg(info_kty, info_crv, info_alg, kol):
    if info_alg: return info_alg
    if info_kty == 2: return {1: -7, 2: -35}.get(info_crv, 0)
    if info_kty == 1 and info_crv == 6: return -19 if kol == "kontrol-Ed25519" else -8
    return 0


def b6():
    return {"sonuc_ham": "uygulanamaz", "hata_sinifi": "bicim-desteklenmiyor", "hata_ozeti": "B6: ESLEME.md (API incelemesi)", "api_yolu": API}


def dogrula(isx):
    seri = isx["serilestirme"]
    if seri not in ("COSE_Sign1", "COSE_Sign"): return b6()
    dg = girdi(isx["vektor_id"])
    ham = open(vektor_yolu(isx["dosya"]), "rb").read()
    taban, w, r = politika(isx)
    if taban == "L4-YOL":
        return {"sonuc_ham": "ifade-edilemedi", "hata_sinifi": None, "hata_ozeti": "x5c/x5chain yol sinifi politikasi (L4-YOL, B2) icin belgeli API yok", "api_yolu": API}
    izin = None if w is None else (r if r else w)
    obj, _ = cbor(ham)
    if not (isinstance(obj, tuple) and obj[0] == "etiket"):
        return {"sonuc_ham": "red", "hata_sinifi": "ayristirma", "hata_ozeti": "etiketsiz COSE", "api_yolu": API}
    govde = obj[2]
    imzaci = -1
    if seri == "COSE_Sign":
        imzalar = govde[3]
        if len(imzalar) != 1:
            # Çoklu imzacı kuralı (P0/P1/R) için belgeli seçenek yok: wc_CoseSign_Verify imzacıyı tek tek doğrular;
            # imzacılar üzerinde dolaşan döngü çağıranın kodu olur (B4, NOTLAR.md).
            return {"sonuc_ham": "ifade-edilemedi", "hata_sinifi": None,
                    "hata_ozeti": "COSE_Sign coklu imzaci kurali (P0/P1/R) icin API secenegi yok (wc_CoseSign_Verify imzaci basina)", "api_yolu": API}
        imzaci = 0
        kor, korsuz = basliklar(imzalar[0][0], imzalar[0][1])
    else:
        kor, korsuz = basliklar(govde[0], govde[1])
    alg_id = kor.get(1)
    kid = kor.get(4, korsuz.get(4))
    harita = dg.get("cose_key_hex") or {}
    if isinstance(harita, str): harita = json.loads(harita)
    kh = kid.hex() if isinstance(kid, bytes) else (dg.get("cose_kid_hex") or [None])[0]
    if kh not in harita:
        return {"sonuc_ham": "red", "hata_sinifi": "anahtar-bulunamadi", "hata_ozeti": f"COSE_Key yok (kid={kh})", "api_yolu": API, "anahtar_yolu": "COSE_Key"}
    ck = bytes.fromhex(harita[kh])
    kmap = cbor(ck)[0]
    pin_kullan, pin = 0, 0
    if izin is not None:
        # anahtar–alg bağlaması: anahtarın doğal alg'ı W içindeyse o, değilse W'nin ilk öğesi iğnelenir
        d = dogal_alg(kmap.get(1), kmap.get(-1), kmap.get(3), isx["kol"])
        ids = [COSE_ID[a] for a in izin if a in COSE_ID]
        pin_kullan, pin = 1, (d if d in ids else ids[0])
    alg_out, asama = ctypes.c_int32(0), ctypes.c_int(0)
    ret = lib.a10_dogrula(ham, len(ham), ck, len(ck), pin_kullan, pin, imzaci, ctypes.byref(alg_out), ctypes.byref(asama))
    if ret == 0:
        a = alg_out.value if seri == "COSE_Sign1" else alg_id
        return {"sonuc_ham": "kabul", "api_yolu": API, "anahtar_yolu": "COSE_Key",
                "dogrulanan": [{"sira": 0, "alg": AD.get(a, str(a)), "sonuc": "gecerli"}]}
    ad = AD.get(alg_id)
    if asama.value < 4: sinif = "alg-desteklenmiyor" if ret in (-9021, -9015, -9011) or ad not in KUTUPHANE else "istisna-diger"
    elif ret == -9012: sinif = "imza-gecersiz"
    # Ed25519/EdDSA'da bozuk imza wolfCrypt'ten WOLFCOSE_E_CRYPTO (-9020) olarak döner (sentetik duman: SENTC_MINUS_Ed*)
    elif ret == -9020 and ad in ("EdDSA", "Ed25519"): sinif = "imza-gecersiz"
    elif ret == -9011:
        sinif = "alg-desteklenmiyor" if ad not in KUTUPHANE else ("alg-izin-disi" if izin is not None and ad not in izin else "alg-anahtar-uyusmazligi")
    elif ret == -9015: sinif = "alg-anahtar-uyusmazligi"
    elif ret == -9021: sinif = "alg-desteklenmiyor"
    elif ret in (-9002, -9003, -9010, -9004, -9006): sinif = "ayristirma"
    elif ret == -9014: sinif = "crit" if 2 in kor else "ayristirma"
    else: sinif = "istisna-diger"
    return {"sonuc_ham": "red", "hata_sinifi": sinif, "api_yolu": API, "anahtar_yolu": "COSE_Key",
            "hata_ozeti": f"wolfCOSE {ret} ({HATA.get(ret, '?')}) asama={asama.value} pin={pin if pin_kullan else 'yok'}"}


def sabit(ad):
    try: return open("/opt/a/" + ad).read().strip()
    except OSError: return ""


def main(a):
    girdi_d, cikti = a[1], a[2]
    kosu = os.environ.get("KOSU") or (os.path.basename(cikti)[:-6].split(".")[-1] if os.path.basename(cikti)[:-6].count(".") else "oncesi")
    with open(cikti, "w", encoding="utf-8", newline="\n") as out:
        for l in open(girdi_d, encoding="utf-8"):
            if not l.strip(): continue
            isx = json.loads(l); t0 = time.monotonic()
            try: s = dogrula(isx)
            except Exception as e:  # noqa: BLE001
                s = {"sonuc_ham": "istisna", "hata_sinifi": "adaptor-hatasi", "hata_ozeti": f"{type(e).__name__}: {e}", "api_yolu": None}
            out.write(json.dumps({"sozlesme": "adaptor-sozlesme/1.0", "hedef_id": os.environ.get("HEDEF_ID", "bilinmiyor"),
                "hedef_surum": sabit("HEDEF_SURUM"), "adaptor_sha256": sabit("ADAPTOR_SHA256"), "kosu": kosu,
                "vektor_id": isx["vektor_id"], "politika": isx["politika"], "kol": isx["kol"], "sonuc_ham": s["sonuc_ham"],
                "hata_sinifi": s.get("hata_sinifi"), "hata_ozeti": (s.get("hata_ozeti") or None) and s["hata_ozeti"][:200],
                "dogrulanan_algoritmalar": s.get("dogrulanan", []), "api_yolu": s.get("api_yolu"),
                "anahtar_yolu": s.get("anahtar_yolu"), "sure_ms": int((time.monotonic() - t0) * 1000)}, ensure_ascii=False) + "\n")
            out.flush()


if __name__ == "__main__":
    main(sys.argv)
