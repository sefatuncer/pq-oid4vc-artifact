"""Sistem OpenSSL (>= 3.5) komut satiri sarmalayicisi.

Kullanim yerleri:
  * belirlenimci ML-DSA imzasi (FIPS 204 deterministic varyant; -pkeyopt deterministic:1)
  * capraz dogrulama (imzalayicimizin ciktisini bagimsiz bir OpenSSL surumu dogrular)
  * X.509 sertifika uretimi (belirlenimci: -sigopt deterministic:1 / nonce-type:1)
  * x5c zincir dogrulamasi (openssl verify)
"""
import functools
import os
import subprocess
import tempfile

OPENSSL = os.environ.get('PQJOSE_OPENSSL', 'openssl')


class OpenSSLError(RuntimeError):
    pass


def run(args, input_bytes=None, check=True):
    p = subprocess.run([OPENSSL] + list(args), input=input_bytes, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    if check and p.returncode != 0:
        raise OpenSSLError('openssl %s -> %d: %s' % (' '.join(args[:3]), p.returncode,
                                                      p.stderr.decode(errors='replace')[:400]))
    return p


@functools.lru_cache(maxsize=1)
def version() -> str:
    return run(['version']).stdout.decode().strip()


class _Tmp:
    def __init__(self):
        self.d = tempfile.TemporaryDirectory(prefix='pqjose-')

    def path(self, name, data=None):
        p = os.path.join(self.d.name, name)
        if data is not None:
            with open(p, 'wb') as f:
                f.write(data)
        return p

    def read(self, name):
        with open(os.path.join(self.d.name, name), 'rb') as f:
            return f.read()

    def close(self):
        self.d.cleanup()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


@functools.lru_cache(maxsize=256)
def mldsa_private_pem(level: int, seed: bytes) -> bytes:
    """ML-DSA ozel anahtari (PKCS#8, tohum bicimi) — FIPS 204 KeyGen_internal(seed)."""
    if len(seed) != 32:
        raise ValueError('ML-DSA tohumu 32 bayt olmali')
    return run(['genpkey', '-algorithm', 'ML-DSA-%d' % level, '-pkeyopt', 'hexseed:' + seed.hex()]).stdout


def public_pem_from_private(priv_pem: bytes) -> bytes:
    return run(['pkey', '-pubout'], input_bytes=priv_pem).stdout


def public_der_from_private(priv_pem: bytes) -> bytes:
    return run(['pkey', '-pubout', '-outform', 'DER'], input_bytes=priv_pem).stdout


def mldsa_sign(level: int, seed: bytes, msg: bytes, ctx: bytes = b'', deterministic: bool = True) -> bytes:
    with _Tmp() as t:
        k = t.path('k.pem', mldsa_private_pem(level, seed))
        m = t.path('m.bin', msg)
        s = t.path('s.bin')
        args = ['pkeyutl', '-sign', '-inkey', k, '-in', m, '-out', s]
        if deterministic:
            args += ['-pkeyopt', 'deterministic:1']
        if ctx:
            args += ['-pkeyopt', 'hexcontext-string:' + ctx.hex()]
        run(args)
        return t.read('s.bin')


def pkey_verify(pub_pem: bytes, msg: bytes, sig: bytes, ctx: bytes = b'') -> bool:
    """pkeyutl -verify (ML-DSA, Ed25519, Ed448: ham ileti)."""
    with _Tmp() as t:
        k = t.path('p.pem', pub_pem)
        m = t.path('m.bin', msg)
        s = t.path('s.bin', sig)
        args = ['pkeyutl', '-verify', '-pubin', '-inkey', k, '-in', m, '-sigfile', s]
        if ctx:
            args += ['-pkeyopt', 'hexcontext-string:' + ctx.hex()]
        p = run(args, check=False)
        return p.returncode == 0 and b'Signature Verified Successfully' in p.stdout


def pkey_sign_raw(priv_pem: bytes, msg: bytes) -> bytes:
    """pkeyutl -sign -rawin (Ed25519/Ed448)."""
    with _Tmp() as t:
        k = t.path('k.pem', priv_pem)
        m = t.path('m.bin', msg)
        run(['pkeyutl', '-sign', '-rawin', '-inkey', k, '-in', m, '-out', t.path('s.bin')])
        return t.read('s.bin')


def dgst_verify(pub_pem: bytes, msg: bytes, der_sig: bytes, md: str) -> bool:
    """ECDSA dogrulamasi (imza DER Ecdsa-Sig-Value)."""
    with _Tmp() as t:
        k = t.path('p.pem', pub_pem)
        m = t.path('m.bin', msg)
        s = t.path('s.der', der_sig)
        p = run(['dgst', '-' + md, '-verify', k, '-signature', s, m], check=False)
        return p.returncode == 0 and b'Verified OK' in p.stdout


def dgst_sign(priv_pem: bytes, msg: bytes, md: str, deterministic: bool = True) -> bytes:
    """ECDSA imzasi (DER). deterministic: RFC 6979 (nonce-type:1)."""
    with _Tmp() as t:
        k = t.path('k.pem', priv_pem)
        m = t.path('m.bin', msg)
        args = ['dgst', '-' + md, '-sign', k, '-out', t.path('s.der')]
        if deterministic:
            args += ['-sigopt', 'nonce-type:1']
        run(args + [m])
        return t.read('s.der')


def verify_chain(leaf_der: bytes, intermediates_der, anchors_der, attime: int, extra_args=()):
    """openssl verify -x509_strict; (ok, cikti) dondurur."""
    with _Tmp() as t:
        leaf = t.path('leaf.pem', der_to_pem(leaf_der))
        anc = t.path('anchors.pem', b''.join(der_to_pem(a) for a in anchors_der))
        args = ['verify', '-x509_strict', '-attime', str(int(attime)), '-CAfile', anc]
        if intermediates_der:
            unt = t.path('untrusted.pem', b''.join(der_to_pem(c) for c in intermediates_der))
            args += ['-untrusted', unt]
        args += list(extra_args) + [leaf]
        p = run(args, check=False)
        out = (p.stdout + p.stderr).decode(errors='replace').strip()
        return p.returncode == 0 and out.endswith(': OK'), out


def der_to_pem(der: bytes, label: str = 'CERTIFICATE') -> bytes:
    import base64
    b = base64.b64encode(der)
    lines = [b[i:i + 64] for i in range(0, len(b), 64)]
    return (b'-----BEGIN ' + label.encode() + b'-----\n' + b'\n'.join(lines) + b'\n-----END ' +
            label.encode() + b'-----\n')


def cert_pem_to_der(pem: bytes) -> bytes:
    return run(['x509', '-outform', 'DER'], input_bytes=pem).stdout


def make_certificate(subject: str, subject_pub_pem: bytes, issuer_key_pem: bytes,
                     issuer_cert_pem, serial: int, not_before: str, not_after: str,
                     config_text: str, ext_section: str, sigopts=()) -> bytes:
    """Belirlenimci sertifika (PEM). issuer_cert_pem None ise kendinden imzali kok.

    Kok: 'openssl req -new -x509'; digerleri: 'openssl x509 -new -force_pubkey -CA'.
    Gecerlilik tarihleri sabit (-not_before/-not_after, OpenSSL >= 3.4).
    """
    with _Tmp() as t:
        cnf = t.path('c.cnf', config_text.encode())
        ik = t.path('ik.pem', issuer_key_pem)
        out = t.path('out.pem')
        so = []
        for o in sigopts:
            so += ['-sigopt', o]
        if issuer_cert_pem is None:
            args = ['req', '-new', '-x509', '-key', ik, '-subj', subject, '-set_serial', str(serial),
                    '-not_before', not_before, '-not_after', not_after, '-config', cnf,
                    '-extensions', ext_section] + so + ['-out', out]
        else:
            sp = t.path('sp.pem', subject_pub_pem)
            ic = t.path('ic.pem', issuer_cert_pem)
            args = ['x509', '-new', '-force_pubkey', sp, '-subj', subject, '-CA', ic, '-CAkey', ik,
                    '-set_serial', str(serial), '-not_before', not_before, '-not_after', not_after,
                    '-extfile', cnf, '-extensions', ext_section] + so + ['-out', out]
        run(args)
        return t.read('out.pem')
