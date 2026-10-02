"""x5c (RFC 7515 4.1.6) operations: decoding, chain validation (OpenSSL CLI), chain class.

* x5c values are standard base64 DER (not base64url).
* Chain validation is done with the system OpenSSL (supports ML-DSA-signed certificates).
* Chain class: the classical/pq class of every link (leaf key + the signature of every certificate in x5c);
  a 'karisik' (mixed) chain = at least one classical and at least one PQ link.
* Composite X.509 (draft-ietf-lamps-pq-composite-sigs) is not in OpenSSL 3.5 -> OUT OF SCOPE.
"""
from dataclasses import dataclass, field

from cryptography import x509 as cx509
from cryptography.hazmat.primitives import serialization

from . import openssl
from .keys import key_from_public_object
from .util import FormatError, b64_std_decode, b64u_encode, sha256

SIG_OIDS = {
    '1.2.840.10045.4.3.2': ('ecdsa-with-SHA256', 'klasik'),
    '1.2.840.10045.4.3.3': ('ecdsa-with-SHA384', 'klasik'),
    '1.2.840.10045.4.3.4': ('ecdsa-with-SHA512', 'klasik'),
    '1.2.840.113549.1.1.11': ('sha256WithRSAEncryption', 'klasik'),
    '1.2.840.113549.1.1.12': ('sha384WithRSAEncryption', 'klasik'),
    '1.2.840.113549.1.1.13': ('sha512WithRSAEncryption', 'klasik'),
    '1.2.840.113549.1.1.10': ('RSASSA-PSS', 'klasik'),
    '1.3.101.112': ('Ed25519', 'klasik'),
    '1.3.101.113': ('Ed448', 'klasik'),
    '2.16.840.1.101.3.4.3.17': ('ML-DSA-44', 'pq'),
    '2.16.840.1.101.3.4.3.18': ('ML-DSA-65', 'pq'),
    '2.16.840.1.101.3.4.3.19': ('ML-DSA-87', 'pq'),
}


def key_class_of(obj) -> str:
    n = type(obj).__name__
    if n.startswith('MLDSA'):
        return 'pq'
    return 'klasik'


def x509_hash(der: bytes) -> str:
    """OID4VP 5.9.3: base64url(SHA-256(DER yaprak sertifika))."""
    return b64u_encode(sha256(der))


def cert_info(der: bytes) -> dict:
    c = cx509.load_der_x509_certificate(der)
    oid = c.signature_algorithm_oid.dotted_string
    name, cls = SIG_OIDS.get(oid, (oid, 'bilinmiyor'))
    try:
        pk = c.public_key()
        k_alg = type(pk).__name__
        k_cls = key_class_of(pk)
    except Exception as e:  # noqa: BLE001
        k_alg, k_cls = 'cozulemedi:%s' % e, 'bilinmiyor'
    return {
        'subject': c.subject.rfc4514_string(), 'issuer': c.issuer.rfc4514_string(),
        'serial': c.serial_number, 'imza_alg': name, 'imza_sinif': cls,
        'anahtar_tipi': k_alg, 'anahtar_sinif': k_cls, 'der_bayt': len(der),
        'sha256': sha256(der).hex(), 'x509_hash': x509_hash(der),
        'kendinden_imzali': c.subject == c.issuer,
    }


@dataclass
class X5CResult:
    ok: bool
    reason: str = ''
    leaf_key: object = None
    chain: list = field(default_factory=list)
    chain_class: str = ''
    openssl_output: str = ''


def decode_x5c(x5c) -> list:
    if not isinstance(x5c, list) or not x5c:
        raise FormatError('x5c bos olmayan dizi olmali')
    return [b64_std_decode(s) for s in x5c]


def chain_class(infos) -> str:
    links = [infos[0]['anahtar_sinif']] + [i['imza_sinif'] for i in infos]
    s = set(links)
    if s == {'pq'}:
        return 'tam-pq'
    if s == {'klasik'}:
        return 'tam-klasik'
    return 'karisik'


def validate_x5c(x5c, anchors_der, attime: int, pq_only: bool = False) -> X5CResult:
    try:
        ders = decode_x5c(x5c)
        infos = [cert_info(d) for d in ders]
    except Exception as e:  # noqa: BLE001
        return X5CResult(False, 'x5c-cozulemedi: %s' % e)
    cc = chain_class(infos)
    ok, out = openssl.verify_chain(ders[0], ders[1:], anchors_der, attime)
    if not ok:
        return X5CResult(False, 'x5c-zincir-gecersiz', chain=infos, chain_class=cc, openssl_output=out)
    if pq_only and cc != 'tam-pq':
        return X5CResult(False, 'x5c-klasik-halka', chain=infos, chain_class=cc, openssl_output=out)
    leaf = cx509.load_der_x509_certificate(ders[0])
    try:
        k = key_from_public_object(leaf.public_key())
    except Exception as e:  # noqa: BLE001
        return X5CResult(False, 'x5c-yaprak-anahtari: %s' % e, chain=infos, chain_class=cc)
    return X5CResult(True, 'ok', leaf_key=k, chain=infos, chain_class=cc, openssl_output=out)


def pem_to_der(pem: bytes) -> bytes:
    return cx509.load_pem_x509_certificate(pem).public_bytes(serialization.Encoding.DER)
