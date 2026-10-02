#!/usr/bin/env python3
"""T05 — Acceptance test of the PQ primitive verification service (pqdogrula).

Acceptance criterion (9a D-E3/D-E5): the t01 and t02 vectors must give the SAME result from the service too.
  * t01: 12 external vectors (RFC 9964 JOSE+COSE, composite -04 JOSE) + corrupted variants of each
  * t02: the same scenarios with the same deterministic keys (label 't02/<alg>'): pqjose (hedged), OpenSSL CLI,
         dilithium-py signatures; for composite pqjose and OpenSSL-component signatures + corrupted variants
  Every request via three routes: HTTP /v1/dogrula, HTTP /v1/dogrula/toplu, CLI (python -m service.pqdogrula dogrula).
  Comparison: service {gecerli, bilesenler} == library (pqjose.mldsa / pqjose.composite) result.
Usage: python t05_service.py <external-vectors folder> <result folder>
"""
import glob
import json
import os
import subprocess
import sys
import threading
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from ortak import Kayit  # noqa: E402

from dilithium_py.ml_dsa import ML_DSA_44, ML_DSA_65, ML_DSA_87  # noqa: E402

from pqjose import composite, der, openssl  # noqa: E402
from pqjose import mldsa as M  # noqa: E402
from pqjose.keys import CompositeKey, MLDSAKey, derive_key, key_from_jwk  # noqa: E402
from pqjose.params import COMPOSITE, MLDSA  # noqa: E402
from pqjose.util import b64u_encode, json_bytes  # noqa: E402
from service import pqdogrula  # noqa: E402

DPY = {44: ML_DSA_44, 65: ML_DSA_65, 87: ML_DSA_87}


def flip(b, i):
    x = bytearray(b)
    x[i] ^= 1
    return bytes(x)


def kitaplik(alg, key, m, s):
    if alg in MLDSA:
        ok = M.verify(MLDSA[alg], key.pub, m, s)
        return {'gecerli': ok, 'bilesenler': {'ml': ok}}
    c = composite.verify_components(alg, key, m, s)
    return {'gecerli': bool(c['ml'] and c['trad']) and not c['hata'], 'bilesenler': {'ml': bool(c['ml']), 'trad': bool(c['trad'])}}


def istek(alg, key, m, s, bicim='jwk'):
    d = {'alg': alg, 'imzalama_girdisi': b64u_encode(m), 'imza': b64u_encode(s)}
    if bicim == 'jwk':
        d['jwk'] = key.public_jwk(kid=False)
    elif bicim == 'hex':
        d = {'alg': alg, 'acik_anahtar_hex': key.pub.hex(), 'imzalama_girdisi_hex': m.hex(), 'imza_hex': s.hex()}
    else:
        d['acik_anahtar'] = b64u_encode(key.pub)
    return d


