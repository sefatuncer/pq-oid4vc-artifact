#!/usr/bin/env python3
"""T01 — External test vectors: RFC 9964 Appendix A (ML-DSA) and draft-ietf-jose-pq-composite-sigs-04 Appendix A.1.

Checks:
  (a) our verifier VERIFIES all vectors
  (b) deterministic components: public key from seed, JWK/priv serialization, kid (RFC 7638), M',
      EdDSA component, (if deterministic) ML-DSA signature — our generator produces byte-identical output
  (c) independent implementations: system OpenSSL 3.5.7 CLI and dilithium-py (pure Python FIPS 204)
Usage: python t01_dis_vektorler.py <external-vectors folder> <result folder>
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ortak import Kayit  # noqa: E402

from dilithium_py.ml_dsa import ML_DSA_44, ML_DSA_65, ML_DSA_87  # noqa: E402

from pqjose import algs, composite, jws, openssl  # noqa: E402
from pqjose import mldsa as M  # noqa: E402
from pqjose.der import ec_private_key_encode  # noqa: E402
from pqjose.keys import CompositeKey, ECKey, MLDSAKey, OKPKey, key_from_jwk  # noqa: E402
from pqjose.params import COMPOSITE  # noqa: E402
from pqjose.util import b64u_decode, b64u_encode, json_bytes  # noqa: E402

DPY = {44: ML_DSA_44, 65: ML_DSA_65, 87: ML_DSA_87}


def rfc9964(v, K):
    o = v['veri']
    g = v['id']
    seed = bytes.fromhex(o['priv'])
    tbs = bytes.fromhex(o['raw_to_be_signed'])
    sig = bytes.fromhex(o['raw_signature'])
    pk = bytes.fromhex(o['raw_public_key'])
    lvl = {'44': 44, '65': 65, '87': 87}[g[-2:]]
    alg = 'ML-DSA-%d' % lvl
    k = MLDSAKey(alg, seed=seed)
    K.kontrol(g, 'tohumdan-acik-anahtar', k.pub == pk)
    K.kontrol(g, 'imza-dogrulama(ham)', M.verify(lvl, pk, tbs, sig))
    det = M.sign(lvl, seed, tbs, b'', deterministic=True)
    K.kontrol(g, 'belirlenimci-imza-bayt-ayni', det == sig)
    # independent: dilithium-py
    dpk, dsk = DPY[lvl].key_derive(seed)
    K.kontrol(g, 'dilithium-py:acik-anahtar', dpk == pk)
    K.kontrol(g, 'dilithium-py:dogrulama', DPY[lvl].verify(pk, tbs, sig))
    K.kontrol(g, 'dilithium-py:belirlenimci-imza-ayni', DPY[lvl].sign(dsk, tbs, deterministic=True) == sig)
    # independent: OpenSSL CLI
    K.kontrol(g, 'openssl:dogrulama', openssl.pkey_verify(k.public_pem(), tbs, sig))
    if 'jwk' in o:
        j = o['jwk']
        kj = key_from_jwk(j)
        K.kontrol(g, 'jwk-ice-aktarma', isinstance(kj, MLDSAKey) and kj.pub == pk and kj.seed == seed)
        K.kontrol(g, 'kid==RFC7638-parmak-izi', kj.thumbprint() == j['kid'])
        K.kontrol(g, 'jwk-disa-aktarma-ayni', k.private_jwk(kid=False) == {m: j[m] for m in ('kty', 'alg', 'pub', 'priv')})
        o_jws = jws.parse(o['jws'])
        e = o_jws.signatures[0]
        K.kontrol(g, 'jws-imzalama-girdisi==raw_to_be_signed', o_jws.signing_input(e) == tbs)
        pol = jws.Policy(keys=[kj.public_only()], allowed_algs=frozenset({alg}), required_algs=frozenset({alg}))
        r = jws.verify(o['jws'], pol)
        K.kontrol(g, 'pqjose-dogrulayici:KABUL', r.valid, r.to_dict())
        # generator: rebuild the same header and sign deterministically -> JWS byte-identical
        prot = {'alg': alg, 'kid': j['kid']}
        K.kontrol(g, 'baslik-serilestirme-ayni', b64u_encode(json_bytes(prot)) == e.protected_b64)
        k.kid = j['kid']
        out = jws.sign(o_jws.payload, jws.Signer(k, prot), 'compact', deterministic=True)
        K.kontrol(g, 'uretici:compact-JWS-bayt-ayni', out == o['jws'])


def josecomp(v, K):
    o = v['veri']
    g = v['id']
    j = o['jwk']
    alg = j['alg']
    p = COMPOSITE[alg]
    seed = bytes.fromhex(o['mldsa_seed'])
    tbs = bytes.fromhex(o['raw_to_be_signed'])
    mp = bytes.fromhex(o['raw_message_representative'])
    sig = bytes.fromhex(o['raw_composite_signature'])
    pk = bytes.fromhex(o['raw_composite_public_key'])
    ml = MLDSAKey('ML-DSA-%d' % p['ml'], seed=seed)
    if p['trad'] == 'ECDSA':
        d = int(o['ecdsa_d'], 16)
        trad = ECKey.from_d(p['crv'], d)
    else:
        trad = OKPKey(p['crv'], priv_raw=bytes.fromhex(o['eddsa_seed']))
    k = CompositeKey(alg, ml, trad)
    K.kontrol(g, 'bilesenlerden-composite-acik-anahtar', k.pub == pk)
    K.kontrol(g, 'composite-priv-serilestirme==jwk.priv', b64u_encode(k.priv) == j['priv'])
    if p['trad'] == 'ECDSA':
        K.kontrol(g, 'ECPrivateKey(Tablo4)', k.priv[32:] == ec_private_key_encode(trad.d_bytes(), p['crv']))
    kj = key_from_jwk(j)
    K.kontrol(g, 'jwk-ice-aktarma', isinstance(kj, CompositeKey) and kj.pub == pk and kj.priv == k.priv)
    K.kontrol(g, 'kid==RFC7638-parmak-izi', kj.thumbprint() == j['kid'])
    K.kontrol(g, 'jwk-disa-aktarma-ayni', k.private_jwk(kid=False) == {m: j[m] for m in ('kty', 'alg', 'pub', 'priv')})
    o_jws = jws.parse(o['jws'])
    e = o_jws.signatures[0]
    K.kontrol(g, 'jws-imzalama-girdisi==raw_to_be_signed', o_jws.signing_input(e) == tbs)
    K.kontrol(g, 'jws-imza==raw_composite_signature', e.signature == sig)
    K.kontrol(g, "M'==raw_message_representative", composite.message_representative(alg, tbs) == mp)
    pol = jws.Policy(keys=[kj.public_only()], allowed_algs=frozenset({alg}), required_algs=frozenset({alg}))
    r = jws.verify(o['jws'], pol)
    K.kontrol(g, 'pqjose-dogrulayici:KABUL', r.valid, r.to_dict())
    comp = composite.verify_components(alg, kj, tbs, sig)
    K.kontrol(g, 'bilesenler:ml=True,trad=True', comp['ml'] and comp['trad'], comp)
    ml_sig, trad_sig = composite.split_signature(alg, sig)
    K.bilgi(g, 'boyutlar', {'imza': len(sig), 'ml': len(ml_sig), 'trad': len(trad_sig), 'pub': len(pk),
                            'priv': len(k.priv), "M'": len(mp)})
    # deterministic components
    det_ml = M.sign(p['ml'], seed, mp, ctx=p['label'], deterministic=True)
    K.bilgi(g, 'ML-DSA-bileseni-belirlenimci-mi(taslak)', det_ml == ml_sig)
    if p['trad'] == 'EdDSA':
        K.kontrol(g, 'EdDSA-bileseni-bayt-ayni(belirlenimci)', trad.priv.sign(mp) == trad_sig)
    else:
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import ec
        md = {'sha256': hashes.SHA256, 'sha384': hashes.SHA384}[p['md']]()
        d6979 = trad.priv.sign(mp, ec.ECDSA(md, deterministic_signing=True))
        K.bilgi(g, 'ECDSA-bileseni-RFC6979-mi(taslak)', d6979 == trad_sig)
    # our generator: deterministic composite signature -> our verifier + independent verifiers
    ours = composite.sign(alg, k, tbs, deterministic=True)
    K.kontrol(g, 'uretici:belirlenimci-imza-dogrulanir', composite.verify(alg, kj, tbs, ours))
    if det_ml == ml_sig and (p['trad'] == 'EdDSA'):
        K.kontrol(g, 'uretici:composite-imza-bayt-ayni', ours == sig)
    # independent verifiers (per component)
    K.kontrol(g, 'dilithium-py:ML-DSA-bileseni(ctx=Label)', DPY[p['ml']].verify(ml.pub, mp, ml_sig, ctx=p['label']))
    K.kontrol(g, 'openssl:ML-DSA-bileseni(ctx=Label)', openssl.pkey_verify(ml.public_pem(), mp, ml_sig, ctx=p['label']))
    if p['trad'] == 'ECDSA':
        K.kontrol(g, 'openssl:ECDSA-bileseni(DER,M\')', openssl.dgst_verify(trad.public_pem(), mp, trad_sig, p['md']))
    else:
        K.kontrol(g, 'openssl:EdDSA-bileseni(M\')', openssl.pkey_verify(trad.public_pem(), mp, trad_sig))


def main(src, out):
    K = Kayit('t01_dis_vektorler')
    files = sorted(glob.glob(os.path.join(src, '*.json')))
    n = 0
    for f in files:
        if os.path.basename(f).startswith('00-'):
            continue
        v = json.load(open(f, encoding='utf-8'))
        n += 1
        if v['kaynak'] == 'RFC9964':
            rfc9964(v, K)
        else:
            josecomp(v, K)
    K.bilgi('genel', 'vektor-sayisi', n)
    return K.yaz(out)


if __name__ == '__main__':
    o = main(sys.argv[1], sys.argv[2])
    sys.exit(0 if not o['kalan'] else 1)
