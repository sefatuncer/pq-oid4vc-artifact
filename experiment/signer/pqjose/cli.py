"""Komut satiri: python -m pqjose <komut> ...

  info                                         surumler
  keygen  --alg ALG [--label ETIKET] [--private]   JWK uret (etiket verilirse belirlenimci)
  sign    --key JWK --payload DOSYA [--alg ALG] [--serialization compact|flattened|general]
          [--key JWK2 ...] [--typ T] [--deterministic]
  verify  --jws DOSYA [--keys JWKS] [--anchors PEM ...] [--attime T] [--semantics all|any]
          [--required A,B] [--allowed A,B] [--pq-only-chain] [--embedded-jwk]
  thumbprint --key JWK
"""
import argparse
import json
import sys

from . import jws as J
from . import versions
from .keys import derive_key, key_from_jwk
from .params import ALL_ALGS
from .x509 import pem_to_der


def _load_json(path):
    with open(path, 'rb') as f:
        return json.loads(f.read().decode('utf-8'))


def main(argv=None):
    ap = argparse.ArgumentParser(prog='pqjose')
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('info')
    g = sub.add_parser('keygen')
    g.add_argument('--alg', required=True, choices=ALL_ALGS)
    g.add_argument('--label')
    g.add_argument('--private', action='store_true')
    s = sub.add_parser('sign')
    s.add_argument('--key', action='append', required=True)
    s.add_argument('--alg', action='append')
    s.add_argument('--payload', required=True)
    s.add_argument('--serialization', default='compact', choices=['compact', 'flattened', 'general'])
    s.add_argument('--typ')
    s.add_argument('--deterministic', action='store_true')
    v = sub.add_parser('verify')
    v.add_argument('--jws', required=True)
    v.add_argument('--keys')
    v.add_argument('--anchors', action='append')
    v.add_argument('--attime', type=int)
    v.add_argument('--semantics', default='all', choices=['all', 'any'])
    v.add_argument('--required')
    v.add_argument('--allowed')
    v.add_argument('--pq-only-chain', action='store_true')
    v.add_argument('--embedded-jwk', action='store_true')
    t = sub.add_parser('thumbprint')
    t.add_argument('--key', required=True)
    a = ap.parse_args(argv)

    if a.cmd == 'info':
        print(json.dumps(versions(), indent=1, ensure_ascii=False))
    elif a.cmd == 'keygen':
        if a.label:
            k = derive_key(a.alg, a.label)
        else:
            import os
            k = derive_key(a.alg, 'rastgele', ikm=os.urandom(32))
        print(json.dumps(k.private_jwk() if a.private else k.public_jwk(), indent=1))
    elif a.cmd == 'sign':
        keys = [key_from_jwk(_load_json(p)) for p in a.key]
        alg_list = a.alg or [None] * len(keys)
        signers = []
        for k, alg in zip(keys, alg_list):
            prot = {'typ': a.typ} if a.typ else {}
            if k.kid:
                prot['kid'] = k.kid
            signers.append(J.Signer(k, prot, alg=alg))
        with open(a.payload, 'rb') as f:
            pl = f.read()
        out = J.sign(pl, signers, a.serialization, a.deterministic)
        print(out if isinstance(out, str) else json.dumps(out))
    elif a.cmd == 'verify':
        with open(a.jws, 'rb') as f:
            data = f.read().decode('utf-8')
        pol = J.Policy(semantics=a.semantics)
        if a.keys:
            ks = _load_json(a.keys)
            pol.keys = [key_from_jwk(j) for j in (ks['keys'] if 'keys' in ks else [ks])]
        if a.anchors:
            pol.trust_anchors = [pem_to_der(open(p, 'rb').read()) for p in a.anchors]
            pol.attime = a.attime
        if a.required:
            pol.required_algs = frozenset(a.required.split(','))
        if a.allowed:
            pol.allowed_algs = frozenset(a.allowed.split(','))
        pol.x5c_pq_only = a.pq_only_chain
        pol.allow_embedded_jwk = a.embedded_jwk
        r = J.verify(data, pol)
        print(json.dumps(r.to_dict(), indent=1, ensure_ascii=False))
        return 0 if r.valid else 1
    elif a.cmd == 'thumbprint':
        print(key_from_jwk(_load_json(a.key)).thumbprint())
    return 0


if __name__ == '__main__':
    sys.exit(main())
