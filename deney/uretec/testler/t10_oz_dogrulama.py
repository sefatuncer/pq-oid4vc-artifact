#!/usr/bin/env python3
"""T10 — Ureticinin oz-dogrulamasi (arac ici tutarlilik; hedef kutuphane OLCULMEZ).

  A. Spesifikasyon ornekleri: TSL Ek C (1/2/4/8 bit; cozme + kodlama), RFC 9901 4.2.3 ozet ornegi
  B. MANIFEST butunlugu: her dosyanin SHA-256'si ve SHA256SUMS
  C. Belirlenimcilik: gecici dizine yeniden uretim -> tum dosyalar bayt-bayt ayni
  D. Insa gercekleri: her vektorde manifestin 'insa' alanindaki iddialar (hangi imza gecerli/bozuk,
     composite bilesen durumu, x5c zincir sinifi, client_id=x509_hash, durum listesi degerleri, DPoP jwk,
     KB-JWT sd_hash kapsami) pqjose/OpenSSL ile yeniden hesaplanarak teyit edilir.
     Bu, oracle DEGILDIR: yalniz vektorun tanimlandigi gibi uretildigini gosterir.
Kullanim: python t10_oz_dogrulama.py <uretec_kok> <korpus_metin_dizini> <sonuc_dizini> [v1|v1.1|v1.2|v1.3]
  v1.3 ek olarak: G. v1.2 alt kumesi bayt-ayni; COSE (yapi, kimlik kaynaklari korpusta, imza gecerlilikleri pqjose +
  OpenSSL CLI + dilithium-py, K2/K3/K5 insa iliskileri, K7 bilesen durumu, K8/K9 x5chain, K10, V+/V-, MR4, Ed25519
  esleri); L4c eski ihracci (ayri anahtar/kid/iss; JOSE ve COSE); anahtarlar/v1.3 (turetme, COSE_Key == JWK).
  v1.2 ek olarak: F. v1.1 alt kumesi bayt-ayni; MR4 esleri (icerik korunur), T7 (K5), K10, V+/V-, yeni Ed25519 esleri
  v1.1 ek olarak: E. v1 alt kumesi bayt-ayni; Ed25519 esleri (yapisal denetim, OpenSSL capraz dogrulama,
  pqjose'de 'Ed25519' etiketinin kabulu ve izin listesinde etiket duyarliligi).
"""
import glob
import hashlib
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
# ortak.py (Kayit): imzalayici/testler — imajda /opt/pq/testler; depoda ../../imzalayici/testler
sys.path.insert(0, os.path.join(HERE, '..', '..', 'imzalayici', 'testler'))
sys.path.insert(0, '/opt/pq/testler')
from ortak import Kayit  # noqa: E402

from pqjose import algs, composite, jws, pki  # noqa: E402
from pqjose import x509 as X  # noqa: E402
from pqjose.keys import MLDSAKey, default_alg, key_from_jwk  # noqa: E402
from pqjose.params import COMPOSITE, PREFIX  # noqa: E402
from pqjose.util import b64u_decode, b64u_encode, json_bytes  # noqa: E402

from uretec import sdjwt, statuslist  # noqa: E402
from uretec.uret import main as uret_main  # noqa: E402

SURUM = 'v1'   # main() ile 'v1' ya da 'v1.1' olarak ayarlanir


def unwrap_json(txt):
    out, ins = [], False
    for c in txt:
        if ins:
            if c == '"':
                ins = False
                out.append(c)
            elif c not in '\n\r \t':
                out.append(c)
        else:
            if c == '"':
                ins = True
            out.append(c)
    return ''.join(out)


def test_A(K, korpus):
    txt = open(os.path.join(korpus, 'TSL.txt'), encoding='utf-8').read()
    for bits, sec in ((1, 'C.1'), (2, 'C.2'), (4, 'C.3'), (8, 'C.4')):
        m = re.search(r'^%s\.\s.*?$(.*?)^C\.\d|^%s\.\s.*?$(.*)' % (re.escape(sec), re.escape(sec)), txt, re.S | re.M)
        blk = m.group(1) or m.group(2)
        st = {int(i): int(v, 2) for i, v in re.findall(r'status\[(\d+)\]\s*=\s*0b([01]+)', blk)}
        js = re.search(r'JSON encoding:\s*(\{.*?\})', blk, re.S).group(1)
        obj = json.loads(unwrap_json(js))
        ours = statuslist.encode(st, 2 ** 20, bits)
        dec_theirs = statuslist.decode(obj['lst'], bits)
        dec_ours = statuslist.decode(ours, bits)
        K.kontrol('A:TSL-EkC', '%s bits=%d cozme(bizim bayt dizisi == Ek C)' % (sec, bits),
                  dec_ours == dec_theirs and obj['bits'] == bits, {'durum_sayisi': len(st)})
        ok_idx = all(statuslist.get_status(obj['lst'], i, bits) == v for i, v in st.items())
        K.kontrol('A:TSL-EkC', '%s indeks degerleri' % sec, ok_idx)
        K.bilgi('A:TSL-EkC', '%s kodlama bayt-ayni (zlib 9)' % sec, ours == obj['lst'])
    t9901 = open(os.path.join(korpus, 'RFC9901.txt'), encoding='utf-8').read()
    m = re.search(r'Disclosure W\s*\n\s*(\S+)\s*\n\s*(\S+)\s+for the family_name.*?\n\s*(\S+)\.', t9901, re.S)
    disc = 'W' + m.group(1) + m.group(2)
    K.kontrol('A:RFC9901', '4.2.3 ozet ornegi', sdjwt.digest(disc) == m.group(3), {'ifsa': disc, 'ozet': m.group(3)})


