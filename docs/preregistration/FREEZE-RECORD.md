# Freeze record: pre-registration v1.0

Written after the freeze (pre-registration Section 11, steps 1 and 8). Not part of the hash list.

| Item | Value |
|---|---|
| Freeze date | 2026-10-03 |
| Frozen document | `docs/preregistration/PREREGISTRATION-v1.0.md` |
| Hash list | `docs/preregistration/FREEZE-SHA256SUMS`, 769 files |
| SHA-256 of the hash list | `283ac30b38b1e91e266c8a6b5c728ccedad01c8603c4ba04af33d16c8b16f487` |
| Public commit | `bb0e66933f88afa90220f57ffe474d527d297916` (pull request #10; `29a835a79c9a34e47c86243f858a541925f6d193` before the history rewrite below, same tree) |
| Tag | `prereg-v1.0`, annotated tag object `bdac1b9f94abd4b8183a8894405cedcb64b2d775`, tagger date 2026-10-03T10:15:13Z, pointing to the public commit (first tag object `20f1f616f127589d6055339710fbaf89ccb6365b`, moved with the history rewrite below) |
| External timestamp | OpenTimestamps proof `docs/preregistration/FREEZE-SHA256SUMS.ots` of the SHA-256 of the hash list, submitted on 2026-10-03 to the public calendars a.pool.opentimestamps.org, b.pool.opentimestamps.org, a.pool.eternitywall.com and ots.btc.catallaxy.com (client opentimestamps-client 0.7.2). Only the digest left the machine. Upgraded on 2026-10-03 with `ots upgrade`: the proof contains a Bitcoin block header attestation for block 969719 (other calendars still pending) |

**Verification.**

```
sha256sum -c docs/preregistration/FREEZE-SHA256SUMS                         # every frozen file
sha256sum docs/preregistration/FREEZE-SHA256SUMS                            # 283ac30b...
ots verify docs/preregistration/FREEZE-SHA256SUMS.ots                       # after the upgrade
git cat-file -p prereg-v1.0                                                 # tag object, object bb0e669...
```

The hash list was checked on the public commit (an export of the commit, `sha256sum -c`: all files match) before the
tag was set.

**Section 12.6 lists, re-verified on 2026-10-03 before the freeze** (Section 11, step 1):
- unchanged since their anchors, by comparison with the file at the anchor commit or with the full anchored SHA-256:
  `experiment/vector-generator/vectors/v1.3/MANIFEST.json`, `experiment/vector-generator/vectors/v1.3/SHA256SUMS`,
  `experiment/vector-generator/keys/v1/SHA256SUMS`, `experiment/vector-generator/keys/v1.3/SHA256SUMS` (anchor 9),
  `models/known-answer-tests/nsurum/kat_nsurum.tsv` (anchor 8), `experiment/inventory/SELECTION.csv` and
  `experiment/inventory/FRAME.csv` (anchor 2 hashes), `experiment/oracle/oracle-A/decisions.tsv` and
  `experiment/oracle/oracle-B/decisions.tsv` (hashes recorded in `experiment/oracle/merged/SUMMARY.json`): 9 of 9;
- changed in bytes as stated: `experiment/vector-generator/BATTERY-MAPPING.md` (one path string),
  `models/mechanisms/on_kayit_varyantlar.tsv` (2 comment lines), `models/tamarin/betik/on_kayit_h3_sadelestirme.tsv`
  (1 comment line), `models/tamarin/betik/varyantlar.tsv` (the anchored bytes, SHA-256 `a88d972e…` at anchor 3,
  followed by 7 appended R7hx lines): 4 of 4; `experiment/inventory/CRITERIA-DRAFT.md` translated and
  `experiment/statistics/SHA256SUMS` regenerated, as stated.

**History rewrite of 2026-10-03 (privacy).** Recorded Docker image and container lists in the first 13 public
commits named unrelated local images and containers of the build machine (removed from the current files on the same
day, before the freeze). The public history was rewritten to remove those lines from these lists in every commit, and
one README line that named a local container. The trees of all later commits, including the freeze commit, are
byte-identical to the trees before the rewrite, so the hash list and its SHA-256 are unchanged and the OpenTimestamps
proof is unaffected. The commit identities changed (freeze commit `29a835a` → `bb0e669`), and the tag was recreated
on the rewritten freeze commit with the same message and tagger date. Pull-request references created before the rewrite
still point to the earlier commits.
