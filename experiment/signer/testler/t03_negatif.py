#!/usr/bin/env python3
"""T03 — Negative tests: OUR verifier (pqjose, AND + required set) must reject them all.

The base of every negative example is first accepted as a POSITIVE control (shows that the test is meaningful).
Policy (unless stated otherwise): semantics='all' (AND), required_algs = expected set (L4),
alg/crit/x5c protected, unknown alg and un-understood crit fail-closed.
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ortak import Kayit  # noqa: E402

from pqjose import composite, der, jws, pki  # noqa: E402
from pqjose.keys import MLDSAKey, derive_key  # noqa: E402
from pqjose.params import COMPOSITE, MLDSA  # noqa: E402
from pqjose.util import b64u_decode, b64u_encode, json_bytes  # noqa: E402

PAYLOAD = json_bytes({'iss': 'https://issuer.example', 'vct': 'urn:eudi:pid:1', 'iat': 1790000000,
                      'given_name': 'Erika'})
PAYLOAD2 = json_bytes({'iss': 'https://issuer.example', 'vct': 'urn:eudi:pid:1', 'iat': 1790000001,
                       'given_name': 'Mallory'})


def flip(b: bytes, i: int, bit: int = 0) -> bytes:
    x = bytearray(b)
    x[i] ^= (1 << bit)
    return bytes(x)


def with_sig(c: str, sig: bytes) -> str:
    h, p, _ = c.split('.')
    return h + '.' + p + '.' + b64u_encode(sig)


def sig_of(c: str) -> bytes:
    return b64u_decode(c.split('.')[2])


def reheader(c: str, prot: dict) -> str:
    _, p, s = c.split('.')
    return b64u_encode(json_bytes(prot)) + '.' + p + '.' + s


class T:
    def __init__(self):
        self.K = Kayit('t03_negatif')
        self.neg = [0, 0]
        self.pos = [0, 0]
        self.tablo = []

    def pozitif(self, grup, ad, obj, pol):
        r = jws.verify(obj, pol)
        self.pos[1] += 1
        if self.K.kontrol(grup, 'POZITIF:' + ad, r.valid, r.reason):
            self.pos[0] += 1
        return r

    def negatif(self, grup, ad, obj, pol, beklenen=None):
        r = jws.verify(obj, pol)
        self.neg[1] += 1
        reasons = [r.reason] + ['#%d %s:%s' % (s.index, s.alg, s.reason) for s in r.signatures]
        ok = not r.valid
        if ok and beklenen:
            ok = any(beklenen in x for x in reasons)
        if self.K.kontrol(grup, 'NEGATIF:' + ad, ok, reasons):
            self.neg[0] += 1
        comps = [s.components for s in r.signatures if s.components]
        self.tablo.append({'grup': grup, 'test': ad, 'reddedildi': not r.valid, 'gerekce': reasons,
                           'bilesenler': comps or None})
        return r


def main(out):
    t = T()
    keys = {a: derive_key(a, 't03/' + a) for a in ('ES256', 'ES384', 'EdDSA', 'Ed448') + tuple(MLDSA) + tuple(COMPOSITE)}
    for k in keys.values():
        k.kid = k.thumbprint()
    pub = {a: k.public_only() for a, k in keys.items()}

    def pol(*algs_, **kw):
        return jws.Policy(keys=[pub[a] for a in algs_], required_algs=frozenset(algs_), **kw)

    def one(alg, payload=PAYLOAD, extra=None):
        prot = {'kid': keys[alg].kid, 'typ': 'dc+sd-jwt'}
        prot.update(extra or {})
        return jws.sign(payload, jws.Signer(keys[alg], prot, alg=alg), 'compact')

    # ---------------- N1 corrupted signature (every alg)
    for alg in keys:
        c = one(alg)
        t.pozitif('N1-bozuk-imza', alg, c, pol(alg))
        s = sig_of(c)
        t.negatif('N1-bozuk-imza', alg + ' (orta bayt bit cevirme)', with_sig(c, flip(s, len(s) // 2)), pol(alg),
                  'imza-gecersiz')

    # ---------------- N2 corrupted payload / N3 corrupted protected header
    for alg in ('ES256', 'ML-DSA-65', 'ML-DSA-65-ES256'):
        c = one(alg)
        h, p, s = c.split('.')
        t.negatif('N2-bozuk-yuk', alg, h + '.' + b64u_encode(PAYLOAD2) + '.' + s, pol(alg), 'imza-gecersiz')
        prot = {'alg': alg, 'kid': keys[alg].kid, 'typ': 'vc+sd-jwt'}
        t.negatif('N3-bozuk-baslik', alg + ' (typ degisti)', reheader(c, prot), pol(alg), 'imza-gecersiz')

    # ---------------- N4 wrong alg label
    c65 = one('ML-DSA-65')
    base = {'kid': keys['ML-DSA-65'].kid, 'typ': 'dc+sd-jwt'}
    for wrong in ('ML-DSA-44', 'ML-DSA-87', 'ML-DSA-65-ES256'):
        pk = [pub['ML-DSA-65'], pub[wrong]]
        t.negatif('N4-yanlis-alg', 'ML-DSA-65 imzasi, alg=%s' % wrong, reheader(c65, dict(alg=wrong, **base)),
                  jws.Policy(keys=pk))
    ce = one('ES256')
    t.negatif('N4-yanlis-alg', 'ES256 imzasi, alg=ES384', reheader(ce, {'alg': 'ES384', 'kid': keys['ES256'].kid}),
              jws.Policy(keys=[pub['ES256'], pub['ES384']]))
    cd = one('EdDSA')
    t.negatif('N4-yanlis-alg', 'EdDSA(Ed25519) imzasi, alg=Ed448', reheader(cd, {'alg': 'Ed448', 'kid': keys['EdDSA'].kid}),
              jws.Policy(keys=[pub['EdDSA'], pub['Ed448']]))
    none = b64u_encode(json_bytes({'alg': 'none'})) + '.' + b64u_encode(PAYLOAD) + '.'
    t.negatif('N4-yanlis-alg', 'alg=none, bos imza', none, jws.Policy(keys=list(pub.values())), 'alg-none')
    unk = reheader(c65, {'alg': 'ML-DSA-66', 'kid': keys['ML-DSA-65'].kid})
    t.negatif('N4-yanlis-alg', 'bilinmeyen alg=ML-DSA-66 (gecerli ML-DSA-65 imza baytlari)', unk,
              jws.Policy(keys=list(pub.values())), 'alg-bilinmiyor')
    # alg only in the unprotected header (flattened)
    k = keys['ML-DSA-65']
    pb64 = b64u_encode(json_bytes({'kid': k.kid}))
    from pqjose import algs
    sig = algs.sign('ML-DSA-65', k, (pb64 + '.' + b64u_encode(PAYLOAD)).encode())
    fl = {'payload': b64u_encode(PAYLOAD), 'protected': pb64, 'header': {'alg': 'ML-DSA-65'}, 'signature': b64u_encode(sig)}
    t.negatif('N4-yanlis-alg', 'alg korumasiz baslikta (flattened)', fl, pol('ML-DSA-65'), 'korumasiz-parametre:alg')

    # ---------------- N5 corruption of a composite component
    for alg, prm in COMPOSITE.items():
        c = one(alg)
        s = sig_of(c)
        n = len(composite.split_signature(alg, s)[0])
        t.negatif('N5-composite-bilesen', alg + ': ML-DSA bileseni bozuk', with_sig(c, flip(s, n // 2)), pol(alg), 'imza-gecersiz')
        if prm['trad'] == 'ECDSA':
            # last byte of the r value (DER: 30 L 02 Lr [00] r...)
            tr = s[n:]
            lr = tr[3]
            idx = n + 4 + lr - 1
        else:
            idx = len(s) - 5
        t.negatif('N5-composite-bilesen', alg + ': klasik bilesen bozuk', with_sig(c, flip(s, idx)), pol(alg), 'imza-gecersiz')
    alg = 'ML-DSA-65-ES256'
    prm = COMPOSITE[alg]
    c = one(alg)
    s = sig_of(c)
    ml_sig, tr = composite.split_signature(alg, s)
    raw = der.ecdsa_der_to_raw(tr, 'P-256')
    t.negatif('N5-composite-bilesen', alg + ': DER SEQUENCE uzunlugu bozuk', with_sig(c, ml_sig + tr[:1] + bytes([tr[1] + 1]) + tr[2:]),
              pol(alg), 'serilestirme')
    # non-minimal DER: an extra 0x00 for r
    r_, s_ = raw[:32], raw[32:]

    def dint(v, pad):
        tt = v.lstrip(b'\x00') or b'\x00'
        if tt[0] >= 0x80:
            tt = b'\x00' + tt
        tt = b'\x00' * pad + tt
        return b'\x02' + bytes([len(tt)]) + tt
    body = dint(r_, 1) + dint(s_, 0)
    t.negatif('N5-composite-bilesen', alg + ': asgari olmayan DER (r onunde fazla 0x00)',
              with_sig(c, ml_sig + b'\x30' + bytes([len(body)]) + body), pol(alg), 'serilestirme')
    t.negatif('N5-composite-bilesen', alg + ': sonda artik bayt', with_sig(c, s + b'\x00'), pol(alg), 'serilestirme')
    t.negatif('N5-composite-bilesen', alg + ': ECDSA bileseni kesilmis (yalniz ML-DSA)', with_sig(c, ml_sig), pol(alg), 'serilestirme')
    t.negatif('N5-composite-bilesen', alg + ': ECDSA bileseni ham r||s (DER degil)', with_sig(c, ml_sig + raw), pol(alg), 'serilestirme')
    c2 = one(alg, PAYLOAD2)
    ml2, tr2 = composite.split_signature(alg, sig_of(c2))
    t.negatif('N5-composite-bilesen', alg + ': bilesenler farkli iletilerden (ML-DSA yuk2, ECDSA yuk1)',
              with_sig(c, ml2 + tr), pol(alg), 'imza-gecersiz')
    t.negatif('N5-composite-bilesen', alg + ': bilesen sirasi ters (trad||ml)', with_sig(c, tr + ml_sig), pol(alg))
    # separability: the ECDSA component presented as an ES256 JWS (the same key counts as an independent ES256 key)
    ec_as_es256 = keys[alg].trad.public_only()
    ec_as_es256.kid = 'reuse-ec'
    h_es = b64u_encode(json_bytes({'alg': 'ES256', 'kid': 'reuse-ec'}))
    j_es = h_es + '.' + b64u_encode(PAYLOAD) + '.' + b64u_encode(raw)
    t.negatif('N5-ayrilabilirlik', alg + ': ECDSA bileseni ES256 diye sunuldu (Prefix/Label ayrimi)', j_es,
              jws.Policy(keys=[ec_as_es256], required_algs=frozenset({'ES256'})), 'imza-gecersiz')
    ml_as = MLDSAKey('ML-DSA-65', pub=keys[alg].ml.pub)
    ml_as.kid = 'reuse-ml'
    h_ml = b64u_encode(json_bytes({'alg': 'ML-DSA-65', 'kid': 'reuse-ml'}))
    t.negatif('N5-ayrilabilirlik', alg + ': ML-DSA bileseni ML-DSA-65 diye sunuldu (ctx=Label ayrimi)',
              h_ml + '.' + b64u_encode(PAYLOAD) + '.' + b64u_encode(ml_sig),
              jws.Policy(keys=[ml_as], required_algs=frozenset({'ML-DSA-65'})), 'imza-gecersiz')
    # even over the same signing input: the component is over M', the JWS input over M
    h_c = c.split('.')[0]
    t.negatif('N5-ayrilabilirlik', alg + ': ECDSA bileseni ayni korumali baslikla ES256 JWS',
              reheader(h_c + '.' + b64u_encode(PAYLOAD) + '.' + b64u_encode(raw), {'alg': 'ES256', 'kid': 'reuse-ec'}),
              jws.Policy(keys=[ec_as_es256]), 'imza-gecersiz')

    # ---------------- N6 stripped / mixed multi-signature (General JSON)
    def general(*algs_, payload=PAYLOAD):
        return jws.sign(payload, [jws.Signer(keys[a], {'kid': keys[a].kid, 'typ': 'dc+sd-jwt'}, alg=a) for a in algs_],
                        'general')
    for second in ('EdDSA', 'ML-DSA-65', 'ML-DSA-65-ES256'):
        g = general('ES256', second)
        P = pol('ES256', second)
        t.pozitif('N6-coklu-imza', 'ES256+' + second, g, P)
        g1 = copy.deepcopy(g)
        g1['signatures'] = g1['signatures'][:1]
        t.negatif('N6-coklu-imza', 'ES256+%s -> %s soyuldu' % (second, second), g1, P, 'gerekli-alg-eksik')
        r_any = jws.verify(g1, jws.Policy(keys=[pub['ES256'], pub[second]], semantics='any'))
        t.K.bilgi('N6-coklu-imza', 'KONTROL(P0 any-valid): %s soyulmus -> %s' % (second, 'KABUL' if r_any.valid else 'RED'),
                  r_any.reason)
        r_and = jws.verify(g1, jws.Policy(keys=[pub['ES256'], pub[second]], semantics='all'))
        t.K.bilgi('N6-coklu-imza', 'KONTROL(P1 AND, beklenen kume YOK): %s soyulmus -> %s' % (second, 'KABUL' if r_and.valid else 'RED'),
                  r_and.reason)
        g2 = copy.deepcopy(g)
        g2['signatures'] = g2['signatures'][1:]
        t.negatif('N6-coklu-imza', 'ES256+%s -> ES256 soyuldu' % second, g2, P, 'gerekli-alg-eksik')
        g3 = copy.deepcopy(g)
        sb = b64u_decode(g3['signatures'][1]['signature'])
        g3['signatures'][1]['signature'] = b64u_encode(flip(sb, len(sb) // 2))
        t.negatif('N6-coklu-imza', 'ES256+%s, %s imzasi bozuk (T2)' % (second, second), g3, P, 'imza-gecersiz')
        other = general('ES256', second, payload=PAYLOAD2)
        g4 = copy.deepcopy(g)
        g4['signatures'][1] = other['signatures'][1]
        t.negatif('N6-coklu-imza', 'ES256+%s, %s imzasi baska yukten' % (second, second), g4, P, 'imza-gecersiz')
    g = general('ES256', 'ML-DSA-65')
    P = pol('ES256', 'ML-DSA-65')
    g5 = copy.deepcopy(g)
    g5['signatures'] = [g['signatures'][0], g['signatures'][0]]
    t.negatif('N6-coklu-imza', 'ES256 imzasi iki kez, ML-DSA-65 yok', g5, P, 'gerekli-alg-eksik')
    g6 = copy.deepcopy(g)
    k65 = keys['ML-DSA-65']
    pb = b64u_encode(json_bytes({'alg': 'ML-DSA-66', 'kid': k65.kid}))
    g6['signatures'].append({'protected': pb, 'signature': b64u_encode(algs.sign('ML-DSA-65', k65, (pb + '.' + g['payload']).encode()))})
    t.negatif('N6-coklu-imza', 'ES256+ML-DSA-65 + bilinmeyen alg imzasi (T4 tipi)', g6, P, 'alg-bilinmiyor')
    g7 = copy.deepcopy(g)
    g7['signatures'].append({'protected': b64u_encode(json_bytes({'alg': 'none'})), 'signature': ''})
    t.negatif('N6-coklu-imza', 'ES256+ML-DSA-65 + alg=none imzasi', g7, P, 'alg-none')
    g8 = general('ES256', 'ML-DSA-65')
    t.negatif('N6-coklu-imza', 'izin listesi yalniz ML-DSA-65 iken ES256 imzasi var (L1/L2, AND)', g8,
              jws.Policy(keys=[pub['ES256'], pub['ML-DSA-65']], allowed_algs=frozenset({'ML-DSA-65'})), 'alg-izinli-degil')

    # ---------------- N7 crit
    base_c = {'kid': keys['ML-DSA-65'].kid}
    cc = jws.sign(PAYLOAD, jws.Signer(keys['ML-DSA-65'], dict(base_c, crit=['x-pq-beklenti'], **{'x-pq-beklenti': 'ML-DSA-65'})), 'compact')
    t.negatif('N7-crit', 'anlasilmayan crit parametresi', cc, pol('ML-DSA-65'), 'crit-anlasilmadi')
    t.pozitif('N7-crit', 'ayni nesne, parametre anlasiliyor', cc, pol('ML-DSA-65', understood_crit=frozenset({'x-pq-beklenti'})))
    cc2 = jws.sign(PAYLOAD, jws.Signer(keys['ML-DSA-65'], dict(base_c, crit=['alg'])), 'compact')
    t.negatif('N7-crit', "crit kayitli parametre ('alg') listeliyor", cc2, pol('ML-DSA-65'), 'crit-gecersiz-ad')
    cc3 = jws.sign(PAYLOAD, jws.Signer(keys['ML-DSA-65'], dict(base_c, crit=[])), 'compact')
    t.negatif('N7-crit', 'crit bos dizi', cc3, pol('ML-DSA-65'), 'crit-gecersiz-bicim')
    cc4 = jws.sign(PAYLOAD, jws.Signer(keys['ML-DSA-65'], dict(base_c, crit=['x-yok'])), 'compact')
    t.negatif('N7-crit', 'crit listelenen parametre baslikta yok', cc4,
              pol('ML-DSA-65', understood_crit=frozenset({'x-yok'})), 'crit-listelenen-parametre-yok')
    fl2 = jws.sign(PAYLOAD, jws.Signer(keys['ML-DSA-65'], base_c, header={'crit': ['x-a'], 'x-a': 1}), 'flattened')
    t.negatif('N7-crit', 'crit korumasiz baslikta', fl2, pol('ML-DSA-65', understood_crit=frozenset({'x-a'})), 'korumasiz-parametre:crit')

    # ---------------- N8 x5c
    root_ec = pki.make_root('root-ec', derive_key('ES256', 't03/root-ec'), '/C=EU/O=T03/CN=Root EC', 1)
    root_ml = pki.make_root('root-ml', derive_key('ML-DSA-65', 't03/root-ml'), '/C=EU/O=T03/CN=Root ML', 2)
    int_ec = pki.make_cert('int-ec', derive_key('ES256', 't03/int-ec'), root_ec, '/C=EU/O=T03/CN=Int EC', 3, 'int')
    int_ml = pki.make_cert('int-ml', derive_key('ML-DSA-65', 't03/int-ml'), root_ml, '/C=EU/O=T03/CN=Int ML', 4, 'int')
    lk_ml = derive_key('ML-DSA-65', 't03/leaf-ml')
    lk_ec = derive_key('ES256', 't03/leaf-ec')
    leaf_ml = pki.make_cert('leaf-ml', lk_ml, int_ml, '/C=EU/O=T03/CN=Leaf ML', 5, san_dns=['issuer.example'])
    leaf_ml_ec = pki.make_cert('leaf-ml@int-ec', lk_ml, int_ec, '/C=EU/O=T03/CN=Leaf ML mixed', 6, san_dns=['issuer.example'])
    leaf_ec_ml = pki.make_cert('leaf-ec@int-ml', lk_ec, int_ml, '/C=EU/O=T03/CN=Leaf EC mixed', 7, san_dns=['issuer.example'])
    anchors = [root_ec.der, root_ml.der]
    PX = dict(trust_anchors=anchors, attime=pki.ATTIME)
    j_ok = jws.sign(PAYLOAD, jws.Signer(lk_ml, {'x5c': pki.x5c(leaf_ml, int_ml)}, alg='ML-DSA-65'), 'compact')
    t.pozitif('N8-x5c', 'tam-PQ zincir', j_ok, jws.Policy(required_algs=frozenset({'ML-DSA-65'}), x5c_pq_only=True, **PX))
    fl3 = jws.sign(PAYLOAD, jws.Signer(lk_ml, {}, header={'x5c': pki.x5c(leaf_ml, int_ml)}, alg='ML-DSA-65'), 'flattened')
    t.negatif('N8-x5c', 'x5c korumasiz baslikta', fl3, jws.Policy(**PX), 'korumasiz-parametre:x5c')
    t.negatif('N8-x5c', 'guven capasi listede yok', j_ok, jws.Policy(trust_anchors=[root_ec.der], attime=pki.ATTIME),
              'x5c-zincir-gecersiz')
    j_mix1 = jws.sign(PAYLOAD, jws.Signer(lk_ml, {'x5c': pki.x5c(leaf_ml_ec, int_ec)}, alg='ML-DSA-65'), 'compact')
    j_mix2 = jws.sign(PAYLOAD, jws.Signer(lk_ec, {'x5c': pki.x5c(leaf_ec_ml, int_ml)}, alg='ES256'), 'compact')
    for ad, j in (('karisik: ML-DSA yaprak + klasik ara CA', j_mix1), ('karisik: klasik yaprak + ML-DSA ara CA', j_mix2)):
        r = jws.verify(j, jws.Policy(**PX))
        t.K.bilgi('N8-x5c', 'KONTROL(zincir politikasi yok): %s -> %s' % (ad, 'KABUL' if r.valid else 'RED'),
                  [s.to_dict().get('x5c', {}).get('chain_class') for s in r.signatures])
        t.negatif('N8-x5c', ad + ' (x5c_pq_only)', j, jws.Policy(x5c_pq_only=True, **PX), 'x5c-klasik-halka')
    other = derive_key('ML-DSA-65', 't03/saldirgan')
    j_bad = jws.sign(PAYLOAD, jws.Signer(other, {'x5c': pki.x5c(leaf_ml, int_ml)}, alg='ML-DSA-65'), 'compact')
    t.negatif('N8-x5c', 'baska anahtarla imza, gecerli x5c', j_bad, jws.Policy(**PX), 'imza-gecersiz')
    j_kt = reheader(j_ok, {'alg': 'ML-DSA-65', 'x5c': pki.x5c(leaf_ec_ml, int_ml)})
    t.negatif('N8-x5c', 'x5c yaprak anahtari EC, alg ML-DSA-65', j_kt, jws.Policy(**PX))
    j_root = jws.sign(PAYLOAD, jws.Signer(lk_ml, {'x5c': ['!!!']}, alg='ML-DSA-65'), 'compact')
    t.negatif('N8-x5c', 'x5c base64 degil', j_root, jws.Policy(**PX), 'x5c-cozulemedi')

    # ---------------- N9 format
    c = one('ML-DSA-65')
    t.negatif('N9-bicim', 'compact 4 parca', c + '.AAAA', pol('ML-DSA-65'), 'bicim-hatasi')
    dup = b64u_encode(b'{"alg":"ML-DSA-65","alg":"ES256"}')
    t.negatif('N9-bicim', 'yinelenen baslik adi', dup + '.' + c.split('.', 1)[1], pol('ML-DSA-65'), 'bicim-hatasi')
    ce = one('ES256')
    h, p, s = ce.split('.')
    last = s[-1]
    alt = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
    # 64 bytes -> 86 characters; the low 4 bits of the last character are padding: non-canonical equivalent
    idx = alt.index(last)
    s2 = s[:-1] + alt[(idx & ~0xF) | ((idx + 1) & 0xF)]
    t.negatif('N9-bicim', 'kanonik olmayan base64url (dolgu bitleri)', h + '.' + p + '.' + s2, pol('ES256'), 'bicim-hatasi')
    gj = jws.sign(PAYLOAD, [jws.Signer(keys['ES256'], {'kid': keys['ES256'].kid}, alg='ES256')], 'general')
    gj['signatures'][0]['header'] = {'kid': 'x'}
    t.negatif('N9-bicim', 'korumali/korumasiz ayni ad (kid)', gj, pol('ES256'), 'bicim-hatasi')
    gj2 = jws.sign(PAYLOAD, [jws.Signer(keys['ES256'], {}, alg='ES256')], 'general')
    gj2['signature'] = 'x'
    t.negatif('N9-bicim', 'general JSON ust duzeyde signature', gj2, pol('ES256'), 'bicim-hatasi')
    kd = derive_key('ES256', 't03/dpop')
    dp = jws.sign(PAYLOAD, jws.Signer(kd, {'typ': 'dpop+jwt', 'jwk': kd.private_jwk(kid=False)}, alg='ES256'), 'compact')
    t.negatif('N9-bicim', "gomulu 'jwk' ozel anahtar iceriyor (DPoP)", dp, jws.Policy(allow_embedded_jwk=True),
              'jwk-ozel-anahtar-iceriyor')
    dp_ok = jws.sign(PAYLOAD, jws.Signer(kd, {'typ': 'dpop+jwt', 'jwk': kd.public_jwk(kid=False)}, alg='ES256'), 'compact')
    t.pozitif('N9-bicim', "gomulu 'jwk' acik anahtar (DPoP)", dp_ok, jws.Policy(allow_embedded_jwk=True, expected_typ='dpop+jwt'))
    t.negatif('N9-bicim', 'typ beklenenden farkli', dp_ok, jws.Policy(allow_embedded_jwk=True, expected_typ='kb+jwt'), 'typ-uyusmuyor')

    t.K.bilgi('genel', 'negatif', '%d/%d reddedildi' % tuple(t.neg))
    t.K.bilgi('genel', 'pozitif-kontrol', '%d/%d kabul edildi' % tuple(t.pos))
    return t.K.yaz(out, {'negatif': {'reddedilen': t.neg[0], 'toplam': t.neg[1]},
                         'pozitif_kontrol': {'kabul': t.pos[0], 'toplam': t.pos[1]}, 'tablo': t.tablo})


if __name__ == '__main__':
    o = main(sys.argv[1])
    sys.exit(0 if not o['kalan'] else 1)
