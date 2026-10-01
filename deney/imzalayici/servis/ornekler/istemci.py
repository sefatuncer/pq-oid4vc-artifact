#!/usr/bin/env python3
"""pqdogrula icin asgari Python istemcisi (yalniz standart kitaplik).

Bir hedef kutuphanenin genisletme noktasina takilacak "eklenti"nin yapacagi is budur:
JWS'ten imzalama girdisini ve imzayi cikar, alg + acik anahtarla servise gonder, yalniz
{gecerli} sonucunu kutuphaneye dondur. Politika (hangi alg, kac imza, anahtar secimi) kutuphanede kalir.

Kullanim:
  python istemci.py --url http://127.0.0.1:18765 --jws belirtec.jws --jwk anahtar.json
  python istemci.py --url http://127.0.0.1:18765 --istek istek_ML-DSA-65.json
"""
import argparse
import base64
import json
import urllib.request


def b64u_decode(s):
    return base64.urlsafe_b64decode(s + '=' * (-len(s) % 4))


def dogrula(url, alg, jwk, imzalama_girdisi: bytes, imza: bytes) -> dict:
    ist = {'alg': alg, 'jwk': jwk,
           'imzalama_girdisi': base64.urlsafe_b64encode(imzalama_girdisi).rstrip(b'=').decode(),
           'imza': base64.urlsafe_b64encode(imza).rstrip(b'=').decode()}
    return _post(url + '/v1/dogrula', ist)


def _post(url, obj):
    req = urllib.request.Request(url, data=json.dumps(obj).encode(), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def compact_jws_dogrula(url, jws: str, jwk: dict) -> dict:
    h, p, s = jws.strip().split('.')
    alg = json.loads(b64u_decode(h))['alg']
    return dogrula(url, alg, jwk, (h + '.' + p).encode('ascii'), b64u_decode(s))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--url', default='http://127.0.0.1:18765')
    ap.add_argument('--jws')
    ap.add_argument('--jwk')
    ap.add_argument('--istek')
    a = ap.parse_args()
    if a.istek:
        print(json.dumps(_post(a.url + '/v1/dogrula', json.load(open(a.istek))), ensure_ascii=False))
    else:
        print(json.dumps(compact_jws_dogrula(a.url, open(a.jws).read(), json.load(open(a.jwk))), ensure_ascii=False))
