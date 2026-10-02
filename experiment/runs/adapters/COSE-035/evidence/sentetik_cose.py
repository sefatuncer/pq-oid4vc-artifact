#!/usr/bin/env python3
"""SYNTHETIC COSE smoke-test fixture (NOT the battery; no oracle). Produces COSE_Sign1 (ES256 -7, EdDSA -8,
Ed25519 -19) and COSE_Sign with one or two signers from temporary keys; the manifest fields have the STRUCTURE of the battery's dogrulama_girdileri
(cose_kid_hex, cose_key_hex). Usage: python sentetik_cose.py <output_folder>  (adds v/, anahtarlar/, isler.jsonl)"""
import json, os, sys
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, utils
from cryptography.hazmat.primitives import hashes

out = sys.argv[1]
os.makedirs(f"{out}/v/C", exist_ok=True)

def h(n, ai):  # CBOR head
    if ai < 24: return bytes([n << 5 | ai])
    if ai < 256: return bytes([n << 5 | 24, ai])
    if ai < 65536: return bytes([n << 5 | 25]) + ai.to_bytes(2, "big")
    return bytes([n << 5 | 26]) + ai.to_bytes(4, "big")

def enc(o):
    if isinstance(o, bool): raise TypeError
    if isinstance(o, int): return h(0, o) if o >= 0 else h(1, -1 - o)
    if isinstance(o, bytes): return h(2, len(o)) + o
    if isinstance(o, str): b = o.encode(); return h(3, len(b)) + b
    if isinstance(o, list): return h(4, len(o)) + b"".join(enc(x) for x in o)
    if isinstance(o, dict): return h(5, len(o)) + b"".join(enc(k) + enc(v) for k, v in o.items())
    raise TypeError(o)

def tag(t, o): return h(6, t) + enc(o)

from cryptography.hazmat.primitives.asymmetric import mldsa
ec_k = ec.generate_private_key(ec.SECP256R1()); ed_k = ed25519.Ed25519PrivateKey.generate(); ml_k = mldsa.MLDSA65PrivateKey.generate()
n = ec_k.public_key().public_numbers()
kid_ec, kid_ed, kid_ml = b"\x01" * 32, b"\x02" * 32, b"\x03" * 32
keys = {kid_ec.hex(): enc({1: 2, 2: kid_ec, -1: 1, -2: n.x.to_bytes(32, "big"), -3: n.y.to_bytes(32, "big")}).hex(),
        kid_ed.hex(): enc({1: 1, 2: kid_ed, -1: 6, -2: ed_k.public_key().public_bytes_raw()}).hex(),
        kid_ml.hex(): enc({1: 7, 2: kid_ml, 3: -49, -1: ml_k.public_key().public_bytes_raw()}).hex()}

def sign(alg, data):
    if alg == -7:
        r, s = utils.decode_dss_signature(ec_k.sign(data, ec.ECDSA(hashes.SHA256())))
        return r.to_bytes(32, "big") + s.to_bytes(32, "big")
    if alg == -49: return ml_k.sign(data)
    return ed_k.sign(data)

payload = enc({1: "https://issuer.example", 4: 1821536000})
man, jobs = [], []
def add(vid, seri, kol, pols, kids):
    man.append({"id": vid, "dosya": f"C/{vid}.cbor", "serilestirme": seri,
                "dogrulama_girdileri": {"cose_kid_hex": [k.hex() for k in kids], "cose_key_hex": {k.hex(): keys[k.hex()] for k in kids}, "simdi": 1790003700}})
    for p in pols:
        jobs.append({"algler": "", "artefakt": "cose", "dosya": f"v1.3/C/{vid}.cbor", "kol": kol, "politika": p, "serilestirme": seri, "vektor_id": vid})

for alg, kid, ad, kol in ((-7, kid_ec, "ES256", "kontrol-EdDSA"), (-8, kid_ed, "EdDSA", "kontrol-EdDSA"), (-19, kid_ed, "Ed25519", "kontrol-Ed25519"),
                          (-49, kid_ml, "ML-DSA-65", "tedavi-ML-DSA-65")):
    prot = enc({1: alg})
    sig = sign(alg, enc(["Signature1", prot, b"", payload]))
    for vid, s in ((f"SENTC_PLUS_{ad}", sig), (f"SENTC_MINUS_{ad}", sig[:5] + bytes([sig[5] ^ 1]) + sig[6:])):
        open(f"{out}/v/C/{vid}.cbor", "wb").write(tag(18, [prot, {4: kid}, payload, s]))
        add(vid, "COSE_Sign1", kol, ["GEC", "IZIN-A", "IZIN-AX", "L4"], [kid])

def cose_sign(vid, signers, bozuk=None):
    body = b""
    sigs = []
    for i, (alg, kid) in enumerate(signers):
        sp = enc({1: alg}); s = sign(alg, enc(["Signature", body, sp, b"", payload]))
        if bozuk == i: s = s[:5] + bytes([s[5] ^ 1]) + s[6:]
        sigs.append([sp, {4: kid}, s])
    open(f"{out}/v/C/{vid}.cbor", "wb").write(tag(98, [body, {}, payload, sigs]))
    add(vid, "COSE_Sign", "kontrol-EdDSA", ["GEC", "P0", "P1", "L4"], [k for _, k in signers])

cose_sign("SENTC_SIGN_tek_ES256", [(-7, kid_ec)])
cose_sign("SENTC_SIGN_iki", [(-7, kid_ec), (-8, kid_ed)])
m = json.load(open(f"{out}/v/MANIFEST.json"))
m["vektorler"] = [e for e in m["vektorler"] if not e["id"].startswith("SENTC_")] + man
json.dump(m, open(f"{out}/v/MANIFEST.json", "w"), indent=1)
open(f"{out}/isler_cose.jsonl", "w").write("".join(json.dumps(j) + "\n" for j in jobs))
print(len(jobs), "sentetik COSE isi")
