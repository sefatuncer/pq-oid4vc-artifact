# C3 adapter contract (Step 9, tasks 7 and 7a) — Oracle A proposal

> **Status:** draft of Oracle A, 25.09.2026, adopted by the maintainers as contract 1.0 with the pre-freeze addendum of Section 0 (2026-10-03); it goes into the freeze package.
> **Binding sources:**
> - PR §2B (n = 31; L4m/L4c; TK1–TK3; MR4; delegation), §2D items 1–2 (key path, `EdDSA`/`Ed25519`), §2E item 3 (label sensitivity), §2G item 4 (primary/secondary);
> - PR §4.13–§4.15 (L0–L5, B1–B6, evidence rule, indeterminate and adapter invalid), §6.4–§6.6 and §6.11;
> - work plan Step 9 task 7/7a and Step 10.
>
> **Oracle:** `karar.tsv` (Oracle A) and the decisions of Oracle B. An A–B disagreement falls into the "indeterminate" class (PR §4.15).
>
> (Quotations from the pre-registration are translated from Turkish; quotations from specifications are verbatim.)

## 0. Pre-freeze addendum (maintainers, 2026-10-03)

The maintainers adopted this proposal as **contract 1.0** for the C3 measurement. The body below is kept as written on
25.09.2026; this addendum lists where it is superseded. Where the body and this addendum differ, this addendum and
pre-registration v1.0 prevail. The runner interface is `experiment/runs/RUNNER.md`; decisions D1–D7 are in
`experiment/runs/DECISIONS-PREFREEZE.md`.

| Body | Superseded by |
|---|---|
| Oracle: `karar.tsv` of Oracle A and the decisions of Oracle B | The merged oracle `experiment/oracle/birlesik/karar_v14.tsv` (2,202 rows; A–B disagreements are `indeterminate`, as before) |
| Battery v1.2 (§2.1, the output example of §3, §4 item 3, §5.3, the COSE warning of §6) | Measurement battery **v1.4**: 230 vectors = the 200 vectors of v1.3 (byte-identical) + 30 ES384 counterparts (Amendment 10). v1.3 added 45 COSE vectors (the COSE warning, DECISION-NOTES N-0, no longer applies) and the legacy issuer `https://legacy-issuer.example` used by L4c (pre-registration Section 5.13; the first bullet of §5.3 no longer applies) |
| Arms `kontrol-EdDSA`, `kontrol-Ed25519`, `tedavi-ML-DSA-65`, `tedavi-composite` (§2.2) and the two-label control rule (§8 item 4) | A fifth arm `kontrol-ES384` (X = ES384). Control label = first label in the order EdDSA, Ed25519, ES384 whose validity gate the target passes (Decision D4, Amendment 10); per target in `experiment/runs/CONTROL-LABELS.csv` |
| Output path `outputs/r{1,2,3}/<target>.jsonl` and the full output object of §3 | `experiment/runs/outputs/measurement/<target>.<r1|r2|r3>.jsonl`. The mandatory fields are those of `RUNNER.md` §3. The adapter does not write `karar`: the analysis script `experiment/runs/analysis/analyze_c3.py` maps `sonuc_ham` to the decision with the table of §3.1. Fields that belong to TK2 (`tk`, `pq_servis_cagrilari`) are not used |
| TK2 plug-in class (§3.1 "TK2 service log", §5.0, §6 items 2 and 4) and the preliminary assignment table of §6 | **TK2 out of scope** (2026-10-01): a target without native support is TK3. The assignment, made before the measurement by API review and validity gate only, is `experiment/runs/TK-ASSIGNMENT.csv` (JOSE-102: TK3 primary, TK1 sensitivity, Decision D2). Composite arm: TK3 for every target. T2 covers TK1 targets and is descriptive (Amendment 11) |
| §4 item 1: pinning to `son_commit_sha` of `CERCEVE.csv`; historical baseline | Pinning to the versions of the build pretest, `experiment/environments/derleme-sonuc.csv` (Amendment 8, item 14). The historical baseline was removed (Amendment 11) |
| §4 item 3: battery and oracle checked with `sha256sum -c` | `experiment/runs/run_measurement.sh` checks `docs/preregistration/FREEZE-SHA256SUMS` (battery v1.4, merged oracle, job list, adapter sources, analysis and statistics scripts) before the first run; any mismatch stops the measurement |
| §4 timeouts | 60 s per vector inside the adapter process where the adapter implements it, and 30 min per target and run enforced by `experiment/runs/adapters/_tools/kos.sh`, which stops the container. Rows that a stopped run did not write are missing in that run, so the cell is unstable and becomes `indeterminate` (§4 repetition rule) |
| §5 L ladder | Only Y_L4 (L4m or L4c) is confirmatory. L0–L3, L5 and B1–B6 are descriptive; L2 is inferred from the API path string and L3 is computed without the API-evidence condition (Amendment 11). A control-arm rejection with `hata_sinifi = alg-desteklenmiyor` counts as "not supported", never as agreement with an oracle `reject` (Amendment 11) |
| §5.0 validity gate on SD-JWT targets with battery vectors | SD-JWT targets are gated with 16 SD-JWT-format vectors (`experiment/runs/vpm-sdjwt/`, Decision D1). SDJWT-002 does not use the result of its signature check: it is measured as is and flagged `integrity-failure` |
| §2.2 and §3.2: per-target `MAPPING.md` | Targets with their own adapter folder and the four `_rs` targets have `MAPPING.md`. For the 15 targets of the shared adapters `_py`, `_node`, `_go`, `_jvm` and `_kt`, the policy → API mapping, the B6 format decisions and the exception mapping are fixed in the target's entry of the shared adapter source (part of the freeze package) |
| §7 delegation rows REF-003, REF-011, irmago | Reference verifiers were removed (Amendment 11). SDJWT-004 (authlete) and SDJWT-010 are measured through the verification path they document (Amendment 8, item 15; Decision D5) |
| Policy names | `|sdjwtvc=…` and `@-19` split only the expected outcome; `P2` uses the library default; `L4-YOL` is `ifade-edilemedi` for every target (Decision D6). Calling conventions: Decision D7 |

