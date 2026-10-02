#!/usr/bin/env python3
"""T04 — Size measurements and comparison with the P4 values of pilot B.

P4 (referans/pilot/p4/mldsa_sizes.csv; OpenSSL 3.5.6): SPKI, signature, CA and leaf certificate DER,
number of base64 characters of an x5c with 2 certificates. The P4 certificate profile (names, 20-byte serial number, 30-day
UTCTime validity, BC/KU/SKI/AKI) is copied exactly; since the ML-DSA sizes are fixed, exact
equality is expected; since the ECDSA signature varies by 70-72 bytes in DER, a tolerance of +-2 bytes for EC.
In addition: JWS/JWK/composite/DPoP sizes (nginx 8,182 B and Node 16,348 B thresholds, P4).
Usage: python t04_sizes.py <p4 folder> <result folder>
"""
import csv
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ortak import Kayit  # noqa: E402

from pqjose import composite, jws, openssl  # noqa: E402
from pqjose.keys import derive_key  # noqa: E402
from pqjose.params import COMPOSITE, MLDSA  # noqa: E402
from pqjose.util import b64_std_encode, b64u_encode, json_bytes  # noqa: E402
from pqjose.x509 import pem_to_der  # noqa: E402

P4_CNF = """[req]
distinguished_name=dn
prompt=no
[dn]
CN=pilot
[v3ca]
basicConstraints=critical,CA:TRUE
keyUsage=critical,keyCertSign,cRLSign
subjectKeyIdentifier=hash
[v3leaf]
basicConstraints=critical,CA:FALSE
keyUsage=critical,digitalSignature
authorityKeyIdentifier=keyid
subjectKeyIdentifier=hash
"""
NGINX = 8182
NODE = 16348


def serial20(label):
    h = hashlib.sha256(label.encode()).digest()[:20]
    return int.from_bytes(bytes([0x40 | (h[0] & 0x3F)]) + h[1:], 'big')


def p4_replica(alg_name, key):
    so = ['deterministic:1'] if alg_name.startswith('ML-DSA') else ['nonce-type:1']
    ca_pem = openssl.make_certificate('/C=EU/O=Pilot/CN=Pilot Issuer CA ' + alg_name, None, key.private_pem(), None,
                                      serial20('ca' + alg_name), '20260923190258Z', '20261023190258Z', P4_CNF, 'v3ca', so)
    leaf_key = derive_key(key.algs()[0] if alg_name.startswith('ML') else 'ES256', 't04/leaf/' + alg_name)
    leaf_pem = openssl.make_certificate('/C=EU/O=Pilot/CN=issuer.example', leaf_key.public_pem(), key.private_pem(), ca_pem,
                                        serial20('leaf' + alg_name), '20260923190258Z', '20261023190258Z', P4_CNF, 'v3leaf', so)
    return pem_to_der(ca_pem), pem_to_der(leaf_pem), leaf_key