def http_post(url, obj):
    req = urllib.request.Request(url, data=json.dumps(obj).encode(), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def cli(obj):
    p = subprocess.run([sys.executable, '-m', 'service.pqdogrula', 'dogrula'], input=json.dumps(obj).encode(),
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=os.path.join(os.path.dirname(__file__), '..'))
    return json.loads(p.stdout.decode()), p.returncode


def main(src, out):
    K = Kayit('t05_service')
    srv = pqdogrula.sunucu('127.0.0.1', 0)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = 'http://127.0.0.1:%d' % port
    durum = {'t01': [0, 0], 't02': [0, 0]}
    vakalar = []  # (source, name, alg, key, m, s, format)

    # ---------------- t01 external vectors
    for f in sorted(glob.glob(os.path.join(src, '*.json'))):
        if os.path.basename(f).startswith('00-'):
            continue
        v = json.load(open(f, encoding='utf-8'))
        o = v['veri']
        if v['kaynak'] == 'RFC9964':
            lvl = int(v['id'][-2:])
            alg = 'ML-DSA-%d' % lvl
            key = MLDSAKey(alg, pub=bytes.fromhex(o['raw_public_key']))
            m, s = bytes.fromhex(o['raw_to_be_signed']), bytes.fromhex(o['raw_signature'])
            bicimler = ('jwk', 'hex', 'b64u') if 'jwk' in o else ('hex', 'b64u')
        else:
            alg = o['jwk']['alg']
            key = key_from_jwk({k: o['jwk'][k] for k in ('kty', 'alg', 'pub')})
            m, s = bytes.fromhex(o['raw_to_be_signed']), bytes.fromhex(o['raw_composite_signature'])
            bicimler = ('jwk', 'hex')
        for b in bicimler:
            vakalar.append(('t01', v['id'] + '/' + b, alg, key, m, s, b))
        vakalar.append(('t01', v['id'] + '/imza-bozuk', alg, key, m, flip(s, 7), 'jwk' if alg in COMPOSITE else 'hex'))
        vakalar.append(('t01', v['id'] + '/ileti-bozuk', alg, key, flip(m, 0), s, 'hex'))
        if alg in COMPOSITE:
            n = M.sig_len(COMPOSITE[alg]['ml'])
            vakalar.append(('t01', v['id'] + '/klasik-bilesen-bozuk', alg, key, m, flip(s, len(s) - 3), 'jwk'))
            vakalar.append(('t01', v['id'] + '/sonda-artik-bayt', alg, key, m, s + b'\x00', 'jwk'))
            vakalar.append(('t01', v['id'] + '/ml-bileseni-bozuk', alg, key, m, flip(s, n // 2), 'jwk'))

    # ---------------- t02 scenarios (same deterministic keys)
    payload = json_bytes({'iss': 'https://issuer.example', 'vct': 'urn:eudi:pid:1', 'iat': 1790000000})
    for alg, lvl in MLDSA.items():
        k = derive_key(alg, 't02/' + alg)
        k.kid = k.thumbprint()
        m = (b64u_encode(json_bytes({'alg': alg, 'kid': k.kid})) + '.' + b64u_encode(payload)).encode()
        sigs = {'pqjose-hedged': M.sign(lvl, k.seed, m), 'openssl-hedged': openssl.mldsa_sign(lvl, k.seed, m, deterministic=False),
                'dilithium-py': DPY[lvl].sign(DPY[lvl].key_derive(k.seed)[1], m), 'belirlenimci': M.sign(lvl, k.seed, m, deterministic=True)}
        for ad, s in sigs.items():
            vakalar.append(('t02', '%s/%s' % (alg, ad), alg, k.public_only(), m, s, 'jwk'))
        vakalar.append(('t02', '%s/bozuk' % alg, alg, k.public_only(), m, flip(sigs['pqjose-hedged'], 100), 'jwk'))
    for alg, prm in COMPOSITE.items():
        k = derive_key(alg, 't02/' + alg)
        k.kid = k.thumbprint()
        m = (b64u_encode(json_bytes({'alg': alg, 'kid': k.kid})) + '.' + b64u_encode(payload)).encode()
        mp = composite.message_representative(alg, m)
        o_ml = openssl.mldsa_sign(prm['ml'], k.ml.seed, mp, ctx=prm['label'], deterministic=False)
        if prm['trad'] == 'ECDSA':
            o_tr = der.ecdsa_raw_to_der(der.ecdsa_der_to_raw(openssl.dgst_sign(k.trad.private_pem(), mp, prm['md'], False),
                                                             prm['crv']), prm['crv'])
        else:
            o_tr = openssl.pkey_sign_raw(k.trad.private_pem(), mp)
        s1 = composite.sign(alg, k, m)
        n = M.sig_len(prm['ml'])
        for ad, s in (('pqjose', s1), ('openssl-bilesenleri', o_ml + o_tr), ('ml-bozuk', flip(s1, n // 2)),
                      ('trad-bozuk', flip(s1, len(s1) - 3)), ('kesik', s1[:n])):
            vakalar.append(('t02', '%s/%s' % (alg, ad), alg, k.public_only(), m, s, 'jwk'))

    # ---------------- comparison: HTTP single, CLI; then batch
    istekler = []
    for kaynak, ad, alg, key, m, s, b in vakalar:
        beklenen = kitaplik(alg, key, m, s)
        ist = istek(alg, key, m, s, b)
        istekler.append(ist)
        h = http_post(base + '/v1/dogrula', ist)
        c, rc = cli(ist)
        ayni = all(x['gecerli'] == beklenen['gecerli'] and x['bilesenler'] == beklenen['bilesenler'] for x in (h, c))
        rc_ok = (rc == 0) == beklenen['gecerli']
        durum[kaynak][1] += 1
        if K.kontrol(kaynak, ad + ' (HTTP+CLI == kitaplik)', ayni and rc_ok,
                     {'kitaplik': beklenen, 'http': {k: h[k] for k in ('gecerli', 'bilesenler', 'hata')}, 'cli_cikis': rc}):
            durum[kaynak][0] += 1
    toplu = []
    for i in range(0, len(istekler), 200):
        toplu += http_post(base + '/v1/dogrula/toplu', {'istekler': istekler[i:i + 200]})['yanitlar']
    ayni_toplu = all(t['gecerli'] == kitaplik(a, k_, m, s)['gecerli'] for t, (_, _, a, k_, m, s, _) in zip(toplu, vakalar))
    K.kontrol('toplu', '/v1/dogrula/toplu %d istek == kitaplik' % len(toplu), ayni_toplu and len(toplu) == len(vakalar))

    # ---------------- error paths and health
    k65 = derive_key('ML-DSA-65', 't02/ML-DSA-65')
    e1 = http_post(base + '/v1/dogrula', {'alg': 'ES256', 'acik_anahtar': 'AA', 'imzalama_girdisi': 'AA', 'imza': 'AA'})
    K.kontrol('hata', 'desteklenmeyen alg (ES256) -> hata, gecersiz', not e1['gecerli'] and 'desteklenmeyen' in e1['hata'], e1['hata'])
    j = k65.public_jwk(kid=False)
    j['alg'] = 'ML-DSA-44'
    e2 = http_post(base + '/v1/dogrula', {'alg': 'ML-DSA-65', 'jwk': j, 'imzalama_girdisi': 'AA', 'imza': 'AA'})
    K.kontrol('hata', 'jwk.alg != istek alg -> hata', not e2['gecerli'] and e2['hata'], e2['hata'])
    e3 = http_post(base + '/v1/dogrula', {'alg': 'ML-DSA-65', 'acik_anahtar_hex': 'zz', 'imzalama_girdisi': 'AA', 'imza': 'AA'})
    K.kontrol('hata', 'gecersiz hex -> hata', not e3['gecerli'] and e3['hata'], e3['hata'])
    e4 = http_post(base + '/v1/dogrula', {'alg': 'ML-DSA-65', 'acik_anahtar': b64u_encode(k65.pub[:-1]),
                                          'imzalama_girdisi': 'AA', 'imza': 'AA'})
    K.kontrol('hata', 'acik anahtar uzunlugu hatali -> hata', not e4['gecerli'] and e4['hata'], e4['hata'])
    jp = k65.private_jwk(kid=False)
    m = b'x'
    e5 = http_post(base + '/v1/dogrula', {'alg': 'ML-DSA-65', 'jwk': jp, 'imzalama_girdisi': b64u_encode(m),
                                          'imza': b64u_encode(M.sign(65, k65.seed, m))})
    K.kontrol('hata', "jwk'de priv varsa yok sayilir (yalniz pub kullanilir)", e5['gecerli'], e5)
    with urllib.request.urlopen(base + '/v1/saglik', timeout=30) as r:
        sg = json.loads(r.read().decode())
    K.kontrol('saglik', '/v1/saglik 9 alg', sg['durum'] == 'ok' and len(sg['desteklenen_alg']) == 9, sg['desteklenen_alg'])
    srv.shutdown()
    K.bilgi('genel', 'ayni-sonuc', {k: '%d/%d' % tuple(v) for k, v in durum.items()})
    return K.yaz(out, {'ayni_sonuc': {k: {'ayni': v[0], 'toplam': v[1]} for k, v in durum.items()}})


if __name__ == '__main__':
    o = main(sys.argv[1], sys.argv[2])
    sys.exit(0 if not o['kalan'] else 1)
