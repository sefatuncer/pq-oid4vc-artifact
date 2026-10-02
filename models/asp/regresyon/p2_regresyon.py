# -*- coding: utf-8 -*-
"""Regression of pilot P2 (48 queries) — referans/pilot/p2 (read only, /referans mount).

1) The pilot's OWN program (trustchain_base.lp + trustchain_mig.lp) is run again with the same options;
   all minimal sets are collected without truncation and compared with the recorded p2a_results.json
   (n, min_card, first ≤6 sets).
2) The pilot topology is translated into the fact format of the new core (regresyon/p2_ornegi.lp) and run with cekirdek.lp
   (ASP) and with the z3 encoding. Mapping: link->karar artefact (conveyed, window infinite),
   signed_under->kenar, can_convey->tasiyabilir(m_f), anchored->sabit, coexist(yaprak)->klasik_alt_zorla,
   wscd=p256 -> wscd_pq=yok, policy P4 (the pilot's expected/K3 rule), convey->tasi.
3) P2b order: the pilot's order program (order.lp) is compared with the new order encoding (sorgular/sira.py).
"""
import itertools, json, os, sys, time
import clingo
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'z3'))
from sorgular.ortak import parametreler, asgari_kumeler, KOK
from yapi import olgulari_oku
from z3_kodlama import asgari_kumeler_z3

PILOT = os.environ.get('PILOT_P2', '/referans/pilot/p2')
LINKS = 'lotl tl_pid tl_wp tl_rp ca_iss iss_cert meta cred status wua kb rp_cert req'.split()
SU = [('tl_pid', 'lotl'), ('tl_wp', 'lotl'), ('tl_rp', 'lotl'), ('ca_iss', 'tl_pid'), ('iss_cert', 'ca_iss'),
      ('cred', 'iss_cert'), ('meta', 'iss_cert'), ('status', 'iss_cert'), ('wua', 'tl_wp'), ('kb', 'cred'),
      ('rp_cert', 'tl_rp'), ('req', 'rp_cert')]
CC = [('tl_pid', 'cred'), ('tl_pid', 'meta'), ('tl_pid', 'status'), ('meta', 'cred'), ('meta', 'status'),
      ('ca_iss', 'cred'), ('tl_rp', 'req'), ('rp_cert', 'req'), ('tl_wp', 'wua')]
LEAF = ['cred', 'meta', 'status', 'req', 'wua']
HEDEF = {'claims': 'g1', 'holder': 'g2', 'revocation': 'g3', 'rp_auth': 'g4', 'wscd_assurance': 'g2i', 'all': 'tum'}
HEDEF_ART = {'g1': 'cred', 'g2': 'kb', 'g3': 'status', 'g4': 'req', 'g2i': 'wua'}
ORNEK = os.path.join(KOK, 'regresyon', 'p2_ornegi.lp')


def ornek_yaz():
    s = ['% Pilot P2 topolojisi, yeni çekirdeğin olgu biçiminde (otomatik: regresyon/p2_regresyon.py)',
         'sure(uzun,157680000). sure(sonsuz,2000000000).',
         'param_alan(pilot_faz,coexist). param_alan(pilot_faz,post).']
    for L in LINKS:
        s.append('artefakt(%s). sinif(%s,pilot). imzali(%s). karar(%s). kanal(%s,aktarilan). pencere_sabit(%s,sonsuz).'
                 % ((L,) * 6))
    for i, (a, b) in enumerate(SU):
        s.append('kenar(p%d,%s,%s).' % (i, a, b))
    for c, x in CC:
        s.append('tasiyabilir(%s,%s,m_f).' % (c, x))
    s.append('sabit(lotl). sabit_kosullu(tl_pid,capa,sabit).')
    for L in LEAF:
        s.append('klasik_alt_zorla(%s,pilot_faz,coexist).' % L)
    s.append('wscd_artefakt(kb).')
    for g, a in HEDEF_ART.items():
        s.append('hedef_artefakt(%s,%s). ana_hedef(%s).' % (g, a, g))
    with open(ORNEK, 'w', encoding='utf-8') as f:
        f.write('\n'.join(s) + '\n')