def test_B(K, kok):
    man = json.load(open(os.path.join(kok, 'vektorler', SURUM, 'MANIFEST.json'), encoding='utf-8'))
    bad = []
    for v in man['vektorler']:
        data = open(os.path.join(kok, 'vektorler', SURUM, v['dosya']), 'rb').read()
        if hashlib.sha256(data).hexdigest() != v['sha256'] or len(data) != v['bayt']:
            bad.append(v['id'])
    K.kontrol('B:manifest', 'dosya SHA-256 == manifest (%d vektor)' % len(man['vektorler']), not bad, bad)
    dizinler = (('vektorler', SURUM), ('anahtarlar', 'v1')) + ((('anahtarlar', 'v1.3'),) if SURUM == 'v1.3' else ())
    for sub, sv in dizinler:
        d = os.path.join(kok, sub, sv)
        sums = dict(reversed(l.strip().split('  ', 1)) for l in open(os.path.join(d, 'SHA256SUMS'), encoding='utf-8'))
        mism = [rel for rel, h in sums.items() if hashlib.sha256(open(os.path.join(d, rel), 'rb').read()).hexdigest() != h]
        K.kontrol('B:manifest', '%s/%s SHA256SUMS (%d dosya)' % (sub, sv, len(sums)), not mism, mism)
    return man


def test_C(K, kok):
    if SURUM == 'v1.3':
        import pqjose
        from uretec import __version__
        from uretec.v13 import uret_v13
        sv = pqjose.versions()
        sv['uretec'] = __version__
        with tempfile.TemporaryDirectory() as td:
            uret_v13(td, kok, sv)
            for sub, fn in (('vektorler', 'SHA256SUMS'), ('vektorler', 'MANIFEST.json'), ('vektorler', 'MANIFEST.csv'),
                            ('anahtarlar', 'SHA256SUMS')):
                a = open(os.path.join(kok, sub, 'v1.3', fn), 'rb').read()
                b = open(os.path.join(td, sub, 'v1.3', fn), 'rb').read()
                K.kontrol('C:belirlenimcilik', '%s/v1.3/%s yeniden uretim bayt-bayt ayni' % (sub, fn), a == b)
        return
    if SURUM == 'v1.2':
        import pqjose
        from uretec import __version__
        from uretec.v12 import uret_v12
        sv = pqjose.versions()
        sv['uretec'] = __version__
        with tempfile.TemporaryDirectory() as td:
            uret_v12(td, kok, sv)
            for fn in ('SHA256SUMS', 'MANIFEST.json'):
                a = open(os.path.join(kok, 'vektorler', 'v1.2', fn), 'rb').read()
                b = open(os.path.join(td, 'vektorler', 'v1.2', fn), 'rb').read()
                K.kontrol('C:belirlenimcilik', 'vektorler/v1.2/%s yeniden uretim bayt-bayt ayni' % fn, a == b)
        return
    if SURUM == 'v1.1':
        import pqjose
        from uretec import __version__
        from uretec.v11 import uret_v11
        sv = pqjose.versions()
        sv['uretec'] = __version__
        with tempfile.TemporaryDirectory() as td:
            uret_v11(td, kok, sv)
            for fn in ('SHA256SUMS', 'MANIFEST.json'):
                a = open(os.path.join(kok, 'vektorler', 'v1.1', fn), 'rb').read()
                b = open(os.path.join(td, 'vektorler', 'v1.1', fn), 'rb').read()
                K.kontrol('C:belirlenimcilik', 'vektorler/v1.1/%s yeniden uretim bayt-bayt ayni' % fn, a == b)
        return
    with tempfile.TemporaryDirectory() as td:
        uret_main(td)
        for sub in ('vektorler', 'anahtarlar'):
            a = open(os.path.join(kok, sub, 'v1', 'SHA256SUMS'), encoding='utf-8').read()
            b = open(os.path.join(td, sub, 'v1', 'SHA256SUMS'), encoding='utf-8').read()
            K.kontrol('C:belirlenimcilik', '%s/v1 yeniden uretim bayt-bayt ayni' % sub, a == b)


# ------------------------------------------------------------------ D: insa gercekleri
class Ctx:
    def __init__(self, kok):
        self.kok = kok
        self.keys = {}
        roller = json.load(open(os.path.join(kok, 'anahtarlar', 'v1', 'roller.json'), encoding='utf-8'))
        for rol, r in roller['roller'].items():
            self.keys[rol] = key_from_jwk(json.load(open(os.path.join(kok, 'anahtarlar', 'v1', r['ozel_jwk']))))
        ck = self.keys['issuer/ML-DSA-65-ES256']
        self.keys['issuer/ML-DSA-65-ES256#trad'] = ck.trad
        self.keys['issuer/ML-DSA-65-ES256#ml'] = ck.ml
        self.anchors = [X.pem_to_der(open(os.path.join(kok, 'anahtarlar', 'v1', 'pki', n), 'rb').read())
                        for n in ('root-ec.pem', 'root-ml.pem')]
        self.roller = roller
        r13 = os.path.join(kok, 'anahtarlar', 'v1.3', 'roller.json')
        if SURUM == 'v1.3' and os.path.isfile(r13):
            for rol, r in json.load(open(r13, encoding='utf-8'))['roller'].items():
                self.keys[rol] = key_from_jwk(json.load(open(os.path.join(kok, 'anahtarlar', 'v1.3', r['ozel_jwk']))))


def load(kok, v, surum=None):
    p = os.path.join(kok, 'vektorler', surum or SURUM, v['dosya'])
    s = open(p, 'rb').read().decode('utf-8')
    return json.loads(s) if v['dosya'].endswith('.json') else s


def jws_parts(obj):
    """(serilestirme, [(protected_b64, protected, header, sig_bytes)], payload_b64)"""
    if isinstance(obj, str):
        jwt = obj.split('~')[0]
        h, p, s = jwt.split('.')
        return [(h, json.loads(b64u_decode(h)), None, b64u_decode(s) if s else b'')], p
    if 'signatures' in obj:
        return [(e.get('protected'), json.loads(b64u_decode(e['protected'])) if e.get('protected') else {},
                 e.get('header'), b64u_decode(e['signature']) if e['signature'] else b'') for e in obj['signatures']], obj['payload']
    return [(obj.get('protected'), json.loads(b64u_decode(obj['protected'])), obj.get('header'),
             b64u_decode(obj['signature']))], obj['payload']


