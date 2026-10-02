#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Oracle A -- karar ureteci (Adim 9, gorev 6).

Kural: karar yalniz spesifikasyon maddesi + manifest `insa` gercekleri (ve vektor
dosyalarinin base64url cozumuyle okunan baslik/talep gercekleri) uzerinden verilir.
KRIPTOGRAFI YOK, HEDEF KUTUPHANE YOK, AG YOK. Imza dogrulanmaz; imzanin gecerli olup
olmadigi manifestteki uretim gercegidir (`insa`).

Kullanim:  python karar_uret.py <proje_koku>
Ciktilar (experiment/oracle/oracle-A/): karar.tsv, maddeler.tsv, karar_ozet.json,
                                   insa_denetimi.txt
"""
import base64
import csv
import hashlib
import json
import os
import sys
from collections import Counter, OrderedDict

KOK = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
CIKTI = os.path.join(KOK, 'experiment', 'oracle', 'oracle-A')
KORPUS = os.path.join(KOK, 'spec-corpus', 'metin')
VDIR = os.path.join(KOK, 'experiment', 'vector-generator', 'vektorler', 'v1.2')
OK_YOL = os.path.join(KOK, '00-on-kayit', 'ON-KAYIT-TASLAK.md')
ESLEME_YOL = os.path.join(KOK, 'experiment', 'vector-generator', 'BATARYA-ESLEME.md')

BEKLENEN = {
    OK_YOL: 'dcc84092e2ca5eee0fcca8277fbcbd6b06ff613dc3459f63195f44d1ce3df79a',
    os.path.join(VDIR, 'MANIFEST.json'): 'bb17aaa76a3d1859b2dd5df54c62e7039948a715e2c4b4628fed82d184c6e738',
    os.path.join(VDIR, 'SHA256SUMS'): '92663b48f477f51e5a4cdd2a6942d97d36b2d9591fa67af451fd33eb14f0b2a3',
    ESLEME_YOL: 'd73352179cdf281825d498000b7f9dc6d1df0fe835c8258c6aa2c516e659e3fc',
}


def sha256(yol):
    return hashlib.sha256(open(yol, 'rb').read()).hexdigest()


for yol, ozet in BEKLENEN.items():
    gercek = sha256(yol)
    if gercek != ozet:
        sys.exit('OZET UYUSMAZLIGI: %s %s != %s' % (yol, gercek, ozet))

# korpus metinlerinin ozetleri spec-corpus/MANIFEST.csv ile
KORPUS_MAN = {r['id']: r for r in csv.DictReader(open(os.path.join(KOK, 'spec-corpus', 'MANIFEST.csv'), encoding='utf-8'))}

SURUM = {
    'JWTBCP': 'draft-ietf-oauth-rfc8725bis-10',
    'JOSECOMP': 'draft-ietf-jose-pq-composite-sigs-04',
    'LAMPSCOMP': 'draft-ietf-lamps-pq-composite-sigs-19',
    'RFC7515': 'RFC 7515', 'RFC7518': 'RFC 7518', 'RFC8725': 'RFC 8725',
    'RFC9864': 'RFC 9864', 'RFC9964': 'RFC 9964', 'RFC9901': 'RFC 9901',
    'RFC9449': 'RFC 9449',
    'SDJWTVC': 'draft-ietf-oauth-sd-jwt-vc-19', 'SDJWTVC13': 'draft-ietf-oauth-sd-jwt-vc-13',
    'HAIP': 'HAIP 1.0 Final', 'OID4VP': 'OID4VP 1.0 Final',
    'TSL': 'draft-ietf-oauth-status-list-21', 'ACM2': 'ECCG ACM v2.0',
    'OK': 'ON-KAYIT v0.8 (capa 7)',
}
DOSYA = {k: os.path.join(KORPUS, k + '.txt') for k in SURUM if k != 'OK'}
DOSYA['OK'] = OK_YOL

for k, yol in DOSYA.items():
    if k == 'OK':
        continue
    if sha256(yol) != KORPUS_MAN[k]['sha256_metin']:
        sys.exit('KORPUS OZET UYUSMAZLIGI: ' + k)

_SATIRLAR = {k: open(v, encoding='utf-8').read().split('\n') for k, v in DOSYA.items()}


def _norm(s):
    return ' '.join(s.split())


def satir_bul(belge, alinti, yakin=None, pencere=14):
    """Alintinin (bosluk normallestirilmis) basladigi 1-tabanli satiri dondurur."""
    L = _SATIRLAR[belge]
    q = _norm(alinti)
    bulunan = []
    n = len(L)
    for i in range(n):
        w = _norm(' '.join(L[i:i + pencere]))
        if q in w:
            w2 = _norm(' '.join(L[i + 1:i + 1 + pencere]))
            if q not in w2:
                bulunan.append(i + 1)
    if not bulunan:
        return None
    if yakin is None:
        return bulunan[0]
    return min(bulunan, key=lambda x: abs(x - yakin))


# ---------------------------------------------------------------------------
# 1. Madde kayitlari. kimlik: izlenebilirlik matrisi T-kimligi (varsa) ya da bolum.
# ---------------------------------------------------------------------------
MADDELER = OrderedDict()


def M(anahtar, kimlik, belge, bolum, alinti, yakin=None):
    MADDELER[anahtar] = dict(kimlik=kimlik, belge=belge, bolum=bolum, alinti=alinti, yakin=yakin)


# 8725bis (JWTBCP)
M('BCP31-izin', 'T327', 'JWTBCP', '§3.1', 'MUST NOT employ any algorithms outside this configured set')
M('BCP31-ihracci', 'T328', 'JWTBCP', '§3.1', 'it MUST determine which algorithms are permitted for itself and that issuer and ensure that the received JWT complies with those requirements')
M('BCP31-anahtar', 'T329', 'JWTBCP', '§3.1', 'is consistent with the algorithm associated with the key identified by the corresponding identifier')
M('BCP31-tekalg', '§3.1', 'JWTBCP', '§3.1', 'each key MUST be used with exactly one algorithm')
M('BCP32-none', '§3.2', 'JWTBCP', '§3.2', 'JWT libraries MUST NOT consume JWTs using "none" unless explicitly allowed by the caller')
M('BCP33', '§3.3', 'JWTBCP', '§3.3', 'the entire JWT MUST be rejected if any of them fail to validate')
M('BCP32-ed', 'T331', 'JWTBCP', '§3.2', 'New deployments SHOULD prefer fully-specified algorithm identifiers')
M('BCP314', '§3.14', 'JWTBCP', '§3.14', 'is not a JWT and MUST be rejected')
# composite -04
M('CMP43-AND', 'T345', 'JOSECOMP', '§4.3', 'The Verify algorithm MUST validate a signature only if all component signatures were successfully validated.')
M('CMP43-ser', '§4.3', 'JOSECOMP', '§4.3', 'If Error during deserialization, or if any of the component keys or signature values are not of the correct type or length for the given component algorithm then output "Invalid signature" and stop.')
M('CMP42-iki', '§4.2', 'JOSECOMP', '§4.2', "A composite signature's value MUST include the two signature components")
M('CMP42-sira', '§4.2', 'JOSECOMP', '§4.2', 'the two components MUST be in the same order as the components from the corresponding signing key')
M('CMP42-Mp', '§4.2', 'JOSECOMP', '§4.2', "M' <- Prefix || Label || 0x00 || PH(M)", yakin=380)
M('CMP42-ctx', '§4.2', 'JOSECOMP', '§4.2', "mldsaSig <- ML-DSA.Sign(mldsaSK, M', ctx=Label)")
M('CMP42-der', '§4.2', 'JOSECOMP', '§4.2', 'the ECDSA signature is encoded as an Ecdsa-Sig-Value')
M('CMP-T5', '§5.1 Tablo 5', 'JOSECOMP', '§5.1', '|ML-DSA-65-ES256 |ML-DSA-65|ecdsa-with-SHA256|SHA512 |Composite |')
M('CMP451-geri', '§4.5.1', 'JOSECOMP', '§4.5.1', 'Decoding simply reverses these two steps.')
M('CMP62-bilesen', 'T057', 'JOSECOMP', '§6.2', 'compliant parties MUST NOT use, import, or export component keys that are used in other contexts, combinations, or as standalone keys')
M('CMP62-sertifika', 'T055', 'JOSECOMP', '§6.2', 'Because the certificate itself is protected by a composite signature, an attacker cannot forge a fake certificate to swap a public key even if the traditional algorithm is broken.')
M('CMP63', 'T347', 'JOSECOMP', '§6.3', 'ensures that signatures cannot be removed from the composite and used in other contexts')
M('CMP71-talep', '§7.1', 'JOSECOMP', '§7.1', 'are requested to be added to the "JSON Web Signature and Encryption Algorithms" registry')
M('LAMPS43', '§4.3', 'LAMPSCOMP', '§4.3', 'Deserialization reverses this process, raising an error in the event that the input is malformed.')
# RFC 7515
M('JWS411', 'T319', 'RFC7515', '§4.1.1', 'The JWS Signature value is not valid if the "alg" value does not represent a supported algorithm')
M('JWS411-harf', '§4.1.1', 'RFC7515', '§4.1.1', 'The "alg" value is a case- sensitive ASCII string')
M('JWS416', 'T038', 'RFC7515', '§4.1.6', 'The recipient MUST validate the certificate chain according to RFC 5280 [RFC5280] and consider the certificate or certificate chain to be invalid if any validation failure occurs.')
M('JWS4111-crit', 'T386', 'RFC7515', '§4.1.11', 'If any of the listed extension Header Parameters are not understood and supported by the recipient, then the JWS is invalid.')
M('JWS4111-MAY', '§4.1.11', 'RFC7515', '§4.1.11', 'Recipients MAY consider the JWS to be invalid if the critical list contains any Header Parameter names defined by this specification or [JWA] for use with JWS or if any other constraints on its use are violated.')
M('JWS4111-korumali', '§4.1.11', 'RFC7515', '§4.1.11', 'it MUST occur only within the JWS Protected Header')
M('JWS52-uygulama', 'T314', 'RFC7515', '§5.2', 'When there are multiple JWS Signature values, it is an application decision which of the JWS Signature values must successfully validate for the JWS to be accepted.')
M('JWS52-enaz', 'T315', 'RFC7515', '§5.2', 'at least one JWS Signature value MUST successfully validate, or the JWS MUST be considered invalid')
M('JWS52-alg', 'T316', 'RFC7515', '§5.2', 'unless the algorithm(s) used in the JWS are acceptable to the application, it SHOULD consider the JWS to be invalid')
M('JWS52-8', '§5.2 (8)', 'RFC7515', '§5.2', 'which MUST be accurately represented by the value of the "alg" (algorithm) Header Parameter')
M('JWS52-4', '§5.2 (4)', 'RFC7515', '§5.2', 'the same Header Parameter name also MUST NOT occur in distinct JSON object values that together comprise the JOSE Header')
M('JWS6', 'T040', 'RFC7515', '§6', 'These Header Parameters MUST be integrity protected if the information that they convey is to be utilized in a trust decision')
M('JWS721-ayrik', '§7.2.1', 'RFC7515', '§7.2.1', 'The Header Parameter names in the two locations MUST be disjoint.')
# RFC 7518 / 9864 / 9964
M('JWA34-64', '§3.4', 'RFC7518', '§3.4', 'The JWS Signature value MUST be a 64-octet sequence.')
M('JWA34-girdi', '§3.4', 'RFC7518', '§3.4', 'Submit the JWS Signing Input, R, S, and the public key (x, y) to the ECDSA P-256 SHA-256 validator.')
M('R9864-eddsa', '§4.1.2', 'RFC9864', '§4.1.2', 'JOSE Implementation Requirements: Deprecated')
M('R9864-tekalg', 'T335', 'RFC9864', '§7', 'A cryptographic key MUST be used with only a single algorithm')
M('R9964-alg', 'T337', 'RFC9964', '§3', 'The alg JSON Web Key (JWK) parameter or COSE Key Common parameter is REQUIRED for all AKP keys.')
M('R9964-ctx', 'T338', 'RFC9964', '§5', 'The ctx parameter MUST be the empty string for ML-DSA-44, ML-DSA- 65, and ML-DSA-87.')
# RFC 9901
M('SD41-none', 'T102', 'RFC9901', '§4.1', 'It MUST NOT use the none algorithm.')
M('SD71-2a', 'T103', 'RFC9901', '§7.1 (2a)', 'The "none" algorithm MUST NOT be accepted.', yakin=1665)
M('SD71-iptal', '§7.1', 'RFC9901', '§7.1', 'If any step fails, the SD-JWT is not valid, and processing MUST be aborted.')
M('SD73-sdhash', '§7.3 (5g)', 'RFC9901', '§7.3', 'verify that it matches the value of the sd_hash claim in the Key Binding JWT')
M('SD81-sdhash', '§8.1', 'RFC9901', '§8.1', 'the SD-JWT Compact Serialization part is built by concatenating the protected header, the payload, and the signature of the JWS JSON serialized SD-JWT')
M('SD8-opsiyon', '§8', 'RFC9901', '§8', 'Supporting this format is OPTIONAL.')
M('SD83', 'T108', 'RFC9901', '§8.3', 'disclosures and kb_jwt MUST be included in the first unprotected header')
M('SD91', 'T107', 'RFC9901', '§9.1', 'The Issuer-signed JWT MUST be rejected if the signature cannot be verified.')
M('SD911', '§9.11', 'RFC9901', '§9.11', 'it is RECOMMENDED that application profiles of SD-JWT specify an explicit type by including the typ header parameter when the SD-JWT is issued, and that Verifiers check this value.')
# SD-JWT VC
M('VC13-typ', '§3.2.1', 'SDJWTVC13', '§3.2.1', 'The typ value MUST use dc+sd-jwt.')
M('VC13-gecis', '§3.2.1', 'SDJWTVC13', '§3.2.1', 'it is RECOMMENDED that Verifiers and Holders accept both vc+sd-jwt and dc+sd-jwt as the value of the typ header for a reasonable transitional period.')
M('VC13-json', 'T114', 'SDJWTVC13', '§3.2', 'where support for the JWS JSON Serialization is OPTIONAL')
M('VC13-x5c', '§3.5', 'SDJWTVC13', '§3.5', 'When the protected header of the Issuer-signed JWT contains the x5c parameter, the recipient uses the public key from the end-entity certificate')
M('VC19-json', 'T113', 'SDJWTVC', '§2.2', 'is not precluded but the specific details are beyond the scope of this specification')
M('VC19-typ', 'T119', 'SDJWTVC', '§2.2.1', 'The Issuer MUST include the typ header parameter in the SD-JWT. The typ value MUST use dc+sd-jwt.')
M('VC19-x5c', 'T045', 'SDJWTVC', '§2.5', 'When the protected header of the Issuer-signed JWT contains the x5c parameter, the recipient uses the public key from the end- entity certificate')
M('VC19-red', 'T047', 'SDJWTVC', '§2.5', 'If a recipient cannot validate that the public verification key corresponds to the Issuer of the Issuer-signed JWT using a permitted key discovery and validation mechanism, the SD-JWT VC MUST be rejected.')
M('VC19-73', 'T048', 'SDJWTVC', '§7.3', 'an attacker cannot influence the type of verification process used')
# HAIP
M('HAIP61-json', 'T115', 'HAIP', '§6.1', 'Compact serialization MUST be supported as defined in [RFC9901]. JSON serialization MAY be supported.')
M('HAIP61-tsl', 'T167', 'HAIP', '§6.1', 'The public key used to validate the signature on the Status List Token defined in [I-D.ietf-oauth-status-list] MUST be included in the x5c JOSE header of the Token.')
M('HAIP611-x5c', 'T042', 'HAIP', '§6.1.1', "The SD-JWT VC MUST contain the credential issuer's signing certificate along with a trust chain in the x5c JOSE header parameter")
M('HAIP611-capa', 'T043', 'HAIP', '§6.1.1', 'The X.509 certificate of the trust anchor MUST NOT be included in the x5c JOSE header of the SD-JWT VC.')
M('HAIP6111', 'T219', 'HAIP', '§6.1.1.1', 'If the credential has cryptographic holder binding, a KB-JWT, as defined in [I-D.ietf-oauth-sd-jwt-vc], MUST always be present when presenting an SD-JWT VC.')
M('HAIP5-x509', '§5', 'HAIP', '§5', 'For signed requests, the Verifier MUST use, and the Wallet MUST accept the Client Identifier Prefix x509_hash')
M('HAIP52-imzasiz', 'T281', 'HAIP', '§5.2', 'The Wallet MUST support unsigned, signed, and multi-signed requests as defined in Appendices A.3.1 and A.3.2 of [OIDF.OID4VP].')
M('HAIP52-webpki', 'T282', 'HAIP', '§5.2', 'Note that unsigned requests depend on the origin information provided by the platform and the web PKI for request integrity protection and to authenticate the Verifier.')
M('HAIP7-onceden', 'T123', 'HAIP', '§7', 'Verifiers are assumed to determine in advance the cryptographic suites supported by the Ecosystem')
# OID4VP
M('VP593-x509', 'T240', 'OID4VP', '§5.9.3', 'The Wallet MUST validate the signature and the trust chain of the X.509 leaf certificate.')
M('VP593-takdir', 'T268', 'OID4VP', '§5.9.3', 'it is at the discretion of the Wallet whether it validates the signature on the Request Object')
M('VPA2-clientid', 'T279', 'OID4VP', 'A.2', 'The Wallet MUST ignore any client_id parameter that is present in an unsigned request.')
M('VPA322', 'T269', 'OID4VP', 'A.3.2.2', 'allows the Verifier to use multiple Client Identifiers and corresponding key material to protect the same request')
# RFC 9449
M('DPOP43-5', 'T378', 'RFC9449', '§4.3 (5)', 'The alg JOSE Header Parameter indicates a registered asymmetric digital signature algorithm [IANA.JOSE.ALGS], is not none, is supported by the application, and is acceptable per local policy.')
M('DPOP43-7', '§4.3 (7)', 'RFC9449', '§4.3 (7)', 'The jwk JOSE Header Parameter does not contain a private key.')
M('DPOP43-11', 'T380', 'RFC9449', '§4.3 (11)', 'is within an acceptable window (see Section 11.1)')
# Token Status List
M('TSL51-typ', '§5.1', 'TSL', '§5.1', 'The JWT type MUST be statuslist+jwt.')
M('TSL51-imza', 'T146', 'TSL', '§5.1', 'Relying Parties MUST reject JWTs with an invalid signature.')
# ECCG
M('ACM2-51', 'T135', 'ACM2', 'Note 51', 'the veriﬁcation function accepting if and only if all signatures are correct')
# On kayit (politika tanimlari)
M('OK65-pol', 'ÖK §6.5', 'OK', '§6.5', 'İhraççı başına gerekli küme R = {X}, izinli küme {A, X}.')
M('OK65-K1', 'ÖK §6.5 K1', 'OK', '§6.5', 'Çift imza (A + X), ikisi geçerli | KABUL')
M('OK65-K2', 'ÖK §6.5 K2', 'OK', '§6.5', 'X imzası bozuk | RED')
M('OK65-K3', 'ÖK §6.5 K3', 'OK', '§6.5', 'X soyulmuş (yalnız A) | RED')
M('OK65-K4', 'ÖK §6.5 K4', 'OK', '§6.5', 'Yalnız X | KABUL')
M('OK65-K5', 'ÖK §6.5 K5', 'OK', '§6.5', 'K1 + tanınmayan algoritmalı üçüncü imza | Politikaya göre (MR2); bayrak B1')
M('OK65-K6', 'ÖK §6.5 K6', 'OK', '§6.5', 'Composite tek imza, geçerli (desteklenen hedeflerde) | KABUL')
M('OK65-K7', 'ÖK §6.5 K7', 'OK', '§6.5', 'Composite etiketli, bileşeni bozuk | RED')
M('OK65-K8', 'ÖK §6.5 K8', 'OK', '§6.5', 'zinciri (yaprak composite, ara CA klasik) | Bayrak B2')
M('OK65-K9', 'ÖK §6.5 K9', 'OK', '§6.5', 'Korumasız başlıkta `x5c` | Bayrak B3')
M('OK65-K10', 'ÖK §6.5 K10', 'OK', '§6.5', 'Alg–anahtar uyuşmazlığı | RED (L2/L3)')
M('OK65-K11', 'ÖK §6.5 K11', 'OK', '§6.5', 'İkili ihraç: göç etmiş ihraççıdan yalnız klasik kimlik bilgisi | RED (G5)')
M('OK65-V', 'ÖK §6.5 V±', 'OK', '§6.5', 'Adaptör geçerlilik kontrolleri | KABUL / RED')
M('OK415-V', 'ÖK §4.15', 'OK', '§4.15', 'V+: tek geçerli klasik imza → KABUL; V−: bozuk imza → RED')
M('OK47-G5', 'ÖK §4.7 G5', 'OK', '§4.7', 'Göç etmiş bir varlık, ilan ettiği eski-sürüm penceresi dışında yalnız klasik kanıtla kabul edilemez.')
M('OK48-P0', 'ÖK §4.8 P0', 'OK', '§4.8', 'En az bir imza geçerliyse kabul')
M('OK48-P1', 'ÖK §4.8 P1', 'OK', '§4.8', 'Mevcut imzaların tümü geçerliyse kabul. İmza silinmesi (soyma) fark edilmez')
M('OK48-P3', 'ÖK §4.8 P3', 'OK', '§4.8', 'P2 + ihraççı başına gerekli küme R_I')
M('OK413-L4', 'ÖK §4.13 L4', 'OK', '§4.13', 'Yapılandırılmış hâlde K1 KABUL, K2 RED, K3 RED (§6.5)')
M('OK413-L1', 'ÖK §4.13 L1', 'OK', '§4.13', 'Doğrulayıcı genelinde izin listesi; izinsiz algoritma reddediliyor')
M('OK413-L3', 'ÖK §4.13 L3', 'OK', '§4.13', 'Anahtar ya da ihraççı başına algoritma bağlama; K10 (alg–anahtar uyuşmazlığı) reddediliyor')
M('OK413-B6', 'ÖK §4.13 B6', 'OK', '§4.13', 'Bu bir başarısızlık değil, "uygulanamaz" kaydıdır.')
M('OK2B-L4c', 'ÖK §2B m.6', 'OK', '§2B', 'Göç etmiş ihraççının yalnız klasik imzalı belgesi reddedilir, eski ihraççının klasik imzalı belgesi kabul edilir.')
M('OK2D-x5c', 'ÖK §2D m.1', 'OK', '§2D', '`x5c`/zincir davranışı yalnız X5C vektörlerinde, klasik ve ML-DSA zincirleriyle ölçülür.')
M('OK2D-kb', 'ÖK §2D m.4', 'OK', '§2D', 'General JSON serileştirmede birden çok imza varsa `sd_hash`\'in hangi imzayı bağladığı tanımsızdır.')
M('OK2D-yol', 'ÖK §2D m.13', 'OK', '§2D', "kabul edilen yolun, TL/LoTE'de listelenen çıpadan kimlik bilgisine kadar bütün kenarları PQ olmalıdır")
M('OK2F-K8', 'ÖK §2F m.4', 'OK', '§2F', '"**yaprak ML-DSA-65, ara CA klasik**" (vektör X5C04)')
M('OK-MR2', 'ÖK §4.20 MR2', 'OK', '§4.20', 'MR2: Bilinmeyen alg eklemenin etkisi politikaya göre öngörülebilir olmalı.')
M('OK-sdjwtvc', 'ÖK §2C.2.3', 'OK', '§2C', '| `sdjwtvc_surum` | -13 | -19 |')

# ---------------------------------------------------------------------------
# Alinti dogrulama: her alinti korpus metninde bulunmali; satiri hesaplanir.
# ---------------------------------------------------------------------------
_hatalar = []
for k, m in MADDELER.items():
    s = satir_bul(m['belge'], m['alinti'], m['yakin'])
    if s is None:
        _hatalar.append(k)
    m['satir'] = s
if _hatalar:
    sys.exit('ALINTI BULUNAMADI: ' + ', '.join(_hatalar))


def dayanak(*anahtarlar):
    """Bicim: [Tnnn] BELGE §bolum (surum; dosya:satir): "birebir alinti"  -- ' | ' ile ayrilir."""
    parca = []
    gorulen = set()
    for a in anahtarlar:
        if a in gorulen:
            continue
        gorulen.add(a)
        m = MADDELER[a]
        if m['belge'] == 'OK':
            etiket = '%s (%s; 00-on-kayit/ON-KAYIT-TASLAK.md:%d)' % (m['kimlik'], SURUM['OK'], m['satir'])
        else:
            kim = '[%s] ' % m['kimlik'] if m['kimlik'].startswith('T') else ''
            etiket = '%s%s %s (%s; metin/%s.txt:%d)' % (kim, m['belge'], m['bolum'], SURUM[m['belge']], m['belge'], m['satir'])
        parca.append('%s: "%s"' % (etiket, _norm(m['alinti'])))
    return ' | '.join(parca)


def kisa(*anahtarlar):
    """Not alanindaki madde anilari icin kisa bicim."""
    out = []
    for a in anahtarlar:
        m = MADDELER[a]
        if m['belge'] == 'OK':
            out.append(m['kimlik'])
        else:
            out.append(('%s ' % m['kimlik'] if m['kimlik'].startswith('T') else '') + '%s %s' % (m['belge'], m['bolum']))
    return '[' + '; '.join(out) + ']'


# ---------------------------------------------------------------------------
# 2. Vektorler ve insa gercekleri
# ---------------------------------------------------------------------------
MAN = json.load(open(os.path.join(VDIR, 'MANIFEST.json'), encoding='utf-8'))
SIMDI = MAN['simdi']
VEKTOR = OrderedDict((v['id'], v) for v in MAN['vektorler'])

A = 'ES256'
KOLLAR = OrderedDict([
    ('kontrol-EdDSA', 'EdDSA'),
    ('kontrol-Ed25519', 'Ed25519'),
    ('tedavi-ML-DSA-65', 'ML-DSA-65'),
    ('tedavi-composite', 'ML-DSA-65-ES256'),
])
PQ = {'ML-DSA-44', 'ML-DSA-65', 'ML-DSA-87', 'ML-DSA-65-ES256', 'ML-DSA-65-Ed25519'}
# Bataryadaki kayitli ya da taslakta tanimli (desteklenen varsayilan) algoritmalar.
DESTEKLENEN = {'ES256', 'EdDSA', 'Ed25519', 'ML-DSA-44', 'ML-DSA-65', 'ML-DSA-87', 'ML-DSA-65-ES256', 'ML-DSA-65-Ed25519'}
# IANA JOSE kaydinda olanlar (RFC 7518, 8037/9864, 9964). Composite -04 yalniz "talep" (JOSECOMP §7.1).
KAYITLI = {'ES256', 'EdDSA', 'Ed25519', 'ML-DSA-44', 'ML-DSA-65', 'ML-DSA-87'}


def b64d(s):
    return base64.urlsafe_b64decode(s + '=' * (-len(s) % 4))


def jd(s):
    return json.loads(b64d(s))


def oku(v):
    return open(os.path.join(VDIR, v['dosya'].replace('/', os.sep)), encoding='utf-8').read().strip()


DENETIM = []  # (vektor, gercek, sonuc)


def denetle(vid, aciklama, kosul):
    DENETIM.append((vid, aciklama, bool(kosul)))
    if not kosul:
        sys.exit('INSA DENETIMI BASARISIZ: %s: %s' % (vid, aciklama))


def cozum(v):
    """Vektor dosyasindan baslik ve talep gercekleri (yalniz base64url)."""
    raw = oku(v)
    d = {'imzalar': []}
    ser = v['serilestirme']
    if ser == 'compact':
        p = raw.split('.')
        d['imzalar'].append({'korumali': jd(p[0]), 'korumasiz': None})
        d['yuk'] = jd(p[1]) if p[1] else None
    elif ser == 'sd-jwt-compact':
        c = raw.split('~')
        p = c[0].split('.')
        d['imzalar'].append({'korumali': jd(p[0]), 'korumasiz': None})
        d['yuk'] = jd(p[1])
        d['ifsa'] = len(c) - 2
        if c[-1]:
            q = c[-1].split('.')
            d['kb'] = {'baslik': jd(q[0]), 'yuk': jd(q[1])}
    elif ser in ('general', 'sd-jwt-general', 'sd-jwt-flattened'):
        o = json.loads(raw)
        d['yuk'] = jd(o['payload'])
        imz = o['signatures'] if 'signatures' in o else [o]
        for s in imz:
            d['imzalar'].append({'korumali': jd(s['protected']) if s.get('protected') else {}, 'korumasiz': s.get('header')})
        h0 = d['imzalar'][0]['korumasiz'] or {}
        if 'kb_jwt' in h0:
            q = h0['kb_jwt'].split('.')
            d['kb'] = {'baslik': jd(q[0]), 'yuk': jd(q[1])}
    elif ser == 'oid4vci-toplu-yanit':
        o = json.loads(raw)
        d['kimlik_bilgileri'] = []
        for cr in o['credentials']:
            s = cr['credential'] if isinstance(cr, dict) else cr
            p = s.split('~')[0].split('.')
            d['kimlik_bilgileri'].append({'korumali': jd(p[0]), 'yuk': jd(p[1])})
    elif ser == 'dcapi-json-parametre':
        o = json.loads(raw)
        d['protokol'] = o['protocol']
        d['veri'] = o['data']
    return d


# ---------------------------------------------------------------------------
# 3. Imza gecerliligi (insa -> gecerli: True / False / None(belirsiz)) ve neden
# ---------------------------------------------------------------------------
CMP_KURAL = {
    'ML-DSA bileseni bozuk (bayt 1654, bit 0); ECDSA bileseni gecerli': (False, ['CMP43-AND'], 'ML-DSA bileşeni bozuk; composite AND gereği geçersiz'),
    'ECDSA bileseni bozuk (r son bayt); ML-DSA gecerli': (False, ['CMP43-AND'], 'ECDSA bileşeni bozuk; composite AND gereği geçersiz'),
    'ECDSA DER uzunluk bayti bozuk': (False, ['CMP42-der', 'CMP43-ser', 'LAMPS43'], 'ECDSA bileşeni Ecdsa-Sig-Value olarak çözülemez'),
    'ECDSA bileseni ham r||s (DER degil); degerler gecerli': (False, ['CMP42-der', 'CMP43-ser', 'LAMPS43'], 'ECDSA bileşeni DER Ecdsa-Sig-Value değil (ham r||s)'),
    'asgari olmayan DER; degerler gecerli': (None, ['CMP42-der', 'CMP451-geri', 'LAMPS43'], 'asgari olmayan DER: -04 §4.5.1 "çözme adımları tersine çevirir" der, katı DER reddi yazılı değil'),
    'gecerli imza + artik bayt': (None, ['CMP42-der', 'CMP451-geri', 'LAMPS43'], 'Ecdsa-Sig-Value sonrası artık bayt: "malformed" tanımsız; katı ayrıştırıcı reddeder, gevşek ayrıştırıcı kabul eder'),
    'yalniz ML-DSA bileseni': (False, ['CMP42-iki', 'CMP43-ser'], 'ECDSA bileşeni yok'),
    'ML-DSA bileseni baska ileti; ECDSA bileseni gecerli': (False, ['CMP43-AND'], "ML-DSA bileşeni bu M' üzerinde doğrulanmaz"),
    'ML-DSA bileseni ctx bos; ECDSA gecerli': (False, ['CMP42-ctx', 'CMP43-AND'], 'ML-DSA bileşeni ctx=Label ile doğrulanmaz (boş ctx ile üretilmiş)'),
    "iki bilesen de yanlis on-ozetli M' uzerinde gecerli": (False, ['CMP-T5', 'CMP42-Mp', 'CMP43-AND'], "doğrulayıcı M'yi SHA512 ön-özetle kurar (Tablo 5); SHA-256 ile kurulmuş M' üzerindeki bileşenler doğrulanmaz"),
    "iki bilesen de 0x00'siz M' uzerinde gecerli": (False, ['CMP42-Mp', 'CMP43-AND'], "doğrulayıcı M'yi 0x00 ile kurar; bileşenler doğrulanmaz"),
    "composite'in ECDSA bileseni (M' uzerinde)": (False, ['JWA34-girdi', 'CMP63', 'CMP62-bilesen'], "ES256 doğrulaması JWS Signing Input üzerinde yapılır; imza M' üzerinde üretilmiş; bileşen anahtarının bağımsız kullanımı yasak"),
    "composite'in ML-DSA bileseni (M', ctx=Label)": (False, ['R9964-ctx', 'CMP63', 'CMP62-bilesen'], "ML-DSA-65 doğrulaması boş ctx ile JWS Signing Input üzerinde yapılır; imza M' ve ctx=Label ile üretilmiş; bileşen anahtarının bağımsız kullanımı yasak"),
    'ML-DSA bileseni bozuk; Ed25519 gecerli': (False, ['CMP43-AND'], 'ML-DSA bileşeni bozuk; composite AND'),
    'Ed25519 bileseni bozuk; ML-DSA gecerli': (False, ['CMP43-AND'], 'Ed25519 bileşeni bozuk; composite AND'),
    'bilesen sirasi ters': (False, ['CMP42-sira', 'CMP43-ser'], 'bileşen sırası anahtardakinin tersi; ilk 3309 bayt ML-DSA imzası olarak çözülemez'),
}


def imza_durumu(vid, s):
    """(gecerli, neden_anahtarlari, aciklama)"""
    alg = s['alg']
    ins = s.get('insa')
    if vid.startswith('CMP') and ins in CMP_KURAL:
        return CMP_KURAL[ins]
    if alg == 'none':
        return (False, ['BCP32-none', 'JWS411'], 'alg=none: imza yok')
    if alg not in DESTEKLENEN:
        if alg == 'ml-dsa-65':
            return (False, ['JWS411', 'JWS411-harf'], 'alg büyük/küçük harfe duyarlı; "ml-dsa-65" desteklenen bir algoritma değil')
        return (False, ['JWS411'], 'alg "%s" kayıtsız/desteklenmeyen' % alg)
    if ins == 'gecerli':
        return (True, [], 'geçerli')
    if ins and ins.startswith('bozuk'):
        return (False, ['JWS52-8'] + (['CMP43-AND'] if alg == 'ML-DSA-65-ES256' else []), 'imza bozuk (%s)' % ins)
    if ins and ins.startswith('gercek anahtarin algoritmasiyla'):
        k = ['BCP31-anahtar', 'JWS52-8', 'R9864-tekalg']
        if alg == 'ES256':
            k.append('JWA34-64' if 'ML-DSA' in ins else 'JWA34-girdi')
        if alg in ('ML-DSA-65', 'ML-DSA-65-ES256'):
            k.append('R9964-alg')
        return (False, k, 'başlık alg ile anahtarın algoritması uyuşmuyor (K10)')
    if ins and ins.startswith('x5c yapragiyla gecerli'):
        return (True, [], 'x5c yaprağıyla geçerli')
    raise SystemExit('SINIFLANMAMIS INSA: %s %s' % (vid, ins))


# ---------------------------------------------------------------------------
# 4. Politika yapilandirmalari
# ---------------------------------------------------------------------------
YAPILANDIRMALAR = OrderedDict([
    ('GEC', 'Geçerlilik tabanı (ÖK §4.15 V±): W = bataryanın desteklenen tüm algoritmaları; R = ∅; anahtar–alg bağlama; tek imzalı nesneler'),
    ('IZIN-A', 'L1/L2 negatif: W = {A}; R = ∅; tek imzalı nesneler'),
    ('IZIN-AX', 'L1/L2 pozitif, L3 (K10), L4c-eski ihraççı: W = {A, X}; R = ∅; tek imzalı nesneler'),
    ('L4', 'ÖK §6.5 politikası (birincil L4 oracle): W = {A, X}; R = {X}; ihraççı göç etmiş (G5); izin dışı ek imza için karar ÖK\'de "politikaya göre" → S ile Y ayrışırsa indeterminate'),
    ('L4-S', 'L4 + mevcut her imza W içinde ve geçerli olmalı (ÖK §4.8 P3 ⊇ P1; ECCG ACM Not 51; RFC 7515 §5.2 son paragraf)'),
    ('L4-Y', 'L4 + W dışındaki ek imzalar yok sayılır (RFC 7515 §5.2 "application decision"; 8725bis §3.1 "MUST NOT employ ... outside")'),
    ('P0', 'ÖK §4.8 P0 en-az-biri-geçerli: W = desteklenen tümü; R = ∅; çoklu imzalı (General JSON) nesneler'),
    ('P1', 'ÖK §4.8 P1 mevcut-tümü-geçerli: W = desteklenen tümü; R = ∅; çoklu imzalı (General JSON) nesneler'),
    ('L4-YOL', 'B2: L4 + x5c yolunun bütün sertifika imzaları PQ olmalı (ÖK §2D m.13 yol_sinifi); yalnız X5C vektörleri'),
    ('GEC@-19', 'GEC, sdjwtvc_surum = -19 (MR3)'),
    ('L4@-19', 'L4, sdjwtvc_surum = -19 (MR3)'),
])


def W_R(cfg, X):
    base = cfg.split('@')[0]
    if base in ('GEC', 'P0', 'P1'):
        return set(DESTEKLENEN), set()
    if base == 'IZIN-A':
        return {A}, set()
    if base == 'IZIN-AX':
        return {A, X}, set()
    if base in ('L4', 'L4-S', 'L4-Y', 'L4-YOL'):
        return {A, X}, {X}
    raise KeyError(cfg)


def uc_degerli_ve(*xs):
    if any(x is False for x in xs):
        return False
    if any(x is None for x in xs):
        return None
    return True


def imza_kumesi_karari(imzalar, cfg, X):
    """imzalar: [(alg, gecerli, neden, aciklama)]. Donus: (karar, neden_anahtarlari, not)."""
    base = cfg.split('@')[0]
    W, R = W_R(cfg, X)
    nedenler = []
    notlar = []

    def etiket_klasik_mi(kume):
        return not any(a in PQ for a, _, _, _ in kume)

    if base in ('GEC', 'IZIN-A', 'IZIN-AX'):
        # tek imza varsayimi (uygulanabilirlik bunu saglar); coklu olursa P1 gibi degerlendir
        dis = [s for s in imzalar if s[0] not in W]
        if dis:
            return ('reject', ['BCP31-izin', 'JWS52-enaz'] + (['OK413-L1'] if base.startswith('IZIN') else []),
                    'alg %s izin kümesi W=%s dışında' % (','.join(s[0] for s in dis), sorted(W)))
        g = uc_degerli_ve(*[s[1] for s in imzalar])
        for s in imzalar:
            nedenler += s[2]
        if g is False:
            return ('reject', nedenler or ['JWS52-8'], '; '.join(s[3] for s in imzalar if s[1] is False))
        if g is None:
            return ('indeterminate', nedenler, '; '.join(s[3] for s in imzalar if s[1] is None))
        return ('accept-classical' if etiket_klasik_mi(imzalar) else 'accept-hybrid', [], 'imza(lar) geçerli; alg ∈ W')

    if base == 'P0':
        gecerli = [s for s in imzalar if s[0] in W and s[1] is True]
        belirsiz = [s for s in imzalar if s[0] in W and s[1] is None]
        if gecerli:
            klasik = [s for s in gecerli if s[0] not in PQ]
            if klasik:
                return ('accept-classical', ['OK48-P0', 'JWS52-uygulama'], 'en az bir geçerli imza var; kabul için klasik %s yeterli' % klasik[0][0])
            if belirsiz:
                return ('indeterminate', ['OK48-P0'], 'geçerli imzalar yalnız PQ; belirsiz klasik imza etiketi belirsizleştiriyor')
            return ('accept-hybrid', ['OK48-P0'], 'geçerli imzaların hepsi PQ')
        if belirsiz:
            return ('indeterminate', ['OK48-P0'] + sum([s[2] for s in belirsiz], []), '; '.join(s[3] for s in belirsiz))
        return ('reject', ['OK48-P0', 'JWS52-enaz'], 'hiçbir imza geçerli değil')

    if base == 'P1':
        dis = [s for s in imzalar if s[0] not in W]
        gecersiz = [s for s in imzalar if s[0] in W and s[1] is False]
        belirsiz = [s for s in imzalar if s[0] in W and s[1] is None]
        if dis or gecersiz:
            k = ['OK48-P1']
            for s in dis + gecersiz:
                k += s[2]
            return ('reject', k, 'mevcut imzaların tümü geçerli değil: ' + '; '.join('%s: %s' % (s[0], s[3]) for s in dis + gecersiz))
        if belirsiz:
            return ('indeterminate', ['OK48-P1'] + sum([s[2] for s in belirsiz], []), '; '.join(s[3] for s in belirsiz))
        return ('accept-classical' if etiket_klasik_mi(imzalar) else 'accept-hybrid', ['OK48-P1', 'ACM2-51'],
                'mevcut imzaların tümü geçerli' + ('' if etiket_klasik_mi(imzalar) else '; aralarında PQ imza var, kabul PQ doğrulamasını içerir'))

    # L4 ailesi
    def l4(varyant):
        kume = imzalar if varyant == 'S' else [s for s in imzalar if s[0] in W]
        dis = [s for s in imzalar if s[0] not in W]
        k = ['OK65-pol', 'BCP31-ihracci', 'OK47-G5']
        if varyant == 'S' and dis:
            return ('reject', k + ['OK48-P3', 'OK48-P1', 'ACM2-51', 'JWS52-alg', 'BCP31-izin'],
                    'S: W dışı imza var (%s) → mevcut-tümü-geçerli koşulu sağlanmaz' % ','.join(s[0] for s in dis))
        gecersiz = [s for s in kume if s[1] is False]
        if gecersiz:
            kk = k + ['BCP33']
            for s in gecersiz:
                kk += s[2]
            return ('reject', kk, 'W içinde geçersiz imza: ' + '; '.join('%s: %s' % (s[0], s[3]) for s in gecersiz))
        r_durum = {}
        for r in R:
            adaylar = [s for s in kume if s[0] == r]
            if any(s[1] is True for s in adaylar):
                r_durum[r] = True
            elif not adaylar:
                r_durum[r] = False
            else:
                r_durum[r] = None
        if any(v is False for v in r_durum.values()):
            return ('reject', k + ['OK413-L4'], 'gerekli küme R=%s karşılanmıyor (yalnız %s)' % (sorted(R), ','.join(s[0] for s in kume) or 'hiç imza yok'))
        belirsiz = [s for s in kume if s[1] is None]
        if belirsiz or any(v is None for v in r_durum.values()):
            kk = list(k)
            for s in belirsiz:
                kk += s[2]
            return ('indeterminate', kk, '; '.join(s[3] for s in belirsiz))
        etiket = 'accept-hybrid' if X in PQ else 'accept-classical'
        notu = 'R={%s} geçerli imzayla karşılandı; W içindeki imzalar geçerli' % X
        if varyant == 'Y' and dis:
            notu += '; Y: W dışı ek imza(lar) yok sayıldı (%s)' % ','.join(s[0] for s in dis)
            k = k + ['JWS52-uygulama', 'BCP31-izin']
        if X not in PQ:
            notu += '; kontrol kolu: X klasik'
        return (etiket, k, notu)

    if base == 'L4-S':
        return l4('S')
    if base == 'L4-Y':
        return l4('Y')
    if base in ('L4', 'L4-YOL'):
        s_, y_ = l4('S'), l4('Y')
        if s_[0] == y_[0]:
            return (s_[0], s_[1] + [x for x in y_[1] if x not in s_[1]], s_[2] if s_[2] == y_[2] else s_[2] + ' || ' + y_[2])
        return ('indeterminate', ['OK65-K5', 'OK-MR2', 'JWS52-uygulama', 'JWS52-alg'],
                'ÖK §6.5 K5 "politikaya göre": S → %s, Y → %s (W dışı ek imza: %s)' % (
                    s_[0], y_[0], ','.join(s[0] for s in imzalar if s[0] not in W)))
    raise KeyError(cfg)


def birlestir(karar, ek):
    """Imza kararina yapisal/ek bir kosul uygular. ek: None ya da (tur, neden, not)
    tur: 'red' (her kosulda red), 'belirsiz' (kabul ise belirsizlestirir), 'bilgi'."""
    if ek is None:
        return karar
    tur, nedenler, notu = ek
    k, n, t = karar
    if tur == 'red':
        return ('reject', nedenler + [x for x in n if x not in nedenler], notu + (' || imza düzeyi: %s (%s)' % (k, t) if k != 'reject' else ' || ' + t))
    if tur == 'belirsiz':
        if k == 'reject':
            return (k, n, t + ' || ayrıca: ' + notu)
        return ('indeterminate', n + [x for x in nedenler if x not in n], notu + ' || imza düzeyi: %s (%s)' % (k, t))
    if tur == 'bilgi':  # karari etkilemez ama dayanagin parcasidir
        return (k, n + [x for x in nedenler if x not in n], t + ' || ' + notu)
    if tur == 'not':  # yalniz not; madde anisi kisa bicimde nota yazilir, dayanaga girmez
        return (k, n, t + ' || ' + notu + ' ' + kisa(*nedenler))
    raise ValueError(tur)


# ---------------------------------------------------------------------------
# 5. Aileye ozgu kurallar
# ---------------------------------------------------------------------------
KAPSAM_YALNIZ_GEC = {'kapsam-pq', 'kapsam-hibrit'}


def ana_imzalar(vid, v, d):
    ins = v.get('insa') or {}
    if vid == 'VC10_ikili_ihrac':
        s = ins['kimlik_bilgileri'][0]
        return [(s['alg'],) + imza_durumu(vid, s)]
    return [(s['alg'],) + imza_durumu(vid, s) for s in (ins.get('imzalar') or [])]


def aile_ek(vid, v, d, cfg):
    """Imza kumesi disindaki (yapisal) kosullar."""
    fam = v['aile']
    surum = '-19' if cfg.endswith('@-19') else '-13'
    ek = []
    if fam in ('VC', 'X5C', 'CRIT', 'VP'):
        # SD-JWT VC typ
        if vid == 'VC10_ikili_ihrac':
            typ = d['kimlik_bilgileri'][0]['korumali'].get('typ')
        else:
            typ = d['imzalar'][0]['korumali'].get('typ')
        if typ == 'vc+sd-jwt':
            if surum == '-13':
                ek.append(('bilgi', ['VC13-typ', 'VC13-gecis'], '-13: typ=vc+sd-jwt; doğrulayıcıların geçiş döneminde kabul etmesi RECOMMENDED (SHOULD düzeyi)'))
            else:
                ek.append(('red', ['VC19-typ', 'SD911'], '-19: typ MUST dc+sd-jwt; geçiş notu -19\'da kaldırıldı; doğrulayıcının typ denetimi RECOMMENDED (SHOULD düzeyi red)'))
        if v['serilestirme'] in ('sd-jwt-general', 'sd-jwt-flattened'):
            ek.append(('not', ['SD8-opsiyon', 'VC13-json' if surum == '-13' else 'VC19-json', 'HAIP61-json', 'OK413-B6'],
                       'JSON serileştirme isteğe bağlı: destekleyen hedef için karar; desteklemeyen hedefte B6 (uygulanamaz)'))
    if fam == 'X5C':
        x = v['insa']['x5c']
        if vid in ('X5C07_korumasiz_x5c', 'X5C08_korumasiz_x5c_zincir_degisimi'):
            ek.append(('red', ['VC13-x5c', 'VC19-x5c', 'VC19-red', 'JWS6', 'VC19-73', 'OK2D-x5c'],
                       'x5c yalnız korumasız başlıkta: X.509 anahtar mekanizması yalnız korumalı başlıktaki x5c için tanımlı; güven kararında korumasız bilgi kullanılamaz; izinli mekanizmayla anahtar doğrulanamaz → MUST red (B3 = korumasız x5c işlenirse 1)'))
        if vid == 'X5C09_korumali_ve_korumasiz_x5c':
            ek.append(('red', ['JWS721-ayrik', 'JWS52-4'], 'x5c hem korumalı hem korumasız başlıkta: başlık adları ayrık olmalı → doğrulama adımı başarısız'))
        if vid == 'X5C06_guven_capasi_x5c_icinde':
            ek.append(('belirsiz', ['HAIP611-capa', 'JWS416'], 'güven çapası x5c içinde: HAIP üreticiye MUST NOT der, doğrulayıcının tepkisi yazılı değil; RFC 5280 yolu yine kurulur'))
        if vid == 'X5C10_x5c_ve_baska_anahtar_kid':
            ek.append(('belirsiz', ['VC19-x5c', 'BCP31-anahtar'], 'kid başka anahtarı (issuer/ES256) gösteriyor: SD-JWT VC anahtarı x5c yaprağından alır (kabul yönü), 8725bis kid ile belirlenen anahtarın alg uyumunu ister (red yönü)'))
        if cfg.startswith('L4-YOL'):
            sinif = x.get('sinif')
            if vid == 'X5C09_korumali_ve_korumasiz_x5c':
                sinif = 'tam-pq'  # korumali zincir; yine de ayriklik ihlaliyle red
            if sinif != 'tam-pq':
                ek.append(('red', ['OK2D-yol', 'CMP62-sertifika', 'JWS416'], 'yol sınıfı "%s": yolun en az bir kenarı klasik imzalı → B2 politikası reddeder' % sinif))
            else:
                ek.append(('bilgi', ['OK2D-yol'], 'yol sınıfı tam-PQ'))
        else:
            ek.append(('bilgi', ['OK2D-x5c', 'JWS416'], 'anahtar x5c + güven çapalarıyla (root-ec, root-ml) çözülür; zincir sınıfı %s; yol politikası yok' % x.get('sinif', 'korumalı: tam-pq / korumasız: karışık')))
    if fam == 'CRIT':
        crit = v['insa']['crit']
        if vid in ('CRIT01_bilinmeyen_parametre', 'CRIT05_listelenen_parametre_yok'):
            ek.append(('red', ['JWS4111-crit'], 'crit=%s: listelenen uzantı anlaşılmıyor → JWS geçersiz' % crit))
        elif vid == 'CRIT02_korumasiz_crit':
            ek.append(('red', ['JWS4111-crit', 'JWS4111-korumali'], 'crit korumasız başlıkta ve listelenen uzantı anlaşılmıyor → JWS geçersiz'))
        else:
            ek.append(('belirsiz', ['JWS4111-MAY'], 'crit=%s: RFC 7515 alıcıya yalnız MAY ile geçersiz sayma izni verir' % crit))
    if fam == 'VP':
        kb = v['insa'].get('kb_jwt') or {}
        ek.append(('bilgi', ['HAIP6111'], 'KB-JWT gerekli; KB alg=%s (P-L4 ihraççı politikası KB algoritmasını kısıtlamaz; etiket ihraççı imzasına göredir)' % kb.get('alg')))
        if v['serilestirme'] == 'sd-jwt-general' and len(v['insa']['imzalar']) > 1:
            ek.append(('belirsiz', ['SD81-sdhash', 'SD73-sdhash', 'OK2D-kb'],
                       'General JSON + birden çok ihraççı imzası: sd_hash için geçici compact biçimin hangi imzayla kurulacağı tanımsız (insa: sd_hash_imza_sirasi=%s, 0-tabanlı)' % kb.get('sd_hash_imza_sirasi')))
    if fam == 'VC' and vid == 'VC10_ikili_ihrac':
        ek.append(('not', ['OK65-K11'], 'değerlendirilen: credentials[0] (ES256, x5c issuer-ec); PQ kopya (ML-DSA-65) K11 kararına girmez'))
    if fam == 'TSL':
        ek.append(('bilgi', ['TSL51-typ', 'TSL51-imza'], 'typ=statuslist+jwt; sub/iat/exp/ttl geçerli (simdi < exp)'))
        if vid == 'TSL03_composite_kid':
            ek.append(('not', ['HAIP61-tsl', 'OK2D-x5c'], 'composite anahtar kid ile (x5c yok): HAIP §6.1 sapması, ÖK §2D m.1 gereği kabul edilen düzenek'))
    if fam == 'DPOP':
        alg = v['insa']['imzalar'][0]['alg']
        if v['insa'].get('jwk_ozel_uye'):
            ek.append(('red', ['DPOP43-7'], 'jwk başlığı özel anahtar (priv) içeriyor'))
        if alg not in KAYITLI:
            ek.append(('red', ['DPOP43-5', 'CMP71-talep'], 'alg %s IANA JOSE kaydında değil (composite -04 yalnız kayıt talebi); RFC 9449 kayıtlı algoritma ister (kayıt olursa karar accept-hybrid olur)' % alg))
        ek.append(('bilgi', ['DPOP43-11'], 'iat = simdi − 10 s; htm/htu eşleşiyor; sunucu nonce/erişim belirteci vermedi (nonce/ath denetimi uygulanmaz)'))
    if fam == 'REQ':
        ek.append(('bilgi', ['VP593-takdir'], 'cüzdan tarafı (Adım 11); yapılandırma "cüzdan imzaları doğrular" varsayar'))
        if vid in ('REQ01_imzali_ES256_x509_hash', 'REQ02_imzali_MLDSA65_x509_hash', 'REQ04_coklu_imzali', 'REQ05_coklu_imzali_pq_soyuldu', 'REQ06_coklu_imzali_klasik_soyuldu', 'REQ07_coklu_imzali_pq_bozuk', 'REQ04_coklu_imzali-SIRA-ters'):
            ek.append(('bilgi', ['VP593-x509'], 'x509_hash: imza ve yaprak zinciri doğrulanır (inşa gereği hash ve zincir tutarlı)'))
        if vid == 'REQ03_imzali_composite_onkayitli':
            ek.append(('not', ['HAIP5-x509'], 'önkayıtlı istemci (M-d), x509_hash değil: HAIP §5 doğrulayıcı yükümlülüğünden sapma (composite X.509 yok)'))
        if vid == 'REQ10_istek_alg_none':
            ek.append(('red', ['VP593-x509', 'BCP32-none'], 'imzalı istek protokolünde alg=none: x509_hash imzası doğrulanamaz'))
        if vid in ('REQ04_coklu_imzali', 'REQ04_coklu_imzali-SIRA-ters', 'REQ05_coklu_imzali_pq_soyuldu', 'REQ06_coklu_imzali_klasik_soyuldu', 'REQ07_coklu_imzali_pq_bozuk'):
            ek.append(('bilgi', ['VPA322', 'JWS52-uygulama'], 'A.3.2.2: hangi imzaların doğrulanacağı cüzdanın güven çerçevesi politikasına bırakılmış'))
    return ek


def karar_ver(vid, cfg, kol):
    v = VEKTOR[vid]
    d = COZUM[vid]
    X = KOLLAR.get(kol, None)
    fam = v['aile']
    # imzasiz DC API istekleri (REQ08/09)
    if fam == 'REQ' and v['serilestirme'] == 'dcapi-json-parametre':
        if cfg.split('@')[0] == 'GEC':
            k = ('accept-classical', ['HAIP52-imzasiz', 'HAIP52-webpki'] + (['VPA2-clientid'] if 'client_id' in d['veri'] else []),
                 'imzasız istek (openid4vp-v1-unsigned): RP kimliği yalnız köken/Web PKI ile (klasik)' + ('; client_id yok sayılır' if 'client_id' in d['veri'] else ''))
        else:
            k = ('reject', ['OK65-pol', 'OK47-G5', 'HAIP52-webpki'] + (['VPA2-clientid'] if 'client_id' in d['veri'] else []),
                 'imzasız istek: RP için R={%s} PQ kimlik doğrulaması sağlanamaz' % X)
        for e in aile_ek(vid, v, d, cfg):
            k = birlestir(k, e)
        return k
    imz = ana_imzalar(vid, v, d)
    Xeff = X
    if fam == 'X5C' and kol == 'tedavi-composite':
        Xeff = 'ML-DSA-65'  # OK §2F m.4 uyarlamasi: K8/K9 kol-bagimsiz, ML-DSA-65 yaprakla
    if Xeff is None:
        Xeff = 'ML-DSA-65'  # yalniz GEC/P0/P1'de kullanilir (W/R X'ten bagimsiz)
    k = imza_kumesi_karari(imz, cfg, Xeff)
    for e in aile_ek(vid, v, d, cfg):
        k = birlestir(k, e)
    if fam == 'X5C' and kol == 'tedavi-composite':
        k = (k[0], k[1] + ['OK2F-K8'], k[2] + ' || composite kolunda ÖK §2F m.4 uyarlaması: politika X=ML-DSA-65 ile örneklendi (composite X.509 kapsam dışı)')
    return k


# ---------------------------------------------------------------------------
# 6. Insa denetimi (base64url cozumu; kripto yok)
# ---------------------------------------------------------------------------
COZUM = {}
for vid, v in VEKTOR.items():
    d = cozum(v)
    COZUM[vid] = d
    fam = v['aile']
    # zaman: exp > simdi >= iat
    yuklar = []
    if d.get('yuk'):
        yuklar.append(d['yuk'])
    for c in d.get('kimlik_bilgileri', []):
        yuklar.append(c['yuk'])
    for y in yuklar:
        if isinstance(y, dict) and 'exp' in y:
            denetle(vid, 'exp > simdi', y['exp'] > SIMDI)
        if isinstance(y, dict) and 'iat' in y:
            denetle(vid, 'iat <= simdi', y['iat'] <= SIMDI)
    if 'kb' in d:
        denetle(vid, 'KB typ=kb+jwt', d['kb']['baslik'].get('typ') == 'kb+jwt')
        denetle(vid, 'KB iat penceresi (<=600 s)', 0 <= SIMDI - d['kb']['yuk']['iat'] <= 600)
        denetle(vid, 'KB aud/nonce = dogrulama_girdileri', d['kb']['yuk']['aud'] == v['dogrulama_girdileri']['kb_aud'] and d['kb']['yuk']['nonce'] == v['dogrulama_girdileri']['kb_nonce'])
    # imza sayisi ve alg'ler manifestle ayni
    ins = v.get('insa') or {}
    if ins.get('imzalar') is not None and fam != 'REQ' or (fam == 'REQ' and v['serilestirme'] != 'dcapi-json-parametre'):
        m_alg = [s['alg'] for s in ins.get('imzalar', [])]
        d_alg = [s['korumali'].get('alg') for s in d['imzalar']]
        denetle(vid, 'imza alg dizisi manifestle ayni %s' % m_alg, m_alg == d_alg)
    if fam in ('VC', 'X5C', 'CRIT', 'VP') and vid != 'VC10_ikili_ihrac':
        beklenen = 'vc+sd-jwt' if vid == 'VC11_typ_vc+sd-jwt' else 'dc+sd-jwt'
        for s in d['imzalar']:
            denetle(vid, 'typ=' + beklenen, s['korumali'].get('typ') == beklenen)
    if vid == 'VC10_ikili_ihrac':
        denetle(vid, 'credentials[0] ES256 dc+sd-jwt', d['kimlik_bilgileri'][0]['korumali']['alg'] == 'ES256' and d['kimlik_bilgileri'][0]['korumali']['typ'] == 'dc+sd-jwt')
    if fam == 'X5C':
        h = d['imzalar'][0]
        kor = 'x5c' in h['korumali']
        kz = bool(h['korumasiz']) and 'x5c' in h['korumasiz']
        if vid in ('X5C07_korumasiz_x5c', 'X5C08_korumasiz_x5c_zincir_degisimi'):
            denetle(vid, 'x5c yalniz korumasiz', (not kor) and kz)
        elif vid == 'X5C09_korumali_ve_korumasiz_x5c':
            denetle(vid, 'x5c hem korumali hem korumasiz', kor and kz)
        else:
            denetle(vid, 'x5c korumali', kor and not kz)
        if vid == 'X5C06_guven_capasi_x5c_icinde':
            denetle(vid, 'x5c 3 sertifika', len(h['korumali']['x5c']) == 3)
        if vid == 'X5C10_x5c_ve_baska_anahtar_kid':
            denetle(vid, 'kid = issuer/ES256', h['korumali'].get('kid') == 'Dae-6PSSx7FfaEPNMopZGZ-wBvY8xkwyPQHmeHIgaUU')
    if fam == 'CRIT':
        h = d['imzalar'][0]
        crit_yer = 'korumali' if 'crit' in h['korumali'] else 'korumasiz'
        denetle(vid, 'crit yeri', (crit_yer == 'korumasiz') == (vid == 'CRIT02_korumasiz_crit'))
    if fam == 'DPOP':
        h = d['imzalar'][0]['korumali']
        y = d['yuk']
        denetle(vid, 'typ dpop+jwt', h.get('typ') == 'dpop+jwt')
        denetle(vid, 'DPoP iat penceresi', 0 <= SIMDI - y['iat'] <= 600)
        denetle(vid, 'htm/htu', y['htm'] == v['dogrulama_girdileri']['htm'] and y['htu'] == v['dogrulama_girdileri']['htu'])
        denetle(vid, 'jwk priv yalniz DPOP10', ('priv' in h['jwk']) == (vid == 'DPOP10_jwk_ozel_anahtar_iceriyor'))
    if fam == 'TSL':
        h = d['imzalar'][0]['korumali']
        denetle(vid, 'typ statuslist+jwt', h.get('typ') == 'statuslist+jwt')
        denetle(vid, 'sub = status uri', d['yuk']['sub'] == 'https://issuer.example/statuslists/1')
    if fam == 'K10':
        h = d['imzalar'][0]['korumali']
        jwk = v['dogrulama_girdileri']['jwk']
        denetle(vid, 'kid = dg jwk kid', h.get('kid') == jwk['kid'])
        eslesme = {'ES256': ('EC', None), 'EdDSA': ('OKP', None), 'Ed25519': ('OKP', None), 'ML-DSA-65': ('AKP', 'ML-DSA-65'), 'ML-DSA-65-ES256': ('AKP', 'ML-DSA-65-ES256')}
        kty, kalg = eslesme[h['alg']]
        denetle(vid, 'baslik alg ile anahtar turu uyusmuyor', not (jwk['kty'] == kty and (kalg is None or jwk.get('alg') == kalg)))
    if fam == 'REQ' and v['serilestirme'] == 'dcapi-json-parametre':
        denetle(vid, 'protokol openid4vp-v1-unsigned', d['protokol'] == 'openid4vp-v1-unsigned')

# ---------------------------------------------------------------------------
# 7. Esleme: birincil / ikincil (BATARYA-ESLEME.md; kimlikler dosyada aranir)
# ---------------------------------------------------------------------------
ESLEME_METIN = open(ESLEME_YOL, encoding='utf-8').read()
KK, KE, KP, KC = 'kontrol-EdDSA', 'kontrol-Ed25519', 'tedavi-ML-DSA-65', 'tedavi-composite'
BIRINCIL = [  # (vaka, kol, vektor)
    ('K1', KK, 'T1K_both_valid'), ('K1', KE, 'T1K_both_valid-ED25519'), ('K1', KP, 'T1P_both_valid'), ('K1', KC, 'T1C_both_valid'),
    ('K2', KK, 'T2K_second_tampered'), ('K2', KE, 'T2K_second_tampered-ED25519'), ('K2', KP, 'T2P_second_tampered'), ('K2', KC, 'T2C_second_tampered'),
    ('K3', KK, 'T3_stripped_to_ES256'), ('K3', KE, 'T3_stripped_to_ES256'), ('K3', KP, 'T3_stripped_to_ES256'), ('K3', KC, 'T3_stripped_to_ES256'),
    ('K4', KK, 'T5K_only_EdDSA'), ('K4', KE, 'T5K_only_EdDSA-ED25519'), ('K4', KP, 'T5P_only_ML-DSA-65'), ('K4', KC, 'T5C_only_ML-DSA-65-ES256'),
    ('K5', KK, 'T7K_plus_kayitsiz'), ('K5', KE, 'T7K_plus_kayitsiz-ED25519'), ('K5', KP, 'T7P_plus_kayitsiz'), ('K5', KC, 'T7C_plus_kayitsiz'),
    ('K6', KC, 'CMP00_gecerli_referans'),
    ('K7', KC, 'CMP01_ml_bileseni_bozuk'), ('K7', KC, 'CMP02_ecdsa_bileseni_bozuk'),
    ('K8', KP, 'X5C04_karisik_pq_yaprak_klasik_ara'), ('K8', KC, 'X5C04_karisik_pq_yaprak_klasik_ara'),
    ('K9', KP, 'X5C07_korumasiz_x5c'), ('K9', KC, 'X5C07_korumasiz_x5c'),
    ('K10', KK, 'K10K_alg-EdDSA_anahtar-ES256'), ('K10', KE, 'K10K_alg-EdDSA_anahtar-ES256-ED25519'),
    ('K10', KK, 'K10K_alg-ES256_anahtar-Ed25519'), ('K10', KE, 'K10K_alg-ES256_anahtar-Ed25519'),
    ('K10', KP, 'K10P_alg-ML-DSA-65_anahtar-ES256'), ('K10', KP, 'K10P_alg-ES256_anahtar-ML-DSA-65'),
    ('K10', KC, 'K10C_alg-ML-DSA-65-ES256_anahtar-ML-DSA-65'), ('K10', KC, 'K10C_alg-ML-DSA-65_anahtar-ML-DSA-65-ES256'),
    ('K11', KK, 'VC10_ikili_ihrac'), ('K11', KE, 'VC10_ikili_ihrac'), ('K11', KP, 'VC10_ikili_ihrac'), ('K11', KC, 'VC10_ikili_ihrac'),
    ('V+', KK, 'VPLUS_ES256'), ('V+', KK, 'VPLUS_EdDSA'), ('V+', KE, 'VPLUS_ES256'), ('V+', KE, 'VPLUS_EdDSA-ED25519'),
    ('V+', KP, 'VPLUS_ES256'), ('V+', KP, 'VPLUS_ML-DSA-65'), ('V+', KC, 'VPLUS_ES256'), ('V+', KC, 'CMP00_gecerli_referans'),
    ('V-', KK, 'VMINUS_ES256'), ('V-', KK, 'VMINUS_EdDSA'), ('V-', KE, 'VMINUS_ES256'), ('V-', KE, 'VMINUS_EdDSA-ED25519'),
    ('V-', KP, 'VMINUS_ES256'), ('V-', KP, 'VMINUS_ML-DSA-65'), ('V-', KC, 'VMINUS_ES256'), ('V-', KC, 'CMP01_ml_bileseni_bozuk'),
]
IKINCIL = [
    ('K1', KK, 'VC09_GJ_ES256_EdDSA'), ('K1', KE, 'VC09_GJ_ES256_EdDSA-ED25519'), ('K1', KP, 'VC07_GJ_ES256_MLDSA65'), ('K1', KC, 'VC08_GJ_ES256_composite'),
    ('K3', KP, 'VP06_GJ_pq_soyuldu_kb_gecerli'),
    ('K5', KK, 'T4K_plus_ML-DSA-65'), ('K5', KE, 'T4K_plus_ML-DSA-65-ED25519'), ('K5', KK, 'T6_plus_composite'), ('K5', KE, 'T6_plus_composite-ED25519'),
    ('K5', KP, 'T4P_plus_ML-DSA-65-ES256'), ('K5', KP, 'UNK04_general_arti_kayitsiz_composite'), ('K5', KP, 'UNK05_general_arti_alg_none'), ('K5', KC, 'T4C_plus_ML-DSA-65'),
    ('K6', KC, 'T5C_only_ML-DSA-65-ES256'), ('K6', KC, 'VC03_composite_kid'),
] + [('K7', KC, c) for c in ['CMP03_ecdsa_der_uzunluk_bozuk', 'CMP04_ecdsa_ham_rs', 'CMP05_ecdsa_asgari_olmayan_der', 'CMP06_sonda_artik_bayt',
                            'CMP07_yalniz_ml_bileseni', 'CMP08_bilesenler_farkli_iletilerden', 'CMP09_ml_bileseni_ctx_bos', 'CMP10_onozet_sha256',
                            'CMP11_bos_ctx_uzunlugu_yok', 'CMP16_bilesen_sirasi_ters']] + [
    ('K8', KP, 'X5C03_karisik_klasik_yaprak_pq_ara'), ('K8', KP, 'X5C05_karisik_pq_ara_klasik_kok'),
    ('K9', KP, 'X5C08_korumasiz_x5c_zincir_degisimi'), ('K9', KP, 'X5C09_korumali_ve_korumasiz_x5c'),
    ('K10', KC, 'CMP12_ayrilabilirlik_ecdsa_ES256'), ('K10', KC, 'CMP13_ayrilabilirlik_ml_MLDSA65'),
    ('K11', KK, 'VC01_ES256_x5c'), ('K11', KE, 'VC01_ES256_x5c'), ('K11', KP, 'VC01_ES256_x5c'), ('K11', KC, 'VC01_ES256_x5c'),
]
MR = [  # (mr, kol, vektor, cift)
    ('MR1', KK, 'T1K_both_valid', 'T3_stripped_to_ES256'), ('MR1', KE, 'T1K_both_valid-ED25519', 'T3_stripped_to_ES256'),
    ('MR1', KP, 'T1P_both_valid', 'T3_stripped_to_ES256'), ('MR1', KC, 'T1C_both_valid', 'T3_stripped_to_ES256'),
    ('MR1', KP, 'VP05_GJ_ES256_MLDSA65_kb', 'VP06_GJ_pq_soyuldu_kb_gecerli'), ('MR1', KP, 'REQ04_coklu_imzali', 'REQ05_coklu_imzali_pq_soyuldu'),
    ('MR2', KK, 'T1K_both_valid', 'T7K_plus_kayitsiz'), ('MR2', KE, 'T1K_both_valid-ED25519', 'T7K_plus_kayitsiz-ED25519'),
    ('MR2', KP, 'T1P_both_valid', 'T7P_plus_kayitsiz'), ('MR2', KC, 'T1C_both_valid', 'T7C_plus_kayitsiz'),
    ('MR2', KK, 'T1K_both_valid', 'T4K_plus_ML-DSA-65'), ('MR2', KK, 'T1K_both_valid', 'T6_plus_composite'),
    ('MR2', KP, 'T1P_both_valid', 'T4P_plus_ML-DSA-65-ES256'), ('MR2', KC, 'T1C_both_valid', 'T4C_plus_ML-DSA-65'),
    ('MR3', KK, 'VC09_GJ_ES256_EdDSA', 'VC09_GJ_ES256_EdDSA'), ('MR3', KE, 'VC09_GJ_ES256_EdDSA-ED25519', 'VC09_GJ_ES256_EdDSA-ED25519'),
    ('MR3', KP, 'VC07_GJ_ES256_MLDSA65', 'VC07_GJ_ES256_MLDSA65'), ('MR3', KC, 'VC08_GJ_ES256_composite', 'VC08_GJ_ES256_composite'),
    ('MR3', None, 'VC01_ES256_x5c', 'VC11_typ_vc+sd-jwt'),
]
for _, _, vid in BIRINCIL + IKINCIL:
    if vid not in ESLEME_METIN or vid not in VEKTOR:
        sys.exit('ESLEMEDE/MANIFESTTE YOK: ' + vid)


def sinif_vaka(vid, kol):
    vb = sorted({c for c, k, x in BIRINCIL if x == vid and k == kol})
    vi = sorted({c for c, k, x in IKINCIL if x == vid and k == kol})
    mr = sorted({m for m, k, a, b in MR if (a == vid or b == vid) and (k == kol or k is None)})
    v = VEKTOR[vid]
    mr4 = (v.get('insa') or {}).get('mr4')
    parca = vb + ['%s(ikincil)' % c for c in vi] + mr
    if mr4:
        tanim = 'MR4-dışı tanımlayıcı' if 'MR4-kapsam-disi(tanimlayici): sd_hash-baglamasi-degisir' in v['sinanan']['ek_etiketler'] else 'MR4'
        parca.append('%s(%s)' % (tanim, mr4['kaynak_vektor']))
    if not parca:
        parca = ['eşleme-dışı']
    return ('birincil' if vb else 'ikincil'), ';'.join(parca)


# ---------------------------------------------------------------------------
# 8. Uygulanabilirlik: (vektor -> [(yapilandirma, kol)])
# ---------------------------------------------------------------------------
def tum_kollar():
    return list(KOLLAR.keys())


def kollar_for(vid, v):
    kol = v['kol']
    # ESLEME'de birden cok kol sutununda gecen vektorler (manifest kolundan once)
    if kol == 'ortak' or vid in ('VC10_ikili_ihrac', 'VC01_ES256_x5c', 'VC11_typ_vc+sd-jwt'):
        return tum_kollar()
    if vid in ('X5C04_karisik_pq_yaprak_klasik_ara', 'X5C07_korumasiz_x5c'):
        return [KP, KC]
    if kol in KOLLAR:
        # EdDSA etiketi icermeyen kontrol vektorleri (esi yok) yedek kolda aynen kullanilir;
        # EdDSA etiketli her kontrol vektorunun '-ED25519' esi bulunmali.
        if kol == KK:
            etiketler = [s['alg'] for s in (v.get('insa') or {}).get('imzalar', [])]
            ikiz = (vid + '-ED25519') in VEKTOR
            if 'EdDSA' in etiketler and not ikiz and v['aile'] != 'DPOP':
                sys.exit('ED25519 ESI YOK: ' + vid)
            if 'EdDSA' not in etiketler and not ikiz:
                return [KK, KE]
        return [kol]
    if kol == 'ortak' or vid in ('VC10_ikili_ihrac', 'VC01_ES256_x5c', 'VC11_typ_vc+sd-jwt'):
        return tum_kollar()
    if vid in ('X5C04_karisik_pq_yaprak_klasik_ara', 'X5C07_korumasiz_x5c'):
        return [KP, KC]
    if kol == 'klasik-taban':
        return [KP]
    if v['aile'] == 'REQ' and kol is None:
        return [KP]
    return []


def uygulama(vid):
    v = VEKTOR[vid]
    fam = v['aile']
    ser = v['serilestirme']
    ins = v.get('insa') or {}
    n_imza = len(ins.get('imzalar') or []) if vid != 'VC10_ikili_ihrac' else 1
    cift = []
    # yalniz GEC: TSL, DPOP, kapsam vektorleri, VC12
    if fam in ('TSL', 'DPOP') or v['kol'] in KAPSAM_YALNIZ_GEC or vid == 'VC12_alg_none':
        return [('GEC', v['kol'] or 'yok')]
    kollar = kollar_for(vid, v)
    if fam == 'X5C':
        x5c_kollar = kollar if kollar else [KP]
        # GEC kolu bagimsiz; X5C icin tek satir (tedavi-ML-DSA-65)
        cift += [('GEC', KP)]
        for c in ('L4', 'L4-S', 'L4-Y', 'L4-YOL'):
            cift += [(c, k) for k in x5c_kollar]
        return cift
    tek = (n_imza <= 1)
    for k in kollar:
        if tek or ser == 'dcapi-json-parametre':
            cift.append(('GEC', k))
        izin_aileleri = ('V', 'K10', 'UNK', 'T', 'CMP')
        if tek and (fam in izin_aileleri or vid in ('VC01_ES256_x5c', 'VC02_MLDSA65_x5c', 'VC03_composite_kid', 'VC10_ikili_ihrac')):
            cift += [('IZIN-A', k), ('IZIN-AX', k)]
        cift += [('L4', k), ('L4-S', k), ('L4-Y', k)]
        if ser in ('general', 'sd-jwt-general'):
            cift += [('P0', k), ('P1', k)]
    # MR3: -19
    if vid in ('VC01_ES256_x5c', 'VC11_typ_vc+sd-jwt'):
        cift += [('GEC@-19', k) for k in kollar]
    if vid in ('VC07_GJ_ES256_MLDSA65', 'VC08_GJ_ES256_composite', 'VC09_GJ_ES256_EdDSA', 'VC09_GJ_ES256_EdDSA-ED25519'):
        cift += [('L4@-19', k) for k in kollar]
    return cift


# ---------------------------------------------------------------------------
# 9. Uretim
# ---------------------------------------------------------------------------
TABAN = {  # her satira eklenen yapilandirma tanimi dayanagi (kararin kendi dayanagindan sonra)
    'GEC': ['OK415-V', 'JWS52-enaz'],
    'IZIN-A': ['OK413-L1', 'BCP31-izin'],
    'IZIN-AX': ['OK413-L1', 'BCP31-izin'],
    'L4': ['OK65-pol', 'OK413-L4'], 'L4-S': ['OK65-pol', 'OK48-P3'], 'L4-Y': ['OK65-pol', 'JWS52-uygulama'],
    'P0': ['OK48-P0'], 'P1': ['OK48-P1'], 'L4-YOL': ['OK65-pol', 'OK2D-yol'],
}
VAKA_MADDE = {'K1': 'OK65-K1', 'K2': 'OK65-K2', 'K3': 'OK65-K3', 'K4': 'OK65-K4', 'K5': 'OK65-K5', 'K6': 'OK65-K6',
              'K7': 'OK65-K7', 'K8': 'OK65-K8', 'K9': 'OK65-K9', 'K10': 'OK65-K10', 'K11': 'OK65-K11'}
L4C_KLASIK = {'VPLUS_ES256', 'T3_stripped_to_ES256', 'VC01_ES256_x5c', 'VC10_ikili_ihrac'}


def taban(cfg, vid, kol):
    b = cfg.split('@')[0]
    t = list(TABAN[b])
    vakalar = {c for c, k, x in BIRINCIL + IKINCIL if x == vid and k == kol}
    if b == 'IZIN-AX':
        if vid.startswith('K10') or vid.startswith('CMP12') or vid.startswith('CMP13'):
            t.append('OK413-L3')
        if vid in L4C_KLASIK:
            t.append('OK2B-L4c')
    if b in ('L4', 'L4-S', 'L4-Y', 'L4-YOL'):
        if vid in L4C_KLASIK or vid in ('VPLUS_EdDSA', 'VPLUS_EdDSA-ED25519', 'VPLUS_ML-DSA-65', 'CMP00_gecerli_referans'):
            t.append('OK2B-L4c')
        for c in sorted(vakalar):
            if c in VAKA_MADDE:
                t.insert(0, VAKA_MADDE[c])
    if b in ('IZIN-A', 'IZIN-AX') and 'K10' in vakalar:
        t.insert(0, 'OK65-K10')
    if b == 'GEC' and vakalar & {'V+', 'V-'}:
        t.insert(0, 'OK65-V')
    return t


satirlar = []
for vid in VEKTOR:
    for cfg, kol in uygulama(vid):
        karar, nedenler, notu = karar_ver(vid, cfg, kol)
        sinif, vaka = sinif_vaka(vid, kol)
        v = VEKTOR[vid]
        ser = v['serilestirme']
        on = 'insa: %s' % ', '.join('%s=%s' % (s[0], {True: 'geçerli', False: 'geçersiz', None: 'belirsiz'}[s[1]]) for s in ana_imzalar(vid, v, COZUM[vid])) if not (v['aile'] == 'REQ' and ser == 'dcapi-json-parametre') else 'insa: imzasız istek'
        tum = list(nedenler) + [t for t in taban(cfg, vid, kol) if t not in nedenler]
        if cfg.endswith('@-19'):
            tum.append('OK-sdjwtvc')
        satirlar.append(OrderedDict([
            ('vektor_id', vid), ('politika', cfg), ('kol', kol), ('sinif', sinif), ('vaka', vaka),
            ('karar', karar), ('dayanak', dayanak(*tum)),
            ('not', on + ' || ' + notu),
        ]))

# Birincil kapsam denetimi: her birincil (vektor, kol) icin gereken yapilandirma satiri var mi?
_var = {(r['vektor_id'], r['politika'], r['kol']) for r in satirlar}
for vaka, kol, vid in BIRINCIL:
    gerek = ['L4']
    if vaka in ('V+', 'V-'):
        gerek += ['GEC']
    if vaka in ('K8', 'K9'):
        gerek += ['L4-YOL']
    for g in gerek:
        if (vid, g, kol) not in _var:
            sys.exit('BIRINCIL SATIR EKSIK: %s %s %s' % (vid, g, kol))

# ---------------------------------------------------------------------------
# 9b. Metamorfik iliskilerin oracle uzerinde oz-denetimi (MR1, MR2, MR4)
# ---------------------------------------------------------------------------
KARAR = {(r['vektor_id'], r['politika'], r['kol']): r['karar'] for r in satirlar}
MR_DENETIM = OrderedDict()
# MR4: permutasyon esi, kaynak vektorle ayni yapilandirma ve kolda ayni karar
mr4_n = 0
for vid, v in VEKTOR.items():
    mr4 = (v.get('insa') or {}).get('mr4')
    if not mr4 or 'MR4-kapsam-disi(tanimlayici): sd_hash-baglamasi-degisir' in v['sinanan']['ek_etiketler']:
        continue
    kaynak = mr4['kaynak_vektor']
    for (a, cfg, kol), k in KARAR.items():
        if a != vid:
            continue
        if KARAR.get((kaynak, cfg, kol)) != k:
            sys.exit('MR4 IHLALI (oracle): %s vs %s %s %s' % (vid, kaynak, cfg, kol))
        mr4_n += 1
MR_DENETIM['MR4_esit_karar_cifti'] = mr4_n
# MR1: gerekli kume karsilanmiyorken soyma kabulu artirmamali (L4 ailesi)
mr1_n = 0
for t1, kol in (('T1K_both_valid', KK), ('T1K_both_valid-ED25519', KE), ('T1P_both_valid', KP), ('T1C_both_valid', KC)):
    for cfg in ('L4', 'L4-S', 'L4-Y'):
        a, b = KARAR[(t1, cfg, kol)], KARAR[('T3_stripped_to_ES256', cfg, kol)]
        if not (a.startswith('accept') and b == 'reject'):
            sys.exit('MR1 IHLALI (oracle): %s %s %s %s' % (t1, cfg, a, b))
        mr1_n += 1
MR_DENETIM['MR1_T1_kabul_T3_red'] = mr1_n
# MR2: S altinda kayitsiz ek imza red; Y altinda T7 karari T1 ile ayni
mr2_n = 0
for t1, t7, kol in (('T1K_both_valid', 'T7K_plus_kayitsiz', KK), ('T1K_both_valid-ED25519', 'T7K_plus_kayitsiz-ED25519', KE),
                    ('T1P_both_valid', 'T7P_plus_kayitsiz', KP), ('T1C_both_valid', 'T7C_plus_kayitsiz', KC)):
    if KARAR[(t7, 'L4-S', kol)] != 'reject' or KARAR[(t7, 'L4-Y', kol)] != KARAR[(t1, 'L4-Y', kol)]:
        sys.exit('MR2 IHLALI (oracle): ' + t7)
    mr2_n += 1
MR_DENETIM['MR2_S_red_Y_esit'] = mr2_n

sutunlar = ['vektor_id', 'politika', 'kol', 'sinif', 'vaka', 'karar', 'dayanak', 'not']
with open(os.path.join(CIKTI, 'karar.tsv'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('\t'.join(sutunlar) + '\n')
    for r in satirlar:
        f.write('\t'.join(str(r[c]).replace('\t', ' ').replace('\n', ' ') for c in sutunlar) + '\n')

with open(os.path.join(CIKTI, 'maddeler.tsv'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('anahtar\tkimlik\tbelge\tbolum\tsurum\turl\tdosya\tsatir\talinti\n')
    for k, m in MADDELER.items():
        url = KORPUS_MAN[m['belge']]['url'] if m['belge'] in KORPUS_MAN else '00-on-kayit/ON-KAYIT-TASLAK.md (SHA-256 dcc84092…)'
        dosya = '00-on-kayit/ON-KAYIT-TASLAK.md' if m['belge'] == 'OK' else 'spec-corpus/metin/%s.txt' % m['belge']
        f.write('\t'.join([k, m['kimlik'], m['belge'], m['bolum'], SURUM[m['belge']], url, dosya, str(m['satir']), _norm(m['alinti'])]) + '\n')

with open(os.path.join(CIKTI, 'insa_denetimi.txt'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('# Insa denetimi: vektor dosyalari yalniz base64url ile cozuldu (kripto yok). %d denetim, hepsi gecti.\n' % len(DENETIM))
    for vid, ac, ok in DENETIM:
        f.write('%s\t%s\t%s\n' % (vid, ac, 'GECTI' if ok else 'KALDI'))

ozet = OrderedDict()
ozet['satir'] = len(satirlar)
ozet['dagilim'] = dict(Counter(r['karar'] for r in satirlar))
ozet['politika_dagilimi'] = {c: dict(Counter(r['karar'] for r in satirlar if r['politika'] == c)) for c in YAPILANDIRMALAR}
ozet['birincil_satir'] = sum(1 for r in satirlar if r['sinif'] == 'birincil')
ozet['birincil_dagilim'] = dict(Counter(r['karar'] for r in satirlar if r['sinif'] == 'birincil'))
ozet['vektor_kapsami'] = len({r['vektor_id'] for r in satirlar})
ozet['madde_sayisi'] = len(MADDELER)
ozet['korpus_belgesi'] = sorted({m['belge'] for m in MADDELER.values() if m['belge'] != 'OK'})
ozet['insa_denetimi'] = len(DENETIM)
ozet['mr_oz_denetim'] = MR_DENETIM
ozet['indeterminate_birincil'] = sorted({(r['vektor_id'], r['politika'], r['kol']) for r in satirlar if r['sinif'] == 'birincil' and r['karar'] == 'indeterminate'})
with open(os.path.join(CIKTI, 'karar_ozet.json'), 'w', encoding='utf-8', newline='\n') as _f:
    json.dump(ozet, _f, ensure_ascii=False, indent=1)
    _f.write('\n')
print(json.dumps(ozet, ensure_ascii=False, indent=1))
