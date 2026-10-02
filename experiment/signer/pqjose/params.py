"""Algorithm parameter tables.

Sources:
  RFC 7518 3.4 (ES256/ES384), RFC 8037 (EdDSA), RFC 9864 (fully specified names Ed25519/Ed448),
  RFC 9964 5 and 8.1.4 (ML-DSA-44/65/87),
  draft-ietf-jose-pq-composite-sigs-04 Table 5 (JOSE alg), Table 7 (Label), 4.2 (Prefix).
"""

# Composite -04, 4.2: "CompositeAlgorithmSignatures2025"
PREFIX = bytes.fromhex('436F6D706F73697465416C676F726974686D5369676E61747572657332303235')
assert PREFIX == b'CompositeAlgorithmSignatures2025'

# Table 5 (JOSE) + Table 7 (Label). 'ph': pre-hash; 'md': the classical component's own hash function.
COMPOSITE = {
    'ML-DSA-44-ES256': dict(ml=44, trad='ECDSA', crv='P-256', md='sha256', ph='sha256',
                            label=b'COMPSIG-MLDSA44-ECDSA-P256-SHA256', cose=-54),
    'ML-DSA-65-ES256': dict(ml=65, trad='ECDSA', crv='P-256', md='sha256', ph='sha512',
                            label=b'COMPSIG-MLDSA65-ECDSA-P256-SHA512', cose=-55),
    'ML-DSA-87-ES384': dict(ml=87, trad='ECDSA', crv='P-384', md='sha384', ph='sha512',
                            label=b'COMPSIG-MLDSA87-ECDSA-P384-SHA512', cose=-56),
    'ML-DSA-44-Ed25519': dict(ml=44, trad='EdDSA', crv='Ed25519', md=None, ph='sha512',
                              label=b'COMPSIG-MLDSA44-Ed25519-SHA512', cose=-57),
    'ML-DSA-65-Ed25519': dict(ml=65, trad='EdDSA', crv='Ed25519', md=None, ph='sha512',
                              label=b'COMPSIG-MLDSA65-Ed25519-SHA512', cose=-58),
    'ML-DSA-87-Ed448': dict(ml=87, trad='EdDSA', crv='Ed448', md=None, ph='shake256',
                            label=b'COMPSIG-MLDSA87-Ed448-SHAKE256', cose=-59),
}

MLDSA = {'ML-DSA-44': 44, 'ML-DSA-65': 65, 'ML-DSA-87': 87}

# kty, crv (None: from the key), hash
CLASSICAL = {
    'ES256': ('EC', 'P-256', 'sha256'),
    'ES384': ('EC', 'P-384', 'sha384'),
    'EdDSA': ('OKP', None, None),          # RFC 8037 (polymorphic; curve from the key)
    'Ed25519': ('OKP', 'Ed25519', None),   # RFC 9864 (fully specified)
    'Ed448': ('OKP', 'Ed448', None),       # RFC 9864
}

ALL_ALGS = tuple(CLASSICAL) + tuple(MLDSA) + tuple(COMPOSITE)


def alg_class(alg: str) -> str:
    """'klasik' | 'pq' | 'hibrit' | 'bilinmiyor' (class for the CRQC emulator: classical, pq, hybrid, unknown)."""
    if alg in CLASSICAL:
        return 'klasik'
    if alg in MLDSA:
        return 'pq'
    if alg in COMPOSITE:
        return 'hibrit'
    return 'bilinmiyor'


# Curve sizes and EdDSA sizes
EC_LEN = {'P-256': 32, 'P-384': 48}
OKP_PUB_LEN = {'Ed25519': 32, 'Ed448': 57}
OKP_SIG_LEN = {'Ed25519': 64, 'Ed448': 114}