def eff_alg(label, key):
    return label if algs.is_supported(label) and algs.key_supports(key, label) else default_alg(key)


def check_sigs(K, C, v, obj):
    sigs, pl = jws_parts(obj)
    ins = v['insa'].get('imzalar', [])
    K.kontrol('D:' + v['aile'], v['id'] + ' imza sayisi', len(sigs) == len(ins), [len(sigs), len(ins)])
    res = []
    for (pb, prot, hdr, sig), r in zip(sigs, ins):
        if r.get('alg') == 'none' or r.get('anahtar_rolu') is None:
            if r.get('alg') == 'none':
                K.kontrol('D:' + v['aile'], '%s #%d alg=none bos imza' % (v['id'], r['sira']), prot.get('alg') == 'none' and sig == b'')
            else:
                K.kontrol('D:' + v['aile'], '%s #%d anahtarsiz etiket %s, bayt mevcut' % (v['id'], r['sira'], r['alg']),
                          prot.get('alg') == r['alg'] and len(sig) > 0)
            continue
        key = C.keys[r['anahtar_rolu']]
        alg = eff_alg(r['alg'], key)
        tbs = ((pb or '') + '.' + pl).encode()
        ok = algs.verify(alg, key, tbs, sig)
        s = r['insa']
        beklenen = not s.startswith('bozuk') and 'bozuk' not in s.split(';')[0]
        if v['aile'] == 'CMP':
            res.append((ok, tbs, sig, key, alg))
            continue
        K.kontrol('D:' + v['aile'], '%s #%d (%s) insa="%s"' % (v['id'], r['sira'], r['alg'], s[:50]), ok == beklenen, ok)
        K.kontrol('D:' + v['aile'], '%s #%d alg etiketi' % (v['id'], r['sira']), prot.get('alg', (hdr or {}).get('alg')) == r['alg'])
        res.append((ok, tbs, sig, key, alg))
    return res


CMP_BEKLENEN = {  # (ml, trad) ya da 'serilestirme'
    'CMP00_gecerli_referans': (True, True), 'CMP01_ml_bileseni_bozuk': (False, True),
    'CMP02_ecdsa_bileseni_bozuk': (True, False), 'CMP03_ecdsa_der_uzunluk_bozuk': 'serilestirme',
    'CMP04_ecdsa_ham_rs': 'serilestirme', 'CMP05_ecdsa_asgari_olmayan_der': 'serilestirme',
    'CMP06_sonda_artik_bayt': 'serilestirme', 'CMP07_yalniz_ml_bileseni': 'serilestirme',
    'CMP08_bilesenler_farkli_iletilerden': (False, True), 'CMP09_ml_bileseni_ctx_bos': (False, True),
    'CMP10_onozet_sha256': (False, False), 'CMP11_bos_ctx_uzunlugu_yok': (False, False),
    'CMP14_ed25519_ml_bileseni_bozuk': (False, True), 'CMP15_ed25519_eddsa_bileseni_bozuk': (True, False),
    'CMP16_bilesen_sirasi_ters': 'serilestirme',
}


def check_cmp(K, C, v, obj):
    res = check_sigs(K, C, v, obj)
    ok, tbs, sig, key, alg = res[0]
    vid = v['id']
    if vid in CMP_BEKLENEN:
        comp = composite.verify_components(alg, key, tbs, sig)
        b = CMP_BEKLENEN[vid]
        got = 'serilestirme' if comp['hata'] else (comp['ml'], comp['trad'])
        K.kontrol('D:CMP', vid + ' bilesen durumu', got == b, comp)
    p = COMPOSITE['ML-DSA-65-ES256']
    ck = C.keys['issuer/ML-DSA-65-ES256']
    from pqjose import mldsa
    if vid in ('CMP10_onozet_sha256', 'CMP11_bos_ctx_uzunlugu_yok', 'CMP09_ml_bileseni_ctx_bos'):
        ml, tr = composite.split_signature(alg, sig)
        ph = 'sha256' if vid.startswith('CMP10') else p['ph']
        zero = b'' if vid.startswith('CMP11') else b'\x00'
        mp = PREFIX + p['label'] + zero + composite.prehash(ph, tbs)
        ctx = b'' if vid.startswith('CMP09') else p['label']
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import ec
        try:
            ck.trad.pub.verify(tr, mp, ec.ECDSA(hashes.SHA256()))
            tr_ok = True
        except Exception:  # noqa: BLE001
            tr_ok = False
        K.kontrol('D:CMP', vid + " sapmali M'/ctx ile tutarli (uygulayici hatasi taklidi dogru kuruldu)",
                  mldsa.verify(65, ck.ml.pub, mp, ml, ctx) and tr_ok)
    if vid in ('CMP12_ayrilabilirlik_ecdsa_ES256', 'CMP13_ayrilabilirlik_ml_MLDSA65'):
        ref = load(C.kok, next(x for x in C.man['vektorler'] if x['id'] == 'CMP00_gecerli_referans'))
        h0, p0, _ = ref.split('.')
        mp = composite.message_representative('ML-DSA-65-ES256', (h0 + '.' + p0).encode())
        K.kontrol('D:CMP', vid + ' JWS olarak gecersiz (bilesen M\' uzerinde)', not ok)
        if vid.startswith('CMP12'):
            from pqjose.der import ecdsa_raw_to_der
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import ec
            try:
                ck.trad.pub.verify(ecdsa_raw_to_der(sig, 'P-256'), mp, ec.ECDSA(hashes.SHA256()))
                g = True
            except Exception:  # noqa: BLE001
                g = False
        else:
            g = mldsa.verify(65, ck.ml.pub, mp, sig, p['label'])
        K.kontrol('D:CMP', vid + " imza gercek bir bilesen (M' uzerinde gecerli)", g)