## 1. Scope and roles

- **Adapter:** a thin wrapper that verifies one vector under one policy configuration through the **documented public API** of the target library. The library code is **not changed**.
  - The adapter does not write its own verification loop. If it does, this is a record of "expressible with custom code" (B4) and does not raise the L level (PR §4.13).
- **Runner:** manages the trial layout. It calls the adapter in a fresh container, writes the output to JSONL, compares it with the oracle and runs the divergence detector.
- **Oracle:** gives the expected decision for the triple (vector, policy, arm). The adapter does **not see** the oracle.
- **Pre-registration protection:** before the freeze only installation and V± (`VPLUS_*`/`VMINUS_*` under `GEC`) may be run on the targets. K1–K11 are not run (work plan Step 9 "Pre-registration protection"; risk R12).

## 2. Input

### 2.1 Vector

- `experiment/vector-generator/vektorler/v1.2/<family>/<id>.<jws|sdjwt|json>` and the MANIFEST entry.
- **`dogrulama_girdileri`:** `jwks`/`jwk`/`kid`, `guven_capalari`, `simdi` = 1790003700, `kb_aud`/`kb_nonce`, `htm`/`htu`, `beklenen_origin`.
- **Clock:** the adapter supplies the time as `simdi`: a fake clock or the "current time" parameter of the API. On a target that cannot do this, vectors containing `exp` are still valid (exp = 1821536000). The KB-JWT and DPoP `iat` values, however, fall outside the validity window with the real clock. In that case `indeterminate` is written with `hata_sinifi = zaman`, and a note is added per target.

### 2.2 Policy configuration (JSON)

