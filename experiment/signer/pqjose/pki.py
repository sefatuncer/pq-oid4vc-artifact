"""Belirlenimci test PKI'si (OpenSSL CLI).

* Tum sertifikalar sabit seri no ve sabit gecerlilik (2026-01-01 .. 2036-12-31) ile uretilir.
* Imzalar belirlenimci: ECDSA -> RFC 6979 (nonce-type:1), ML-DSA -> deterministic:1, EdDSA dogal.
  Ayni anahtarlar -> bayt-bayt ayni sertifikalar.
* HAIP 1.0 6.1.1 / 5: x5c guven capasini (kok) ICERMEZ; imzalayan sertifika kendinden imzali olmaz.
* Composite X.509 (draft-ietf-lamps-pq-composite-sigs-19): OpenSSL 3.5'te yok -> kapsam disi.
"""
from dataclasses import dataclass

from . import openssl
from .keys import ECKey, MLDSAKey, OKPKey
from .x509 import pem_to_der

NOT_BEFORE = '20260101000000Z'
NOT_AFTER = '20361231235959Z'
ATTIME = 1790000000  # 2026-09-21: dogrulama anlik zamani (gecerlilik penceresi icinde)

_CNF = """[req]
distinguished_name=dn
prompt=no
[dn]
CN=unused
[v3_root]
basicConstraints=critical,CA:TRUE
keyUsage=critical,keyCertSign,cRLSign
subjectKeyIdentifier=hash
[v3_int]
basicConstraints=critical,CA:TRUE,pathlen:0
keyUsage=critical,keyCertSign,cRLSign
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid
[v3_leaf]
basicConstraints=critical,CA:FALSE
keyUsage=critical,digitalSignature
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid
{san}
"""


@dataclass
class Cert:
    name: str
    key: object
    pem: bytes
    der: bytes
    issuer: object = None

    @property
    def x5c_b64(self):
        from .util import b64_std_encode
        return b64_std_encode(self.der)


def sigopts(issuer_key):
    if isinstance(issuer_key, ECKey):
        return ['nonce-type:1']
    if isinstance(issuer_key, MLDSAKey):
        return ['deterministic:1']
    if isinstance(issuer_key, OKPKey):
        return []
    raise ValueError('sertifika imzalayan anahtar tipi desteklenmiyor (composite X.509 kapsam disi)')


def _cnf(san_dns=None):
    return _CNF.format(san=('subjectAltName=' + ','.join('DNS:' + d for d in san_dns)) if san_dns else '')


def make_root(name, key, subject, serial) -> Cert:
    pem = openssl.make_certificate(subject, None, key.private_pem(), None, serial, NOT_BEFORE, NOT_AFTER,
                                   _cnf(), 'v3_root', sigopts(key))
    return Cert(name, key, pem, pem_to_der(pem), None)


def make_cert(name, key, issuer: Cert, subject, serial, profile='leaf', san_dns=None) -> Cert:
    pem = openssl.make_certificate(subject, key.public_pem(), issuer.key.private_pem(), issuer.pem, serial,
                                   NOT_BEFORE, NOT_AFTER, _cnf(san_dns), 'v3_' + profile, sigopts(issuer.key))
    return Cert(name, key, pem, pem_to_der(pem), issuer)


def x5c(*certs):
    return [c.x5c_b64 for c in certs]
