"""T10-G (v1.3): v1.2 subset, COSE and L4c construction facts.

NOT an oracle: it only shows that the vectors were produced as defined in the manifest. Every signature is checked
in three independent ways: pqjose (the same library as the generation), the system OpenSSL CLI and (for ML-DSA) dilithium-py. Called
by t10_self_verification.py with 'v1.3'.
"""
import hashlib
import json
import os

from dilithium_py.ml_dsa import ML_DSA_65

from pqjose import algs, composite, jws, pki
from pqjose import x509 as X
from pqjose.keys import derive_bytes, derive_key, key_from_jwk
from pqjose.params import COMPOSITE
from pqjose.util import b64_std_encode, b64u_decode

from generator import cbor, cose, v13

ML65_SIG = 3309


def _beklenen(rec):
    s = rec['insa']
    return not (s.startswith('bozuk') or 'bozuk' in s.split(';')[0])


def _bilesen_beklenen(rec):
    s = rec['insa']
    if s.startswith('ML-DSA bileseni bozuk'):
        return (False, True)
    if s.startswith('ECDSA bileseni bozuk'):
        return (True, False)
    if s.startswith('bozuk: bayt '):
        n = int(s.split('bayt ')[1].split(',')[0])
        return (False, True) if n < ML65_SIG else (True, False)
    return (True, True)


def _tek_bit_farki(a: bytes, b: bytes):
    if len(a) != len(b):
        return None
    fark = [(i, x ^ y) for i, (x, y) in enumerate(zip(a, b)) if x != y]
    return fark if len(fark) == 1 and bin(fark[0][1]).count('1') == 1 else None


