"""pqjose — PQ/composite JWS signer and verifier for the PQ-OID4VC experiments (Step 9b).

This package is an experiment TOOL; it does not measure the behaviour of the target libraries.
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
