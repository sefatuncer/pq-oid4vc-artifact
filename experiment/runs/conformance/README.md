# Adapter conformance test before the freeze (decision D9)

The validity gate (`../DECISIONS-PREFREEZE.md`) runs single-signature objects signed with the default issuer key under
`GEC`. It cannot show adapter defects in key selection by kid, in multi-signature objects, in the legacy issuer of L4c or
in the policy configurations. This test runs every adapter on objects outside the battery that cover those paths. It is
an instrument check: it does not measure, and its outputs are not analysed with the frozen scripts.

## Objects (`generate.py`, `vectors/v1.3/`, `results/self-check.txt`)

38 objects. 36 mirror a battery vector of v1.4: the same protected and unprotected headers (kid, x5c), the same
signer keys and the same signature order. Only the payload differs: a claim `jti` is added and every signature is made
again. Two derived objects (an SD-JWT VC signed only with EdDSA or ES384, with kid) have no counterpart in the control
arms. The generator checks every object independently: every signature verifies with the key of its recorded role,
every kid names that key, the headers are byte-identical to the mirrored vector, the payload equals the mirrored
payload plus `jti`, and no object has the SHA-256 of any battery file (246 files). The folder is laid out like a
battery (`vectors/v1.3/MANIFEST.json`) so that the adapters read it exactly as they read the battery.

| Arm | Mirrored vectors |
|---|---|
| `kontrol-EdDSA` | VPLUS_ES256, VPLUS_EdDSA, L4C-JOSE; T1K, T1K-SIRA-ters, T5K; COSE-VPLUS_ES256, COSE-VPLUS_EdDSA, L4C-COSE; COSE-K1K, COSE-K1K-SIRA-ters, COSE-K4K; VC01; VC09, VC09-SIRA-ters; derived SD-JWT VC (EdDSA) |
| `kontrol-ES384` | the `-ES384` counterparts of the X-specific vectors above, the shared vectors, derived SD-JWT VC (ES384) |
| `tedavi-ML-DSA-65` | VPLUS_ML-DSA-65, T1P, T1P-SIRA-ters, T5P, COSE-VPLUS_ML-DSA-65, COSE-K1P, COSE-K1P-SIRA-ters, COSE-K4P, VC02, VC07, VC07-SIRA-ters and the shared vectors |

## Job rows (`jobs.jsonl`, `expected.tsv`)

258 rows. A row is included only if the oracle decision of the mirrored (vector, policy, arm) row is an acceptance
(`accept-classical` or `accept-hybrid`), for the policies GEC, IZIN-A, IZIN-AX, L4, L4-S, L4-Y, P0 and P1. Every expected
decision is therefore `kabul`.

**Why acceptances only.** The confirmatory variable Y_L4 and the descriptive variables D_soy, B5 and L1 separate targets
by rejections: T2/K2 (X corrupted), T3/K3 (X stripped), VPLUS_ES256 under the L4 family and VPLUS_X under IZIN-A. None of
these rows, and no T3/K3 object, is in the test. A wrong acceptance cannot be shown by this test. It covers the defect
class seen in COSE-014 (decision D8): a valid object rejected because the adapter selects the wrong key or signer. An
acceptance row can still reveal that a target fails a case on which Y depends (for example T1K under L4). Such
pre-knowledge is one-sided and is disclosed in the pre-registration.

## Run and comparison

```
docker run --rm --network none -v "<repo>/experiment/vector-generator:/work:ro" -v "<repo>/experiment/runs/conformance:/out" \
    -v "<repo>/experiment/oracle/merged:/oracle:ro" pq-a09-credgen:1.3 python /out/generate.py /out
bash experiment/runs/conformance/run.sh                 # every target, output outputs/<target>.jsonl
python experiment/runs/conformance/compare.py           # results/conformance.csv, results/SUMMARY.csv
```

`compare.py` reads, per target, the control-label arm and, for targets that passed the ML-DSA-65 gate, the ML-DSA-65
arm. Classes: `uyumlu` (accepted), `uygulanamaz` and `ifade-edilemedi` (fixed in advance in the target's mapping),
`sapma` (anything else). It also derives the L4 form as `analysis/analyze_c3.py` does.

## Results (`results/SUMMARY.csv`, after the corrections of decision D9)

31 targets, 3,182 (target, row) cells: 630 accepted, 2,314 `uygulanamaz`, 201 `ifade-edilemedi`, 37 deviations. Every
remaining deviation is library behaviour:

| Target | Rows | Outcome | Reason |
|---|---|---|---|
| SDJWT-002 | 16 | exception in `SdJwt.parse` (sdjwt.dart L144) on every JWS-level object given as `<jws>~` | the library reads `_sd_alg` as a required string (`Hasher.fromString(payload['_sd_alg'])`, sdjwt.dart L143-144); RFC 9901 §4.1.1 makes the claim optional with the default sha-256. Same outcome in the validity gate |
| SDJWT-021 | 9 | `typ` rejected (only `vc+sd-jwt`), EdDSA not supported | decision D1 |
| SDJWT-018 | 8 | `KeyError: 'disclosures'` in `sd_jwt/common.py` L143 on General JSON SD-JWT (VC07, VC09, both orders) | the library reads `disclosures` from the top level of the JSON object; the battery places them in the first unprotected header, as RFC 9901 §8.3 requires. The mirrored battery vector fails in the same way |
| SDJWT-010 | 4 | "The JWS kid header claim is required" on VC01 (key identified by x5c) | josekit requires a matching kid header when the verifier key has a kid |

Corrections made after the first run (all recorded in decision D9): COSE-001 (kid decoded as text), COSE-014
(COSE_Sign key when no signer carries the ES256 kid), SDJWT-015 (multi-signature L4/L4-S recorded as
`ifade-edilemedi`), the error class of a `KeyError` in the shared Python adapter. The first run also exposed the kid
defect of battery v1.4 (decision D9).

L4 form and Y-determining row per target (`l4_form`, `l4_determining_row` in `results/SUMMARY.csv`): every target
whose Y-determining row is `ifade-edilemedi` has a second attempt under the evidence rule
(`../evidence-rule/`, `../analysis/evidence-rule.csv`), except SDJWT-021, which has no control label.
