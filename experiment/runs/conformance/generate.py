"""Pre-freeze adapter conformance objects (decision D9). NOT part of the measurement battery.

Every object mirrors one battery vector: the same headers (byte-identical protected headers, kid, x5c), the same
signer keys and the same signature order. Only the payload differs: a claim "jti" is added, and every signature is
made again over the new payload. The mirrored vectors were chosen so that every job row has an acceptance as the
oracle decision of the mirrored (vector, policy, arm) row. No row on which Y_L4, D_soy or B5 can separate targets by
a rejection is included (T2/K2, T3/K3, VPLUS_ES256 under the L4 family, IZIN-A with X); see README.md.

Two derived objects (an SD-JWT VC signed only with X, with kid) have no battery counterpart in the control arms; their
expected decision is that of VPLUS_X (oracle row of the JWS-level counterpart).

Run (from the repository root, image of the vector generator, network off):
  docker run --rm --network none -v "<repo>/experiment/vector-generator:/work:ro" \
      -v "<repo>/experiment/runs/conformance:/out" -v "<repo>/experiment/oracle/merged:/oracle:ro" \
      pq-a09-credgen:1.3 python /out/generate.py /out
Outputs: vectors/v1.3/ (objects, MANIFEST.json, SHA256SUMS), jobs.jsonl, expected.tsv, results/self-check.txt.
"""
import copy
import csv
import glob
import hashlib
import json
import os
import sys

sys.path.insert(0, '/work')
from pqjose import algs                          # noqa: E402
from pqjose.keys import derive_key               # noqa: E402
from pqjose.util import b64u_decode, b64u_encode, json_bytes   # noqa: E402

from generator import artefakt as A              # noqa: E402
from generator import cbor, cose                 # noqa: E402
from generator.anahtar import AnahtarSeti        # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else '/out'
BATTERY = '/work/vectors/v1.4'
ORACLE = '/oracle/decisions_v14.tsv'
POLICIES = ('GEC', 'IZIN-A', 'IZIN-AX', 'L4', 'L4-S', 'L4-Y', 'P0', 'P1')
COSE_NAME = {-7: 'ES256', -8: 'EdDSA', -19: 'Ed25519', -35: 'ES384', -49: 'ML-DSA-65'}

# arm -> mirrored battery vectors (JOSE compact, JOSE General JSON, COSE_Sign1, COSE_Sign, SD-JWT compact, SD-JWT General JSON)
MIRRORS = {
    'kontrol-EdDSA': ['VPLUS_ES256', 'VPLUS_EdDSA', 'L4C-JOSE_eski_ES256',
                      'T1K_both_valid', 'T1K_both_valid-SIRA-ters', 'T5K_only_EdDSA',
                      'COSE-VPLUS_ES256', 'COSE-VPLUS_EdDSA', 'L4C-COSE_eski_ES256',
                      'COSE-K1K_iki_gecerli', 'COSE-K1K_iki_gecerli-SIRA-ters', 'COSE-K4K_yalniz_X',
                      'VC01_ES256_x5c', 'VC09_GJ_ES256_EdDSA', 'VC09_GJ_ES256_EdDSA-SIRA-ters'],
    'kontrol-ES384': ['VPLUS_ES256', 'VPLUS_EdDSA-ES384', 'L4C-JOSE_eski_ES256',
                      'T1K_both_valid-ES384', 'T1K_both_valid-SIRA-ters-ES384', 'T5K_only_EdDSA-ES384',
                      'COSE-VPLUS_ES256', 'COSE-VPLUS_EdDSA-ES384', 'L4C-COSE_eski_ES256',
                      'COSE-K1K_iki_gecerli-ES384', 'COSE-K1K_iki_gecerli-SIRA-ters-ES384', 'COSE-K4K_yalniz_X-ES384',
                      'VC01_ES256_x5c', 'VC09_GJ_ES256_EdDSA-ES384', 'VC09_GJ_ES256_EdDSA-SIRA-ters-ES384'],
    'tedavi-ML-DSA-65': ['VPLUS_ES256', 'VPLUS_ML-DSA-65', 'L4C-JOSE_eski_ES256',
                         'T1P_both_valid', 'T1P_both_valid-SIRA-ters', 'T5P_only_ML-DSA-65',
                         'COSE-VPLUS_ES256', 'COSE-VPLUS_ML-DSA-65', 'L4C-COSE_eski_ES256',
                         'COSE-K1P_iki_gecerli', 'COSE-K1P_iki_gecerli-SIRA-ters', 'COSE-K4P_yalniz_X',
                         'VC01_ES256_x5c', 'VC02_MLDSA65_x5c', 'VC07_GJ_ES256_MLDSA65', 'VC07_GJ_ES256_MLDSA65-SIRA-ters'],
}
# derived SD-JWT VC objects (X only, kid): arm -> (alg, key role, JWS-level counterpart whose oracle rows are used)
DERIVED = {'kontrol-EdDSA': ('EdDSA', 'issuer/EdDSA', 'VPLUS_EdDSA'),
           'kontrol-ES384': ('ES384', 'issuer/ES384', 'VPLUS_EdDSA-ES384')}