def check_x5c(K, C, v, obj):
    sigs, _ = jws_parts(obj)
    pb, prot, hdr, sig = sigs[0]
    x = v['insa'].get('x5c', {})
    if 'korumali_zincir' in x:
        for yer, ch in (('korumali', prot['x5c']), ('korumasiz', hdr['x5c'])):
            r = X.validate_x5c(ch, C.anchors, pki.ATTIME)
            K.kontrol('D:X5C', '%s %s x5c zinciri gecerli' % (v['id'], yer), r.ok, r.reason)
        return
    ch = prot.get('x5c') if 'x5c' in prot else (hdr or {}).get('x5c')
    K.kontrol('D:X5C', v['id'] + ' x5c korumali mi == insa', ('x5c' in prot) == x.get('korumali', True))
    r = X.validate_x5c(ch, C.anchors, pki.ATTIME)
    K.kontrol('D:X5C', v['id'] + ' x5c zinciri OpenSSL ile gecerli', r.ok, r.openssl_output[-120:])
    if 'sinif' in x:
        K.kontrol('D:X5C', v['id'] + ' zincir sinifi == insa (%s)' % x['sinif'], r.chain_class == x['sinif'], r.chain_class)
    if 'kok_x5c_icinde' in x:
        K.kontrol('D:X5C', v['id'] + ' kok x5c icinde mi == insa', any(c['kendinden_imzali'] for c in r.chain) == x['kok_x5c_icinde'])
    K.kontrol('D:X5C', v['id'] + ' yaprak anahtari == imzalayan rol', r.leaf_key is not None and
              r.leaf_key.public_jwk(kid=False) == C.keys[v['insa']['imzalar'][0]['anahtar_rolu']].public_jwk(kid=False))


def check_sdjwt(K, C, v, obj):
    """Ifsa ozetleri, tuzlar ve (varsa) KB-JWT sd_hash kapsami."""
    if isinstance(obj, str):
        parts = obj.split('~')
        issuer_jwt, discl, kb = parts[0], parts[1:-1], parts[-1]
        payload = json.loads(b64u_decode(issuer_jwt.split('.')[1]))
        jwt_for_hash = [issuer_jwt]
    else:
        h0 = obj['signatures'][0].get('header') if 'signatures' in obj else obj.get('header')
        discl, kb = h0.get('disclosures', []), h0.get('kb_jwt', '')
        payload = json.loads(b64u_decode(obj['payload']))
        ss = obj['signatures'] if 'signatures' in obj else [obj]
        jwt_for_hash = [s['protected'] + '.' + obj['payload'] + '.' + s['signature'] for s in ss]
    alld = []
    sdjwt._collect_digests(payload, alld)
    dg = [sdjwt.digest(d) for d in discl]
    K.kontrol('D:' + v['aile'], v['id'] + ' her ifsa ozeti yukte var', all(x in alld for x in dg), len(discl))
    if kb:
        kbc = json.loads(b64u_decode(kb.split('.')[1]))
        hk = key_from_jwk(payload['cnf']['jwk'])
        kh = json.loads(b64u_decode(kb.split('.')[0]))
        K.kontrol('D:' + v['aile'], v['id'] + ' KB-JWT cnf anahtariyla gecerli', algs.verify(
            kh['alg'], hk, '.'.join(kb.split('.')[:2]).encode(), b64u_decode(kb.split('.')[2])))
        idx = v['insa'].get('kb_jwt', {}).get('sd_hash_imza_sirasi', 0)
        cands = [sdjwt.sd_hash_compact(j, discl) for j in jwt_for_hash]
        K.kontrol('D:' + v['aile'], v['id'] + ' sd_hash, insa\'daki imza sirasini (%d) kapsiyor' % idx,
                  kbc['sd_hash'] == (cands[idx] if idx < len(cands) else sdjwt.sd_hash_compact(
                      load(C.kok, next(x for x in C.man['vektorler'] if x['id'] == 'VP05_GJ_ES256_MLDSA65_kb'))['signatures'][idx]
                      ['protected'] + '.' + obj['payload'] + '.' +
                      load(C.kok, next(x for x in C.man['vektorler'] if x['id'] == 'VP05_GJ_ES256_MLDSA65_kb'))['signatures'][idx]
                      ['signature'], discl)))
        K.kontrol('D:' + v['aile'], v['id'] + ' KB aud/nonce', kbc['aud'] == v['dogrulama_girdileri'].get('kb_aud') and
                  kbc['nonce'] == v['dogrulama_girdileri'].get('kb_nonce'))


