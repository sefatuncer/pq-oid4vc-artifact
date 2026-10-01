"""Smoke-test data for the Rust adapters (not part of the battery).

Creates its own deterministic keys and tokens under <out>:
  anahtarlar/v1/{acik-jwks.json,roller.json}, anahtarlar/v1.3/{acik-jwks.json,roller.json}
  v/smoke/*                         tokens
  is/jobs_smoke.jsonl               job list, written with CRLF line ends on purpose
  expected.json                     expected (sonuc_ham, hata_sinifi, alg) per target and job,
                                    derived from the API reading in MAPPING.md before running
Needs Python 3 with `cryptography`. Usage: python make_smoke.py <out>
"""
import base64
import hashlib
import json
import os
import sys

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, ed25519
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

OUT = sys.argv[1]
ISS = "https://issuer.example"
LEGACY = "https://legacy-issuer.example"


def b64(b):
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def seed(label, n=32):
    return hashlib.sha256(("smoke-test/" + label).encode()).digest()[:n]


def ec_key(label, curve, order):
    return ec.derive_private_key(int.from_bytes(seed(label), "big") % (order - 1) + 1, curve)


P256_N = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
P384_N = int("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFC7634D81F4372DDF581A0DB248B0A77AECEC196ACCC52973", 16)

k_es256 = ec_key("es256", ec.SECP256R1(), P256_N)
k_legacy = ec_key("es256-legacy", ec.SECP256R1(), P256_N)
k_es384 = ec_key("es384", ec.SECP384R1(), P384_N)
k_ed = ed25519.Ed25519PrivateKey.from_private_bytes(seed("ed25519"))


def ec_jwk(k, kid, crv, size):
    n = k.public_key().public_numbers()
    return {"kid": kid, "kty": "EC", "crv": crv, "x": b64(n.x.to_bytes(size, "big")), "y": b64(n.y.to_bytes(size, "big"))}


ed_raw = k_ed.public_key().public_bytes_raw()
JWKS_V1 = [
    ec_jwk(k_es256, "smoke-es256", "P-256", 32),
    ec_jwk(k_es384, "smoke-es384", "P-384", 48),
    {"kid": "smoke-ed25519", "kty": "OKP", "crv": "Ed25519", "x": b64(ed_raw)},
    # Placeholder AKP key (random bytes, not a real ML-DSA key): exercises unsupported key types.
    {"kid": "smoke-mldsa", "kty": "AKP", "alg": "ML-DSA-65", "pub": b64(hashlib.shake_256(b"smoke-mldsa").digest(1952))},
]
JWKS_V13 = [ec_jwk(k_legacy, "smoke-es256-legacy", "P-256", 32)]
ROLES_V1 = {
    "issuer/ES256": {"tur": "ES256", "kid": "smoke-es256"},
    "issuer/ES384": {"tur": "ES384", "kid": "smoke-es384"},
    "issuer/EdDSA": {"tur": "EdDSA", "kid": "smoke-ed25519"},
    "issuer/ML-DSA-65": {"tur": "ML-DSA-65", "kid": "smoke-mldsa"},
}


def sign(alg, key, header, payload):
    h = b64(json.dumps(header, separators=(",", ":")).encode())
    p = b64(json.dumps(payload, separators=(",", ":")).encode())
    msg = f"{h}.{p}".encode()
    if alg == "ES256":
        r, s = decode_dss_signature(key.sign(msg, ec.ECDSA(hashes.SHA256())))
        sig = r.to_bytes(32, "big") + s.to_bytes(32, "big")
    elif alg == "ES384":
        r, s = decode_dss_signature(key.sign(msg, ec.ECDSA(hashes.SHA384())))
        sig = r.to_bytes(48, "big") + s.to_bytes(48, "big")
    elif alg == "EdDSA":
        sig = key.sign(msg)
    else:
        sig = hashlib.shake_256(msg).digest(3309)  # placeholder bytes
    return f"{h}.{p}.{b64(sig)}"


def tamper(tok):
    h, p, s = tok.split(".")
    raw = bytearray(base64.urlsafe_b64decode(s + "=" * (-len(s) % 4)))
    raw[5] ^= 0x01
    return f"{h}.{p}.{b64(bytes(raw))}"