```json
{
  "politika": "L4",                     // GEC | IZIN-A | IZIN-AX | L4 | L4-S | L4-Y | P0 | P1 | L4-YOL
  "kol": "tedavi-ML-DSA-65",            // kontrol-EdDSA | kontrol-Ed25519 | tedavi-ML-DSA-65 | tedavi-composite
  "A": "ES256",
  "X": "ML-DSA-65",                     // EdDSA | Ed25519 | ML-DSA-65 | ML-DSA-65-ES256
  "W": ["ES256", "ML-DSA-65"],          // allow set
  "R": ["ML-DSA-65"],                   // required set per issuer (R_I); [] for IZIN-*/GEC/P0/P1
  "coklu_imza": "gerekli-kume",         // en-az-biri (P0) | mevcut-tumu (P1) | gerekli-kume (L4) | gerekli-kume+tumu (L4-S) | gerekli-kume+W-disi-yok (L4-Y)
  "ihracci": {"iss": "https://issuer.example", "durum": "goc-etmis"},   // L4c: goc-etmis (migrated) | eski (old)
  "anahtar_yolu": "JWKS",               // JWKS | JWK | dogrudan (direct) | x5c+capa (X5C only) | jwk-basligi (DPoP only)
  "zincir_politikasi": null,            // L4-YOL: "yol-tam-pq"
  "sdjwtvc_surum": "-13",               // -13 (primary) | -19 (MR3)
  "kb_gerekli": true,                   // VP family
  "simdi": 1790003700
}
```

- The meaning of the configurations is in `METHOD.md` §2. The adapter translates this JSON into documented API calls of the target. The translation table is written per target to `experiment/runs/adapters/<target>/MAPPING.md`.
- If the target's API cannot express a field (e.g. R), the adapter does **not skip** that field. It marks the row with `sonuc_ham = ifade-edilemedi` (could not be expressed). This record becomes input to the L-level protocol (§5).

## 3. Output (one JSON object per line; `outputs/r{1,2,3}/<target>.jsonl`)

```json
{
  "sozlesme": "adaptor-sozlesme/1.0",
  "hedef_id": "JOSE-083", "hedef_surum": "2.15.0", "hedef_commit": "1d41a647…", "imaj_ozeti": "sha256:…",
  "adaptor_sha256": "…", "batarya": "v1.2", "manifest_sha256": "bb17aaa7…",
  "kosu": "r1", "tarih_utc": "2026-11-05T10:00:00Z",
  "vektor_id": "T1P_both_valid", "vektor_sha256": "…",
  "politika": "L4", "kol": "tedavi-ML-DSA-65", "tk": "TK2", "sdjwtvc_surum": "-13",
  "kontrol_etiketi": null,                  // "EdDSA" or "Ed25519" in the control arm (7a)
  "kullanilan_alg_etiketi": "ML-DSA-65",    // header label used for X
  "anahtar_yolu": "JWKS", "api_yolu": "jwt.PyJWS().decode_complete(..., algorithms=[...])",
  "sonuc_ham": "kabul",                     // kabul | red | istisna | zaman-asimi | cokme | uygulanamaz | ifade-edilemedi
  "karar": "accept-hybrid",                 // accept-classical | accept-hybrid | reject | indeterminate | uygulanamaz
  "hata_sinifi": null,                      // §3.2
  "hata_ozeti": null, "hata_sha256": null,  // first 200 characters + digest of the full text
  "dogrulanan_algoritmalar": [
    {"sira": 0, "alg": "ES256", "sonuc": "gecerli"},
    {"sira": 1, "alg": "ML-DSA-65", "sonuc": "gecerli"}
  ],                                        // sonuc: gecerli | gecersiz | denenmedi | bilinmiyor
  "pq_servis_cagrilari": 1,                 // TK2 only: from the log of the local PQ verification service
  "sure_ms": 14, "zaman_asimi": false,
  "stdout_sha256": "…", "stderr_sha256": "…"
}
```

(Values of `sonuc_ham`: `kabul` accept, `red` reject, `istisna` exception, `zaman-asimi` timeout, `cokme` crash, `uygulanamaz` not applicable, `ifade-edilemedi` could not be expressed. Values of `sonuc`: `gecerli` valid, `gecersiz` invalid, `denenmedi` not tried, `bilinmiyor` unknown. See `docs/DATA-DICTIONARY.md`.)

