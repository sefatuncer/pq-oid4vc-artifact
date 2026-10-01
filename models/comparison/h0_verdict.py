"""H0 verdict (pre-registration section 3.1): the model is sound enough to judge H1-H5 only if
 (a) every health lemma has its pre-registered verdict (executable lemmas verified unless the plan expects F),
 (b) under policy P0 and coexistence a stripping/downgrade attack exists (ASP: cells not secured; Tamarin: trace),
 (c) the total mutation score is at least 0.90.
Inputs are read only; writes H0-RESULT.json. Usage: python h0_verdict.py
"""
import csv, json, os, re

H = os.path.dirname(os.path.abspath(__file__))
M = os.path.join(H, '..')
HEALTH = re.compile(r'^(executable|attack_needs_crqc)')

def plan(path):
    exp = {}
    for line in open(path, encoding='utf-8'):
        if line.startswith('#') or not line.strip():
            continue
        c = line.rstrip('\n').split('\t')
        if len(c) >= 7 and c[6]:
            exp[(c[0], c[1])] = dict(x.split('=', 1) for x in c[6].split(';') if '=' in x)
        elif len(c) >= 2:
            exp.setdefault((c[0], c[1]), {})
    return exp

res = {}
health = {'checked': 0, 'as_expected': 0, 'expected_F': 0, 'mismatch': []}
for ozet, varyant in ((os.path.join(M, 'tamarin', 'sonuc', 'ozet.csv'), os.path.join(M, 'tamarin', 'betik', 'varyantlar.tsv')),
                      (os.path.join(M, 'mechanisms', 'sonuc', 'ozet.csv'), os.path.join(M, 'mechanisms', 'on_kayit_varyantlar.tsv'))):
    exp = plan(varyant)
    for r in csv.DictReader(open(ozet, encoding='utf-8')):
        if not HEALTH.match(r['lemma']):
            continue
        e = exp.get((r['kural'], r['varyant']), {}).get(r['lemma'], 'V')
        o = {'verified': 'V', 'falsified': 'F'}.get(r['sonuc'], r['sonuc'])
        health['checked'] += 1
        health['expected_F'] += e == 'F'
        if e == o:
            health['as_expected'] += 1
        else:
            health['mismatch'].append([r['kural'], r['varyant'], r['lemma'], e, o])
res['a_health'] = health
res['a_pass'] = health['checked'] == health['as_expected']

a2 = list(csv.DictReader(open(os.path.join(H, 'A2-politika.csv'), encoding='utf-8')))
p0 = [r for r in a2 if r['politika'] == 'p0' and r['faz'] in ('f1', 'f2')]
asp_violation = all(int(r['SAT']) == 0 for r in p0)
tam = [r for r in csv.DictReader(open(os.path.join(M, 'tamarin', 'sonuc', 'ozet.csv'), encoding='utf-8'))
       if (r['kural'], r['varyant'], r['lemma']) == ('R2', 'M_expect_absent', 'S1_downgrade_trace')]
tamarin_trace = bool(tam) and tam[0]['sonuc'] == 'verified'
res['b_asp_p0_coexistence_cells'] = {'cells': sum(int(r['hucre']) for r in p0), 'secured': sum(int(r['SAT']) for r in p0)}
res['b_tamarin_trace'] = 'R2/M_expect_absent/S1_downgrade_trace = ' + (tam[0]['sonuc'] if tam else 'missing')
res['b_pass'] = asp_violation and tamarin_trace

ms = json.load(open(os.path.join(M, 'mutation', 'mutation-score.json'), encoding='utf-8'))['total']
res['c_mutation'] = ms
res['c_pass'] = ms['score'] is not None and ms['score'] >= 0.90
res['H0'] = 'satisfied' if res['a_pass'] and res['b_pass'] and res['c_pass'] else 'not satisfied'
json.dump(res, open(os.path.join(H, 'H0-RESULT.json'), 'w', encoding='utf-8'), indent=1)
print(json.dumps(res, indent=1))