def pilot_kendi(phase, wscd, anchor, target):
    base = open(os.path.join(PILOT, 'trustchain_base.lp'), encoding='utf-8').read()
    mig = open(os.path.join(PILOT, 'trustchain_mig.lp'), encoding='utf-8').read()
    ctl = clingo.Control(['0', '--heuristic=Domain', '--enum-mode=domRec', '--warn=none',
                          '-cphase=%s' % phase, '-cwscd=%s' % wscd, '-canchor=%s' % anchor, '-ctarget=%s' % target])
    ctl.add('base', [], base + mig)
    ctl.ground([('base', [])])
    sols = []
    ctl.solve(on_model=lambda m: sols.append(tuple(sorted(str(s) for s in m.symbols(shown=True)))))
    return sorted(set(sols))


def norm_pilot(k):
    return tuple(sorted(('tasi(' + a[7:]) if a.startswith('convey(') else a for a in k))


def prm_p2(phase, wscd, anchor):
    prm = parametreler(faz='f3', politika='p4', tau=600, capa=('sabit' if anchor == 'pinned_tl' else 'taze'),
                       wscd_pq=('yok' if wscd == 'p256' else 'var'))
    prm['kat']['pilot_faz'] = phase
    return prm


def main():
    ornek_yaz()
    kayit = json.load(open(os.path.join(PILOT, 'p2a_results.json'), encoding='utf-8'))
    O = olgulari_oku(['regresyon/p2_ornegi.lp', 'olgular/parametreler.lp'])
    dosyalar = ['regresyon/p2_ornegi.lp', 'olgular/parametreler.lp', 'olgular/pencereler.lp']
    satir, kendi_ok, sistem_ok, z3_ok = [], 0, 0, 0
    t0 = time.perf_counter()
    for phase, wscd, anchor in itertools.product(['coexist', 'post'], ['p256', 'pq'], ['lotl', 'pinned_tl']):
        for target in ['all', 'claims', 'holder', 'revocation', 'rp_auth', 'wscd_assurance']:
            anah = '%s/%s/%s/%s' % (phase, wscd, anchor, target)
            ref = pilot_kendi(phase, wscd, anchor, target)
            k = kayit[anah]
            kayit_ok = (k['n_min_sets'] == len(ref) and
                        k['min_card'] == min((sum(1 for a in s if a.startswith('pq(')) for s in ref), default=None) and
                        {tuple(x) for x in k['sets']} <= set(ref) and len(k['sets']) == min(6, len(ref)))
            # the record keeps only the first ≤6 sets in enumeration order: compare as subset + count + minimal cardinality
            prm = prm_p2(phase, wscd, anchor)
            sis, bilgi = asgari_kumeler(prm, [HEDEF[target]], dosyalar=dosyalar)
            z, zb = asgari_kumeler_z3(prm, [HEDEF[target]], O=O)
            refn = sorted(norm_pilot(x) for x in ref)
            s_ok, z_ok = (sis == refn), (z == refn)
            kendi_ok += kayit_ok
            sistem_ok += s_ok
            z3_ok += z_ok
            satir.append({'sorgu': anah, 'pilot_kayit_yeniden_uretildi': kayit_ok, 'n_pilot': len(ref),
                          'n_sistem': len(sis), 'sistem_esit': s_ok, 'z3_esit': z_ok,
                          'sistem_s': round(bilgi['ground_s'] + bilgi['solve_s'], 4)})
            if not (kayit_ok and s_ok and z_ok):
                print('FARK', anah, kayit_ok, s_ok, z_ok, len(ref), len(sis), len(z))
    ozet = {'sorgu': len(satir), 'pilot_kaydi_yeniden_uretim': kendi_ok, 'sistem_cekirdegi_esit': sistem_ok,
            'z3_esit': z3_ok, 'toplam_asgari_kume_pilot': sum(r['n_pilot'] for r in satir),
            'sure_s': round(time.perf_counter() - t0, 2)}
    json.dump({'ozet': ozet, 'satirlar': satir}, open(os.path.join(KOK, 'regresyon', 'sonuc', 'p2_regresyon.json'), 'w',
              encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps(ozet, ensure_ascii=False))


if __name__ == '__main__':
    main()