### 3.1 Mapping from observation to the four-valued decision

| Observation | Decision |
|---|---|
| The library accepted **and** it was shown that at least one PQ signature (ML-DSA or composite) was verified. Evidence: the result object of the library (RFC 7515 §5.2 step 10) or the TK2 service log | `accept-hybrid` |
| The library accepted and PQ verification could not be shown. Example: TK3 or an acceptance that relies only on the classical signature | `accept-classical` |
| The library rejected or threw a verification exception (with a class from §3.2) | `reject` |
| Timeout, crash or a result that is not the same in 3 repetitions (PR §6.11) | `indeterminate` |
| The target does not support this serialization with its documented API (B6) | `uygulanamaz` (not applicable; excluded from the comparison) |

**Distinguishing B6 from rejection:**
- B6 is determined **in advance, by API review**. Example: the target has no General JSON verification API → the General JSON vectors are not run and `uygulanamaz` is written.
- If the API exists, the vector is run. A parsing error is then a **rejection** (`hata_sinifi = ayristirma`).
- Under 8725bis §3.14, JWT libraries rejecting JSON input is B6, not a deviation.

### 3.2 Error classes (closed list)

`imza-gecersiz`, `alg-desteklenmiyor`, `alg-izin-disi`, `alg-anahtar-uyusmazligi`, `gerekli-kume-eksik`, `anahtar-bulunamadi`, `zincir-gecersiz`, `x5c-korumasiz`, `baslik-cakismasi`, `crit`, `typ`, `zaman`, `kb`, `sd_hash`, `ayristirma`, `istisna-diger`, `zaman-asimi`, `cokme`, `adaptor-hatasi`, `bicim-desteklenmiyor` (B6).

(English meanings in `docs/DATA-DICTIONARY.md`.)

- The mapping is made per target in `MAPPING.md` from the exception types of the library. An exception that cannot be mapped becomes `istisna-diger` (other exception) and a digest of the message is recorded.
- **"Wrong pre-hash" (CMP10):** a target that **accepts** CMP10 is written into the taxonomy class "wrong pre-hash implementer error" (PR §2D item 5).

## 4. Timeout, repetition, version pinning

- **Timeout:**
  - 60 s per vector (hard);
  - 30 min per target × run.
  - Exceeding it becomes `zaman-asimi` → `indeterminate`.
  - JVM/.NET warm-up is outside the measurement. The adapter processes all vectors in sequence in one process; the time is measured per vector.
- **Repetition:** 3 runs (r1–r3), each in a fresh container. A cell value is valid only if 3/3 are the same; otherwise "unstable" → indeterminate (PR §6.11).
- **Version pinning:**
  1. The target is pinned to the `son_commit_sha` of `CERCEVE.csv` at the time of the freeze (CRITERIA §7 item 6).
     - The environment work (interim record of 25.09) recorded that for many targets the release tag differs from this commit.
     - **cose-lib 4.8.2 has no ML-DSA source; HEAD has it.**
     - **Proposed rule:** since the TK assignment was made according to the API at the commit the inventory relies on, the measurement is made with the target built from that commit. The release version and its commit are recorded separately. The historical baseline (PR §6.12) goes back from the release versions. The decision lies with the maintainers (DECISION-NOTES N-7).
  2. The digest of the lock file, the image digest and the SHA-256 of the adapter code are written to every output row.
  3. The battery (v1.2, anchor 7) and the oracle (SHA-256 of `karar.tsv`) are checked with `sha256sum -c` before the first measurement. On a mismatch the measurement does not start (work plan Step 10.3).

## 5. L-level determination protocol (PR §4.13; L4m/L4c PR §2B item 6)

The L level is determined **in the control arm** (X = EdDSA, Ed25519 if needed; PR §3.7). The treatment arms are for F_T and the B flags. At every step API scanning, configuration attempts and battery verification go together.

### 5.0 Adapter validity gate (PR §4.15)