def claims(iss=ISS, iat=1790000000, exp=1821536000, **extra):
    c = {"iss": iss, "iat": iat, "exp": exp, "vct": "urn:eudi:pid:1"}
    c.update(extra)
    return c


def hdr(alg, kid=None):
    h = {"alg": alg, "typ": "JWT"}
    if kid:
        h["kid"] = kid
    return h


def disclosure(salt, name, value):
    d = b64(json.dumps([salt, name, value]).encode())
    return d, b64(hashlib.sha256(d.encode()).digest())


d1, dg1 = disclosure("c2FsdC0wMDAwMDAwMDAx", "given_name", "Erika")
d2, _ = disclosure("c2FsdC0wMDAwMDAwMDAy", "family_name", "Mustermann")  # digest not in _sd
sd_payload = claims(_sd=[dg1], _sd_alg="sha-256")
sd_hdr = {"alg": "ES256", "kid": "smoke-es256", "typ": "dc+sd-jwt"}
sd_jws = sign("ES256", k_es256, sd_hdr, sd_payload)

TOKENS = {
    "es256_ok.jws": sign("ES256", k_es256, hdr("ES256", "smoke-es256"), claims(given_name="Erika")),
    "eddsa_ok.jws": sign("EdDSA", k_ed, hdr("EdDSA", "smoke-ed25519"), claims(given_name="Erika")),
    "es256_legacy.jws": sign("ES256", k_legacy, hdr("ES256", "smoke-es256-legacy"), claims(iss=LEGACY)),
    "es384_ok.jws": sign("ES384", k_es384, hdr("ES384", "smoke-es384"), claims()),
    # Header says EdDSA, key id points to the P-256 key and the signature is ES256.
    "confusion.jws": sign("ES256", k_es256, hdr("EdDSA", "smoke-es256"), claims()),
    "nokid_es256.jws": sign("ES256", k_es256, hdr("ES256"), claims()),
    "mldsa_hdr.jws": sign("ML-DSA-65", None, hdr("ML-DSA-65", "smoke-mldsa"), claims()),
    "expired_es256.jws": sign("ES256", k_es256, hdr("ES256", "smoke-es256"), claims(iat=1789000000, exp=1789500000)),
    "garbage.jws": "not.a.jws",
    "sdjwt_ok.sdjwt": f"{sd_jws}~{d1}~",
    "sdjwt_badsig.sdjwt": f"{tamper(sd_jws)}~{d1}~",
    "sdjwt_unused.sdjwt": f"{sd_jws}~{d1}~{d2}~",
}
TOKENS["es256_badsig.jws"] = tamper(TOKENS["es256_ok.jws"])
TOKENS["eddsa_badsig.jws"] = tamper(TOKENS["eddsa_ok.jws"])

