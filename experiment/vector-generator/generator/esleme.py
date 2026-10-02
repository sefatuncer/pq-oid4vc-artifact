"""Generator of BATTERY-MAPPING.md: PR §6.5 (K1-K11, V+/V-), MR1-MR4 and L4c <-> test vector set v1.3.

* Oracle decisions, MR definitions, L4c and the §2H quotations are taken verbatim BY PARSING ON-KAYIT-TASLAK.md
  (not written by hand); if they are not found, the generation STOPS.
* Every vector id must exist in the v1.3 MANIFEST; otherwise the generation STOPS.
* If an id of the control arm has a '-ED25519' counterpart, it is added to the cell automatically (fallback rule of PR §2D item 2).
* The vectors and the manifest contain NO oracle decision; this file only quotes the decisions of the PR.
* Sections: §1-§2 JOSE/SD-JWT (the same as the v1.2 mapping; the only difference is that the K8/K9 control and composite cells were adapted to
  PR §2H item 9), §3 COSE, §4 L4c, §5 honesty notes, §6 check.
  The v1.2 mapping (d7335217...) was produced with the esleme.py in the image pq-a09-credgen:1.2; its copy is
  results/BATTERY-MAPPING_v1.2.md. The generated text (Turkish) is unchanged; it still names the old paths.
Usage: python -m generator.esleme <generator_root> <ON-KAYIT-TASLAK.md> [output.md]
"""
import hashlib
import json
import os
import re
import sys

SURUM = 'v1.3'
KOLLAR = ('kontrol', 'ML-DSA-65', 'composite')
KOL_BASLIK = {'kontrol': 'kontrol (X = EdDSA)', 'ML-DSA-65': 'ML-DSA-65 (TK ikincil kol)',
              'composite': 'composite ML-DSA-65-ES256 (TK ana kol)'}


def H(b=(), i=(), n=None, na=None):
    return {'b': list(b), 'i': list(i), 'n': n, 'na': na}


CMP_IKINCIL = ['CMP03_ecdsa_der_uzunluk_bozuk', 'CMP04_ecdsa_ham_rs', 'CMP05_ecdsa_asgari_olmayan_der',
               'CMP06_sonda_artik_bayt', 'CMP07_yalniz_ml_bileseni', 'CMP08_bilesenler_farkli_iletilerden',
               'CMP09_ml_bileseni_ctx_bos', 'CMP10_onozet_sha256', 'CMP11_bos_ctx_uzunlugu_yok', 'CMP16_bilesen_sirasi_ters']
KOL_BAGIMSIZ = ('kol-bağımsız bayrak (ÖK §2H m.9): hedef başına bir kez, R = {ML-DSA-65} ile ML-DSA-65 sütunundaki '
                'vektörle ölçülür; bu kolun sonucu değildir (anahtar yolu ÖK §2D m.1, D-S1; EdDSA sertifika zinciri yok)')
KOL_BAGIMSIZ_C = ('kol-bağımsız bayrak (ÖK §2H m.9): composite kolunun sonucu değildir; hedef başına bir kez ML-DSA-65 '
                  'sütunundaki vektörle ölçülür (composite X.509 kapsam dışı, D-S1)')

