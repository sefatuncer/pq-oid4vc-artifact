#!/usr/bin/env python3
"""T12 — Validation of the COSE implementation (uretec/cbor.py, uretec/cose.py) with external vectors.

  A. KAYNAK: every algorithm/label/key id in cose.KAYNAK occurs VERBATIM in a corpus line (no guessing).
  B. RFC 9964 Appendix A.2 COSE (ML-DSA-44/65/87): the COSE_Key is decoded and re-encoded byte-identically (in insertion order);
     AKP COSE thumbprint (RFC 9964 §6) = kid; COSE_Sign1 is parsed; Sig_structure == raw_to_be_signed;
     the signature is verified; deterministic re-signing produces a BYTE-IDENTICAL COSE_Sign1; dilithium-py cross-verifies.
  C. draft-ietf-jose-pq-composite-sigs-04 Appendix A.2 COSE (6 composite): the seed/key/payload/M'/signature
     extracted from the CBOR diagnostic notation; protected header + Sig_structure with our encoding equal M' exactly;
     the composite signature is verified; the components are verified separately with the OpenSSL CLI and dilithium-py;
     the deterministic components (ML-DSA; EdDSA) are regenerated.
Usage: python t12_cose.py <corpus_text_folder> <external-vectors folder> <result_folder>
"""
import glob
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'signer', 'testler'))
sys.path.insert(0, '/opt/pq/testler')
from ortak import Kayit  # noqa: E402

from dilithium_py.ml_dsa import ML_DSA_44, ML_DSA_65, ML_DSA_87  # noqa: E402

from pqjose import composite, mldsa, openssl  # noqa: E402
from pqjose.keys import ECKey, MLDSAKey, OKPKey  # noqa: E402
from pqjose.params import COMPOSITE  # noqa: E402

from uretec import cbor, cose  # noqa: E402

DPY = {44: ML_DSA_44, 65: ML_DSA_65, 87: ML_DSA_87}
# -04 Appendix A.2 ML-DSA-87-ES384 (Figure 11): the SHA-512 of the shown Sig_structure ["Signature1", <<{1: -56, 4: h'10da59a01e274d3d'}>>,
# h'', payload] does not match the PH inside the shown M' (tried alg -70..-1, the kids of the 6 examples, no kid,
# canonical/insertion order, SHA-512/SHAKE256-64/SHA3-512; none matched). Both components of the signature are valid over the shown
# M'. Conclusion: the example cannot be verified as a COSE_Sign1 (erratum candidate). Its JOSE counterpart in Appendix A.1 is valid in T01.
BILINEN_TUTARSIZLIK = {'ML-DSA-87-ES384'}


def test_A(K, korpus):
    cache = {}
    for ad, (mid, satir, metin) in cose.KAYNAK.items():
        if mid not in cache:
            cache[mid] = open(os.path.join(korpus, mid + '.txt'), encoding='utf-8').read().split('\n')
        line = cache[mid][satir - 1] if satir - 1 < len(cache[mid]) else ''
        K.kontrol('A:KAYNAK', '%s -> %s:%d' % (ad, mid, satir), metin in line, line.strip()[:90])
    # are the table values consistent with the KAYNAK texts
    for alg, v in cose.ALG.items():
        mid, satir, metin = cose.KAYNAK['alg.' + alg]
        K.kontrol('A:ALG', '%s = %d kaynak metninde geciyor' % (alg, v), str(v) in metin)