def test_G(K, kok, korpus, man, C, ossl):
    byid = {v['id']: v for v in man['vektorler']}
    yol = lambda v: os.path.join(kok, 'vectors', 'v1.3', v['dosya'])  # noqa: E731
    veri = lambda v: open(yol(v), 'rb').read()  # noqa: E731

    # ---------------------------------------------------------------- G1: v1.2 subset
    v12man = json.load(open(os.path.join(kok, 'vectors', 'v1.2', 'MANIFEST.json'), encoding='utf-8'))
    v12ids = {v['id']: v for v in v12man['vektorler']}
    ayni = [v['id'] for v in man['vektorler'] if v['id'] in v12ids and v == v12ids[v['id']] and
            open(os.path.join(kok, 'vectors', 'v1.2', v['dosya']), 'rb').read() == veri(v)]
    K.kontrol('G:v1.2-alt-kume', 'v1.2 vektorleri v1.3 icinde bayt-ayni ve manifest girdisi ayni (%d/%d)' % (
        len(ayni), len(v12ids)), len(ayni) == len(v12ids) == 153 and
        [v['id'] for v in man['vektorler'][:153]] == [v['id'] for v in v12man['vektorler']])
    K.kontrol('G:v1.2-alt-kume', 'b-uyumlu/vectors.json bayt-ayni',
              open(os.path.join(kok, 'vectors', 'v1.2', 'b-uyumlu', 'vectors.json'), 'rb').read() ==
              open(os.path.join(kok, 'vectors', 'v1.3', 'b-uyumlu', 'vectors.json'), 'rb').read())

    def sh(*p):
        return hashlib.sha256(open(os.path.join(kok, *p), 'rb').read()).hexdigest()
    K.kontrol('G:capalar', 'v1.3 manifestindeki v1.2/v1.1/v1 capalari ve iki anahtar SHA256SUMS ozeti dogru',
              man['v1_2_capalari'] == {'vektorler/v1.2/MANIFEST.json': sh('vectors', 'v1.2', 'MANIFEST.json'),
                                       'vektorler/v1.2/SHA256SUMS': sh('vectors', 'v1.2', 'SHA256SUMS')}
              and man['v1_1_capalari'] == v12man['v1_1_capalari'] and man['v1_capalari'] == v12man['v1_capalari']
              and man['anahtar_sha256sums'] == {'anahtarlar/v1/SHA256SUMS': sh('keys', 'v1', 'SHA256SUMS'),
                                                'anahtarlar/v1.3/SHA256SUMS': sh('keys', 'v1.3', 'SHA256SUMS')})
    yeni = [v for v in man['vektorler'] if v['id'] not in v12ids]
    K.kontrol('G:genel', 'yeni vektor sayisi 47 (COSE 45 + L4C 2)', len(yeni) == 47 and
              sum(v['aile'] == 'COSE' for v in yeni) == 45 and sum(v['aile'] == 'L4C' for v in yeni) == 2,
              man['yeni_dagilim'])

    # ---------------------------------------------------------------- G2: COSE id sources verbatim in the corpus
    cache = {}
    beklenen_kaynak = {k: '%s:%d %s' % v for k, v in cose.KAYNAK.items()}
    K.kontrol('G:kaynak', 'manifest cose_kimlik_kaynaklari == generator/cose.py KAYNAK',
              man['cose_kimlik_kaynaklari'] == beklenen_kaynak)
    for ad, (mid, satir, metin) in cose.KAYNAK.items():
        if mid not in cache:
            cache[mid] = open(os.path.join(korpus, mid + '.txt'), encoding='utf-8').read().split('\n')
        K.kontrol('G:kaynak', '%s -> %s:%d korpus satirinda birebir' % (ad, mid, satir),
                  satir - 1 < len(cache[mid]) and metin in cache[mid][satir - 1])

    # ---------------------------------------------------------------- G3: keys/v1.3
    d13 = os.path.join(kok, 'keys', 'v1.3')
    eski = C.keys[v13.ESKI_ROL]
    t = derive_key('ES256', v13.ESKI_ETIKET)
    t.kid = t.thumbprint()
    ozel = json.load(open(os.path.join(d13, 'ozel', 'issuer-eski__ES256.json'), encoding='utf-8'))
    K.kontrol('G:anahtar', 'eski ihracci anahtari "%s" etiketinden yeniden turetildi (ozel JWK ayni, kid=RFC 7638)' %
              v13.ESKI_ETIKET, t.private_jwk() == ozel and eski.kid == t.kid)
    v1_kids = {k.kid for r, k in C.keys.items() if r != v13.ESKI_ROL and '#' not in r}
    K.kontrol('G:anahtar', 'eski ihracci kid ve acik anahtari v1 anahtarlarindan farkli',
              eski.kid not in v1_kids and eski.public_jwk(kid=False) != C.keys['issuer/ES256'].public_jwk(kid=False))
    ck = json.load(open(os.path.join(d13, 'cose-anahtarlar.json'), encoding='utf-8'))
    for e in ck['anahtarlar']:
        m_b = bytes.fromhex(e['cose_key_hex'])
        m = cbor.decode(m_b)
        j = e['jwk']
        kid_ok = m[2] == b64u_decode(j['kid']) == bytes.fromhex(e['cose_kid_hex']) and j['kid'] == C.keys[e['rol']].kid
        if j['kty'] == 'EC':
            icerik = m[1] == 2 and m[-1] == 1 and m[-2] == b64u_decode(j['x']) and m[-3] == b64u_decode(j['y'])
        elif j['kty'] == 'OKP':
            icerik = m[1] == 1 and m[-1] == 6 and m[-2] == b64u_decode(j['x'])
        else:
            icerik = m[1] == 7 and m[3] == cose.ALG[j['alg']] and m[-1] == b64u_decode(j['pub']) and \
                cose.key_from_cose(m).public_jwk(kid=False) == key_from_jwk(j).public_jwk(kid=False)
        K.kontrol('G:anahtar', '%s COSE_Key (belirlenimci CBOR) == JWK; kid = base64url-cozulmus JWK kid' % e['rol'],
                  cbor.is_canonical(m_b) and kid_ok and icerik and j == C.keys[e['rol']].public_jwk())
    l4 = json.load(open(os.path.join(d13, 'acik-jwks-l4c.json'), encoding='utf-8'))
    goc = ['issuer/ES256', 'issuer/ML-DSA-65', 'issuer/ML-DSA-65-ES256']
    K.kontrol('G:anahtar', 'acik-jwks-l4c.json: goc etmis ihracci (3 anahtar) + eski ihracci (1), ihracci eslemesi',
              l4['keys'] == [C.keys[r].public_jwk() for r in goc] + [eski.public_jwk()] and
              l4['ihraccilar'] == {v13.A.ISS: [C.keys[r].kid for r in goc], v13.ESKI_ISS: [eski.kid]})

    # ---------------------------------------------------------------- G4: COSE vectors
    cv = [v for v in man['vektorler'] if v['artefakt'] == 'cose']
    K.kontrol('G:COSE', 'COSE nesneli vektor sayisi 46 (COSE 45 + L4C-COSE)', len(cv) == 46)
    P = {}
    for v in cv:
        data = veri(v)
        p = cose.ayristir(data)
        P[v['id']] = p
        ins = v['insa']
        ic = [p['payload']] + ([p['body_prot']] if p['body_prot'] else []) + [s['sp'] for s in p['imzalar'] if s['sp']]
        K.kontrol('G:COSE-yapi', '%s %s (etiket %d) == insa; dis ve ic CBOR belirlenimci' % (v['id'], p['tur'], p['etiket']),
                  p['tur'] == ins['cose']['yapi'] and p['etiket'] == ins['cose']['etiket'] and cbor.is_canonical(data)
                  and all(cbor.is_canonical(x) for x in ic))
        iss = v13.ESKI_ISS if v['aile'] == 'L4C' else v13.A.ISS
        K.kontrol('G:COSE-yapi', v['id'] + ' yuk == {"iss","vct","given_name"} (iss=%s)' % iss,
                  cbor.decode(p['payload']) == {'iss': iss, 'vct': v13.A.VCT, 'given_name': 'Erika'})
        if p['tur'] == 'COSE_Sign':
            K.kontrol('G:COSE-yapi', v['id'] + " govde korumali h'' ve korumasiz {}", p['body_prot'] == b'' and
                      p['body_unprot'] == {})
        K.kontrol('G:COSE-imza', v['id'] + ' imzaci sayisi == insa', len(p['imzalar']) == len(ins['imzalar']))
        for s, rec in zip(p['imzalar'], ins['imzalar']):
            etk = '%s #%d' % (v['id'], rec['sira'])
            konum_ok = s['sp_map'].get(cose.H_ALG) == rec['cose_alg'] and (
                p['tur'] == 'COSE_Sign1' or set(s['sp_map']) == {cose.H_ALG})
            K.kontrol('G:COSE-imza', '%s alg etiketi korumali baslikta = %r' % (etk, rec['cose_alg']), konum_ok)
            if rec['alg'] in cose.ALG:
                K.kontrol('G:COSE-imza', '%s alg degeri korpus kaynagiyla (%s)' % (etk, rec.get('kimlik_kaynagi')),
                          rec['cose_alg'] == cose.ALG[rec['alg']] and
                          rec.get('kimlik_kaynagi') == cose.kaynak_etiketi('alg.' + rec['alg']) and
                          (rec['alg'] not in cose.KAYITLI_DEGIL or 'KAYITLI DEGIL' in rec.get('kayit_durumu', '')))
            if rec['anahtar_rolu'] is None:
                kol = v['id'][len('COSE-K5')]
                K.kontrol('G:COSE-K5', '%s kayitsiz etiket %r, korumasiz baslik bos, %d B HKDF baytlari' % (
                    etk, v13.KAYITSIZ, v13.KAYITSIZ_BAYT),
                    s['alg'] == v13.KAYITSIZ and s['unprot'] == {} and
                    s['imza'] == derive_bytes('v1.3/COSE-K5%s/kayitsiz-imza' % kol, v13.KAYITSIZ_BAYT))
                continue
            key = C.keys[rec['anahtar_rolu']]
            if 'x5chain' in ins:
                K.kontrol('G:COSE-imza', etk + ' kid basligi yok (anahtar x5chain yapragindan)', s['kid'] is None)
            else:
                K.kontrol('G:COSE-imza', etk + ' korumasiz kid = base64url-cozulmus JWK kid',
                          s['unprot'] == {cose.H_KID: cose.kid_bytes(key)} and s['kid'] == bytes.fromhex(rec['cose_kid_hex']))
            gercek = ins['k10']['imza_uretim_alg'] if 'k10' in ins else rec['alg']
            bek = _beklenen(rec)
            K.kontrol('G:COSE-imza', '%s (%s) insa="%s" pqjose -> %s' % (etk, gercek, rec['insa'][:40],
                                                                        'gecerli' if bek else 'gecersiz'),
                      algs.verify(gercek, key, s['tbs'], s['imza']) == bek)
            K.kontrol('G:COSE-openssl', '%s (%s) OpenSSL CLI -> %s' % (etk, gercek, 'gecerli' if bek else 'gecersiz'),
                      ossl(gercek, key, s['tbs'], s['imza']) == bek)
            if gercek == 'ML-DSA-65':
                K.kontrol('G:COSE-dilithium', '%s dilithium-py -> %s' % (etk, 'gecerli' if bek else 'gecersiz'),
                          ML_DSA_65.verify(key.pub, s['tbs'], s['imza']) == bek)
            if gercek in COMPOSITE:
                comp = composite.verify_components(gercek, key, s['tbs'], s['imza'])
                b = _bilesen_beklenen(rec)
                ml, _tr = composite.split_signature(gercek, s['imza'])
                mp = composite.message_representative(gercek, s['tbs'])
                K.kontrol('G:COSE-composite', '%s bilesen durumu (ml, ecdsa) == %s; dilithium-py ML bileseni (ctx=Label)' % (
                    etk, b), (comp['ml'], comp['trad']) == b and
                    ML_DSA_65.verify(key.ml.pub, mp, ml, ctx=COMPOSITE[gercek]['label']) == b[0], comp)
            if 'k10' in ins:
                k10 = ins['k10']
                K.kontrol('G:COSE-K10', '%s baslik alg=%r (%s), anahtar %s; anahtar baslik alg\'ini desteklemiyor' % (
                    v['id'], s['alg'], k10['baslik_alg'], k10['anahtar_turu']),
                    s['alg'] == cose.alg_deger(k10['baslik_alg']) == k10['baslik_cose_alg'] and
                    not algs.key_supports(key, k10['baslik_alg']))
                jwk_ok = cose.cose_key(key) == cbor.decode(bytes.fromhex(
                    v['dogrulama_girdileri']['cose_key_hex'][rec['cose_kid_hex']]))
                K.kontrol('G:COSE-K10', v['id'] + ' dogrulama_girdileri.cose_key_hex == rol acik COSE_Key', jwk_ok)
        if 'x5chain' in ins:
            x = ins['x5chain']
            zincir = p['body_prot_map'].get(cose.H_X5CHAIN) if x['korumali'] else p['body_unprot'].get(cose.H_X5CHAIN)
            diger = p['body_unprot'].get(cose.H_X5CHAIN) if x['korumali'] else p['body_prot_map'].get(cose.H_X5CHAIN)
            K.kontrol('G:COSE-x5chain', '%s x5chain (33) %s baslikta, digerinde yok' % (
                v['id'], 'korumali' if x['korumali'] else 'korumasiz'), isinstance(zincir, list) and diger is None)
            r = X.validate_x5c([b64_std_encode(dd) for dd in zincir], C.anchors, pki.ATTIME)
            K.kontrol('G:COSE-x5chain', '%s zincir OpenSSL ile gecerli; sinif == %s; yaprak anahtari == imzalayan' % (
                v['id'], x['sinif']), r.ok and r.chain_class == x['sinif'] and r.leaf_key is not None and
                r.leaf_key.public_jwk(kid=False) == C.keys[ins['imzalar'][0]['anahtar_rolu']].public_jwk(kid=False),
                r.reason)

    # ---------------------------------------------------------------- G5: construction relations between cases
    def imzacilar(vid):
        return [(s['sp'], s['unprot'], s['imza']) for s in P[vid]['imzalar']]
    k3 = imzacilar('COSE-K3_X_soyuldu')
    K.kontrol('G:iliski', 'K3: tek imzaci == K1K/K1P/K1C ilk imzacisi (uc kolda ayni)',
              all(k3 == imzacilar('COSE-K1%s_iki_gecerli' % a)[:1] for a in 'KPC'))
    for a in 'KPC':
        k1 = imzacilar('COSE-K1%s_iki_gecerli' % a)
        k2 = imzacilar('COSE-K2%s_X_bozuk' % a)
        fark = _tek_bit_farki(k1[1][2], k2[1][2])
        K.kontrol('G:iliski', 'K2%s: K1%s ile ayni; yalniz X imzasinda tek bit (bayt 5) farkli' % (a, a),
                  k1[0] == k2[0] and k1[1][:2] == k2[1][:2] and fark is not None and fark[0][0] == 5, fark)
        K.kontrol('G:iliski', 'K4%s: tek imzaci == K1%s ikinci imzacisi (ayni Sig_structure, belirlenimci)' % (a, a),
                  imzacilar('COSE-K4%s_yalniz_X' % a) == k1[1:])
        K.kontrol('G:iliski', 'K5%s: ilk iki imzaci == K1%s' % (a, a), imzacilar('COSE-K5%s_arti_kayitsiz' % a)[:2] == k1)
    for alg in ('ES256', 'EdDSA', 'ML-DSA-65'):
        a, b = P['COSE-VPLUS_' + alg], P['COSE-VMINUS_' + alg]
        fark = _tek_bit_farki(a['imzalar'][0]['imza'], b['imzalar'][0]['imza'])
        K.kontrol('G:iliski', 'V-_%s: V+ ile ayni; imzada tek bit (orta bayt) farkli' % alg,
                  a['body_prot'] == b['body_prot'] and a['body_unprot'] == b['body_unprot'] and a['payload'] == b['payload']
                  and fark is not None and fark[0][0] == len(a['imzalar'][0]['imza']) // 2)
    k6 = P['COSE-K6_composite_gecerli']['imzalar'][0]['imza']
    for vid, bolum in (('COSE-K7_ml_bileseni_bozuk', 'ml'), ('COSE-K7_ecdsa_bileseni_bozuk', 'ecdsa')):
        fark = _tek_bit_farki(k6, P[vid]['imzalar'][0]['imza'])
        K.kontrol('G:iliski', '%s: K6 ile tek bit farki %s bileseninde' % (vid, bolum), fark is not None and (
            (fark[0][0] < ML65_SIG) == (bolum == 'ml')), fark)

    # ---------------------------------------------------------------- G6: MR4 and Ed25519 counterparts
    for v in [x for x in cv if 'mr4' in x['insa']]:
        mr = v['insa']['mr4']
        order = mr['yeni_siradaki_ozgun_indeksler']
        try:
            ok = v13.cose_mr4_denetimi(veri(byid[mr['kaynak_vektor']]), veri(v), order)
        except RuntimeError as ex:
            ok = str(ex)
        K.kontrol('G:MR4', '%s: sira %s; govde/yuk ve her COSE_Signature bayt-ayni tasindi' % (v['id'], order), ok is True, ok)
        src = byid[mr['kaynak_vektor']]
        K.kontrol('G:MR4', v['id'] + ' insa kayitlari permutasyonla birebir tasindi',
                  [dict(r, sira=None, ozgun_sira=None) for r in v['insa']['imzalar']] ==
                  [dict(src['insa']['imzalar'][oi], sira=None, ozgun_sira=None) for oi in order] and
                  [r['ozgun_sira'] for r in v['insa']['imzalar']] == order)
    for v in [x for x in cv if x['id'].endswith('-ED25519')]:
        try:
            deg = v13.cose_es_denetimi(veri(byid[v['insa']['etiket_esi']]), veri(v))
            ok = deg == v['insa']['etiket_degisikligi']['yeniden_hesaplanan_imza_sirasi']
        except RuntimeError as ex:
            ok, deg = False, str(ex)
        K.kontrol('G:ED25519', '%s: %s ile yalniz EdDSA(-8)->Ed25519(-19) etiketi ve o imza farkli' % (
            v['id'], v['insa']['etiket_esi']), ok and v['kol'] == 'kontrol-Ed25519', deg)
    eksik = [v['id'] for v in cv if v['kol'] == 'kontrol-EdDSA' and
             any(s['alg'] == cose.ALG['EdDSA'] for s in P[v['id']]['imzalar']) and v['id'] + '-ED25519' not in byid]
    K.kontrol('G:ED25519', 'EdDSA (-8) etiketi tasiyan her kontrol COSE vektorunun -ED25519 esi var', not eksik, eksik)

    # ---------------------------------------------------------------- G7: L4c
    gk = C.keys['issuer/ES256']
    vj = byid['L4C-JOSE_eski_ES256']
    o = veri(vj).decode('ascii')
    h, pl, sg = o.split('.')
    hdr, yuk, sig = json.loads(b64u_decode(h)), json.loads(b64u_decode(pl)), b64u_decode(sg)
    K.kontrol('G:L4c', 'L4C-JOSE: baslik {alg:ES256, kid:eski, typ:JWT}; yuk iss=%s; insa.ihracci tutarli' % v13.ESKI_ISS,
              hdr == {'alg': 'ES256', 'kid': eski.kid, 'typ': 'JWT'} and yuk['iss'] == v13.ESKI_ISS and
              vj['insa']['ihracci']['iss'] == v13.ESKI_ISS and vj['insa']['ihracci']['kid'] == eski.kid)
    pub = eski.public_only()
    pub.kid = eski.kid
    r = jws.verify(o, jws.Policy(keys=[pub], allowed_algs=frozenset({'ES256'})))
    tbs = (h + '.' + pl).encode()
    K.kontrol('G:L4c', 'L4C-JOSE: eski ihracci anahtariyla gecerli (pqjose + OpenSSL CLI)',
              r.valid and ossl('ES256', eski, tbs, sig), r.reason)
    K.kontrol('G:L4c', 'L4C-JOSE: goc etmis ihraccinin ES256 anahtariyla gecersiz (ayri kimlik)',
              not algs.verify('ES256', gk, tbs, sig))
    pc = P['L4C-COSE_eski_ES256']
    s = pc['imzalar'][0]
    K.kontrol('G:L4c', 'L4C-COSE: kid = eski ihracci; eski anahtarla gecerli (pqjose + OpenSSL); goc etmis ES256 ile gecersiz',
              s['kid'] == cose.kid_bytes(eski) and algs.verify('ES256', eski, s['tbs'], s['imza']) and
              ossl('ES256', eski, s['tbs'], s['imza']) and not algs.verify('ES256', gk, s['tbs'], s['imza']))
    for vid in ('VPLUS_ES256', 'VPLUS_ML-DSA-65', 'CMP00_gecerli_referans'):
        yk = json.loads(b64u_decode(veri(byid[vid]).decode('ascii').split('.')[1]))
        K.kontrol('G:L4c', 'goc etmis ihracci JOSE karsiligi %s mevcut (iss=%s)' % (vid, v13.A.ISS), yk['iss'] == v13.A.ISS)
    for vid in ('COSE-VPLUS_ES256', 'COSE-VPLUS_ML-DSA-65', 'COSE-K6_composite_gecerli'):
        K.kontrol('G:L4c', 'goc etmis ihracci COSE karsiligi %s mevcut (iss=%s)' % (vid, v13.A.ISS),
                  cbor.decode(P[vid]['payload'])['iss'] == v13.A.ISS and P[vid]['imzalar'][0]['kid'] != cose.kid_bytes(eski))
    for v in yeni:
        K.bilgi('G:boyut', v['id'], v['bayt'])
