#!/usr/bin/env python3
"""SENTETIK duman testi fikstürü (BATARYA DEĞİL; oracle'sız; yalnız adaptör iskeletinin çalıştığını sınar).

Ön kayıt koruması: batarya vektörleri (experiment/vector-generator/vektorler) bu testte KULLANILMAZ. Bu betik kendi geçici
anahtarlarını üretir, kendi belirteçlerini imzalar ve manifest/JWKS'i bataryanın ALAN YAPISIYLA (ama farklı
kimliklerle: SENT_*) yazar. Çıktı: <hedef>/v (MANIFEST.json + dosyalar), <hedef>/anahtarlar, <hedef>/isler.jsonl.
Kullanım: python sentetik_uret.py <cikti_klasoru>
"""
import base64, json, os, sys, time
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, utils
from cryptography.hazmat.primitives import hashes

try:
    from cryptography.hazmat.primitives.asymmetric import mldsa
except Exception:  # pragma: no cover
    mldsa = None

out = sys.argv[1]
os.makedirs(f"{out}/v/S", exist_ok=True)
os.makedirs(f"{out}/anahtarlar/s", exist_ok=True)
b64 = lambda b: base64.urlsafe_b64encode(b).rstrip(b"=").decode()
now = int(time.time())

ec_k = ec.generate_private_key(ec.SECP256R1())
ed_k = ed25519.Ed25519PrivateKey.generate()
nums = ec_k.public_key().public_numbers()
keys = [
    {"kid": "sent-es256", "kty": "EC", "crv": "P-256", "x": b64(nums.x.to_bytes(32, "big")), "y": b64(nums.y.to_bytes(32, "big"))},
    {"kid": "sent-ed25519", "kty": "OKP", "crv": "Ed25519", "x": b64(ed_k.public_key().public_bytes_raw())},
]
ml_k = None
if mldsa is not None:
    ml_k = mldsa.MLDSA65PrivateKey.generate()
    keys.append({"kid": "sent-mldsa65", "kty": "AKP", "alg": "ML-DSA-65", "pub": b64(ml_k.public_key().public_bytes_raw())})
json.dump({"keys": keys}, open(f"{out}/anahtarlar/s/jwks.json", "w"))

def sign(alg, data):
    if alg == "ES256":
        r, s = utils.decode_dss_signature(ec_k.sign(data, ec.ECDSA(hashes.SHA256())))
        return r.to_bytes(32, "big") + s.to_bytes(32, "big")
    if alg in ("EdDSA", "Ed25519"):
        return ed_k.sign(data)
    if alg == "ML-DSA-65":
        return ml_k.sign(data)
    raise ValueError(alg)

KID = {"ES256": "sent-es256", "EdDSA": "sent-ed25519", "Ed25519": "sent-ed25519", "ML-DSA-65": "sent-mldsa65"}
payload = b64(json.dumps({"iss": "https://issuer.example", "iat": now - 60, "exp": now + 86400, "vct": "s"}).encode())
manifest, jobs = [], []

def add(vid, dosya, seri, kol, pol, algler, dg):
    manifest.append({"id": vid, "dosya": dosya, "serilestirme": seri, "dogrulama_girdileri": dg})
    jobs.append({"algler": algler, "artefakt": "jws-cekirdek", "dosya": "v1.3/" + dosya, "kol": kol,
                 "politika": pol, "serilestirme": seri, "vektor_id": vid})

