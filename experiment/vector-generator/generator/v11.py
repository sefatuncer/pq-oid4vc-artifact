"""Test vector set v1.1 = v1 (93 vectors, BYTE-IDENTICAL) + Ed25519-labelled counterparts of the control arm.

Maintainers' decision A9 (24.09.2026): the primary label of the control arm stays 'EdDSA'. FALLBACK RULE: if a target
does not support 'EdDSA' but documents support for 'Ed25519' of RFC 9864, the control arm of that target
is run with the 'Ed25519'-labelled vectors and the label used is recorded per target.

Generation (python -m generator.v11 <output_root> [<frozen_v1_root>]):
  1. v1 is generated from scratch in a TEMPORARY folder and compared with the frozen v1 (SHA256SUMS of vectors/v1 and
     keys/v1); on any difference the generation STOPS. The frozen v1/ and keys/v1/ are only READ.
  2. The 93 vector files of v1 (+ b-uyumlu/vectors.json) are copied into v1.1 (byte-identical).
  3. For EVERY v1 vector with kol = kontrol-EdDSA a counterpart '<v1-id>-ED25519' is produced: the same key
     (issuer/EdDSA or dpop/EdDSA = Ed25519), the same payload, the same structure; ONLY the alg in the protected header of the
     'EdDSA'-labelled signature becomes 'Ed25519' and that signature is recomputed (Ed25519 is deterministic).
     A protection check confirms that the counterpart differs from v1 only at these points.
  4. NO new key: keys/v1 is used as it is.
NO oracle decision is written.
"""
import copy
import csv
import hashlib
import json
import os
import shutil
import sys
import tempfile

import pqjose
from pqjose import jws
from pqjose.util import b64u_decode, b64u_encode

from . import __version__
from . import artefakt as A
from .vektorler import B_PAYLOAD, SIMDI, Uretici

SURUM = 'v1.1'
ED_DAYANAK = ['RFC9864 §2.2 (Tablo 2: Ed25519)', 'RFC9864 §4.1.1 (JOSE kaydi: Ed25519)',
              'RFC9864 §4.1.2 (EdDSA: Deprecated)']
YEDEK_KURAL = ("A9 yedek kurali: kontrol kolunun birincil etiketi 'EdDSA'dir. Bir hedef 'EdDSA'yi desteklemiyor ama "
               "RFC 9864'teki 'Ed25519'u belgeli olarak destekliyorsa, o hedefin kontrol kolu '-ED25519' sonekli "
               "vektorlerle kosulur ve kullanilan etiket hedef basina kaydedilir.")
META_DOSYALAR = ('MANIFEST.json', 'MANIFEST.csv', 'SHA256SUMS')


def _sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def _decode_prot(pb64):
    return json.loads(b64u_decode(pb64))


def _sigs(obj):
    """(payload_b64, [(protected_b64, signature_b64)], disclosures) — compact JWS, General JSON JWS or SD-JWT."""
    if isinstance(obj, str):
        jwt = obj.split('~')[0]
        h, p, s = jwt.split('.')
        return p, [(h, s)], obj.split('~')[1:-1] if '~' in obj else None
    discl = (obj['signatures'][0].get('header') or {}).get('disclosures')
    return obj['payload'], [(e['protected'], e['signature']) for e in obj['signatures']], discl


def koruma_denetimi(v1_obj, es_obj):
    """The counterpart must differ from v1 only in the EdDSA->Ed25519 label and in that signature. Return: the recomputed positions."""
    p1, s1, d1 = _sigs(v1_obj)
    p2, s2, d2 = _sigs(es_obj)
    if p1 != p2 or d1 != d2 or len(s1) != len(s2):
        raise RuntimeError('es: yuk/ifsa/imza sayisi v1 ile ayni degil')
    degisen = []
    for i, ((h1, g1), (h2, g2)) in enumerate(zip(s1, s2)):
        a, b = _decode_prot(h1), _decode_prot(h2)
        if a.get('alg') == 'EdDSA':
            if b.get('alg') != 'Ed25519' or list(a) != list(b) or {k: v for k, v in a.items() if k != 'alg'} != \
                    {k: v for k, v in b.items() if k != 'alg'}:
                raise RuntimeError('es: imza %d basligi yalniz alg bakimindan farkli olmali' % i)
            degisen.append(i)
        elif h1 != h2 or g1 != g2:
            raise RuntimeError('es: EdDSA disi imza %d degismemeli' % i)
    if not degisen:
        raise RuntimeError('es: EdDSA etiketli imza yok')
    return degisen


def flip(b, i, bit=0):
    x = bytearray(b)
    x[i] ^= (1 << bit)
    return bytes(x)


