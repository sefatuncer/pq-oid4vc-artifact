# -*- coding: utf-8 -*-
"""Step 6 | verbatim quotation check (the same code in every KAT folder; work plan Step 6 acceptance criterion 4).

Looks up every quotation of alintilar.tsv in the pinned text and compares the SHA-256 of the text with the MANIFEST value.
Matching steps (the step that found it is reported; the quotation text is NOT CHANGED):
  1 'bosluk'   : whitespace sequences are reduced to one space (RFC page/line breaks);
  2 'unicode'  : + NFKC (ligatures) and curly quotes/long dashes -> ASCII (PDF text extraction);
  3 'tireleme' : + end-of-line hyphenation ("classi- cal" -> "classical");
  4 'tire_sil' : + hyphens inside words are removed on both sides (PDF extraction drops the end-of-line hyphen:
                 "alt-signature" -> "altsignature" in the text).
Output: sonuc/alinti_denetimi.tsv. Usage: ./calistir.sh alinti_dogrula.py
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
