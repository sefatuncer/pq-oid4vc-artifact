# -*- coding: utf-8 -*-
"""Adım 6 | K1-11 TANISI (SONUÇ GÖRÜLDÜKTEN SONRA; kapı hücresi DEĞİL).

Dondurulmuş ../tamarin_kos.py işlevlerini DEĞİŞTİRMEDEN kullanır (içe aktarma). Bütünlük testi (COMPLETENESS) kullanan
altı KAT-1 hücresini, bütünlüğü DNSKEY adımına da uygulayan tanı modeliyle (KAT1_DNSSEC_tani.spthy) koşar.
Beklenen değerler: nsurum/kat_nsurum.tsv 'ilk_ajan' (tek kaynak). Çıktı: tani/sonuc.csv.
Kullanım (dnssec klasöründen): python tani/tani_kos.py
"""
import csv, os, sys

BURASI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(BURASI))
import tamarin_kos as tk  # noqa: E402  (dondurulmuş koşucu; değiştirilmedi)

HUCRELER = [('K1-02', 'DS_CL,DK3_USABLE,COMPLETENESS'), ('K1-04', 'DS_PQ,DK3_USABLE,COMPLETENESS'),
            ('K1-05', 'DS_PQ,OLD_DS_REPLAY,DK3_USABLE,COMPLETENESS'), ('K1-06', 'DS_PQ,DK3_USABLE,COMPLETENESS'),
            ('K1-11', 'DS_BOTH,DK3_USABLE,COMPLETENESS'), ('K1-12', 'DS_PQ,DK3_USABLE,COMPLETENESS,PARENT_CL')]


def main():
    NS = {}
    with open(tk.NSURUM, encoding='utf-8', newline='') as f:
        for x in csv.DictReader(f, delimiter='\t'):
            NS[(x['hucre'], x['sutun'])] = x['ilk_ajan']
    cikti = []
    for h, bay in HUCRELER:
        r = {'kosu': 'TANI.%s.tam' % h, 'tamarin_bayraklari': bay, 'model': 'tani/KAT1_DNSSEC_tani.spthy'}
        ex = tk.kanitla(r, 'executable')
        ln = tk.kanitla(r, 'a_rrset_authentic')
        bek = NS[(h, 'Tamarin:a_rrset_authentic')]
        cikti.append({'hucre': h, 'bayraklar': bay, 'beklenen': bek, 'tani_gozlenen': ln[0],
                      'uyum': 'EVET' if ln[0] == bek else 'HAYIR', 'adim': ln[1], 'merdiven': ln[2], 'meta': ln[3],
                      'iyi_bicim': ln[4], 'executable': ex[0]})
        print(cikti[-1], flush=True)
    with open(os.path.join(BURASI, 'sonuc.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(cikti[0].keys()))
        w.writeheader()
        w.writerows(cikti)
    return 0


if __name__ == '__main__':
    sys.exit(main())
