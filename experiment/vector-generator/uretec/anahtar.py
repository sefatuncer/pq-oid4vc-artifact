"""v1 key roles and test PKI (fully deterministic).

Key: pqjose.keys.derive_key(kind, 'v1/<role>') — HKDF-SHA256, fixed IKM. Same label -> same key.
Certificate: pqjose.pki (fixed serial number, fixed validity 2026-01-01..2036-12-31, deterministic signature).

PKI (HAIP 1.0: x5c = [leaf, intermediate CA]; the root is NOT put into x5c; the signing certificate is NOT self-signed):
  root-ec  (P-256, self-signed)               root-ml (ML-DSA-65, self-signed)
  int-ec   (P-256, signed by root-ec)         int-ml  (ML-DSA-65, signed by root-ml)
  int-ml-rootec (ML-DSA-65 key, signed by root-ec)   <- PQ intermediate CA / classical root (mixed root link)
  Leaves: issuer-ec@int-ec, issuer-ml@int-ml, issuer-ml@int-ec (mixed), issuer-ec@int-ml (mixed),
             issuer-ml@int-ml-rootec (mixed root), status-ec@int-ec, status-ml@int-ml,
             rp-ec@int-ec, rp-ml@int-ml  (SAN: DNS issuer.example / verifier.example)
Composite X.509 (LAMPS): not in OpenSSL 3.5 -> composite keys are resolved with kid/JWKS.
"""
from pqjose import pki
from pqjose.keys import derive_key
from pqjose.params import COMPOSITE, MLDSA

SUBJ = '/C=EU/O=PQ-OID4VC Test PKI v1/CN='

# role -> key type
ROLLER = {
    # issuer (signs the credential)
    'issuer/ES256': 'ES256', 'issuer/ES384': 'ES384', 'issuer/EdDSA': 'EdDSA', 'issuer/Ed448': 'Ed448',
    **{'issuer/' + a: a for a in MLDSA}, **{'issuer/' + a: a for a in COMPOSITE},
    # signs the status list
    'status/ES256': 'ES256', 'status/ML-DSA-65': 'ML-DSA-65', 'status/ML-DSA-65-ES256': 'ML-DSA-65-ES256',
    # verifier (RP), signs the request object
    'rp/ES256': 'ES256', 'rp/ML-DSA-65': 'ML-DSA-65', 'rp/ML-DSA-65-ES256': 'ML-DSA-65-ES256',
    'rp/enc': 'ES256',   # ECDH-ES P-256 response encryption key (only the public JWK is used)
    # user (holder) — cnf.jwk and KB-JWT
    'holder/ES256': 'ES256', 'holder/ML-DSA-65': 'ML-DSA-65', 'holder/ML-DSA-65-ES256': 'ML-DSA-65-ES256',
    # DPoP
    **{'dpop/' + a: a for a in ('ES256', 'EdDSA') + tuple(MLDSA) + tuple(COMPOSITE)},
    # CA keys
    'ca/root-ec': 'ES256', 'ca/root-ml': 'ML-DSA-65', 'ca/int-ec': 'ES256', 'ca/int-ml': 'ML-DSA-65',
    'ca/int-ml-rootec': 'ML-DSA-65',
}


class AnahtarSeti:
    def __init__(self):
        self.k = {}
        for rol, tur in ROLLER.items():
            key = derive_key(tur, 'v1/' + rol)
            key.kid = key.thumbprint()
            self.k[rol] = key
        self.certs = {}
        self._pki()

    def __getitem__(self, rol):
        return self.k[rol]

    def _pki(self):
        c = self.certs
        c['root-ec'] = pki.make_root('root-ec', self.k['ca/root-ec'], SUBJ + 'Root CA EC-P256', 1)
        c['root-ml'] = pki.make_root('root-ml', self.k['ca/root-ml'], SUBJ + 'Root CA ML-DSA-65', 2)
        c['int-ec'] = pki.make_cert('int-ec', self.k['ca/int-ec'], c['root-ec'], SUBJ + 'Issuing CA EC-P256', 11, 'int')
        c['int-ml'] = pki.make_cert('int-ml', self.k['ca/int-ml'], c['root-ml'], SUBJ + 'Issuing CA ML-DSA-65', 12, 'int')
        c['int-ml-rootec'] = pki.make_cert('int-ml-rootec', self.k['ca/int-ml-rootec'], c['root-ec'],
                                           SUBJ + 'Issuing CA ML-DSA-65 (EC root)', 13, 'int')
        iss = ['issuer.example']
        rp = ['verifier.example']
        leaves = [
            ('issuer-ec@int-ec', 'issuer/ES256', 'int-ec', 'PID Issuer (EC)', iss),
            ('issuer-ml@int-ml', 'issuer/ML-DSA-65', 'int-ml', 'PID Issuer (ML-DSA-65)', iss),
            ('issuer-ml@int-ec', 'issuer/ML-DSA-65', 'int-ec', 'PID Issuer (ML-DSA-65, EC CA)', iss),
            ('issuer-ec@int-ml', 'issuer/ES256', 'int-ml', 'PID Issuer (EC, ML-DSA CA)', iss),
            ('issuer-ml@int-ml-rootec', 'issuer/ML-DSA-65', 'int-ml-rootec', 'PID Issuer (ML-DSA-65, EC root)', iss),
            ('status-ec@int-ec', 'status/ES256', 'int-ec', 'Status List Signer (EC)', iss),
            ('status-ml@int-ml', 'status/ML-DSA-65', 'int-ml', 'Status List Signer (ML-DSA-65)', iss),
            ('rp-ec@int-ec', 'rp/ES256', 'int-ec', 'Relying Party (EC)', rp),
            ('rp-ml@int-ml', 'rp/ML-DSA-65', 'int-ml', 'Relying Party (ML-DSA-65)', rp),
        ]
        for i, (name, rol, issuer, cn, san) in enumerate(leaves):
            c[name] = pki.make_cert(name, self.k[rol], c[issuer], SUBJ + cn, 100 + i, 'leaf', san_dns=san)

    def x5c(self, leaf):
        """HAIP: [leaf, intermediate CA] (without the root)."""
        c = self.certs[leaf]
        return pki.x5c(c, c.issuer)

    def anchors(self):
        return [self.certs['root-ec'].der, self.certs['root-ml'].der]

    def public_jwks(self, roller=None):
        roller = roller or list(self.k)
        return {'keys': [self.k[r].public_jwk() for r in roller]}
