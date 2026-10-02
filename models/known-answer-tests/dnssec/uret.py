# -*- coding: utf-8 -*-
"""Step 6 | generator of the instance files (the same code in every KAT folder).

Writes the `asp_sabitler` column (ASP facts) of the 'asp' rows of hucreler.tsv and mutasyonlar.tsv into one file per
cell: ornekler/<kosu>.lp  (the '.asp' at the end of the run name is dropped).
Deterministic: same table -> byte-identical files. Touches neither the core nor any run.
Usage (from inside the folder): python uret.py
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
