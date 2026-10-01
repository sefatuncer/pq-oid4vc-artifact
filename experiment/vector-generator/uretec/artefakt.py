"""Artefakt uretecleri: SD-JWT VC (PID), sunum (KB-JWT), Status List Token, OID4VP istek nesnesi, DPoP.

Tum zaman damgalari sabit (T0 = 1790000000 = 2026-09-21T14:13:20Z); tuz, jti ve sahte ozetler
HKDF'den turetilir -> uretim bayt-bayt tekrarlanabilir. Kisisel veri YOK (sentetik PID: 'Erika Mustermann').
"""
import hashlib

from pqjose import jws
from pqjose.keys import derive_bytes
from pqjose.util import b64u_encode, json_bytes
from pqjose.x509 import x509_hash

from . import sdjwt, statuslist

T0 = 1790000000
ISS = 'https://issuer.example'
VCT = 'urn:eudi:pid:1'
STATUS_URI = 'https://issuer.example/statuslists/1'
ORIGIN = 'https://verifier.example'
NONCE = 'n-0S6_WzA2Mj'
KB_AUD_DCAPI = 'origin:' + ORIGIN + '/'          # OID4VP A.4: DC API'de aud = 'origin:' + Origin
ACCESS_TOKEN = 'Kz~8mXK1EalYznwH-LC-1fBAo.4Ljp~zsPE_NeO.gxU'   # RFC 9449 7.1 ornek degeri
DPOP_NONCE = 'eyJ7S_zG.eyJH0-Z.HX4w-7v'                     # RFC 9449 8 ornek degeri
SUPPORTED = ['ES256', 'ML-DSA-65', 'ML-DSA-65-ES256']


def salt_fn(cred_id):
    return lambda label: b64u_encode(derive_bytes('v1/salt/%s/%s' % (cred_id, label), 16))


def decoy_fn(cred_id):
    return lambda label: b64u_encode(hashlib.sha256(derive_bytes('v1/decoy/%s/%s' % (cred_id, label), 32)).digest())


# ------------------------------------------------------------------ SD-JWT VC (PID)
def pid_payload(cred_id, holder_pub_jwk, status_idx=7):
    """Sentetik PID. SD: given_name, family_name, birthdate, address.{4 alan}, nationalities[0],
    age_equal_or_over.{18,21}; 2 sahte ozet. SD OLAMAZLAR (SD-JWT VC 2.2.2.3): iss, iat, exp, vct, cnf, status."""
    b = sdjwt.Builder(salt_fn(cred_id), decoy_fn(cred_id))
    p = {'iss': ISS, 'iat': T0, 'exp': T0 + 365 * 86400, 'vct': VCT}
    b.sd_prop(p, 'given_name', 'Erika', 'given_name')
    b.sd_prop(p, 'family_name', 'Mustermann', 'family_name')
    b.sd_prop(p, 'birthdate', '1964-08-12', 'birthdate')
    addr = {}
    for k, v in (('street_address', 'Heidestrasse 17'), ('locality', 'Koeln'), ('postal_code', '51147'), ('country', 'DE')):
        b.sd_prop(addr, k, v, 'address.' + k)
    p['address'] = addr
    p['nationalities'] = [b.sd_elem('DE', 'nationalities[0]')]
    age = {}
    b.sd_prop(age, '18', True, 'age_equal_or_over.18')
    b.sd_prop(age, '21', True, 'age_equal_or_over.21')
    p['age_equal_or_over'] = age
    b.decoys(p, 2, 'top')
    p['cnf'] = {'jwk': holder_pub_jwk}
    p['status'] = {'status_list': {'idx': status_idx, 'uri': STATUS_URI}}
    p['_sd_alg'] = 'sha-256'
    sdjwt.Builder.finalize(p)
    return p, b.disclosures


def vc_header(alg, x5c=None, kid=None, typ='dc+sd-jwt'):
    h = {'typ': typ}
    if x5c is not None:
        h['x5c'] = x5c
    if kid is not None:
        h['kid'] = kid
    return h


def issue_vc(cred_id, signer_specs, holder_pub_jwk, serialization='compact', typ='dc+sd-jwt', status_idx=7):
    """signer_specs: [(key, alg, x5c|None)] ; x5c yoksa kid kullanilir."""
    payload, labeled = pid_payload(cred_id, holder_pub_jwk, status_idx)
    discl = [d for _, d in labeled]
    signers = [jws.Signer(k, vc_header(a, x5c, None if x5c else k.kid, typ), alg=a) for (k, a, x5c) in signer_specs]
    if serialization == 'compact':
        if len(signers) != 1:
            raise ValueError('compact tek imza')
        obj = sdjwt.issue_compact(payload, discl, signers[0])
    else:
        obj = sdjwt.issue_general(payload, discl, signers)
    return {'obj': obj, 'labeled': labeled, 'payload': payload}