VAKALAR = [
    ('K1', {'kontrol': H(['T1K_both_valid'], ['VC09_GJ_ES256_EdDSA'], 'ikincil: SD-JWT VC, General JSON (senaryo d)'),
            'ML-DSA-65': H(['T1P_both_valid'], ['VC07_GJ_ES256_MLDSA65'], 'ikincil: SD-JWT VC, General JSON (senaryo d)'),
            'composite': H(['T1C_both_valid'], ['VC08_GJ_ES256_composite'], 'ikincil: SD-JWT VC, General JSON (senaryo d)')}),
    ('K2', {'kontrol': H(['T2K_second_tampered']), 'ML-DSA-65': H(['T2P_second_tampered']),
            'composite': H(['T2C_second_tampered'], n='bozulma ML-DSA bileşeninin içinde (bayt 5)')}),
    ('K3', {'kontrol': H(['T3_stripped_to_ES256'], n='üç kolda ORTAK dosya; R = {X} kola göre değişir'),
            'ML-DSA-65': H(['T3_stripped_to_ES256'], ['VP06_GJ_pq_soyuldu_kb_gecerli'],
                           'ortak dosya; VP06: SD-JWT sunumu, KB etkisi tanımlayıcı (ÖK §2D m.4)'),
            'composite': H(['T3_stripped_to_ES256'], n='ortak dosya')}),
    ('K4', {'kontrol': H(['T5K_only_EdDSA']), 'ML-DSA-65': H(['T5P_only_ML-DSA-65']),
            'composite': H(['T5C_only_ML-DSA-65-ES256'])}),
    ('K5', {'kontrol': H(['T7K_plus_kayitsiz'], ['T4K_plus_ML-DSA-65', 'T6_plus_composite'],
                         'T7: gerçekten kayıtsız "X-KAYITSIZ-1" etiketi, rastgele bayt; T4/T6 ek imzası gerçek bir '
                         'algoritma (bazı hedeflerce tanınabilir) → ikincil'),
            'ML-DSA-65': H(['T7P_plus_kayitsiz'], ['T4P_plus_ML-DSA-65-ES256', 'UNK04_general_arti_kayitsiz_composite',
                                                    'UNK05_general_arti_alg_none'],
                           'UNK04: kayıtsız composite adı + geçerli bayt; UNK05: alg=none'),
            'composite': H(['T7C_plus_kayitsiz'], ['T4C_plus_ML-DSA-65'])}),
    ('K6', {'kontrol': H(na='uygulanamaz: vaka yalnız composite kolunda tanımlı ("Composite tek imza")'),
            'ML-DSA-65': H(na='uygulanamaz: vaka yalnız composite kolunda tanımlı'),
            'composite': H(['CMP00_gecerli_referans'], ['T5C_only_ML-DSA-65-ES256', 'VC03_composite_kid'],
                           'CMP00 compact; T5C General JSON; VC03 SD-JWT VC (kid)')}),
    ('K7', {'kontrol': H(na='uygulanamaz: vaka yalnız composite kolunda tanımlı'),
            'ML-DSA-65': H(na='uygulanamaz: vaka yalnız composite kolunda tanımlı'),
            'composite': H(['CMP01_ml_bileseni_bozuk', 'CMP02_ecdsa_bileseni_bozuk'], CMP_IKINCIL,
                           'CMP01: ML-DSA bileşeni, CMP02: ECDSA bileşeni ayrı ayrı bozuk; ikinciller serileştirme ve '
                           'uygulayıcı hatası taklitleri. (CMP14/15: ML-DSA-65-Ed25519, kol dışı composite)')}),
    ('K8', {'kontrol': H(na=KOL_BAGIMSIZ),
            'ML-DSA-65': H(['X5C04_karisik_pq_yaprak_klasik_ara'], ['X5C03_karisik_klasik_yaprak_pq_ara',
                                                                   'X5C05_karisik_pq_ara_klasik_kok'],
                           'X5C04: ML-DSA yaprak + klasik ara CA. UYARLANMIŞ: yaprak composite DEĞİL, ML-DSA-65 '
                           '(composite X.509 kapsam dışı; D-S1; HAIP §6.1.1 sapması)'),
            'composite': H(na=KOL_BAGIMSIZ_C)}),
    ('K9', {'kontrol': H(na=KOL_BAGIMSIZ),
            'ML-DSA-65': H(['X5C07_korumasiz_x5c'], ['X5C08_korumasiz_x5c_zincir_degisimi', 'X5C09_korumali_ve_korumasiz_x5c'],
                           'ML-DSA-65 yaprak; X5C08 zincir ikamesi, X5C09 hem korumalı hem korumasız'),
            'composite': H(na=KOL_BAGIMSIZ_C)}),
    ('K10', {'kontrol': H(['K10K_alg-EdDSA_anahtar-ES256', 'K10K_alg-ES256_anahtar-Ed25519'],
                          n='ikinci yön EdDSA etiketi içermez → -ED25519 eşi yok (bayt-aynı olurdu)'),
             'ML-DSA-65': H(['K10P_alg-ML-DSA-65_anahtar-ES256', 'K10P_alg-ES256_anahtar-ML-DSA-65']),
             'composite': H(['K10C_alg-ML-DSA-65-ES256_anahtar-ML-DSA-65', 'K10C_alg-ML-DSA-65_anahtar-ML-DSA-65-ES256'],
                            ['CMP12_ayrilabilirlik_ecdsa_ES256', 'CMP13_ayrilabilirlik_ml_MLDSA65'],
                            'ikincil: composite bileşen anahtarının bağımsız anahtar olarak yeniden kullanımı')}),
    ('K11', {'kontrol': H(['VC10_ikili_ihrac'], ['VC01_ES256_x5c'],
                          'VC10.credentials[0] (ES256 kopya) değerlendirilir; toplu yanıttaki PQ kopya ML-DSA-65 imzalıdır, '
                          'K11 kararı yalnız klasik kopyaya dayanır; "göç etmiş ihraççı" politikası kola göre'),
             'ML-DSA-65': H(['VC10_ikili_ihrac'], ['VC01_ES256_x5c'], 'VC10.credentials[0] (ES256 kopya)'),
             'composite': H(['VC10_ikili_ihrac'], ['VC01_ES256_x5c'], 'VC10.credentials[0] (ES256 kopya)')}),
    ('V+', {'kontrol': H(['VPLUS_ES256', 'VPLUS_EdDSA'], n='VPLUS_ES256 üç kolda ortak (ÖK §4.15: tek geçerli klasik imza)'),
            'ML-DSA-65': H(['VPLUS_ES256', 'VPLUS_ML-DSA-65'], n='VPLUS_ES256 ortak'),
            'composite': H(['VPLUS_ES256', 'CMP00_gecerli_referans'], n='VPLUS_ES256 ortak; CMP00 yeniden kullanıldı')}),
    ('V-', {'kontrol': H(['VMINUS_ES256', 'VMINUS_EdDSA'], n='VMINUS_ES256 üç kolda ortak'),
            'ML-DSA-65': H(['VMINUS_ES256', 'VMINUS_ML-DSA-65'], n='VMINUS_ES256 ortak'),
            'composite': H(['VMINUS_ES256', 'CMP01_ml_bileseni_bozuk'], n='VMINUS_ES256 ortak; CMP01 yeniden kullanıldı')}),
]

