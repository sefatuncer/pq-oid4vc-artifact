# -*- coding: utf-8 -*-
"""Adım 6 | birebir alıntı denetimi (her KAT klasöründe aynı kod; IS-PLANI Adım 6 kabul ölçütü 4).

alintilar.tsv'deki her alıntıyı sabitlenmiş metinde arar ve metnin SHA-256'sını MANIFEST değeriyle karşılaştırır.
Eşleme adımları (hangisiyle bulunduğu raporlanır; alıntı metni DEĞİŞTİRİLMEZ):
  1 'bosluk'   : boşluk dizileri tek boşluğa indirgenir (RFC sayfa/satır kırılmaları);
  2 'unicode'  : + NFKC (bitişik harfler) ve kıvrık tırnak/uzun tire -> ASCII (PDF metin çıkarımı);
  3 'tireleme' : + satır sonu tirelemesi ("classi- cal" -> "classical");
  4 'tire_sil' : + sözcük içi tireler iki tarafta da silinir (PDF çıkarımı satır sonu tiresini düşürür:
                 "alt-signature" -> metinde "altsignature").
Çıktı: sonuc/alinti_denetimi.tsv. Kullanım: ./calistir.sh alinti_dogrula.py
"""
import csv, hashlib, os, re, sys, unicodedata

KOK = os.path.dirname(os.path.abspath(__file__))
CEVIR = str.maketrans({'‘': "'", '’': "'", '“': '"', '”': '"', '–': '-', '—': '--',
                       ' ': ' ', '­': ''})


def bosluk(s):
    return re.sub(r'\s+', ' ', s).strip()


def uni(s):
    return bosluk(unicodedata.normalize('NFKC', s).translate(CEVIR))


def tire(s):
    return re.sub(r'(\w)- (\w)', r'\1\2', uni(s))


def tire_sil(s):
    return re.sub(r'(\w)-(\w)', r'\1\2', tire(s))


def main():
    with open(os.path.join(KOK, 'alintilar.tsv'), encoding='utf-8', newline='') as f:
        satirlar = list(csv.DictReader(f, delimiter='\t'))
    cikti = []
    for r in satirlar:
        ham = open(r['metin'], 'rb').read()
        h = hashlib.sha256(ham).hexdigest()
        metin = ham.decode('utf-8', errors='replace')
        adim = 'BULUNAMADI'
        for ad, fn in (('bosluk', bosluk), ('unicode', uni), ('tireleme', tire), ('tire_sil', tire_sil)):
            if fn(r['alinti']) in fn(metin):
                adim = ad
                break
        cikti.append({'id': r['id'], 'kaynak_id': r['kaynak_id'], 'bolum': r['bolum'], 'bulundu': adim,
                      'metin_sha256': h, 'metin_sha256_manifest_ile_ayni': 'EVET' if h == r['sha256_metin'] else 'HAYIR'})
        print(cikti[-1])
    os.makedirs(os.path.join(KOK, 'sonuc'), exist_ok=True)
    with open(os.path.join(KOK, 'sonuc', 'alinti_denetimi.tsv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(cikti[0].keys()), delimiter='\t')
        w.writeheader()
        w.writerows(cikti)
    tamam = all(c['bulundu'] != 'BULUNAMADI' and c['metin_sha256_manifest_ile_ayni'] == 'EVET' for c in cikti)
    return 0 if tamam else 2


if __name__ == '__main__':
    sys.exit(main())