PRESENT_LABELS = ('given_name', 'family_name', 'age_equal_or_over.18')


def present(vc, holder_key, holder_alg, aud=KB_AUD_DCAPI, nonce=NONCE, iat=T0 + 3600, sd_hash_sig_index=0):
    if isinstance(vc['obj'], str):
        return sdjwt.present_compact(vc['obj'], PRESENT_LABELS, vc['labeled'], holder_key, holder_alg, aud, nonce, iat)
    return sdjwt.present_general(vc['obj'], PRESENT_LABELS, vc['labeled'], holder_key, holder_alg, aud, nonce, iat,
                                 sd_hash_sig_index=sd_hash_sig_index)


# ------------------------------------------------------------------ Status List Token
STATUSES = {3: 1, 7: 0, 12: 1}    # 16 girdilik 1 bitlik liste; idx 7 (PID) = VALID
STATUS_SIZE = 16


def status_token(key, alg, x5c=None):
    lst = statuslist.encode(STATUSES, STATUS_SIZE, 1)
    prot = {'x5c': x5c} if x5c else {'kid': key.kid}
    return statuslist.status_list_token(jws.Signer(key, prot, alg=alg), STATUS_URI, T0, T0 + 86400, 43200, lst, 1)


# ------------------------------------------------------------------ OID4VP istek nesnesi (JAR / DC API)
def dcql_pid():
    return {'credentials': [{'id': 'pid', 'format': 'dc+sd-jwt', 'meta': {'vct_values': [VCT]},
                             'claims': [{'path': ['given_name']}, {'path': ['family_name']},
                                        {'path': ['age_equal_or_over', '18']}]}]}


def request_params(rp_enc_pub_jwk, client_id=None, expected_origins=True):
    enc = dict(rp_enc_pub_jwk)
    enc.update({'use': 'enc', 'alg': 'ECDH-ES'})
    p = {}
    if client_id is not None:
        p['client_id'] = client_id
    p['response_type'] = 'vp_token'
    p['response_mode'] = 'dc_api.jwt'
    p['nonce'] = NONCE
    if expected_origins:
        p['expected_origins'] = [ORIGIN]
    p['dcql_query'] = dcql_pid()
    p['client_metadata'] = {
        'jwks': {'keys': [enc]},
        'encrypted_response_enc_values_supported': ['A128GCM', 'A256GCM'],
        'vp_formats_supported': {'dc+sd-jwt': {'sd-jwt_alg_values': SUPPORTED, 'kb-jwt_alg_values': SUPPORTED}},
    }
    return p


def x509_hash_client_id(leaf_der):
    return 'x509_hash:' + x509_hash(leaf_der)


def request_compact(key, alg, params, x5c=None):
    prot = {'typ': 'oauth-authz-req+jwt'}
    if x5c:
        prot['x5c'] = x5c
    else:
        prot['kid'] = key.kid
    return jws.sign(json_bytes(params), jws.Signer(key, prot, alg=alg), 'compact', True)


def request_multisigned(params, signer_specs):
    """OID4VP A.3.2.2: client_id YALNIZ ilgili imzanin korumali basliginda; diger parametreler yukte.
    signer_specs: [(key, alg, x5c|None, client_id)]"""
    signers = []
    for key, alg, x5c, cid in signer_specs:
        prot = {'typ': 'oauth-authz-req+jwt'}
        if x5c:
            prot['x5c'] = x5c
        else:
            prot['kid'] = key.kid
        prot['client_id'] = cid
        signers.append(jws.Signer(key, prot, alg=alg))
    return jws.sign(json_bytes(params), signers, 'general', True)


# ------------------------------------------------------------------ DPoP (RFC 9449 4.2)
def dpop(key, alg, label, htm='POST', htu=ISS + '/token', iat=T0, with_ath=False, with_nonce=False):
    h = {'typ': 'dpop+jwt', 'jwk': key.public_jwk(kid=False)}
    c = {'jti': b64u_encode(derive_bytes('v1/dpop/jti/' + label, 16)), 'htm': htm, 'htu': htu, 'iat': iat}
    if with_ath:
        c['ath'] = b64u_encode(hashlib.sha256(ACCESS_TOKEN.encode('ascii')).digest())
    if with_nonce:
        c['nonce'] = DPOP_NONCE
    return jws.sign(json_bytes(c), jws.Signer(key, h, alg=alg), 'compact', True)
