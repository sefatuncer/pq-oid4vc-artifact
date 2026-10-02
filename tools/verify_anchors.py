#!/usr/bin/env python3
"""Check every SHA-256 record of the repository against the files it names.

The study fixed many files with SHA-256 lists before the runs (``SHA256SUMS``, ``*.sha256``,
``SHA256-ON-KAYIT.txt``, ``models/tamarin/sonuc/sha256*.txt`` ...). For the English release some
of these files were translated or renamed. The records themselves were not edited; instead the
recorded bytes are kept under ``archive/hash-anchored/<original path>``. This script shows that
every record entry is still accounted for.

For each entry the script looks, in this order, at
  1. the current file at the recorded path,
  2. the archived copy ``archive/hash-anchored/<recorded path>``,
  3. ``archive/hash-anchored/ANCHOR-NOTES.tsv``, which lists entries whose file already differed
     from the record in the base commit of this release (edited earlier in the private working
     history), entries whose recorded path was rewritten in the base commit (the file is named
     in the last column), and entries whose path lies outside the repository.

Entry classes:
  current   the current file matches the record
  archived  the archived copy matches the record
  noted     not matched, but listed in ANCHOR-NOTES.tsv and the current or archived file has the
            base-commit digest given there (or the path is outside the repository)
  FAIL      none of the above

Usage: python tools/verify_anchors.py [--root DIR] [--list] [--fails-only]
Exit code 0 if there is no FAIL, 1 otherwise. Standard library only.
"""
import argparse
import hashlib
import os
import posixpath
import re
import sys

ENTRY = re.compile(r'^([0-9a-f]{64})\s[ *](.+?)\s*$')
RECORD_NAME = re.compile(
    r'^(SHA256SUMS|[^/]*_SHA256SUMS|[^/]*\.sha256|SHA256-ON-KAYIT\.txt|sha256[^/]*\.txt'
    r'|[^/]*_sha256\.txt|[^/]*\.sha256\.txt)$')
