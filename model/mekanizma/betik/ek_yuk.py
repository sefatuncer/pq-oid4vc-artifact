# -*- coding: utf-8 -*-
"""
PQ-OID4VC | Adım 7 görev 8 | mekanizma başına BELİRLENİMCİ ek yük (bayt, ek alım) [Y]
======================================================================================
Tel üzerindeki ek baytlar kodlama kurallarından hesaplanır (ölçüm değildir; süre ölçümü Adım 11'de).
Birincil boyutlar:
  ML-DSA-44/65/87 açık anahtar 1312/1952/2592 B, imza 2420/3309/4627 B
      (draft-ietf-jose-pq-composite-sigs Tablo 1; 01-korpus/metin/JOSECOMP.txt satır 537-545)
  ES256 imzası 64 B (RFC 7518 §3.4 adım 4: "The resulting 64-octet sequence is the JWS Signature value")
  id-ML-DSA-65 = 2.16.840.1.101.3.4.3.18, id-sha256 = 2.16.840.1.101.3.4.2.1 (LAMPSCOMP.txt 3509, 3577)
  vicente eki: id-ce-pqchc-experimental = 1.3.6.1.4.1.65953.1.1 (draft-vicente-lamps-pqchc-02 §4.1)
  reddy eki: id-pe-pqchc = id-pe TBD2 (draft-reddy-lamps-x509-pq-commit-01 §3.2; tek baytlık yay varsayıldı)
  sheffer uzantısı: uint32 algorithm_validity_period (draft-sheffer-tls-pqc-continuity-02 §3.3)
Çıktı: sonuc/ek_yuk.csv
"""
import base64
import csv
import io
import os

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MLDSA = {'ML-DSA-44': (1312, 2420), 'ML-DSA-65': (1952, 3309), 'ML-DSA-87': (2592, 4627)}


def b64u(n):
    """n baytın base64url (dolgusuz) uzunluğu."""
    return len(base64.urlsafe_b64encode(b'\0' * n).rstrip(b'='))