def test_B(K, dis):
    for f in sorted(glob.glob(os.path.join(dis, 'RFC9964-COSE-*.json'))):
        v = json.load(open(f, encoding='utf-8'))
        o = v['veri']
        g = 'B:' + v['id']
        key_b = bytes.fromhex(o['key'])
        km = cbor.decode(key_b)
        K.kontrol(g, 'COSE_Key ekleme sirasiyla yeniden kodlaninca bayt-ayni', cbor.encode(km, canonical=False) == key_b)
        K.bilgi(g, 'COSE_Key kanonik (belirlenimci) sirada mi', cbor.is_canonical(key_b))
        k = cose.key_from_cose(km)
        K.kontrol(g, 'AKP anahtari: tohumdan acik anahtar == -1', isinstance(k, MLDSAKey) and k.pub == km[-1] and
                  k.pub == bytes.fromhex(o['raw_public_key']))
        tp = hashlib.sha256(cbor.encode({1: km[1], 3: km[3], -1: km[-1]})).digest()
        K.kontrol(g, 'AKP COSE parmak izi (RFC 9964 §6: kty, alg, pub) == kid', tp == km[2])
        s1 = bytes.fromhex(o['sign1'])
        p = cose.ayristir(s1)
        e = p['imzalar'][0]
        K.kontrol(g, 'COSE_Sign1 ayristirildi; korumali baslik {1: alg, 4: kid}',
                  p['tur'] == 'COSE_Sign1' and e['alg'] == km[3] and e['kid'] == km[2] and p['body_unprot'] == {})
        K.kontrol(g, 'Sig_structure (bizim kodlama) == raw_to_be_signed', e['tbs'] == bytes.fromhex(o['raw_to_be_signed']))
        K.kontrol(g, 'imza == raw_signature', e['imza'] == bytes.fromhex(o['raw_signature']))
        K.kontrol(g, 'COSE_Sign1 dogrulandi (pqjose)', cose.dogrula_imza(e, k))
        lvl = mldsa.SIZES and {-48: 44, -49: 65, -50: 87}[km[3]]
        K.kontrol(g, 'dilithium-py capraz dogrulama', DPY[lvl].verify(k.pub, e['tbs'], e['imza']))
        yapi = cose.sign1_yapi(p['payload'], k, cose.alg_adi(km[3]), prot_ek={cose.H_KID: km[2]}, unprot={},
                               deterministic=True)
        K.kontrol(g, 'belirlenimci yeniden imzalama: COSE_Sign1 BAYT-AYNI', cose.kodla(yapi, cose.TAG_SIGN1) == s1)


def _hex_bloklari(blok):
    return [re.sub(r'\s+', '', h) for h in re.findall(r"h'([0-9a-fA-F\s]*)'", blok)]


