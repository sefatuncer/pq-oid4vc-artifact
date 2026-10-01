"""Compares an adapter's smoke-test output with expected.json.
Usage: python check_smoke.py <expected.json> <output.jsonl> <TARGET>
Prints one line per job and a summary; exit code 1 if any job differs.
"""
import json
import sys

expected = json.load(open(sys.argv[1], encoding="utf-8"))[sys.argv[3]]
rows = [json.loads(l) for l in open(sys.argv[2], encoding="utf-8") if l.strip()]
bad = 0
print(f"{'job':4} {'vector':22} {'policy':16} {'arm':17} {'expected':42} {'observed':42} ok")
for r in rows:
    jid = r["vektor_id"].split("_")[0]
    exp = expected[jid]
    algs = [a["alg"] for a in r["dogrulanan_algoritmalar"]]
    obs = [r["sonuc_ham"], r["hata_sinifi"], algs[0] if algs else None]
    ok = list(exp) == obs
    bad += not ok
    fmt = lambda t: "/".join(str(x) for x in t if x is not None)
    print(f"{jid:4} {r['vektor_id'][4:26]:22} {r['politika']:16} {r['kol']:17} {fmt(exp):42} {fmt(obs):42} {'yes' if ok else 'NO'}")
    if not ok and r.get("hata_ozeti"):
        print(f"     detail: {r['hata_ozeti']}")
missing = set(expected) - {r["vektor_id"].split("_")[0] for r in rows}
print(f"\n{len(rows) - bad}/{len(rows)} jobs as expected; jobs without output: {sorted(missing) or 'none'}")
print(f"hedef_surum={rows[0]['hedef_surum']} adaptor_sha256={rows[0]['adaptor_sha256']}")
sys.exit(1 if bad or missing else 0)
