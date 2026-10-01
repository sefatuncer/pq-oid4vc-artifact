# -*- coding: utf-8 -*-
"""Adım 6 | örnek dosyası üreticisi (her KAT klasöründe aynı kod).

hucreler.tsv ve mutasyonlar.tsv'deki 'asp' satırlarının `asp_sabitler` sütununu (ASP olguları) hücre
başına bir dosyaya yazar: ornekler/<kosu>.lp  (kosu adının sonundaki '.asp' atılır).
Belirlenimci: aynı tablo -> bayt-aynı dosyalar. Çekirdeğe ve hiçbir koşuma dokunmaz.
Kullanım (klasörün içinden): python uret.py
"""
import csv, os, sys

KOK = os.path.dirname(os.path.abspath(__file__))


def satirlar(ad):
    yol = os.path.join(KOK, ad)
    if not os.path.exists(yol):
        return []
    with open(yol, encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f, delimiter='\t'))


def main():
    hedef = os.path.join(KOK, 'ornekler')
    os.makedirs(hedef, exist_ok=True)
    yazilan = []
    for tablo in ('hucreler.tsv', 'mutasyonlar.tsv'):
        for r in satirlar(tablo):
            if r['motor'] != 'asp':
                continue
            ad = r['kosu'][:-4] if r['kosu'].endswith('.asp') else r['kosu']
            olgular = [o.strip() + '.' for o in r['asp_sabitler'].split('.') if o.strip()]
            govde = '%% %s | kaynak: %s | otomatik: uret.py (elle düzenlemeyin)\n' % (r['kosu'], tablo)
            govde += '\n'.join(olgular) + '\n'
            with open(os.path.join(hedef, ad + '.lp'), 'w', encoding='utf-8', newline='\n') as f:
                f.write(govde)
            yazilan.append(ad + '.lp')
    print('%d örnek dosyası yazıldı: %s' % (len(yazilan), ', '.join(sorted(yazilan))))
    return 0


if __name__ == '__main__':
    sys.exit(main())