def test_C(K, korpus):
    txt = open(os.path.join(korpus, 'JOSECOMP.txt'), encoding='utf-8').read()
    a2 = txt[txt.rindex('A.2.  COSE'):txt.rindex('Appendix B.')]   # the first occurrences are in the table of contents
    bloklar = re.split(r'\n\s+Figure \d+: (ML-DSA-[0-9A-Za-z-]+)\n', a2)
    ornekler = list(zip(bloklar[1::2], bloklar[0:-1:2]))
    K.kontrol('C:genel', '-04 Ek A.2 COSE ornek sayisi 6', len(ornekler) == 6, [a for a, _ in ornekler])
    for alg, blok in ornekler:
        g = 'C:' + alg
        prm = COMPOSITE[alg]
        hx = _hex_bloklari(blok)
        seed, trad_raw, kid, pub, priv, kid2, aad, pl1, mp, kid3, pl2, sig = [bytes.fromhex(h) for h in hx]
        cv = int(re.search(r'3:\s*(-\d+),', blok).group(1))
        K.kontrol(g, 'COSE alg degeri = %d (-04 Tablo 6, talep edilen)' % cose.ALG[alg], cv == cose.ALG[alg])
        K.kontrol(g, 'cikarim tutarliligi (kid x3, payload x2, aad bos)', kid == kid2 == kid3 and pl1 == pl2 and aad == b'')
        k = cose.key_from_cose({1: 7, 3: cv, -1: pub, -2: priv})
        K.kontrol(g, 'COSE_Key priv = tohum || klasik ozel; pub tutarli', k.priv == priv and k.pub == pub and priv[:32] == seed)
        if prm['trad'] == 'ECDSA':
            K.kontrol(g, 'ECDSA d cikarimi == anahtar', k.trad.d_bytes() == trad_raw)
        else:
            K.kontrol(g, 'EdDSA tohumu == anahtar', k.trad.raw_priv() == trad_raw)
        pb = cose.prot({cose.H_ALG: cv, cose.H_KID: kid})
        tbs = cose.sig_structure1(pb, pl1)
        ml, tr = composite.split_signature(alg, sig)
        if alg in BILINEN_TUTARSIZLIK:
            # The draft example is internally inconsistent: the PH of the shown Sig_structure does not match M'; the signature is over the shown M'.
            K.kontrol(g, "BILINEN TUTARSIZLIK (erratum adayi) suruyor: PH(Sig_structure) != M' icindeki PH",
                      composite.message_representative(alg, tbs) != mp)
            K.kontrol(g, "imza bilesenleri taslagin GOSTERDIGI M' uzerinde gecerli",
                      openssl.pkey_verify(k.ml.public_pem(), mp, ml, ctx=prm['label']) and
                      openssl.dgst_verify(k.trad.public_pem(), mp, tr, prm['md']))
            ours = composite.sign(alg, k, tbs, deterministic=True)
            K.kontrol(g, 'ayni anahtar/baslik/yukle bizim COSE_Sign1 imzamiz gecerli (ic tutarli ornek)',
                      cose.dogrula_imza(cose.ayristir(cose.kodla([pb, {}, pl1, ours], cose.TAG_SIGN1))['imzalar'][0],
                                        k.public_only()))
            K.bilgi(g, 'not', 'COSE_Sign1 olarak dogrulanamaz; JOSE Ek A.1 esi (T01) gecerli; NOTLAR H')
            continue
        K.kontrol(g, "M' (bizim korumali baslik + Sig_structure kodlamamizla) BIREBIR", composite.message_representative(alg, tbs) == mp)
        comp = composite.verify_components(alg, k.public_only(), tbs, sig)
        K.kontrol(g, 'composite COSE imzasi dogrulandi (ml ve trad)', comp['ml'] and comp['trad'], comp)
        K.kontrol(g, 'dilithium-py: ML-DSA bileseni (ctx=Label)', DPY[prm['ml']].verify(k.ml.pub, mp, ml, ctx=prm['label']))
        K.kontrol(g, 'OpenSSL CLI: ML-DSA bileseni (ctx=Label)', openssl.pkey_verify(k.ml.public_pem(), mp, ml, ctx=prm['label']))
        if prm['trad'] == 'ECDSA':
            K.kontrol(g, 'OpenSSL CLI: ECDSA bileseni', openssl.dgst_verify(k.trad.public_pem(), mp, tr, prm['md']))
        else:
            K.kontrol(g, 'OpenSSL CLI: EdDSA bileseni', openssl.pkey_verify(k.trad.public_pem(), mp, tr))
        det_ml = mldsa.sign(prm['ml'], seed, mp, ctx=prm['label'], deterministic=True)
        K.bilgi(g, 'ML-DSA bileseni belirlenimci mi (taslak)', det_ml == ml)
        if prm['trad'] == 'EdDSA':
            K.kontrol(g, 'EdDSA bileseni bayt-ayni (belirlenimci)', k.trad.priv.sign(mp) == tr)
            if det_ml == ml:
                ours = composite.sign(alg, k, tbs, deterministic=True)
                yapi = [pb, {}, pl1, ours]
                K.kontrol(g, 'bizim COSE_Sign1 imzamiz bayt-ayni', ours == sig and cose.ayristir(
                    cose.kodla(yapi, cose.TAG_SIGN1))['imzalar'][0]['imza'] == sig)


def main(korpus, dis, out):
    K = Kayit('t12_cose')
    test_A(K, korpus)
    test_B(K, dis)
    test_C(K, korpus)
    return K.yaz(out)


if __name__ == '__main__':
    o = main(sys.argv[1], sys.argv[2], sys.argv[3])
    sys.exit(0 if not o['kalan'] else 1)