# ---------------------------------------------------------------- COSE (v1.3)
C_NA_KOMP = 'uygulanamaz: vaka yalnız composite kolunda tanımlı'
C_SIGN1_NOT = 'ikincil: COSE_Sign1 karşılığı (yalnız COSE_Sign1 destekleyen hedefler için tanımlayıcı)'
COSE_VAKALAR = [
    ('K1', {'kontrol': H(['COSE-K1K_iki_gecerli'], n='COSE_Sign (etiket 98): ES256 (-7) + EdDSA (-8)'),
            'ML-DSA-65': H(['COSE-K1P_iki_gecerli'], n='COSE_Sign: ES256 (-7) + ML-DSA-65 (-49)'),
            'composite': H(['COSE-K1C_iki_gecerli'], n='COSE_Sign: ES256 (-7) + ML-DSA-65-ES256 (-55, talep edilen)')}),
    ('K2', {'kontrol': H(['COSE-K2K_X_bozuk']), 'ML-DSA-65': H(['COSE-K2P_X_bozuk']),
            'composite': H(['COSE-K2C_X_bozuk'], n='bozulma ML-DSA bileşeninin içinde (bayt 5)')}),
    ('K3', {'kontrol': H(['COSE-K3_X_soyuldu'], ['COSE-VPLUS_ES256'], 'üç kolda ORTAK dosya; R = {X} kola göre değişir; ' +
                         C_SIGN1_NOT),
            'ML-DSA-65': H(['COSE-K3_X_soyuldu'], ['COSE-VPLUS_ES256'], 'ortak dosya; ' + C_SIGN1_NOT),
            'composite': H(['COSE-K3_X_soyuldu'], ['COSE-VPLUS_ES256'], 'ortak dosya; ' + C_SIGN1_NOT)}),
    ('K4', {'kontrol': H(['COSE-K4K_yalniz_X'], ['COSE-VPLUS_EdDSA'], C_SIGN1_NOT),
            'ML-DSA-65': H(['COSE-K4P_yalniz_X'], ['COSE-VPLUS_ML-DSA-65'], C_SIGN1_NOT),
            'composite': H(['COSE-K4C_yalniz_X'], ['COSE-K6_composite_gecerli'], C_SIGN1_NOT)}),
    ('K5', {'kontrol': H(['COSE-K5K_arti_kayitsiz'], n='üçüncü imzacı: kayıtsız tstr alg "X-KAYITSIZ-1", 128 B rastgele '
                                                      'belirlenimci bayt; bayrak B1 (ÖK §2H m.8)'),
            'ML-DSA-65': H(['COSE-K5P_arti_kayitsiz']), 'composite': H(['COSE-K5C_arti_kayitsiz'])}),
    ('K6', {'kontrol': H(na='uygulanamaz: vaka yalnız composite kolunda tanımlı ("Composite tek imza")'),
            'ML-DSA-65': H(na=C_NA_KOMP),
            'composite': H(['COSE-K6_composite_gecerli'], ['COSE-K4C_yalniz_X'],
                           'K6: COSE_Sign1, alg -55 (talep edilen, kayıtlı değil); ikincil K4C: COSE_Sign tek imzacı')}),
    ('K7', {'kontrol': H(na=C_NA_KOMP), 'ML-DSA-65': H(na=C_NA_KOMP),
            'composite': H(['COSE-K7_ml_bileseni_bozuk', 'COSE-K7_ecdsa_bileseni_bozuk'],
                           n='COSE_Sign1; ML-DSA ve ECDSA bileşenleri ayrı ayrı bozuk (DER yapısı geçerli)')}),
    ('K8', {'kontrol': H(na=KOL_BAGIMSIZ),
            'ML-DSA-65': H(['COSE-K8_x5chain_karisik'], n='COSE_Sign1, KORUMALI x5chain (RFC 9360, etiket 33): ML-DSA-65 '
                                                          'yaprak + klasik ara CA. UYARLANMIŞ: yaprak composite DEĞİL (D-S1)'),
            'composite': H(na=KOL_BAGIMSIZ_C)}),
    ('K9', {'kontrol': H(na=KOL_BAGIMSIZ),
            'ML-DSA-65': H(['COSE-K9_x5chain_korumasiz'], n='COSE_Sign1, x5chain KORUMASIZ başlıkta; tam-PQ zincir'),
            'composite': H(na=KOL_BAGIMSIZ_C)}),
    ('K10', {'kontrol': H(['COSE-K10K_alg-EdDSA_anahtar-ES256', 'COSE-K10K_alg-ES256_anahtar-Ed25519'],
                          n='COSE_Sign1; ikinci yön EdDSA etiketi içermez → -ED25519 eşi yok'),
             'ML-DSA-65': H(['COSE-K10P_alg-ML-DSA-65_anahtar-ES256', 'COSE-K10P_alg-ES256_anahtar-ML-DSA-65']),
             'composite': H(['COSE-K10C_alg-ML-DSA-65-ES256_anahtar-ML-DSA-65',
                             'COSE-K10C_alg-ML-DSA-65_anahtar-ML-DSA-65-ES256'])}),
    ('K11', {k: H(na='uygulanamaz: K11 ikili ihraç (OID4VCI toplu yanıtı, SD-JWT VC; `VC10`) biçimine bağlıdır; COSE '
                     'bataryasında ihraç yanıtı yoktur (mdoc kapsam dışı, ÖK §2D). İmza düzeyindeki karşılığı "göç etmiş '
                     'ihraççının yalnız klasik belgesi" §4 L4c-2 satırıdır (`COSE-VPLUS_ES256`)') for k in KOLLAR}),
    ('V+', {'kontrol': H(['COSE-VPLUS_ES256', 'COSE-VPLUS_EdDSA'], n='COSE-VPLUS_ES256 üç kolda ortak (ÖK §4.15)'),
            'ML-DSA-65': H(['COSE-VPLUS_ES256', 'COSE-VPLUS_ML-DSA-65'], n='COSE-VPLUS_ES256 ortak'),
            'composite': H(['COSE-VPLUS_ES256', 'COSE-K6_composite_gecerli'], n='COSE-VPLUS_ES256 ortak; K6 yeniden kullanıldı')}),
    ('V-', {'kontrol': H(['COSE-VMINUS_ES256', 'COSE-VMINUS_EdDSA'], n='COSE-VMINUS_ES256 üç kolda ortak'),
            'ML-DSA-65': H(['COSE-VMINUS_ES256', 'COSE-VMINUS_ML-DSA-65'], n='COSE-VMINUS_ES256 ortak'),
            'composite': H(['COSE-VMINUS_ES256', 'COSE-K7_ml_bileseni_bozuk'],
                           n='COSE-VMINUS_ES256 ortak; K7 (ML bileşeni) yeniden kullanıldı')}),
]


