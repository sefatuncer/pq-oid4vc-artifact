#!/usr/bin/env python3
"""T02 — OpenSSL cross-verification (both directions) + independent implementation (dilithium-py).

pqjose's crypto path: cryptography 50.0.1 (embedded OpenSSL 4.0.2).
Cross-verifier        : system OpenSSL 3.5.7 CLI (separate version, separate process).
Third implementation  : dilithium-py 1.4.0 (pure Python FIPS 204; independent of the OpenSSL code base).

Directions:
  O1  pqjose signs     -> OpenSSL verifies    (on the JWS signing input)
  O2  OpenSSL signs    -> pqjose verifies     (placed into a JWS, full JWS verification)
  O3  key from seed: OpenSSL genpkey == cryptography == dilithium-py
  O4  composite -04: the COMPONENTS of the pqjose signature with OpenSSL; a composite signature built from
      OpenSSL components with pqjose
  O5  X.509: in the ML-DSA/mixed chains produced by OpenSSL the certificate signatures are also verified with
      cryptography (OpenSSL 4.0.2)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ortak import Kayit  # noqa: E402

from dilithium_py.ml_dsa import ML_DSA_44, ML_DSA_65, ML_DSA_87  # noqa: E402

from pqjose import composite, der, jws, openssl, pki  # noqa: E402
from pqjose import mldsa as M  # noqa: E402
from pqjose.keys import derive_key  # noqa: E402
from pqjose.params import COMPOSITE, MLDSA  # noqa: E402
from pqjose.util import b64u_encode, json_bytes  # noqa: E402

DPY = {44: ML_DSA_44, 65: ML_DSA_65, 87: ML_DSA_87}
PAYLOAD = json_bytes({'iss': 'https://issuer.example', 'vct': 'urn:eudi:pid:1', 'iat': 1790000000})


def tbs_for(alg, kid):
    pb64 = b64u_encode(json_bytes({'alg': alg, 'kid': kid}))
    return pb64, (pb64 + '.' + b64u_encode(PAYLOAD)).encode()


def compact(pb64, sig):
    return pb64 + '.' + b64u_encode(PAYLOAD) + '.' + b64u_encode(sig)


def main(out):
    K = Kayit('t02_openssl_cross')
    sayac = {'openssl': [0, 0], 'dilithium-py': [0, 0]}

    def ks(grup, ad, kosul, kim='openssl', ayrinti=None):
        sayac[kim][1] += 1
        if K.kontrol(grup, ad, kosul, ayrinti):
            sayac[kim][0] += 1

    # ---------------- ML-DSA (RFC 9964)
    for alg, lvl in MLDSA.items():
        k = derive_key(alg, 't02/' + alg)
        k.kid = k.thumbprint()
        pol = jws.Policy(keys=[k.public_only()], required_algs=frozenset({alg}))
        pb64, tbs = tbs_for(alg, k.kid)
        # O3 key derivation
        ossl_pub = openssl.public_der_from_private(openssl.mldsa_private_pem(lvl, k.seed))
        ks(alg, 'O3:openssl-genpkey(hexseed)-acik-anahtar==pqjose', ossl_pub[-M.pk_len(lvl):] == k.pub)
        ks(alg, 'O3:dilithium-py-key_derive==pqjose', DPY[lvl].key_derive(k.seed)[0] == k.pub, 'dilithium-py')
        # O1 pqjose (hedged) -> OpenSSL
        s1 = M.sign(lvl, k.seed, tbs, b'', deterministic=False)
        ks(alg, 'O1:pqjose(hedged)->openssl-dogrular', openssl.pkey_verify(k.public_pem(), tbs, s1))
        ks(alg, 'O1b:pqjose(hedged)->dilithium-py-dogrular', DPY[lvl].verify(k.pub, tbs, s1), 'dilithium-py')
        # O2 OpenSSL (hedged) -> pqjose full JWS
        s2 = openssl.mldsa_sign(lvl, k.seed, tbs, deterministic=False)
        r = jws.verify(compact(pb64, s2), pol)
        ks(alg, 'O2:openssl(hedged)->pqjose-JWS-kabul', r.valid, ayrinti=r.reason)
        # O2b dilithium-py -> pqjose
        s3 = DPY[lvl].sign(DPY[lvl].key_derive(k.seed)[1], tbs)
        r = jws.verify(compact(pb64, s3), pol)
        ks(alg, 'O2b:dilithium-py(hedged)->pqjose-JWS-kabul', r.valid, 'dilithium-py', r.reason)
        # deterministic path: OpenSSL(deterministic) == dilithium-py(deterministic)
        sd = M.sign(lvl, k.seed, tbs, b'', deterministic=True)
        ks(alg, 'belirlenimci:openssl==dilithium-py', sd == DPY[lvl].sign(DPY[lvl].key_derive(k.seed)[1], tbs,
                                                                         deterministic=True), 'dilithium-py')
        # end to end: pqjose.sign (hedged) compact -> OpenSSL
        c = jws.sign(PAYLOAD, jws.Signer(k, {'kid': k.kid}), 'compact')
        p = jws.parse(c)
        ks(alg, 'O1c:pqjose.sign(compact)->openssl', openssl.pkey_verify(k.public_pem(), p.signing_input(p.signatures[0]),
                                                                        p.signatures[0].signature))

    # ---------------- Classical control arm
    for alg in ('ES256', 'ES384', 'EdDSA', 'Ed448'):
        k = derive_key(alg, 't02/' + alg)
        k.kid = k.thumbprint()
        pol = jws.Policy(keys=[k.public_only()], required_algs=frozenset({alg}))
        pb64, tbs = tbs_for(alg, k.kid)
        c = jws.sign(PAYLOAD, jws.Signer(k, {'kid': k.kid}, alg=alg), 'compact')
        p = jws.parse(c)
        e = p.signatures[0]
        if alg.startswith('ES'):
            md = 'sha256' if alg == 'ES256' else 'sha384'
            crv = 'P-256' if alg == 'ES256' else 'P-384'
            ks(alg, 'O1:pqjose->openssl(ham r||s -> DER)', openssl.dgst_verify(k.public_pem(), p.signing_input(e),
                                                                             der.ecdsa_raw_to_der(e.signature, crv), md))
            sig = der.ecdsa_der_to_raw(openssl.dgst_sign(k.private_pem(), tbs, md), crv)
        else:
            ks(alg, 'O1:pqjose->openssl', openssl.pkey_verify(k.public_pem(), p.signing_input(e), e.signature))
            sig = openssl.pkey_sign_raw(k.private_pem(), tbs)
        r = jws.verify(compact(pb64, sig), pol)
        ks(alg, 'O2:openssl->pqjose-JWS-kabul', r.valid, ayrinti=r.reason)

    # ---------------- Composite -04
    for alg, prm in COMPOSITE.items():
        k = derive_key(alg, 't02/' + alg)
        k.kid = k.thumbprint()
        pol = jws.Policy(keys=[k.public_only()], required_algs=frozenset({alg}))
        pb64, tbs = tbs_for(alg, k.kid)
        mp = composite.message_representative(alg, tbs)
        # O4a: pqjose composite -> components with OpenSSL
        s = composite.sign(alg, k, tbs, deterministic=False)
        ml_sig, tr_sig = composite.split_signature(alg, s)
        ks(alg, 'O4a:ML-DSA-bileseni(ctx=Label)->openssl', openssl.pkey_verify(k.ml.public_pem(), mp, ml_sig, ctx=prm['label']))
        if prm['trad'] == 'ECDSA':
            ks(alg, 'O4a:ECDSA-bileseni(DER)->openssl', openssl.dgst_verify(k.trad.public_pem(), mp, tr_sig, prm['md']))
        else:
            ks(alg, 'O4a:EdDSA-bileseni->openssl', openssl.pkey_verify(k.trad.public_pem(), mp, tr_sig))
        ks(alg, 'O4a:ML-DSA-bileseni->dilithium-py', DPY[prm['ml']].verify(k.ml.pub, mp, ml_sig, ctx=prm['label']),
           'dilithium-py')
        # O4b: OpenSSL components -> pqjose
        o_ml = openssl.mldsa_sign(prm['ml'], k.ml.seed, mp, ctx=prm['label'], deterministic=False)
        if prm['trad'] == 'ECDSA':
            o_tr = openssl.dgst_sign(k.trad.private_pem(), mp, prm['md'], deterministic=False)
            o_tr = der.ecdsa_raw_to_der(der.ecdsa_der_to_raw(o_tr, prm['crv']), prm['crv'])
        else:
            o_tr = openssl.pkey_sign_raw(k.trad.private_pem(), mp)
        r = jws.verify(compact(pb64, o_ml + o_tr), pol)
        ks(alg, 'O4b:openssl-bilesenleri->pqjose-composite-JWS-kabul', r.valid, ayrinti=r.reason)
        # deterministic composite: two runs byte-identical
        d1 = composite.sign(alg, k, tbs, deterministic=True)
        d2 = composite.sign(alg, k, tbs, deterministic=True)
        K.kontrol(alg, 'belirlenimci-composite-tekrar-ayni', d1 == d2)

    # ---------------- O5: X.509 (OpenSSL produces; cryptography verifies too)
    root_ec = pki.make_root('root-ec', derive_key('ES256', 't02/root-ec'), '/C=EU/O=T02/CN=Root EC', 1)
    root_ml = pki.make_root('root-ml', derive_key('ML-DSA-65', 't02/root-ml'), '/C=EU/O=T02/CN=Root ML', 2)
    int_ml = pki.make_cert('int-ml', derive_key('ML-DSA-65', 't02/int-ml'), root_ml, '/C=EU/O=T02/CN=Int ML', 3, 'int')
    int_ec = pki.make_cert('int-ec', derive_key('ES256', 't02/int-ec'), root_ec, '/C=EU/O=T02/CN=Int EC', 4, 'int')
    leaf_ec_ml = pki.make_cert('leaf-ec@int-ml', derive_key('ES256', 't02/leaf1'), int_ml, '/C=EU/O=T02/CN=L1', 5,
                               san_dns=['issuer.example'])
    leaf_ml_ec = pki.make_cert('leaf-ml@int-ec', derive_key('ML-DSA-65', 't02/leaf2'), int_ec, '/C=EU/O=T02/CN=L2', 6,
                               san_dns=['issuer.example'])
    from cryptography import x509 as cx
    for child, parent in ((int_ml, root_ml), (leaf_ec_ml, int_ml), (int_ec, root_ec), (leaf_ml_ec, int_ec)):
        c = cx.load_der_x509_certificate(child.der)
        pcert = cx.load_der_x509_certificate(parent.der)
        try:
            c.verify_directly_issued_by(pcert)
            ok = True
            err = None
        except Exception as ex:  # noqa: BLE001
            ok, err = False, repr(ex)
        ks('X.509', 'O5:%s<-%s cryptography-dogrular' % (child.name, parent.name), ok, ayrinti=err)
    for leaf, inter, root in ((leaf_ec_ml, int_ml, root_ml), (leaf_ml_ec, int_ec, root_ec)):
        ok, outp = openssl.verify_chain(leaf.der, [inter.der], [root.der], pki.ATTIME)
        ks('X.509', 'O5:openssl-verify %s' % leaf.name, ok, ayrinti=outp)

    K.bilgi('genel', 'sayac', {k: '%d/%d' % tuple(v) for k, v in sayac.items()})
    return K.yaz(out, {'capraz_sayac': {k: {'gecen': v[0], 'toplam': v[1]} for k, v in sayac.items()}})


if __name__ == '__main__':
    o = main(sys.argv[1])
    sys.exit(0 if not o['kalan'] else 1)
