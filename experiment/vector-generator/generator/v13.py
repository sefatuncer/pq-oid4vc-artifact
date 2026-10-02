"""Test vector set v1.3 = v1.2 (153 vectors, BYTE-IDENTICAL) + MINIMAL additions (Oracle A N-0 and N-2; approved by the study lead).

A) COSE (RFC 9052): COSE_Sign (tag 98) and COSE_Sign1 (tag 18). Ids verbatim from the corpus (generator/cose.py KAYNAK):
   ES256 = -7 (RFC9053:248; RFC 9864 §4.2.2 "Deprecated"), EdDSA = -8 (RFC9053:365; "Deprecated"), Ed25519 = -19
   (RFC9864:225), ML-DSA-65 = -49 (RFC9964:367), ML-DSA-65-ES256 = -55 (JOSECOMP:1268 "TBD (request assignment -55)":
   requested, NOT REGISTERED). Cases in every arm: K1, K2, K3 (shared), K4, K5 (unregistered tstr alg "X-KAYITSIZ-1"),
   K10 (two directions), V+/V- (COSE_Sign1), MR4 (K1/K2 signer order reversed); composite only: K6, K7 (ML and ECDSA separately);
   arm-independent: K8 (x5chain, ML-DSA-65 leaf + classical intermediate CA), K9 (unprotected x5chain). K11 is not applicable in COSE.
   Ed25519 (-19) counterparts of the EdDSA-labelled vectors of the control arm.
B) L4c: an "old issuer" with a separate identity (iss https://legacy-issuer.example, key issuer-eski/ES256, derivation label
   v1.3/issuer-eski/ES256): JOSE compact and COSE_Sign1, ES256 only. The vectors of the migrated issuer EXIST and are
   reused (not regenerated because they would be byte-identical): JOSE VPLUS_ML-DSA-65 / CMP00 / VPLUS_ES256;
   COSE COSE-VPLUS_ML-DSA-65 / COSE-K6 / COSE-VPLUS_ES256 (BATTERY-MAPPING.md).
The frozen v1/, v1.1/, v1.2/ and keys/v1/ are only READ. New key: keys/v1.3/. NO oracle decision is written.
Manifest values such as 'anahtarlar/v1/acik-jwks.json' are recorded paths inside the run containers (mount point
/anahtarlar = keys/); they keep their names so that regeneration stays byte-identical.
Usage: python -m generator.v13 <output_root> [<frozen_root>]
"""
import copy
import csv
import hashlib
import json
import os
import shutil
import sys
import tempfile

import pqjose
from pqjose import algs
from pqjose.keys import derive_bytes, derive_key
from pqjose.params import alg_class
from pqjose.util import json_bytes

from . import __version__
from . import artefakt as A
from . import cbor, cose, v12
from .anahtar import AnahtarSeti
from .vektorler import SIMDI, Uretici

SURUM = 'v1.3'
ESKI_ISS = 'https://legacy-issuer.example'
ESKI_ROL = 'issuer-eski/ES256'
ESKI_ETIKET = 'v1.3/issuer-eski/ES256'
KAYITSIZ = v12.KAYITSIZ
KAYITSIZ_BAYT = 128
ARM_X = {'K': 'EdDSA', 'P': 'ML-DSA-65', 'C': 'ML-DSA-65-ES256'}
ARM_KOL = {'K': 'kontrol-EdDSA', 'P': 'tedavi-ML-DSA-65', 'C': 'tedavi-composite'}
ROLES = {'ES256': 'issuer/ES256', 'EdDSA': 'issuer/EdDSA', 'Ed25519': 'issuer/EdDSA', 'ML-DSA-65': 'issuer/ML-DSA-65',
         'ML-DSA-65-ES256': 'issuer/ML-DSA-65-ES256', ESKI_ROL: ESKI_ROL}
COSE_YUK = cbor.encode({'iss': A.ISS, 'vct': A.VCT, 'given_name': 'Erika'})
COSE_YUK_ESKI = cbor.encode({'iss': ESKI_ISS, 'vct': A.VCT, 'given_name': 'Erika'})
JWT_YUK_ESKI = json_bytes({'iss': ESKI_ISS, 'iat': A.T0, 'exp': A.T0 + 365 * 86400, 'vct': A.VCT, 'given_name': 'Erika'})
META_DOSYALAR = ('MANIFEST.json', 'MANIFEST.csv', 'SHA256SUMS')
D_SIGN, D_SIGN1, D_SIGSTR = 'RFC9052 §4.1', 'RFC9052 §4.2', 'RFC9052 §4.4'
ALG_DAYANAK = {'ES256': ['RFC9053 §2.1', 'RFC9864 §4.2.2', 'HAIP §7'], 'EdDSA': ['RFC9053 §2.2', 'RFC9864 §4.2.2'],
               'Ed25519': ['RFC9864 §2.2', 'RFC9864 §4.2.1'], 'ML-DSA-65': ['RFC9964 §5', 'RFC9964 §8.1.1'],
               'ML-DSA-65-ES256': ['JOSECOMP §5.2 (Tablo 6)', 'JOSECOMP §7.2.2', 'JOSECOMP §4.2']}


def _sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def flip(b, i, bit=0):
    x = bytearray(b)
    x[i] ^= (1 << bit)
    return bytes(x)


def _harita_algsiz(m):
    return {k: v for k, v in m.items() if k != cose.H_ALG}


def cose_es_denetimi(o1: bytes, o2: bytes):
    """Ed25519 counterpart: only the label EdDSA(-8) -> Ed25519(-19) and that signature may differ."""
    p1, p2 = cose.ayristir(o1), cose.ayristir(o2)
    if (p1['tur'], p1['payload'], p1['body_unprot']) != (p2['tur'], p2['payload'], p2['body_unprot']) or \
            len(p1['imzalar']) != len(p2['imzalar']):
        raise RuntimeError('COSE esi: yapi/yuk farkli')
    if p1['tur'] == 'COSE_Sign' and p1['body_prot'] != p2['body_prot']:
        raise RuntimeError('COSE esi: govde korumali baslik farkli')
    degisen = []
    for i, (a, b) in enumerate(zip(p1['imzalar'], p2['imzalar'])):
        if a['alg'] == cose.ALG['EdDSA']:
            if b['alg'] != cose.ALG['Ed25519'] or _harita_algsiz(a['sp_map']) != _harita_algsiz(b['sp_map']) or \
                    a['unprot'] != b['unprot']:
                raise RuntimeError('COSE esi: imzaci %d yalniz alg bakimindan farkli olmali' % i)
            degisen.append(i)
        elif (a['sp'], a['unprot'], a['imza']) != (b['sp'], b['unprot'], b['imza']):
            raise RuntimeError('COSE esi: EdDSA disi imzaci %d degismemeli' % i)
    if not degisen:
        raise RuntimeError('COSE esi: EdDSA etiketli imzaci yok')
    return degisen