def P(*ciftler, n=None, na=None):
    return {'c': list(ciftler), 'n': n, 'na': na}


def mr4_ciftleri(man_ids, kok_idler):
    out = []
    for k in kok_idler:
        for vid in man_ids:
            if vid.startswith(k + '-SIRA-') and not vid.endswith('-ED25519'):
                out.append((k, vid))
    return out


MR = [
    ('MR1', {'kontrol': P(('T1K_both_valid', 'T3_stripped_to_ES256')),
             'ML-DSA-65': P(('T1P_both_valid', 'T3_stripped_to_ES256'), ('VP05_GJ_ES256_MLDSA65_kb', 'VP06_GJ_pq_soyuldu_kb_gecerli'),
                            ('REQ04_coklu_imzali', 'REQ05_coklu_imzali_pq_soyuldu'),
                            n='VP05↔VP06 tanımlayıcı (KB); REQ04↔REQ05 senaryo (c), cüzdan tarafı (IS-PLANI Adım 11)'),
             'composite': P(('T1C_both_valid', 'T3_stripped_to_ES256'))}),
    ('MR2', {'kontrol': P(('T1K_both_valid', 'T7K_plus_kayitsiz'), ('T1K_both_valid', 'T4K_plus_ML-DSA-65'),
                          ('T1K_both_valid', 'T6_plus_composite'), n='birincil T1↔T7; ikincil T1↔T4, T1↔T6'),
             'ML-DSA-65': P(('T1P_both_valid', 'T7P_plus_kayitsiz'), ('T1P_both_valid', 'T4P_plus_ML-DSA-65-ES256'),
                            n='birincil T1↔T7; ikincil T1↔T4'),
             'composite': P(('T1C_both_valid', 'T7C_plus_kayitsiz'), ('T1C_both_valid', 'T4C_plus_ML-DSA-65'),
                            n='birincil T1↔T7; ikincil T1↔T4')}),
    ('MR3', {'kontrol': P(('VC09_GJ_ES256_EdDSA', 'VC09_GJ_ES256_EdDSA'), ('VC01_ES256_x5c', 'VC11_typ_vc+sd-jwt'),
                          n='VC09: aynı dosya, sdjwtvc_surum -13 (JSON isteğe bağlı) / -19 (kapsam dışı); '
                            'VC01↔VC11: typ dc+sd-jwt / vc+sd-jwt (-13 geçişi)'),
             'ML-DSA-65': P(('VC07_GJ_ES256_MLDSA65', 'VC07_GJ_ES256_MLDSA65'), ('VC01_ES256_x5c', 'VC11_typ_vc+sd-jwt'),
                            n='VC07 aynı dosya -13/-19; VC01↔VC11 ortak'),
             'composite': P(('VC08_GJ_ES256_composite', 'VC08_GJ_ES256_composite'), ('VC01_ES256_x5c', 'VC11_typ_vc+sd-jwt'),
                            n='VC08 aynı dosya -13/-19; VC01↔VC11 ortak')}),
]
MR4_KOK = {'kontrol': ['T1K_both_valid', 'T2K_second_tampered', 'T4K_plus_ML-DSA-65', 'T6_plus_composite', 'T7K_plus_kayitsiz',
                       'VC09_GJ_ES256_EdDSA'],
           'ML-DSA-65': ['T1P_both_valid', 'T2P_second_tampered', 'T4P_plus_ML-DSA-65-ES256', 'T7P_plus_kayitsiz',
                         'VC07_GJ_ES256_MLDSA65', 'REQ04_coklu_imzali'],
           'composite': ['T1C_both_valid', 'T2C_second_tampered', 'T4C_plus_ML-DSA-65', 'T7C_plus_kayitsiz',
                         'VC08_GJ_ES256_composite']}
COSE_MR = [
    ('MR1', {a: P(('COSE-K1%s_iki_gecerli' % c, 'COSE-K3_X_soyuldu')) for a, c in zip(KOLLAR, 'KPC')}),
    ('MR2', {a: P(('COSE-K1%s_iki_gecerli' % c, 'COSE-K5%s_arti_kayitsiz' % c), n='birincil K1↔K5 (kayıtsız etiket)')
             for a, c in zip(KOLLAR, 'KPC')}),
    ('MR3', {a: P(na='uygulanamaz: MR3 SD-JWT VC -13/-19 sürüm farkıdır (ÖK §2D m.7); COSE vektörlerinde bu boyut yok')
             for a in KOLLAR}),
]
COSE_MR4_KOK = {a: ['COSE-K1%s_iki_gecerli' % c, 'COSE-K2%s_X_bozuk' % c] for a, c in zip(KOLLAR, 'KPC')}

# ---------------------------------------------------------------- L4c (v1.3)
L4C_SATIRLAR = [
    ('L4c-1', 'göç etmiş ihraççı (`https://issuer.example`), yalnız X', 'K4',
     {'ML-DSA-65': ('VPLUS_ML-DSA-65', 'COSE-VPLUS_ML-DSA-65'),
      'composite': ('CMP00_gecerli_referans', 'COSE-K6_composite_gecerli')}),
    ('L4c-2', 'göç etmiş ihraççı (`https://issuer.example`), yalnız ES256', 'goc',
     {'ML-DSA-65': ('VPLUS_ES256', 'COSE-VPLUS_ES256'), 'composite': ('VPLUS_ES256', 'COSE-VPLUS_ES256')}),
    ('L4c-3', 'eski ihraççı (`https://legacy-issuer.example`, ayrı anahtar/kid), yalnız ES256', 'eski',
     {'ML-DSA-65': ('L4C-JOSE_eski_ES256', 'L4C-COSE_eski_ES256'),
      'composite': ('L4C-JOSE_eski_ES256', 'L4C-COSE_eski_ES256')}),
]