ARCHIVE = 'archive/hash-anchored'
NOTES = ARCHIVE + '/ANCHOR-NOTES.tsv'
# Folders that are not part of the study's own records: third-party build output and the archive.
SKIP_DIR = re.compile(r'(^|/)(\.git|archive|cikti[^/]*)(/|$)')
# Old top-level folder names (docs/PATHS.md) used to resolve paths written in the old layout.
OLD_PREFIX = [
    ('01-korpus/', 'spec-corpus/'), ('02-izlenebilirlik/', 'traceability/'),
    ('03-tehdit-modeli/', 'threat-model/'), ('arac/test/', 'tools/regression-tests/'),
    ('arac/', 'tools/'), ('deney/envanter/', 'experiment/inventory/'),
    ('deney/imzalayici/', 'experiment/signer/'), ('deney/istatistik/', 'experiment/statistics/'),
    ('deney/kosum/', 'experiment/runs/'), ('deney/ortam/', 'experiment/environments/'),
    ('deney/uretec/', 'experiment/vector-generator/'), ('deney/', 'experiment/'),
    ('veri/', 'data/'), ('model/bilinen-cevap/', 'models/known-answer-tests/'),
    ('model/karsilastirma/', 'models/comparison/'), ('model/mekanizma/', 'models/mechanisms/'),
    ('model/ornekleme/', 'models/sampling/'), ('model/asp/ornekleme/', 'models/asp/sampling/'),
    ('model/', 'models/'),
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def find_records(root):
    out = []
    for d, dirs, files in os.walk(root):
        rel = os.path.relpath(d, root).replace(os.sep, '/')
        rel = '' if rel == '.' else rel
        dirs[:] = [x for x in dirs if not SKIP_DIR.search(posixpath.join(rel, x))]
        for name in files:
            if RECORD_NAME.match(name) and not name.endswith('.jws'):
                out.append(posixpath.join(rel, name))
    return sorted(out)


def candidates(record_dir, raw):
    """Possible repository-relative paths for a recorded path, most specific first."""
    p = raw.replace('\\', '/')
    if '/PQ-OID4VC/' in p:                      # absolute path of the working copy
        p = p.split('/PQ-OID4VC/', 1)[1]
    if p.startswith('./'):
        p = p[2:]
    base = []
    if not p.startswith('/'):
        base.append(posixpath.normpath(posixpath.join(record_dir, p)))
        d = record_dir
        while d:
            d = posixpath.dirname(d)
            base.append(posixpath.normpath(posixpath.join(d, p)))
    out = []
    for c in base:
        out.append(c)
        for old, new in OLD_PREFIX:
            if c.startswith(old):
                out.append(new + c[len(old):])
                break
    seen, uniq = set(), []
    for c in out:
        if c not in seen and not c.startswith('..'):
            seen.add(c)
            uniq.append(c)
    return uniq


def load_notes(root):
    notes = {}
    path = os.path.join(root, NOTES)
    if not os.path.exists(path):
        return notes
    with open(path, encoding='utf-8') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            cols = line.rstrip('\n').split('\t')
            if cols[0] == 'record':
                continue
            record, recorded_path, anchor, base_digest, status = cols[:5]
            actual = cols[5] if len(cols) > 5 else ''
            notes[(record, recorded_path)] = (anchor, base_digest, status, actual)
    return notes


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--root', default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument('--list', action='store_true', help='print every entry that is not "current"')
    ap.add_argument('--fails-only', action='store_true', help='print only FAIL entries')
    a = ap.parse_args()
    root = a.root
    notes = load_notes(root)
    totals = {'current': 0, 'archived': 0, 'noted': 0, 'FAIL': 0}
    per_record = []
    details = []
    for rec in find_records(root):
        rdir = posixpath.dirname(rec)
        counts = {'current': 0, 'archived': 0, 'noted': 0, 'FAIL': 0}
        with open(os.path.join(root, rec), encoding='utf-8', errors='replace') as f:
            lines = f.read().splitlines()
        for line in lines:
            m = ENTRY.match(line)
            if not m:
                continue
            anchor, raw = m.group(1), m.group(2)
            cls, where = 'FAIL', ''
            cands = candidates(rdir, raw)
            digests = []
            for c in cands:
                cur = os.path.join(root, c)
                if os.path.isfile(cur):
                    d = sha256(cur)
                    digests.append(d)
                    if d == anchor:
                        cls, where = 'current', c
                        break
            if cls == 'FAIL':
                for c in cands:
                    arc = os.path.join(root, ARCHIVE, c)
                    if os.path.isfile(arc):
                        d = sha256(arc)
                        digests.append(d)
                        if d == anchor:
                            cls, where = 'archived', ARCHIVE + '/' + c
                            break
            if cls == 'FAIL':
                note = notes.get((rec, raw))
                if note:
                    _, base_digest, status, actual = note
                    if actual and os.path.isfile(os.path.join(root, actual)):
                        d = sha256(os.path.join(root, actual))
                        if d == anchor:
                            digests.append(base_digest)
                    if status == 'outside-repository' or base_digest in digests:
                        cls, where = 'noted', status + (' ' + actual if actual else '')
            counts[cls] += 1
            if cls != 'current':
                details.append((cls, rec, raw, where))
        for k in totals:
            totals[k] += counts[k]
        per_record.append((rec, counts))

    print('SHA-256 record check (tools/verify_anchors.py)')
    print('record | entries | current | archived | noted | FAIL')
    for rec, c in per_record:
        n = sum(c.values())
        print(f'{rec} | {n} | {c["current"]} | {c["archived"]} | {c["noted"]} | {c["FAIL"]}')
    n = sum(totals.values())
    print(f'TOTAL {len(per_record)} records | {n} entries | current {totals["current"]} | '
          f'archived {totals["archived"]} | noted {totals["noted"]} | FAIL {totals["FAIL"]}')
    if a.list or a.fails_only:
        for cls, rec, raw, where in details:
            if a.fails_only and cls != 'FAIL':
                continue
            print(f'  {cls:8s} {rec}: {raw} -> {where}')
    return 1 if totals['FAIL'] else 0


if __name__ == '__main__':
    sys.exit(main())
