# -*- coding: utf-8 -*-
"""C3 adaptörü (Python): JOSE-083 pyjwt, JOSE-084 python-jose, SDJWT-018 sd-jwt-python.
Sözleşme: experiment/oracle/oracle-A/adaptor-sozlesme.md (1.0) ve experiment/runs/RUNNER.md. Oracle'ı GÖRMEZ.
Kullanım (konteynerde): python /a/adaptor.py <hedef_id> <jobs-v1.3.jsonl> <cikti.jsonl> <kosu>
Kurallar: yalnız belgeli genel API; politika için kendi doğrulama döngüsü YAZILMAZ (gerekiyorsa
'ifade-edilemedi' + NOTLAR'da B4). Biçim desteği (B6) API incelemesiyle önceden sabittir (MAPPING.md).
"""
import base64, hashlib, json, sys, time, traceback

V, K = "/v", "/anahtarlar"
A = "ES256"
X_OF = {"kontrol-EdDSA": "EdDSA", "kontrol-Ed25519": "Ed25519", "kontrol-ES384": "ES384", "tedavi-ML-DSA-65": "ML-DSA-65",
        "tedavi-composite": "ML-DSA-65-ES256"}
LEGACY_ISS = "https://legacy-issuer.example"


def b64d(s):
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def keys():
    kid, role = {}, {}
    for f in ("v1/acik-jwks.json", "v1.3/acik-jwks.json"):
        for k in json.load(open(f"{K}/{f}"))["keys"]:
            kid[k["kid"]] = k
    for f in ("v1/roller.json", "v1.3/roller.json"):
        for r, d in json.load(open(f"{K}/{f}"))["roller"].items():
            role[r] = d
    alg2kid = {}
    for r, d in role.items():
        if r.startswith("issuer/"):
            alg2kid.setdefault(d["tur"], d["kid"])
    return kid, alg2kid


KID, ALG2KID = keys()


def hdr(compact):
    return json.loads(b64d(compact.split(".")[0]))


def payload_iss(compact):
    try:
        return json.loads(b64d(compact.split(".")[1])).get("iss")
    except Exception:
        return None


def jwk_for(h):
    if h.get("kid") in KID:
        return KID[h["kid"]]
    a = h.get("alg")
    a = {"EdDSA": "Ed25519"}.get(a, a) if a not in ALG2KID else a
    return KID.get(ALG2KID.get(a) or ALG2KID.get(h.get("alg"), ""), None)


def temel(pol):
    """Politikanın yapılandırma adı: `|sdjwtvc=…` ve `@-19` ekleri yalnız oracle beklentisini böler (oracle-B YONTEM §2)."""
    return pol.split("|")[0].split("@")[0]


def allowed(pol, X, iss, supported):
    """W kümesi (YONTEM §2). Kompakt tek imzalı nesnede R={X}: göç etmiş ihraççı için yalnız X."""
    pol = temel(pol)
    if pol in ("GEC", "GEC@-19", "P0", "P1"):
        return list(supported)
    if pol == "IZIN-A":
        return [A]
    if pol == "IZIN-AX":
        return [A, X]
    if pol in ("L4", "L4-S", "L4-Y", "L4@-19", "L4-YOL"):
        return [A, X] if iss == LEGACY_ISS else [X]
    return list(supported)


def klass(e):
    m = f"{type(e).__name__}: {e}".lower()
    for pat, c in (("not allowed", "alg-izin-disi"), ("not supported", "alg-desteklenmiyor"), ("unsupported", "alg-desteklenmiyor"),
                   ("unable to find an algorithm", "alg-desteklenmiyor"), ("algorithm not", "alg-desteklenmiyor"),
                   ("asymmetric key", "alg-anahtar-uyusmazligi"), ("signature", "imza-gecersiz"), ("verification failed", "imza-gecersiz"),
                   ("expired", "zaman"), ("decode", "ayristirma"), ("invalid header", "ayristirma"), ("no key", "anahtar-bulunamadi"),
                   ("key", "anahtar-bulunamadi")):
        if pat in m:
            return c
    return "istisna-diger"


# ---------------- hedefler ----------------
class PyJWT:
    hid, api = "JOSE-083", "jwt.decode(token, key, algorithms=W)"
    def __init__(self):
        import jwt
        self.jwt = jwt
        self.ver = jwt.__version__
        self.supported = [a for a in jwt.algorithms.get_default_algorithms() if a not in ("none",) and not a.startswith("HS")]
    def formats(self):
        return {"compact"}
    def verify(self, job, data, X):
        from jwt import PyJWK
        tok = data.strip()
        h = hdr(tok)
        j = jwk_for(h)
        if j is None:
            raise LookupError("no key for kid/alg")
        key = PyJWK(j, algorithm=h.get("alg") if h.get("alg") in self.supported else None).key
        W = allowed(job["politika"], X, payload_iss(tok), self.supported)
        self.jwt.decode(tok, key, algorithms=W, options={"verify_aud": False, "verify_exp": False, "verify_iat": False, "verify_nbf": False})
        return [{"sira": 0, "alg": h.get("alg"), "sonuc": "gecerli"}]


