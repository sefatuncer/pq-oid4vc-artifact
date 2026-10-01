"""Uretec giris noktasi: python -m uretec.uret <cikti_kok>

<cikti_kok>/anahtarlar/v1/   anahtarlar (ozel/acik JWK), PKI (PEM/DER), roller.json, SHA256SUMS
<cikti_kok>/vektorler/v1/    vektor dosyalari, MANIFEST.json/.csv, b-uyumlu/vectors.json, SHA256SUMS
<cikti_kok>/sonuclar/        v1_boyutlar.csv (artefakt boyutlari)
"""
import csv
import json
import os
import sys
import time

import pqjose

from . import __version__
from .vektorler import SIMDI, Uretici


def main(kok):
    t0 = time.time()
    surumler = pqjose.versions()
    surumler['uretec'] = __version__
    u = Uretici(kok)
    items = u.uret(surumler)
    os.makedirs(os.path.join(kok, 'sonuclar'), exist_ok=True)
    with open(os.path.join(kok, 'sonuclar', 'v1_boyutlar.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['id', 'aile', 'artefakt', 'serilestirme', 'algler', 'bayt', 'nginx_8182_asar', 'node_16348_asar'])
        for i in items:
            sigs = i['insa'].get('imzalar') or i['insa'].get('kimlik_bilgileri') or []
            w.writerow([i['id'], i['aile'], i['artefakt'], i['serilestirme'], ';'.join(s.get('alg', '') for s in sigs),
                        i['bayt'], i['bayt'] > 8182, i['bayt'] > 16348])
    print(json.dumps({'vektor': len(items), 'aileler': sorted({i['aile'] for i in items}), 'sure_s': round(time.time() - t0, 2),
                      'simdi': SIMDI}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else '.'))