algs = ["ES256", "EdDSA", "Ed25519"] + (["ML-DSA-65"] if ml_k else [])
for alg in algs:
    h = b64(json.dumps({"alg": alg, "kid": KID[alg], "typ": "JWT"}).encode())
    si = f"{h}.{payload}".encode()
    sig = sign(alg, si)
    bad = bytearray(sig); bad[5] ^= 1
    for ad, s in (("SENT_PLUS_" + alg, sig), ("SENT_MINUS_" + alg, bytes(bad))):
        open(f"{out}/v/S/{ad}.jws", "w").write(f"{h}.{payload}.{b64(s)}")
        dg = {"jwks": "anahtarlar/s/jwks.json", "kid": [KID[alg]], "simdi": now}
        kol = {"ES256": "kontrol-EdDSA", "EdDSA": "kontrol-EdDSA", "Ed25519": "kontrol-Ed25519", "ML-DSA-65": "tedavi-ML-DSA-65"}[alg]
        for pol in ("GEC", "IZIN-A", "IZIN-AX", "L4"):
            add(ad, f"S/{ad}.jws", "compact", kol, pol, alg, dg)

# General JSON, iki imza (ES256 + EdDSA), kid yok -> alg_kid ile seçim; ikinci imza bozuk eşi
def general(ad, algs2, bozuk=None):
    sigs = []
    for i, alg in enumerate(algs2):
        h = b64(json.dumps({"alg": alg}).encode())
        s = bytearray(sign(alg, f"{h}.{payload}".encode()))
        if bozuk == i: s[5] ^= 1
        sigs.append({"protected": h, "signature": b64(bytes(s))})
    open(f"{out}/v/S/{ad}.json", "w").write(json.dumps({"payload": payload, "signatures": sigs}))
    dg = {"jwks": "anahtarlar/s/jwks.json", "kid": [KID[a] for a in algs2], "simdi": now, "alg_kid": {a: KID[a] for a in algs2}}
    for pol in ("GEC", "P0", "P1", "L4", "L4-S", "L4-Y"):
        add(ad, f"S/{ad}.json", "general", "kontrol-EdDSA", pol, ";".join(algs2), dg)

# SD-JWT (açıklamasız, `_sd_alg` VAR, typ dc+sd-jwt / vc+sd-jwt) — SD-JWT kütüphanelerinin iskelet sınaması için
for typ in ("dc+sd-jwt", "vc+sd-jwt"):
    yuk = b64(json.dumps({"iss": "https://issuer.example", "iat": now - 60, "exp": now + 86400, "vct": "s", "_sd_alg": "sha-256"}).encode())
    for alg in ("ES256", "EdDSA"):
        h = b64(json.dumps({"alg": alg, "kid": KID[alg], "typ": typ}).encode())
        sig = sign(alg, f"{h}.{yuk}".encode()); bad = bytearray(sig); bad[5] ^= 1
        for ad, s in ((f"SENT_SD_{typ[:2]}_PLUS_{alg}", sig), (f"SENT_SD_{typ[:2]}_MINUS_{alg}", bytes(bad))):
            open(f"{out}/v/S/{ad}.sdjwt", "w").write(f"{h}.{yuk}.{b64(s)}~")
            manifest.append({"id": ad, "dosya": f"S/{ad}.sdjwt", "serilestirme": "sd-jwt-compact",
                             "dogrulama_girdileri": {"jwks": "anahtarlar/s/jwks.json", "kid": [KID[alg]], "simdi": now}})
            jobs.append({"algler": alg, "artefakt": "sd-jwt-vc", "dosya": f"v1.3/S/{ad}.sdjwt", "kol": "kontrol-EdDSA",
                         "politika": "GEC", "serilestirme": "sd-jwt-compact", "vektor_id": ad})

general("SENT_GJ_ES256_EdDSA", ["ES256", "EdDSA"])
general("SENT_GJ_ES256_EdDSA_ikinci_bozuk", ["ES256", "EdDSA"], bozuk=1)
general("SENT_GJ_tek_ES256", ["ES256"])
json.dump({"surum": "SENTETIK", "vektorler": manifest}, open(f"{out}/v/MANIFEST.json", "w"), indent=1)
with open(f"{out}/isler.jsonl", "w") as f:
    for j in jobs:
        f.write(json.dumps(j) + "\n")
print(f"{len(jobs)} sentetik is; mldsa={'var' if ml_k else 'yok'}")
