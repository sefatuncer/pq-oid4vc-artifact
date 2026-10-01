import time, json, random, itertools, sys
import clingo
import z3

BASE = open('trustchain_base.lp').read()
MIG = open('trustchain_mig.lp').read()
ORD = open('order.lp').read()

def solve_min_sets(consts, extra=''):
    ctl = clingo.Control(['0', '--heuristic=Domain', '--enum-mode=domRec'] + [f'-c{k}={v}' for k, v in consts.items()])
    ctl.add('base', [], BASE + MIG + extra)
    ctl.ground([('base', [])])
    sols = []
    t = time.perf_counter()
    res = ctl.solve(on_model=lambda m: sols.append(sorted(str(s) for s in m.symbols(shown=True))))
    return sols, time.perf_counter() - t, str(res)

out = {}
print('== P2a: subset-minimal PQ migration sets (clingo domRec) ==')
t_all = time.perf_counter()
for phase, wscd, anchor in itertools.product(['coexist', 'post'], ['p256', 'pq'], ['lotl', 'pinned_tl']):
    for target in ['all', 'claims', 'holder', 'revocation', 'rp_auth', 'wscd_assurance']:
        c = dict(phase=phase, wscd=wscd, anchor=anchor, target=target)
        sols, dt, res = solve_min_sets(c)
        key = f'{phase}/{wscd}/{anchor}/{target}'
        out[key] = dict(n_min_sets=len(sols), min_card=min((sum(1 for a in s if a.startswith('pq(')) for s in sols), default=None), time_s=round(dt, 4), sets=sols[:6])
print('total P2a wall s:', round(time.perf_counter() - t_all, 3), 'queries:', len(out))
for k in ['coexist/p256/lotl/claims', 'coexist/p256/lotl/holder', 'coexist/pq/lotl/holder', 'coexist/pq/lotl/all',
          'post/pq/lotl/claims', 'coexist/pq/pinned_tl/claims', 'coexist/p256/lotl/revocation']:
    v = out[k]
    print(k, '-> n_min_sets', v['n_min_sets'], 'min_pq_card', v['min_card'], 't', v['time_s'])
    for s in v['sets'][:3]:
        print('    ', ' '.join(s))
json.dump(out, open('p2a_results.json', 'w'), indent=1)

# ---- P2b ordering ----
print('== P2b: migration order for coexist/pq/lotl/claims (first minimal set) ==')
sol = out['coexist/pq/lotl/claims']['sets'][0]
facts = ''.join(f'target_pq({a[3:-1]}).' for a in sol if a.startswith('pq('))
facts += ''.join(f'conv({a[7:-1]}).' for a in sol if a.startswith('convey('))
ctl = clingo.Control(['0', '--opt-mode=optN', '-cphase=coexist', '-cwscd=pq', '-canchor=lotl'])
ctl.add('base', [], BASE + ORD + facts)
ctl.ground([('base', [])])
best = []
t = time.perf_counter()
def onm(m):
    if m.optimality_proven:
        best.append(sorted(((s.arguments[1].number, str(s.arguments[0])) for s in m.symbols(shown=True))))
ctl.solve(on_model=onm)
print('order solve s:', round(time.perf_counter() - t, 3), 'optimal orders:', len(best))
for b in best[:4]:
    print('   ', ' -> '.join(x[1] for x in b))

# ---- P2c z3 cross-check (same semantics, explicit acyclic encoding) ----
print('== P2c: z3 cross-check ==')
links = 'lotl tl_pid tl_wp tl_rp ca_iss iss_cert meta cred status wua kb rp_cert req'.split()
su = dict(tl_pid='lotl', tl_wp='lotl', tl_rp='lotl', ca_iss='tl_pid', iss_cert='ca_iss', cred='iss_cert', meta='iss_cert',
          status='iss_cert', wua='tl_wp', kb='cred', rp_cert='tl_rp', req='rp_cert')
cc = [('tl_pid','cred'),('tl_pid','meta'),('tl_pid','status'),('meta','cred'),('meta','status'),('ca_iss','cred'),('tl_rp','req'),('rp_cert','req'),('tl_wp','wua')]
topo = ['lotl','tl_pid','tl_wp','tl_rp','ca_iss','iss_cert','meta','cred','status','wua','kb','rp_cert','req']
goalmap = dict(claims='cred', holder='kb', revocation='status', rp_auth='req', wscd_assurance='wua')

