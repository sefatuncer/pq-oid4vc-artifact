"""Descriptive Wilson 95% intervals of Y_L4 by stratum and by L4 form.

Post-hoc and descriptive (added 2026-10-28 after the paper review). The frozen analysis reports Wilson
intervals for the L4 forms but not for the strata. This script reads the statistics inputs of the
registered analysis and of deviation 1 and applies the Wilson function of the frozen statistics
package (implementation A, c3istat.kesin.wilson), so the intervals use the same method as the paper.

Usage, from experiment/runs:
    python -I analysis/subgroup_wilson.py
Output: analysis/results/subgroup-wilson.json and a table on stdout.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'statistics', 'scripts'))
from c3istat.kesin import wilson  # noqa: E402

INPUTS = {
    'registered': os.path.join(HERE, 'results', 'c3-input-primary.json'),
    'deviation-1': os.path.join(HERE, 'deviation-1', 'results', 'c3-input-primary.json'),
}


def groups(targets):
    """Targets of the primary T1 analysis: valid adapter and a determined Y_L4."""
    used = [t for t in targets if not t['adaptor_gecersiz'] and t['Y_L4'] is not None]
    out = {'all': used}
    for key in ('tabaka', 'l4_bicimi'):
        for t in used:
            out.setdefault(t[key], []).append(t)
    return out


def main():
    result = {}
    for name, path in INPUTS.items():
        with open(path, encoding='utf-8') as f:
            targets = json.load(f)['hedefler']
        rows = {}
        for group, members in sorted(groups(targets).items()):
            x, n = sum(t['Y_L4'] for t in members), len(members)
            lo, hi = wilson(x, n)
            rows[group] = {'x': x, 'n': n, 'share': x / n, 'wilson95': [lo, hi]}
            print(f'{name:12s} {group:6s} {x:3d}/{n:<3d} {x / n:6.1%}  [{lo:6.1%}, {hi:6.1%}]')
        result[name] = rows
    out = os.path.join(HERE, 'results', 'subgroup-wilson.json')
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(result, f, indent=2, sort_keys=True)
        f.write('\n')


if __name__ == '__main__':
    main()
