# Pre-freeze validity gate v1.4 (run of 2026-10-03, decision D9)

Canonical gate on battery v1.4 after the corrections of decision D9 (`../../DECISIONS-PREFREEZE.md`): the 9 COSE
ES384 counterparts carry the kid of their signing key, and the adapter images were rebuilt with the corrected
sources. Run from `experiment/runs`:

```
bash adapters/_tools/run.sh jobs-prefreeze-v1.4.jsonl oncesi outputs/prefreeze-v1.4 <the 31 targets of CONTROL-LABELS.csv>
python adapters/_tools/gate_summary.py outputs/prefreeze-v1.4
python adapters/_tools/control_labels.py
```

Result: 31 targets, 1,240 (vector, policy, arm) cells. Compared with the run on the first generation of v1.4
(`../prefreeze-v1.4-first-generation/`), 6 cells differ, all in the ES384 arm of COSE-034, COSE-035 and COSE-036:
`COSE-VPLUS_EdDSA-ES384` is now accepted and `COSE-VMINUS_EdDSA-ES384` rejected as `imza-gecersiz`. Before the
correction the kid of these objects named the Ed25519 key, so the three adapters found no usable key. These targets
now also pass the ES384 gate; their control label stays EdDSA (`../../CONTROL-LABELS.csv`, column `gates_passed`).
`GATE-SUMMARY.csv` is byte-identical. Targets passing per algorithm: ES256 29, EdDSA 16, Ed25519 7, ES384 27,
ML-DSA-65 6, composite 0.