def test_D(K, kok, man):
    C = Ctx(kok)
    C.man = man
    for v in man['vektorler']:
        if v['artefakt'] == 'cose':
            continue   # COSE (v1.3): test_G
        obj = load(kok, v)
        fam = v['aile']
        if fam == 'CMP':
            check_cmp(K, C, v, obj)
        elif v['serilestirme'] == 'dcapi-json-parametre':
            K.kontrol('D:REQ', v['id'] + ' imzasiz DC API istegi', obj['protocol'] == 'openid4vp-v1-unsigned')
            K.kontrol('D:REQ', v['id'] + ' client_id var mi == insa', ('client_id' in obj['data']) == ('client_id' in v['insa']))
        elif v['id'] == 'VC10_ikili_ihrac':
            for i, c in enumerate(obj['credentials']):
                vv = dict(v, insa={'imzalar': [dict(v['insa']['kimlik_bilgileri'][i], sira=0)]})
                check_sigs(K, C, dict(vv, id=v['id'] + '[%d]' % i), c['credential'])
                check_sdjwt(K, C, dict(vv, id=v['id'] + '[%d]' % i), c['credential'])
        else:
            if v['id'] == 'X5C09_korumali_ve_korumasiz_x5c':
                K.kontrol('D:X5C', v['id'] + ' pqjose ayristirici ayriklik ihlalini yakalar',
                          not jws.verify({k: val for k, val in obj.items()}, jws.Policy()).valid)
            check_sigs(K, C, v, obj)
            if 'x5c' in v['insa']:
                check_x5c(K, C, v, obj)
            if v['artefakt'].startswith('sd-jwt'):
                check_sdjwt(K, C, v, obj)
        if fam == 'REQ' and 'client_id' in v['insa'] and v['serilestirme'] == 'compact' and 'x5c' in v['insa']:
            prot = json.loads(b64u_decode(obj.split('.')[0]))
            K.kontrol('D:REQ', v['id'] + ' client_id == x509_hash(yaprak)',
                      prot.get('x5c') and v['insa']['client_id'] == 'x509_hash:' + X.x509_hash(X.decode_x5c(prot['x5c'])[0]))
        if v['id'] == 'REQ04_coklu_imzali':
            for e in obj['signatures']:
                pr = json.loads(b64u_decode(e['protected']))
                K.kontrol('D:REQ', 'REQ04 client_id korumali baslikta ve x509_hash(yaprak)',
                          pr['client_id'] == 'x509_hash:' + X.x509_hash(X.decode_x5c(pr['x5c'])[0]))
            K.kontrol('D:REQ', 'REQ04 yukte client_id yok (A.3.2.2)', 'client_id' not in json.loads(b64u_decode(obj['payload'])))
        if fam == 'TSL':
            sl = json.loads(b64u_decode(obj.split('.')[1]))['status_list']
            K.kontrol('D:TSL', v['id'] + ' durum degerleri == insa', all(
                statuslist.get_status(sl['lst'], int(i), sl['bits']) == s for i, s in v['insa']['durumlar'].items()))
            K.kontrol('D:TSL', v['id'] + ' typ=statuslist+jwt', json.loads(b64u_decode(obj.split('.')[0]))['typ'] == 'statuslist+jwt')
        if fam == 'DPOP':
            h = json.loads(b64u_decode(obj.split('.')[0]))
            if v['id'].startswith('DPOP10'):
                K.kontrol('D:DPOP', v['id'] + ' jwk ozel uye (priv) iceriyor', 'priv' in h['jwk'])
            else:
                K.kontrol('D:DPOP', v['id'] + ' jwk == rol acik anahtari', h['jwk'] == C.keys[v['insa']['imzalar'][0]['anahtar_rolu']]
                          .public_jwk(kid=False))
            if 'bayt' in v['insa']:
                K.kontrol('D:DPOP', v['id'] + ' bayt == manifest', len(obj) == v['insa']['bayt'])
        if fam == 'CRIT':
            sigs, _ = jws_parts(obj)
            pb, prot, hdr, _s = sigs[0]
            where = prot if v['insa'].get('crit_korumali', True) else (hdr or {})
            K.kontrol('D:CRIT', v['id'] + ' crit konumu/degeri == insa', where.get('crit') == v['insa']['crit'])


def test_E(K, kok, man):
    """v1.1: v1 alt kumesi bayt-ayni; Ed25519 esleri yapisal denetim, OpenSSL capraz dogrulama, kitaplik kabulu."""
    from pqjose import openssl
    from uretec.v11 import ED_DAYANAK, koruma_denetimi
    v1man = json.load(open(os.path.join(kok, 'vektorler', 'v1', 'MANIFEST.json'), encoding='utf-8'))
    v1ids = {v['id']: v for v in v1man['vektorler']}
    ayni = [v['id'] for v in man['vektorler'] if v['id'] in v1ids and
            open(os.path.join(kok, 'vektorler', 'v1', v['dosya']), 'rb').read() ==
            open(os.path.join(kok, 'vektorler', 'v1.1', v['dosya']), 'rb').read() and v == v1ids[v['id']]]
    K.kontrol('E:v1-alt-kume', 'v1 vektorleri v1.1 icinde bayt-ayni ve manifest girdisi ayni (%d/%d)' % (len(ayni), len(v1ids)),
              len(ayni) == len(v1ids) == 93)
    K.kontrol('E:v1-alt-kume', 'b-uyumlu/vectors.json bayt-ayni',
              open(os.path.join(kok, 'vektorler', 'v1', 'b-uyumlu', 'vectors.json'), 'rb').read() ==
              open(os.path.join(kok, 'vektorler', 'v1.1', 'b-uyumlu', 'vectors.json'), 'rb').read())

    def sh(*p):
        return hashlib.sha256(open(os.path.join(kok, *p), 'rb').read()).hexdigest()
    K.kontrol('E:capalar', 'v1.1 manifestindeki v1 capalari ve anahtar SHA256SUMS ozeti dogru',
              man['v1_capalari'] == {'vektorler/v1/MANIFEST.json': sh('vektorler', 'v1', 'MANIFEST.json'),
                                     'vektorler/v1/SHA256SUMS': sh('vektorler', 'v1', 'SHA256SUMS')}
              and man['anahtar_sha256sums'] == sh('anahtarlar', 'v1', 'SHA256SUMS') and man['anahtar_dizini'] == 'anahtarlar/v1')
    kontrol_v1 = [v['id'] for v in v1man['vektorler'] if v['kol'] == 'kontrol-EdDSA']
    esler = [v for v in man['vektorler'] if v['id'].endswith('-ED25519')]
    K.kontrol('E:esler', 'her kontrol-EdDSA vektorunun tam bir esi var (%d)' % len(kontrol_v1),
              sorted(e['insa']['v1_esi'] for e in esler) == sorted(kontrol_v1) and
              all(e['id'] == e['insa']['v1_esi'] + '-ED25519' for e in esler))
    C = Ctx(kok)
    pub = {}
    for r, k in C.keys.items():
        if '#' in r:
            continue
        pk = k.public_only()
        pk.kid = k.kid
        pub[r] = pk
    for e in esler:
        v1 = v1ids[e['insa']['v1_esi']]
        o1, o2 = load(kok, v1, 'v1'), load(kok, e, 'v1.1')
        try:
            deg = koruma_denetimi(o1, o2)
            ok = deg == e['insa']['etiket_degisikligi']['yeniden_hesaplanan_imza_sirasi']
        except RuntimeError as ex:
            ok, deg = False, str(ex)
        K.kontrol('E:esler', e['id'] + " v1'den yalniz EdDSA->Ed25519 basligi ve o imza farkli", ok, deg)
        K.kontrol('E:esler', e['id'] + ' kol/dayanak (RFC 9864)', e['kol'] == 'kontrol-Ed25519' and
                  all(d in e['dayanak'] for d in ED_DAYANAK))
        sigs, pl = jws_parts(o2)
        algs_in = []
        for (pb, prot, hdr, sig), rec in zip(sigs, e['insa']['imzalar']):
            algs_in.append(prot['alg'])
            if prot['alg'] != 'Ed25519':
                continue
            key = C.keys[rec['anahtar_rolu']]
            tbs = (pb + '.' + pl).encode()
            beklenen = not rec['insa'].startswith('bozuk')
            K.kontrol('E:openssl-capraz', '%s #%d Ed25519 imzasi OpenSSL CLI ile %s' % (
                e['id'], rec['sira'], 'gecerli' if beklenen else 'gecersiz (insa: bozuk)'),
                openssl.pkey_verify(key.public_pem(), tbs, sig) == beklenen)
        req = frozenset(algs_in)
        if e['aile'] == 'T':
            keys = [pub[r] for r in ('issuer/ES256', 'issuer/EdDSA', 'issuer/ML-DSA-65', 'issuer/ML-DSA-65-ES256')]
            r = jws.verify(o2, jws.Policy(keys=keys, allowed_algs=req, required_algs=req))
            beklenen = not any(x['insa'].startswith('bozuk') for x in e['insa']['imzalar'])
            K.kontrol('E:kitaplik', '%s pqjose (allowed=required=%s) -> %s' % (
                e['id'], sorted(req), 'KABUL' if beklenen else 'RED (insa: bozuk)'), r.valid == beklenen, r.reason)
            if beklenen:
                r2 = jws.verify(o2, jws.Policy(keys=keys, allowed_algs=(req - {'Ed25519'}) | {'EdDSA'}))
                K.kontrol('E:kitaplik', e['id'] + " izin listesinde yalniz 'EdDSA' -> Ed25519 imzasi alg-izinli-degil",
                          (not r2.valid) and any(s.alg == 'Ed25519' and s.reason == 'alg-izinli-degil' for s in r2.signatures))
                r3 = jws.verify(o1, jws.Policy(keys=keys, allowed_algs=req))
                K.kontrol('E:kitaplik', v1['id'] + " (v1) izin listesinde yalniz 'Ed25519' -> EdDSA imzasi alg-izinli-degil",
                          (not r3.valid) and any(s.alg == 'EdDSA' and s.reason == 'alg-izinli-degil' for s in r3.signatures))
        elif e['aile'] == 'VC':
            pol = jws.Policy(trust_anchors=C.anchors, attime=pki.ATTIME, keys=[pub['issuer/EdDSA']],
                             allowed_algs=req, required_algs=req)
            ok, why, claims, _ = sdjwt.verify_sdjwt(o2, pol)
            K.kontrol('E:kitaplik', '%s SD-JWT VC (ES256 x5c + Ed25519 kid) pqjose -> KABUL' % e['id'],
                      ok and claims.get('given_name') == 'Erika', why)
        elif e['aile'] == 'DPOP':
            r = jws.verify(o2, jws.Policy(allow_embedded_jwk=True, expected_typ='dpop+jwt',
                                          allowed_algs=frozenset({'Ed25519'})))
            K.kontrol('E:kitaplik', '%s DPoP (gomulu jwk, alg=Ed25519) pqjose -> KABUL' % e['id'], r.valid, r.reason)
            K.bilgi('E:boyut', e['id'], {'bayt': len(o2), 'v1_bayt': len(o1)})