def es_uret(u: Uretici):
    """Ed25519 counterparts of the v1 control-arm vectors: {v1_id: obj}."""
    S = u.S
    roles = {'ES256': 'issuer/ES256', 'EdDSA': 'issuer/EdDSA', 'Ed25519': 'issuer/EdDSA',
             'ML-DSA-65': 'issuer/ML-DSA-65', 'ML-DSA-65-ES256': 'issuer/ML-DSA-65-ES256'}

    def gen(*al):
        return jws.sign(B_PAYLOAD, [jws.Signer(S[roles[a]], {}, alg=a) for a in al], 'general', True)

    out = {}
    out['T1K_both_valid'] = gen('ES256', 'Ed25519')
    t2 = copy.deepcopy(out['T1K_both_valid'])
    s = b64u_decode(t2['signatures'][1]['signature'])
    t2['signatures'][1]['signature'] = b64u_encode(flip(s, 5, 0))       # same corruption as v1 T2K
    out['T2K_second_tampered'] = t2
    out['T4K_plus_ML-DSA-65'] = gen('ES256', 'Ed25519', 'ML-DSA-65')
    out['T5K_only_EdDSA'] = gen('Ed25519')
    out['T6_plus_composite'] = gen('ES256', 'Ed25519', 'ML-DSA-65-ES256')
    hold = S['holder/ES256'].public_jwk(kid=False)
    vc = A.issue_vc('VC09_GJ_ES256_EdDSA',                                  # SAME cred_id -> same salts/payload
                    [(S['issuer/ES256'], 'ES256', S.x5c('issuer-ec@int-ec')), (S['issuer/EdDSA'], 'Ed25519', None)],
                    hold, serialization='general')
    out['VC09_GJ_ES256_EdDSA'] = vc['obj']
    out['DPOP02_EdDSA'] = A.dpop(S['dpop/EdDSA'], 'Ed25519', 'DPOP02', iat=SIMDI - 10)   # same jti label and iat
    return out