def main(p4dir, out):
    K = Kayit('t04_sizes')
    p4 = {r['alg']: {k: int(v) for k, v in r.items() if k != 'alg'} for r in csv.DictReader(open(os.path.join(p4dir, 'mldsa_sizes.csv')))}
    tablo = []
    msg = open(os.path.join(p4dir, 'msg.txt'), 'rb').read()
    for alg_name, kind in (('ML-DSA-44', 'ML-DSA-44'), ('ML-DSA-65', 'ML-DSA-65'), ('ML-DSA-87', 'ML-DSA-87'), ('EC-P256', 'ES256')):
        k = derive_key(kind, 't04/ca/' + alg_name)
        spki = openssl.public_der_from_private(k.private_pem())
        if kind.startswith('ML'):
            from pqjose import mldsa
            sig = mldsa.sign(MLDSA[kind], k.seed, msg, deterministic=True)
        else:
            sig = openssl.dgst_sign(k.private_pem(), msg, 'sha256')
        ca, leaf, _ = p4_replica(alg_name, k)
        x5c_chars = len(b64_std_encode(leaf)) + len(b64_std_encode(ca))
        biz = {'spki_der_B': len(spki), 'sig_B': len(sig), 'ca_cert_der_B': len(ca), 'leaf_cert_der_B': len(leaf),
               'x5c_2certs_b64_chars': x5c_chars}
        ref = p4[alg_name]
        tol = 0 if kind.startswith('ML') else 2
        for m in biz:
            d = biz[m] - ref[m]
            tol_m = tol if m != 'x5c_2certs_b64_chars' else (0 if tol == 0 else 8)
            K.kontrol('P4:' + alg_name, m, abs(d) <= tol_m, {'biz': biz[m], 'P4': ref[m], 'fark': d})
        tablo.append(dict(alg=alg_name, **{m + '_biz': biz[m] for m in biz}, **{m + '_P4': ref[m] for m in biz}))

    # ---- JWS / JWK / composite / DPoP sizes
    payload = json_bytes({'iss': 'https://issuer.example', 'vct': 'urn:eudi:pid:1', 'iat': 1790000000})
    jws_tablo = []
    for alg in ('ES256', 'EdDSA') + tuple(MLDSA) + tuple(COMPOSITE):
        k = derive_key(alg, 't04/jws/' + alg)
        k.kid = k.thumbprint()
        c = jws.sign(payload, jws.Signer(k, {'kid': k.kid}, alg=alg), 'compact', deterministic=True)
        sig_len = len(jws.parse(c).signatures[0].signature)
        pj = len(json_bytes(k.public_jwk(kid=False)))
        dp_hdr = {'typ': 'dpop+jwt', 'alg': alg, 'jwk': k.public_jwk(kid=False)}
        dp_claims = {'jti': b64u_encode(hashlib.sha256(alg.encode()).digest()[:16]), 'htm': 'POST',
                     'htu': 'https://issuer.example/token', 'iat': 1790000000}
        dp = jws.sign(json_bytes(dp_claims), jws.Signer(k, dp_hdr, alg=alg), 'compact', deterministic=True)
        row = {'alg': alg, 'imza_B': sig_len, 'jwk_acik_json_B': pj, 'compact_jws_B': len(c), 'dpop_B': len(dp),
               'dpop>nginx(8182)': len(dp) > NGINX, 'dpop>node(16348)': len(dp) > NODE}
        if alg in COMPOSITE:
            ml, tr = composite.split_signature(alg, jws.parse(c).signatures[0].signature)
            row['composite_ml_B'] = len(ml)
            row['composite_trad_B'] = len(tr)
        jws_tablo.append(row)
        K.bilgi('JWS', alg, row)
    # expected fixed sizes (RFC 9964 Table 1 / FIPS 204)
    for r in jws_tablo:
        if r['alg'] in MLDSA:
            K.kontrol('FIPS204', r['alg'] + ' imza', r['imza_B'] == {44: 2420, 65: 3309, 87: 4627}[MLDSA[r['alg']]], r['imza_B'])
        if r['alg'] in COMPOSITE:
            p = COMPOSITE[r['alg']]
            ml_exp = {44: 2420, 65: 3309, 87: 4627}[p['ml']]
            tr_ok = (68 <= r['composite_trad_B'] <= 72) if p['crv'] == 'P-256' else \
                (100 <= r['composite_trad_B'] <= 104) if p['crv'] == 'P-384' else r['composite_trad_B'] == {'Ed25519': 64, 'Ed448': 114}[p['crv']]
            K.kontrol('-04 Tablo 1-2', r['alg'] + ' bilesen boyutlari', r['composite_ml_B'] == ml_exp and tr_ok,
                      [r['composite_ml_B'], r['composite_trad_B']])
    # CSV
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, 't04_p4_comparison.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(tablo[0].keys()))
        w.writeheader()
        w.writerows(tablo)
    keys_ = sorted({k for r in jws_tablo for k in r}, key=lambda x: (x != 'alg', x))
    with open(os.path.join(out, 't04_jws_sizes.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=keys_)
        w.writeheader()
        w.writerows(jws_tablo)
    return K.yaz(out, {'p4_tablo': tablo, 'jws_tablo': jws_tablo})


if __name__ == '__main__':
    o = main(sys.argv[1], sys.argv[2])
    sys.exit(0 if not o['kalan'] else 1)