def _ara(desen, txt, ad, flags=re.M):
    m = re.search(desen, txt, flags)
    if not m:
        raise SystemExit('MAPPING ERROR: not found in the PR text: %s' % ad)
    return m.group(1).strip()


def ok_ayristir(txt):
    s65 = txt[txt.index('### 6.5 Test bataryası'):txt.index('### 6.6')]
    satir = {}
    for line in s65.splitlines():
        m = re.match(r'^\| (K\d+|V\+ / V−) \| (.*?) \| (.*?) \|\s*$', line)
        if m:
            satir[m.group(1)] = (m.group(2).strip(), m.group(3).strip())
    politika = re.search(r'\*\*Politika:\*\* (.*)', s65).group(1).strip()
    senaryo = re.search(r'\*\*Senaryo etiketleri.*?\*\*\s*\n(.*?)\n\n', s65, re.S).group(1).strip()
    s420 = txt[txt.index('### 4.20 Oracle'):txt.index('### 4.21')]
    mr = {k: v.strip() for k, v in re.findall(r'^\s*- (MR[123]): (.*)$', s420, re.M)}
    m4 = re.search(r'\*\*Metamorfik ilişki MR4\*\* \([^)]*\): (.*)$', txt, re.M)
    mr['MR4'] = m4.group(1).strip()
    ek = {
        'L4c': _ara(r'^\s*- \*\*L4c \(yalnız kompakt serileştirme destekleyen hedefler\):\*\* (.*)$', txt, 'L4c (§2B m.6)'),
        'Y_i': _ara(r'^\s*- \*\*Y_i\*\* = (.*)$', txt, 'Y_i (§2B m.6)'),
        'K8K9': _ara(r'^\*\*9\. K8/K9\.\*\* (.*)$', txt, '§2H m.9'),
        'V': _ara(r'^\*\*10\. V±\.\*\* (.*)$', txt, '§2H m.10'),
        'COSE': _ara(r'^\*\*12\. COSE ve L4c\.\*\*\s*\n- (.*)$', txt, '§2H m.12'),
    }
    return satir, politika, senaryo, mr, ek