def der_len(n):
    if n < 128:
        return bytes([n])
    b = n.to_bytes((n.bit_length() + 7) // 8, 'big')
    return bytes([0x80 | len(b)]) + b


def tlv(tag, icerik):
    return bytes([tag]) + der_len(len(icerik)) + icerik


def oid(nokta):
    p = [int(x) for x in nokta.split('.')]
    out = bytearray([40 * p[0] + p[1]])
    for v in p[2:]:
        parca = [v & 0x7F]
        v >>= 7
        while v:
            parca.append(0x80 | (v & 0x7F))
            v >>= 7
        out.extend(reversed(parca))
    return tlv(0x06, bytes(out))


def vicente_eki():
    alg = tlv(0x30, oid('2.16.840.1.101.3.4.3.18'))                         # committedAlgorithm
    dig = tlv(0x30, tlv(0x30, oid('2.16.840.1.101.3.4.2.1')) + tlv(0x04, b'\0' * 32))  # DigestInfo (parametre yok)
    zaman = tlv(0x18, b'20301231235959Z')                                  # commitmentNotAfter
    govde = tlv(0x30, alg + dig + zaman)                                   # commitmentValid DEFAULT TRUE: kodlanmaz
    return tlv(0x30, oid('1.3.6.1.4.1.65953.1.1') + tlv(0x04, govde))      # Extension (critical yok)


def reddy_eki():
    govde = tlv(0x30, tlv(0x02, (365).to_bytes(2, 'big')))                  # continuityPeriod = 365 gün
    return tlv(0x30, oid('1.3.6.1.5.5.7.1.99') + tlv(0x04, govde))          # id-pe TBD2: tek baytlık yay


def main():
    pk65, sig65 = MLDSA['ML-DSA-65']
    satir = []

    def ekle(mek, nesne, bayt, alim, formul, kaynak):
        satir.append({'mekanizma': mek, 'nesne': nesne, 'ek_bayt': bayt, 'ek_alim': alim,
                      'formul': formul, 'kaynak': kaynak})

    ph = b64u(len(b'{"alg":"ML-DSA-65"}'))
    imza_nesnesi = len(',{"protected":"","signature":""}') + ph + b64u(sig65)
    ekle('M-b / A.3.2.2', 'imzalı istek (JWS JSON genel), ikinci imza', imza_nesnesi, 0,
         'b64u(korumalı başlık) + b64u(ML-DSA-65 imzası 3309 B) + JSON sarmalayıcı', 'JOSECOMP Tablo 1; RFC 7515 §7.2.1')
    ekle('M-a', 'HTTP başlığı Accept-Signature-Algorithms', len('Accept-Signature-Algorithms: ML-DSA-65, ES256\r\n'), 0,
         'başlık satırı; istek nesnesi tek imza (ML-DSA-65 seçilirse 3309 B imza 64 B yerine)', '#791 yorumu (12.09.2026)')
    ekle('M-c', 'ikinci istek parametresi request_pqc', 'yük + ' + str(b64u(sig65) + len('&request_pqc=') + 2), '0 (değerle) / +1 (request_uri ile)',
         'aynı istek nesnesinin ML-DSA-65 imzalı ikinci kopyası: b64u(başlık)+b64u(yük)+b64u(3309 B)', '#791 yorumu')
    ekle('M-b0', 'imzasız istek (taban)', 0, 0, 'taban; ek yok', 'HAIP 5.2 (T281)')
    alan = len(b'"credential_signing_alg_values_required":["ML-DSA-65"],')
    ekle('M-e′', 'meta veri alanı (required)', alan, 0, 'JSON alanı', 'T393/T394 örüntüsü')
    ekle('M-e / M-e′ (imzalı)', 'imzalı meta veri', b64u(sig65) + 2, '+1 meta veri alımı (taze kip)',
         'b64u(ML-DSA-65 imzası) + ayraç; taze kipte doğrulama başına bir alım', 'T073, T075, T076')
    ekle('M-d', 'kayıt meta verisi alanı', len(b'"request_object_signing_alg_values_required":["ML-DSA-65"],'), 0,
         'kayıt başına bir kez (işlem başına 0)', '#2153 madde 3, 5')
    tl_xml = len(b'<pq:Expectation Scope="path" Sunset="2031-01-01T00:00:00Z">pq_required</pq:Expectation>')
    lote_json = len(b',"pqExpectation":{"state":"pq_required","scope":"path","sunset":"2031-01-01T00:00:00Z"}')
    ekle('M-f', 'TL kaydı uzantısı (XML, varlık başına)', tl_xml, '0 (sabitli/güncel görünüm) / +1 (çevrimiçi sorgu)',
         'varlık başına bir öğe; TL imzası zaten var (ML-DSA-65 ile 3309 B, göçte bir kez)', 'TS 119 612 §5.7.1 (T013, T014); öneri')
    ekle('M-f', 'LoTE kaydı uzantısı (JSON, varlık başına)', lote_json, '0 / +1', 'aynı; JAdES-B tek imza (T023-T025)', 'TS 119 602 §6.8.0 (T022); öneri')
    ekle('M-g', 'TLS uzantısı pq_cert_available (sunucu)', 2 + 2 + 4, 0, 'tür (2) + uzunluk (2) + uint32 (4)', 'sheffer-02 §3.3')
    ekle('M-g', 'TLS uzantısı pq_cert_available (ClientHello)', 2 + 2, 0, 'boş uzantı', 'sheffer-02 §3.3')
    ekle('M-h reddy', 'X.509 PQCHC eki (continuityPeriod=365)', len(reddy_eki()), 0, 'DER; policyURI yok', 'reddy-01 §3.2')
    ekle('M-h vicente', 'X.509 PQCHC eki (ML-DSA-65, SHA-256)', len(vicente_eki()), 0,
         'DER; commitmentValid varsayılan, policyURI yok', 'vicente-02 §4.1')
    with io.open(os.path.join(KOK, 'sonuc', 'ek_yuk.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['mekanizma', 'nesne', 'ek_bayt', 'ek_alim', 'formul', 'kaynak'],
                           lineterminator='\n')
        w.writeheader()
        w.writerows(satir)
    for s in satir:
        print('%-22s %-48s %8s  %s' % (s['mekanizma'], s['nesne'], s['ek_bayt'], s['ek_alim']))


if __name__ == '__main__':
    main()
