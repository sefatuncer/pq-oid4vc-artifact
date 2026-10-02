"""Test vector set v1 (Step 9b) — fully deterministic (keys with fixed seeds, deterministic signatures).

IMPORTANT: this module defines WHAT the vector is (construction facts, tested L level/flag,
specification basis). The expected decision (accept/reject) is NOT written — the oracle is produced separately as an N-version oracle.

Families:
  T    T1-T6 of the P3 pilot of B, with REAL PQ/composite signatures (control/treatment arms)
  UNK  unknown / unregistered alg labels
  CMP  composite -04 component corruptions, imitations of implementer errors, separability
  X5C  classical / PQ / mixed chains, unprotected x5c, trust anchor inside x5c
  REQ  OID4VP request objects (compact, multi-signed A.3.2.2, unsigning M-b0, alg=none)
  VC   SD-JWT VC issuance (-13/-19 modes; General JSON; double issuance; typ; alg=none)
  VP   SD-JWT+KB presentations (KB-JWT algorithms; General JSON sd_hash ambiguity)
  TSL  Token Status List tokens
  DPOP DPoP proofs (size thresholds, jwk with a private key)
  CRIT cases of the crit header
"""
import copy
import csv
import hashlib
import json
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

from pqjose import algs, composite, jws, mldsa, pki
from pqjose.der import ecdsa_der_to_raw, ecdsa_raw_to_der
from pqjose.keys import MLDSAKey
from pqjose.params import COMPOSITE, PREFIX, alg_class
from pqjose.util import b64u_decode, b64u_encode, json_bytes

from . import artefakt as A
from . import sdjwt
from .anahtar import ROLLER, AnahtarSeti

SURUM = 'v1'
SIMDI = A.T0 + 3700   # verification instant for all vectors (UNIX)

# ------------------------------------------------------------------ bases (MANIFEST id + section)
R = dict(
    alg='RFC7515 §4.1.1', x5c='RFC7515 §4.1.6', crit='RFC7515 §4.1.11', dogr='RFC7515 §5.2',
    json='RFC7515 §7.2', gen='RFC7515 §7.2.1', flat='RFC7515 §7.2.2', algkoruma='RFC7515 §10.7',
    es256='RFC7518 §3.4', eddsa='RFC9864 §2.2', mldsa='RFC9964 §5', akp='RFC9964 §3',
    c_sign='JOSECOMP §4.2', c_verify='JOSECOMP §4.3', c_enc='JOSECOMP §4.4', c_der='JOSECOMP §4.5.1',
    c_alg='JOSECOMP §5.1 (Tablo 5)', c_label='JOSECOMP §5.3 (Tablo 7)', c_iana='JOSECOMP §7.1',
    c_reuse='JOSECOMP §6.2', c_sep='JOSECOMP §6.3',
    bcp='JWTBCP §3.1', typ='JWTBCP §3.11',
    sd_fmt='RFC9901 §4', sd_iss='RFC9901 §4.1', sd_disc='RFC9901 §4.2', sd_kb='RFC9901 §4.3',
    sd_kbbind='RFC9901 §4.3.1', sd_ver='RFC9901 §7.3', sd_json='RFC9901 §8.1', sd_flat='RFC9901 §8.2',
    sd_gen='RFC9901 §8.3', sd_sign='RFC9901 §9.1',
    vc19_fmt='SDJWTVC §2.2', vc19_hdr='SDJWTVC §2.2.1', vc19_cl='SDJWTVC §2.2.2.3', vc19_key='SDJWTVC §2.5',
    vc13_fmt='SDJWTVC13 §3.2', vc13_hdr='SDJWTVC13 §3.2.1', vc13_key='SDJWTVC13 §3.5', vc13_pres='SDJWTVC13 §4.1',
    tsl_bits='TSL §4.1', tsl_json='TSL §4.2', tsl_jwt='TSL §5.1', tsl_ref='TSL §6.2',
    haip_dpop='HAIP §4', haip_vp='HAIP §5', haip_dc='HAIP §5.2', haip_status='HAIP §6.1',
    haip_x5c='HAIP §6.1.1', haip_kb='HAIP §6.1.1.1', haip_sig='HAIP §7', haip_pre='HAIP §9.4',
    vp_req='OID4VP §5', vp_cid='OID4VP §5.9.3', vp_dcreq='OID4VP A.2', vp_uns='OID4VP A.3.1',
    vp_sig='OID4VP A.3.2.1', vp_multi='OID4VP A.3.2.2', vp_aud='OID4VP A.4',
    jar='RFC9101 §4', jar_val='RFC9101 §6.2', dpop='RFC9449 §4.2', dpop_chk='RFC9449 §4.3',
    eccg='ACM2 (ECCG ACM v2, hibrit AND)',
)

B_PAYLOAD = json_bytes({'iss': 'https://issuer.example', 'vct': 'urn:eudi:pid:1', 'given_name': 'Erika'})
JWT_PAYLOAD = json_bytes({'iss': A.ISS, 'iat': A.T0, 'exp': A.T0 + 365 * 86400, 'vct': A.VCT, 'given_name': 'Erika'})
ARM = {'EdDSA': 'kontrol-EdDSA', 'ML-DSA-65': 'tedavi-ML-DSA-65', 'ML-DSA-65-ES256': 'tedavi-composite'}


def kol_of(alg):
    return {'ES256': 'klasik-taban', 'EdDSA': 'kontrol-EdDSA', 'ML-DSA-65': 'tedavi-ML-DSA-65',
            'ML-DSA-65-ES256': 'tedavi-composite'}.get(alg, 'kapsam-' + alg_class(alg))


def flip(b: bytes, i: int, bit: int = 0) -> bytes:
    x = bytearray(b)
    x[i] ^= (1 << bit)
    return bytes(x)