E, T, C = "kontrol-EdDSA", "tedavi-ML-DSA-65", "tedavi-composite"
# id, file, serialisation, artefact, policy, arm
JOBS = [
    ("J01", "es256_ok.jws", "compact", "jws-cekirdek", "GEC", E),
    ("J02", "es256_ok.jws", "compact", "jws-cekirdek", "IZIN-A", E),
    ("J03", "es256_ok.jws", "compact", "jws-cekirdek", "IZIN-AX", E),
    ("J04", "es256_ok.jws", "compact", "jws-cekirdek", "L4", E),
    ("J05", "es256_ok.jws", "compact", "jws-cekirdek", "L4", T),
    ("J06", "es256_ok.jws", "compact", "jws-cekirdek", "L4-YOL", E),
    ("J07", "es256_ok.jws", "compact", "jws-cekirdek", "L4|sdjwtvc=-19", E),
    ("J08", "es256_ok.jws", "compact", "jws-cekirdek", "GEC@-19", E),
    ("J09", "es256_ok.jws", "compact", "jws-cekirdek", "P0", C),
    ("J10", "es256_badsig.jws", "compact", "jws-cekirdek", "GEC", E),
    ("J11", "eddsa_ok.jws", "compact", "jws-cekirdek", "GEC", E),
    ("J12", "eddsa_ok.jws", "compact", "jws-cekirdek", "IZIN-A", E),
    ("J13", "eddsa_ok.jws", "compact", "jws-cekirdek", "IZIN-AX", E),
    ("J14", "eddsa_ok.jws", "compact", "jws-cekirdek", "L4", E),
    ("J15", "eddsa_badsig.jws", "compact", "jws-cekirdek", "GEC", E),
    ("J16", "es256_legacy.jws", "compact", "jws-cekirdek", "L4", E),
    ("J17", "es384_ok.jws", "compact", "jws-cekirdek", "GEC", E),
    ("J18", "es384_ok.jws", "compact", "jws-cekirdek", "IZIN-A", E),
    ("J19", "confusion.jws", "compact", "jws-cekirdek", "GEC", E),
    ("J20", "confusion.jws", "compact", "jws-cekirdek", "IZIN-A", E),
    ("J21", "nokid_es256.jws", "compact", "jws-cekirdek", "GEC", E),
    ("J22", "mldsa_hdr.jws", "compact", "jws-cekirdek", "GEC", T),
    ("J23", "mldsa_hdr.jws", "compact", "jws-cekirdek", "IZIN-AX", T),
    ("J24", "expired_es256.jws", "compact", "jws-cekirdek", "GEC", E),
    ("J25", "garbage.jws", "compact", "jws-cekirdek", "GEC", E),
    ("J26", "sdjwt_ok.sdjwt", "sd-jwt-compact", "vc-sdjwt", "GEC", E),
    ("J27", "sdjwt_ok.sdjwt", "sd-jwt-compact", "vc-sdjwt", "IZIN-A", E),
    ("J28", "sdjwt_badsig.sdjwt", "sd-jwt-compact", "vc-sdjwt", "GEC", E),
    ("J29", "sdjwt_unused.sdjwt", "sd-jwt-compact", "vc-sdjwt", "GEC", E),
    ("J30", "dummy.cbor", "COSE_Sign1", "cose", "GEC", E),
    ("J31", "missing.jws", "compact", "jws-cekirdek", "GEC", E),
    ("J32", "sdjwt_ok.sdjwt", "sd-jwt-compact", "vp-sdjwt", "GEC", E),
]

K, R, N, U, I = "kabul", "red", "ifade-edilemedi", "uygulanamaz", "istisna"
UA = (U, "bicim-desteklenmiyor", None)
MISSING = (I, "adaptor-hatasi", None)
NE = (N, None, None)


def acc(alg):
    return (K, None, alg)


def rej(cls):
    return (R, cls, None)