def _ossl_dogrula(alg, key, m, sig):
    """Bagimsiz capraz dogrulama (sistem OpenSSL CLI)."""
    from pqjose import openssl
    from pqjose.der import ecdsa_raw_to_der
    if alg in ('ES256', 'ES384'):
        crv = 'P-256' if alg == 'ES256' else 'P-384'
        if len(sig) != (64 if alg == 'ES256' else 96):
            return False
        return openssl.dgst_verify(key.public_pem(), m, ecdsa_raw_to_der(sig, crv), 'sha256' if alg == 'ES256' else 'sha384')
    if alg in ('EdDSA', 'Ed25519', 'Ed448', 'ML-DSA-44', 'ML-DSA-65', 'ML-DSA-87'):
        return openssl.pkey_verify(key.public_pem(), m, sig)
    if alg in COMPOSITE:
        p = COMPOSITE[alg]
        try:
            ml, tr = composite.split_signature(alg, sig)
        except ValueError:
            return False
        mp = composite.message_representative(alg, m)
        ok_ml = openssl.pkey_verify(key.ml.public_pem(), mp, ml, ctx=p['label'])
        ok_tr = (openssl.dgst_verify(key.trad.public_pem(), mp, tr, p['md']) if p['trad'] == 'ECDSA'
                 else openssl.pkey_verify(key.trad.public_pem(), mp, tr))
        return ok_ml and ok_tr
    return False


