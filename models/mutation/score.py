"""Total mutation score (pre-registration section 4.17).

A mutant removes one protection. It is killed when a security lemma that is verified for its base
variant becomes falsified (Tamarin), or when the ASP property test reports the attack.
Score = killed / (total - equivalent - base_insecure). Reported per rule and in total.
Equivalent: known-answer-test probes whose expected outcome is "no attack" (redundant protection).
Base insecure: the protected base variant already violates every security lemma, so the mutant is uninformative.

Inputs (read only):
  ../tamarin/betik/varyantlar.tsv          rule mutants R1-R7h, role 'mutant:<protection>[(<base>)]'
  ../tamarin/sonuc/ozet.csv                Tamarin verdicts per (rule, variant, lemma)
  ../known-answer-tests/*/sonuc/tamarin_mutasyon.csv, asp_mutasyon.csv   known-answer-test mutants
Outputs: mutation-score.json, mutation-score.csv (one row per mutant)
Usage: python score.py
"""
import csv, glob, json, os, re
from collections import defaultdict

H = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(H, '..', 'tamarin')
HEALTH = re.compile(r'^(executable|attack_needs_crqc)')

def security(lemma):
    return not HEALTH.match(lemma) and not lemma.startswith('M_')

verdict = defaultdict(dict)                      # (rule, variant) -> {lemma: result}
for r in csv.DictReader(open(os.path.join(T, 'sonuc', 'ozet.csv'), encoding='utf-8')):
    verdict[(r['kural'], r['varyant'])][r['lemma']] = r['sonuc']

rows, protected = [], defaultdict(list)
lines = [l.rstrip('\n').split('\t') for l in open(os.path.join(T, 'betik', 'varyantlar.tsv'), encoding='utf-8')
         if l.strip() and not l.startswith('#')]
for c in lines:
    if len(c) > 2 and c[2] == 'korumali':
        protected[c[0]].append(c[1])
for c in lines:
    if len(c) < 3 or not c[2].startswith('mutant:'):
        continue
    rule, var, role = c[0], c[1], c[2]
    m = re.match(r'mutant:([^(]+)(?:\((.+)\))?$', role)
    removed, base = m.group(1), m.group(2)
    bases = [base] if base else protected[rule]
    mv = verdict[(rule, var)]
    killed_by = sorted({l for b in bases for l, res in verdict[(rule, b)].items()
                        if security(l) and res == 'verified' and mv.get(l) == 'falsified'})
    # If no security lemma holds for the base variant, removing the protection cannot be detected: the base is
    # already insecure (for R7h this is the finding itself). Such mutants are reported but not scored.
    base_secure = any(security(l) and res == 'verified' for b in bases for l, res in verdict[(rule, b)].items())
    rows.append({'source': 'rule', 'group': rule, 'mutant': var, 'removed': removed, 'base': '+'.join(bases),
                 'killed': int(bool(killed_by)), 'equivalent': 0, 'base_insecure': int(not base_secure),
                 'evidence': ';'.join(killed_by)})

for kat in sorted(glob.glob(os.path.join(H, '..', 'known-answer-tests', '*', 'sonuc'))):
    name = os.path.basename(os.path.dirname(kat))
    for fn, tool, attack in (('tamarin_mutasyon.csv', 'tamarin', 'falsified'), ('asp_mutasyon.csv', 'asp', 'SALDIRI')):
        p = os.path.join(kat, fn)
        if not os.path.exists(p):
            continue
        for r in csv.DictReader(open(p, encoding='utf-8')):
            rows.append({'source': 'kat-' + tool, 'group': name, 'mutant': r['kosu'], 'removed': r.get('mutasyon', ''),
                         'base': r.get('temel', ''), 'killed': int(r['gozlenen'] == attack),
                         'equivalent': int(r.get('beklenen') not in (attack,)), 'base_insecure': 0,
                         'evidence': r.get('lemma', r.get('sonda', ''))})

def score(sel):
    tot = len(sel); eq = sum(r['equivalent'] for r in sel); bi = sum(r['base_insecure'] for r in sel)
    k = sum(r['killed'] for r in sel if not r['equivalent'] and not r['base_insecure'])
    n = tot - eq - bi
    return {'mutants': tot, 'equivalent': eq, 'base_insecure': bi, 'killed': k, 'score': round(k / n, 4) if n else None}

groups = sorted({(r['source'], r['group']) for r in rows})
out = {'total': score(rows),
       'by_source': {s: score([r for r in rows if r['source'] == s]) for s in sorted({r['source'] for r in rows})},
       'by_group': {'%s/%s' % g: score([r for r in rows if (r['source'], r['group']) == g]) for g in groups},
       'base_insecure': [r for r in rows if r['base_insecure']],
       'surviving': [r for r in rows if not r['killed'] and not r['equivalent'] and not r['base_insecure']]}
json.dump(out, open(os.path.join(H, 'mutation-score.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
with open(os.path.join(H, 'mutation-score.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(json.dumps({k: out[k] for k in ('total', 'by_source')}, indent=1))
print('surviving:', [(r['group'], r['mutant']) for r in out['surviving']])