EXPECTED = {
    "JOSE-091": {
        "J01": acc("ES256"), "J02": acc("ES256"), "J03": acc("ES256"), "J04": rej("alg-desteklenmiyor"),
        "J05": rej("alg-desteklenmiyor"), "J06": NE, "J07": rej("alg-desteklenmiyor"), "J08": acc("ES256"),
        "J09": acc("ES256"), "J10": rej("imza-gecersiz"), "J11": rej("alg-desteklenmiyor"),
        "J12": rej("alg-anahtar-uyusmazligi"), "J13": rej("alg-anahtar-uyusmazligi"), "J14": rej("alg-desteklenmiyor"),
        "J15": rej("alg-desteklenmiyor"), "J16": acc("ES256"), "J17": acc("ES384"), "J18": rej("imza-gecersiz"),
        "J19": rej("alg-desteklenmiyor"), "J20": acc("ES256"), "J21": acc("ES256"), "J22": rej("alg-desteklenmiyor"),
        "J23": rej("alg-desteklenmiyor"), "J24": acc("ES256"), "J25": rej("ayristirma"), "J26": UA, "J27": UA,
        "J28": UA, "J29": UA, "J30": UA, "J31": MISSING, "J32": UA,
    },
    "JOSE-092": {
        "J01": acc("ES256"), "J02": acc("ES256"), "J03": acc("ES256"), "J04": rej("alg-izin-disi"),
        "J05": rej("alg-izin-disi"), "J06": NE, "J07": rej("alg-izin-disi"), "J08": acc("ES256"), "J09": acc("ES256"),
        "J10": rej("imza-gecersiz"), "J11": acc("EdDSA"), "J12": rej("alg-izin-disi"), "J13": acc("EdDSA"),
        "J14": acc("EdDSA"), "J15": rej("imza-gecersiz"), "J16": acc("ES256"), "J17": acc("ES384"),
        "J18": rej("alg-izin-disi"), "J19": rej("alg-izin-disi"), "J20": rej("alg-izin-disi"), "J21": acc("ES256"),
        "J22": rej("alg-desteklenmiyor"), "J23": rej("alg-desteklenmiyor"), "J24": acc("ES256"), "J25": rej("ayristirma"),
        "J26": UA, "J27": UA, "J28": UA, "J29": UA, "J30": UA, "J31": MISSING, "J32": UA,
    },
    "SDJWT-010": {
        "J01": acc("ES256"), "J02": acc("ES256"), "J03": acc("ES256"), "J04": rej("alg-anahtar-uyusmazligi"),
        "J05": rej("alg-desteklenmiyor"), "J06": NE, "J07": rej("alg-anahtar-uyusmazligi"), "J08": acc("ES256"),
        "J09": acc("ES256"), "J10": rej("imza-gecersiz"), "J11": acc("EdDSA"), "J12": rej("alg-anahtar-uyusmazligi"),
        "J13": acc("EdDSA"), "J14": acc("EdDSA"), "J15": rej("imza-gecersiz"), "J16": acc("ES256"), "J17": acc("ES384"),
        "J18": rej("alg-anahtar-uyusmazligi"), "J19": rej("alg-anahtar-uyusmazligi"), "J20": rej("alg-izin-disi"),
        "J21": rej("anahtar-bulunamadi"), "J22": rej("alg-desteklenmiyor"), "J23": rej("alg-anahtar-uyusmazligi"),
        "J24": acc("ES256"), "J25": rej("ayristirma"), "J26": acc("ES256"), "J27": acc("ES256"),
        "J28": rej("imza-gecersiz"), "J29": rej("istisna-diger"), "J30": UA, "J31": MISSING, "J32": NE,
    },
    "SDJWT-025": {
        "J01": acc("ES256"), "J02": NE, "J03": NE, "J04": NE, "J05": NE, "J06": NE, "J07": NE, "J08": acc("ES256"),
        "J09": acc("ES256"), "J10": rej("imza-gecersiz"), "J11": acc("EdDSA"), "J12": NE, "J13": NE, "J14": NE,
        "J15": rej("imza-gecersiz"), "J16": NE, "J17": rej("imza-gecersiz"), "J18": NE, "J19": rej("imza-gecersiz"),
        "J20": NE, "J21": acc("ES256"), "J22": rej("alg-desteklenmiyor"), "J23": NE, "J24": rej("zaman"),
        "J25": rej("ayristirma"), "J26": acc("ES256"), "J27": NE, "J28": rej("imza-gecersiz"), "J29": rej("ayristirma"),
        "J30": UA, "J31": MISSING, "J32": NE,
    },
}


def write(path, data, mode="w"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode, **({} if "b" in mode else {"encoding": "utf-8", "newline": ""})) as f:
        f.write(data)


write(f"{OUT}/anahtarlar/v1/acik-jwks.json", json.dumps({"keys": JWKS_V1}, indent=1))
write(f"{OUT}/anahtarlar/v1.3/acik-jwks.json", json.dumps({"keys": JWKS_V13}, indent=1))
write(f"{OUT}/anahtarlar/v1/roller.json", json.dumps({"roller": ROLES_V1}, indent=1))
write(f"{OUT}/anahtarlar/v1.3/roller.json", json.dumps({"roller": {}}, indent=1))
for name, tok in TOKENS.items():
    write(f"{OUT}/v/smoke/{name}", tok + "\n")
write(f"{OUT}/v/smoke/dummy.cbor", b"\xd2\x84\x43\xa1\x01\x26\xa0\x40\x40", "wb")
lines = []
for jid, f, ser, art, pol, kol in JOBS:
    lines.append(json.dumps({"algler": "", "artefakt": art, "dosya": f"smoke/{f}", "kol": kol,
                             "politika": pol, "serilestirme": ser, "vektor_id": f"{jid}_{f.split('.')[0]}"}))
write(f"{OUT}/is/jobs_smoke.jsonl", "\r\n".join(lines) + "\r\n")
write(f"{OUT}/expected.json", json.dumps(EXPECTED, indent=1))
print(f"{len(TOKENS) + 1} files, {len(JOBS)} jobs written to {OUT}")