S = AnahtarSeti()
LEGACY = derive_key('ES256', 'v1.3/issuer-eski/ES256')
LEGACY.kid = LEGACY.thumbprint()


def key(role):
    return LEGACY if role == 'issuer-eski/ES256' else S[role]


def syn_id(mirror):
    return 'SYN-' + mirror


def with_jti(claims, sid):
    c = dict(claims)
    assert 'jti' not in c
    c['jti'] = 'conformance/' + sid
    return c


# ------------------------------------------------------------------ re-signing
def jws_entries(obj):
    """(payload_b64, entries) for compact (str) or JSON (dict) serializations; entries have 'protected' and 'signature'."""
    if isinstance(obj, str):
        h, p, s = obj.split('.')
        return p, [{'protected': h, 'signature': s}]
    return obj['payload'], obj['signatures'] if 'signatures' in obj else [obj]


def resign_jws(obj, roles, sid):
    payload_b64, _ = jws_entries(obj)
    new_payload = b64u_encode(json_bytes(with_jti(json.loads(b64u_decode(payload_b64)), sid)))
    if isinstance(obj, str):
        h = obj.split('.')[0]
        alg = json.loads(b64u_decode(h))['alg']
        sig = algs.sign(alg, key(roles[0]), (h + '.' + new_payload).encode('ascii'), True)
        return h + '.' + new_payload + '.' + b64u_encode(sig)
    out = copy.deepcopy(obj)
    out['payload'] = new_payload
    for e, role in zip(out['signatures'], roles):
        alg = json.loads(b64u_decode(e['protected']))['alg']
        e['signature'] = b64u_encode(algs.sign(alg, key(role), (e['protected'] + '.' + new_payload).encode('ascii'), True))
    return out


def resign_sdjwt_compact(text, roles, sid):
    jwt, rest = text.split('~', 1)
    return resign_jws(jwt, roles, sid) + '~' + rest


def resign_cose(data, roles, sid):
    t = cbor.decode(data)
    body = list(t.value)
    payload = cbor.encode(with_jti(cbor.decode(body[2]), sid))
    body[2] = payload
    if t.tag == cose.TAG_SIGN1:
        alg = COSE_NAME[cbor.decode(body[0])[cose.H_ALG]]
        body[3] = algs.sign(alg, key(roles[0]), cose.sig_structure1(body[0], payload), True)
        return cose.kodla(body, cose.TAG_SIGN1)
    signers = []
    for s, role in zip(body[3], roles):
        alg = COSE_NAME[cbor.decode(s[0])[cose.H_ALG]]
        signers.append([s[0], s[1], algs.sign(alg, key(role), cose.sig_structure(body[0], s[0], payload), True)])
    body[3] = signers
    return cose.kodla(body, cose.TAG_SIGN)


# ------------------------------------------------------------------ independent self-check
def check_jws(obj, mirror_obj, roles):
    """Every signature verifies with its role key; protected headers equal the mirror's; payload = mirror + jti."""
    p_new, e_new = jws_entries(obj)
    p_old, e_old = jws_entries(mirror_obj)
    assert [e['protected'] for e in e_new] == [e['protected'] for e in e_old], 'protected headers differ'
    a, b = json.loads(b64u_decode(p_new)), json.loads(b64u_decode(p_old))
    assert a.pop('jti').startswith('conformance/') and a == b, 'payload differs beyond jti'
    for e, role in zip(e_new, roles):
        h = json.loads(b64u_decode(e['protected']))
        if 'kid' in h:
            assert h['kid'] == key(role).kid, 'kid does not match the signer role'
        ok = algs.verify(h['alg'], key(role), (e['protected'] + '.' + p_new).encode('ascii'), b64u_decode(e['signature']))
        assert ok, 'signature does not verify'
    return len(e_new)