class Uretici:
    def __init__(self, kok_dizin):
        self.kok = kok_dizin
        self.vdir = os.path.join(kok_dizin, 'vectors', SURUM)
        self.kdir = os.path.join(kok_dizin, 'keys', SURUM)
        self.S = AnahtarSeti()
        self.items = []
        self.objs = {}

    # ------------------------------------------------------------ helpers
    def kid(self, rol):
        return self.S[rol].kid

    def sig_rec(self, sira, alg, rol, durum, **kw):
        d = {'sira': sira, 'alg': alg, 'alg_sinifi': alg_class(alg), 'anahtar_rolu': rol,
             'kid': self.S[rol].kid if rol else None, 'insa': durum}
        d.update(kw)
        return d

    def ekle(self, vid, aile, obj, meta):
        if isinstance(obj, str):
            ext = 'sdjwt' if '~' in obj else 'jws'
            data = obj.encode('utf-8')
        else:
            ext = 'json'
            data = (json.dumps(obj, indent=1, ensure_ascii=False) + '\n').encode('utf-8')
        rel = '%s/%s.%s' % (aile, vid, ext)
        p = os.path.join(self.vdir, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'wb') as f:
            f.write(data)
        item = {'id': vid, 'dosya': rel, 'sha256': hashlib.sha256(data).hexdigest(), 'bayt': len(data), 'aile': aile}
        item.update(meta)
        self.items.append(item)
        self.objs[vid] = obj
        return obj

    @staticmethod
    def meta(aciklama, artefakt, serilestirme, basamak=(), plan=(), ek=(), dayanak=(), kol=None, senaryo=None,
             sdjwtvc=None, insa=None, girdiler=None, b_pilot=None, dcapi=None):
        return {'aciklama': aciklama, 'artefakt': artefakt, 'serilestirme': serilestirme, 'kol': kol,
                'senaryo': senaryo, 'sdjwtvc_surum': sdjwtvc,
                'sinanan': {'basamak': list(basamak), 'plan_bayraklari': list(plan), 'ek_etiketler': list(ek)},
                'dayanak': list(dayanak), 'insa': insa or {}, 'dogrulama_girdileri': girdiler or {},
                'b_pilot_esi': b_pilot, 'dcapi_protokol': dcapi}

    def girdi(self, roller=(), x5c=False, **kw):
        g = {'jwks': 'anahtarlar/v1/acik-jwks.json', 'kid': [self.kid(r) for r in roller], 'simdi': SIMDI}
        if x5c:
            g['guven_capalari'] = ['anahtarlar/v1/pki/root-ec.pem', 'anahtarlar/v1/pki/root-ml.pem']
        g.update(kw)
        return g

    # ------------------------------------------------------------ T family (pilot B)
    def aile_T(self):
        S = self.S
        roles = {'ES256': 'issuer/ES256', 'EdDSA': 'issuer/EdDSA', 'ML-DSA-65': 'issuer/ML-DSA-65',
                 'ML-DSA-65-ES256': 'issuer/ML-DSA-65-ES256'}

        def gen(*al):
            return jws.sign(B_PAYLOAD, [jws.Signer(S[roles[a]], {}, alg=a) for a in al], 'general', True)

        alg_kid = {a: S[r].kid for a, r in roles.items()}
        base_dayanak = [R['gen'], R['json'], R['dogr'], R['bcp']]
        G = self.girdi(list(roles.values()), anahtar_secimi='alg basligina gore (B pilotundaki gibi; kid yok)',
                       alg_kid=alg_kid)
        for second in ('EdDSA', 'ML-DSA-65', 'ML-DSA-65-ES256'):
            sfx = {'EdDSA': 'K', 'ML-DSA-65': 'P', 'ML-DSA-65-ES256': 'C'}[second]
            extra_ref = {'EdDSA': R['eddsa'], 'ML-DSA-65': R['mldsa'], 'ML-DSA-65-ES256': R['c_alg']}[second]
            t1 = gen('ES256', second)
            self.ekle('T1%s_both_valid' % sfx, 'T', t1, self.meta(
                'General JSON JWS; ES256 + %s, iki imza da gecerli uretildi (B T1).' % second, 'jws-cekirdek', 'general',
                ['L1', 'L2'], ek=['coklu-imza', 'saglik-kontrolu(H0)'], dayanak=base_dayanak + [extra_ref],
                kol=ARM[second], senaryo='d (JWS duzeyi)', b_pilot='T1_both_valid', girdiler=G,
                insa={'imzalar': [self.sig_rec(0, 'ES256', roles['ES256'], 'gecerli'),
                                  self.sig_rec(1, second, roles[second], 'gecerli')]}))
            t2 = copy.deepcopy(t1)
            s = b64u_decode(t2['signatures'][1]['signature'])
            t2['signatures'][1]['signature'] = b64u_encode(flip(s, 5, 0))
            comp = ' (ML-DSA bileseni icinde)' if second in COMPOSITE else ''
            self.ekle('T2%s_second_tampered' % sfx, 'T', t2, self.meta(
                'T1%s ile ayni; ikinci (%s) imzanin 5. baytinin 0. biti cevrildi%s (B T2: s[5]^=1).' % (sfx, second, comp),
                'jws-cekirdek', 'general', ['L4'], ek=['coklu-imza-semantigi(any/all)', 'bozuk-imza'],
                dayanak=base_dayanak + [R['eccg']], kol=ARM[second], senaryo='d (JWS duzeyi)',
                b_pilot='T2_eddsa_tampered', girdiler=G,
                insa={'kaynak_vektor': 'T1%s_both_valid' % sfx,
                      'imzalar': [self.sig_rec(0, 'ES256', roles['ES256'], 'gecerli'),
                                  self.sig_rec(1, second, roles[second], 'bozuk: bayt 5, bit 0 cevrildi' + comp)]}))
            if sfx == 'K':
                t3 = copy.deepcopy(t1)
                t3['signatures'] = t3['signatures'][:1]
                self.ekle('T3_stripped_to_ES256', 'T', t3, self.meta(
                    'T1x\'ten ikinci imza soyuldu; yalniz ES256 kaldi. ES256 imzasi uc kolda da AYNI (ayni yuk, anahtar, '
                    'baslik; belirlenimci) -> tek dosya, tum kollar icin ortak (B T3).', 'jws-cekirdek', 'general',
                    ['L4'], ek=['soyma'], dayanak=base_dayanak + [R['eccg']], kol='ortak', senaryo='d (JWS duzeyi)',
                    b_pilot='T3_stripped_to_ES256', girdiler=G,
                    insa={'kaynak_vektor': 'T1K/T1P/T1C', 'imzalar': [self.sig_rec(0, 'ES256', roles['ES256'], 'gecerli')],
                          'soyulan': 'ikinci imza (EdDSA | ML-DSA-65 | ML-DSA-65-ES256)'}))
        # T4: base + one more valid signature (an alg not in the base set of the arm)
        for sfx, base2, extra in (('K', 'EdDSA', 'ML-DSA-65'), ('P', 'ML-DSA-65', 'ML-DSA-65-ES256'),
                                  ('C', 'ML-DSA-65-ES256', 'ML-DSA-65')):
            t4 = gen('ES256', base2, extra)
            plan = ['bilinmeyen-composite-alg'] if extra in COMPOSITE else []
            self.ekle('T4%s_plus_%s' % (sfx, extra), 'T', t4, self.meta(
                'ES256 + %s + GECERLI %s imzasi (B T4 "plus_unknown_MLDSA65" rastgele bayt idi; burada gercek). '
                'Ek imzanin alg\'i hedef kutuphane icin bilinmiyor olabilir.' % (base2, extra), 'jws-cekirdek', 'general',
                ['L1', 'L4'], plan=plan, ek=['bilinmeyen-alg', 'ek-imza'],
                dayanak=base_dayanak + [R['mldsa'], R['c_alg']], kol=ARM[base2], senaryo='d (JWS duzeyi)',
                b_pilot='T4_plus_unknown_MLDSA65', girdiler=G,
                insa={'imzalar': [self.sig_rec(0, 'ES256', roles['ES256'], 'gecerli'),
                                  self.sig_rec(1, base2, roles[base2], 'gecerli'),
                                  self.sig_rec(2, extra, roles[extra], 'gecerli')]}))
        for sfx, only in (('P', 'ML-DSA-65'), ('C', 'ML-DSA-65-ES256'), ('K', 'EdDSA')):
            t5 = gen(only)
            self.ekle('T5%s_only_%s' % (sfx, only), 'T', t5, self.meta(
                'General JSON; YALNIZ %s imzasi (gecerli). B T5 (only_MLDSA65) rastgele bayt idi.' % only,
                'jws-cekirdek', 'general', ['L1', 'L2', 'L3'], ek=['yalniz-tek-alg'],
                dayanak=base_dayanak + [R['mldsa'] if only == 'ML-DSA-65' else R['c_alg'] if only in COMPOSITE else R['eddsa']],
                kol=ARM[only], senaryo='d (JWS duzeyi)', b_pilot='T5_only_MLDSA65', girdiler=G,
                insa={'imzalar': [self.sig_rec(0, only, roles[only], 'gecerli')]}))
        t6 = gen('ES256', 'EdDSA', 'ML-DSA-65-ES256')
        self.ekle('T6_plus_composite', 'T', t6, self.meta(
            'ES256 + EdDSA + GECERLI composite ML-DSA-65-ES256 imzasi (B T6 "plus_composite_label" rastgele bayt idi).',
            'jws-cekirdek', 'general', ['L1', 'L4'], plan=['bilinmeyen-composite-alg'], ek=['ek-imza'],
            dayanak=base_dayanak + [R['c_alg'], R['c_sign']], kol='kontrol-EdDSA', senaryo='d (JWS duzeyi)',
            b_pilot='T6_plus_composite_label', girdiler=G,
            insa={'imzalar': [self.sig_rec(0, 'ES256', roles['ES256'], 'gecerli'),
                              self.sig_rec(1, 'EdDSA', roles['EdDSA'], 'gecerli'),
                              self.sig_rec(2, 'ML-DSA-65-ES256', roles['ML-DSA-65-ES256'], 'gecerli')]}))
        # B-compatible file (the same structure as B's scripts p3_node.mjs / p3_py.py: pub1=ES256, pub2=EdDSA)
        b = {'pub1': S['issuer/ES256'].public_jwk(kid=False), 'pub2': S['issuer/EdDSA'].public_jwk(kid=False),
             'pub_mldsa65': S['issuer/ML-DSA-65'].public_jwk(kid=False),
             'pub_composite': S['issuer/ML-DSA-65-ES256'].public_jwk(kid=False),
             'vectors': {'T1_both_valid': self.objs['T1K_both_valid'], 'T2_eddsa_tampered': self.objs['T2K_second_tampered'],
                         'T3_stripped_to_ES256': self.objs['T3_stripped_to_ES256'],
                         'T4_plus_unknown_MLDSA65': self.objs['T4K_plus_ML-DSA-65'],
                         'T5_only_MLDSA65': self.objs['T5P_only_ML-DSA-65'],
                         'T6_plus_composite_label': self.objs['T6_plus_composite']}}
        p = os.path.join(self.vdir, 'b-uyumlu', 'vectors.json')
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(b, f, indent=1)
            f.write('\n')

    # ------------------------------------------------------------ UNK family
    def _compact_with_sig(self, header, payload, sig):
        return b64u_encode(json_bytes(header)) + '.' + b64u_encode(payload) + '.' + b64u_encode(sig)

    def _tbs(self, header, payload):
        return (b64u_encode(json_bytes(header)) + '.' + b64u_encode(payload)).encode('ascii')

    def aile_UNK(self):
        S = self.S
        k65, kc = S['issuer/ML-DSA-65'], S['issuer/ML-DSA-65-ES256']
        D = [R['alg'], R['bcp'], R['algkoruma']]
        G = self.girdi(['issuer/ES256', 'issuer/ML-DSA-65', 'issuer/ML-DSA-65-ES256'])
        h = {'alg': 'ML-DSA-66', 'kid': k65.kid, 'typ': 'JWT'}
        self.ekle('UNK01_alg_ML-DSA-66', 'UNK', self._compact_with_sig(
            h, JWT_PAYLOAD, algs.sign('ML-DSA-65', k65, self._tbs(h, JWT_PAYLOAD), True)), self.meta(
            'Compact JWS; alg="ML-DSA-66" (kayitsiz). Imza baytlari issuer/ML-DSA-65 anahtariyla bu imzalama girdisi '
            'uzerinde uretilmis gecerli bir ML-DSA-65 imzasi; kid ML-DSA-65 anahtarini gosteriyor.', 'jws-cekirdek',
            'compact', ['L1'], ek=['bilinmeyen-alg'], dayanak=D + [R['mldsa']], kol='tedavi-ML-DSA-65', girdiler=G,
            insa={'imzalar': [self.sig_rec(0, 'ML-DSA-66', 'issuer/ML-DSA-65', 'ML-DSA-65 ile gecerli bayt; etiket kayitsiz')]}))
        h = {'alg': 'ML-DSA-65-P256', 'kid': kc.kid, 'typ': 'JWT'}
        self.ekle('UNK02_alg_ML-DSA-65-P256', 'UNK', self._compact_with_sig(
            h, JWT_PAYLOAD, composite.sign('ML-DSA-65-ES256', kc, self._tbs(h, JWT_PAYLOAD), True)), self.meta(
            'Compact JWS; alg="ML-DSA-65-P256" (akla yakin ama KAYITSIZ composite adi; -04 adi ML-DSA-65-ES256). '
            'Imza, bu girdi uzerinde gecerli bir ML-DSA-65-ES256 composite imzasi.', 'jws-cekirdek', 'compact', ['L1'],
            plan=['bilinmeyen-composite-alg'], dayanak=D + [R['c_alg']], kol='tedavi-composite', girdiler=G,
            insa={'imzalar': [self.sig_rec(0, 'ML-DSA-65-P256', 'issuer/ML-DSA-65-ES256',
                                            'ML-DSA-65-ES256 ile gecerli bayt; etiket kayitsiz')]}))
        h = {'alg': 'ml-dsa-65', 'kid': k65.kid, 'typ': 'JWT'}
        self.ekle('UNK03_alg_kucuk_harf', 'UNK', self._compact_with_sig(
            h, JWT_PAYLOAD, algs.sign('ML-DSA-65', k65, self._tbs(h, JWT_PAYLOAD), True)), self.meta(
            'Compact JWS; alg="ml-dsa-65" (kucuk harf). RFC 7515 4.1.1: alg degeri buyuk/kucuk harfe duyarli. '
            'Imza ML-DSA-65 ile gecerli.', 'jws-cekirdek', 'compact', ['L1'], ek=['alg-buyuk-kucuk-harf'],
            dayanak=D + [R['mldsa']], kol='tedavi-ML-DSA-65', girdiler=G,
            insa={'imzalar': [self.sig_rec(0, 'ml-dsa-65', 'issuer/ML-DSA-65', 'ML-DSA-65 ile gecerli bayt; etiket kucuk harf')]}))
        g = jws.sign(JWT_PAYLOAD, [jws.Signer(S['issuer/ES256'], {'kid': self.kid('issuer/ES256')}, alg='ES256'),
                                   jws.Signer(k65, {'kid': k65.kid}, alg='ML-DSA-65')], 'general', True)
        hh = {'alg': 'ML-DSA-65-P256', 'kid': kc.kid}
        pb = b64u_encode(json_bytes(hh))
        g['signatures'].append({'protected': pb, 'signature': b64u_encode(
            composite.sign('ML-DSA-65-ES256', kc, (pb + '.' + g['payload']).encode(), True))})
        self.ekle('UNK04_general_arti_kayitsiz_composite', 'UNK', g, self.meta(
            'General JSON; ES256 + ML-DSA-65 (gecerli) + alg="ML-DSA-65-P256" (kayitsiz etiket, gecerli composite bayt).',
            'jws-cekirdek', 'general', ['L1', 'L4'], plan=['bilinmeyen-composite-alg'], ek=['ek-imza'],
            dayanak=D + [R['gen'], R['json']], kol='tedavi-ML-DSA-65', senaryo='d (JWS duzeyi)', girdiler=G,
            insa={'imzalar': [self.sig_rec(0, 'ES256', 'issuer/ES256', 'gecerli'),
                              self.sig_rec(1, 'ML-DSA-65', 'issuer/ML-DSA-65', 'gecerli'),
                              self.sig_rec(2, 'ML-DSA-65-P256', 'issuer/ML-DSA-65-ES256',
                                           'ML-DSA-65-ES256 ile gecerli bayt; etiket kayitsiz')]}))
        g2 = copy.deepcopy(self.objs['UNK04_general_arti_kayitsiz_composite'])
        g2['signatures'][2] = {'protected': b64u_encode(json_bytes({'alg': 'none'})), 'signature': ''}
        self.ekle('UNK05_general_arti_alg_none', 'UNK', g2, self.meta(
            'General JSON; ES256 + ML-DSA-65 (gecerli) + {"alg":"none"} bos imza.', 'jws-cekirdek', 'general',
            ['L1', 'L4'], ek=['alg-none', 'ek-imza'], dayanak=D + [R['gen']], kol='tedavi-ML-DSA-65',
            senaryo='d (JWS duzeyi)', girdiler=G,
            insa={'kaynak_vektor': 'UNK04', 'imzalar': [self.sig_rec(0, 'ES256', 'issuer/ES256', 'gecerli'),
                                                          self.sig_rec(1, 'ML-DSA-65', 'issuer/ML-DSA-65', 'gecerli'),
                                                          self.sig_rec(2, 'none', None, 'bos imza')]}))

    # ------------------------------------------------------------ CMP family
    def _cmp_parts(self, alg, ck, tbs, ph=None, ctx=True, zero=True):
        p = COMPOSITE[alg]
        mp = PREFIX + p['label'] + (b'\x00' if zero else b'') + composite.prehash(ph or p['ph'], tbs)
        ml = mldsa.sign(p['ml'], ck.ml.seed, mp, ctx=p['label'] if ctx else b'', deterministic=True)
        if p['trad'] == 'ECDSA':
            md = hashes.SHA256() if p['md'] == 'sha256' else hashes.SHA384()
            d = ck.trad.priv.sign(mp, ec.ECDSA(md, deterministic_signing=True))
            tr = ecdsa_raw_to_der(ecdsa_der_to_raw(d, p['crv']), p['crv'])
        else:
            tr = ck.trad.priv.sign(mp)
        return ml, tr

    def aile_CMP(self):
        S = self.S
        alg = 'ML-DSA-65-ES256'
        ck = S['issuer/' + alg]
        h = {'alg': alg, 'kid': ck.kid, 'typ': 'JWT'}
        tbs = self._tbs(h, JWT_PAYLOAD)
        ml, tr = self._cmp_parts(alg, ck, tbs)
        D = [R['c_sign'], R['c_verify'], R['c_enc'], R['c_label']]
        G = self.girdi(['issuer/' + alg])
        rec = lambda s: {'imzalar': [self.sig_rec(0, alg, 'issuer/' + alg, s)]}  # noqa: E731

        def put(vid, sig, acik, ek, dayanak, insa_s, basamak=('L4',), h_=h, girdiler=G, kol='tedavi-composite'):
            self.ekle(vid, 'CMP', self._compact_with_sig(h_, JWT_PAYLOAD, sig), self.meta(
                acik, 'jws-cekirdek', 'compact', list(basamak), ek=['composite-bilesen-dogrulugu'] + list(ek),
                dayanak=dayanak, kol=kol, senaryo='a', girdiler=girdiler, insa=insa_s))

        put('CMP00_gecerli_referans', ml + tr, 'Referans: gecerli ML-DSA-65-ES256 compact JWS (bozulmalarin tabani).', [],
            D, rec('gecerli'), basamak=('L1',))
        put('CMP01_ml_bileseni_bozuk', flip(ml, len(ml) // 2) + tr,
            'ML-DSA bileseninin orta baytinda bit cevrildi; ECDSA bileseni gecerli.', ['bilesen-bozulmasi'], D,
            rec('ML-DSA bileseni bozuk (bayt %d, bit 0); ECDSA bileseni gecerli' % (len(ml) // 2)))
        lr = tr[3]
        put('CMP02_ecdsa_bileseni_bozuk', ml + flip(tr, 4 + lr - 1),
            'ECDSA bileseninde r degerinin son baytinda bit cevrildi (DER yapisi gecerli); ML-DSA bileseni gecerli.',
            ['bilesen-bozulmasi'], D + [R['c_der']], rec('ECDSA bileseni bozuk (r son bayt); ML-DSA gecerli'))
        put('CMP03_ecdsa_der_uzunluk_bozuk', ml + tr[:1] + bytes([tr[1] + 1]) + tr[2:],
            'ECDSA bileseninin DER SEQUENCE uzunluk bayti +1 (yapisal bozulma).', ['serilestirme'], D + [R['c_der']],
            rec('ECDSA DER uzunluk bayti bozuk'))
        raw = ecdsa_der_to_raw(tr, 'P-256')
        put('CMP04_ecdsa_ham_rs', ml + raw,
            'ECDSA bileseni DER yerine JOSE ES256 tarzi HAM r||s (64 B) kodlandi (olasi uygulayici hatasi; -04 4.5.1 DER ister). '
            'r,s degerleri gecerli bir imzaya ait.', ['serilestirme', 'uygulayici-hatasi-taklidi'], D + [R['c_der'], R['es256']],
            rec('ECDSA bileseni ham r||s (DER degil); degerler gecerli'))

        def dint(v, pad):
            t = v.lstrip(b'\x00') or b'\x00'
            if t[0] >= 0x80:
                t = b'\x00' + t
            t = b'\x00' * pad + t
            return b'\x02' + bytes([len(t)]) + t
        body = dint(raw[:32], 1) + dint(raw[32:], 0)
        put('CMP05_ecdsa_asgari_olmayan_der', ml + b'\x30' + bytes([len(body)]) + body,
            'ECDSA bileseni asgari olmayan DER (r onunde fazladan 0x00); sayisal degerler gecerli imzaya ait.',
            ['serilestirme', 'der-kanoniklik'], D + [R['c_der']], rec('asgari olmayan DER; degerler gecerli'))
        put('CMP06_sonda_artik_bayt', ml + tr + b'\x00', 'Gecerli composite imzanin sonuna 0x00 eklendi.',
            ['serilestirme'], D, rec('gecerli imza + artik bayt'))
        put('CMP07_yalniz_ml_bileseni', ml, 'ECDSA bileseni kesildi; yalniz ML-DSA bileseni (3309 B) kaldi.',
            ['serilestirme', 'bilesen-soyma'], D, rec('yalniz ML-DSA bileseni'))
        h2 = copy.deepcopy(h)
        tbs2 = self._tbs(h2, json_bytes({'iss': A.ISS, 'iat': A.T0, 'vct': A.VCT, 'given_name': 'Mallory'}))
        ml2, tr2 = self._cmp_parts(alg, ck, tbs2)
        put('CMP08_bilesenler_farkli_iletilerden', ml2 + tr,
            'ML-DSA bileseni baska bir yukun imzasindan, ECDSA bileseni bu yukun imzasindan (ayni anahtar).',
            ['bilesen-karistirma'], D, rec('ML-DSA bileseni baska ileti; ECDSA bileseni gecerli'))
        ml_noctx, tr_n = self._cmp_parts(alg, ck, tbs, ctx=False)
        put('CMP09_ml_bileseni_ctx_bos', ml_noctx + tr_n,
            'ML-DSA bileseni ctx=Label yerine BOS ctx ile imzalandi (olasi uygulayici hatasi; -04 4.2 ctx=Label ister); '
            "M' dogru; ECDSA bileseni gecerli.", ['uygulayici-hatasi-taklidi'], D,
            rec('ML-DSA bileseni ctx bos; ECDSA gecerli'))
        ml_ph, tr_ph = self._cmp_parts(alg, ck, tbs, ph='sha256')
        put('CMP10_onozet_sha256', ml_ph + tr_ph,
            "Her iki bilesen de SHA-256 on-ozetli M' uzerinde tutarli imzalandi (dogrusu SHA-512; -04 Tablo 5). "
            "Uygulayici hatasi taklidi: -04 7.1.2 IANA aciklamasi 'P-256 curve and SHA-256' der.",
            ['uygulayici-hatasi-taklidi', 'spesifikasyon-belirsizligi'], D + [R['c_alg'], R['c_iana']],
            rec("iki bilesen de yanlis on-ozetli M' uzerinde gecerli"))
        ml_nz, tr_nz = self._cmp_parts(alg, ck, tbs, zero=False)
        put('CMP11_bos_ctx_uzunlugu_yok', ml_nz + tr_nz,
            "M' icinde Label'dan sonraki 0x00 (bos baglam uzunlugu) atlandi; iki bilesen bu M' uzerinde tutarli.",
            ['uygulayici-hatasi-taklidi'], D, rec("iki bilesen de 0x00'siz M' uzerinde gecerli"))
        # separability: reuse of the component keys as independent keys
        trad_pub = ck.trad.public_only()
        ml_pub = MLDSAKey('ML-DSA-65', pub=ck.ml.pub)
        tkid, mkid = trad_pub.thumbprint(), ml_pub.thumbprint()
        G2 = {'jwks': 'anahtarlar/v1/bilesen-yeniden-kullanim-jwks.json', 'kid': [tkid], 'simdi': SIMDI}
        he = {'alg': 'ES256', 'kid': tkid, 'typ': 'JWT'}
        self.ekle('CMP12_ayrilabilirlik_ecdsa_ES256', 'CMP', self._compact_with_sig(he, JWT_PAYLOAD, raw), self.meta(
            "Composite imzanin ECDSA bileseni (M' uzerinde) ham r||s'ye cevrilip ES256 JWS imzasi olarak sunuldu. "
            'Dogrulama anahtari: composite\'in EC bileseni BAGIMSIZ ES256 anahtari olarak (anahtar yeniden kullanimi '
            'senaryosu; -04 6.2 bunu yasaklar).', 'jws-cekirdek', 'compact', ['L3'],
            ek=['ayrilabilirlik', 'anahtar-yeniden-kullanimi'], dayanak=[R['c_sep'], R['c_reuse'], R['bcp'], R['es256']],
            kol='tedavi-composite', senaryo='a', girdiler=G2,
            insa={'kaynak_vektor': 'CMP00', 'imzalar': [{'sira': 0, 'alg': 'ES256', 'alg_sinifi': 'klasik',
                                                          'anahtar_rolu': 'issuer/ML-DSA-65-ES256#trad', 'kid': tkid,
                                                          'insa': "composite'in ECDSA bileseni (M' uzerinde)"}]}))
        hm = {'alg': 'ML-DSA-65', 'kid': mkid, 'typ': 'JWT'}
        G3 = {'jwks': 'anahtarlar/v1/bilesen-yeniden-kullanim-jwks.json', 'kid': [mkid], 'simdi': SIMDI}
        self.ekle('CMP13_ayrilabilirlik_ml_MLDSA65', 'CMP', self._compact_with_sig(hm, JWT_PAYLOAD, ml), self.meta(
            "Composite imzanin ML-DSA bileseni (M' ve ctx=Label uzerinde) ML-DSA-65 JWS imzasi olarak sunuldu. "
            "Dogrulama anahtari: composite'in ML-DSA bileseni bagimsiz AKP anahtari olarak.", 'jws-cekirdek', 'compact',
            ['L3'], ek=['ayrilabilirlik', 'anahtar-yeniden-kullanimi'],
            dayanak=[R['c_sep'], R['c_reuse'], R['bcp'], R['mldsa']], kol='tedavi-composite', senaryo='a', girdiler=G3,
            insa={'kaynak_vektor': 'CMP00', 'imzalar': [{'sira': 0, 'alg': 'ML-DSA-65', 'alg_sinifi': 'pq',
                                                          'anahtar_rolu': 'issuer/ML-DSA-65-ES256#ml', 'kid': mkid,
                                                          'insa': "composite'in ML-DSA bileseni (M', ctx=Label)"}]}))
        # composite with EdDSA
        alg2 = 'ML-DSA-65-Ed25519'
        ck2 = S['issuer/' + alg2]
        h3 = {'alg': alg2, 'kid': ck2.kid, 'typ': 'JWT'}
        ml3, tr3 = self._cmp_parts(alg2, ck2, self._tbs(h3, JWT_PAYLOAD))
        G4 = self.girdi(['issuer/' + alg2])
        rec2 = lambda s: {'imzalar': [self.sig_rec(0, alg2, 'issuer/' + alg2, s)]}  # noqa: E731
        put('CMP14_ed25519_ml_bileseni_bozuk', flip(ml3, 100) + tr3, 'ML-DSA-65-Ed25519: ML-DSA bileseni bozuk (bayt 100).',
            ['bilesen-bozulmasi'], D, rec2('ML-DSA bileseni bozuk; Ed25519 gecerli'), h_=h3, girdiler=G4, kol='kapsam-hibrit')
        put('CMP15_ed25519_eddsa_bileseni_bozuk', ml3 + flip(tr3, 10), 'ML-DSA-65-Ed25519: Ed25519 bileseni bozuk (bayt 10).',
            ['bilesen-bozulmasi'], D, rec2('Ed25519 bileseni bozuk; ML-DSA gecerli'), h_=h3, girdiler=G4, kol='kapsam-hibrit')
        put('CMP16_bilesen_sirasi_ters', tr + ml, 'ML-DSA-65-ES256: bilesen sirasi ters (tradSig || mldsaSig).',
            ['serilestirme'], D + [R['c_enc']], rec('bilesen sirasi ters'))

    # ------------------------------------------------------------ X5C family (with SD-JWT VC)
    def _vc_compact(self, cred_id, key, alg, prot, holder='holder/ES256'):
        payload, labeled = A.pid_payload(cred_id, self.S[holder].public_jwk(kid=False))
        jwt = jws.sign(json_bytes(payload), jws.Signer(key, prot, alg=alg), 'compact', True)
        return jwt + '~' + ''.join(d + '~' for _, d in labeled), payload, labeled

    def _vc_flattened(self, cred_id, key, alg, prot, header):
        payload, labeled = A.pid_payload(cred_id, self.S['holder/ES256'].public_jwk(kid=False))
        fl = jws.sign(json_bytes(payload), jws.Signer(key, prot, header=header, alg=alg), 'flattened', True)
        out = {'header': dict(fl.get('header') or {}), 'payload': fl['payload'], 'protected': fl['protected'],
               'signature': fl['signature']}
        out['header']['disclosures'] = [d for _, d in labeled]
        return out

    def aile_X5C(self):
        S = self.S
        D = [R['x5c'], R['haip_x5c'], R['vc19_key'], R['vc13_key']]
        cases = [
            ('X5C01_klasik_zincir', 'issuer/ES256', 'ES256', 'issuer-ec@int-ec', 'tam-klasik', [], ['x5c-zincir']),
            ('X5C02_pq_zincir', 'issuer/ML-DSA-65', 'ML-DSA-65', 'issuer-ml@int-ml', 'tam-pq', [], ['x5c-zincir']),
            ('X5C03_karisik_klasik_yaprak_pq_ara', 'issuer/ES256', 'ES256', 'issuer-ec@int-ml', 'karisik',
             ['karisik-x5c'], []),
            ('X5C04_karisik_pq_yaprak_klasik_ara', 'issuer/ML-DSA-65', 'ML-DSA-65', 'issuer-ml@int-ec', 'karisik',
             ['karisik-x5c'], []),
            ('X5C05_karisik_pq_ara_klasik_kok', 'issuer/ML-DSA-65', 'ML-DSA-65', 'issuer-ml@int-ml-rootec', 'karisik',
             ['karisik-x5c'], ['kok-halkasi-klasik']),
        ]
        for vid, rol, alg, leaf, cls, plan, ek in cases:
            prot = {'typ': 'dc+sd-jwt', 'x5c': S.x5c(leaf)}
            obj, _, _ = self._vc_compact(vid, S[rol], alg, prot)
            c = S.certs[leaf]
            zincir = [c.name, c.issuer.name, c.issuer.issuer.name + ' (guven capasi; x5c disinda)']
            self.ekle(vid, 'X5C', obj, self.meta(
                'SD-JWT VC (compact, PID); %s imzasi; x5c = [%s, %s]; zincir sinifi: %s.' % (alg, c.name, c.issuer.name, cls),
                'sd-jwt-vc', 'sd-jwt-compact', ['L3'], plan=plan, ek=ek, dayanak=D, kol=kol_of(alg),
                sdjwtvc=['-13', '-19'], girdiler=self.girdi([rol], x5c=True),
                insa={'imzalar': [self.sig_rec(0, alg, rol, 'gecerli')],
                      'x5c': {'zincir': zincir, 'sinif': cls, 'korumali': True, 'kok_x5c_icinde': False}}))
        # trust anchor inside x5c
        rol, alg, leaf = 'issuer/ML-DSA-65', 'ML-DSA-65', 'issuer-ml@int-ml'
        c = S.certs[leaf]
        prot = {'typ': 'dc+sd-jwt', 'x5c': pki.x5c(c, c.issuer, c.issuer.issuer)}
        obj, _, _ = self._vc_compact('X5C06', S[rol], alg, prot)
        self.ekle('X5C06_guven_capasi_x5c_icinde', 'X5C', obj, self.meta(
            'X5C02 ile ayni zincir, ancak x5c kok sertifikayi (root-ml) da iceriyor (HAIP 6.1.1: guven capasi x5c\'ye KONMAZ).',
            'sd-jwt-vc', 'sd-jwt-compact', ['L3'], ek=['x5c-guven-capasi-icinde'], dayanak=D, kol=kol_of(alg),
            sdjwtvc=['-13', '-19'], girdiler=self.girdi([rol], x5c=True),
            insa={'imzalar': [self.sig_rec(0, alg, rol, 'gecerli')],
                  'x5c': {'zincir': [leaf, 'int-ml', 'root-ml'], 'sinif': 'tam-pq', 'korumali': True, 'kok_x5c_icinde': True}}))
        # unprotected x5c (flattened JSON SD-JWT)
        fl = self._vc_flattened('X5C07', S[rol], alg, {'typ': 'dc+sd-jwt'}, {'x5c': S.x5c(leaf)})
        DD = [R['x5c'], R['flat'], R['sd_json'], R['sd_flat'], R['haip_x5c']]
        self.ekle('X5C07_korumasiz_x5c', 'X5C', fl, self.meta(
            'SD-JWT VC flattened JSON (RFC 9901 8.2); x5c KORUMASIZ baslikta (tam-PQ zincir); korumali baslik {alg,typ}.',
            'sd-jwt-vc', 'sd-jwt-flattened', ['L3'], plan=['korumasiz-x5c'], dayanak=DD, kol=kol_of(alg),
            sdjwtvc=['-13'], girdiler=self.girdi([rol], x5c=True),
            insa={'imzalar': [self.sig_rec(0, alg, rol, 'gecerli')],
                  'x5c': {'zincir': [leaf, 'int-ml'], 'sinif': 'tam-pq', 'korumali': False}}))
        fl2 = copy.deepcopy(fl)
        fl2['header']['x5c'] = S.x5c('issuer-ml@int-ec')
        self.ekle('X5C08_korumasiz_x5c_zincir_degisimi', 'X5C', fl2, self.meta(
            'X5C07 ile imza bayt-bayt ayni; korumasiz x5c, AYNI yaprak anahtari icin klasik CA zinciriyle '
            '[issuer-ml@int-ec, int-ec] degistirildi (imzayi bozmadan zincir sinifi dusurme).', 'sd-jwt-vc',
            'sd-jwt-flattened', ['L3'], plan=['korumasiz-x5c', 'karisik-x5c'], ek=['zincir-ikamesi'], dayanak=DD,
            kol=kol_of(alg), sdjwtvc=['-13'], girdiler=self.girdi([rol], x5c=True),
            insa={'kaynak_vektor': 'X5C07', 'imzalar': [self.sig_rec(0, alg, rol, 'gecerli')],
                  'x5c': {'zincir': ['issuer-ml@int-ec', 'int-ec'], 'sinif': 'karisik', 'korumali': False}}))
        fl3 = self._vc_flattened('X5C09', S[rol], alg, {'typ': 'dc+sd-jwt', 'x5c': S.x5c(leaf)}, None)
        fl3['header']['x5c'] = S.x5c('issuer-ml@int-ec')
        self.ekle('X5C09_korumali_ve_korumasiz_x5c', 'X5C', fl3, self.meta(
            'Flattened JSON; x5c HEM korumali (tam-PQ zincir) HEM korumasiz baslikta (karisik zincir). '
            'RFC 7515 7.2.1: korumali/korumasiz baslik adlari ayrik olmali.', 'sd-jwt-vc', 'sd-jwt-flattened', ['L3'],
            plan=['korumasiz-x5c'], ek=['baslik-ayriklik-ihlali'], dayanak=DD + [R['gen']], kol=kol_of(alg),
            sdjwtvc=['-13'], girdiler=self.girdi([rol], x5c=True),
            insa={'imzalar': [self.sig_rec(0, alg, rol, 'gecerli')],
                  'x5c': {'korumali_zincir': [leaf, 'int-ml'], 'korumasiz_zincir': ['issuer-ml@int-ec', 'int-ec']}}))
        prot = {'typ': 'dc+sd-jwt', 'x5c': S.x5c(leaf), 'kid': self.kid('issuer/ES256')}
        obj, _, _ = self._vc_compact('X5C10', S[rol], alg, prot)
        self.ekle('X5C10_x5c_ve_baska_anahtar_kid', 'X5C', obj, self.meta(
            'Korumali baslikta x5c (tam-PQ zincir; imza bu yaprak anahtariyla gecerli) VE baska bir anahtari '
            '(issuer/ES256) gosteren kid. Anahtar cozumleme belirsizligi.', 'sd-jwt-vc', 'sd-jwt-compact', ['L3'],
            ek=['anahtar-cozumleme-belirsizligi'], dayanak=D + [R['bcp']], kol=kol_of(alg), sdjwtvc=['-13', '-19'],
            girdiler=self.girdi([rol, 'issuer/ES256'], x5c=True),
            insa={'imzalar': [self.sig_rec(0, alg, rol, 'x5c yapragiyla gecerli; kid issuer/ES256\'yi gosteriyor')],
                  'x5c': {'zincir': [leaf, 'int-ml'], 'sinif': 'tam-pq', 'korumali': True}}))

    # ------------------------------------------------------------ REQ family
    def aile_REQ(self):
        S = self.S
        enc = S['rp/enc'].public_jwk(kid=False)
        cid_ec = A.x509_hash_client_id(S.certs['rp-ec@int-ec'].der)
        cid_ml = A.x509_hash_client_id(S.certs['rp-ml@int-ml'].der)
        D = [R['vp_req'], R['vp_cid'], R['vp_sig'], R['haip_vp'], R['jar'], R['typ']]
        for vid, rol, alg, leaf, cid in (('REQ01_imzali_ES256_x509_hash', 'rp/ES256', 'ES256', 'rp-ec@int-ec', cid_ec),
                                          ('REQ02_imzali_MLDSA65_x509_hash', 'rp/ML-DSA-65', 'ML-DSA-65', 'rp-ml@int-ml', cid_ml)):
            obj = A.request_compact(S[rol], alg, A.request_params(enc, cid), S.x5c(leaf))
            self.ekle(vid, 'REQ', obj, self.meta(
                'OID4VP istek nesnesi (DC API, compact); typ=oauth-authz-req+jwt; %s; client_id=x509_hash (yaprak %s).'
                % (alg, leaf), 'oid4vp-istek', 'compact', ['L1', 'L3'], ek=['x509_hash'], dayanak=D, kol=kol_of(alg),
                girdiler=self.girdi([rol], x5c=True, beklenen_origin=A.ORIGIN), dcapi='openid4vp-v1-signed',
                insa={'imzalar': [self.sig_rec(0, alg, rol, 'gecerli')], 'client_id': cid,
                      'x5c': {'zincir': [leaf, S.certs[leaf].issuer.name]}}))
        cid_pre = 'rp.example.pq'
        obj = A.request_compact(S['rp/ML-DSA-65-ES256'], 'ML-DSA-65-ES256', A.request_params(enc, cid_pre))
        self.ekle('REQ03_imzali_composite_onkayitli', 'REQ', obj, self.meta(
            'OID4VP istek nesnesi (compact); ML-DSA-65-ES256; kid ile; client_id onkayitli (onek yok, "rp.example.pq"): '
            'composite X.509 olmadigi icin x509_hash kullanilamadi (bant disi anahtar, M-d).', 'oid4vp-istek', 'compact',
            ['L1', 'L3'], ek=['onkayitli-istemci(M-d)'], dayanak=[R['vp_req'], R['vp_cid'], R['vp_sig'], R['c_alg']],
            kol='tedavi-composite', senaryo='a', girdiler=self.girdi(['rp/ML-DSA-65-ES256'], beklenen_origin=A.ORIGIN),
            dcapi='openid4vp-v1-signed',
            insa={'imzalar': [self.sig_rec(0, 'ML-DSA-65-ES256', 'rp/ML-DSA-65-ES256', 'gecerli')], 'client_id': cid_pre}))
        params_multi = A.request_params(enc, None)
        multi = A.request_multisigned(params_multi, [(S['rp/ES256'], 'ES256', S.x5c('rp-ec@int-ec'), cid_ec),
                                                     (S['rp/ML-DSA-65'], 'ML-DSA-65', S.x5c('rp-ml@int-ml'), cid_ml)])
        DM = [R['vp_multi'], R['haip_dc'], R['gen'], R['json'], R['vp_cid']]
        GM = self.girdi(['rp/ES256', 'rp/ML-DSA-65'], x5c=True, beklenen_origin=A.ORIGIN)
        irec = [self.sig_rec(0, 'ES256', 'rp/ES256', 'gecerli', client_id=cid_ec),
                self.sig_rec(1, 'ML-DSA-65', 'rp/ML-DSA-65', 'gecerli', client_id=cid_ml)]
        self.ekle('REQ04_coklu_imzali', 'REQ', multi, self.meta(
            'OID4VP A.3.2.2 coklu imzali istek (General JSON): ES256 (klasik guven cercevesi, x509_hash) + ML-DSA-65 '
            '(PQ guven cercevesi, x509_hash); client_id her imzanin korumali basliginda.', 'oid4vp-istek', 'general',
            ['L4'], ek=['coklu-imzali-istek'], dayanak=DM, kol='tedavi-ML-DSA-65', senaryo='c', girdiler=GM,
            dcapi='openid4vp-v1-multisigned', insa={'imzalar': irec}))
        m5 = copy.deepcopy(multi)
        m5['signatures'] = m5['signatures'][:1]
        self.ekle('REQ05_coklu_imzali_pq_soyuldu', 'REQ', m5, self.meta(
            'REQ04\'ten ML-DSA-65 imzasi soyuldu; yalniz ES256 (klasik) imza kaldi.', 'oid4vp-istek', 'general', ['L4'],
            ek=['soyma', 'coklu-imzali-istek'], dayanak=DM + [R['eccg']], kol='tedavi-ML-DSA-65', senaryo='c', girdiler=GM,
            dcapi='openid4vp-v1-multisigned', insa={'kaynak_vektor': 'REQ04', 'imzalar': irec[:1]}))
        m6 = copy.deepcopy(multi)
        m6['signatures'] = m6['signatures'][1:]
        self.ekle('REQ06_coklu_imzali_klasik_soyuldu', 'REQ', m6, self.meta(
            'REQ04\'ten ES256 imzasi soyuldu; yalniz ML-DSA-65 imza kaldi.', 'oid4vp-istek', 'general', ['L4'],
            ek=['soyma', 'coklu-imzali-istek'], dayanak=DM, kol='tedavi-ML-DSA-65', senaryo='c', girdiler=GM,
            dcapi='openid4vp-v1-multisigned',
            insa={'kaynak_vektor': 'REQ04', 'imzalar': [dict(irec[1], sira=0)]}))
        m7 = copy.deepcopy(multi)
        sb = b64u_decode(m7['signatures'][1]['signature'])
        m7['signatures'][1]['signature'] = b64u_encode(flip(sb, 5))
        self.ekle('REQ07_coklu_imzali_pq_bozuk', 'REQ', m7, self.meta(
            'REQ04; ML-DSA-65 imzasinin 5. baytinda bit cevrildi.', 'oid4vp-istek', 'general', ['L4'],
            ek=['bozuk-imza', 'coklu-imzali-istek'], dayanak=DM, kol='tedavi-ML-DSA-65', senaryo='c', girdiler=GM,
            dcapi='openid4vp-v1-multisigned',
            insa={'kaynak_vektor': 'REQ04', 'imzalar': [irec[0], dict(irec[1], insa='bozuk: bayt 5, bit 0')]}))
        DU = [R['vp_uns'], R['vp_dcreq'], R['haip_dc']]
        self.ekle('REQ08_imzasiz_M-b0', 'REQ', {'protocol': 'openid4vp-v1-unsigned',
                                               'data': A.request_params(enc, None, expected_origins=False)}, self.meta(
            'M-b0 imzasizlastirma: ayni istek parametreleri DC API imzasiz istek olarak (openid4vp-v1-unsigned); '
            'client_id ve expected_origins yok (A.2: imzasiz istekte client_id OLMAMALI).', 'oid4vp-istek',
            'dcapi-json-parametre', [], ek=['imzasizlastirma(M-b0)'], dayanak=DU, senaryo='M-b0',
            girdiler={'simdi': SIMDI, 'origin': A.ORIGIN}, dcapi='openid4vp-v1-unsigned',
            insa={'imzalar': [], 'kaynak_vektor': 'REQ02 (parametreler)'}))
        self.ekle('REQ09_imzasiz_M-b0_client_id_korundu', 'REQ', {'protocol': 'openid4vp-v1-unsigned',
                                                                 'data': A.request_params(enc, cid_ml)}, self.meta(
            'M-b0: REQ02\'nin imzali yuku imzasi atilarak imzasiz istek olarak sunuldu; client_id (x509_hash, PQ yaprak) '
            've expected_origins KORUNDU (A.2: cuzdan imzasiz istekte client_id ve expected_origins\'i yok saymali).',
            'oid4vp-istek', 'dcapi-json-parametre', [], ek=['imzasizlastirma(M-b0)', 'kimlik-dogrulanmamis-client_id'],
            dayanak=DU, senaryo='M-b0', girdiler={'simdi': SIMDI, 'origin': A.ORIGIN}, dcapi='openid4vp-v1-unsigned',
            insa={'imzalar': [], 'kaynak_vektor': 'REQ02 (yuk)', 'client_id': cid_ml}))
        h = {'alg': 'none', 'typ': 'oauth-authz-req+jwt'}
        obj = b64u_encode(json_bytes(h)) + '.' + b64u_encode(json_bytes(A.request_params(enc, cid_ml))) + '.'
        self.ekle('REQ10_istek_alg_none', 'REQ', obj, self.meta(
            'Istek nesnesi alg=none (imzasiz JWT; bos imza), typ=oauth-authz-req+jwt, client_id=x509_hash (PQ yaprak), '
            'x5c yok.', 'oid4vp-istek', 'compact', ['L1'], ek=['alg-none', 'imzasizlastirma(M-b0)'],
            dayanak=[R['vp_req'], R['jar_val'], R['alg']], senaryo='M-b0',
            girdiler={'simdi': SIMDI, 'origin': A.ORIGIN}, dcapi='openid4vp-v1-signed',
            insa={'imzalar': [{'sira': 0, 'alg': 'none', 'insa': 'bos imza'}], 'client_id': cid_ml}))

    # ------------------------------------------------------------ VC family
    def aile_VC(self):
        S = self.S
        hold = S['holder/ES256'].public_jwk(kid=False)
        Dc = [R['sd_iss'], R['sd_disc'], R['vc19_hdr'], R['vc13_hdr'], R['vc19_cl']]
        single = [
            ('VC01_ES256_x5c', 'issuer/ES256', 'ES256', 'issuer-ec@int-ec', [R['haip_x5c'], R['haip_sig']]),
            ('VC02_MLDSA65_x5c', 'issuer/ML-DSA-65', 'ML-DSA-65', 'issuer-ml@int-ml', [R['haip_x5c'], R['mldsa']]),
            ('VC03_composite_kid', 'issuer/ML-DSA-65-ES256', 'ML-DSA-65-ES256', None, [R['c_alg']]),
            ('VC04_MLDSA44_kid', 'issuer/ML-DSA-44', 'ML-DSA-44', None, [R['mldsa']]),
            ('VC05_MLDSA87_kid', 'issuer/ML-DSA-87', 'ML-DSA-87', None, [R['mldsa']]),
            ('VC06_composite_Ed25519_kid', 'issuer/ML-DSA-65-Ed25519', 'ML-DSA-65-Ed25519', None, [R['c_alg']]),
        ]
        for vid, rol, alg, leaf, extra in single:
            vc = A.issue_vc(vid, [(S[rol], alg, S.x5c(leaf) if leaf else None)], hold)
            kid_note = '' if leaf else ' (x5c yok: composite/ek ML-DSA duzeyleri icin kid; composite X.509 kapsam disi)'
            self.ekle(vid, 'VC', vc['obj'], self.meta(
                'SD-JWT VC ihraci (compact; typ=dc+sd-jwt; PID; 10 ifsa + 2 sahte ozet; cnf.jwk=holder/ES256); %s%s.'
                % (alg, ', x5c=[%s, ara CA]' % leaf if leaf else kid_note), 'sd-jwt-vc', 'sd-jwt-compact', ['L1', 'L3'],
                dayanak=Dc + extra, kol=kol_of(alg), senaryo='a' if alg in COMPOSITE else None, sdjwtvc=['-13', '-19'],
                girdiler=self.girdi([rol], x5c=bool(leaf)),
                insa={'imzalar': [self.sig_rec(0, alg, rol, 'gecerli')], 'ifsa_sayisi': len(vc['labeled'])}))
        gj_cases = [
            ('VC07_GJ_ES256_MLDSA65', [('issuer/ES256', 'ES256', 'issuer-ec@int-ec'), ('issuer/ML-DSA-65', 'ML-DSA-65', 'issuer-ml@int-ml')],
             'tedavi-ML-DSA-65'),
            ('VC08_GJ_ES256_composite', [('issuer/ES256', 'ES256', 'issuer-ec@int-ec'), ('issuer/ML-DSA-65-ES256', 'ML-DSA-65-ES256', None)],
             'tedavi-composite'),
            ('VC09_GJ_ES256_EdDSA', [('issuer/ES256', 'ES256', 'issuer-ec@int-ec'), ('issuer/EdDSA', 'EdDSA', None)],
             'kontrol-EdDSA'),
        ]
        Dg = [R['sd_gen'], R['sd_json'], R['vc13_fmt'], R['vc19_fmt'], R['haip_pre'], R['gen']]
        for vid, specs, kol in gj_cases:
            vc = A.issue_vc(vid, [(S[r], a, S.x5c(l) if l else None) for r, a, l in specs], hold, serialization='general')
            self.ekle(vid, 'VC', vc['obj'], self.meta(
                'SD-JWT VC, JWS General JSON (RFC 9901 8.3), coklu ihracci imzasi: %s; ifsalar ilk korumasiz baslikta. '
                'SD-JWT VC -13\'te JSON serilestirme ISTEGE BAGLI (3.2), -19\'da ayrintilar kapsam disi (2.2).'
                % ' + '.join(a for _, a, _ in specs), 'sd-jwt-vc', 'sd-jwt-general', ['L4'], ek=['coklu-imza'],
                dayanak=Dg, kol=kol, senaryo='d', sdjwtvc=['-13'],
                girdiler=self.girdi([r for r, _, _ in specs], x5c=True),
                insa={'imzalar': [self.sig_rec(i, a, r, 'gecerli') for i, (r, a, _) in enumerate(specs)]}))
        a = A.issue_vc('VC10a', [(S['issuer/ES256'], 'ES256', S.x5c('issuer-ec@int-ec'))], hold)
        b = A.issue_vc('VC10b', [(S['issuer/ML-DSA-65'], 'ML-DSA-65', S.x5c('issuer-ml@int-ml'))], hold)
        self.ekle('VC10_ikili_ihrac', 'VC', {'credentials': [{'credential': a['obj']}, {'credential': b['obj']}]}, self.meta(
            'Ikili ihrac (senaryo b): ayni toplu yanitta (OID4VCI credentials dizisi bicimi) ayni talepli iki SD-JWT VC — '
            'ES256 (klasik zincir) ve ML-DSA-65 (PQ zincir); tuzlar farkli (baglantilanamazlik).', 'sd-jwt-vc',
            'oid4vci-toplu-yanit', ['L1', 'L3'], ek=['ikili-ihrac'],
            dayanak=Dc + [R['haip_x5c']], kol='tedavi-ML-DSA-65', senaryo='b', sdjwtvc=['-13', '-19'],
            girdiler=self.girdi(['issuer/ES256', 'issuer/ML-DSA-65'], x5c=True),
            insa={'kimlik_bilgileri': [{'sira': 0, 'alg': 'ES256', 'anahtar_rolu': 'issuer/ES256', 'insa': 'gecerli'},
                                       {'sira': 1, 'alg': 'ML-DSA-65', 'anahtar_rolu': 'issuer/ML-DSA-65', 'insa': 'gecerli'}]}))
        vc = A.issue_vc('VC11', [(S['issuer/ES256'], 'ES256', S.x5c('issuer-ec@int-ec'))], hold, typ='vc+sd-jwt')
        self.ekle('VC11_typ_vc+sd-jwt', 'VC', vc['obj'], self.meta(
            'VC01 benzeri; typ="vc+sd-jwt" (eski deger). -13 3.2.1: gecis doneminde her iki degerin kabulu ONERILIR; '
            '-19 yalniz dc+sd-jwt tanimlar.', 'sd-jwt-vc', 'sd-jwt-compact', ['L1'], ek=['typ-gecisi(-13)'],
            dayanak=[R['vc13_hdr'], R['vc19_hdr'], R['typ']], kol='klasik-taban', sdjwtvc=['-13'],
            girdiler=self.girdi(['issuer/ES256'], x5c=True),
            insa={'imzalar': [self.sig_rec(0, 'ES256', 'issuer/ES256', 'gecerli')], 'typ': 'vc+sd-jwt'}))
        payload, labeled = A.pid_payload('VC12', hold)
        none = b64u_encode(json_bytes({'alg': 'none', 'typ': 'dc+sd-jwt'})) + '.' + b64u_encode(json_bytes(payload)) + '.'
        self.ekle('VC12_alg_none', 'VC', none + '~' + ''.join(d + '~' for _, d in labeled), self.meta(
            'SD-JWT VC; ihracci JWT alg=none (imzasiz; bos imza). RFC 9901 9.1: ihracci JWT imzali OLMALI.', 'sd-jwt-vc',
            'sd-jwt-compact', ['L1'], ek=['alg-none'], dayanak=[R['sd_sign'], R['alg']], sdjwtvc=['-13', '-19'],
            girdiler={'simdi': SIMDI}, insa={'imzalar': [{'sira': 0, 'alg': 'none', 'insa': 'bos imza'}]}))

    # ------------------------------------------------------------ VP family
    def aile_VP(self):
        S = self.S
        D = [R['sd_kb'], R['sd_kbbind'], R['sd_ver'], R['haip_kb'], R['vp_aud']]
        cases = [
            ('VP01_ihracci_ES256_kb_ES256', 'issuer/ES256', 'ES256', 'issuer-ec@int-ec', 'holder/ES256', 'ES256', []),
            ('VP02_ihracci_MLDSA65_kb_ES256', 'issuer/ML-DSA-65', 'ML-DSA-65', 'issuer-ml@int-ml', 'holder/ES256', 'ES256',
             ['pq-ihracci-klasik-cihaz-anahtari']),
            ('VP03_ihracci_MLDSA65_kb_MLDSA65', 'issuer/ML-DSA-65', 'ML-DSA-65', 'issuer-ml@int-ml', 'holder/ML-DSA-65',
             'ML-DSA-65', []),
            ('VP04_ihracci_composite_kb_composite', 'issuer/ML-DSA-65-ES256', 'ML-DSA-65-ES256', None,
             'holder/ML-DSA-65-ES256', 'ML-DSA-65-ES256', []),
        ]
        for vid, irol, ialg, leaf, hrol, halg, ek in cases:
            vc = A.issue_vc(vid, [(S[irol], ialg, S.x5c(leaf) if leaf else None)], S[hrol].public_jwk(kid=False))
            vp = A.present(vc, S[hrol], halg)
            self.ekle(vid, 'VP', vp, self.meta(
                'SD-JWT+KB sunumu (compact): ihracci %s%s; KB-JWT %s (cnf.jwk=%s); acilan ifsalar: %s; aud="%s", nonce="%s".'
                % (ialg, ' (x5c)' if leaf else ' (kid)', halg, hrol, ', '.join(A.PRESENT_LABELS), A.KB_AUD_DCAPI, A.NONCE),
                'sd-jwt-vc+kb', 'sd-jwt-compact', ['L1', 'L3'], ek=['kb-jwt'] + ek, dayanak=D, kol=kol_of(ialg),
                senaryo='a' if ialg in COMPOSITE else None, sdjwtvc=['-13', '-19'],
                girdiler=self.girdi([irol], x5c=bool(leaf), kb_aud=A.KB_AUD_DCAPI, kb_nonce=A.NONCE),
                insa={'imzalar': [self.sig_rec(0, ialg, irol, 'gecerli')],
                      'kb_jwt': {'alg': halg, 'anahtar_rolu': hrol, 'insa': 'gecerli', 'iat': A.T0 + 3600}}))
        vc = A.issue_vc('VP05', [(S['issuer/ES256'], 'ES256', S.x5c('issuer-ec@int-ec')),
                                 (S['issuer/ML-DSA-65'], 'ML-DSA-65', S.x5c('issuer-ml@int-ml'))],
                        S['holder/ES256'].public_jwk(kid=False), serialization='general')
        DG = [R['sd_json'], R['sd_gen'], R['sd_kbbind'], R['vc13_pres']]
        G = self.girdi(['issuer/ES256', 'issuer/ML-DSA-65'], x5c=True, kb_aud=A.KB_AUD_DCAPI, kb_nonce=A.NONCE)
        vp5 = A.present(vc, S['holder/ES256'], 'ES256')
        sigs = [self.sig_rec(0, 'ES256', 'issuer/ES256', 'gecerli'), self.sig_rec(1, 'ML-DSA-65', 'issuer/ML-DSA-65', 'gecerli')]
        self.ekle('VP05_GJ_ES256_MLDSA65_kb', 'VP', vp5, self.meta(
            'SD-JWT+KB, General JSON (RFC 9901 8.3): ihracci ES256 + ML-DSA-65; disclosures ve kb_jwt ilk korumasiz '
            'baslikta; sd_hash, ILK imza (ES256) ile kurulan gecici compact bicim uzerinden (8.1\'in bu aracin okumasi).',
            'sd-jwt-vc+kb', 'sd-jwt-general', ['L4'], ek=['kb-jwt', 'coklu-imza'], dayanak=DG, kol='tedavi-ML-DSA-65',
            senaryo='d', sdjwtvc=['-13'], girdiler=G,
            insa={'imzalar': sigs, 'kb_jwt': {'alg': 'ES256', 'anahtar_rolu': 'holder/ES256', 'sd_hash_imza_sirasi': 0}}))
        vp6 = copy.deepcopy(vp5)
        vp6['signatures'] = vp6['signatures'][:1]
        self.ekle('VP06_GJ_pq_soyuldu_kb_gecerli', 'VP', vp6, self.meta(
            'VP05\'ten ML-DSA-65 ihracci imzasi soyuldu. KB-JWT sd_hash\'i yalniz ilk (ES256) imzayi kapsadigindan '
            'KB-JWT hala bu nesneyle tutarli (sd_hash baglamasi coklu imzayi korumuyor).', 'sd-jwt-vc+kb', 'sd-jwt-general',
            ['L4'], ek=['soyma', 'sd_hash-belirsizligi', 'kb-jwt'], dayanak=DG + [R['eccg']], kol='tedavi-ML-DSA-65',
            senaryo='d', sdjwtvc=['-13'], girdiler=G,
            insa={'kaynak_vektor': 'VP05', 'imzalar': sigs[:1],
                  'kb_jwt': {'alg': 'ES256', 'anahtar_rolu': 'holder/ES256', 'sd_hash_imza_sirasi': 0}}))
        vp7 = A.present(vc, S['holder/ES256'], 'ES256', sd_hash_sig_index=1)
        self.ekle('VP07_GJ_sd_hash_ikinci_imza', 'VP', vp7, self.meta(
            'VP05 ile ayni; ancak KB-JWT sd_hash\'i IKINCI (ML-DSA-65) imzayla kurulan gecici compact bicim uzerinden '
            '(8.1\'in alternatif okumasi).', 'sd-jwt-vc+kb', 'sd-jwt-general', ['L4'],
            ek=['sd_hash-belirsizligi', 'kb-jwt'], dayanak=DG, kol='tedavi-ML-DSA-65', senaryo='d', sdjwtvc=['-13'],
            girdiler=G, insa={'imzalar': sigs,
                              'kb_jwt': {'alg': 'ES256', 'anahtar_rolu': 'holder/ES256', 'sd_hash_imza_sirasi': 1}}))

    # ------------------------------------------------------------ TSL family
    def aile_TSL(self):
        S = self.S
        D = [R['tsl_jwt'], R['tsl_json'], R['tsl_bits'], R['haip_status'], R['haip_sig']]
        for vid, rol, alg, leaf in (('TSL01_ES256_x5c', 'status/ES256', 'ES256', 'status-ec@int-ec'),
                                    ('TSL02_MLDSA65_x5c', 'status/ML-DSA-65', 'ML-DSA-65', 'status-ml@int-ml'),
                                    ('TSL03_composite_kid', 'status/ML-DSA-65-ES256', 'ML-DSA-65-ES256', None)):
            obj = A.status_token(S[rol], alg, S.x5c(leaf) if leaf else None)
            self.ekle(vid, 'TSL', obj, self.meta(
                'Status List Token (JWT; typ=statuslist+jwt; bits=1, 16 girdi; idx 3 ve 12 = INVALID, idx 7 (PID) = VALID); '
                '%s; %s.' % (alg, 'x5c=[%s, ara CA]' % leaf if leaf else 'kid (composite X.509 kapsam disi)'),
                'status-list-token', 'compact', ['L1', 'L3'], ek=['durum-listesi'], dayanak=D, kol=kol_of(alg),
                senaryo='a' if alg in COMPOSITE else None, girdiler=self.girdi([rol], x5c=bool(leaf)),
                insa={'imzalar': [self.sig_rec(0, alg, rol, 'gecerli')], 'durumlar': {'3': 1, '7': 0, '12': 1}}))

    # ------------------------------------------------------------ DPOP family
    def aile_DPOP(self):
        S = self.S
        D = [R['dpop'], R['dpop_chk'], R['haip_dpop']]
        rows = []
        for i, alg in enumerate(('ES256', 'EdDSA', 'ML-DSA-44', 'ML-DSA-65', 'ML-DSA-87', 'ML-DSA-65-ES256', 'ML-DSA-65-Ed25519')):
            obj = A.dpop(S['dpop/' + alg], alg, 'DPOP%02d' % (i + 1), iat=SIMDI - 10)
            rows.append(('DPOP%02d_%s' % (i + 1, alg), alg, obj, 'asgari talepler (jti, htm, htu, iat)'))
        for j, alg in enumerate(('ML-DSA-65', 'ML-DSA-65-ES256')):
            obj = A.dpop(S['dpop/' + alg], alg, 'DPOP%02d' % (8 + j), iat=SIMDI - 10, with_ath=True, with_nonce=True)
            rows.append(('DPOP%02d_%s_ath_nonce' % (8 + j, alg), alg, obj, 'kaynak erisimi: + ath (erisim belirteci ozeti) + nonce'))
        for vid, alg, obj, note in rows:
            n = len(obj)
            self.ekle(vid, 'DPOP', obj, self.meta(
                'DPoP kaniti (typ=dpop+jwt; jwk=acik anahtar); %s; %s; %d B (nginx 1.31.6 varsayilan baslik degeri '
                'esigi 8.182 B, Node 24.15 16.348 B — P4).' % (alg, note, n), 'dpop', 'compact', ['L1'],
                ek=['boyut-esigi'], dayanak=D, kol=kol_of(alg), senaryo='a' if alg in COMPOSITE else None,
                girdiler={'simdi': SIMDI, 'htm': 'POST', 'htu': A.ISS + '/token', 'anahtar': 'jwk basligindan'},
                insa={'imzalar': [self.sig_rec(0, alg, 'dpop/' + alg, 'gecerli')], 'bayt': n,
                      'nginx_8182_asar': n > 8182, 'node_16348_asar': n > 16348}))
        k = S['dpop/ML-DSA-65']
        h = {'typ': 'dpop+jwt', 'jwk': k.private_jwk(kid=False)}
        c = {'jti': b64u_encode(hashlib.sha256(b'DPOP10').digest()[:16]), 'htm': 'POST', 'htu': A.ISS + '/token',
             'iat': SIMDI - 10}
        obj = jws.sign(json_bytes(c), jws.Signer(k, h, alg='ML-DSA-65'), 'compact', True)
        self.ekle('DPOP10_jwk_ozel_anahtar_iceriyor', 'DPOP', obj, self.meta(
            'DPoP kaniti; jwk basligi AKP OZEL anahtar uyesini (priv) iceriyor (RFC 9449 4.2: jwk ozel anahtar ICERMEMELI).',
            'dpop', 'compact', ['L1'], ek=['jwk-ozel-anahtar'], dayanak=D + [R['akp']], kol='tedavi-ML-DSA-65',
            girdiler={'simdi': SIMDI, 'htm': 'POST', 'htu': A.ISS + '/token', 'anahtar': 'jwk basligindan'},
            insa={'imzalar': [self.sig_rec(0, 'ML-DSA-65', 'dpop/ML-DSA-65', 'gecerli')], 'jwk_ozel_uye': 'priv'}))

    # ------------------------------------------------------------ CRIT family
    def aile_CRIT(self):
        S = self.S
        rol, alg, leaf = 'issuer/ML-DSA-65', 'ML-DSA-65', 'issuer-ml@int-ml'
        D = [R['crit'], R['vc19_hdr']]
        G = self.girdi([rol], x5c=True)
        beklenti = {'gerekli_alg': ['ML-DSA-65'], 'sunset': A.T0 + 5 * 365 * 86400}
        cases = [
            ('CRIT01_bilinmeyen_parametre', {'typ': 'dc+sd-jwt', 'x5c': S.x5c(leaf), 'crit': ['x-pq-beklenti'],
                                             'x-pq-beklenti': beklenti},
             'crit=["x-pq-beklenti"] ve parametre korumali baslikta (M-f tasiyicisi adayi: taniyamayan dogrulayici '
             'reddetmek ZORUNDA — fail-closed dagitim).', ['crit', 'M-f-tasiyici-adayi']),
            ('CRIT03_kayitli_ad', {'typ': 'dc+sd-jwt', 'x5c': S.x5c(leaf), 'crit': ['alg']},
             'crit=["alg"] (RFC 7515 4.1.11: bu belgede tanimli parametreler crit\'te listelenmemeli).', ['crit']),
            ('CRIT04_bos_dizi', {'typ': 'dc+sd-jwt', 'x5c': S.x5c(leaf), 'crit': []},
             'crit=[] (bos liste kullanilmamali).', ['crit']),
            ('CRIT05_listelenen_parametre_yok', {'typ': 'dc+sd-jwt', 'x5c': S.x5c(leaf), 'crit': ['x-yok']},
             'crit=["x-yok"] ama x-yok baslikta yok.', ['crit']),
        ]
        for vid, prot, acik, ek in cases:
            obj, _, _ = self._vc_compact(vid, S[rol], alg, prot)
            self.ekle(vid, 'CRIT', obj, self.meta(
                'SD-JWT VC (compact; ML-DSA-65; x5c tam-PQ); ' + acik, 'sd-jwt-vc', 'sd-jwt-compact', ['L1'], ek=ek,
                dayanak=D, kol='tedavi-ML-DSA-65', sdjwtvc=['-13', '-19'], girdiler=G,
                insa={'imzalar': [self.sig_rec(0, alg, rol, 'gecerli')], 'crit': prot['crit']}))
        fl = self._vc_flattened('CRIT02', S[rol], alg, {'typ': 'dc+sd-jwt', 'x5c': S.x5c(leaf)},
                                {'crit': ['x-pq-beklenti'], 'x-pq-beklenti': beklenti})
        self.ekle('CRIT02_korumasiz_crit', 'CRIT', fl, self.meta(
            'SD-JWT VC flattened JSON; crit ve x-pq-beklenti KORUMASIZ baslikta (RFC 7515 4.1.11: crit korumali olmali).',
            'sd-jwt-vc', 'sd-jwt-flattened', ['L1'], ek=['crit', 'M-f-tasiyici-adayi'], dayanak=D + [R['flat'], R['sd_flat']],
            kol='tedavi-ML-DSA-65', sdjwtvc=['-13'], girdiler=G,
            insa={'imzalar': [self.sig_rec(0, alg, rol, 'gecerli')], 'crit': ['x-pq-beklenti'], 'crit_korumali': False}))

    # ------------------------------------------------------------ key files and manifest
    def yaz_anahtarlar(self):
        S = self.S
        os.makedirs(os.path.join(self.kdir, 'ozel'), exist_ok=True)
        os.makedirs(os.path.join(self.kdir, 'pki'), exist_ok=True)
        roller = {}
        pub = []
        for rol, tur in ROLLER.items():
            k = S[rol]
            fn = 'ozel/' + rol.replace('/', '__') + '.json'
            with open(os.path.join(self.kdir, fn), 'w', encoding='utf-8') as f:
                json.dump(k.private_jwk(), f, indent=1)
                f.write('\n')
            roller[rol] = {'tur': tur, 'kid': k.kid, 'turetme_etiketi': 'v1/' + rol, 'ozel_jwk': fn}
            if not rol.startswith('ca/'):
                pub.append(k.public_jwk())
        with open(os.path.join(self.kdir, 'acik-jwks.json'), 'w', encoding='utf-8') as f:
            json.dump({'keys': pub}, f, indent=1)
            f.write('\n')
        ck = S['issuer/ML-DSA-65-ES256']
        tp = ck.trad.public_only()
        tp.kid = tp.thumbprint()
        mp = MLDSAKey('ML-DSA-65', pub=ck.ml.pub)
        mp.kid = mp.thumbprint()
        with open(os.path.join(self.kdir, 'bilesen-yeniden-kullanim-jwks.json'), 'w', encoding='utf-8') as f:
            json.dump({'not': 'YALNIZ CMP12/CMP13 icin: issuer/ML-DSA-65-ES256 bilesen anahtarlari bagimsiz anahtar olarak '
                              '(anahtar yeniden kullanimi senaryosu; -04 6.2 bunu yasaklar).',
                       'keys': [tp.public_jwk(), mp.public_jwk()]}, f, indent=1)
            f.write('\n')
        certs = {}
        for name, c in S.certs.items():
            with open(os.path.join(self.kdir, 'pki', name + '.pem'), 'wb') as f:
                f.write(c.pem)
            with open(os.path.join(self.kdir, 'pki', name + '.der'), 'wb') as f:
                f.write(c.der)
            from pqjose.x509 import cert_info
            info = cert_info(c.der)
            certs[name] = {k: info[k] for k in ('subject', 'issuer', 'serial', 'imza_alg', 'imza_sinif', 'anahtar_sinif',
                                                 'der_bayt', 'sha256', 'x509_hash', 'kendinden_imzali')}
            certs[name]['anahtar_rolu'] = next((r for r, kk in S.k.items() if kk is c.key), None)
        with open(os.path.join(self.kdir, 'pki', 'guven-capalari.pem'), 'wb') as f:
            f.write(S.certs['root-ec'].pem + S.certs['root-ml'].pem)
        with open(os.path.join(self.kdir, 'roller.json'), 'w', encoding='utf-8') as f:
            json.dump({'turetme': 'pqjose.keys.derive_key(tur, etiket): HKDF-SHA256(IKM="PQ-OID4VC Adim 9b test '
                                  'vektorleri v1", salt="pqjose/derive/v1", info=etiket|tur)',
                       'gecerlilik': [pki.NOT_BEFORE, pki.NOT_AFTER], 'roller': roller, 'sertifikalar': certs},
                      f, indent=1, ensure_ascii=False)
            f.write('\n')
        self._sha256sums(self.kdir)

    @staticmethod
    def _sha256sums(d):
        lines = []
        for root, _, files in os.walk(d):
            for fn in sorted(files):
                if fn == 'SHA256SUMS':
                    continue
                p = os.path.join(root, fn)
                rel = os.path.relpath(p, d).replace(os.sep, '/')
                lines.append((rel, hashlib.sha256(open(p, 'rb').read()).hexdigest()))
        with open(os.path.join(d, 'SHA256SUMS'), 'w', encoding='utf-8') as f:
            for rel, h in sorted(lines):
                f.write('%s  %s\n' % (h, rel))

    def yaz_manifest(self, surumler):
        m = {'surum': SURUM, 'vektor_sayisi': len(self.items), 'simdi': SIMDI, 'T0': A.T0,
             'uyari': 'Bu manifest vektorlerin NE OLDUGUNU tanimlar; beklenen karar (oracle) ICERMEZ. '
                      "'insa' alanlari uretim gercekleridir (hangi imza nasil kuruldu), kabul/red hukmu degildir.",
             'anahtar_dizini': 'anahtarlar/v1', 'uretim_ortami': surumler,
             'aileler': sorted({i['aile'] for i in self.items}), 'vektorler': self.items}
        with open(os.path.join(self.vdir, 'MANIFEST.json'), 'w', encoding='utf-8') as f:
            json.dump(m, f, indent=1, ensure_ascii=False)
            f.write('\n')
        cols = ['id', 'aile', 'dosya', 'sha256', 'bayt', 'artefakt', 'serilestirme', 'kol', 'senaryo', 'sdjwtvc_surum',
                'basamak', 'plan_bayraklari', 'ek_etiketler', 'dayanak', 'b_pilot_esi', 'dcapi_protokol', 'algler', 'aciklama']
        with open(os.path.join(self.vdir, 'MANIFEST.csv'), 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(cols)
            for i in self.items:
                sigs = i['insa'].get('imzalar') or i['insa'].get('kimlik_bilgileri') or []
                w.writerow([i['id'], i['aile'], i['dosya'], i['sha256'], i['bayt'], i['artefakt'], i['serilestirme'],
                            i['kol'] or '', i['senaryo'] or '', ';'.join(i['sdjwtvc_surum'] or []),
                            ';'.join(i['sinanan']['basamak']), ';'.join(i['sinanan']['plan_bayraklari']),
                            ';'.join(i['sinanan']['ek_etiketler']), ';'.join(i['dayanak']), i['b_pilot_esi'] or '',
                            i['dcapi_protokol'] or '', ';'.join(s.get('alg', '') for s in sigs), i['aciklama']])
        self._sha256sums(self.vdir)

    def uret(self, surumler):
        for fn in (self.aile_T, self.aile_UNK, self.aile_CMP, self.aile_X5C, self.aile_REQ, self.aile_VC, self.aile_VP,
                   self.aile_TSL, self.aile_DPOP, self.aile_CRIT):
            fn()
        self.yaz_anahtarlar()
        self.yaz_manifest(surumler)
        return self.items