class PyJose:
    hid, api = "JOSE-084", "jose.jws.verify(token, jwk, algorithms=W)"
    def __init__(self):
        from jose import jws, constants
        import jose
        self.jws, self.ver = jws, jose.__version__
        self.supported = sorted(constants.ALGORITHMS.SUPPORTED - constants.ALGORITHMS.HMAC - {"none"})
    def formats(self):
        return {"compact"}
    def verify(self, job, data, X):
        tok = data.strip()
        h = hdr(tok)
        j = jwk_for(h)
        if j is None:
            raise LookupError("no key for kid/alg")
        W = allowed(job["politika"], X, payload_iss(tok), self.supported)
        self.jws.verify(tok, j, algorithms=W)
        return [{"sira": 0, "alg": h.get("alg"), "sonuc": "gecerli"}]


class SdJwtPython:
    """sd-jwt 0.10.4: SDJWTVerifier(presentation, cb_get_issuer_key, expected_aud, expected_nonce,
    serialization_format). İzin listesi parametresi YOK (kaynak: sd_jwt/verifier.py _verify_sd_jwt sign_alg=None,
    genel __init__'e açılmamış). Bu yüzden IZIN-*/L4* -> ifade-edilemedi (MAPPING.md; B4 alternatifi NOTES.md)."""
    hid, api = "SDJWT-018", "sd_jwt.verifier.SDJWTVerifier(presentation, cb_get_issuer_key, aud, nonce, serialization_format)"
    def __init__(self):
        import importlib.metadata as md
        from sd_jwt.verifier import SDJWTVerifier
        from jwcrypto.jwk import JWK
        self.V, self.JWK, self.ver = SDJWTVerifier, JWK, md.version("sd-jwt")
        self.supported = []
    def formats(self):
        return {"sd-jwt-compact", "sd-jwt-flattened", "sd-jwt-general", "compact-as-sdjwt"}
    def verify(self, job, data, X):
        pol = temel(job["politika"])
        if pol not in ("GEC", "P0", "P1", "P2"):
            return "ifade-edilemedi"
        ser = job["serilestirme"]
        fmt = "compact" if ser in ("sd-jwt-compact", "compact") else "json"
        pres = data.strip()
        if ser == "compact":
            pres = pres + "~"   # açıklamasız SD-JWT (imza ve yük değişmez; MAPPING.md)
        def cb(iss, header):
            j = jwk_for(header)
            if j is None:
                raise LookupError("no key for kid/alg")
            return self.JWK(**j)
        man = job.get("_man", {})
        aud, nonce = (man.get("kb_aud"), man.get("kb_nonce")) if job["artefakt"].startswith("vp") else (None, None)
        self.V(pres, cb, expected_aud=aud, expected_nonce=nonce, serialization_format=fmt)
        return []


IMPL = {"JOSE-083": PyJWT, "JOSE-084": PyJose, "SDJWT-018": SdJwtPython}


def main():
    hid, isler, cikti, kosu = sys.argv[1:5]
    t = IMPL[hid]()
    asha = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
    fmts = t.formats()
    out = open(cikti, "w", encoding="utf-8")
    for line in open(isler, encoding="utf-8"):
        job = json.loads(line)
        X = X_OF.get(job["kol"], "EdDSA")
        rec = dict(hedef_id=hid, hedef_surum=t.ver, adaptor_sha256=asha, kosu=kosu, vektor_id=job["vektor_id"],
                   politika=job["politika"], kol=job["kol"], sonuc_ham=None, hata_sinifi=None, hata_ozeti=None,
                   dogrulanan_algoritmalar=[], api_yolu=t.api, sure_ms=None)
        ser = job["serilestirme"]
        eff = "compact-as-sdjwt" if (ser == "compact" and "compact-as-sdjwt" in fmts) else ser
        if eff not in fmts:
            rec.update(sonuc_ham="uygulanamaz", hata_sinifi="bicim-desteklenmiyor")
            out.write(json.dumps(rec, ensure_ascii=False) + "\n"); continue
        data = open(f"{V}/{job['dosya']}", encoding="utf-8").read()
        t0 = time.perf_counter()
        try:
            r = t.verify(job, data, X)
            if r == "ifade-edilemedi":
                rec.update(sonuc_ham="ifade-edilemedi")
            else:
                rec.update(sonuc_ham="kabul", dogrulanan_algoritmalar=r)
        except Exception as e:
            rec.update(sonuc_ham="red", hata_sinifi=klass(e), hata_ozeti=f"{type(e).__name__}: {e}"[:200])
        rec["sure_ms"] = round((time.perf_counter() - t0) * 1000, 2)
        out.write(json.dumps(rec, ensure_ascii=False) + "\n")
    out.close()


if __name__ == "__main__":
    main()