def cose_mr4_denetimi(kaynak: bytes, perm: bytes, order):
    p1, p2 = cose.ayristir(kaynak), cose.ayristir(perm)
    if p1['tur'] != 'COSE_Sign' or p2['tur'] != 'COSE_Sign':
        raise RuntimeError('MR4 yalniz COSE_Sign')
    if (p1['body_prot'], p1['body_unprot'], p1['payload']) != (p2['body_prot'], p2['body_unprot'], p2['payload']):
        raise RuntimeError('MR4: govde/yuk degisti')
    for j, oi in enumerate(order):
        a, b = p1['imzalar'][oi], p2['imzalar'][j]
        if (a['sp'], a['unprot'], a['imza']) != (b['sp'], b['unprot'], b['imza']):
            raise RuntimeError('MR4: imzaci %d icerigi degisti' % oi)
    return True


class V13:
    def __init__(self, S: AnahtarSeti, eski, out):
        self.S = S
        self.eski = eski
        self.out = out
        self.yeni = []
        self.nesne = {}

    def key(self, rol):
        return self.eski if rol == ESKI_ROL else self.S[rol]

    def kidb(self, rol):
        return cose.kid_bytes(self.key(rol))

    # -------------------------------------------------------- writing
    def yaz(self, aile, vid, obj):
        if isinstance(obj, (bytes, bytearray)):
            ext, data = 'cbor', bytes(obj)
        elif isinstance(obj, str):
            ext, data = 'jws', obj.encode('utf-8')
        else:
            ext, data = 'json', (json.dumps(obj, indent=1, ensure_ascii=False) + '\n').encode('utf-8')
        rel = '%s/%s.%s' % (aile, vid, ext)
        p = os.path.join(self.out, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'wb') as f:
            f.write(data)
        return rel, data

    def ekle(self, vid, aile, obj, meta):
        rel, data = self.yaz(aile, vid, obj)
        g = {'id': vid, 'dosya': rel, 'sha256': hashlib.sha256(data).hexdigest(), 'bayt': len(data), 'aile': aile}
        g.update(meta)
        self.yeni.append(g)
        self.nesne[vid] = obj
        return g

    # -------------------------------------------------------- metadata helpers
    def kayit(self, sira, alg, rol, durum, **kw):
        k = self.key(rol) if rol else None
        d = {'sira': sira, 'alg': alg, 'cose_alg': cose.alg_deger(alg), 'alg_sinifi': alg_class(alg), 'anahtar_rolu': rol,
             'kid': k.kid if k else None, 'cose_kid_hex': cose.kid_bytes(k).hex() if k else None, 'insa': durum}
        if alg in cose.ALG:
            d['kimlik_kaynagi'] = cose.kaynak_etiketi('alg.' + alg)
        if alg in cose.KAYITLI_DEGIL:
            d['kayit_durumu'] = 'talep edilen, KAYITLI DEGIL (%s: "TBD (request assignment %d)")' % (
                cose.kaynak_etiketi('alg.' + alg), cose.ALG[alg])
        elif alg in ('ES256', 'EdDSA'):
            d['kayit_durumu'] = 'kayitli; RFC 9864 §4.2.2 "Deprecated" (polimorfik) (%s)' % cose.kaynak_etiketi(
                'alg.%s.deprecated' % alg)
            if alg == 'ES256':
                d['kayit_durumu'] += '; HAIP §7: "COSE algorithm identifier -7 or -9, as applicable" (%s)' % \
                    cose.kaynak_etiketi('alg.ES256.haip')
        d.update(kw)
        return d

    def girdi(self, roller, x5chain=False):
        g = {'cose_anahtarlar': 'anahtarlar/v1.3/cose-anahtarlar.json', 'jwks': 'anahtarlar/v1/acik-jwks.json',
             'kid': [self.key(r).kid for r in roller], 'cose_kid_hex': [self.kidb(r).hex() for r in roller],
             'cose_key_hex': {self.kidb(r).hex(): cbor.encode(cose.cose_key(self.key(r))).hex() for r in roller},
             'anahtar_yolu': "hedefin belgeli API'si (COSE_Key/JWK ya da dogrudan anahtar); ÖK §2D m.1",
             'simdi': SIMDI}
        if ESKI_ROL in roller:
            g['jwks'] = 'anahtarlar/v1.3/acik-jwks-l4c.json'
        if x5chain:
            g['guven_capalari'] = ['anahtarlar/v1/pki/root-ec.pem', 'anahtarlar/v1/pki/root-ml.pem']
        return g

    @staticmethod
    def meta(aciklama, serilestirme, basamak, plan=(), ek=(), dayanak=(), kol=None, senaryo=None, insa=None,
             girdiler=None, artefakt='cose'):
        return {'aciklama': aciklama, 'artefakt': artefakt, 'serilestirme': serilestirme, 'kol': kol,
                'senaryo': senaryo, 'sdjwtvc_surum': None,
                'sinanan': {'basamak': list(basamak), 'plan_bayraklari': list(plan), 'ek_etiketler': list(ek)},
                'dayanak': list(dayanak), 'insa': insa or {}, 'dogrulama_girdileri': girdiler or {},
                'b_pilot_esi': None, 'dcapi_protokol': None}

    # -------------------------------------------------------- COSE structures
    def imz(self, alg, rol=None, imza=None, prot_ek=None, unprot=None, imza_alg=None, yuk=COSE_YUK):
        rol = rol or ROLES[alg]
        return cose.imzaci(b'', yuk, self.key(rol) if imza is None else None, alg, prot_ek=prot_ek,
                           unprot={cose.H_KID: self.kidb(rol)} if unprot is None else unprot,
                           imza_alg=imza_alg, imza=imza)

    def sign(self, imzacilar):
        return cose.kodla(cose.sign_yapi(COSE_YUK, imzacilar), cose.TAG_SIGN)

    def sign1(self, alg, rol=None, prot_ek=None, unprot=None, imza_alg=None, yuk=COSE_YUK, bozma=None):
        rol = rol or ROLES[alg]
        y = cose.sign1_yapi(yuk, self.key(rol), alg, prot_ek=prot_ek,
                            unprot={cose.H_KID: self.kidb(rol)} if unprot is None else unprot, imza_alg=imza_alg)
        if bozma:
            y[3] = bozma(y[3])
        return cose.kodla(y, cose.TAG_SIGN1)

    def cose_bilgi(self, etiket, basliklar):
        return {'yapi': 'COSE_Sign' if etiket == cose.TAG_SIGN else 'COSE_Sign1', 'etiket': etiket,
                'etiket_kaynagi': cose.kaynak_etiketi('etiket.COSE_Sign' if etiket == cose.TAG_SIGN else 'etiket.COSE_Sign1'),
                'govde_korumali': "bos (h'')" if etiket == cose.TAG_SIGN else 'alg (+ varsa x5chain)',
                'yuk': 'belirlenimci CBOR harita {"iss","vct","given_name"}', 'external_aad': "bos (h'')",
                'kid': 'COSE kid (etiket 4) = base64url-cozulmus JWK kid (RFC 7638 parmak izi, 32 B); korumasiz baslikta',
                'basliklar': basliklar}

    # -------------------------------------------------------- A) COSE family
    def aile_cose(self):
        kayitlar = {}
        for a in 'KPC':
            x = ARM_X[a]
            dy = [D_SIGN, D_SIGSTR] + ALG_DAYANAK['ES256'] + ALG_DAYANAK[x]
            roller = ['issuer/ES256', ROLES[x]]
            G = self.girdi(roller)
            sen = 'd-COSE (COSE_Sign cok imzacili; RFC 9052 §4.1)'
            bas = {'imzaci_korumali': '{1: alg}', 'imzaci_korumasiz': '{4: kid}'}
            k1 = self.sign([self.imz('ES256'), self.imz(x)])
            r = [self.kayit(0, 'ES256', 'issuer/ES256', 'gecerli'), self.kayit(1, x, ROLES[x], 'gecerli')]
            kayitlar['K1' + a] = self.ekle('COSE-K1%s_iki_gecerli' % a, 'COSE', k1, self.meta(
                'COSE_Sign (etiket 98), iki imzaci: ES256 + %s, ikisi gecerli uretildi (ÖK §6.5 K1).' % x, 'COSE_Sign',
                ['L1', 'L2'], ek=['COSE', 'K1', 'coklu-imza'], dayanak=dy, kol=ARM_KOL[a], senaryo=sen, girdiler=G,
                insa={'imzalar': r, 'cose': self.cose_bilgi(98, bas)}))
            y2 = cbor.decode(k1).value
            y2[3][1][2] = flip(y2[3][1][2], 5, 0)
            k2 = cose.kodla(y2, cose.TAG_SIGN)
            kayitlar['K2' + a] = self.ekle('COSE-K2%s_X_bozuk' % a, 'COSE', k2, self.meta(
                'COSE-K1%s ile ayni; ikinci (%s) imzacinin imzasinin 5. baytinin 0. biti cevrildi (ÖK §6.5 K2).' % (a, x),
                'COSE_Sign', ['L4'], ek=['COSE', 'K2', 'bozuk-imza', 'coklu-imza-semantigi(any/all)'], dayanak=dy,
                kol=ARM_KOL[a], senaryo=sen, girdiler=G,
                insa={'kaynak_vektor': 'COSE-K1%s_iki_gecerli' % a,
                      'imzalar': [r[0], dict(r[1], insa='bozuk: bayt 5, bit 0 cevrildi')], 'cose': self.cose_bilgi(98, bas)}))
            if a == 'K':
                k3 = self.sign([self.imz('ES256')])
                kayitlar['K3'] = self.ekle('COSE-K3_X_soyuldu', 'COSE', k3, self.meta(
                    'COSE_Sign, yalniz ES256 imzacisi (X soyuldu; ÖK §6.5 K3). ES256 imzacisi uc kolda AYNI (ayni yuk, '
                    'anahtar, baslik; belirlenimci) -> tek dosya, tum kollar icin ortak.', 'COSE_Sign', ['L4'],
                    ek=['COSE', 'K3', 'soyma'], dayanak=[D_SIGN, D_SIGSTR] + ALG_DAYANAK['ES256'], kol='ortak',
                    senaryo=sen, girdiler=self.girdi(['issuer/ES256']),
                    insa={'kaynak_vektor': 'COSE-K1K/K1P/K1C', 'imzalar': [r[0]], 'soyulan': 'ikinci imzaci (X)',
                          'cose': self.cose_bilgi(98, bas)}))
            k4 = self.sign([self.imz(x)])
            kayitlar['K4' + a] = self.ekle('COSE-K4%s_yalniz_X' % a, 'COSE', k4, self.meta(
                'COSE_Sign, YALNIZ %s imzacisi (gecerli; ÖK §6.5 K4).' % x, 'COSE_Sign', ['L1', 'L2', 'L3'],
                ek=['COSE', 'K4', 'yalniz-tek-alg'], dayanak=[D_SIGN, D_SIGSTR] + ALG_DAYANAK[x], kol=ARM_KOL[a],
                senaryo=sen, girdiler=self.girdi([ROLES[x]]),
                insa={'imzalar': [dict(r[1], sira=0)], 'cose': self.cose_bilgi(98, bas)}))
            ucuncu = [cose.prot({cose.H_ALG: KAYITSIZ}), {},
                      derive_bytes('v1.3/COSE-K5%s/kayitsiz-imza' % a, KAYITSIZ_BAYT)]
            k5 = self.sign([self.imz('ES256'), self.imz(x), ucuncu])
            kayitlar['K5' + a] = self.ekle('COSE-K5%s_arti_kayitsiz' % a, 'COSE', k5, self.meta(
                'COSE_Sign: COSE-K1%s ile ayni iki gecerli imzaci + KAYITSIZ tstr alg ("%s") etiketli ucuncu imzaci; imza '
                'baytlari rastgele ve belirlenimci (HKDF "v1.3/COSE-K5%s/kayitsiz-imza", %d B), korumasiz baslik bos '
                '(kid yok). ÖK §6.5 K5.' % (a, KAYITSIZ, a, KAYITSIZ_BAYT), 'COSE_Sign', ['L1', 'L4'],
                plan=['bilinmeyen-composite-alg'], ek=['COSE', 'K5', 'kayitsiz-alg', 'ek-imza'],
                dayanak=dy + ['RFC9052 §3.1'], kol=ARM_KOL[a], senaryo=sen, girdiler=G,
                insa={'kaynak_vektor': 'COSE-K1%s_iki_gecerli' % a,
                      'imzalar': r + [{'sira': 2, 'alg': KAYITSIZ, 'cose_alg': KAYITSIZ, 'alg_sinifi': alg_class(KAYITSIZ),
                                       'anahtar_rolu': None, 'kid': None, 'cose_kid_hex': None,
                                       'insa': 'rastgele belirlenimci %d B (HKDF); kriptografik anlami yok' % KAYITSIZ_BAYT}],
                      'cose': self.cose_bilgi(98, bas)}))
        return kayitlar

    def aile_cose_tek(self):
        """K10, V+/V-, K6, K7, K8, K9 (COSE_Sign1)."""
        bas1 = {'korumali': '{1: alg}', 'korumasiz': '{4: kid}'}
        out = {}
        cases = [('K', 'EdDSA', 'issuer/ES256', 'ES256'), ('K', 'ES256', 'issuer/EdDSA', 'EdDSA'),
                 ('P', 'ML-DSA-65', 'issuer/ES256', 'ES256'), ('P', 'ES256', 'issuer/ML-DSA-65', 'ML-DSA-65'),
                 ('C', 'ML-DSA-65-ES256', 'issuer/ML-DSA-65', 'ML-DSA-65'),
                 ('C', 'ML-DSA-65', 'issuer/ML-DSA-65-ES256', 'ML-DSA-65-ES256')]
        tur = {'issuer/ES256': 'ES256', 'issuer/EdDSA': 'Ed25519', 'issuer/ML-DSA-65': 'ML-DSA-65',
               'issuer/ML-DSA-65-ES256': 'ML-DSA-65-ES256'}
        for a, halg, rol, galg in cases:
            key = self.key(rol)
            if algs.key_supports(key, halg):
                raise RuntimeError('K10 insasi hatali')
            o = self.sign1(halg, rol=rol, imza_alg=galg)
            vid = 'COSE-K10%s_alg-%s_anahtar-%s' % (a, halg, tur[rol])
            dy = [D_SIGN1, D_SIGSTR, 'RFC9052 §3.1', 'RFC9052 §7.1', 'JWTBCP §3.1'] + ALG_DAYANAK.get(halg, []) + \
                ALG_DAYANAK.get(galg, [])
            out[vid] = self.ekle(vid, 'COSE', o, self.meta(
                'COSE_Sign1 (ÖK §6.5 K10, alg-anahtar uyusmazligi): korumali baslikta alg=%s (%r), dogrulama anahtari %s '
                '(%s; COSE_Key ve JWK olarak verilir). Imza, baslik alg\'iyla DEGIL gercek anahtarin kendi algoritmasiyla '
                '(%s) bu Sig_structure uzerinde uretilmis GECERLI imzadir.' % (halg, cose.alg_deger(halg), rol, tur[rol], galg),
                'COSE_Sign1', ['L2', 'L3'], ek=['COSE', 'K10', 'alg-anahtar-uyusmazligi'], dayanak=list(dict.fromkeys(dy)),
                kol=ARM_KOL[a], girdiler=self.girdi([rol]),
                insa={'imzalar': [self.kayit(0, halg, rol, 'gercek anahtarin algoritmasiyla (%s) gecerli imza; baslik alg '
                                                          'anahtarla uyusmuyor' % galg)],
                      'k10': {'baslik_alg': halg, 'baslik_cose_alg': cose.alg_deger(halg), 'anahtar_rolu': rol,
                              'anahtar_turu': tur[rol], 'imza_uretim_alg': galg},
                      'cose': self.cose_bilgi(18, bas1)}))
        for alg in ('ES256', 'EdDSA', 'ML-DSA-65'):
            rol = ROLES[alg]
            kol = 'ortak' if alg == 'ES256' else ARM_KOL['K' if alg == 'EdDSA' else 'P']
            for isaret, bozuk in (('PLUS', False), ('MINUS', True)):
                o = self.sign1(alg, bozma=(lambda s: flip(s, len(s) // 2)) if bozuk else None)
                vid = 'COSE-V%s_%s' % (isaret, alg)
                slen = {'ES256': 64, 'EdDSA': 64, 'ML-DSA-65': 3309}[alg]
                out[vid] = self.ekle(vid, 'COSE', o, self.meta(
                    'V%s adaptor gecerlilik kontrolu (ÖK §6.5 V+/V-, §4.15): tek imzali COSE_Sign1, %s (%r), kid ile; %s.'
                    % ('+' if not bozuk else '-', alg, cose.alg_deger(alg),
                       'imzanin orta baytinda bit cevrildi' if bozuk else 'imza gecerli'),
                    'COSE_Sign1', [], ek=['COSE', 'V+' if not bozuk else 'V-', 'adaptor-gecerlilik-kontrolu'],
                    dayanak=[D_SIGN1, D_SIGSTR] + ALG_DAYANAK[alg], kol=kol, girdiler=self.girdi([rol]),
                    insa={'imzalar': [self.kayit(0, alg, rol, ('bozuk: bayt %d, bit 0 cevrildi' % (slen // 2)) if bozuk
                                                 else 'gecerli')], 'cose': self.cose_bilgi(18, bas1)}))
        c = 'ML-DSA-65-ES256'
        rc = ROLES[c]
        dyc = [D_SIGN1, D_SIGSTR] + ALG_DAYANAK[c] + ['JOSECOMP §4.3']
        out['K6'] = self.ekle('COSE-K6_composite_gecerli', 'COSE', self.sign1(c), self.meta(
            'COSE_Sign1, composite ML-DSA-65-ES256 (%d; talep edilen, kayitli degil), gecerli (ÖK §6.5 K6).' % cose.ALG[c],
            'COSE_Sign1', ['L1'], ek=['COSE', 'K6', 'composite-bilesen-dogrulugu'], dayanak=dyc, kol='tedavi-composite',
            senaryo='a', girdiler=self.girdi([rc]),
            insa={'imzalar': [self.kayit(0, c, rc, 'gecerli')], 'cose': self.cose_bilgi(18, bas1)}))
        sig = cbor.decode(self.nesne['COSE-K6_composite_gecerli']).value[3]
        n = 3309                      # ML-DSA-65 signature length (FIPS 204); composite = mldsaSig || DER(Ecdsa-Sig-Value)
        der = sig[n:]
        if der[0] != 0x30 or der[2] != 0x02:
            raise RuntimeError('K7: beklenmeyen DER yapisi')
        lr = der[3]
        for vid, idx, acik, dur in (
                ('COSE-K7_ml_bileseni_bozuk', n // 2, 'ML-DSA bileseninin orta baytinda bit cevrildi; ECDSA bileseni gecerli',
                 'ML-DSA bileseni bozuk (bayt %d, bit 0); ECDSA bileseni gecerli' % (n // 2)),
                ('COSE-K7_ecdsa_bileseni_bozuk', n + 4 + lr - 1,
                 'ECDSA bileseninde r degerinin son baytinda bit cevrildi (DER yapisi gecerli); ML-DSA bileseni gecerli',
                 'ECDSA bileseni bozuk (r son bayt); ML-DSA gecerli')):
            y2 = cbor.decode(self.nesne['COSE-K6_composite_gecerli']).value
            y2[3] = flip(y2[3], idx)
            out[vid] = self.ekle(vid, 'COSE', cose.kodla(y2, cose.TAG_SIGN1), self.meta(
                'COSE_Sign1 composite (ÖK §6.5 K7): %s.' % acik, 'COSE_Sign1', ['L4'],
                ek=['COSE', 'K7', 'composite-bilesen-dogrulugu', 'bilesen-bozulmasi'], dayanak=dyc, kol='tedavi-composite',
                senaryo='a', girdiler=self.girdi([rc]),
                insa={'kaynak_vektor': 'COSE-K6_composite_gecerli', 'imzalar': [self.kayit(0, c, rc, dur)],
                      'cose': self.cose_bilgi(18, bas1)}))
        S = self.S
        leaf = S.certs['issuer-ml@int-ec']
        zincir = [leaf.der, leaf.issuer.der]
        out['K8'] = self.ekle('COSE-K8_x5chain_karisik', 'COSE', self.sign1(
            'ML-DSA-65', prot_ek={cose.H_X5CHAIN: zincir}, unprot={}), self.meta(
            'COSE_Sign1, ML-DSA-65; KORUMALI x5chain (etiket 33) = [issuer-ml@int-ec, int-ec]: ML-DSA-65 yaprak + klasik '
            'ara CA (karisik zincir). ÖK §6.5 K8, §2F m.4 uyarlamasi (composite yaprak kapsam disi; D-S1). Guven capasi '
            'x5chain disinda. HAIP §6.1.1 JOSE x5c kurali ([yaprak, ara CA], kok haric) COSE icin benzetimle uygulandi; '
            'HAIP COSE x5chain icin ayrica kural koymaz.', 'COSE_Sign1', ['L3'], plan=['karisik-x5c'], ek=['COSE', 'K8', 'x5chain'],
            dayanak=[D_SIGN1, D_SIGSTR, 'RFC9360 §2'] + ALG_DAYANAK['ML-DSA-65'], kol='tedavi-ML-DSA-65',
            girdiler=self.girdi(['issuer/ML-DSA-65'], x5chain=True),
            insa={'imzalar': [self.kayit(0, 'ML-DSA-65', 'issuer/ML-DSA-65', 'gecerli')],
                  'x5chain': {'zincir': ['issuer-ml@int-ec', 'int-ec', 'root-ec (guven capasi; x5chain disinda)'],
                              'sinif': 'karisik', 'korumali': True, 'kaynak': cose.kaynak_etiketi('hdr.x5chain')},
                  'cose': self.cose_bilgi(18, {'korumali': '{1: alg, 33: [yaprak, ara CA]}', 'korumasiz': '{}'})}))
        leaf2 = S.certs['issuer-ml@int-ml']
        out['K9'] = self.ekle('COSE-K9_x5chain_korumasiz', 'COSE', self.sign1(
            'ML-DSA-65', unprot={cose.H_X5CHAIN: [leaf2.der, leaf2.issuer.der]}), self.meta(
            'COSE_Sign1, ML-DSA-65; x5chain (etiket 33) KORUMASIZ baslikta = [issuer-ml@int-ml, int-ml] (tam-PQ zincir); '
            'korumali baslik yalniz {1: alg} (ÖK §6.5 K9).', 'COSE_Sign1', ['L3'], plan=['korumasiz-x5c'],
            ek=['COSE', 'K9', 'x5chain'], dayanak=[D_SIGN1, D_SIGSTR, 'RFC9360 §2'] + ALG_DAYANAK['ML-DSA-65'],
            kol='tedavi-ML-DSA-65', girdiler=self.girdi(['issuer/ML-DSA-65'], x5chain=True),
            insa={'imzalar': [self.kayit(0, 'ML-DSA-65', 'issuer/ML-DSA-65', 'gecerli')],
                  'x5chain': {'zincir': ['issuer-ml@int-ml', 'int-ml'], 'sinif': 'tam-pq', 'korumali': False,
                              'kaynak': cose.kaynak_etiketi('hdr.x5chain')},
                  'cose': self.cose_bilgi(18, {'korumali': '{1: alg}', 'korumasiz': '{33: [yaprak, ara CA]}'})}))
        return out

    # -------------------------------------------------------- MR4 and Ed25519 counterparts
    def mr4(self, kaynak_g):
        vid = kaynak_g['id'] + '-SIRA-ters'
        o = cbor.decode(self.nesne[kaynak_g['id']]).value
        o[3] = list(reversed(o[3]))
        perm = cose.kodla(o, cose.TAG_SIGN)
        order = list(reversed(range(len(cbor.decode(self.nesne[kaynak_g['id']]).value[3]))))
        cose_mr4_denetimi(self.nesne[kaynak_g['id']], perm, order)
        e = copy.deepcopy(kaynak_g)
        for k in ('id', 'dosya', 'sha256', 'bayt'):
            e.pop(k)
        imz = kaynak_g['insa']['imzalar']
        e['insa']['imzalar'] = [dict(imz[oi], sira=j, ozgun_sira=oi) for j, oi in enumerate(order)]
        e['insa']['mr4'] = {'kaynak_vektor': kaynak_g['id'], 'yeni_siradaki_ozgun_indeksler': order, 'permutasyon': 'ters'}
        e['aciklama'] = ('MR4 esi (ÖK §2B m.8, §2C m.4): %s COSE_Sign imzaci sirasi ters (yeni sira = ozgun %s). Her '
                         'COSE_Signature [korumali, korumasiz, imza] ve govde/yuk bayt-ayni; imzaci Sig_structure\'i sira '
                         'bagimsizdir. Ozgun aciklama: %s' % (kaynak_g['id'], order, kaynak_g['aciklama']))
        e['sinanan']['ek_etiketler'] = e['sinanan']['ek_etiketler'] + ['MR4(imza-sirasi-permutasyonu)']
        return self.ekle(vid, 'COSE', perm, e), order

    def ed_esi(self, g, es_obj):
        degisen = cose_es_denetimi(self.nesne[g['id']], es_obj)
        e = copy.deepcopy(g)
        for k in ('id', 'dosya', 'sha256', 'bayt'):
            e.pop(k)
        e['kol'] = 'kontrol-Ed25519'
        e['aciklama'] = ('%s vektorunun Ed25519 etiketli esi (A9 yedek kurali; ÖK §2D m.2): EdDSA (-8) yerine RFC 9864 tam '
                         'belirtilmis Ed25519 (-19; %s); ayni anahtar, ayni yuk, ayni yapi; yalniz bu baslik ve ona bagli imza '
                         'farkli. Ozgun aciklama: %s' % (g['id'], cose.kaynak_etiketi('alg.Ed25519'), g['aciklama']))
        e['dayanak'] = [d for d in g['dayanak'] if d not in ('RFC9053 §2.2',)] + ['RFC9864 §2.2', 'RFC9864 §4.2.1']
        e['dayanak'] = list(dict.fromkeys(e['dayanak']))
        for s in e['insa'].get('imzalar', []):
            if s.get('alg') == 'EdDSA':
                s.update(alg='Ed25519', cose_alg=cose.ALG['Ed25519'], kimlik_kaynagi=cose.kaynak_etiketi('alg.Ed25519'))
                s.pop('kayit_durumu', None)
        e['insa']['etiket_esi'] = g['id']
        e['insa']['etiket_degisikligi'] = {'eski': 'EdDSA (-8)', 'yeni': 'Ed25519 (-19)', 'yeniden_hesaplanan_imza_sirasi': degisen}
        if 'k10' in e['insa'] and e['insa']['k10']['baslik_alg'] == 'EdDSA':
            e['insa']['k10'].update(baslik_alg='Ed25519', baslik_cose_alg=cose.ALG['Ed25519'])
        if 'mr4' in e['insa']:
            e['insa']['mr4']['kaynak_vektor'] += '-ED25519'
        e['sinanan']['ek_etiketler'] = e['sinanan']['ek_etiketler'] + ['ed25519-etiketi(RFC 9864; A9 yedek kurali)']
        return self.ekle(g['id'] + '-ED25519', g['aile'], es_obj, e)

    # -------------------------------------------------------- B) L4c old issuer
    def aile_l4c(self):
        from pqjose import jws
        e = self.eski
        h = {'kid': e.kid, 'typ': 'JWT'}
        jose_o = jws.sign(JWT_YUK_ESKI, jws.Signer(e, h, alg='ES256'), 'compact', True)
        ihr = {'kimlik': 'eski-ihracci (goc etmemis)', 'iss': ESKI_ISS, 'anahtar_rolu': ESKI_ROL, 'kid': e.kid,
               'cose_kid_hex': cose.kid_bytes(e).hex(), 'turetme_etiketi': ESKI_ETIKET}
        dy = ['JWTBCP §3.1', 'RFC7519 §4.1.1', 'RFC7515 §4.1.4', 'RFC7518 §3.4']
        self.ekle('L4C-JOSE_eski_ES256', 'L4C', jose_o, self.meta(
            'L4c (ÖK §2B m.6): AYRI kimlikli "eski ihracci"nin compact JWS\'i (iss %s, ayri anahtar ve kid; yalniz ES256). '
            'Baslik {"alg","kid","typ":"JWT"}, yuk VPLUS_ES256 ile ayni yapida (yalniz iss farkli). Goc etmis ihraccinin '
            'karsiliklari mevcut vektorlerdir (VPLUS_ES256, VPLUS_ML-DSA-65, CMP00; BATARYA-ESLEME.md).' % ESKI_ISS,
            'compact', ['L4'], ek=['L4c', 'eski-ihracci'], dayanak=dy, kol='ortak (L4c; iki tedavi kolu)',
            girdiler={'jwks': 'anahtarlar/v1.3/acik-jwks-l4c.json', 'kid': [e.kid], 'jwk': e.public_jwk(),
                      'anahtar_yolu': "hedefin belgeli API'si (JWK/JWKS ya da dogrudan anahtar); ÖK §2D m.1",
                      'simdi': SIMDI}, artefakt='jws-cekirdek',
            insa={'imzalar': [{'sira': 0, 'alg': 'ES256', 'alg_sinifi': 'klasik', 'anahtar_rolu': ESKI_ROL, 'kid': e.kid,
                               'insa': 'gecerli'}], 'ihracci': ihr}))
        cose_o = self.sign1('ES256', rol=ESKI_ROL, yuk=COSE_YUK_ESKI)
        self.ekle('L4C-COSE_eski_ES256', 'L4C', cose_o, self.meta(
            'L4c (ÖK §2B m.6): AYRI kimlikli "eski ihracci"nin COSE_Sign1\'i (yukte iss %s; korumasiz kid; yalniz ES256 (-7)). '
            'Goc etmis ihraccinin karsiliklari mevcut vektorlerdir (COSE-VPLUS_ES256, COSE-VPLUS_ML-DSA-65, COSE-K6).' % ESKI_ISS,
            'COSE_Sign1', ['L4'], ek=['L4c', 'eski-ihracci', 'COSE'], dayanak=[D_SIGN1, D_SIGSTR, 'RFC9052 §3.1'] +
            ALG_DAYANAK['ES256'] + ['JWTBCP §3.1'], kol='ortak (L4c; iki tedavi kolu)', girdiler=self.girdi([ESKI_ROL]),
            insa={'imzalar': [self.kayit(0, 'ES256', ESKI_ROL, 'gecerli')], 'ihracci': ihr,
                  'cose': self.cose_bilgi(18, {'korumali': '{1: alg}', 'korumasiz': '{4: kid}'})}))

    def uret(self):
        k = self.aile_cose()
        t = self.aile_cose_tek()
        mr4 = {}
        for a in 'KPC':
            mr4['K1' + a] = self.mr4(k['K1' + a])
            mr4['K2' + a] = self.mr4(k['K2' + a])
        # Ed25519 counterparts (control arm, those that carry the EdDSA label)
        E = self.imz
        k1e = self.sign([E('ES256'), E('Ed25519')])
        self.ed_esi(k['K1K'], k1e)
        y = cbor.decode(k1e).value
        y[3][1][2] = flip(y[3][1][2], 5, 0)
        k2e = cose.kodla(y, cose.TAG_SIGN)
        self.ed_esi(k['K2K'], k2e)
        self.ed_esi(k['K4K'], self.sign([E('Ed25519')]))
        ucuncu = [cose.prot({cose.H_ALG: KAYITSIZ}), {}, derive_bytes('v1.3/COSE-K5K/kayitsiz-imza', KAYITSIZ_BAYT)]
        self.ed_esi(k['K5K'], self.sign([E('ES256'), E('Ed25519'), ucuncu]))
        self.ed_esi(t['COSE-K10K_alg-EdDSA_anahtar-ES256'], self.sign1('Ed25519', rol='issuer/ES256', imza_alg='ES256'))
        self.ed_esi(t['COSE-VPLUS_EdDSA'], self.sign1('Ed25519'))
        self.ed_esi(t['COSE-VMINUS_EdDSA'], self.sign1('Ed25519', bozma=lambda s: flip(s, len(s) // 2)))
        for kk, src_es in (('K1K', k1e), ('K2K', k2e)):
            g, order = mr4[kk]
            o = cbor.decode(src_es).value
            o[3] = [o[3][i] for i in order]
            self.ed_esi(g, cose.kodla(o, cose.TAG_SIGN))
        self.aile_l4c()
        return self.yeni


def yaz_anahtarlar_v13(kok, S, eski):
    d = os.path.join(kok, 'keys', SURUM)
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(os.path.join(d, 'ozel'))
    with open(os.path.join(d, 'ozel', 'issuer-eski__ES256.json'), 'w', encoding='utf-8') as f:
        json.dump(eski.private_jwk(), f, indent=1)
        f.write('\n')
    with open(os.path.join(d, 'acik-jwks.json'), 'w', encoding='utf-8') as f:
        json.dump({'keys': [eski.public_jwk()]}, f, indent=1)
        f.write('\n')
    goc = ['issuer/ES256', 'issuer/ML-DSA-65', 'issuer/ML-DSA-65-ES256']
    with open(os.path.join(d, 'acik-jwks-l4c.json'), 'w', encoding='utf-8') as f:
        json.dump({'not': 'L4c: goc etmis ihracci (iss %s) anahtarlari + eski ihracci (iss %s) anahtari' % (A.ISS, ESKI_ISS),
                   'ihraccilar': {A.ISS: [S[r].kid for r in goc], ESKI_ISS: [eski.kid]},
                   'keys': [S[r].public_jwk() for r in goc] + [eski.public_jwk()]}, f, indent=1)
        f.write('\n')
    roller = ['issuer/ES256', 'issuer/EdDSA', 'issuer/ML-DSA-65', 'issuer/ML-DSA-65-ES256']
    ck = []
    for r in roller + [ESKI_ROL]:
        k = eski if r == ESKI_ROL else S[r]
        ck.append({'rol': r, 'kid': k.kid, 'cose_kid_hex': cose.kid_bytes(k).hex(),
                   'cose_key_hex': cbor.encode(cose.cose_key(k)).hex(), 'jwk': k.public_jwk()})
    with open(os.path.join(d, 'cose-anahtarlar.json'), 'w', encoding='utf-8') as f:
        json.dump({'not': 'Acik COSE_Key (belirlenimci CBOR). EC2: {1:2, 2:kid, -1:1, -2:x, -3:y}; OKP: {1:1, 2:kid, -1:6, -2:x}; '
                          'AKP: {1:7, 2:kid, 3:alg, -1:pub}. kid = base64url-cozulmus JWK kid (RFC 7638, 32 B). '
                          'Kaynaklar: RFC 9052 §7.1, RFC 9053 §7.1-7.2, RFC 9964 §8.1.2-8.1.3 (satirlar uretec/cose.py KAYNAK).',
                   'anahtarlar': ck}, f, indent=1)
        f.write('\n')
    with open(os.path.join(d, 'roller.json'), 'w', encoding='utf-8') as f:
        json.dump({'turetme': 'pqjose.keys.derive_key(tur, etiket): HKDF-SHA256 (anahtarlar/v1/roller.json ile ayni IKM/salt)',
                   'roller': {ESKI_ROL: {'tur': 'ES256', 'kid': eski.kid, 'turetme_etiketi': ESKI_ETIKET,
                                         'ozel_jwk': 'ozel/issuer-eski__ES256.json', 'iss': ESKI_ISS}},
                   'v1_anahtarlari': 'anahtarlar/v1 (degismedi)'}, f, indent=1, ensure_ascii=False)
        f.write('\n')
    Uretici._sha256sums(d)


def uret_v13(cikti_kok, donmus_kok, surumler):
    out = os.path.join(cikti_kok, 'vectors', SURUM)
    with tempfile.TemporaryDirectory(prefix='pq-v13-') as td:
        v12.uret_v12(td, donmus_kok, surumler)
        for fn in ('SHA256SUMS', 'MANIFEST.json'):
            a = open(os.path.join(donmus_kok, 'vectors', 'v1.2', fn), 'rb').read()
            b = open(os.path.join(td, 'vectors', 'v1.2', fn), 'rb').read()
            if a != b:
                raise RuntimeError('v1.2 yeniden uretimi donmus v1.2 ile ayni degil (%s) — v1.3 uretilmedi' % fn)
        v12_man = json.load(open(os.path.join(td, 'vectors', 'v1.2', 'MANIFEST.json'), encoding='utf-8'))
        S = AnahtarSeti()
        eski = derive_key('ES256', ESKI_ETIKET)
        eski.kid = eski.thumbprint()
        if os.path.isdir(out):
            shutil.rmtree(out)
        src = os.path.join(td, 'vectors', 'v1.2')
        shutil.copytree(src, out, ignore=lambda d, names: [n for n in names if d == src and n in META_DOSYALAR])
        g = V13(S, eski, out)
        yeni = g.uret()
        yaz_anahtarlar_v13(cikti_kok, S, eski)
        ids = [i['id'] for i in v12_man['vektorler']] + [i['id'] for i in yeni]
        if len(ids) != len(set(ids)):
            raise RuntimeError('yinelenen vektor kimligi')
        items = copy.deepcopy(v12_man['vektorler']) + yeni
        sayim = {}
        for i in yeni:
            k = i['aile'] + ('-MR4' if 'mr4' in i['insa'] else '') + ('+ED25519' if i['id'].endswith('-ED25519') else '')
            sayim[k] = sayim.get(k, 0) + 1
        a13 = os.path.join(cikti_kok, 'keys', SURUM, 'SHA256SUMS')
        m = {'surum': SURUM, 'temel_surum': 'v1.2', 'vektor_sayisi': len(items),
             'v1_2_vektor_sayisi': len(v12_man['vektorler']), 'yeni_vektor_sayisi': len(yeni), 'yeni_dagilim': sayim,
             'simdi': SIMDI, 'T0': v12_man['T0'],
             'uyari': 'Bu manifest vektorlerin NE OLDUGUNU tanimlar; beklenen karar (oracle) ICERMEZ. '
                      "'insa' alanlari uretim gercekleridir, kabul/red hukmu degildir. ÖK kararlarinin alintisi "
                      'yalniz BATARYA-ESLEME.md\'dedir.',
             'yedek_kural': v12.v11.YEDEK_KURAL, 'kayitsiz_alg': KAYITSIZ,
             'cose_kimlik_kaynaklari': {k: '%s:%d %s' % v for k, v in cose.KAYNAK.items()},
             'eski_ihracci': {'iss': ESKI_ISS, 'anahtar_rolu': ESKI_ROL, 'kid': eski.kid, 'turetme_etiketi': ESKI_ETIKET},
             'anahtar_dizinleri': ['anahtarlar/v1', 'anahtarlar/v1.3'],
             'anahtar_sha256sums': {'anahtarlar/v1/SHA256SUMS': _sha(os.path.join(donmus_kok, 'keys', 'v1', 'SHA256SUMS')),
                                    'anahtarlar/v1.3/SHA256SUMS': _sha(a13)},
             'v1_2_capalari': {'vektorler/v1.2/MANIFEST.json': _sha(os.path.join(donmus_kok, 'vectors', 'v1.2', 'MANIFEST.json')),
                               'vektorler/v1.2/SHA256SUMS': _sha(os.path.join(donmus_kok, 'vectors', 'v1.2', 'SHA256SUMS'))},
             'v1_1_capalari': v12_man['v1_1_capalari'], 'v1_capalari': v12_man['v1_capalari'],
             'uretim_ortami': surumler, 'aileler': sorted({i['aile'] for i in items}), 'vektorler': items}
        with open(os.path.join(out, 'MANIFEST.json'), 'w', encoding='utf-8') as f:
            json.dump(m, f, indent=1, ensure_ascii=False)
            f.write('\n')
        cols = ['id', 'aile', 'dosya', 'sha256', 'bayt', 'artefakt', 'serilestirme', 'kol', 'senaryo', 'sdjwtvc_surum',
                'basamak', 'plan_bayraklari', 'ek_etiketler', 'dayanak', 'b_pilot_esi', 'dcapi_protokol', 'algler', 'aciklama']
        with open(os.path.join(out, 'MANIFEST.csv'), 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(cols)
            for i in items:
                sigs = i['insa'].get('imzalar') or i['insa'].get('kimlik_bilgileri') or []
                w.writerow([i['id'], i['aile'], i['dosya'], i['sha256'], i['bayt'], i['artefakt'], i['serilestirme'],
                            i['kol'] or '', i['senaryo'] or '', ';'.join(i['sdjwtvc_surum'] or []),
                            ';'.join(i['sinanan']['basamak']), ';'.join(i['sinanan']['plan_bayraklari']),
                            ';'.join(i['sinanan']['ek_etiketler']), ';'.join(i['dayanak']), i['b_pilot_esi'] or '',
                            i['dcapi_protokol'] or '', ';'.join(str(s.get('alg', '')) for s in sigs), i['aciklama']])
        Uretici._sha256sums(out)
    return items, yeni


def main(kok, donmus_kok=None):
    surumler = pqjose.versions()
    surumler['uretec'] = __version__
    items, yeni = uret_v13(kok, donmus_kok or kok, surumler)
    os.makedirs(os.path.join(kok, 'results'), exist_ok=True)
    with open(os.path.join(kok, 'results', 'v1.3_sizes.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['id', 'aile', 'artefakt', 'serilestirme', 'kol', 'algler', 'bayt'])
        for i in items:
            sigs = i['insa'].get('imzalar') or i['insa'].get('kimlik_bilgileri') or []
            w.writerow([i['id'], i['aile'], i['artefakt'], i['serilestirme'], i['kol'] or '',
                        ';'.join(str(s.get('alg', '')) for s in sigs), i['bayt']])
    print(json.dumps({'surum': SURUM, 'vektor': len(items), 'yeni': len(yeni)}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else '.', sys.argv[2] if len(sys.argv) > 2 else None))
