"""PQ ilkel dogrulama servisi (Adim 9b ek gereksinim; 9a D-E3/D-E5, C3 tedavi kolu TK2 "eklenti").

Hedef kutuphanenin KAMUYA ACIK genisletme noktasina (JWSVerifier, crypto arayuzu, SignatureProvider,
algoritma kaydi, ozel dogrulayici...) takilan ince bir istemci bu servisi cagirir. Servis YALNIZ
kriptografik ilkeli dogrular; politika karari (hangi alg kabul, kac imza, anahtar cozumleme, x5c,
crit, typ...) hedef kutuphanede kalir.

Desteklenen alg: ML-DSA-44/65/87 (RFC 9964; ctx bos) ve composite -04: ML-DSA-44-ES256,
ML-DSA-65-ES256, ML-DSA-87-ES384, ML-DSA-44-Ed25519, ML-DSA-65-Ed25519, ML-DSA-87-Ed448.

Istek (JSON):
  alg                      zorunlu
  jwk | acik_anahtar(_hex) biri zorunlu. jwk: AKP (kty=AKP, alg ZORUNLU ve istek alg'ina esit, pub).
                           acik_anahtar: base64url ham acik anahtar (ML-DSA: FIPS 204 pk;
                           composite: mldsaPK || tradPK, -04 4.1). *_hex: onaltilik es degeri.
  imzalama_girdisi(_hex)   zorunlu: imzalanan baytlar (JWS'te ASCII(protected '.' payload); COSE'da Sig_structure)
  imza(_hex)               zorunlu: ham imza baytlari (JWS'te base64url cozulmus)
Yanit (JSON):
  {"gecerli": bool, "alg": str, "bilesenler": {"ml": bool, "trad": bool}|{"ml": bool}|null,
   "hata": null|str, "servis": "pqdogrula/1"}
  'hata' dolu ise istek/serilestirme sorunu vardir (gecerli=false).

HTTP (yalniz yerel / Docker ic agi; kimlik dogrulama YOK — disa ACILMAMALI):
  GET  /v1/saglik          -> surumler, desteklenen alg'ler
  POST /v1/dogrula         -> tek istek
  POST /v1/dogrula/toplu   -> {"istekler": [...]} -> {"yanitlar": [...]}
CLI:
  python -m servis.pqdogrula dogrula [--istek DOSYA]     (DOSYA yoksa stdin) ; cikis kodu 0=gecerli 1=gecersiz 2=hata
  python -m servis.pqdogrula sunucu [--host 127.0.0.1] [--port 8765]
"""
import argparse
import binascii
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from pqjose import composite, mldsa
from pqjose.keys import CompositeKey, MLDSAKey, key_from_jwk
from pqjose.params import COMPOSITE, MLDSA
from pqjose.util import FormatError, b64u_decode

SERVIS = 'pqdogrula/1'
DESTEKLENEN = tuple(MLDSA) + tuple(COMPOSITE)
AZAMI_GOVDE = 4 * 1024 * 1024      # 4 MiB (toplu istekler icin)
AZAMI_TOPLU = 256


def _bytes(ist, ad, zorunlu=True):
    if ad in ist:
        return b64u_decode(ist[ad])
    if ad + '_hex' in ist:
        try:
            return binascii.unhexlify(ist[ad + '_hex'])
        except (binascii.Error, TypeError) as e:
            raise FormatError('%s_hex gecersiz' % ad) from e
    if zorunlu:
        raise FormatError('%s (ya da %s_hex) eksik' % (ad, ad))
    return None


def _anahtar(ist, alg):
    if 'jwk' in ist:
        j = ist['jwk']
        if not isinstance(j, dict) or j.get('kty') != 'AKP':
            raise FormatError('jwk: kty=AKP bekleniyor')
        if j.get('alg') != alg:
            raise FormatError('jwk.alg istek alg ile ayni olmali (RFC 9964 3: AKP alg ZORUNLU)')
        pub_only = {k: v for k, v in j.items() if k != 'priv'}
        return key_from_jwk(pub_only)
    pub = _bytes(ist, 'acik_anahtar')
    if alg in MLDSA:
        return MLDSAKey(alg, pub=pub)
    return CompositeKey.from_bytes(alg, pub=pub)


