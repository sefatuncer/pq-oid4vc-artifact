# -*- coding: utf-8 -*-
"""Step 6 | DIAGNOSIS of K1-11 (AFTER THE RESULT WAS SEEN; NOT a gate cell).

Uses the functions of the frozen ../tamarin_kos.py WITHOUT CHANGING them (import). Runs the six KAT-1 cells that use the
completeness test (COMPLETENESS) with the diagnosis model that also applies completeness to the DNSKEY step (KAT1_DNSSEC_tani.spthy).
Expected values: nsurum/kat_nsurum.tsv 'ilk_ajan' (single source). Output: tani/sonuc.csv.
Usage (from the dnssec folder): python tani/tani_kos.py
"""
import csv, os, sys

BURASI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(BURASI))
import tamarin_kos as tk  # noqa: E402  (frozen runner; not changed)

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
