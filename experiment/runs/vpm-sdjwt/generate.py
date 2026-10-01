"""Pre-freeze SD-JWT-format validity vectors (V+ / V-) for the SD-JWT targets.

These vectors are NOT part of the measurement battery. They only check, before the pre-registration
is frozen, that an adapter drives its SD-JWT library correctly (a valid credential is accepted and a
credential with a corrupted issuer signature is rejected). They were added because the battery's
JWS-level V+/V- pair is not a well-formed SD-JWT VC for libraries that require `_sd_alg` or a
specific `typ`.

Keys are the battery's deterministic keys (same kids as keys/v1). Both typ values are produced
(dc+sd-jwt and the legacy vc+sd-jwt). One credential per algorithm: ES256, EdDSA, Ed25519, ML-DSA-65.

Run (from the repository root):
  docker run --rm -v "<repo>/experiment/vector-generator:/work:ro" -v "<repo>/experiment/runs/vpm-sdjwt:/out" \
      pq-a09-credgen:1.3 python /out/generate.py /out
"""
import hashlib
import json
import os
import sys

sys.path.insert(0, '/work')
from uretec import artefakt as A          # noqa: E402
from uretec.anahtar import AnahtarSeti    # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
ALGS = [('ES256', 'issuer/ES256', 'tedavi-ML-DSA-65'), ('EdDSA', 'issuer/EdDSA', 'kontrol-EdDSA'),
        ('Ed25519', 'issuer/EdDSA', 'kontrol-Ed25519'), ('ML-DSA-65', 'issuer/ML-DSA-65', 'tedavi-ML-DSA-65')]
TYPS = [('DC', 'dc+sd-jwt'), ('VC', 'vc+sd-jwt')]


def corrupt_issuer_signature(sdjwt):
    """Flip one bit in the middle of the issuer JWS signature; disclosures and payload are unchanged."""
    jwt, rest = sdjwt.split('~', 1)
    h, p, s = jwt.split('.')
    i = len(s) // 2
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
    c = alphabet[(alphabet.index(s[i]) ^ 1)]
    return '.'.join((h, p, s[:i] + c + s[i + 1:])) + '~' + rest


def main():
    S = AnahtarSeti()
    holder = S['holder/ES256'].public_jwk(kid=False)
    vdir = os.path.join(OUT, 'vectors')
    os.makedirs(vdir, exist_ok=True)
    jobs, manifest = [], []
    for typ_tag, typ in TYPS:
        for alg, role, arm in ALGS:
            label = alg.replace('ML-DSA-65', 'MLDSA65')
            vc = A.issue_vc('VPM-SD-%s-%s' % (typ_tag, label), [(S[role], alg, None)], holder, typ=typ)
            for sign, obj in (('PLUS', vc['obj']), ('MINUS', corrupt_issuer_signature(vc['obj']))):
                vid = 'VPM-SD%s_%s_%s' % (typ_tag, sign, label)
                name = vid + '.sdjwt'
                data = obj.encode('ascii')
                open(os.path.join(vdir, name), 'wb').write(data)
                pub = S[role].public_jwk(kid=True)
                manifest.append({'id': vid, 'dosya': 'vpm-sdjwt/' + name, 'sha256': hashlib.sha256(data).hexdigest(),
                                 'typ': typ, 'alg': alg, 'gecerli': sign == 'PLUS',
                                 # same schema as the battery manifest's verification inputs
                                 'dogrulama_girdileri': {'jwks': 'anahtarlar/v1/acik-jwks.json', 'kid': [pub['kid']],
                                                         'jwk': pub, 'simdi': 1790003700}})
                jobs.append({'algler': alg, 'artefakt': 'sd-jwt-vc', 'dosya': 'vpm-sdjwt/' + name, 'kol': arm,
                             'politika': 'GEC', 'serilestirme': 'sd-jwt-compact', 'vektor_id': vid})
    # 'vektorler' is the battery manifest's key name, so adapters can load this file with the same code
    json.dump({'purpose': 'pre-freeze SD-JWT validity vectors (not part of the battery)', 'vektorler': manifest},
              open(os.path.join(vdir, 'MANIFEST.json'), 'w'), indent=1)
    with open(os.path.join(OUT, 'jobs_prefreeze_V_sdjwt.jsonl'), 'w', newline='\n') as f:
        for j in jobs:
            f.write(json.dumps(j, sort_keys=True) + '\n')
    print(len(manifest), 'vectors')


if __name__ == '__main__':
    main()
