# -*- coding: utf-8 -*-
"""Step 6 | KAT-3 S/MIME (3a: CEK confidentiality; 3b: authentication duality) — ASP runner.
SINGLE CORE: only /asp/cekirdek.lp + the instance files of this folder (kat3a_smime.lp or kat3b_auth.lp + ornekler/).

READING RULES (MAPPING.md §4.4–§4.5; fixed BEFORE the run). In every run E := ihlal(tum,g1).
 KAT-3a (7 probes per vector; label ONLY from the probe results, priority of Das Table 1):
   accept_strict = 1 - E(kati); accept_transitional = 1 - E(gecis)
   out: E(gecersiz) -> invalid; otherwise E(klasik) and E(pq_hibrit) -> unsafe_mixed; otherwise E(bilinmeyen) -> unknown;
        otherwise E(klasik) -> classical_only; otherwise not E(kati) -> pqc_protected; otherwise not E(gecis) -> hybrid_protected.
   Additional (pass items of KAT-SPEC §4(d); not gate values): kat3a_fail = accept_strict and E(klasik) (must be empty);
   model_gap = accept_strict and E(tum_klasik_yol) (expected only in o8).
 KAT-3b: dynamic (qday0/qday200): SALDIRI <=> E; static (violation): 1 <=> E.
Expected values: /nsurum/kat_nsurum.tsv 'ilk_ajan' (single source); for the mutations mutasyonlar.tsv 'beklenen'.
Usage: ./calistir.sh kos.py  ->  sonuc/asp.csv, sonuc/asp_sondalar.csv, sonuc/asp_mutasyon.csv, sonuc/asp_ozet.json
"""
import csv, hashlib, json, os, sys, time
from collections import defaultdict
import clingo

KOK = os.path.dirname(os.path.abspath(__file__))
CEKIRDEK = os.environ.get('KAT_CEKIRDEK', '/asp/cekirdek.lp')
NSURUM = os.environ.get('KAT_NSURUM', '/nsurum/kat_nsurum.tsv')
TABAN = {'KAT-3a': 'kat3a_smime.lp', 'KAT-3b': 'kat3b_auth.lp'}
CEKIRDEK_BEKLENEN = 'a32372a7c646274ce672c9586e25b34f75f4febb2f966596cc97e7afb89e0b38'  # commit 45cbd0f


def sha(yol):
    return hashlib.sha256(open(yol, 'rb').read()).hexdigest()


def tablo(ad):
    yol = os.path.join(KOK, ad)
    if not os.path.exists(yol):
        return []
    with open(yol, encoding='utf-8', newline='') as f:
        return [r for r in csv.DictReader(f, delimiter='\t') if r['motor'] == 'asp']


def nsurum():
    with open(NSURUM, encoding='utf-8', newline='') as f:
        return {(r['hucre'], r['sutun']): r['ilk_ajan'] for r in csv.DictReader(f, delimiter='\t')}


def coz(grup, ornek):
    ctl = clingo.Control(['--warn=none', '0'])
    for d in (CEKIRDEK, os.path.join(KOK, TABAN[grup]), os.path.join(KOK, 'ornekler', ornek)):
        ctl.load(d)
    t0 = time.time()
    ctl.ground([('base', [])])
    modeller = []
    ctl.solve(on_model=lambda m: modeller.append({str(s) for s in m.symbols(atoms=True)}))
    sure = time.time() - t0
    if len(modeller) != 1:
        raise RuntimeError('%s: %d cevap kümesi (1 bekleniyordu)' % (ornek, len(modeller)))
    A = modeller[0]
    hata = sorted(a for a in A if a.startswith('parametre_hatasi('))
    if hata:
        raise RuntimeError('%s: parametre hatası %s' % (ornek, hata))
    return A, sure


def tanik(A):
    sec = lambda on: sorted(a for a in A if a.startswith(on))
    return ' '.join(sec('sahte(tum,') + sec('kirilir(tum,') + sec('kirilir_alt(tum,') + sec('beklenir(tum,') +
                    sec('kabul_alti('))


def etiket_3a(E):
    if E['gecersiz']:
        out = 'invalid'
    elif E['klasik'] and E['pq_hibrit']:
        out = 'unsafe_mixed'
    elif E['bilinmeyen']:
        out = 'unknown'
    elif E['klasik']:
        out = 'classical_only'
    elif not E['kati']:
        out = 'pqc_protected'
    elif not E['gecis']:
        out = 'hybrid_protected'
    else:
        out = 'tanimsiz'
    ast = '0' if E['kati'] else '1'
    atr = '0' if E['gecis'] else '1'
    return {'out': out, 'accept_strict': ast, 'accept_transitional': atr,
            'kat3a_fail': ast == '1' and E['klasik'], 'model_gap': ast == '1' and E['tum_klasik_yol']}