def main(kok, onkayit, cikti=None):
    cikti = cikti or os.path.join(kok, 'BATTERY-MAPPING.md')
    man_p = os.path.join(kok, 'vectors', SURUM, 'MANIFEST.json')
    man = json.load(open(man_p, encoding='utf-8'))
    ids = [v['id'] for v in man['vektorler']]
    idset = set(ids)
    raw = open(onkayit, 'rb').read()
    satir, politika, senaryo, mr, ek = ok_ayristir(raw.decode('utf-8'))
    kullanilan = set()

    def chk(vid):
        if vid not in idset:
            raise SystemExit('MAPPING ERROR: %s not in the %s manifest' % (vid, SURUM))
        kullanilan.add(vid)
        return vid

    def fmt_ids(lst, kol):
        out = []
        for vid in lst:
            chk(vid)
            s = '`%s`' % vid
            if kol == 'kontrol' and vid + '-ED25519' in idset:
                s += ' [yedek: `%s`]' % chk(vid + '-ED25519')
            out.append(s)
        return ', '.join(out)

    def hucre(h, kol):
        if h.get('na'):
            return '— *%s*' % h['na']
        parts = []
        if h['b']:
            parts.append('**birincil:** ' + fmt_ids(h['b'], kol))
        if h['i']:
            parts.append('**ikincil:** ' + fmt_ids(h['i'], kol))
        if h.get('n'):
            parts.append('*%s*' % h['n'])
        return '<br>'.join(parts)

    def cift_hucre(p, kol):
        if p.get('na'):
            return '— *%s*' % p['na']
        parts = []
        for a, b in p['c']:
            chk(a)
            chk(b)
            s = '`%s` ↔ `%s`' % (a, b) if a != b else '`%s` (-13 ↔ -19)' % a
            if kol == 'kontrol':
                ea, eb = a + '-ED25519', b + '-ED25519'
                if ea in idset:
                    s += ' [yedek: `%s` ↔ `%s`]' % (chk(ea), chk(eb) if eb in idset else chk(b)) if a != b else \
                        ' [yedek: `%s`]' % chk(ea)
            parts.append(s)
        if p.get('n'):
            parts.append('*%s*' % p['n'])
        return '<br>'.join(parts)

    def vaka_tablosu(L, vakalar, onek):
        L.append('| Vaka | ÖK §6.5 içerik (alıntı) | ÖK §6.5 oracle kararı (alıntı) | ' +
                 ' | '.join(KOL_BASLIK[k] for k in KOLLAR) + ' |')
        L.append('|---|---|---|---|---|---|')
        for vaka, hucreler in vakalar:
            if vaka in ('V+', 'V-'):
                icerik, karar_tam = satir['V+ / V−']
                karar = '%s — alıntı: "%s" (%s)' % ('KABUL' if vaka == 'V+' else 'RED', karar_tam,
                                                    'V+ → ilk' if vaka == 'V+' else 'V− → ikinci')
                icerik = icerik + (' — V+: tek geçerli imza' if vaka == 'V+' else ' — V−: bozuk imza') + ' (ÖK §4.15)'
                ad = 'V+' if vaka == 'V+' else 'V−'
            else:
                icerik, karar = satir[vaka]
                ad = vaka
            L.append('| %s%s | %s | %s | %s |' % (onek, ad, icerik, karar, ' | '.join(hucre(hucreler[k], k) for k in KOLLAR)))

    def mr_tablosu(L, mrler, mr4_kok, onek, mr4_not=None):
        L.append('| MR | Tanım (alıntı; MR1–MR3: ÖK §4.20, MR4: ÖK §2B m.8 / §2C m.4) | ' +
                 ' | '.join(KOL_BASLIK[k] for k in KOLLAR) + ' |')
        L.append('|---|---|---|---|---|')
        for kod, hucreler in mrler:
            L.append('| %s%s | %s | %s |' % (onek, kod, mr[kod], ' | '.join(cift_hucre(hucreler[k], k) for k in KOLLAR)))
        mr4_h = {}
        for k in KOLLAR:
            mr4_h[k] = P(*mr4_ciftleri(ids, mr4_kok[k]), n=(mr4_not or {}).get(k))
        L.append('| %sMR4 | %s | %s |' % (onek, mr['MR4'], ' | '.join(cift_hucre(mr4_h[k], k) for k in KOLLAR)))

    L = []
    L.append('# C3 bataryası eşlemesi — ÖK §6.5 ↔ test vektörü seti v1.3')
    L.append('')
    L.append('> **Üretildi:** `uretec/esleme.py` (belirlenimci). Kararlar, MR tanımları, L4c ve §2H maddeleri ön kayıt '
             'metninden **ayrıştırılarak** birebir alıntılanır; her vektör kimliği v1.3 manifestinde denetlenir.')
    L.append('> - Ön kayıt: `00-on-kayit/ON-KAYIT-TASLAK.md` SHA-256 `%s`' % hashlib.sha256(raw).hexdigest())
    L.append('> - Batarya: `experiment/vector-generator/vektorler/v1.3/MANIFEST.json` SHA-256 `%s` (%d vektör)' %
             (hashlib.sha256(open(man_p, 'rb').read()).hexdigest(), len(ids)))
    L.append('>')
    L.append('> **Vektörler ve manifest oracle kararı İÇERMEZ.** Bu dosya yalnız ÖK §6.5\'in ve §2B m.6\'nın kararlarını '
             'alıntılar; kararın hedef başına uygulanması oracle N-sürüm işidir (ÖK §4.20).')
    L.append('')
    L.append('**ÖK §6.5 politika (alıntı):** ' + politika + ' A = ES256; X = kontrolde EdDSA, tedavide ML-DSA-65 ya da '
             'composite -04 (ÖK §6.5).')
    L.append('')
    L.append('**Yedek kural (ÖK §2D m.2):** hedef `EdDSA`\'yı desteklemiyor ama RFC 9864 `Ed25519`\'u belgeli olarak '
             'destekliyorsa kontrol kolunda `[yedek: …-ED25519]` eşleri koşulur; kullanılan etiket hedef başına kaydedilir. '
             '**Anahtar yolu (ÖK §2D m.1, D-S1):** bütün kollarda hedefin belgeli API\'si (JWK/JWKS ya da doğrudan anahtar; '
             'COSE\'da COSE_Key ya da doğrudan anahtar).')
    L.append('')
    L.append('**Tabaka:** JOSE ve SD-JWT hedefleri §1–§2\'deki vektörlerle, COSE hedefleri §3\'teki vektörlerle ölçülür. '
             'L4c biçimi (ÖK §2B m.6) §4\'tedir. **Birincil / ikincil (ÖK §2G m.4):** önceden kayıtlı sonuç değişkenleri '
             'yalnız **birincil** vektörlerden hesaplanır; **ikincil** vektörler tanımlayıcıdır.')
    L.append('')
    L.append('## 1. JOSE / SD-JWT — vakalar K1–K11, V+ / V−')
    L.append('')
    vaka_tablosu(L, VAKALAR, '')
    L.append('')
    L.append('**Senaryo etiketleri (ÖK §6.5, alıntı):**')
    L.append('')
    L.append(senaryo)
    L.append('')
    L.append('## 2. JOSE / SD-JWT — metamorfik ilişkiler MR1–MR4')
    L.append('')
    mr_tablosu(L, MR, MR4_KOK, '', {'ML-DSA-65': 'REQ04 çiftleri senaryo (c), cüzdan tarafı (IS-PLANI Adım 11, wallet-path)'})
    L.append('')
    L.append('*MR4 dışı, tanımlayıcı:* `%s` ↔ `%s` — permütasyon KB-JWT `sd_hash`\'inin bağladığı imzayı değiştirir '
             '(RFC 9901 §8.1 belirsizliği; ÖK §2D m.4). MR4 kapsamında değerlendirilmez.' %
             (chk('VP05_GJ_ES256_MLDSA65_kb'), chk('VP05_GJ_ES256_MLDSA65_kb-SIRA-ters')))
    L.append('')
    L.append('## 3. COSE (RFC 9052) — vakalar K1–K11, V+ / V−, MR1–MR4')
    L.append('')
    L.append('**ÖK §2H m.12 (alıntı):** ' + ek['COSE'])
    L.append('')
    L.append('COSE_Sign (etiket 98, çok imzacılı; K1–K5 ve MR4) ve COSE_Sign1 (etiket 18, tek imzacılı; K6–K10, V±). '
             'Algoritma kimlikleri korpustan birebir (satır numaraları manifestte `cose_kimlik_kaynaklari`): ES256 = −7 '
             '(RFC 9053; RFC 9864 §4.2.2 "Deprecated"; HAIP §7 "-7 or -9, as applicable"), EdDSA = −8 (RFC 9053; RFC 9864 '
             '"Deprecated"), Ed25519 = −19 (RFC 9864), ML-DSA-65 = −49 (RFC 9964), ML-DSA-65-ES256 = −55 (-04 §7.2: '
             '**talep edilen, kayıtlı değil**). Yük: belirlenimci CBOR harita; `kid` korumasız başlıkta (JWK `kid`\'inin '
             'base64url-çözülmüş 32 baytı). Doğrulama girdileri: `anahtarlar/v1.3/cose-anahtarlar.json`.')
    L.append('')
    vaka_tablosu(L, COSE_VAKALAR, 'COSE ')
    L.append('')
    mr_tablosu(L, COSE_MR, COSE_MR4_KOK, 'COSE ')
    L.append('')
    L.append('## 4. L4c — iki ihraççı (ÖK §2B m.6)')
    L.append('')
    L.append('**L4c (alıntı):** ' + ek['L4c'])
    L.append('')
    L.append('**Y_i (alıntı):** ' + ek['Y_i'])
    L.append('')
    k4_icerik, k4_karar = satir['K4']
    parca = [p.strip() for p in ek['L4c'].split('. ')]
    goc = next((p for p in parca if p.startswith('Göç etmiş ihraççının')), None)
    if not goc or ', eski ihraççının' not in goc:
        raise SystemExit('MAPPING ERROR: the L4c decision sentence could not be parsed')
    goc_c, eski_c = goc.split(', eski ihraççının')
    eski_c = 'eski ihraççının' + eski_c.rstrip('.')
    dayanak = {'K4': 'ÖK §6.5 K4 (alıntı): "%s" → "%s"; L4c politikası "PQ/composite zorunlu"' % (k4_icerik, k4_karar),
               'goc': 'ÖK §2B m.6 L4c (alıntı): "%s"' % goc_c, 'eski': 'ÖK §2B m.6 L4c (alıntı): "%s"' % eski_c}
    L.append('Aynı doğrulayıcı örneğine iki ihraççı birlikte verilir: `anahtarlar/v1.3/acik-jwks-l4c.json` (`ihraccilar`: '
             'iss → kid listesi) ve COSE için `anahtarlar/v1.3/cose-anahtarlar.json`. Eski ihraççı anahtarı '
             '`issuer-eski/ES256`, türetme etiketi `v1.3/issuer-eski/ES256` (`anahtarlar/v1.3/roller.json`).')
    L.append('')
    L.append('| Satır | Belge | Dayanak (alıntı) | %s | %s |' % (KOL_BASLIK['ML-DSA-65'], KOL_BASLIK['composite']))
    L.append('|---|---|---|---|---|')
    for kod, belge, dkey, hucreler in L4C_SATIRLAR:
        h = []
        for k in ('ML-DSA-65', 'composite'):
            j, c = hucreler[k]
            h.append('**birincil:** JOSE compact `%s`; COSE_Sign1 `%s`' % (chk(j), chk(c)))
        L.append('| %s | %s | %s | %s |' % (kod, belge, dayanak[dkey], ' | '.join(h)))
    L.append('')
    L.append('*Kontrol kolu:* L4c "PQ/composite zorunlu" politikasıdır; brif yalnız tedavi kollarını istedi, kontrol için '
             'satır üretilmedi. Gerekirse yeni vektör gerekmeden kurulabilir: `VPLUS_EdDSA` / `COSE-VPLUS_EdDSA` (yalnız X), '
             '`VPLUS_ES256` / `COSE-VPLUS_ES256`, `L4C-*_eski_ES256` (eski ihraççı vektörleri kol-bağımsızdır).')
    L.append('')
    L.append('## 5. Dürüstlük notları')
    L.append('')
    notlar = [
        '**K8 uyarlanmış (D-S1):** ÖK §6.5 K8 "yaprak composite, ara CA klasik" der; composite X.509 (LAMPS) v1–v1.3 '
        'kapsamı dışında olduğu için K8, ML-DSA-65 yaprak + klasik ara CA ile (`X5C04`; COSE\'da `COSE-K8_x5chain_karisik`) '
        'gerçekleştirilir ve "HAIP §6.1.1 sapması" olarak etiketlidir. Aynı nedenle K9 da ML-DSA-65 yaprakla (`X5C07`; '
        '`COSE-K9_x5chain_korumasiz`) gerçekleştirilir.',
        '**K8/K9 kol-bağımsız (ÖK §2H m.9, alıntı):** "%s" Bu nedenle v1.3 eşlemesinde K8/K9\'un kontrol ve composite '
        'hücreleri "—"dir (v1.2 eşlemesinde composite hücresi `X5C04`/`X5C07`\'yi UYARLANMIŞ notuyla gösteriyordu; §2H, '
        '§2A–§2G\'nin önüne geçer). JOSE bölümünde v1.2 eşlemesine göre başka değişiklik yoktur.' % ek['K8K9'],
        '**Uygulanamayan hücreler:** K6 ve K7 ÖK §6.5\'te yalnız composite için tanımlıdır; kontrol ve ML-DSA-65 '
        'sütunlarında "—". COSE\'da K11 ve MR3 uygulanamaz (gerekçeler hücrelerde).',
        '**K3 ortak dosya:** `T3_stripped_to_ES256` ve `COSE-K3_X_soyuldu` üç kolda aynı dosyadır (aynı yük, anahtar, '
        'başlık; belirlenimci ES256 imzası); kollar arası fark yalnız politikadadır (R = {X}).',
        '**K5 birincil/ikincil:** birincil `T7*` / `COSE-K5*` (gerçekten kayıtsız etiket `X-KAYITSIZ-1`, 128 B rastgele '
        'belirlenimci bayt); `T4*`/`T6` ek imzası gerçek bir algoritma olduğu için bazı hedeflerce tanınabilir → ikincil. '
        'K5 tek bir oracle kararı taşımaz; B1 bayrağında sınıflanır (ÖK §2H m.8).',
        '**K10:** her kolda iki yön; imza baytları başlıktaki alg ile değil gerçek anahtarın kendi algoritmasıyla '
        'üretilmiş geçerli imzadır (manifest `insa.k10`). Kontrolün ikinci yönü (`alg=ES256` + Ed25519 anahtarı) EdDSA '
        'etiketi içermez; `-ED25519` eşi bayt-aynı olacağından üretilmedi (JOSE ve COSE).',
        '**K11:** ikili ihraç vektörü (`VC10`) ES256 ve ML-DSA-65 kopyalarını taşır; K11 kararı yalnız klasik kopyaya dayanır, '
        '"göç etmiş ihraççı" politikası kola göre tanımlanır. Kontrol ve composite kollarının PQ kopyası toplu yanıtta yoktur; '
        'K11 kararı için gerekmez.',
        '**V± (ÖK §2H m.10, alıntı):** "%s"' % ek['V'],
        '**MR1 (soyma):** T1 ↔ T3 her kolda; ML-DSA-65 kolunda ek olarak VP05 ↔ VP06 (tanımlayıcı, KB) ve REQ04 ↔ REQ05 '
        '(senaryo c, cüzdan tarafı). COSE: K1 ↔ K3.',
        '**MR2 (bilinmeyen alg):** T1 ↔ T7 birincil (kayıtsız etiket), T1 ↔ T4 (ve kontrolde T1 ↔ T6) ikincil. COSE: K1 ↔ K5.',
        '**MR3 (sürüm):** -13 / -19 farkı iki yere dokunur (ÖK §2D m.7): senaryo (d) JSON vektörleri (VC07/VC08/VC09; '
        'aynı dosya iki `sdjwtvc_surum` ayarında) ve `VC11` (`vc+sd-jwt` geçişi; VC01 ile çift).',
        '**MR4:** iki imzalılarda ters sıra; üç imzalılarda (T4*, T6, T7*) "ek/kayıtsız imza önce" ve "tam ters". SD-JWT VC '
        'permütasyonlarında `disclosures` her zaman yeni ilk korumasız başlıktadır (RFC 9901 §8.3; manifest `insa.mr4`). '
        'T7* permütasyonları ÖK listesine ek olarak üretildi (K5 birincil vektörleri çoklu imzalıdır). COSE: K1 ve K2 '
        'COSE_Sign imzacı sırası ters; her COSE_Signature bayt-aynı taşınır (imzacı Sig_structure\'ı sıradan bağımsızdır).',
        '**Senaryo (c):** REQ04 ve permütasyonu cüzdan tarafı vakalarıdır; kütüphane bataryasında değil IS-PLANI Adım 11\'de '
        '(`wallet-path`) koşulur.',
        '**COSE_Sign1\'e sınırlı hedefler:** K1, K2, K5 ve MR4 COSE_Sign gerektirir. Çoklu imzayı desteklemeyen hedefte '
        'Y_i = L4c\'dir (ÖK §2B m.6; §4). K3/K4 satırlarındaki COSE_Sign1 karşılıkları ikincildir (tanımlayıcı); bu '
        'hedeflerde K1–K5\'in nasıl sayılacağı oracle/ÖK kararıdır, eşleme karar vermez.',
        '**COSE algoritma kimlikleri:** RFC 9864 §4.2.2 COSE `ES256` (−7) ve `EdDSA` (−8) değerlerini "Deprecated" '
        '(polimorfik) yapar; HAIP §7 ES256 için "COSE algorithm identifier -7 or -9, as applicable" der. Brif ES256 '
        'istediği için yalnız −7 üretildi; ESP256 (−9) üretilmedi (açık soru, NOTLAR H). Composite −55 IANA\'da kayıtlı '
        'değildir (-04 §7.2 "TBD (request assignment -55)").',
        '**L4c:** eski ihraççının vektörleri yalnız ES256\'dır ve kol-bağımsızdır; göç etmiş ihraççının karşılıkları '
        'mevcut vektörlerdir (yeniden üretilmedi, bayt-aynı olurlardı). Vektörlerde yalnız `insa.ihracci` gerçekleri '
        'vardır; kabul/red beklentisi yalnız bu dosyadaki ÖK alıntısındadır.',
    ]
    for n in notlar:
        L.append('- ' + n)
    L.append('')
    L.append('## 6. Denetim')
    L.append('')
    L.append('- Eşlemede kullanılan vektör kimliği: **%d** (hepsi v1.3 manifestinde var).' % len(kullanilan))
    yeni = [v['id'] for v in man['vektorler'][man['v1_2_vektor_sayisi']:]]
    kullanilmayan = [v for v in yeni if v not in kullanilan]
    L.append('- v1.3\'te yeni olup eşlemede geçmeyen kimlik: %s.' % (', '.join('`%s`' % v for v in kullanilmayan)
                                                                     if kullanilmayan else '**yok**'))
    metin = '\n'.join(L) + '\n'
    with open(cikti, 'w', encoding='utf-8', newline='\n') as f:
        f.write(metin)
    print(json.dumps({'cikti': cikti, 'kullanilan_kimlik': len(kullanilan), 'esleme_disi_yeni': kullanilmayan,
                      'sha256': hashlib.sha256(metin.encode('utf-8')).hexdigest()}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None))
