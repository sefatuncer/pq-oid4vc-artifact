"""DPoP boyut tablosu (yurutucu karari A6): talep kumesiyle birlikte ve composite imza UST SINIRIYLA.

Talep kumeleri: 'asgari' (jti, htm, htu, iat), '+ath' (kaynak erisimi; erisim belirteci ozeti),
'+ath+nonce' (sunucu nonce'u ile). Anahtarlar: anahtarlar/v1 'dpop/<alg>' (belirlenimci).
Composite ECDSA bileseni DER oldugundan imza boyu degiskendir (-04 Tablo 2: P-256 <= 72 B, P-384 <= 104 B);
'bayt_ust_sinir' ML-DSA-65-ES256 icin 3309 + 72 = 3381 B imza ile hesaplanir.
Bu bir RAPOR tablosudur; vektor seti (v1/v1.1) degismez.
Kullanim: python -m uretec.boyut_dpop <cikti_kok>   -> <cikti_kok>/sonuclar/v1.1_dpop_boyutlari.{csv,json}
"""
import csv
import json
import os
import sys

from pqjose import jws, mldsa
from pqjose.params import COMPOSITE, OKP_SIG_LEN

from . import artefakt as A
from .anahtar import AnahtarSeti
from .vektorler import SIMDI

NGINX = 8182
NODE = 16348
ALGS = ('ES256', 'EdDSA', 'Ed25519', 'ML-DSA-44', 'ML-DSA-65', 'ML-DSA-87', 'ML-DSA-44-ES256', 'ML-DSA-65-ES256',
        'ML-DSA-87-ES384', 'ML-DSA-44-Ed25519', 'ML-DSA-65-Ed25519', 'ML-DSA-87-Ed448')
TALEP = (('asgari', False, False), ('+ath', True, False), ('+ath+nonce', True, True))


def b64len(n):
    return (4 * n + 2) // 3  # dolgusuz base64url uzunlugu


def ust_sinir_imza(alg, gercek):
    if alg in COMPOSITE:
        p = COMPOSITE[alg]
        ml = mldsa.sig_len(p['ml'])
        if p['trad'] == 'ECDSA':
            return ml + (72 if p['crv'] == 'P-256' else 104)
        return ml + OKP_SIG_LEN[p['crv']]
    return gercek


def main(kok):
    S = AnahtarSeti()
    rows = []
    for alg in ALGS:
        key = S['dpop/' + ('EdDSA' if alg == 'Ed25519' else alg)]
        for ad, ath, nonce in TALEP:
            obj = A.dpop(key, alg, 'boyut/%s/%s' % (alg, ad), iat=SIMDI - 10, with_ath=ath, with_nonce=nonce)
            sig = jws.parse(obj).signatures[0].signature
            ub_sig = ust_sinir_imza(alg, len(sig))
            ub = len(obj) - b64len(len(sig)) + b64len(ub_sig)
            rows.append({'alg': alg, 'talep_kumesi': ad, 'imza_B': len(sig), 'imza_ust_sinir_B': ub_sig,
                         'dpop_B': len(obj), 'dpop_ust_sinir_B': ub, 'nginx_8182_asar(ust)': ub > NGINX,
                         'node_16348_asar(ust)': ub > NODE})
    os.makedirs(os.path.join(kok, 'sonuclar'), exist_ok=True)
    with open(os.path.join(kok, 'sonuclar', 'v1.1_dpop_boyutlari.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(kok, 'sonuclar', 'v1.1_dpop_boyutlari.json'), 'w', encoding='utf-8') as f:
        json.dump({'aciklama': __doc__.split('\n')[0], 'esikler': {'nginx_1.31.6': NGINX, 'node_24.15': NODE},
                   'satirlar': rows}, f, indent=1, ensure_ascii=False)
        f.write('\n')
    for r in rows:
        print('%-18s %-11s imza %4d/%4d  dpop %5d/%5d  nginx:%s' % (r['alg'], r['talep_kumesi'], r['imza_B'], r['imza_ust_sinir_B'],
                                                                   r['dpop_B'], r['dpop_ust_sinir_B'], r['nginx_8182_asar(ust)']))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else '.'))