- **Rows:** `GEC` × {`VPLUS_ES256`, `VPLUS_EdDSA` | `VPLUS_EdDSA-ED25519`, `VMINUS_ES256`, `VMINUS_EdDSA` | …}. Oracle: V+ → accept, V− → reject.
- At most two correction attempts are made. A target that does not pass becomes **adapter invalid** (outside n_eff, with a justification).
- In the treatment arms `VPLUS_ML-DSA-65`/`VMINUS_ML-DSA-65` and `CMP00`/`CMP01` pass the same gate. This shows that TK1/TK2 works; if it does not pass, that arm falls to TK3 (§6).

### 5.1 API scan

- Documented options, type definitions and public exports are scanned. Example command: `rg -n "algorithms|allowlist|RegisterJws|register_algorithm|required|all|any" <source>`. The command and its output are written to `evidence/<target>/api-tarama.txt` (PR §4.14).
- For each L level the candidate mechanism is listed:
  - global allow-list,
  - per-call allow-list,
  - per-key/per-issuer binding,
  - required set or multi-signature rule.

### 5.2 Levels

| Level | Configuration and vectors | Success criterion (identical to the oracle) |
|---|---|---|
| **L1** | Global allow-list. `VPLUS_ES256` and `VPLUS_EdDSA` with `IZIN-A` (W={ES256}); then `IZIN-AX` | IZIN-A: VPLUS_EdDSA → reject, VPLUS_ES256 → accept-classical. IZIN-AX: both accept-classical. (In the treatment arms, additionally `UNK01–03` reject in every configuration.) |
| **L2** | Two calls on the same verifier instance: `IZIN-A` and `IZIN-AX` (per call) | The decisions of the two calls are the same as the IZIN-A and IZIN-AX rows of the oracle |
| **L3** | `IZIN-AX` + documented per-key/per-issuer alg binding. `K10K_alg-EdDSA_anahtar-ES256` [-ED25519], `K10K_alg-ES256_anahtar-Ed25519` and `VPLUS_*` | K10 (both directions) → reject; VPLUS_* → accept. **Additional condition:** it must be shown with API evidence that the rejection comes from the binding mechanism. A coincidental rejection arising from a key-type mismatch does not count as L3 (RFC 7515 §5.2 step 8 already produces a rejection) |
| **L4m** (the target supports General JSON multi-signature) | `L4` (R={X}, W={A,X}) with `T1K`, `T2K`, `T3`, `T5K` [fallback counterparts] | T1K accept-classical, T2K reject, T3 reject, T5K accept-classical. **Y_i = 1** |
| **L4c** (compact only) | Per-issuer policy on the same verifier instance: I_migrated (R={X}) and I_old (R=∅). Migrated: `VPLUS_ES256` → reject, `VPLUS_EdDSA` → accept-classical. Old: `VPLUS_ES256` → accept-classical (`IZIN-AX` row) | All three decisions the same as the oracle → **Y_i = 1**. The battery limit and the interpretation of "same instance" are in §5.3 |
| **L5** | Default configuration (only the key is given). The L3 and L4 vectors are run | L5 if the decisions are the same as the `IZIN-AX` rows for L3 and the `L4` rows for L4 |

- The L level of a target is the **highest** level reached with the documented API (PR §4.13).
- **Y_i:** L4m if the target supports multi-signature, L4c if it does not (PR §2B item 6). Which form was applied is written to `L-duzeyleri.csv`.
- **"Expressible with custom code":** the code and its line count are recorded as B4. The L level does not rise.

### 5.3 The "same verifier instance" condition of L4c and the battery limit

