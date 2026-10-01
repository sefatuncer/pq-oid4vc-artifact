"""pqjose — PQ-OID4VC deneyleri icin PQ/composite JWS imzalayici ve dogrulayici (Adim 9b).

Bu paket deney ARACIDIR; hedef kutuphanelerin davranisini olcmez.
"""
__version__ = '1.0.0'

SPEC_VERSIONS = {
    'JWS': 'RFC 7515',
    'JWA': 'RFC 7518 (RFC 9864 ile guncellendi)',
    'ML-DSA': 'RFC 9964 (Mayis 2026)',
    'composite': 'draft-ietf-jose-pq-composite-sigs-04 (10.09.2026)',
    'EdDSA': 'RFC 8037 / RFC 9864',
}


def versions() -> dict:
    import sys

    import cryptography
    from cryptography.hazmat.backends.openssl import backend

    from . import openssl
    return {
        'pqjose': __version__,
        'python': sys.version.split()[0],
        'cryptography': cryptography.__version__,
        'cryptography_openssl': backend.openssl_version_text(),
        'openssl_cli': openssl.version(),
        'spesifikasyonlar': SPEC_VERSIONS,
    }