def check_cose(data, mirror_data, roles):
    n, o = cose.ayristir(data), cose.ayristir(mirror_data)
    assert n['body_prot'] == o['body_prot'] and n['body_unprot'] == o['body_unprot']
    assert [s['sp'] for s in n['imzalar']] == [s['sp'] for s in o['imzalar']], 'protected headers differ'
    assert [s['unprot'] for s in n['imzalar']] == [s['unprot'] for s in o['imzalar']], 'unprotected headers differ'
    a, b = cbor.decode(n['payload']), cbor.decode(o['payload'])
    assert a.pop('jti').startswith('conformance/') and a == b, 'payload differs beyond jti'
    for s, role in zip(n['imzalar'], roles):
        if s['kid'] is not None:
            assert s['kid'] == cose.kid_bytes(key(role)), 'kid does not match the signer role'
        assert cose.dogrula_imza(s, key(role), COSE_NAME[s['alg']]), 'signature does not verify'
    return len(n['imzalar'])


# ------------------------------------------------------------------ main
def main():
    man = {r['id']: r for r in json.load(open(os.path.join(BATTERY, 'MANIFEST.json'), encoding='utf-8'))['vektorler']}
    oracle = {}
    for r in csv.DictReader(open(ORACLE, encoding='utf-8'), delimiter='\t'):
        oracle[(r['vektor_id'], r['politika'], r['kol'])] = r['karar']
    vdir = os.path.join(OUT, 'vectors', 'v1.3')
    os.makedirs(vdir, exist_ok=True)
    battery_hashes = set()
    for f in glob.glob('/work/vectors/**/*', recursive=True):
        if os.path.isfile(f):
            battery_hashes.add(hashlib.sha256(open(f, 'rb').read()).hexdigest())

    rows, made, log = [], {}, []

    def write(sid, family, ext, data, entry):
        rel = '%s/%s.%s' % (family, sid, ext)
        p = os.path.join(vdir, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'wb').write(data)
        h = hashlib.sha256(data).hexdigest()
        assert h not in battery_hashes, 'collides with a battery file: ' + sid
        e = copy.deepcopy(entry)
        e.update({'id': sid, 'dosya': rel, 'sha256': h, 'bayt': len(data), 'aile': family})
        e['aciklama'] = 'Conformance object (not in the battery). ' + e.get('aciklama', '')
        made[sid] = e

    for arm, mirrors in MIRRORS.items():
        for mid in mirrors:
            sid = syn_id(mid)
            src = man[mid]
            roles = [s['anahtar_rolu'] for s in src['insa']['imzalar']]
            if sid not in made:
                raw = open(os.path.join(BATTERY, src['dosya']), 'rb').read()
                ser = src['serilestirme']
                family = 'SYN-' + src['dosya'].split('/')[0]
                if ser in ('compact',):
                    obj = resign_jws(raw.decode('utf-8').strip(), roles, sid)
                    n = check_jws(obj, raw.decode('utf-8').strip(), roles)
                    data, ext = obj.encode('utf-8'), 'jws'
                elif ser == 'sd-jwt-compact':
                    old = raw.decode('utf-8').strip()
                    obj = resign_sdjwt_compact(old, roles, sid)
                    assert obj.split('~', 1)[1] == old.split('~', 1)[1], 'disclosures changed'
                    n = check_jws(obj.split('~')[0], old.split('~')[0], roles)
                    data, ext = obj.encode('utf-8'), 'sdjwt'
                elif ser in ('general', 'sd-jwt-general'):
                    old = json.loads(raw)
                    obj = resign_jws(old, roles, sid)
                    n = check_jws(obj, old, roles)
                    data, ext = (json.dumps(obj, indent=1, ensure_ascii=False) + '\n').encode('utf-8'), 'json'
                elif ser in ('COSE_Sign1', 'COSE_Sign'):
                    data = resign_cose(raw, roles, sid)
                    n = check_cose(data, raw, roles)
                    ext = 'cbor'
                else:
                    raise ValueError(ser)
                write(sid, family, ext, data, src)
                made[sid]['ayna'] = mid
                log.append('%s mirror=%s serialization=%s signatures=%d verified, headers equal, payload = mirror + jti'
                           % (sid, mid, ser, n))
            for pol in POLICIES:
                d = oracle.get((mid, pol, arm))
                if d in ('accept-classical', 'accept-hybrid'):
                    rows.append((sid, pol, arm, src, roles, 'mirror:%s (%s)' % (mid, d)))

    holder = S['holder/ES256'].public_jwk(kid=False)
    base = man['VC03_composite_kid']
    for arm, (alg, role, analogue) in DERIVED.items():
        sid = 'SYN-D-VCX_%s_kid' % alg
        vc = A.issue_vc(sid, [(S[role], alg, None)], holder)
        jwt = vc['obj'].split('~')[0]
        h = json.loads(b64u_decode(jwt.split('.')[0]))
        assert h['alg'] == alg and h['kid'] == S[role].kid
        assert algs.verify(alg, S[role], jwt.rsplit('.', 1)[0].encode('ascii'), b64u_decode(jwt.rsplit('.', 1)[1]))
        entry = copy.deepcopy(base)
        entry['aciklama'] = 'Derived SD-JWT VC (compact; typ=dc+sd-jwt; PID), %s only, kid.' % alg
        entry['kol'] = arm
        entry['insa'] = {'imzalar': [{'sira': 0, 'alg': alg, 'anahtar_rolu': role, 'kid': S[role].kid, 'insa': 'gecerli'}],
                         'ifsa_sayisi': len(vc['labeled'])}
        entry['dogrulama_girdileri'] = {'jwks': 'anahtarlar/v1/acik-jwks.json', 'kid': [S[role].kid], 'simdi': base['dogrulama_girdileri']['simdi']}
        write(sid, 'SYN-VC', 'sdjwt', vc['obj'].encode('utf-8'), entry)
        made[sid]['ayna'] = None
        log.append('%s derived (X only, kid) signature verified' % sid)
        for pol in POLICIES:
            d = oracle.get((analogue, pol, arm))
            if d in ('accept-classical', 'accept-hybrid'):
                rows.append((sid, pol, arm, made[sid], [role], 'derived:analogue %s (%s)' % (analogue, d)))

    entries = sorted(made.values(), key=lambda e: e['id'])
    json.dump({'surum': 'conformance-1', 'not': 'Pre-freeze adapter conformance objects (decision D9); not battery vectors.',
               'vektorler': entries}, open(os.path.join(vdir, 'MANIFEST.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    with open(os.path.join(vdir, 'SHA256SUMS'), 'w', encoding='utf-8') as f:
        for e in entries:
            f.write('%s  %s\n' % (e['sha256'], e['dosya']))
    with open(os.path.join(OUT, 'jobs.jsonl'), 'w', encoding='utf-8') as fj, \
            open(os.path.join(OUT, 'expected.tsv'), 'w', encoding='utf-8') as fe:
        fe.write('vektor_id\tpolitika\tkol\tbeklenen\tkaynak\n')
        for sid, pol, arm, src, roles, why in rows:
            algler = ';'.join(s['alg'] for s in src['insa']['imzalar'])
            fj.write(json.dumps({'algler': algler, 'artefakt': src['artefakt'], 'dosya': 'v1.3/' + made[sid]['dosya'],
                                 'kol': arm, 'politika': pol, 'serilestirme': src['serilestirme'], 'vektor_id': sid},
                                sort_keys=True) + '\n')
            fe.write('%s\t%s\t%s\tkabul\t%s\n' % (sid, pol, arm, why))
    os.makedirs(os.path.join(OUT, 'results'), exist_ok=True)
    with open(os.path.join(OUT, 'results', 'self-check.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(log) + '\n')
        f.write('objects %d, job rows %d, no object hash equals a battery file hash (%d battery files checked)\n'
                % (len(entries), len(rows), len(battery_hashes)))
    print('objects', len(entries), 'job rows', len(rows))


if __name__ == '__main__':
    main()