- In v1.2 there is no separate old-issuer identity: a single `iss` and a single ES256 issuer key.
- **Proposal (maintainers' decision; DECISION-NOTES N-2):** the adapter puts two issuer policy records into the same verifier instance. A policy record is bound to whatever the API uses to recognise the issuer: `iss`, `kid` or the key object.
  - VPLUS_ES256 must be reject when verified with the key of the "migrated" record.
  - It must be accept-classical when verified with the key of the "old" record (same ES256 key material, separate record).
- If the API recognises the issuer only by `iss`, the same bytes cannot be split into two records. In that case L4c is tested with two **consecutive** configurations over the same API mechanism and marked "L4c (consecutive)". This is a candidate deviation from the PR text.

### 5.4 Flags

- **B1** (unknown composite alg): K5 (`T7*`, secondary `T4*`, `T6`, `UNK04/05`). Recorded values:
  - "reject" if the same as the `L4-S` row;
  - "ignore" if the same as the `L4-Y` row;
  - "whole verification fails" if the whole verification fails with an exception.
  - If it is the same as none of them, an **MR2 violation**.
- **B2** (can a mixed-x5c policy be expressed?): `L4-YOL` × X5C03/04/05. B2 = 1 if the target can set up the path-class policy with its API and gives reject in all three.
- **B3** (is an unprotected x5c processed?): `L4` or `GEC` × X5C07/08/09. The oracle is reject in all three. B3 = 1 if the target accepts X5C07 or X5C08.
- **B4:** line count of the custom code (excluding blank lines and comments).
- **B5** (semantic class): the class is whichever of the oracle rows `P0` / `P1` / `L4-S` / `L4-Y` the T1/T2/T3/T7 decisions of the target's **default** configuration are the same as:
  - at-least-one-valid: P0 (T2 accept);
  - all-present-valid: P1 (T2 reject, T3 accept, T7 reject);
  - required-set: L4-S or L4-Y (T3 reject);
  - "other" if the same as none of them.
- **B6:** format support as in §3.1.
- **MR4:** the decision for a source vector and its permutation counterpart must be the same in every configuration (165/165 the same in the oracle). If it differs, a separate MR4 flag is written (PR §2B item 8). VP05-SIRA-ters is outside MR4.

### 5.5 Evidence rule for "not expressible" (PR §4.14)

The verdict "not expressible" is given only when these three conditions hold together:
1. no hook in the scan of §5.1 (command and output recorded);
2. two independent work attempts failed;
   - they are made in different sessions;
   - the second attempt sees only the target and this contract;
   - each attempt at most 45 min;
3. there is a line reference in the source code: repository + commit SHA + file + line range.

If a condition is missing, the result is **indeterminate**.

## 6. Treatment arm assignment: TK1 / TK2 / TK3 (PR §2B item 7; CRITERIA §5.5)

**Rule (separately per arm: ML-DSA-65 arm and composite arm):**
1. **TK1 native:** the documented public API at the pinned commit verifies the algorithm natively. Evidence: a row with a pinned commit in `destek_kanitlari.csv` or a documentation line.
   - The V± gate passes in that arm: `VPLUS_ML-DSA-65` / `VMINUS_ML-DSA-65` or `CMP00` / `CMP01`.
   - The runtime condition is met in a Linux container (e.g. PHP 8.4 + OpenSSL 3.5; .NET MLDsa).
2. **TK2 plug-in:** no native support, but a documented public extension point exists: algorithm registration, verifier callback or a Signer/Verifier interface. The local PQ verification service in `experiment/signer` can be plugged into this point without changing the library code.
   - **The policy layer stays the library's:** alg allow-list and multi-signature semantics. The plug-in only answers the question "is this signature valid with this key?".
   - The V± gate passes with the plug-in. The service log is written to the field `pq_servis_cagrilari`.
3. **TK3 unknown-alg:** none of the above. Only the unknown-alg behaviour is observed. In the oracle comparison, the target giving `accept-classical` in a cell where `accept-hybrid` is expected is a **PQ-specific failure**. T2 (McNemar) does not include TK3 targets; TK3 is reported descriptively.
4. **Priority:** TK1 > TK2 > TK3. If the plug-in requires changing the library code, it does not count as TK2.
5. **Freeze:** the assignment is made before the measurement; only with API review and the V± gate (not with behaviour measurement). Targets marked "to be reviewed" are assigned to TK2 or TK3 by API review while the adapter is written (SUMMARY P5). The result is written to `tk-atamasi.csv` with a justification row.

**Preliminary assignment (from the inventory; `SUMMARY.md` §2 and §3.2, `destek_kanitlari.csv`). Not binding; frozen with rule 5.**

| Target | ML-DSA-65 arm | composite arm | Basis and note |
|---|---|---|---|
| JOSE-009 panva/jose | TK1 | TK3 | `types.d.ts` L23–25 (ML-DSA-44/65/87); composite pattern 0 matches |
| JOSE-001 IdentityModel | TK1 | to be reviewed | MlDsaSecurityKey; composite 0 matches; .NET MLDsa environment |
| JOSE-083 pyjwt | TK2 | TK2 | `register_algorithm` (SUMMARY §3.2) |
| JOSE-055 jjwt | TK2 | TK2 | `parserBuilder().sig().add` |
| JOSE-034 jose2go | TK2 | TK2 | `RegisterJws` |
| JOSE-033 golang-jwt | to be reviewed | to be reviewed | binding left to the Keyfunc; registration mechanism by API review |
| JOSE-052 java-jwt, JOSE-002 JWT.NET, JOSE-071 lcobucci, JOSE-087 ruby-jwt, JOSE-089 json-jwt | to be reviewed | to be reviewed | SUMMARY §3.2 item 3 |
| JOSE-065 node-jsonwebtoken, JOSE-084 python-jose, JOSE-070 php-jwt, JOSE-092 jsonwebtoken, JOSE-091 frank_jwt, JOSE-104 Swift-JWT | TK3 | TK3 | ML-DSA and composite patterns 0 matches; no plug-in evidence (JOSE-065 noted "to be reviewed") |
| JOSE-102 jwt-kit | TK1 conditional, TK3 likely on Linux | TK3 | README L281 "MLDSA requires macOS 26+" |
| SDJWT-015 identity-common-ts | TK2 | TK2 | verifier callback; `allowedIssuerAlgorithms` |
| SDJWT-018 sd-jwt-python | TK1-indirect (jwcrypto) | to be reviewed | verification is delegated to jwcrypto; environment: jwcrypto 1.6.1, mldsa module present |
| SDJWT-010 sd-jwt-payload | TK2 candidate | TK2 candidate | `JwsSigner` trait (crypto-agnostic) |
| SDJWT-021 WalletFramework | TK3 | TK3 | ES256 hard-coded; delegates to IdentityModel (§7) |
| SDJWT-025 ssi, SDJWT-001 vck, SDJWT-004 authlete, SDJWT-002 affinidi | to be reviewed | to be reviewed | authlete: according to the environment record it leaves JWS signature verification to the caller (DECISION-NOTES N-8) |
| COSE-035 cose-lib | TK1 (HEAD only) | TK3 | no ML-DSA in 4.8.2; depends on version pinning (§4) |
| COSE-036 wolfCOSE | TK1 | TK3 | `WOLFCOSE_LEAN_VERIFY_MLDSA`; GPL-3.0 |
| COSE-034 go-cose | TK2 | TK2 | Signer/Verifier interface (README L270–322, HEAD) |
| COSE-001 Signum, COSE-014 cose-js | TK3 | TK3 | ML-DSA/composite 0 matches |

**Warning for the COSE stratum:** the v1.2 battery has no COSE vectors. All 153 vectors are in JWS/SD-JWT form (PR §2D item 8). Therefore the behavioural L level and F_K/F_T cannot be measured with the battery for the 5 COSE targets; all rows become B6. The decision lies with the maintainers (DECISION-NOTES **N-0**).

## 7. Delegation relations (D-E7; PR §2B item 9)

| Delegating target | Verification delegated to | Inside n? | Source |
|---|---|---|---|
| SDJWT-021 WalletFramework.SdJwtVc | JOSE-001 Microsoft IdentityModel (`JwtSecurityTokenHandler`) | **yes: delegation set** | SUMMARY §4 |
| SDJWT-001 vck | Signum `indispensable-josef/cosef` (same project as COSE-001) | candidate (environment 25.09) | note in `experiment/environments/derleme-sonuc.csv` |
| SDJWT-018 sd-jwt-python | jwcrypto | no (jwcrypto outside n) | SUMMARY §4 |
| REF-003 EUDI verifier | eudi-lib-jvm-sdjwt-kt + Nimbus | outside n (REF) | SUMMARY §2.4 |
| REF-011 Credo | SDJWT-015 identity-common-ts (`@openid4vc/*`) | REF outside n; target inside n | SUMMARY §4 |
| irmago (REF fallback) | jwx | outside n | SUMMARY §4 |

**Rules:**
- T1 and T2 are recomputed with the delegating targets removed (descriptive, outside Holm).
- The divergence detector also shows the delegation sets as a single unit (`divergence-detector.md` §4).
- If SDJWT-004 authlete leaves signature verification to the caller, the policy layer is not in the library. The L level of this target should be assessed by the API scan as "L0 (no signature policy)" or as out of scope (K1). The decision lies with the maintainers.

## 8. Rules of task 7a (PR §2D items 1–2, §2E item 3)

1. **Key path:** the verification key is given **in all arms** with the documented API of the target (JWK/JWKS or a direct key object). The **same path** is used across arms; the field `anahtar_yolu` is recorded in every row. For a target that uses different paths across arms, the control–treatment comparison is considered invalid.
2. **`x5c` only in the X5C vectors:** in X5C01–X5C10 the key is resolved with x5c and the trust anchors (`anahtarlar/v1/pki/root-ec.pem`, `root-ml.pem`). In the other vectors the key is given with the documented API even if the header contains x5c. If the target cannot ignore x5c, it is still correct, because the chains in the battery are valid. This behaviour is noted.
3. **Composite X.509 is out of scope:** composite objects are resolved with kid/JWKS and labelled "**HAIP §6.1.1 deviation**". K8 and K9 are run in the composite arm with X5C04/X5C07 with an ML-DSA-65 leaf (PR §2F item 4). In these rows the oracle instantiates the policy with X = ML-DSA-65.
4. **Control label:**
   - The primary label is `EdDSA`.
   - If the target does not support `EdDSA` but **documents** support for `Ed25519` (RFC 9864), the control arm is run with the `-ED25519` counterparts (arm = `kontrol-Ed25519`).
   - If it supports both, `EdDSA` is used.
   - The label used is written to the field `kontrol_etiketi` and to `tk-atamasi.csv`. A single-label allow-list rejects the other label (PR §2E item 3). Therefore the allow set W is always built with the label used. Using the fallback does not change the definition of Y_L4.
5. **Shared files:** `T3_stripped_to_ES256`, `VPLUS_ES256`, `VMINUS_ES256` and `VC10_ikili_ihrac` are re-evaluated in every arm with the arm's W/R. The oracle has a separate row for each arm.

## 9. Rule for the comparison with the oracle

1. **Unit of agreement:** (target, vector, policy, arm, cell stable in 3/3).
2. Excluded from the comparison:
   - cells where oracles A and B disagree → indeterminate (PR §4.15);
   - oracle `indeterminate` cells → reported but not counted as a deviation;
   - target `uygulanamaz` (B6) cells.
3. **Types of deviation:**
   - **decision deviation:** accept-* ↔ reject;
   - **acceptance without PQ verification:** oracle `accept-hybrid`, target `accept-classical`. In the L4 family this is a deviation, because R was not applied;
   - **harmless difference in acceptance type:** oracle `accept-classical`, target `accept-hybrid`. Example: the target verifying all signatures in a P0 row. Recorded, not counted as a deviation.
4. **F_K / F_T (PR §6.4):** 1 if, in the target's best reachable configuration (highest L with the API), there is a decision deviation or an acceptance without PQ verification in at least one of the K1–K3 primary vectors.
   - K: control arm; T: treatment arm. Composite is the main arm; the ML-DSA-65 secondary arm is reported separately.
   - The comparison is with the `L4` rows. The S or Y semantics of the target does not change K1–K3.
5. **Primary outcome variables** (the battery part of Y_L4, F_K, F_T, D_soy, B1–B6) are computed only from rows with `sinif = birincil` (PR §2G item 4). Secondary rows are descriptive.
