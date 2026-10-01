"""Test vektoru seti v1.2 = v1.1 (100 vektor, BAYT-AYNI) + ON-KAYIT §6.5 bataryasinin eksikleri.

Kaynak: yurutucu (gozden-gecirme/adim-09b.md §8 "Ek 2: Batarya esleme denetimi"), ON-KAYIT-TASLAK.md §6.5,
§2B m.8 / §2C m.4 (MR4), §4.20 (MR1-MR3), §2D (Degisiklik 4), §2E (Degisiklik 5).

Eklenenler:
  1. MR4 (imza sirasi permutasyonu): T1*/T2* ters; T4*/T6/T7* 'ek-once'|'kayitsiz-once' ve 'ters'; VC07/VC08/VC09
     ters (RFC 9901 §8.3: disclosures YENI ilk korumasiz baslikta); REQ04 ters. VP05 ters: MR4 DISI, tanimlayici
     (KB sd_hash'in bagladigi imza degisir). Kimlik: <id>-SIRA-<kisa-ad>.
  2. K10 (alg-anahtar uyusmazligi), her kolda iki yon; imza baslik alg'iyla DEGIL gercek anahtarin kendi
     algoritmasiyla uretilmis gecerli imzadir.
  3. K5: T7K/T7P/T7C_plus_kayitsiz = T1* + gercekten kayitsiz 'X-KAYITSIZ-1' etiketli ucuncu imza
     (128 B rastgele, HKDF'den belirlenimci).
  4. V+ / V-: tek imzali compact JWS (ES256, EdDSA, ML-DSA-65; composite icin CMP00/CMP01 yeniden kullanilir).
  5. Yeni her kontrol-EdDSA vektorunun '-ED25519' esi (EdDSA etiketi icermeyen K10K(b) haric; bayt-ayni olurdu).
Donmus v1/ ve v1.1/ yalniz OKUNUR; v1.1 once gecici dizinde bastan uretilip donmus v1.1 ile karsilastirilir.
Yeni anahtar YOK: anahtarlar/v1. Oracle karari YAZILMAZ.
Kullanim: python -m uretec.v12 <cikti_kok> [<donmus_kok>]
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
from pqjose.keys import derive_bytes
from pqjose.params import alg_class
from pqjose.util import b64u_decode, b64u_encode, json_bytes

from . import __version__
from . import v11
from .vektorler import B_PAYLOAD, JWT_PAYLOAD, R, SIMDI, Uretici

SURUM = 'v1.2'
KAYITSIZ = 'X-KAYITSIZ-1'
KAYITSIZ_BAYT = 128
ARM_X = {'K': 'EdDSA', 'P': 'ML-DSA-65', 'C': 'ML-DSA-65-ES256'}
ARM_KOL = {'K': 'kontrol-EdDSA', 'P': 'tedavi-ML-DSA-65', 'C': 'tedavi-composite'}
ROLES = {'ES256': 'issuer/ES256', 'EdDSA': 'issuer/EdDSA', 'Ed25519': 'issuer/EdDSA',
         'ML-DSA-65': 'issuer/ML-DSA-65', 'ML-DSA-65-ES256': 'issuer/ML-DSA-65-ES256'}
MR4_ETIKET = 'MR4(imza-sirasi-permutasyonu)'
SD_UYELER = ('disclosures', 'kb_jwt')
META_DOSYALAR = ('MANIFEST.json', 'MANIFEST.csv', 'SHA256SUMS')


def _sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def flip(b, i, bit=0):
    x = bytearray(b)
    x[i] ^= (1 << bit)
    return bytes(x)


# ------------------------------------------------------------------ MR4 permutasyonu
def permute(obj, order):
    """General JSON (JWS / SD-JWT) imza sirasi permutasyonu. order: yeni siradaki ozgun indeksler.
    RFC 9901 §8.3: 'disclosures' ve 'kb_jwt' YALNIZ (yeni) ilk korumasiz baslikta bulunur."""
    sigs = obj['signatures']
    tasinan = {}
    for s in sigs:
        for k in SD_UYELER:
            if k in (s.get('header') or {}):
                tasinan[k] = s['header'][k]
    yeni = []
    for j, oi in enumerate(order):
        s = sigs[oi]
        e = {}
        if 'protected' in s:
            e['protected'] = s['protected']
        h = {k: v for k, v in (s.get('header') or {}).items() if k not in SD_UYELER}
        if j == 0 and tasinan:
            h = dict(tasinan, **h)
        if h:
            e['header'] = h
        e['signature'] = s['signature']
        yeni.append(e)
    return {'payload': obj['payload'], 'signatures': yeni}


def mr4_denetimi(kaynak, perm, order):
    """Permutasyon yalniz sirayi degistirmeli: yuk, her (protected, signature) cifti ve SD-JWT ifsalari korunur."""
    if perm['payload'] != kaynak['payload'] or len(perm['signatures']) != len(kaynak['signatures']):
        raise RuntimeError('MR4: yuk/imza sayisi degisti')
    if sorted(order) != list(range(len(order))):
        raise RuntimeError('MR4: gecersiz permutasyon')
    for j, oi in enumerate(order):
        a, b = kaynak['signatures'][oi], perm['signatures'][j]
        if a.get('protected') != b.get('protected') or a['signature'] != b['signature']:
            raise RuntimeError('MR4: imza %d icerigi degisti' % oi)
        ha = {k: v for k, v in (a.get('header') or {}).items() if k not in SD_UYELER}
        hb = {k: v for k, v in (b.get('header') or {}).items() if k not in SD_UYELER}
        if ha != hb:
            raise RuntimeError('MR4: korumasiz baslik (ifsa disi) degisti')
    tasinan = {}
    for s in kaynak['signatures']:
        for k in SD_UYELER:
            if k in (s.get('header') or {}):
                tasinan[k] = s['header'][k]
    h0 = perm['signatures'][0].get('header') or {}
    if any(h0.get(k) != v for k, v in tasinan.items()):
        raise RuntimeError('MR4: ifsalar/kb_jwt yeni ilk baslikta degil')
    if any(k in (s.get('header') or {}) for s in perm['signatures'][1:] for k in SD_UYELER):
        raise RuntimeError('MR4: ifsalar/kb_jwt ilk baslik disinda')
    return bool(tasinan)


# ------------------------------------------------------------------ compact yardimcilari
def compact(header, payload, sig):
    return b64u_encode(json_bytes(header)) + '.' + b64u_encode(payload) + '.' + b64u_encode(sig)


def tbs(header, payload):
    return (b64u_encode(json_bytes(header)) + '.' + b64u_encode(payload)).encode('ascii')


class V12:
    def __init__(self, u: Uretici, esler: dict, v11_items: list, out: str):
        self.u = u
        self.S = u.S
        self.esler = esler                      # v1.1 Ed25519 esleri (v1 id -> nesne)
        self.v11 = {i['id']: i for i in v11_items}
        self.out = out
        self.yeni = []                          # (nesne, girdi)
        self.nesne = {}                          # id -> nesne (v1.1 + v1.2)
        for vid, o in u.objs.items():
            self.nesne[vid] = o
        for vid, o in esler.items():
            self.nesne[vid + '-ED25519'] = o

    # -------------------------------------------------------- yazma
    def yaz(self, aile, vid, obj):
        if isinstance(obj, str):
            ext = 'sdjwt' if '~' in obj else 'jws'
            data = obj.encode('utf-8')
        else:
            ext = 'json'
            data = (json.dumps(obj, indent=1, ensure_ascii=False) + '\n').encode('utf-8')
        rel = '%s/%s.%s' % (aile, vid, ext)
        p = os.path.join(self.out, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'wb') as f:
            f.write(data)
        return rel, data

    def ekle(self, girdi, obj, data, rel):
        girdi['dosya'] = rel
        girdi['sha256'] = hashlib.sha256(data).hexdigest()
        girdi['bayt'] = len(data)
        sirali = {k: girdi[k] for k in ('id', 'dosya', 'sha256', 'bayt', 'aile')}   # v1 girdileriyle ayni anahtar sirasi
        sirali.update({k: v for k, v in girdi.items() if k not in sirali})
        self.yeni.append(sirali)
        self.nesne[sirali['id']] = obj
        return sirali

    # -------------------------------------------------------- Ed25519 esi (A9 yedek kurali)
    def ed_esi(self, girdi, es_obj):
        """girdi: EdDSA etiketli yeni vektorun manifest girdisi; es_obj: Ed25519 etiketli esi."""
        degisen = v11.koruma_denetimi(self.nesne[girdi['id']], es_obj)
        e = copy.deepcopy(girdi)
        e['id'] = girdi['id'] + '-ED25519'
        e['kol'] = 'kontrol-Ed25519'
        e['aciklama'] = ('%s vektorunun Ed25519 etiketli esi (A9 yedek kurali): kontrol imzasinin alg etiketi "EdDSA" '
                         'yerine RFC 9864 tam belirtilmis "Ed25519"; ayni anahtar, ayni yuk, ayni yapi; yalniz bu baslik '
                         've ona bagli imza farkli. Ozgun aciklama: %s' % (girdi['id'], girdi['aciklama']))
        e['dayanak'] = [d for d in girdi['dayanak'] if not d.startswith('RFC9864')] + v11.ED_DAYANAK
        ins = e['insa']
        for s in ins.get('imzalar', []):
            if s.get('alg') == 'EdDSA':
                s['alg'] = 'Ed25519'
        ins['etiket_esi'] = girdi['id']
        ins['etiket_degisikligi'] = {'eski': 'EdDSA', 'yeni': 'Ed25519', 'yeniden_hesaplanan_imza_sirasi': degisen}
        if 'k10' in ins and ins['k10'].get('baslik_alg') == 'EdDSA':
            ins['k10']['baslik_alg'] = 'Ed25519'
        if 'mr4' in ins:
            ins['mr4']['kaynak_vektor'] = ins['mr4']['kaynak_vektor'] + '-ED25519'
        g = e['dogrulama_girdileri']
        if 'alg_kid' in g and 'EdDSA' in g['alg_kid']:
            g['alg_kid']['Ed25519'] = g['alg_kid']['EdDSA']
        e['sinanan']['ek_etiketler'] = e['sinanan']['ek_etiketler'] + ['ed25519-etiketi(RFC 9864; A9 yedek kurali)']
        rel, data = self.yaz(girdi['aile'], e['id'], es_obj)
        self.ekle(e, es_obj, data, rel)
        return e

    # -------------------------------------------------------- 1. MR4
    def mr4(self, kaynak_id, order, kisa, kaynak_girdi=None, es_kaynak_obj=None, tanimlayici=False):
        src = kaynak_girdi or self.v11[kaynak_id]
        obj = self.nesne[kaynak_id]
        perm = permute(obj, order)
        tasindi = mr4_denetimi(obj, perm, order)
        vid = '%s-SIRA-%s' % (kaynak_id, kisa)
        e = copy.deepcopy(src)
        e['id'] = vid
        imz = src['insa'].get('imzalar', [])
        e['insa']['imzalar'] = [dict(imz[oi], sira=j, ozgun_sira=oi) for j, oi in enumerate(order)]
        e['insa']['mr4'] = {'kaynak_vektor': kaynak_id, 'yeni_siradaki_ozgun_indeksler': order, 'permutasyon': kisa,
                            'ifsalar_yeni_ilk_basliga_tasindi': tasindi}
        ifsa_notu = (' SD-JWT: disclosures%s YENI ilk korumasiz baslikta (RFC 9901 §8.3); ifsa listesi ayni.' %
                     (' ve kb_jwt' if 'kb_jwt' in json.dumps(perm) else '')) if tasindi else ''
        algler = [imz[oi].get('alg') for oi in order]
        if tanimlayici:
            e['insa']['kb_jwt'] = dict(src['insa'].get('kb_jwt', {}))
            e['insa']['kb_jwt']['sd_hash_imza_sirasi'] = order.index(src['insa'].get('kb_jwt', {}).get('sd_hash_imza_sirasi', 0))
            e['insa']['kb_jwt']['not'] = ('KB-JWT baytlari kaynakla ayni; sd_hash kaynakta ilk imza uzerinden hesaplanmisti, '
                                          'permutasyondan sonra o imza %d. sirada.' % e['insa']['kb_jwt']['sd_hash_imza_sirasi'])
            e['aciklama'] = ('TANIMLAYICI (MR4 kapsami DISI): %s vektorunun imza sirasi %s (yeni sira = ozgun %s; algler %s). '
                             'Imzalar ve yuk bayt-ayni; disclosures ve kb_jwt yeni ilk basliga tasindi (RFC 9901 §8.3). '
                             'KB-JWT degismedigi icin sd_hash artik ILK imzayi degil %d. siradaki imzayi baglar: '
                             'permutasyon sd_hash\'in bagladigi imzayi degistirir (RFC 9901 §8.1 belirsizligi; ÖK §2D m.4). '
                             'Ozgun aciklama: %s' % (kaynak_id, kisa, order, algler,
                                                      e['insa']['kb_jwt']['sd_hash_imza_sirasi'], src['aciklama']))
            e['sinanan']['ek_etiketler'] = e['sinanan']['ek_etiketler'] + ['MR4-kapsam-disi(tanimlayici): sd_hash-baglamasi-degisir']
        else:
            e['aciklama'] = ('MR4 esi (ÖK §2B m.8, §2C m.4): %s vektorunun imza sirasi "%s" (yeni sira = ozgun indeksler %s; '
                             'algler %s). Her imzanin korumali basligi ve imza baytlari ile yuk bayt-ayni; yalniz signatures '
                             'dizisindeki sira degisti.%s Ozgun aciklama: %s' % (kaynak_id, kisa, order, algler, ifsa_notu,
                                                                                  src['aciklama']))
            e['sinanan']['ek_etiketler'] = e['sinanan']['ek_etiketler'] + [MR4_ETIKET]
        if tasindi and 'RFC9901 §8.3' not in e['dayanak']:
            e['dayanak'] = e['dayanak'] + ['RFC9901 §8.3']
        for k in ('etiket_degisikligi', 'v1_esi', 'etiket_esi'):
            e['insa'].pop(k, None)
        rel, data = self.yaz(src['aile'], vid, perm)
        self.ekle(e, perm, data, rel)
        if es_kaynak_obj is not None:
            self.ed_esi(e, permute(es_kaynak_obj, order))
        return e

    def aile_mr4(self):
        E = self.esler
        for a in 'KPC':
            base = 'T1%s_both_valid' % a
            self.mr4(base, [1, 0], 'ters', es_kaynak_obj=E.get(base) if a == 'K' else None)
        for a in 'KPC':
            base = 'T2%s_second_tampered' % a
            self.mr4(base, [1, 0], 'ters', es_kaynak_obj=E.get(base) if a == 'K' else None)
        for base in ('T4K_plus_ML-DSA-65', 'T4P_plus_ML-DSA-65-ES256', 'T4C_plus_ML-DSA-65', 'T6_plus_composite'):
            es = E.get(base)
            self.mr4(base, [2, 0, 1], 'ek-once', es_kaynak_obj=es)
            self.mr4(base, [2, 1, 0], 'ters', es_kaynak_obj=es)
        for base in ('VC07_GJ_ES256_MLDSA65', 'VC08_GJ_ES256_composite', 'VC09_GJ_ES256_EdDSA'):
            self.mr4(base, [1, 0], 'ters', es_kaynak_obj=E.get(base))
        self.mr4('REQ04_coklu_imzali', [1, 0], 'ters')
        self.mr4('VP05_GJ_ES256_MLDSA65_kb', [1, 0], 'ters', tanimlayici=True)

    # -------------------------------------------------------- 3. K5: T7*
    def aile_T7(self):
        for a in 'KPC':
            t1 = 'T1%s_both_valid' % a
            src = self.v11[t1]
            ucuncu = {'protected': b64u_encode(json_bytes({'alg': KAYITSIZ})),
                      'signature': b64u_encode(derive_bytes('v1.2/T7%s/kayitsiz-imza' % a, KAYITSIZ_BAYT))}
            obj = copy.deepcopy(self.nesne[t1])
            obj['signatures'].append(ucuncu)
            vid = 'T7%s_plus_kayitsiz' % a
            x = ARM_X[a]
            g = copy.deepcopy(src['dogrulama_girdileri'])
            g['not'] = '%s icin anahtar yoktur (kayitsiz etiket; imza baytlari rastgele)' % KAYITSIZ
            e = self.u.meta(
                'General JSON JWS; %s ile ayni iki gecerli imza (ES256 + %s) + GERCEKTEN KAYITSIZ alg etiketli ("%s") '
                'ucuncu imza; ucuncu imzanin baytlari rastgele ve belirlenimci (HKDF "v1.2/T7%s/kayitsiz-imza", %d B), '
                'kriptografik anlami yok. ÖK §6.5 K5 birincil vektoru.' % (t1, x, KAYITSIZ, a, KAYITSIZ_BAYT),
                'jws-cekirdek', 'general', ['L1', 'L4'], plan=['bilinmeyen-composite-alg'],
                ek=['K5', 'kayitsiz-alg', 'ek-imza'], dayanak=[R['gen'], R['json'], R['dogr'], R['alg'], R['bcp']],
                kol=ARM_KOL[a], senaryo='d (JWS duzeyi)',
                b_pilot='T4_plus_unknown_MLDSA65 (B: rastgele bayt; burada etiket de kayitsiz)', girdiler=g,
                insa={'kaynak_vektor': t1,
                      'imzalar': copy.deepcopy(src['insa']['imzalar']) +
                      [{'sira': 2, 'alg': KAYITSIZ, 'alg_sinifi': alg_class(KAYITSIZ), 'anahtar_rolu': None, 'kid': None,
                        'insa': 'rastgele belirlenimci %d B (HKDF); kriptografik anlami yok' % KAYITSIZ_BAYT}]})
            e['id'] = vid
            e['aile'] = 'T'
            rel, data = self.yaz('T', vid, obj)
            self.ekle(e, obj, data, rel)
            es_obj = None
            if a == 'K':
                es_obj = copy.deepcopy(self.esler[t1])
                es_obj['signatures'].append(ucuncu)
                self.ed_esi(e, es_obj)
            self.mr4(vid, [2, 0, 1], 'kayitsiz-once', kaynak_girdi=e, es_kaynak_obj=es_obj)
            self.mr4(vid, [2, 1, 0], 'ters', kaynak_girdi=e, es_kaynak_obj=es_obj)

    # -------------------------------------------------------- 2. K10
    def aile_K10(self):
        S = self.S
        # (kol, baslik alg, gercek anahtar rolu, imzada kullanilan gercek alg)
        cases = [
            ('K', 'EdDSA', 'issuer/ES256', 'ES256'),
            ('K', 'ES256', 'issuer/EdDSA', 'EdDSA'),
            ('P', 'ML-DSA-65', 'issuer/ES256', 'ES256'),
            ('P', 'ES256', 'issuer/ML-DSA-65', 'ML-DSA-65'),
            ('C', 'ML-DSA-65-ES256', 'issuer/ML-DSA-65', 'ML-DSA-65'),
            ('C', 'ML-DSA-65', 'issuer/ML-DSA-65-ES256', 'ML-DSA-65-ES256'),
        ]
        tur = {'issuer/ES256': 'ES256', 'issuer/EdDSA': 'Ed25519', 'issuer/ML-DSA-65': 'ML-DSA-65',
               'issuer/ML-DSA-65-ES256': 'ML-DSA-65-ES256'}
        for a, halg, rol, galg in cases:
            key = S[rol]
            h = {'alg': halg, 'kid': key.kid}
            sig = algs.sign(galg, key, tbs(h, B_PAYLOAD), True)
            if not algs.verify(galg, key.public_only(), tbs(h, B_PAYLOAD), sig) or algs.key_supports(key, halg):
                raise RuntimeError('K10 insasi hatali')
            obj = compact(h, B_PAYLOAD, sig)
            vid = 'K10%s_alg-%s_anahtar-%s' % (a, halg, tur[rol])
            dy = [R['bcp'], 'RFC8725 §3.1', R['alg']]
            if 'ML-DSA' in halg + galg:
                dy += [R['akp'], 'RFC9964 §7.4']
            if 'ES256' in (halg, galg) or rol == 'issuer/ES256':
                dy += [R['es256']]
            if 'EdDSA' in (halg, galg):
                dy += [R['eddsa']]
            if halg.count('-') >= 3 or galg.count('-') >= 3:
                dy += [R['c_alg']]
            g = {'jwks': 'anahtarlar/v1/acik-jwks.json', 'kid': [key.kid], 'jwk': key.public_jwk(),
                 'anahtar_yolu': 'hedefin belgeli API\'si (JWK/JWKS ya da dogrudan anahtar); ÖK §2D m.1 (D-S1)',
                 'simdi': SIMDI}
            e = self.u.meta(
                'Compact JWS (ÖK §6.5 K10, alg-anahtar uyusmazligi): baslikta alg="%s", dogrulama anahtari %s (%s JWK, '
                'kid ile). Imza, baslik alg\'iyla DEGIL gercek anahtarin kendi algoritmasiyla (%s) bu imzalama girdisi '
                'uzerinde uretilmis GECERLI bir imzadir (%d B).' % (halg, rol, tur[rol], galg, len(sig)),
                'jws-cekirdek', 'compact', ['L2', 'L3'], ek=['K10', 'alg-anahtar-uyusmazligi'], dayanak=dy,
                kol=ARM_KOL[a], girdiler=g,
                insa={'imzalar': [{'sira': 0, 'alg': halg, 'alg_sinifi': alg_class(halg), 'anahtar_rolu': rol,
                                   'kid': key.kid, 'insa': 'gercek anahtarin algoritmasiyla (%s) gecerli imza; baslik alg '
                                                           'anahtarla uyusmuyor' % galg}],
                      'k10': {'baslik_alg': halg, 'anahtar_rolu': rol, 'anahtar_turu': tur[rol], 'imza_uretim_alg': galg,
                              'imza_bayt': len(sig)}})
            e['id'] = vid
            e['aile'] = 'K10'
            rel, data = self.yaz('K10', vid, obj)
            self.ekle(e, obj, data, rel)
            if halg == 'EdDSA':
                h2 = {'alg': 'Ed25519', 'kid': key.kid}
                sig2 = algs.sign(galg, key, tbs(h2, B_PAYLOAD), True)
                self.ed_esi(e, compact(h2, B_PAYLOAD, sig2))

    # -------------------------------------------------------- 4. V+ / V-
    def aile_V(self):
        S = self.S
        for alg in ('ES256', 'EdDSA', 'ML-DSA-65'):
            rol = ROLES[alg]
            key = S[rol]
            kol = 'ortak' if alg == 'ES256' else ARM_KOL['K' if alg == 'EdDSA' else 'P']
            dy = [R['dogr'], R['alg'], {'ES256': R['es256'], 'EdDSA': R['eddsa'], 'ML-DSA-65': R['mldsa']}[alg]]
            g = {'jwks': 'anahtarlar/v1/acik-jwks.json', 'kid': [key.kid], 'jwk': key.public_jwk(),
                 'anahtar_yolu': 'hedefin belgeli API\'si (JWK/JWKS ya da dogrudan anahtar); ÖK §2D m.1', 'simdi': SIMDI}

            def yap(halg):
                h = {'alg': halg, 'kid': key.kid, 'typ': 'JWT'}
                s = algs.sign(halg, key, tbs(h, JWT_PAYLOAD), True)
                return h, s
            h, s = yap(alg)
            not_ = ' (ÖK §4.15: tek gecerli klasik imza)' if alg == 'ES256' else ''
            for isaret, bozuk in (('PLUS', False), ('MINUS', True)):
                sig = flip(s, len(s) // 2) if bozuk else s
                obj = compact(h, JWT_PAYLOAD, sig)
                vid = 'V%s_%s' % (isaret, alg)
                e = self.u.meta(
                    'V%s adaptor gecerlilik kontrolu (ÖK §6.5 V+/V-, §4.15): tek imzali compact JWS, %s, kid ile%s; %s.'
                    % ('+' if not bozuk else '-', alg, not_, 'imzanin orta baytinda bit cevrildi' if bozuk else 'imza gecerli'),
                    'jws-cekirdek', 'compact', [], ek=['V+' if not bozuk else 'V-', 'adaptor-gecerlilik-kontrolu'],
                    dayanak=dy, kol=kol, girdiler=g,
                    insa={'imzalar': [{'sira': 0, 'alg': alg, 'alg_sinifi': alg_class(alg), 'anahtar_rolu': rol,
                                       'kid': key.kid, 'insa': ('bozuk: bayt %d, bit 0 cevrildi' % (len(s) // 2)) if bozuk
                                       else 'gecerli'}]})
                e['id'] = vid
                e['aile'] = 'V'
                rel, data = self.yaz('V', vid, obj)
                self.ekle(e, obj, data, rel)
                if alg == 'EdDSA':
                    h2, s2 = yap('Ed25519')
                    self.ed_esi(e, compact(h2, JWT_PAYLOAD, flip(s2, len(s2) // 2) if bozuk else s2))

    def uret(self):
        self.aile_mr4()
        self.aile_T7()
        self.aile_K10()
        self.aile_V()
        return self.yeni


def uret_v12(cikti_kok, donmus_kok, surumler):
    out = os.path.join(cikti_kok, 'vektorler', SURUM)
    with tempfile.TemporaryDirectory(prefix='pq-v12-') as td:
        # (i) v1.1'i (ve onun icinde v1'i) bastan uret; donmus v1.1 ile karsilastir
        v11.uret_v11(td, donmus_kok, surumler)
        for fn in ('SHA256SUMS', 'MANIFEST.json'):
            a = open(os.path.join(donmus_kok, 'vektorler', 'v1.1', fn), 'rb').read()
            b = open(os.path.join(td, 'vektorler', 'v1.1', fn), 'rb').read()
            if a != b:
                raise RuntimeError('v1.1 yeniden uretimi donmus v1.1 ile ayni degil (%s) — v1.2 uretilmedi' % fn)
        v11_man = json.load(open(os.path.join(td, 'vektorler', 'v1.1', 'MANIFEST.json'), encoding='utf-8'))
        # (ii) bellekte v1 nesneleri + v1.1 esleri (belirlenimci; ayni nesneler)
        with tempfile.TemporaryDirectory(prefix='pq-v12-v1-') as td2:
            u = Uretici(td2)
            u.uret(surumler)
        esler = v11.es_uret(u)
        # (iii) v1.1 dosyalarini kopyala, yenileri ekle
        if os.path.isdir(out):
            shutil.rmtree(out)
        src = os.path.join(td, 'vektorler', 'v1.1')
        shutil.copytree(src, out, ignore=lambda d, names: [n for n in names if d == src and n in META_DOSYALAR])
        g = V12(u, esler, v11_man['vektorler'], out)
        yeni = g.uret()
        ids = [i['id'] for i in v11_man['vektorler']] + [i['id'] for i in yeni]
        if len(ids) != len(set(ids)):
            raise RuntimeError('yinelenen vektor kimligi')
        items = copy.deepcopy(v11_man['vektorler']) + yeni
        sayim = {}
        for i in yeni:
            if 'mr4' in i['insa']:
                k = 'MR4-disi-tanimlayici' if 'MR4-kapsam-disi' in ';'.join(i['sinanan']['ek_etiketler']) else 'MR4'
            elif i['id'].startswith('T7'):
                k = 'K5-T7'
            else:
                k = i['aile']
            k = k + ('+ED25519' if i['id'].endswith('-ED25519') else '')
            sayim[k] = sayim.get(k, 0) + 1
        m = {'surum': SURUM, 'temel_surum': 'v1.1', 'vektor_sayisi': len(items),
             'v1_1_vektor_sayisi': len(v11_man['vektorler']), 'yeni_vektor_sayisi': len(yeni), 'yeni_dagilim': sayim,
             'simdi': SIMDI, 'T0': v11_man['T0'],
             'uyari': 'Bu manifest vektorlerin NE OLDUGUNU tanimlar; beklenen karar (oracle) ICERMEZ. '
                      "'insa' alanlari uretim gercekleridir, kabul/red hukmu degildir. ÖK §6.5 kararlarinin alintisi "
                      'yalniz BATARYA-ESLEME.md\'dedir.',
             'yedek_kural': v11.YEDEK_KURAL, 'kayitsiz_alg': KAYITSIZ,
             'anahtar_dizini': 'anahtarlar/v1',
             'anahtar_sha256sums': _sha(os.path.join(donmus_kok, 'anahtarlar', 'v1', 'SHA256SUMS')),
             'v1_1_capalari': {'vektorler/v1.1/MANIFEST.json': _sha(os.path.join(donmus_kok, 'vektorler', 'v1.1', 'MANIFEST.json')),
                               'vektorler/v1.1/SHA256SUMS': _sha(os.path.join(donmus_kok, 'vektorler', 'v1.1', 'SHA256SUMS'))},
             'v1_capalari': v11_man['v1_capalari'],
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
    items, yeni = uret_v12(kok, donmus_kok or kok, surumler)
    os.makedirs(os.path.join(kok, 'sonuclar'), exist_ok=True)
    with open(os.path.join(kok, 'sonuclar', 'v1.2_boyutlar.csv'), 'w', newline='', encoding='utf-8') as f:
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