def main():
    s_once = sha(CEKIRDEK)
    NS = nsurum()
    os.makedirs(os.path.join(KOK, 'sonuc'), exist_ok=True)
    sondalar, hucre, mut, sureler = [], [], [], []
    E3a = defaultdict(dict)
    for r in tablo('hucreler.tsv'):
        A, t = coz(r['grup'], r['kosu'][:-4] + '.lp')
        sureler.append(t)
        e = 'ihlal(tum,g1)' in A
        sondalar.append({'kosu': r['kosu'], 'grup': r['grup'], 'hucre': r['nsurum_hucre'], 'sonda': r['sonda'],
                         'E': int(e), 'sure_s': round(t, 4), 'tanik': tanik(A)})
        if r['grup'] == 'KAT-3a':
            E3a[r['nsurum_hucre']][r['sonda']] = e
        else:
            g = ('1' if e else '0') if r['sonda'] == 'statik' else ('SALDIRI' if e else 'YOK')
            b = NS.get((r['nsurum_hucre'], r['nsurum_sutun']), 'YOK_ANAHTAR')
            hucre.append({'hucre': r['nsurum_hucre'], 'sutun': r['nsurum_sutun'], 'beklenen': b, 'gozlenen': g,
                          'uyum': 'EVET' if g == b else 'HAYIR', 'dayanak': r['kosu']})
    ekler = {}
    for o in sorted(E3a, key=lambda x: int(x[1:])):
        et = etiket_3a(E3a[o])
        ekler[o] = {'kat3a_fail': et['kat3a_fail'], 'model_gap': et['model_gap']}
        for sutun in ('out', 'accept_strict', 'accept_transitional'):
            b = NS.get((o, sutun), 'YOK_ANAHTAR')
            hucre.append({'hucre': o, 'sutun': sutun, 'beklenen': b, 'gozlenen': et[sutun],
                          'uyum': 'EVET' if et[sutun] == b else 'HAYIR',
                          'dayanak': ' '.join('%s=%d' % (p, int(v)) for p, v in sorted(E3a[o].items()))})
    for r in tablo('mutasyonlar.tsv'):
        A, t = coz(r['grup'], r['kosu'][:-4] + '.lp')
        e = 'ihlal(tum,g1)' in A
        g = ('0' if e else '1') if r['grup'] == 'KAT-3a' else ('SALDIRI' if e else 'YOK')
        mut.append({'kosu': r['kosu'], 'mutasyon': r['mutasyon'], 'temel': r['temel'], 'sonda': r['sonda'],
                    'beklenen': r['beklenen'], 'gozlenen': g, 'dondu': 'EVET' if g == r['beklenen'] else 'HAYIR',
                    'sure_s': round(t, 4), 'tanik': tanik(A)})
    s_sonra = sha(CEKIRDEK)
    for ad, satir in (('asp.csv', hucre), ('asp_sondalar.csv', sondalar), ('asp_mutasyon.csv', mut)):
        with open(os.path.join(KOK, 'sonuc', ad), 'w', encoding='utf-8', newline='') as f:
            if satir:
                w = csv.DictWriter(f, fieldnames=list(satir[0].keys()))
                w.writeheader()
                w.writerows(satir)
    ozet = {'kat': 'KAT-3', 'clingo': clingo.__version__, 'cekirdek_sha256_once': s_once,
            'cekirdek_sha256_sonra': s_sonra, 'cekirdek_commit_45cbd0f_ile_ayni': s_once == s_sonra == CEKIRDEK_BEKLENEN,
            'taban_sha256': {g: sha(os.path.join(KOK, t)) for g, t in TABAN.items()},
            'asp_kosusu': len(sondalar), 'hucre_degeri': len(hucre), 'hucre_uyum': sum(r['uyum'] == 'EVET' for r in hucre),
            'kat3a_fail': sorted(o for o, v in ekler.items() if v['kat3a_fail']),
            'model_gap': sorted(o for o, v in ekler.items() if v['model_gap']),
            'mutasyon_kosusu': len(mut), 'mutasyon_dondu': sum(r['dondu'] == 'EVET' for r in mut),
            'en_uzun_s': round(max(sureler + [r['sure_s'] for r in mut] or [0]), 4)}
    json.dump(ozet, open(os.path.join(KOK, 'sonuc', 'asp_ozet.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps(ozet, ensure_ascii=False, indent=1))
    for r in hucre:
        if r['uyum'] != 'EVET':
            print('UYUMSUZ', r)
    return 0 if s_once == s_sonra else 3


if __name__ == '__main__':
    sys.exit(main())
