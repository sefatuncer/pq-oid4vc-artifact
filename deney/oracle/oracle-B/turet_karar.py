#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Oracle B (PQ-OID4VC, Adim 9 gorev 6) -- karar.tsv turetici.

Ne yapar:
  * v1.2 MANIFEST.json'u okur (yalniz 'insa' ve 'dogrulama_girdileri' gercekleri);
    vektor dosyalarini ACMAZ, dogrulamaz; ag kullanmaz.
  * Elle yazilmis olgu/rol tablolarini manifestle capraz denetler.
  * Madde kutuphanesindeki her birebir alintiyi kaynak metinde (satir araliginda,
    bosluk normalize) arar; bulunamazsa durur.
  * YONTEM.md'deki uc yapilandirmayi (L4, P2, P0) ve kol atamasini uygular,
    karar.tsv'yi yazar, dagilim ozetini basar.

Calistirma (klasor kokunden):
  PYTHONIOENCODING=utf-8 python turet_karar.py [--kollar k1,k2,...]
"""
import argparse
import collections
import json
import os
import re
import sys

# ---------------------------------------------------------------- yollar
BU = os.path.dirname(os.path.abspath(__file__))


def proje_koku(bas):
    d = bas
    for _ in range(6):
        if os.path.isdir(os.path.join(d, '00-on-kayit')) and os.path.isdir(os.path.join(d, '01-korpus')):
            return d
        d = os.path.dirname(d)
    sys.exit('proje koku bulunamadi')


KOK = proje_koku(BU)
MANIFEST = os.path.join(KOK, 'deney', 'uretec', 'vektorler', 'v1.2', 'MANIFEST.json')
METIN = os.path.join(KOK, '01-korpus', 'metin')
OK_DOSYA = os.path.join(KOK, '00-on-kayit', 'ON-KAYIT-TASLAK.md')
CIKTI = os.path.join(BU, 'karar.tsv')

# ---------------------------------------------------------------- belgeler
BELGE = {
    'JWTBCP': ('draft-ietf-oauth-rfc8725bis-10', os.path.join(METIN, 'JWTBCP.txt'), 'JWTBCP.txt'),
    'JOSECOMP': ('draft-ietf-jose-pq-composite-sigs-04', os.path.join(METIN, 'JOSECOMP.txt'), 'JOSECOMP.txt'),
    'LAMPSCOMP': ('draft-ietf-lamps-pq-composite-sigs-19', os.path.join(METIN, 'LAMPSCOMP.txt'), 'LAMPSCOMP.txt'),
    'RFC9964': ('RFC 9964', os.path.join(METIN, 'RFC9964.txt'), 'RFC9964.txt'),
    'RFC7515': ('RFC 7515', os.path.join(METIN, 'RFC7515.txt'), 'RFC7515.txt'),
    'RFC9864': ('RFC 9864', os.path.join(METIN, 'RFC9864.txt'), 'RFC9864.txt'),
    'RFC9901': ('RFC 9901', os.path.join(METIN, 'RFC9901.txt'), 'RFC9901.txt'),
    'SDJWTVC': ('draft-ietf-oauth-sd-jwt-vc-19', os.path.join(METIN, 'SDJWTVC.txt'), 'SDJWTVC.txt'),
    'SDJWTVC13': ('draft-ietf-oauth-sd-jwt-vc-13', os.path.join(METIN, 'SDJWTVC13.txt'), 'SDJWTVC13.txt'),
    'HAIP': ('OpenID4VC HAIP 1.0 Final', os.path.join(METIN, 'HAIP.txt'), 'HAIP.txt'),
    'OID4VP': ('OpenID4VP 1.0 Final', os.path.join(METIN, 'OID4VP.txt'), 'OID4VP.txt'),
    'RFC9449': ('RFC 9449', os.path.join(METIN, 'RFC9449.txt'), 'RFC9449.txt'),
    'TSL': ('draft-ietf-oauth-status-list-21', os.path.join(METIN, 'TSL.txt'), 'TSL.txt'),
    'ACM2': ('ECCG ACM v2.0', os.path.join(METIN, 'ACM2.txt'), 'ACM2.txt'),
    'OK': ('ON-KAYIT-TASLAK v0.8', OK_DOSYA, 'ON-KAYIT-TASLAK.md'),
}

# ---------------------------------------------------------------- madde kutuphanesi
# kimlik: (belge, bolum, matris-kimligi, birebir alinti, (ilk satir, son satir))
M = {
    # --- JWTBCP (8725bis-10)
    'J31-ALLOW': ('JWTBCP', '§3.1', 'T327', 'MUST NOT employ any algorithms outside this configured set', (463, 466)),
    'J31-KEY': ('JWTBCP', '§3.1', 'T329', 'consistent with the algorithm associated with the key identified by the corresponding identifier', (468, 471)),
    'J31-ISS': ('JWTBCP', '§3.1', 'T328', 'MUST determine which algorithms are permitted for itself and that issuer and ensure that the received JWT complies with those requirements', (482, 485)),
    'J31-ONE': ('JWTBCP', '§3.1', '', 'each key MUST be used with exactly one algorithm', (488, 489)),
    'J211': ('JWTBCP', '§2.11', '', 'reading algorithm values as if they were case-insensitive', (412, 413)),
    'J32-NONE': ('JWTBCP', '§3.2', '', 'JWT libraries MUST NOT consume JWTs using "none" unless explicitly allowed by the caller', (524, 525)),
    'J33': ('JWTBCP', '§3.3', '', 'the entire JWT MUST be rejected if any of them fail to validate', (565, 566)),
    # --- composite -04
    'C42-ORD': ('JOSECOMP', '§4.2', '', 'the two components MUST be in the same order as the components from the corresponding signing key', (334, 336)),
    'C42-CTX': ('JOSECOMP', '§4.2', '', "mldsaSig <- ML-DSA.Sign(mldsaSK, M', ctx=Label)", (389, 389)),
    'C42-0X00': ('JOSECOMP', '§4.2', '', "the byte 0x00 is appended in the message M' after the label to indicate the context has length 0", (439, 441)),
    'C42-PFX': ('JOSECOMP', '§4.2', '', 'used by a traditional verifier to detect if the composite signature has been stripped apart', (417, 419)),
    'C43-AND': ('JOSECOMP', '§4.3', 'T345', 'MUST validate a signature only if all component signatures were successfully validated', (452, 453)),
    'C43-DES': ('JOSECOMP', '§4.3', '', 'not of the correct type or length for the given component algorithm then output "Invalid signature"', (489, 489)),
    'C43-MP': ('JOSECOMP', '§4.3', '', "M' <- Prefix || Label || 0x00 || PH(M)", (493, 493)),
    'C43-VER': ('JOSECOMP', '§4.3', '', "if NOT ML-DSA.Verify(mldsaPK, M', ctx=Label)", (497, 497)),
    'C43-TRAD': ('JOSECOMP', '§4.3', '', "if NOT Trad.Verify(tradPK, M')", (499, 499)),
    'C44': ('JOSECOMP', '§4.4', '', 'Signature of the 1st Algorithm || Signature of the 2nd Algorithm', (517, 517)),
    'C45-DER': ('JOSECOMP', '§4.5', '', 'the DER-encoded Ecdsa-Sig-Value [RFC3279]', (555, 557)),
    'C451': ('JOSECOMP', '§4.5.1', '', 'Decoding simply reverses these two steps.', (606, 606)),
    'C51': ('JOSECOMP', '§5.1 Tablo 5', '', 'ML-DSA-65-ES256  |ML-DSA-65|ecdsa-with-SHA256|SHA512', (792, 792)),
    'C62': ('JOSECOMP', '§6.2', 'T057', 'MUST NOT use, import, or export component keys that are used in other contexts, combinations, or as standalone keys', (1045, 1047)),
    'C63': ('JOSECOMP', '§6.3', 'T347', 'signatures cannot be removed from the composite and used in other contexts', (1075, 1077)),
    'C64-EUF': ('JOSECOMP', '§6.4', '', 'existential unforgeability under chosen-message attack (EUF-CMA) is sufficient to meet the intended security goals', (1101, 1103)),
    'C712': ('JOSECOMP', '§7.1.2', '', 'ECDSA using P-256 curve and SHA-256', (1148, 1149)),
    'LC43': ('LAMPSCOMP', '§4.3', '', 'raising an error in the event that the input is malformed', (1300, 1301)),
    # --- RFC 9964
    'M3-ALG': ('RFC9964', '§3', 'T337', 'The alg JSON Web Key (JWK) parameter or COSE Key Common parameter is REQUIRED for all AKP keys.', (112, 113)),
    'M3-PRIV': ('RFC9964', '§3', '', 'The priv parameter contains private information and MUST NOT be present in public keys.', (114, 115)),
    'M5-CTX': ('RFC9964', '§5', 'T338', 'The ctx parameter MUST be the empty string', (219, 220)),
    # --- RFC 7515
    'R411': ('RFC7515', '§4.1.1', 'T319', 'The JWS Signature value is not valid if the "alg" value does not represent a supported algorithm or if there is not a key for use with that algorithm', (508, 510)),
    'R411-CS': ('RFC7515', '§4.1.1', '', 'The "alg" value is a case-sensitive ASCII string', (514, 515)),
    'R414': ('RFC7515', '§4.1.4', '', 'The "kid" (key ID) Header Parameter is a hint indicating which key was used to secure the JWS.', (551, 552)),
    'R416': ('RFC7515', '§4.1.6', 'T038', 'The recipient MUST validate the certificate chain according to RFC 5280', (596, 597)),
    'R4111-INV': ('RFC7515', '§4.1.11', 'T386', 'If any of the listed extension Header Parameters are not understood and supported by the recipient, then the JWS is invalid.', (702, 703)),
    'R4111-PROD': ('RFC7515', '§4.1.11', '', 'Producers MUST NOT include Header Parameter names defined by this specification or [JWA] for use with JWS', (703, 705)),
    'R4111-EMPTY': ('RFC7515', '§4.1.11', '', 'Producers MUST NOT use the empty list "[]" as the "crit" value.', (707, 708)),
    'R4111-MAY': ('RFC7515', '§4.1.11', '', 'Recipients MAY consider the JWS to be invalid', (708, 709)),
    'R4111-PROT': ('RFC7515', '§4.1.11', '', 'it MUST occur only within the JWS Protected Header', (712, 713)),
    'R4111-UND': ('RFC7515', '§4.1.11', '', 'This Header Parameter MUST be understood and processed by implementations.', (713, 714)),
    'R52-APP': ('RFC7515', '§5.2', 'T314', 'it is an application decision which of the JWS Signature values must successfully validate', (810, 812)),
    'R52-ONE': ('RFC7515', '§5.2', 'T315', 'at least one JWS Signature value MUST successfully validate, or the JWS MUST be considered invalid', (814, 816)),
    'R52-S4': ('RFC7515', '§5.2 (4)', '', 'MUST NOT occur in distinct JSON object values that together comprise the JOSE Header', (855, 857)),
    'R52-S5': ('RFC7515', '§5.2 (5)', '', 'Verify that the implementation understands and can process all fields that it is required to support', (859, 860)),
    'R52-S8': ('RFC7515', '§5.2 (8)', '', 'Validate the JWS Signature against the JWS Signing Input', (873, 873)),
    'R52-S9': ('RFC7515', '§5.2 (9)', '', 'repeat this process (steps 4-8) for each digital signature or MAC value', (881, 882)),
    'R6': ('RFC7515', '§6', 'T040', 'MUST be integrity protected if the information that they convey is to be utilized in a trust decision', (946, 948)),
    'R721-DIS': ('RFC7515', '§7.2.1', '', 'The Header Parameter names in the two locations MUST be disjoint.', (1068, 1069)),
    # --- RFC 9864
    'F4111': ('RFC9864', '§4.1.1', '', 'EdDSA using the Ed25519 parameter set', (344, 344)),
    'F412': ('RFC9864', '§4.1.2', '', 'JOSE Implementation Requirements:  Deprecated', (369, 369)),
    'F7': ('RFC9864', '§7', 'T335', 'A cryptographic key MUST be used with only a single algorithm', (650, 650)),
    # --- RFC 9901
    'S41': ('RFC9901', '§4.1', 'T102', 'It MUST NOT use the none algorithm.', (486, 487)),
    'S71-2A': ('RFC9901', '§7.1 (2a)', 'T103', 'The "none" algorithm MUST NOT be accepted.', (1665, 1665)),
    'S71-2B': ('RFC9901', '§7.1 (2b)', '', 'Validate the signature over the Issuer-signed JWT per Section 5.2 of [RFC7515].', (1667, 1668)),
    'S73-5B': ('RFC9901', '§7.3 (5b)', 'T213', 'Ensure that a signing algorithm was used that was deemed secure for the application.', (1849, 1850)),
    'S73-5G': ('RFC9901', '§7.3 (5g)', '', 'verify that it matches the value of the sd_hash claim in the Key Binding JWT', (1868, 1870)),
    'S81': ('RFC9901', '§8.1', '', 'concatenating the protected header, the payload, and the signature of the JWS JSON serialized SD-JWT', (1906, 1907)),
    'S83': ('RFC9901', '§8.3', 'T108', 'disclosures and kb_jwt MUST be included in the first unprotected header', (1987, 1988)),
    'S91': ('RFC9901', '§9.1', 'T107', 'The Issuer-signed JWT MUST be rejected if the signature cannot be verified.', (2081, 2083)),
    'S911': ('RFC9901', '§9.11', '', 'and that Verifiers check this value', (2318, 2319)),
    # --- SD-JWT VC -19 / -13
    'V19-22': ('SDJWTVC', '§2.2', 'T113', 'not precluded but the specific details are beyond the scope of this specification', (307, 309)),
    'V19-221': ('SDJWTVC', '§2.2.1', 'T119', 'The typ value MUST use dc+sd-jwt.', (328, 329)),
    'V19-CL': ('SDJWTVC', 'Doc. History (-19)', '', 'Remove: "Note that this draft used vc+sd-jwt as the value of', (3614, 3615)),
    'V13-32': ('SDJWTVC13', '§3.2', 'T114', 'where support for the JWS JSON Serialization is OPTIONAL', (303, 304)),
    'V13-321M': ('SDJWTVC13', '§3.2.1', '', 'The typ value MUST use dc+sd-jwt.', (323, 324)),
    'V13-321R': ('SDJWTVC13', '§3.2.1', '', 'it is RECOMMENDED that Verifiers and Holders accept both vc+sd-jwt and dc+sd-jwt as the value of the typ header', (340, 342)),
    'V13-35A': ('SDJWTVC13', '§3.5', '', 'When the protected header of the Issuer-signed JWT contains the x5c parameter', (748, 750)),
    'V13-35B': ('SDJWTVC13', '§3.5', '', 'using a permitted Issuer Signature Mechanism, the SD-JWT VC MUST be rejected', (763, 764)),
    # --- HAIP 1.0
    'H4-DPOP': ('HAIP', '§4', 'T374', 'Sender-constrained access token: MUST support DPoP as defined in [RFC9449].', (278, 278)),
    'H5': ('HAIP', '§5', 'T241', 'the Wallet MUST accept the Client Identifier Prefix x509_hash', (382, 382)),
    'H52': ('HAIP', '§5.2', 'T281', 'The Wallet MUST support unsigned, signed, and multi-signed requests', (426, 426)),
    'H52N': ('HAIP', '§5.2', 'T282', 'unsigned requests depend on the origin information provided by the platform and the web PKI', (428, 428)),
    'H61-JSON': ('HAIP', '§6.1', 'T115', 'Compact serialization MUST be supported as defined in [RFC9901]. JSON serialization MAY be supported.', (468, 468)),
    'H61-TSL': ('HAIP', '§6.1', 'T167', 'MUST be included in the x5c JOSE header of the Token', (476, 476)),
    'H611': ('HAIP', '§6.1.1', 'T042', "MUST contain the credential issuer's signing certificate along with a trust chain in the x5c JOSE header parameter", (490, 490)),
    'H611-TA': ('HAIP', '§6.1.1', '', 'The X.509 certificate of the trust anchor MUST NOT be included in the x5c JOSE header of the SD-JWT VC.', (490, 490)),
    'H7': ('HAIP', '§7', 'T122', 'MUST, at a minimum, support ECDSA with P-256 and SHA-256', (498, 498)),
    # --- OID4VP 1.0
    'O5-TYP': ('OID4VP', '§5', 'T293', 'Wallets MUST NOT process Request Objects where the typ Header Parameter is not present or does not have the value oauth-authz-req+jwt.', (605, 605)),
    'O592': ('OID4VP', '§5.9.2', '', 'the Wallet MUST treat the Client Identifier as referencing a pre-registered client', (882, 882)),
    'O593-DC': ('OID4VP', '§5.9.3', 'T268', 'it is at the discretion of the Wallet whether it validates the signature on the Request Object', (894, 894)),
    'O593-HASH': ('OID4VP', '§5.9.3 (x509_hash)', 'T240', 'The Wallet MUST validate the signature and the trust chain of the X.509 leaf certificate.', (947, 947)),
    'OA1': ('OID4VP', 'A.1', 'T278', 'signed requests, as defined in Appendix A.3.2.1, MUST use signed', (2456, 2456)),
    'OA2': ('OID4VP', 'A.2', 'T279', 'The Wallet MUST ignore any client_id parameter that is present in an unsigned request.', (2500, 2500)),
    'OA322': ('OID4VP', 'A.3.2.2', 'T269', 'allows the Verifier to use multiple Client Identifiers and corresponding key material to protect the same request', (2572, 2572)),
    # --- RFC 9449
    'D42-JWK': ('RFC9449', '§4.2', '', 'It MUST NOT contain a private key.', (409, 409)),
    'D43-5': ('RFC9449', '§4.3 (5)', 'T378', 'is supported by the application, and is acceptable per local policy', (496, 498)),
    'D43-6': ('RFC9449', '§4.3 (6)', 'T379', 'The JWT signature verifies with the public key contained in the jwk JOSE Header Parameter.', (499, 500)),
    'D43-7': ('RFC9449', '§4.3 (7)', '', 'The jwk JOSE Header Parameter does not contain a private key.', (501, 501)),
    'D43-10': ('RFC9449', '§4.3 (10)', '', 'If the server provided a nonce value to the client, the nonce claim matches the server-provided nonce value.', (506, 507)),
    'D43-12': ('RFC9449', '§4.3 (12)', '', 'If presented to a protected resource in conjunction with an access token,', (511, 512)),
    # --- TSL
    'T51': ('TSL', '§5.1', 'T145', 'Relying Parties MUST reject JWTs with an invalid signature.', (788, 789)),
    # --- ACM2
    'A51': ('ACM2', 'Note 51', 'T135', 'the veriﬁcation function accepting if and only if all signatures are correct', (946, 946)),
    # --- On kayit (ÖK) -- politika ve hedef tanimlari
    'OK65': ('OK', '§6.5', '', 'İhraççı başına gerekli küme R = {X}, izinli küme {A, X}.', (1054, 1054)),
    'OK413': ('OK', '§4.13 L4', '', 'Yapılandırılmış hâlde K1 KABUL, K2 RED, K3 RED', (844, 844)),
    'OK2B6C': ('OK', '§2B m.6 (L4c)', '', 'Göç etmiş ihraççının yalnız klasik imzalı belgesi reddedilir, eski ihraççının klasik imzalı belgesi kabul edilir.', (256, 256)),
    'OK47': ('OK', '§4.7 G5', '', 'Göç etmiş bir varlık, ilan ettiği eski-sürüm penceresi dışında yalnız klasik kanıtla kabul edilemez.', (767, 767)),
    'OK48-P0': ('OK', '§4.8 P0', '', 'En az bir imza geçerliyse kabul', (775, 775)),
    'OK48-P1': ('OK', '§4.8 P1', '', 'Mevcut imzaların tümü geçerliyse kabul. İmza silinmesi (soyma) fark edilmez', (776, 776)),
    'OK48-P2': ('OK', '§4.8 P2', '', 'P1 + her imza, anahtarının bağlı olduğu algoritmayla doğrulanır', (777, 777)),
    'OK2D1A': ('OK', '§2D m.1', '', 'zincir davranışı yalnız X5C vektörlerinde, klasik ve ML-DSA zincirleriyle ölçülür', (395, 395)),
    'OK2D1B': ('OK', '§2D m.1', '', 'Composite X.509 kapsam dışıdır', (396, 396)),
    'OK2D2': ('OK', '§2D m.2', '', 'Yedeğin kullanılması Y_L4 tanımını değiştirmez.', (401, 401)),
    'OK2D4': ('OK', '§2D m.4', '', 'hangi imzayı bağladığı tanımsızdır', (412, 412)),
    'OK2D7': ('OK', '§2D m.7', '', 'senaryo (d) vektörleri (JSON serileştirmenin statüsü)', (423, 423)),
    'OK2F4': ('OK', '§2F m.4', '', 'Oracle kararı (bayrak B2) değişmez.', (555, 555)),
    'OK415': ('OK', '§4.15', '', 'tek geçerli klasik imza → KABUL', (881, 881)),
    'OK65-K1': ('OK', '§6.5 K1', '', 'Çift imza (A + X), ikisi geçerli | KABUL', (1058, 1058)),
    'OK65-K2': ('OK', '§6.5 K2', '', 'X imzası bozuk | RED', (1059, 1059)),
    'OK65-K3': ('OK', '§6.5 K3', '', 'X soyulmuş (yalnız A) | RED', (1060, 1060)),
    'OK65-K4': ('OK', '§6.5 K4', '', 'Yalnız X | KABUL', (1061, 1061)),
    'OK65-K5': ('OK', '§6.5 K5', '', 'Politikaya göre (MR2); bayrak B1', (1062, 1062)),
    'OK65-K6': ('OK', '§6.5 K6', '', 'Composite tek imza, geçerli (desteklenen hedeflerde) | KABUL', (1063, 1063)),
    'OK65-K7': ('OK', '§6.5 K7', '', 'Composite etiketli, bileşeni bozuk | RED', (1064, 1064)),
    'OK65-K8': ('OK', '§6.5 K8', '', 'Bayrak B2', (1065, 1065)),
    'OK65-K9': ('OK', '§6.5 K9', '', 'Bayrak B3', (1066, 1066)),
    'OK65-K10': ('OK', '§6.5 K10', '', 'RED (L2/L3)', (1067, 1067)),
    'OK65-K11': ('OK', '§6.5 K11', '', 'göç etmiş ihraççıdan yalnız klasik kimlik bilgisi | RED (G5)', (1068, 1068)),
    'OK65-V': ('OK', '§6.5 V+/V−', '', 'Adaptör geçerlilik kontrolleri | KABUL / RED', (1069, 1069)),
}

_ONBELLEK = {}


def _satirlar(belge):
    if belge not in _ONBELLEK:
        with open(BELGE[belge][1], encoding='utf-8') as f:
            _ONBELLEK[belge] = f.read().split('\n')  # grep/sed ile ayni satir numaralamasi
    return _ONBELLEK[belge]


def _norm(s):
    # satir sonundaki tire (RFC metinlerinde gercek tire: case-/sensitive, ML-DSA-/65) bosluksuz birlestirilir
    s = re.sub(r'-\n[ \t]*', '-', s)
    return re.sub(r'\s+', ' ', s).strip()


def alinti_denetimi():
    hatalar = []
    for k, (belge, bolum, t, alinti, (a, b)) in M.items():
        sat = _satirlar(belge)
        parca = _norm('\n'.join(sat[a - 1:b]))
        if _norm(alinti) not in parca:
            hatalar.append(f'{k}: "{alinti}" {belge}:{a}-{b} icinde yok')
    if hatalar:
        print('ALINTI DENETIMI BASARISIZ:', file=sys.stderr)
        for h in hatalar:
            print('  ' + h, file=sys.stderr)
        sys.exit(2)
    return len(M)


def madde(k):
    belge, bolum, t, alinti, (a, b) = M[k]
    surum, _, kisa = BELGE[belge]
    ad = 'ÖK' if belge == 'OK' else belge
    tt = f' [{t}]' if t else ''
    sat = f'{a}' if a == b else f'{a}-{b}'
    return f'{ad} {bolum}{tt} “{alinti}” ({surum}; {kisa}:{sat})'


def dayanak(kimlikler):
    gor = []
    for k in kimlikler:
        if k not in gor:
            gor.append(k)
    return ' ; '.join(madde(k) for k in gor)


# ---------------------------------------------------------------- kollar
KOLLAR = ['kontrol-EdDSA', 'kontrol-Ed25519', 'tedavi-ML-DSA-65', 'tedavi-composite']
X = {'kontrol-EdDSA': 'EdDSA', 'kontrol-Ed25519': 'Ed25519',
     'tedavi-ML-DSA-65': 'ML-DSA-65', 'tedavi-composite': 'ML-DSA-65-ES256'}
PQ = {'ML-DSA-44', 'ML-DSA-65', 'ML-DSA-87', 'ML-DSA-65-ES256', 'ML-DSA-65-Ed25519'}
COKLU_KOL = {'ortak', 'klasik-taban', 'kapsam-pq', 'kapsam-hibrit', None}
EK_KOL = {  # BATARYA-ESLEME kaynakli ek atamalar
    'X5C04_karisik_pq_yaprak_klasik_ara': ['tedavi-composite'],
    'X5C07_korumasiz_x5c': ['tedavi-composite'],
    'K10K_alg-ES256_anahtar-Ed25519': ['kontrol-Ed25519'],
    'VC10_ikili_ihrac': ['kontrol-EdDSA', 'kontrol-Ed25519', 'tedavi-composite'],
}

# ---------------------------------------------------------------- roller (BATARYA-ESLEME.md §1-§2)
# (vektor, kol) -> (rol metni, birincil_mi)
ROL = {}


def rol(vid, kollar, metin, birincil):
    for k in kollar:
        onceki = ROL.get((vid, k))
        if onceki:
            m, b = onceki
            ROL[(vid, k)] = (m + ' + ' + metin, b or birincil)
        else:
            ROL[(vid, k)] = (metin, birincil)


KE, K25, P, C = KOLLAR
TUM = KOLLAR
# K1
rol('T1K_both_valid', [KE], 'K1 birincil', True)
rol('T1K_both_valid-ED25519', [K25], 'K1 birincil (yedek etiket)', True)
rol('T1P_both_valid', [P], 'K1 birincil', True)
rol('T1C_both_valid', [C], 'K1 birincil', True)
rol('VC09_GJ_ES256_EdDSA', [KE], 'K1 ikincil (SD-JWT VC, senaryo d); MR3 (-13↔-19)', False)
rol('VC09_GJ_ES256_EdDSA-ED25519', [K25], 'K1 ikincil (yedek etiket); MR3', False)
rol('VC07_GJ_ES256_MLDSA65', [P], 'K1 ikincil (SD-JWT VC, senaryo d); MR3 (-13↔-19)', False)
rol('VC08_GJ_ES256_composite', [C], 'K1 ikincil (SD-JWT VC, senaryo d); MR3 (-13↔-19)', False)
# K2
rol('T2K_second_tampered', [KE], 'K2 birincil', True)
rol('T2K_second_tampered-ED25519', [K25], 'K2 birincil (yedek etiket)', True)
rol('T2P_second_tampered', [P], 'K2 birincil', True)
rol('T2C_second_tampered', [C], 'K2 birincil', True)
# K3
rol('T3_stripped_to_ES256', TUM, 'K3 birincil (üç kolda ortak dosya; R={X} kola göre)', True)
rol('VP06_GJ_pq_soyuldu_kb_gecerli', [P], 'K3 ikincil (SD-JWT sunumu, KB tanımlayıcı, ÖK §2D m.4); MR1 (VP05↔VP06)', False)
# K4
rol('T5K_only_EdDSA', [KE], 'K4 birincil', True)
rol('T5K_only_EdDSA-ED25519', [K25], 'K4 birincil (yedek etiket)', True)
rol('T5P_only_ML-DSA-65', [P], 'K4 birincil', True)
rol('T5C_only_ML-DSA-65-ES256', [C], 'K4 birincil; K6 ikincil (General JSON)', True)
# K5
rol('T7K_plus_kayitsiz', [KE], 'K5 birincil (X-KAYITSIZ-1); MR2 (T1↔T7)', True)
rol('T7K_plus_kayitsiz-ED25519', [K25], 'K5 birincil (yedek etiket); MR2', True)
rol('T7P_plus_kayitsiz', [P], 'K5 birincil; MR2 (T1↔T7)', True)
rol('T7C_plus_kayitsiz', [C], 'K5 birincil; MR2 (T1↔T7)', True)
rol('T4K_plus_ML-DSA-65', [KE], 'K5 ikincil (ek imza gerçek alg); MR2 ikincil', False)
rol('T4K_plus_ML-DSA-65-ED25519', [K25], 'K5 ikincil (yedek etiket)', False)
rol('T6_plus_composite', [KE], 'K5 ikincil (ek composite imza); MR2 ikincil', False)
rol('T6_plus_composite-ED25519', [K25], 'K5 ikincil (yedek etiket)', False)
rol('T4P_plus_ML-DSA-65-ES256', [P], 'K5 ikincil; MR2 ikincil', False)
rol('UNK04_general_arti_kayitsiz_composite', [P], 'K5 ikincil (kayıtsız composite adı, geçerli bayt)', False)
rol('UNK05_general_arti_alg_none', [P], 'K5 ikincil (alg=none ek imza)', False)
rol('T4C_plus_ML-DSA-65', [C], 'K5 ikincil; MR2 ikincil', False)
# K6
rol('CMP00_gecerli_referans', [C], 'K6 birincil; V+ birincil (composite kolu)', True)
rol('VC03_composite_kid', [C], 'K6 ikincil (SD-JWT VC, kid)', False)
# K7
rol('CMP01_ml_bileseni_bozuk', [C], 'K7 birincil; V− birincil (composite kolu)', True)
rol('CMP02_ecdsa_bileseni_bozuk', [C], 'K7 birincil', True)
for v in ['CMP03_ecdsa_der_uzunluk_bozuk', 'CMP04_ecdsa_ham_rs', 'CMP05_ecdsa_asgari_olmayan_der', 'CMP06_sonda_artik_bayt',
          'CMP07_yalniz_ml_bileseni', 'CMP08_bilesenler_farkli_iletilerden', 'CMP09_ml_bileseni_ctx_bos', 'CMP10_onozet_sha256',
          'CMP11_bos_ctx_uzunlugu_yok', 'CMP16_bilesen_sirasi_ters']:
    rol(v, [C], 'K7 ikincil (serileştirme / uygulayıcı hatası taklidi)', False)
# K8
rol('X5C04_karisik_pq_yaprak_klasik_ara', [P], 'K8 birincil (bayrak B2; UYARLANMIŞ: yaprak ML-DSA-65, ÖK §2F m.4)', True)
rol('X5C04_karisik_pq_yaprak_klasik_ara', [C], 'K8 birincil (composite sütunu; UYARLANMIŞ: yaprak composite değil ML-DSA-65)', True)
rol('X5C03_karisik_klasik_yaprak_pq_ara', [P], 'K8 ikincil (klasik yaprak + PQ ara)', False)
rol('X5C05_karisik_pq_ara_klasik_kok', [P], 'K8 ikincil (PQ ara + klasik kök)', False)
# K9
rol('X5C07_korumasiz_x5c', [P], 'K9 birincil (bayrak B3)', True)
rol('X5C07_korumasiz_x5c', [C], 'K9 birincil (composite sütunu; UYARLANMIŞ: ML-DSA-65 yaprak)', True)
rol('X5C08_korumasiz_x5c_zincir_degisimi', [P], 'K9 ikincil (korumasız x5c zincir ikamesi)', False)
rol('X5C09_korumali_ve_korumasiz_x5c', [P], 'K9 ikincil (x5c hem korumalı hem korumasız)', False)
# K10
rol('K10K_alg-EdDSA_anahtar-ES256', [KE], 'K10 birincil', True)
rol('K10K_alg-EdDSA_anahtar-ES256-ED25519', [K25], 'K10 birincil (yedek etiket)', True)
rol('K10K_alg-ES256_anahtar-Ed25519', [KE, K25], 'K10 birincil (ikinci yön; yedek kolda da aynı dosya)', True)
rol('K10P_alg-ML-DSA-65_anahtar-ES256', [P], 'K10 birincil', True)
rol('K10P_alg-ES256_anahtar-ML-DSA-65', [P], 'K10 birincil (ikinci yön)', True)
rol('K10C_alg-ML-DSA-65-ES256_anahtar-ML-DSA-65', [C], 'K10 birincil', True)
rol('K10C_alg-ML-DSA-65_anahtar-ML-DSA-65-ES256', [C], 'K10 birincil (ikinci yön)', True)
rol('CMP12_ayrilabilirlik_ecdsa_ES256', [C], 'K10 ikincil (bileşen anahtarı bağımsız anahtar olarak)', False)
rol('CMP13_ayrilabilirlik_ml_MLDSA65', [C], 'K10 ikincil (bileşen anahtarı bağımsız anahtar olarak)', False)
# K11
rol('VC10_ikili_ihrac', TUM, 'K11 birincil (credentials[0] = ES256 kopya değerlendirilir)', True)
rol('VC01_ES256_x5c', TUM, 'K11 ikincil; MR3 (VC01↔VC11)', False)
# V+ / V-
rol('VPLUS_ES256', TUM, 'V+ birincil (üç kolda ortak)', True)
rol('VMINUS_ES256', TUM, 'V− birincil (üç kolda ortak)', True)
rol('VPLUS_EdDSA', [KE], 'V+ birincil', True)
rol('VPLUS_EdDSA-ED25519', [K25], 'V+ birincil (yedek etiket)', True)
rol('VMINUS_EdDSA', [KE], 'V− birincil', True)
rol('VMINUS_EdDSA-ED25519', [K25], 'V− birincil (yedek etiket)', True)
rol('VPLUS_ML-DSA-65', [P], 'V+ birincil', True)
rol('VMINUS_ML-DSA-65', [P], 'V− birincil', True)
# MR-yalniz
rol('VP05_GJ_ES256_MLDSA65_kb', [P], 'MR1 eşi (VP05↔VP06, tanımlayıcı KB)', False)
rol('REQ04_coklu_imzali', [P], 'MR1 eşi (REQ04↔REQ05, senaryo c, cüzdan tarafı)', False)
rol('REQ05_coklu_imzali_pq_soyuldu', [P], 'MR1 eşi (REQ04↔REQ05, senaryo c, cüzdan tarafı)', False)
rol('VC11_typ_vc+sd-jwt', TUM, 'MR3 eşi (VC01↔VC11; -13 geçişi)', False)
rol('VP05_GJ_ES256_MLDSA65_kb-SIRA-ters', [P], 'MR4 DIŞI tanımlayıcı (sd_hash bağlaması değişir)', False)

# ---------------------------------------------------------------- imza durumlari (insa != 'gecerli' olanlar)
# (vektor, sira) -> (durum, kisa neden). durum: G gecerli bayt, B gecersiz, K alg-anahtar uyusmaz, U belirlenemez
D = {}


def d(vid, sira, durum, neden):
    D[(vid, sira)] = (durum, neden)


for v in ['T2K_second_tampered', 'T2K_second_tampered-ED25519', 'T2P_second_tampered']:
    d(v, 1, 'B', 'ikinci imzada bayt 5 bit 0 çevrildi')
d('T2C_second_tampered', 1, 'B', 'composite imzanın ML-DSA bileşeninde bayt 5 bozuk')
for v in ['T2K_second_tampered-SIRA-ters', 'T2K_second_tampered-SIRA-ters-ED25519', 'T2P_second_tampered-SIRA-ters']:
    d(v, 0, 'B', 'bozuk imza (permütasyonla 0. sırada)')
d('T2C_second_tampered-SIRA-ters', 0, 'B', 'bozuk composite (permütasyonla 0. sırada)')
for v, s in [('T7K_plus_kayitsiz', 2), ('T7K_plus_kayitsiz-ED25519', 2), ('T7K_plus_kayitsiz-SIRA-kayitsiz-once', 0),
             ('T7K_plus_kayitsiz-SIRA-kayitsiz-once-ED25519', 0), ('T7K_plus_kayitsiz-SIRA-ters', 0),
             ('T7K_plus_kayitsiz-SIRA-ters-ED25519', 0), ('T7P_plus_kayitsiz', 2), ('T7P_plus_kayitsiz-SIRA-kayitsiz-once', 0),
             ('T7P_plus_kayitsiz-SIRA-ters', 0), ('T7C_plus_kayitsiz', 2), ('T7C_plus_kayitsiz-SIRA-kayitsiz-once', 0),
             ('T7C_plus_kayitsiz-SIRA-ters', 0)]:
    d(v, s, 'B', 'X-KAYITSIZ-1: rastgele 128 B, anahtar yok')
d('UNK01_alg_ML-DSA-66', 0, 'G', 'bayt geçerli ML-DSA-65; etiket ML-DSA-66 kayıtsız')
d('UNK02_alg_ML-DSA-65-P256', 0, 'G', 'bayt geçerli composite; etiket ML-DSA-65-P256 kayıtsız')
d('UNK03_alg_kucuk_harf', 0, 'G', 'bayt geçerli; etiket küçük harf ml-dsa-65')
d('UNK04_general_arti_kayitsiz_composite', 2, 'G', 'bayt geçerli composite; etiket kayıtsız')
d('UNK05_general_arti_alg_none', 2, 'B', 'alg=none, boş imza')
d('CMP01_ml_bileseni_bozuk', 0, 'B', 'ML-DSA bileşeni bozuk (ECDSA geçerli)')
d('CMP02_ecdsa_bileseni_bozuk', 0, 'B', 'ECDSA bileşeni bozuk (ML-DSA geçerli)')
d('CMP03_ecdsa_der_uzunluk_bozuk', 0, 'B', 'ECDSA DER uzunluk baytı bozuk')
d('CMP04_ecdsa_ham_rs', 0, 'B', 'ECDSA bileşeni ham r||s (DER değil)')
d('CMP05_ecdsa_asgari_olmayan_der', 0, 'U', 'asgari olmayan DER; sayısal değerler geçerli')
d('CMP06_sonda_artik_bayt', 0, 'B', 'geçerli imza + sonda artık 0x00')
d('CMP07_yalniz_ml_bileseni', 0, 'B', 'ECDSA bileşeni yok')
d('CMP08_bilesenler_farkli_iletilerden', 0, 'B', 'ML-DSA bileşeni başka iletinin')
d('CMP09_ml_bileseni_ctx_bos', 0, 'B', 'ML-DSA bileşeni boş ctx ile')
d('CMP10_onozet_sha256', 0, 'B', "iki bileşen SHA-256 ön-özetli M' üzerinde")
d('CMP11_bos_ctx_uzunlugu_yok', 0, 'B', "M' içinde 0x00 yok")
d('CMP12_ayrilabilirlik_ecdsa_ES256', 0, 'B', "ECDSA bileşeni M' üzerinde; JWS imzalama girdisi üzerinde değil")
d('CMP13_ayrilabilirlik_ml_MLDSA65', 0, 'B', "ML-DSA bileşeni M' ve ctx=Label üzerinde")
d('CMP14_ed25519_ml_bileseni_bozuk', 0, 'B', 'ML-DSA bileşeni bozuk')
d('CMP15_ed25519_eddsa_bileseni_bozuk', 0, 'B', 'Ed25519 bileşeni bozuk')
d('CMP16_bilesen_sirasi_ters', 0, 'B', 'bileşen sırası ters (tradSig || mldsaSig)')
for v in ['K10K_alg-EdDSA_anahtar-ES256', 'K10K_alg-EdDSA_anahtar-ES256-ED25519', 'K10K_alg-ES256_anahtar-Ed25519',
          'K10P_alg-ML-DSA-65_anahtar-ES256', 'K10P_alg-ES256_anahtar-ML-DSA-65', 'K10C_alg-ML-DSA-65-ES256_anahtar-ML-DSA-65',
          'K10C_alg-ML-DSA-65_anahtar-ML-DSA-65-ES256']:
    d(v, 0, 'K', 'başlık alg ≠ anahtarın algoritması (imza gerçek anahtar alg ile)')
d('X5C10_x5c_ve_baska_anahtar_kid', 0, 'G', 'x5c yaprağıyla geçerli; kid ES256 anahtarını gösteriyor')
d('REQ07_coklu_imzali_pq_bozuk', 1, 'B', 'ML-DSA-65 imzasında bayt 5 bozuk')
d('REQ10_istek_alg_none', 0, 'B', 'alg=none, boş imza')
d('VC12_alg_none', 0, 'B', 'alg=none, boş imza')
for v in ['VMINUS_ES256', 'VMINUS_EdDSA', 'VMINUS_EdDSA-ED25519']:
    d(v, 0, 'B', 'bayt 32 bit 0 çevrildi')
d('VMINUS_ML-DSA-65', 0, 'B', 'bayt 1654 bit 0 çevrildi')

# ---------------------------------------------------------------- ozel kurallar
SURUM_BOLUNEN = {
    'VC07_GJ_ES256_MLDSA65', 'VC08_GJ_ES256_composite', 'VC09_GJ_ES256_EdDSA', 'VC09_GJ_ES256_EdDSA-ED25519',
    'VC07_GJ_ES256_MLDSA65-SIRA-ters', 'VC08_GJ_ES256_composite-SIRA-ters', 'VC09_GJ_ES256_EdDSA-SIRA-ters',
    'VC09_GJ_ES256_EdDSA-SIRA-ters-ED25519', 'VP05_GJ_ES256_MLDSA65_kb', 'VP06_GJ_pq_soyuldu_kb_gecerli',
    'VP07_GJ_sd_hash_ikinci_imza', 'VP05_GJ_ES256_MLDSA65_kb-SIRA-ters', 'VC11_typ_vc+sd-jwt',
}
VP_SDHASH = {'VP05_GJ_ES256_MLDSA65_kb', 'VP07_GJ_sd_hash_ikinci_imza', 'VP05_GJ_ES256_MLDSA65_kb-SIRA-ters'}
CMP_MADDE = {
    'CMP01_ml_bileseni_bozuk': ['C43-VER', 'C43-AND'],
    'CMP02_ecdsa_bileseni_bozuk': ['C43-TRAD', 'C43-AND'],
    'CMP03_ecdsa_der_uzunluk_bozuk': ['C43-DES', 'C45-DER', 'LC43'],
    'CMP04_ecdsa_ham_rs': ['C45-DER', 'C43-DES', 'LC43'],
    'CMP06_sonda_artik_bayt': ['C43-DES', 'LC43'],
    'CMP07_yalniz_ml_bileseni': ['C43-DES', 'C43-AND'],
    'CMP08_bilesenler_farkli_iletilerden': ['C43-VER', 'C43-AND'],
    'CMP09_ml_bileseni_ctx_bos': ['C43-VER', 'C42-CTX'],
    'CMP10_onozet_sha256': ['C51', 'C43-MP'],
    'CMP11_bos_ctx_uzunlugu_yok': ['C43-MP', 'C42-0X00'],
    'CMP12_ayrilabilirlik_ecdsa_ES256': ['R52-S8', 'C63', 'C62', 'C42-PFX'],
    'CMP13_ayrilabilirlik_ml_MLDSA65': ['R52-S8', 'M5-CTX', 'C63', 'C62'],
    'CMP14_ed25519_ml_bileseni_bozuk': ['C43-AND'],
    'CMP15_ed25519_eddsa_bileseni_bozuk': ['C43-AND'],
    'CMP16_bilesen_sirasi_ters': ['C42-ORD', 'C44'],
    'T2C_second_tampered': ['C43-AND'],
    'T2C_second_tampered-SIRA-ters': ['C43-AND'],
}

# ---------------------------------------------------------------- manifest
with open(MANIFEST, encoding='utf-8') as f:
    MAN = json.load(f)
VEK = MAN['vektorler']
VID = [v['id'] for v in VEK]
assert len(VID) == 153 and len(set(VID)) == 153


def imzalar(v):
    ins = v['insa'] or {}
    if 'imzalar' in ins:
        return [(s['alg'], s.get('insa', ''), s['sira']) for s in ins['imzalar']]
    if 'kimlik_bilgileri' in ins:  # VC10: yalniz credentials[0] (ES256 kopya) degerlendirilir
        s = ins['kimlik_bilgileri'][0]
        return [(s['alg'], s.get('insa', ''), 0)]
    return []


def capraz_denetim():
    sorun = []
    for v in VEK:
        for alg, ins, sira in imzalar(v):
            if ins != 'gecerli' and (v['id'], sira) not in D:
                sorun.append(f"{v['id']}#{sira} insa='{ins}' icin elle durum yok")
            if ins == 'gecerli' and (v['id'], sira) in D and D[(v['id'], sira)][0] != 'G':
                sorun.append(f"{v['id']}#{sira} insa gecerli ama elle durum gecersiz")
    for (vid, sira) in D:
        if vid not in VID:
            sorun.append(f'{vid} manifestte yok')
    for (vid, k) in ROL:
        if vid not in VID:
            sorun.append(f'rol: {vid} manifestte yok')
    for vid in list(SURUM_BOLUNEN) + list(VP_SDHASH) + list(CMP_MADDE) + list(EK_KOL):
        if vid not in VID:
            sorun.append(f'ozel: {vid} manifestte yok')
    if sorun:
        print('CAPRAZ DENETIM BASARISIZ:', *sorun, sep='\n  ', file=sys.stderr)
        sys.exit(3)


# ---------------------------------------------------------------- karar motoru
def durum(v, alg, ins, sira):
    if (v['id'], sira) in D:
        return D[(v['id'], sira)]
    return ('G', 'geçerli')


def genel(v, kol, cfg):
    """P0 / P2 / L4 kurali. Donus: (karar, madde listesi, gerekce metni)."""
    izinli = {'ES256', X[kol]}
    R = {X[kol]} if cfg == 'L4' else set()
    sig = imzalar(v)
    durumlar = []
    for alg, ins, sira in sig:
        dd, neden = durum(v, alg, ins, sira)
        if alg not in izinli:
            st = 'IZINSIZ'
        elif dd == 'G':
            st = 'GECERLI'
        elif dd == 'K':
            st = 'ANAHTAR'
        elif dd == 'U':
            st = 'BELIRSIZ'
        else:
            st = 'GECERSIZ'
        durumlar.append((alg, st, neden))
    gecerli = [a for a, st, _ in durumlar if st == 'GECERLI']
    belirsiz = [a for a, st, _ in durumlar if st == 'BELIRSIZ']
    kotu = [(a, st, n) for a, st, n in durumlar if st in ('IZINSIZ', 'ANAHTAR', 'GECERSIZ')]
    sinif = 'accept-hybrid' if any(a in PQ for a in gecerli) else 'accept-classical'
    ETK = {"GECERLI": "geçerli", "IZINSIZ": "izinsiz", "ANAHTAR": "alg–anahtar uyuşmaz", "BELIRSIZ": "belirlenemez", "GECERSIZ": "geçersiz"}
    parcalar = []
    for (a, st, n), (_, _, sira) in zip(durumlar, sig):
        p = f'{a}={ETK[st]}'
        if st != 'GECERLI' and (v['id'], sira) in D:
            p += f' ({n})'
        parcalar.append(p)
    ozet = ', '.join(parcalar)
    neden_md = []
    for a, st, n in kotu:
        if st == 'IZINSIZ':
            neden_md += ['J31-ALLOW', 'R411']
        elif st == 'ANAHTAR':
            neden_md += ['J31-KEY', 'R411', 'F7']
        else:
            neden_md += ['R52-S8']
    if cfg == 'P0':
        if gecerli:
            return sinif, ['R52-ONE', 'R52-APP', 'OK48-P0'], f'P0: en az bir izinli imza geçerli [{ozet}]'
        if belirsiz:
            return 'indeterminate', ['R52-ONE'], f'P0: tek aday imzanın geçerliliği belirlenemiyor [{ozet}]'
        return 'reject', ['R52-ONE'] + neden_md, f'P0: geçerli izinli imza yok [{ozet}]'
    # P2 / L4: mevcut her imza gecerli olmali
    if not sig:
        return 'reject', ['R52-ONE'], 'imza yok'
    if kotu:
        md = neden_md + ['OK48-P1', 'A51']
        if cfg == 'L4':
            md += ['OK65']
        return 'reject', md, f'{cfg}: mevcut imzalardan en az biri geçersiz/izinsiz → tüm-mevcut-geçerli koşulu sağlanmıyor [{ozet}]'
    if cfg == 'L4' and not R.issubset(set(gecerli) | set(belirsiz)):
        md = ['OK65', 'J31-ISS', 'OK47'] + (['OK2B6C'] if len(sig) == 1 else [])
        return 'reject', md, f'L4: R={{{X[kol]}}} için geçerli imza yok (yalnız klasik kanıt; G5) [{ozet}]'
    if belirsiz:
        return 'indeterminate', ['R52-S8'], f'{cfg}: imza geçerliliği maddelerle belirlenemiyor [{ozet}]'
    if cfg == 'L4':
        return sinif, ['OK65', 'J31-ISS', 'A51'], f'L4: tüm imzalar geçerli ve R={{{X[kol]}}} karşılandı [{ozet}]'
    return sinif, ['OK48-P1', 'OK48-P2', 'R52-APP'], f'P2: mevcut tüm imzalar geçerli (R=∅) [{ozet}]'


def ek_kabul_maddesi(v):
    art = v['artefakt']
    md = []
    if art in ('sd-jwt-vc', 'sd-jwt-vc+kb'):
        md.append('S71-2B')
    if art == 'sd-jwt-vc+kb':
        md.append('S73-5B')
    if art == 'status-list-token':
        md.append('T51')
    if art == 'dpop':
        md.append('D43-5')
    if art == 'oid4vp-istek':
        md.append('O593-HASH' if (v['insa'] or {}).get('client_id', '').startswith('x509_hash') or any(
            str(s.get('client_id', '')).startswith('x509_hash') for s in (v['insa'] or {}).get('imzalar', [])) else 'O592')
    x = (v['insa'] or {}).get('x5c')
    if x and art != 'oid4vp-istek':
        md.append('R416')
    return md


def karar_uret(v, kol, cfg, surum):
    """Tek satir: (karar, madde listesi, not metni)."""
    vid = v['id']
    kr, md, gerekce = genel(v, kol, cfg)
    notlar = []

    # ---- aile / vektor ozel kurallari
    if vid in ('X5C07_korumasiz_x5c', 'X5C08_korumasiz_x5c_zincir_degisimi'):
        onceki = kr
        kr, md = 'reject', ['R6', 'V13-35A', 'V13-35B', 'H611', 'OK2D1A']
        gerekce = ('x5c korumasız başlıkta: güven kararı sertifika zincirine (ihraççı = yaprak öznesi) dayandığı için '
                   'bütünlük koruması zorunlu; -13 §3.5 X.509 mekanizması korumalı başlık ister → izinli mekanizma yok → ret'
                   + (f' (ayrıca genel kural: {onceki})' if onceki == 'reject' else ''))
        if vid.startswith('X5C08'):
            notlar.append('korumasız x5c aynı yaprak anahtarı için klasik CA zinciriyle değiştirilmiş (imza bozulmadan zincir sınıfı düşürme)')
        notlar.append('B3 bayrağı: hedefin korumasız x5c\'yi işleyip işlemediği ayrıca kaydedilir')
    elif vid == 'X5C09_korumali_ve_korumasiz_x5c':
        kr, md = 'reject', ['R721-DIS', 'R52-S4']
        gerekce = 'x5c hem korumalı hem korumasız başlıkta: başlık adları ayrık olmalı; §5.2 adım 4 başarısız → imza doğrulanamaz'
    elif vid == 'X5C06_guven_capasi_x5c_icinde':
        if kr.startswith('accept'):
            kr, md = 'indeterminate', ['H611-TA', 'R416']
            gerekce = ('güven çapası x5c içinde: HAIP üreticiye "MUST NOT" der, doğrulayıcı için ret kuralı yok; '
                       'RFC 5280 yolu yine kurulabilir → hem kabul hem ret uyumlu')
    elif vid == 'X5C10_x5c_ve_baska_anahtar_kid':
        if kr.startswith('accept'):
            kr, md = 'indeterminate', ['V13-35A', 'R414', 'J31-KEY']
            gerekce = ('x5c (ML-DSA-65 yaprak, imza geçerli) + kid (ES256 anahtarı): -13 §3.5 x5c yaprağını kullanır → kabul; '
                       'kid ile arama yapan kütüphane 8725bis §3.1 gereği alg–anahtar tutarsızlığıyla reddeder → öncelik tanımsız')
    elif vid in ('CRIT01_bilinmeyen_parametre', 'CRIT05_listelenen_parametre_yok'):
        kr, md = 'reject', ['R4111-INV', 'R52-S5']
        gerekce = ('crit listesindeki uzantı ("x-pq-beklenti" / "x-yok") doğrulayıcıca anlaşılmıyor → JWS geçersiz'
                   + ('; M-f taşıyıcı adayı: fail-closed davranış beklenir' if vid.startswith('CRIT01') else ''))
    elif vid == 'CRIT02_korumasiz_crit':
        kr, md = 'reject', ['R4111-UND', 'R52-S5', 'R4111-INV', 'R4111-PROT']
        gerekce = ('crit korumasız başlıkta: crit her durumda anlaşılıp işlenmeli; JOSE başlığı korumalı+korumasız birleşimidir, '
                   'listelenen "x-pq-beklenti" anlaşılmıyor → geçersiz (ayrıca korumasız crit ihlali)')
    elif vid == 'CRIT03_kayitli_ad':
        if kr.startswith('accept'):
            kr, md = 'indeterminate', ['R4111-PROD', 'R4111-MAY']
            gerekce = 'crit=["alg"]: üretici yasağı; doğrulayıcı için yalnız MAY (geçersiz sayabilir) → hem kabul hem ret uyumlu'
    elif vid == 'CRIT04_bos_dizi':
        if kr.startswith('accept'):
            kr, md = 'indeterminate', ['R4111-EMPTY', 'R4111-MAY']
            gerekce = 'crit=[]: üretici yasağı; doğrulayıcı için yalnız MAY → hem kabul hem ret uyumlu'
    elif vid in CMP_MADDE:
        md = CMP_MADDE[vid] + md
    elif vid == 'CMP05_ecdsa_asgari_olmayan_der':
        md = ['C45-DER', 'C451', 'LC43', 'C64-EUF']
        gerekce = ('ECDSA bileşeni asgari olmayan DER (değerler geçerli): -04 "DER-encoded" der ama doğrulayıcıya katı DER reddi '
                   'açıkça yüklenmez ("Decoding simply reverses"); güvenlik hedefi EUF-CMA → geçerlilik belirlenemiyor')
    elif vid in VP_SDHASH:
        if kr.startswith('accept'):
            kr, md = 'indeterminate', ['S81', 'S73-5G', 'OK2D4']
            gerekce = ('ihraççı katmanı: ' + gerekce + '; KB: sd_hash hangi imzanın geçici kompakt biçimi üzerinden? '
                       '§8.1 çoklu imzada tanımsız → sd_hash denetimi sonucu okumaya bağlı')
    elif vid == 'VC11_typ_vc+sd-jwt':
        if kr.startswith('accept'):
            if surum == '-13':
                kr, md = 'indeterminate', ['V13-321M', 'V13-321R']
                gerekce = 'typ=vc+sd-jwt: -13 üreticiye dc+sd-jwt der; doğrulayıcıya her ikisini kabul ÖNERİR (RECOMMENDED) → yön: kabul; zorunlu değil'
            else:
                kr, md = 'indeterminate', ['V19-221', 'V19-CL', 'S911']
                gerekce = 'typ=vc+sd-jwt: -19 yalnız dc+sd-jwt tanımlar, geçiş notu kaldırıldı; doğrulayıcı typ denetimi RECOMMENDED → yön: ret; zorunlu değil'
    elif vid == 'VC12_alg_none':
        kr, md = 'reject', ['S41', 'S71-2A']
        gerekce = 'ihraççı JWT alg=none'
    elif vid == 'REQ10_istek_alg_none':
        kr, md = 'reject', ['OA1', 'O593-HASH', 'J32-NONE']
        gerekce = 'imzalı istek protokolü (openid4vp-v1-signed) + x509_hash, ama alg=none: imza ve zincir doğrulanamaz; none yapılandırmada izinli değil'
        notlar.append('ÖK §2A Ö4 M-b0 sınıfı; OID4VP §5.9.3 DC API takdiri (T268) imzasız işleme yolunu açık bırakır — bu yol REQ08/09 satırlarında')
    elif vid in ('REQ08_imzasiz_M-b0', 'REQ09_imzasiz_M-b0_client_id_korundu'):
        if cfg == 'L4':
            kr, md = 'indeterminate', ['H52', 'O593-DC', 'OK47']
            gerekce = ('imzasız istek (M-b0): HAIP cüzdanın imzasız isteği desteklemesini ZORUNLU kılar; G5 göç etmiş RP için '
                       'yalnız klasik (Web PKI kökeni) kanıtla kabulü yasaklar; imzasız istekte RP kimliği yok → maddeler çelişir/belirlemez')
        else:
            kr, md = 'accept-classical', ['H52', 'H52N'] + (['OA2'] if vid.startswith('REQ09') else [])
            gerekce = ('imzasız istek desteklenmek zorunda; doğrulayıcı kimliği yalnız platform kökeni + Web PKI (klasik)'
                       + ('; client_id yok sayılmalı' if vid.startswith('REQ09') else ''))
    elif vid in ('DPOP08_ML-DSA-65_ath_nonce', 'DPOP09_ML-DSA-65-ES256_ath_nonce'):
        if kr.startswith('accept'):
            kr, md = 'indeterminate', ['D43-10', 'D43-12']
            gerekce = ('imza/alg düzeyinde kabul yolu var, fakat nonce ve ath denetimleri sunucu bağlamına bağlı; '
                       'dogrulama_girdileri sunucu nonce\'unu ve erişim belirtecini vermiyor (htu = belirteç uç noktası)')
    elif vid.startswith('K10'):
        akp = vid in ('K10P_alg-ES256_anahtar-ML-DSA-65', 'K10C_alg-ML-DSA-65-ES256_anahtar-ML-DSA-65',
                      'K10C_alg-ML-DSA-65_anahtar-ML-DSA-65-ES256')
        md = ['J31-KEY', 'R411', 'F7'] + (['M3-ALG'] if akp else []) + md
        gerekce = ('başlık alg ile doğrulama anahtarının bağlı olduğu algoritma uyuşmuyor (imza gerçek anahtarın kendi algoritmasıyla '
                   'geçerli): kütüphane alg–anahtar tutarlılığını denetlemek ZORUNDA → her yapılandırmada ret. ' + gerekce)
    elif vid == 'DPOP10_jwk_ozel_anahtar_iceriyor':
        kr, md = 'reject', ['D42-JWK', 'D43-7', 'M3-PRIV']
        gerekce = 'DPoP jwk başlığı özel anahtar üyesi (priv) içeriyor'

    # ---- SD-JWT VC surum boyutu (senaryo d JSON)
    if surum == '-19' and vid in SURUM_BOLUNEN and vid != 'VC11_typ_vc+sd-jwt':
        if kr.startswith('accept'):
            kr, md = 'indeterminate', ['V19-22', 'H61-JSON', 'OK2D7']
            gerekce = ('-19: JSON serileştirilmiş SD-JWT VC ayrıntıları kapsam dışı; destekleyen doğrulayıcı -13 okumasıyla kabul eder, '
                       'desteklemeyen reddeder → belirlenmemiş (MR3 sürüm farkı). -13 kararı: ' + gerekce)
    if surum == '-13' and vid in SURUM_BOLUNEN and vid != 'VC11_typ_vc+sd-jwt' and kr.startswith('accept'):
        md = md + ['V13-32', 'S83']
    if surum == '-19' and vid in VP_SDHASH and kr == 'indeterminate':
        md = md + ['V19-22']

    # ---- kabul satirlarina artefakt maddeleri
    if kr.startswith('accept'):
        md = md + ek_kabul_maddesi(v)

    # ---- notlar
    if vid in ('X5C04_karisik_pq_yaprak_klasik_ara', 'X5C05_karisik_pq_ara_klasik_kok') and kr.startswith('accept'):
        notlar.append('accept-hybrid yalnız JWS katmanı: sertifika yolunda klasik kenar var (' +
                      ('ara CA int-ec' if vid.startswith('X5C04') else 'kök root-ec') +
                      '); §6.5 politikası zincir kenarlarını kısıtlamaz; yol sınıfı B2 bayrağıyla raporlanır')
    if vid in ('X5C04_karisik_pq_yaprak_klasik_ara', 'X5C07_korumasiz_x5c') and kol == 'tedavi-composite':
        notlar.append('UYARLAMA YAN ETKİSİ: vektör ML-DSA-65 imzalı; composite kolunun izinli kümesinde ML-DSA-65 yok → '
                      'bu kolda karar izin listesinden gelir, B2/B3 davranışı ölçülemez (NOTLAR N3)')
    if vid in ('VC03_composite_kid', 'VC04_MLDSA44_kid', 'VC05_MLDSA87_kid', 'VC06_composite_Ed25519_kid'):
        notlar.append('x5c yok (kid): HAIP §6.1.1 sapması etiketi (ÖK §2D m.1); anahtar dogrulama_girdileri JWKS\'ten')
    if vid == 'TSL03_composite_kid':
        notlar.append('HAIP §6.1 durum listesi için x5c ister; composite X.509 kapsam dışı → HAIP sapması (ÖK §2D m.1); anahtar JWKS\'ten')
    if vid == 'VPLUS_ES256' and cfg == 'L4':
        notlar.append('DİKKAT: ÖK §4.15/§6.5 V+ → KABUL der; L4 (göç etmiş ihraççı) altında yalnız klasik belge G5 gereği reddedilir. '
                      'V+ denetimi P2/P0 (eski ihraççı) yapılandırmasında ya da X imzalı V+ ile koşulmalı (NOTLAR N2)')
    if vid == 'VC10_ikili_ihrac':
        notlar.append('credentials[0] (ES256, klasik zincir) değerlendirildi; aynı yanıttaki ML-DSA-65 kopya K11 kararına girmez')
    if vid.startswith('REQ') and vid not in ('REQ08_imzasiz_M-b0', 'REQ09_imzasiz_M-b0_client_id_korundu', 'REQ10_istek_alg_none'):
        notlar.append('cüzdan tarafı (IS-PLANI Adım 11 wallet-path); R_I imzalayan RP\'ye benzetmeyle uygulandı')
        if vid.startswith('REQ03'):
            notlar.append('client_id önekli değil → önceden kayıtlı istemci (M-d); HAIP §5 x509_hash zorunluluğundan sapma')
        if vid.startswith(('REQ04', 'REQ05', 'REQ06', 'REQ07')):
            md = md + ['OA322'] if kr != 'indeterminate' else md
            notlar.append('A.3.2.2 hangi imzanın doğrulanacağını belirlemez; karar yapılandırmanın (P0/P2/L4) kendi kuralından')
    if v['artefakt'] in ('status-list-token',) :
        notlar.append('R_I durum ihraççısına benzetmeyle uygulandı')
    if v['artefakt'] == 'dpop':
        notlar.append('R_I = yerel politika (RFC 9449 §4.3(5)) benzetmesi; boyut eşiği kararı etkilemez')
    kb = (v['insa'] or {}).get('kb_jwt')
    if kb:
        notlar.append(f"KB-JWT alg={kb['alg']} (izinli kümeye tabi; R_I yalnız ihraççı imzasına uygulanır)"
                      + ('; KB klasik cihaz anahtarı (G2 klasik kalır)' if kb['alg'] == 'ES256' and X[kol] != 'EdDSA' and v['kol'] != 'klasik-taban' else ''))
    if vid == 'CMP10_onozet_sha256':
        notlar.append('IANA açıklaması (-04 §7.1.2) "SHA-256" ECDSA bileşeninin iç özetidir; normatif ön-özet Tablo 5\'te SHA512 '
                      '(ÖK §2D m.5: "yanlış ön-özet" tanımlayıcı uygulayıcı hatası sınıfı)')
    if vid.startswith('UNK03'):
        md = md + ['R411-CS', 'J211']
    if vid == 'UNK05_general_arti_alg_none':
        notlar.append('none imzası izinli değil (8725bis §3.2); General JSON bir JWT değildir (8725bis §2.13), P0 kararı diğer imzalardan')
    if kol == 'kontrol-Ed25519':
        notlar.append('yedek kol: X=Ed25519 (RFC 9864 §2.2; EdDSA "Deprecated" §4.1.2); ÖK §2D m.2')
    mr4 = (v['insa'] or {}).get('mr4')
    if mr4 and vid != 'VP05_GJ_ES256_MLDSA65_kb-SIRA-ters':
        notlar.append(f"MR4 eşi: kaynak {mr4['kaynak_vektor']} ({mr4['permutasyon']}); imzalar bağımsız doğrulandığından karar kaynakla aynı (RFC 7515 §5.2 adım 9)")
    if v['sdjwtvc_surum'] and vid not in SURUM_BOLUNEN:
        sv = v['sdjwtvc_surum']
        notlar.append('sdjwtvc: ' + ('-13/-19 aynı' if len(sv) == 2 else 'yalnız -13 tanımlı (manifest)'))
    return kr, md, gerekce, notlar


# ---------------------------------------------------------------- satir uretimi
def kollar_icin(v):
    k = v['kol']
    ks = KOLLAR[:] if k in COKLU_KOL else [k]
    for e in EK_KOL.get(v['id'], []):
        if e not in ks:
            ks.append(e)
    return [x for x in KOLLAR if x in ks]


def satirlar(secili_kollar):
    out = []
    for kol in KOLLAR:
        if kol not in secili_kollar:
            continue
        for v in VEK:
            if kol not in kollar_icin(v):
                continue
            vid = v['id']
            r = ROL.get((vid, kol))
            if r:
                rol_m, bir = r
            else:
                bir = False
                if (v['insa'] or {}).get('mr4'):
                    rol_m = 'MR4 eşi (eşleme §2)'
                    if vid.endswith('-ED25519'):
                        rol_m += ', yedek etiket'
                else:
                    rol_m = f"eşleme dışı (aile {v['aile']}, kol {v['kol']})"
            surumler = ['-13', '-19'] if vid in SURUM_BOLUNEN else [None]
            for cfg in ['L4', 'P2', 'P0']:
                for s in surumler:
                    kr, md, gerekce, notlar = karar_uret(v, kol, cfg, s)
                    pol = cfg if s is None else f'{cfg}|sdjwtvc={s}'
                    if bir and cfg == 'L4' and kr != 'indeterminate':
                        vaka = rol_m.split()[0]
                        ok_k = {'K1': 'OK65-K1', 'K2': 'OK65-K2', 'K3': 'OK65-K3', 'K4': 'OK65-K4', 'K5': 'OK65-K5',
                                'K6': 'OK65-K6', 'K7': 'OK65-K7', 'K8': 'OK65-K8', 'K9': 'OK65-K9', 'K10': 'OK65-K10',
                                'K11': 'OK65-K11', 'V+': 'OK65-V', 'V−': 'OK65-V'}.get(vaka)
                        if ok_k:
                            md = md + [ok_k]
                    not_m = f'vaka: {rol_m} | {gerekce}'
                    if notlar:
                        not_m += ' | ' + ' | '.join(notlar)
                    alanlar = [vid, pol, kol, 'evet' if bir else 'hayır', kr, dayanak(md), not_m]
                    for a in alanlar:
                        if '\t' in a or '\n' in a or '\r' in a:
                            sys.exit(f'alan icinde sekme/yeni satir: {vid}')
                    out.append(alanlar)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--kollar', default=','.join(KOLLAR))
    a = ap.parse_args()
    secili = [k for k in a.kollar.split(',') if k]
    for k in secili:
        if k not in KOLLAR:
            sys.exit(f'bilinmeyen kol {k}')
    n = alinti_denetimi()
    capraz_denetim()
    rows = satirlar(secili)
    with open(CIKTI, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\t'.join(['vektor_id', 'politika', 'kol', 'birincil_mi', 'karar', 'dayanak', 'not']) + '\n')
        for r in rows:
            f.write('\t'.join(r) + '\n')
    say = collections.Counter(r[4] for r in rows)
    bsay = collections.Counter(r[4] for r in rows if r[3] == 'evet')
    print(f'alinti denetimi: {n} madde OK; capraz denetim OK')
    print(f'kollar: {secili}')
    print(f'satir: {len(rows)}; vektor: {len({r[0] for r in rows})}; birincil satir: {sum(1 for r in rows if r[3] == "evet")}')
    print('dagilim (tum):', dict(sorted(say.items())))
    print('dagilim (birincil):', dict(sorted(bsay.items())))
    for cfg in ['L4', 'P2', 'P0']:
        c = collections.Counter(r[4] for r in rows if r[1].split('|')[0] == cfg)
        print(f'  {cfg}:', dict(sorted(c.items())))


if __name__ == '__main__':
    main()