def test_F(K, kok, man):
    """v1.2: v1.1 alt kumesi bayt-ayni; MR4 esleri (icerik korunur), T7 (K5), K10, V+/V-, yeni Ed25519 esleri."""
    from pqjose.keys import derive_bytes
    from uretec.v11 import koruma_denetimi
    from uretec.v12 import KAYITSIZ, KAYITSIZ_BAYT, mr4_denetimi
    v11man = json.load(open(os.path.join(kok, 'vektorler', 'v1.1', 'MANIFEST.json'), encoding='utf-8'))
    v11ids = {v['id']: v for v in v11man['vektorler']}
    ayni = [v['id'] for v in man['vektorler'] if v['id'] in v11ids and v == v11ids[v['id']] and
            open(os.path.join(kok, 'vektorler', 'v1.1', v['dosya']), 'rb').read() ==
            open(os.path.join(kok, 'vektorler', 'v1.2', v['dosya']), 'rb').read()]
    K.kontrol('F:v1.1-alt-kume', 'v1.1 vektorleri v1.2 icinde bayt-ayni ve manifest girdisi ayni (%d/%d)' % (len(ayni), len(v11ids)),
              len(ayni) == len(v11ids) == 100)
    K.kontrol('F:v1.1-alt-kume', 'b-uyumlu/vectors.json bayt-ayni',
              open(os.path.join(kok, 'vektorler', 'v1.1', 'b-uyumlu', 'vectors.json'), 'rb').read() ==
              open(os.path.join(kok, 'vektorler', 'v1.2', 'b-uyumlu', 'vectors.json'), 'rb').read())

    def sh(*p):
        return hashlib.sha256(open(os.path.join(kok, *p), 'rb').read()).hexdigest()
    K.kontrol('F:capalar', 'v1.2 manifestindeki v1.1 ve v1 capalari, anahtar SHA256SUMS dogru',
              man['v1_1_capalari'] == {'vektorler/v1.1/MANIFEST.json': sh('vektorler', 'v1.1', 'MANIFEST.json'),
                                       'vektorler/v1.1/SHA256SUMS': sh('vektorler', 'v1.1', 'SHA256SUMS')}
              and man['v1_capalari'] == {'vektorler/v1/MANIFEST.json': sh('vektorler', 'v1', 'MANIFEST.json'),
                                         'vektorler/v1/SHA256SUMS': sh('vektorler', 'v1', 'SHA256SUMS')}
              and man['anahtar_sha256sums'] == sh('anahtarlar', 'v1', 'SHA256SUMS'))
    C = Ctx(kok)
    byid = {v['id']: v for v in man['vektorler']}
    yeni = [v for v in man['vektorler'] if v['id'] not in v11ids]
    K.bilgi('F:genel', 'yeni vektor sayisi', len(yeni))

    def gecerli_mi(rec, pb, pl, sig):
        if rec.get('anahtar_rolu') is None:
            return None
        key = C.keys[rec['anahtar_rolu']]
        return algs.verify(eff_alg(rec['alg'], key), key, ((pb or '') + '.' + pl).encode(), sig)

    # ---- MR4
    for v in [x for x in yeni if 'mr4' in x['insa']]:
        mr = v['insa']['mr4']
        src_v = byid[mr['kaynak_vektor']]
        src, perm = load(kok, src_v), load(kok, v)
        order = mr['yeni_siradaki_ozgun_indeksler']
        try:
            tasindi = mr4_denetimi(src, perm, order)
            ok = tasindi == mr['ifsalar_yeni_ilk_basliga_tasindi']
        except RuntimeError as ex:
            ok, tasindi = False, str(ex)
        K.kontrol('F:MR4', '%s: sira %s; yuk + her (protected, imza) cifti korunmus%s' % (
            v['id'], order, '; ifsalar yeni ilk baslikta' if tasindi is True else ''), ok, tasindi)
        s_src, pl = jws_parts(src)
        s_perm, _ = jws_parts(perm)
        g_src = [gecerli_mi(r, sp[0], pl, sp[3]) for r, sp in zip(src_v['insa']['imzalar'], s_src)]
        g_perm = [gecerli_mi(r, sp[0], pl, sp[3]) for r, sp in zip(v['insa']['imzalar'], s_perm)]
        K.kontrol('F:MR4', v['id'] + ' imza gecerlilikleri permutasyonla birebir tasindi',
                  g_perm == [g_src[oi] for oi in order] and
                  [r['ozgun_sira'] for r in v['insa']['imzalar']] == order, {'kaynak': g_src, 'es': g_perm})
        if v['artefakt'] == 'sd-jwt-vc' and 'SIRA' in v['id']:
            roles = [r['anahtar_rolu'] for r in v['insa']['imzalar']]
            keys = [C.keys[r].public_only() for r in roles]
            for k_, r in zip(keys, roles):
                k_.kid = C.keys[r].kid
            req = frozenset(r['alg'] for r in v['insa']['imzalar'])
            ok, why, cl, _ = sdjwt.verify_sdjwt(perm, jws.Policy(trust_anchors=C.anchors, attime=pki.ATTIME, keys=keys,
                                                                 required_algs=req))
            ok0, _, cl0, _ = sdjwt.verify_sdjwt(src, jws.Policy(trust_anchors=C.anchors, attime=pki.ATTIME, keys=keys,
                                                                required_algs=req))
            K.kontrol('F:MR4', v['id'] + ' SD-JWT VC (ifsalar yeni ilk baslikta) pqjose ile kaynakla ayni sonuc ve talepler',
                      ok == ok0 and cl == cl0, why)
        if 'kb_jwt' in v['insa'] and 'SIRA' in v['id']:
            h0 = perm['signatures'][0]['header']
            kbc = json.loads(b64u_decode(h0['kb_jwt'].split('.')[1]))
            cands = [sdjwt.sd_hash_compact(s['protected'] + '.' + perm['payload'] + '.' + s['signature'], h0['disclosures'])
                     for s in perm['signatures']]
            idx = v['insa']['kb_jwt']['sd_hash_imza_sirasi']
            K.kontrol('F:MR4-disi', '%s: KB sd_hash artik %d. siradaki imzayi bagliyor (ilk imzayi degil)' % (v['id'], idx),
                      kbc['sd_hash'] == cands[idx] and kbc['sd_hash'] != cands[0])
    # ---- T7 (K5)
    for a in 'KPC':
        v = byid['T7%s_plus_kayitsiz' % a]
        o, t1 = load(kok, v), load(kok, byid['T1%s_both_valid' % a])
        K.kontrol('F:K5-T7', v['id'] + ' ilk iki imza T1%s ile bayt-ayni' % a, o['signatures'][:2] == t1['signatures'] and
                  o['payload'] == t1['payload'])
        u3 = o['signatures'][2]
        K.kontrol('F:K5-T7', v['id'] + ' ucuncu imza: alg=%s, %d B HKDF baytlari' % (KAYITSIZ, KAYITSIZ_BAYT),
                  json.loads(b64u_decode(u3['protected'])) == {'alg': KAYITSIZ} and
                  b64u_decode(u3['signature']) == derive_bytes('v1.2/T7%s/kayitsiz-imza' % a, KAYITSIZ_BAYT))
        roles = ('issuer/ES256', 'issuer/EdDSA', 'issuer/ML-DSA-65', 'issuer/ML-DSA-65-ES256')
        keys = []
        for r in roles:
            pk = C.keys[r].public_only()
            pk.kid = C.keys[r].kid
            keys.append(pk)
        r_and = jws.verify(o, jws.Policy(keys=keys))
        K.kontrol('F:K5-T7', v['id'] + ' pqjose AND: ucuncu imza alg-bilinmiyor (fail-closed)',
                  (not r_and.valid) and r_and.signatures[2].reason == 'alg-bilinmiyor')
        r_any = jws.verify(o, jws.Policy(keys=keys, semantics='any'))
        K.bilgi('F:K5-T7', v['id'] + ' KONTROL(any-valid)', 'KABUL' if r_any.valid else 'RED')
    # ---- K10
    for v in [x for x in yeni if 'k10' in x['insa']]:
        o = load(kok, v)
        info = v['insa']['k10']
        key = C.keys[info['anahtar_rolu']]
        h, p, s = o.split('.')
        m, sig = (h + '.' + p).encode(), b64u_decode(s)
        hdr = json.loads(b64u_decode(h))
        K.kontrol('F:K10', '%s: baslik alg=%s, anahtar %s; imza gercek anahtarla (%s) gecerli' % (
            v['id'], hdr['alg'], info['anahtar_turu'], info['imza_uretim_alg']),
            hdr['alg'] == info['baslik_alg'] and algs.verify(info['imza_uretim_alg'], key, m, sig) and
            not algs.key_supports(key, hdr['alg']))
        K.kontrol('F:K10', v['id'] + ' OpenSSL CLI capraz dogrulama (gercek anahtar algoritmasiyla)',
                  _ossl_dogrula(info['imza_uretim_alg'], key, m, sig))
        jk = key_from_jwk(v['dogrulama_girdileri']['jwk'])
        K.kontrol('F:K10', v['id'] + ' dogrulama_girdileri.jwk == rol acik anahtari',
                  jk.public_jwk() == key.public_jwk())
        r = jws.verify(o, jws.Policy(keys=[jk]))
        K.kontrol('F:K10', v['id'] + ' pqjose (L3 anahtar-alg baglama) -> RED',
                  (not r.valid) and r.signatures[0].reason == 'anahtar-yok-ya-da-alg-uyumsuz', r.signatures[0].reason)
    # ---- V+ / V-
    for v in [x for x in yeni if x['aile'] == 'V']:
        o = load(kok, v)
        rec = v['insa']['imzalar'][0]
        key = C.keys[rec['anahtar_rolu']]
        h, p, s = o.split('.')
        alg = json.loads(b64u_decode(h))['alg']
        beklenen = not rec['insa'].startswith('bozuk')
        r = jws.verify(o, jws.Policy(keys=[key_from_jwk(v['dogrulama_girdileri']['jwk'])], allowed_algs=frozenset({alg})))
        K.kontrol('F:V', '%s: pqjose %s' % (v['id'], 'KABUL' if beklenen else 'RED'), r.valid == beklenen, r.reason)
        K.kontrol('F:V', '%s: OpenSSL CLI %s' % (v['id'], 'gecerli' if beklenen else 'gecersiz'),
                  _ossl_dogrula(alg, key, (h + '.' + p).encode(), b64u_decode(s)) == beklenen)
    # ---- yeni Ed25519 esleri
    for v in [x for x in yeni if x['id'].endswith('-ED25519')]:
        es_kaynak = v['insa']['etiket_esi']
        try:
            deg = koruma_denetimi(load(kok, byid[es_kaynak]), load(kok, v))
            ok = deg == v['insa']['etiket_degisikligi']['yeniden_hesaplanan_imza_sirasi']
        except RuntimeError as ex:
            ok, deg = False, str(ex)
        K.kontrol('F:ED25519', '%s: %s ile yalniz EdDSA->Ed25519 basligi ve o imza farkli' % (v['id'], es_kaynak), ok, deg)
        o = load(kok, v)
        sigs, pl = jws_parts(o)
        for (pb, prot, hdr, sig), rec in zip(sigs, v['insa']['imzalar']):
            if prot.get('alg') != 'Ed25519':
                continue
            key = C.keys[rec['anahtar_rolu']]
            gercek = v['insa']['k10']['imza_uretim_alg'] if 'k10' in v['insa'] else 'Ed25519'
            beklenen = not rec['insa'].startswith('bozuk')
            K.kontrol('F:ED25519', '%s #%d OpenSSL CLI (%s) %s' % (v['id'], rec['sira'], gercek,
                                                                 'gecerli' if beklenen else 'gecersiz (insa: bozuk)'),
                      _ossl_dogrula(gercek, key, ((pb or '') + '.' + pl).encode(), sig) == beklenen)
    eksik = []
    for v in yeni:
        if v['kol'] != 'kontrol-EdDSA':
            continue
        sigs, _ = jws_parts(load(kok, v))
        if any(s[1].get('alg') == 'EdDSA' for s in sigs) and v['id'] + '-ED25519' not in byid:
            eksik.append(v['id'])
    K.kontrol('F:ED25519', 'EdDSA etiketi tasiyan her yeni kontrol vektorunun -ED25519 esi var', not eksik, eksik)


def main(kok, korpus, out, surum='v1'):
    global SURUM
    SURUM = surum
    K = Kayit('t10_oz_dogrulama' if surum == 'v1' else 't10_oz_dogrulama_' + surum)
    test_A(K, korpus)
    man = test_B(K, kok)
    test_C(K, kok)
    test_D(K, kok, man)
    if surum == 'v1.1':
        test_E(K, kok, man)
    if surum == 'v1.2':
        test_F(K, kok, man)
    if surum == 'v1.3':
        from t10_cose import test_G
        test_G(K, kok, korpus, man, Ctx(kok), _ossl_dogrula)
    return K.yaz(out)


if __name__ == '__main__':
    o = main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else 'v1')
    sys.exit(0 if not o['kalan'] else 1)