def dogrula(ist: dict) -> dict:
    alg = ist.get('alg') if isinstance(ist, dict) else None
    y = {'gecerli': False, 'alg': alg, 'bilesenler': None, 'hata': None, 'servis': SERVIS}
    try:
        if not isinstance(ist, dict):
            raise FormatError('istek JSON nesnesi olmali')
        if alg not in DESTEKLENEN:
            raise FormatError('desteklenmeyen alg (servis yalniz ML-DSA ve composite -04 ilkelleri): %r' % alg)
        key = _anahtar(ist, alg)
        m = _bytes(ist, 'imzalama_girdisi')
        s = _bytes(ist, 'imza')
        if alg in MLDSA:
            ok = mldsa.verify(MLDSA[alg], key.pub, m, s, b'')
            y['bilesenler'] = {'ml': ok}
            y['gecerli'] = ok
        else:
            c = composite.verify_components(alg, key, m, s)
            y['bilesenler'] = {'ml': bool(c['ml']), 'trad': bool(c['trad'])}
            if c['hata']:
                y['hata'] = c['hata']
            y['gecerli'] = bool(c['ml'] and c['trad']) and not c['hata']
    except (FormatError, ValueError, KeyError, TypeError) as e:
        y['hata'] = '%s: %s' % (type(e).__name__, e)
        y['gecerli'] = False
    return y


def saglik() -> dict:
    import pqjose
    return {'servis': SERVIS, 'durum': 'ok', 'desteklenen_alg': list(DESTEKLENEN), 'surumler': pqjose.versions()}


class _H(BaseHTTPRequestHandler):
    server_version = 'pqdogrula/1'

    def _yaz(self, kod, obj):
        b = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(kod)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):  # noqa: N802
        if self.path == '/v1/saglik':
            self._yaz(200, saglik())
        else:
            self._yaz(404, {'hata': 'bulunamadi'})

    def do_POST(self):  # noqa: N802
        n = int(self.headers.get('Content-Length') or 0)
        if n <= 0 or n > AZAMI_GOVDE:
            self._yaz(413 if n > AZAMI_GOVDE else 400, {'hata': 'govde boyutu gecersiz'})
            return
        try:
            ist = json.loads(self.rfile.read(n).decode('utf-8'))
        except (ValueError, UnicodeDecodeError):
            self._yaz(400, {'hata': 'JSON cozulmedi'})
            return
        if self.path == '/v1/dogrula':
            self._yaz(200, dogrula(ist))
        elif self.path == '/v1/dogrula/toplu':
            lst = ist.get('istekler') if isinstance(ist, dict) else None
            if not isinstance(lst, list) or len(lst) > AZAMI_TOPLU:
                self._yaz(400, {'hata': 'istekler dizisi (en fazla %d)' % AZAMI_TOPLU})
                return
            self._yaz(200, {'yanitlar': [dogrula(x) for x in lst]})
        else:
            self._yaz(404, {'hata': 'bulunamadi'})

    def log_message(self, fmt, *args):  # sessiz (kisisel veri yok; yalniz yerel)
        pass


def sunucu(host='127.0.0.1', port=8765):
    srv = ThreadingHTTPServer((host, port), _H)
    return srv


def main(argv=None):
    ap = argparse.ArgumentParser(prog='pqdogrula')
    sub = ap.add_subparsers(dest='cmd', required=True)
    d = sub.add_parser('dogrula')
    d.add_argument('--istek')
    s = sub.add_parser('sunucu')
    s.add_argument('--host', default='127.0.0.1')
    s.add_argument('--port', type=int, default=8765)
    sub.add_parser('saglik')
    a = ap.parse_args(argv)
    if a.cmd == 'dogrula':
        raw = open(a.istek, 'rb').read() if a.istek else sys.stdin.buffer.read()
        try:
            ist = json.loads(raw.decode('utf-8'))
        except (ValueError, UnicodeDecodeError):
            print(json.dumps({'gecerli': False, 'hata': 'JSON cozulmedi', 'servis': SERVIS}))
            return 2
        y = dogrula(ist)
        print(json.dumps(y, ensure_ascii=False))
        return 0 if y['gecerli'] else (2 if y['hata'] and not y['bilesenler'] else 1)
    if a.cmd == 'saglik':
        print(json.dumps(saglik(), ensure_ascii=False, indent=1))
        return 0
    srv = sunucu(a.host, a.port)
    print('pqdogrula dinliyor: http://%s:%d (kimlik dogrulama YOK; yalniz yerel/ic ag)' % (a.host, a.port), flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == '__main__':
    sys.exit(main())