def _yaz(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = obj.encode('utf-8') if isinstance(obj, str) else (json.dumps(obj, indent=1, ensure_ascii=False) + '\n').encode('utf-8')
    with open(path, 'wb') as f:
        f.write(data)
    return data


def es_meta(v, es_obj, data, degisen):
    e = copy.deepcopy(v)
    ext = v['dosya'].rsplit('.', 1)[1]
    e['id'] = v['id'] + '-ED25519'
    e['dosya'] = '%s/%s.%s' % (v['aile'], e['id'], ext)
    e['sha256'] = hashlib.sha256(data).hexdigest()
    e['bayt'] = len(data)
    e['kol'] = 'kontrol-Ed25519'
    ek = ''
    if v['aile'] == 'DPOP':
        ek = ' Bu esin boyutu %d B (nginx 8.182 B esigini %s).' % (len(data), 'asar' if len(data) > 8182 else 'asmaz')
    e['aciklama'] = ('v1 %s vektorunun Ed25519 etiketli esi (A9 yedek kurali): kontrol imzasinin alg etiketi "EdDSA" '
                     'yerine RFC 9864 tam belirtilmis "Ed25519"; ayni anahtar, ayni yuk, ayni yapi; yalniz bu baslik '
                     've ona bagli imza farkli.%s v1 aciklamasi: %s' % (v['id'], ek, v['aciklama']))
    e['dayanak'] = [d for d in v['dayanak'] if not d.startswith('RFC9864')] + ED_DAYANAK
    ins = e['insa']
    for s in ins.get('imzalar', []):
        if s.get('alg') == 'EdDSA':
            s['alg'] = 'Ed25519'
    ins['v1_esi'] = v['id']
    ins['etiket_degisikligi'] = {'eski': 'EdDSA', 'yeni': 'Ed25519', 'yeniden_hesaplanan_imza_sirasi': degisen}
    if v['aile'] == 'DPOP':
        ins['bayt'] = len(data)
        ins['nginx_8182_asar'] = len(data) > 8182
        ins['node_16348_asar'] = len(data) > 16348
    g = e['dogrulama_girdileri']
    if 'alg_kid' in g:
        g['alg_kid']['Ed25519'] = g['alg_kid']['EdDSA']
    e['sinanan']['ek_etiketler'] = e['sinanan']['ek_etiketler'] + ['ed25519-etiketi(RFC 9864; A9 yedek kurali)']
    return e


def uret_v11(cikti_kok, v1_kok, surumler):
    """Produces cikti_kok/vectors/v1.1. v1_kok: root where the frozen v1 is (read only)."""
    out = os.path.join(cikti_kok, 'vectors', SURUM)
    with tempfile.TemporaryDirectory(prefix='pq-v11-') as td:
        u = Uretici(td)
        u.uret(surumler)
        for sub in ('vectors', 'keys'):
            a = open(os.path.join(v1_kok, sub, 'v1', 'SHA256SUMS'), 'rb').read()
            b = open(os.path.join(td, sub, 'v1', 'SHA256SUMS'), 'rb').read()
            if a != b:
                raise RuntimeError('v1 yeniden uretimi donmus v1 ile ayni degil (%s) — v1.1 uretilmedi' % sub)
        if os.path.isdir(out):
            shutil.rmtree(out)
        src = os.path.join(td, 'vectors', 'v1')
        shutil.copytree(src, out, ignore=lambda d, names: [n for n in names if d == src and n in META_DOSYALAR])
        items = [copy.deepcopy(v) for v in u.items]
        esler = es_uret(u)
        yeni = []
        for v in u.items:
            if v['kol'] != 'kontrol-EdDSA':
                continue
            obj = esler[v['id']]
            degisen = koruma_denetimi(u.objs[v['id']], obj)
            ext = v['dosya'].rsplit('.', 1)[1]
            data = _yaz(os.path.join(out, v['aile'], '%s-ED25519.%s' % (v['id'], ext)), obj)
            yeni.append(es_meta(v, obj, data, degisen))
        if len(yeni) != sum(1 for v in u.items if v['kol'] == 'kontrol-EdDSA'):
            raise RuntimeError('her kontrol-EdDSA vektoru icin es uretilmeli')
        items += yeni
        v1_man = os.path.join(v1_kok, 'vectors', 'v1', 'MANIFEST.json')
        m = {'surum': SURUM, 'temel_surum': 'v1', 'vektor_sayisi': len(items), 'v1_vektor_sayisi': len(u.items),
             'ed25519_es_sayisi': len(yeni), 'simdi': SIMDI, 'T0': A.T0,
             'uyari': 'Bu manifest vektorlerin NE OLDUGUNU tanimlar; beklenen karar (oracle) ICERMEZ. '
                      "'insa' alanlari uretim gercekleridir, kabul/red hukmu degildir.",
             'yedek_kural': YEDEK_KURAL,
             'anahtar_dizini': 'anahtarlar/v1',
             'anahtar_sha256sums': _sha(os.path.join(v1_kok, 'keys', 'v1', 'SHA256SUMS')),
             'v1_capalari': {'vektorler/v1/MANIFEST.json': _sha(v1_man),
                             'vektorler/v1/SHA256SUMS': _sha(os.path.join(v1_kok, 'vectors', 'v1', 'SHA256SUMS'))},
             'uretim_ortami': surumler, 'aileler': sorted({i['aile'] for i in items}), 'vektorler': items}
        with open(os.path.join(out, 'MANIFEST.json'), 'w', encoding='utf-8') as f:
            json.dump(m, f, indent=1, ensure_ascii=False)
            f.write('\n')
        cols = ['id', 'aile', 'dosya', 'sha256', 'bayt', 'artefakt', 'serilestirme', 'kol', 'senaryo', 'sdjwtvc_surum',
                'basamak', 'plan_bayraklari', 'ek_etiketler', 'dayanak', 'b_pilot_esi', 'dcapi_protokol', 'algler', 'aciklama']
        with open(os.path.join(out, 'MANIFEST.csv'), 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(cols)
            for i in items:
                sigs = i['insa'].get('imzalar') or i['insa'].get('kimlik_bilgileri') or []
                w.writerow([i['id'], i['aile'], i['dosya'], i['sha256'], i['bayt'], i['artefakt'], i['serilestirme'],
                            i['kol'] or '', i['senaryo'] or '', ';'.join(i['sdjwtvc_surum'] or []),
                            ';'.join(i['sinanan']['basamak']), ';'.join(i['sinanan']['plan_bayraklari']),
                            ';'.join(i['sinanan']['ek_etiketler']), ';'.join(i['dayanak']), i['b_pilot_esi'] or '',
                            i['dcapi_protokol'] or '', ';'.join(s.get('alg', '') for s in sigs), i['aciklama']])
        Uretici._sha256sums(out)
    return items, yeni


def main(kok, v1_kok=None):
    surumler = pqjose.versions()
    surumler['uretec'] = __version__
    items, yeni = uret_v11(kok, v1_kok or kok, surumler)
    os.makedirs(os.path.join(kok, 'results'), exist_ok=True)
    with open(os.path.join(kok, 'results', 'v1.1_sizes.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['id', 'aile', 'artefakt', 'serilestirme', 'kol', 'algler', 'bayt', 'nginx_8182_asar', 'node_16348_asar'])
        for i in items:
            sigs = i['insa'].get('imzalar') or i['insa'].get('kimlik_bilgileri') or []
            w.writerow([i['id'], i['aile'], i['artefakt'], i['serilestirme'], i['kol'] or '',
                        ';'.join(s.get('alg', '') for s in sigs), i['bayt'], i['bayt'] > 8182, i['bayt'] > 16348])
    print(json.dumps({'surum': SURUM, 'vektor': len(items), 'ed25519_es': [v['id'] for v in yeni]}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else '.', sys.argv[2] if len(sys.argv) > 2 else None))