def z3_min_sets(phase, wscd, anchor, target):
    pq = {l: z3.Bool('pq_' + l) for l in links}
    cv = {(c, x): z3.Bool(f'cv_{c}_{x}') for c, x in cc}
    anchored = {'lotl'} | ({'tl_pid'} if anchor == 'pinned_tl' else set())
    F = {}
    for l in topo:
        f = z3.Not(pq[l])
        if l in su and l not in anchored:
            f = z3.Or(f, F[su[l]])
        if phase == 'coexist' and l in ('cred', 'meta', 'status', 'req', 'wua'):
            exp = z3.Or([z3.And(cv[(c, x)], z3.Not(F[c])) for c, x in cc if x == l] or [z3.BoolVal(False)])
            f = z3.Or(f, z3.And(pq[l], z3.Not(exp)))
        F[l] = f
    s = z3.Solver()
    if wscd == 'p256':
        s.add(z3.Not(pq['kb']))
    tg = list(goalmap) if target == 'all' else [target]
    for g in tg:
        s.add(z3.Not(F[goalmap[g]]))
    allv = list(pq.values()) + list(cv.values())
    sols = []
    # enumerate subset-minimal solutions: shrink each model to a minimal one, then block supersets
    while s.check() == z3.sat:
        m = s.model()
        true = [v for v in allv if z3.is_true(m.eval(v, model_completion=True))]
        # greedy shrink to subset-minimal
        changed = True
        while changed:
            changed = False
            for v in list(true):
                trial = [u for u in true if not u.eq(v)]
                s.push(); s.add([u for u in trial]); s.add([z3.Not(u) for u in allv if not any(u.eq(w) for w in trial)])
                ok = s.check() == z3.sat
                s.pop()
                if ok:
                    true = trial; changed = True; break
        sols.append(sorted(str(v) for v in true))
        s.add(z3.Or([z3.Not(v) for v in true]))
    return sols

agree = 0; checked = 0; t = time.perf_counter()
for phase, wscd, anchor in itertools.product(['coexist', 'post'], ['p256', 'pq'], ['lotl', 'pinned_tl']):
    for target in ['all', 'claims', 'holder', 'revocation', 'rp_auth', 'wscd_assurance']:
        zs = z3_min_sets(phase, wscd, anchor, target)
        cs, _, _ = solve_min_sets(dict(phase=phase, wscd=wscd, anchor=anchor, target=target))
        norm = lambda sol: sorted(('pq_' + a[3:-1]) if a.startswith('pq(') else ('cv_' + a[7:-1].replace(',', '_')) for a in sol)
        checked += 1
        if sorted(map(tuple, zs)) == sorted(tuple(norm(x)) for x in cs):
            agree += 1
        else:
            print('MISMATCH', phase, wscd, anchor, target, len(zs), len(cs))
print(f'z3 vs clingo agreement: {agree}/{checked} queries; z3+clingo wall s {round(time.perf_counter()-t,2)}')

# ---- P2d scale test: random layered trust DAGs, minimum-cardinality hitting set ----
print('== P2d: scale test (random layered DAGs) ==')
def rand_instance(n, seed):
    rnd = random.Random(seed)
    layers = max(3, n // 10)
    lay = {i: i * layers // n for i in range(n)}
    facts = []
    for i in range(n):
        facts.append(f'link(a{i}).')
        parents = [j for j in range(n) if lay[j] == lay[i] - 1]
        for p in rnd.sample(parents, min(len(parents), rnd.choice([1, 1, 2]))):
            facts.append(f'signed_under(a{i},a{p}).')
        ups = [j for j in range(n) if lay[j] < lay[i]]
        for c in rnd.sample(ups, min(len(ups), 2)):
            facts.append(f'can_convey(a{c},a{i}).')
    roots = [i for i in range(n) if lay[i] == 0]
    facts += [f'anchored(a{r}).' for r in roots]
    leaves = [i for i in range(n) if lay[i] == layers - 1]
    facts += [f'tgt(a{l}).' for l in rnd.sample(leaves, min(len(leaves), 5))]
    return ''.join(facts)
PROG = '''coexist(L) :- tgt(L).
{ pq(L) : link(L) }. { convey(C,X) : can_convey(C,X) }.
classical(L) :- link(L), not pq(L).
forgeable(L) :- classical(L).
forgeable(L) :- signed_under(L,P), forgeable(P), not anchored(L).
expected(X) :- convey(C,X), not forgeable(C).
forgeable(L) :- pq(L), coexist(L), not expected(L).
:- tgt(L), forgeable(L).
#minimize { 1@2,L : pq(L) ; 1@1,C,X : convey(C,X) }.
'''
for n in [25, 50, 100, 200, 400]:
    ts = []
    for seed in range(3):
        ctl = clingo.Control(['--opt-mode=opt'])
        ctl.add('base', [], rand_instance(n, seed) + PROG)
        t = time.perf_counter(); ctl.ground([('base', [])]); tg = time.perf_counter() - t
        t = time.perf_counter(); r = ctl.solve(); ts.append((round(tg, 3), round(time.perf_counter() - t, 3), str(r)))
    print(f'n={n} links (3 seeds): (ground_s, solve_s, result) =', ts)
