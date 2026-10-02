"""Job lists for battery v1.4 (pre-registration amendment 10): v1.3 jobs plus the kontrol-ES384 arm.

Every kontrol-EdDSA job is copied to the kontrol-ES384 arm with the ES384 counterpart vector when one exists.
v1.4 is mounted at /v/v1.3 (it is a byte-identical superset of v1.3), so file paths keep the v1.3 prefix.
Output: jobs-v1.4.jsonl (measurement), jobs-prefreeze-v1.4.jsonl (validity gate incl. ES384 rows).
Usage: python make_jobs_v14.py
"""
import io, json, os

H = os.path.dirname(os.path.abspath(__file__))
M = json.load(io.open(os.path.join(H, '..', 'vector-generator', 'vectors', 'v1.4', 'MANIFEST.json'), encoding='utf-8'))
byid = {v['id']: v for v in M['vektorler']}
counterpart = {v['insa']['v13_esi']: v['id'] for v in M['vektorler'] if v['kol'] == 'kontrol-ES384'}
edDSA_vectors = {v['id'] for v in M['vektorler'] if v['kol'] == 'kontrol-EdDSA'}

def extend(src, dst):
    jobs = [json.loads(l) for l in io.open(os.path.join(H, src), encoding='utf-8') if l.strip()]
    out = list(jobs)
    for j in jobs:
        if j['kol'] != 'kontrol-EdDSA':
            continue
        vid = j['vektor_id']
        if vid in counterpart:
            v = byid[counterpart[vid]]
            n = dict(j, vektor_id=v['id'], dosya='v1.3/' + v['dosya'], kol='kontrol-ES384')
            if n.get('algler'):
                n['algler'] = ';'.join('ES384' if a == 'EdDSA' else a for a in n['algler'].split(';'))
        elif vid in edDSA_vectors:
            continue
        else:
            n = dict(j, kol='kontrol-ES384')
        out.append(n)
    with io.open(os.path.join(H, dst), 'w', encoding='utf-8', newline='\n') as f:
        for j in out:
            f.write(json.dumps(j, sort_keys=True, ensure_ascii=False) + '\n')
    return len(jobs), len(out)

print('measurement', extend('jobs-v1.3.jsonl', 'jobs-v1.4.jsonl'))
print('validity gate', extend('jobs-prefreeze-v1.3.jsonl', 'jobs-prefreeze-v1.4.jsonl'))
