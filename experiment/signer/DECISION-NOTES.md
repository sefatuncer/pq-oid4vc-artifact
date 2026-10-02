# Step 9b → notes to the maintainers (signer + generator + PQ primitive verification service)

**Date:** 24.09.2026 · **Written by:** the signer work · **Scope:** our own tools only; NO target library measurement.
Evidence: `experiment/signer/sonuclar/` (T01–T05), `experiment/vector-generator/sonuclar/` (T10), `experiment/vector-generator/vektorler/v1/MANIFEST.json`.

(Quotations from the pre-registration (PR) are translated from Turkish.)

## A. Findings with a direct effect on the plan / the pre-registration

| # | Finding | Evidence | Proposed effect |
|---|---|---|---|
| A1 | **The composite arm cannot carry an `x5c` conforming to HAIP.** HAIP 1.0 §6.1.1 makes `x5c` mandatory for SD-JWT VC; composite X.509 (LAMPS -19) is not available in OpenSSL 3.5.7 or cryptography 50.0.1. In v1, composite-signed SD-JWT VC / TSL / request objects are resolved via `kid` (JWKS, similar to JWT VC Issuer Metadata) | README §7; VC03/VC06/VC08, TSL03, REQ03 | The pre-registration must state explicitly the key resolution path for the main TK arm (composite -04): **(i)** `kid`/JWKS (labelled as a HAIP deviation) or **(ii)** production of LAMPS composite certificates. (ii) is technically possible: the `M'` structure of LAMPS -19 is identical to JOSE -04 (empty ctx), and Appendix E has test vectors; our own DER builder + a minimal path validator ≈ 6–10 working hours (estimate). But composite X.509 support in the targets is unlikely → this cell will most likely come out "not supported" |
| A2 | **Composite -04 is not backward compatible and has a single `alg`**: a classical-only verifier cannot use either component; the ECDSA component cannot be reused as ES256 (Prefix/Label, signature over M') — weak non-separability works | T03 N5-separability (3/3 rejected); CMP12/CMP13 | In a mixed verifier population the transition is possible only with multi-signature (scenario d) or double issuance (b); (a) means a "flag day". This should be stated in the H1/H2 narrative and in the scenario definition |
| A3 | **Ambiguity of RFC 9901 §8.1:** in General JSON, `sd_hash` is over "the signature"; with multiple signatures it is undefined which signature that is. This tool uses the first signature → the KB-JWT binds only the first signature; **the KB-JWT stays valid even if the PQ signature is stripped** | VP05/VP06/VP07; T10 sd_hash checks | A new sub-cell for scenario (d) and H5 (aggregate-and-forge): "the KB binding does not protect the multi-signature set". Candidate for specification feedback (outward-facing → ask the user) |
| A4 | **AND alone does not catch stripping; L4 is required.** In our verifier too, P0 (any-valid) and P1 without an expected set (AND) ACCEPT the stripped object; only `required_algs` (L4) rejects it | T03 control information (6/6 ACCEPTED); N6 stripping (7/7 rejected; N6 total 16/16 rejected) | Consistent with the pilot classification; a direct input to the derivation of the L4 oracle (decision of adim-01) |
| A5 | **Pre-hash ambiguity (-04):** for ML-DSA-65-ES256 the pre-hash in Table 5 is SHA-512 and the Label "…-SHA512"; yet the IANA description of §7.1.2 and the description column of Table 5 say "…P-256 curve and SHA-256" (the ECDSA component's own hash). An implementer using a SHA-256 pre-hash cannot interoperate | CMP10 (consistent signature with a wrong pre-hash) | To be recorded in C3 as an implementer-error class; candidate for WG feedback (outward-facing → ask) |
| A6 | **The DPoP size threshold depends on the claim set.** P4 said "ML-DSA-65 DPoP ≈ 8,192 B (10 B above nginx's 8,182)". We get 8,128 B with the minimal claims (54 B **below**), 8,244 B with `ath`+`nonce` (**above**); ML-DSA-65-ES256 is above in every case (8,355 / 8,472 B); ML-DSA-87 11,023 B; ML-DSA-44 5,805 B (below) | `vector-generator/sonuclar/v1_boyutlar.csv`; DPOP01–09 | The deployment constraint table must be reported **together with the claim set** (token request vs. resource access with `ath`). The phrase "10 B above" in §7.17 should be made conditional |
| A7 | **The P4 sizes were reproduced exactly** (OpenSSL 3.5.7, pilot: 3.5.6): ML-DSA-44/65/87 SPKI, signature, CA/leaf certificate and x5c character count equal; EC ±2 B | T04 29/29 | The P4 measurements were verified with an independent tool (evidence for the ✓ label) |
| A8 | The composite signature length is **variable** (DER ECDSA): ML-DSA-65-ES256 3379–3381 B | T04, T01 | The upper bound (3381 B) should be used in threshold calculations |
| A9 | **Alg label of the control arm:** RFC 9864 deprecates the polymorphic `EdDSA`; `Ed25519` is the fully specified name. The v1 control arm uses `EdDSA` for compatibility with the pilot; the library also supports `Ed25519` | params.py; T02 | The label of the control arm should be fixed in the pre-registration (`EdDSA` recommended: pilot compatibility + wide support); if wanted, extra control vectors labelled `Ed25519` can be produced (a one-line change) |
| A10 | **Mixed chains count as valid without a chain policy** (OpenSSL path validation does not look at the algorithm class); an unprotected `x5c` allows lowering the chain class without breaking the signature | T03 N8 control information; X5C03–05, X5C08 | Measuring the flags "mixed x5c" and "unprotected x5c" is meaningful; linked to the `X_alt_ca` cell in the ASP model (adim-04) |
| A11 | **`crit` as an M-f carrier is fail-closed**: RFC 7515 §4.1.11 requires rejecting a crit that is not understood → an M-f marker in the credential header breaks old verifiers | CRIT01, T03 N7 | Carrying M-f in the TL/LoTE (the plan) is right; a header carrier only as an ablation variant |
| A12 | **The -13 / -19 difference in the data format is very small:** both use `dc+sd-jwt`; the difference is the status of the JSON serialization (optional in -13, out of scope in -19) and the `vc+sd-jwt` transition (-13 only) | generator README §4 | In practice the parameter `sdjwtvc_surum` affects the scenario (d) vectors and VC11; the pre-registration should define it so |

## B. Tool-level facts (acceptance)

- Draft test vectors **exist and passed**: composite -04 Appendix A.1 (6 JOSE) + RFC 9964 Appendix A (3 JOSE + 3 raw COSE) → T01 156/156. The RFC 9964 JWSs were reproduced byte for byte by our generator; the ML-DSA component of the draft is deterministic, the ECDSA component uses a random k (byte-identical production was possible, and achieved, only for the composites with EdDSA).
- OpenSSL cross-verification in both directions 44/44; independent pure-Python FIPS 204 (dilithium-py) 18/18.
- Negative tests: 84/84 rejected (corrupted signature, wrong alg label, the ML-DSA and the ECDSA component of the composite separately, stripped multi-signature, crit, x5c, format).
- Test vector set v1: 93 vectors (T 14, UNK 5, CMP 17, X5C 10, REQ 10, VC 12, VP 7, TSL 3, DPOP 10, CRIT 5); deterministic, regeneration byte-identical; **contains no oracle decision**. Identity: `vektorler/v1/MANIFEST.json` SHA-256 `a4b559ed…8891`, `vektorler/v1/SHA256SUMS` `90b28b2a…e197`, `anahtarlar/v1/SHA256SUMS` `c941feb5…fc1a` → can be frozen in the pre-registration.
- **L5** is not a vector property (it is measured by running the L3/L4 vectors with the default configuration); **L0** separates out as the "no constraint" state on the L1-labelled vectors.
- The **PQ primitive verification service** for the TK2 "plug-in" is ready (`servis/`; HTTP on the internal network/127.0.0.1 only + CLI): same result as the library on t01 69/69 and t02 45/45 (T05 121/121). Note: because of the HTTP latency the service must not be used for **timing** measurements.
- Versions: base `python:3.11-slim@sha256:9534e5a8…4534` (Debian 13), system OpenSSL 3.5.7, cryptography 50.0.1 (bundled OpenSSL **4.0.2**, 25 Aug 2026), dilithium-py 1.4.0. Images: `pq-a09-signer:1.0` = `beeb05a70a97`, `pq-a09-credgen:1.0` = `55ac321117b7`.

## C. Notes on validity threats

- The ML-DSA signatures were produced with the deterministic variant (reproducibility); real deployments are hedged. No effect on verification behaviour; one line for §7.18.
- The library and the cross-verifier come from the same OpenSSL code family (4.0.2 vs 3.5.7); therefore dilithium-py and the draft/RFC vectors (from other implementations) were used in addition.
- The vectors are at JOSE/SD-JWT level; COSE/mdoc, JWE, wallet/key attestation are not in v1.

## D. Process note (transparency)

- I ran `docker image prune -f` once (a mistake). It deletes only **untagged** images; the list I recorded at the start (`kayit/docker_images_once_2026-09-24.txt`) had no untagged image, and **all previously existing tagged images are in place**; the running `pq-a03`/`pq-a04` containers were not affected. Still, untagged old layers left from rebuilds of other work may have been deleted in the meantime (1.27 GB reclaimed in total). Afterwards I removed only my own images, by name/id. My remaining resources: `pq-a09-signer:1.0`, `pq-a09-credgen:1.0` (tagged, not deleted); no containers or networks.
- No outward-facing action was taken; packages only from PyPI (pinned by digest), the base image is the official one from Docker Hub.

## E. Open items / recommendations

1. The A1 decision (key resolution path for composite) must be taken before the pre-registration; if wanted, I can add LAMPS composite X.509 (verified with the Appendix E vectors) as v1.1.
2. A3 and A5 are candidates for specification feedback — outward-facing, so the user decides.
3. For the N-version oracle generation the fields `insa`, `dayanak`, `dogrulama_girdileri` of the MANIFEST are sufficient; two independent works can work from the same MANIFEST.

(E.1 closed: maintainers' decision A1 — LAMPS composite X.509 will not be done for now; see F.)

## F. v1.1 (maintainers' decisions A9, A1, A6 — 24.09.2026)

**Done.** `experiment/vector-generator/vektorler/v1.1/` was produced: the 93 vectors of v1 byte-identical (files, `b-uyumlu/vectors.json` and manifest entries) + the `alg = "Ed25519"`-labelled twin of the **7** v1 vectors with `kol = kontrol-EdDSA`: `T1K_both_valid-ED25519`, `T2K_second_tampered-ED25519`, `T4K_plus_ML-DSA-65-ED25519`, `T5K_only_EdDSA-ED25519`, `T6_plus_composite-ED25519`, `VC09_GJ_ES256_EdDSA-ED25519`, `DPOP02_EdDSA-ED25519`. Same key, same payload, same structure; only the `alg` in the protected header of the EdDSA-labelled signature and that signature differ (guard inside the generator + T10-E). Manifest: `kol = "kontrol-Ed25519"`; `dayanak` = `RFC9864 §2.2 (Tablo 2: Ed25519)`, `§4.1.1 (JOSE kaydı: Ed25519; "Reference: Section 2.2 of RFC 9864")`, `§4.1.2 (EdDSA: Deprecated)` — all three verified by reading `spec-corpus/metin/RFC9864.txt`.

**v1 was not touched.** During production and testing `vektorler/v1` and `anahtarlar/v1` were mounted **read-only** into the container. The tree digests (SHA-256 of the SHA-256 list of all files) are the same before and after: `vektorler/v1` `6b2ac52b…8dcb`, `anahtarlar/v1` `d149c25d…3c96`. No new keys; `anahtarlar/v1` was used as is. Before v1.1, the generator regenerates v1 from scratch in a temporary folder and compares it with the frozen v1 (it stops on any difference).

**Identity (C3 battery anchors):**

| File | SHA-256 |
|---|---|
| `vektorler/v1.1/MANIFEST.json` | `e37ee97e4087829d94ce63109e1466c0cdb8d23c3eab25a84bcf7fee8181e102` |
| `vektorler/v1.1/SHA256SUMS` | `8f4466f2ea13cd84f9a646ca801e89e7ba3a950b4e60d56db215e1962333a40c` |
| `anahtarlar/v1/SHA256SUMS` (keys used) | `c941feb5ee70de6adbd2f3f9468ae8f9a2d265897db232c34d4dfda8f7ccfc1a` |

**Verification.** T10 v1.1 **549/549** (`experiment/vector-generator/sonuclar/t10_oz_dogrulama_v1.1.*`); T10 v1 still 471/471. Regeneration of v1.1 byte-identical at the level of `MANIFEST.json` and `SHA256SUMS`. The Ed25519 signatures of the twins were cross-verified with the OpenSSL CLI (6 valid; in the T2K twin the 1 signature that is corrupted by design is invalid). `pqjose` accepts the `Ed25519` label (T twins, VC09 twin, DPoP twin).

**New observation (input to the measurement design).** Allow-lists are **label-sensitive**: in `pqjose`, with only `EdDSA` in the allow-list an `Ed25519`-labelled signature, and with only `Ed25519` the `EdDSA`-labelled signature of v1, is rejected with `alg-izinli-degil` (alg not allowed). The same behaviour is likely in the targets → the label used under the fallback rule must be recorded per target (consistent with A9).

**A6 size table.** `experiment/vector-generator/sonuclar/v1.1_dpop_boyutlari.{csv,json}` (`uretec/boyut_dpop.py`; a report table, the vector set does not change): 12 algs × {minimal, +ath, +ath+nonce}, with the signature upper bound for composite (ML-DSA-65-ES256 3381 B, ML-DSA-44-ES256 2492 B, ML-DSA-87-ES384 4731 B). **ML-DSA-65: minimal 8,128 B (54 B below nginx's 8,182), +ath 8,198 B (16 B above), +ath+nonce 8,244 B.** The value "≈8,192 B, 10 B above" of P4 corresponds to the +ath set. ML-DSA-65-ES256 (upper bound) 8,356 / 8,426 / 8,472 B; ML-DSA-87 ≥ 11,023 B; ML-DSA-44 ≤ 5,921 B; the Node threshold (16,348 B) is exceeded by none.

**READMEs.** `experiment/vector-generator/README.md` §5b (v1.1, fallback rule, texts of A1 and A6, digests, production commands) and §6 (DPoP table with claim sets) were added; the status rows of `experiment/signer/README.md` were updated.

**Resources/process.** Only `--rm` containers named `pq-a09-*` were used; no `prune` or bulk deletion; my own 1.1 image that became untagged after a Dockerfile comment fix had already been cleaned up ("No such image"). Images: `pq-a09-credgen:1.1` = `bd96803a15cd` (FROM `pq-a09-signer:1.0` = `beeb05a70a97`), `pq-a09-credgen:1.0` = `55ac321117b7` (the one that produced v1; kept). No git was used; no outward-facing action.

## G. v1.2 (gaps found by the PR §6.5 mapping audit — 24–25.09.2026)

**Done.** `experiment/vector-generator/vektorler/v1.2/` = the 100 vectors of v1.1 **byte-identical** (files, `b-uyumlu/vectors.json`, manifest entries) + **53 new vectors** (153 in total; 157 files):
- **MR4** (PR §2B item 8, §2C item 4): 24 permutations + 9 Ed25519 twins. Two-signature objects (T1K/P/C, T2K/P/C, VC07/08/09, REQ04) reversed; three-signature objects (T4K/P/C, T6) `ek-once` and `ters`; in addition to the PR list, T7K/P/C (`kayitsiz-once`, `ters`). Every (protected header, signature) pair and the payload byte-identical; in SD-JWT VC `disclosures` in the new first unprotected header (RFC 9901 §8.3; `insa.mr4`).
- **Outside MR4, descriptive:** `VP05_GJ_ES256_MLDSA65_kb-SIRA-ters` — the KB-JWT is unchanged, `sd_hash` now binds the signature in position 2 (ES256).
- **K5:** `T7K/T7P/T7C_plus_kayitsiz` (+1 twin) = T1* + a third signature labelled `alg:"X-KAYITSIZ-1"` with 128 B of HKDF-deterministic random bytes. In the mapping the primary vector of K5 is T7*, the secondary ones T4*/T6 (and UNK04/UNK05 in the ML-DSA arm).
- **K10:** two directions per arm (6 + 1 twin); the signature is a valid signature produced with the real key's own algorithm, not with the header alg (`insa.k10`); the key via `dogrulama_girdileri.jwk` (+ `acik-jwks.json`/`kid`), in line with PR §2D item 1.
- **V+ / V−:** `VPLUS_`/`VMINUS_{ES256, EdDSA, ML-DSA-65}` (6 + 2 twins); CMP00 / CMP01 were reused for composite.
- **Ed25519 twins** (PR §2D item 2): for every new control vector that carries an EdDSA label (13 in total). Exception: `K10K_alg-ES256_anahtar-Ed25519` carries no EdDSA label; its twin would be byte-identical, so it was not produced.
- **`experiment/vector-generator/BATARYA-ESLEME.md`** (`uretec/esleme.py`): K1–K11, V+, V−, MR1–MR4 × control / ML-DSA-65 / composite; primary and secondary ids; the PR §6.5 decisions and the definitions of MR1–MR3 (§4.20) and MR4 (§2B item 8) quoted verbatim **by parsing the PR text**. 107 ids; no new v1.2 id is missing from the mapping.

**Honesty notes (also written in the mapping):**
- **K8 adapted (D-S1):** instead of "composite leaf, classical intermediate CA", an ML-DSA-65 leaf + classical intermediate CA (`X5C04`); composite X.509 is out of scope, "deviation from HAIP §6.1.1". K9 also with an ML-DSA-65 leaf (`X5C07`).
- **Cells that do not apply:** K6/K7 are defined only in the composite arm; K8/K9 are arm-independent flags (chains only in the X5C vectors, with classical and ML-DSA chains; no EdDSA certificate chain in the control arm).
- **K3** is one file common to the three arms (`T3_stripped_to_ES256`); the difference is only in the policy (R = {X}).
- **K11:** the PQ copy in `VC10` is ML-DSA-65; since the K11 decision rests only on the classical copy, no PQ copy is needed in the control and composite arms.
- **MR1** T1 ↔ T3 (+ VP05 ↔ VP06 descriptive in ML-DSA, REQ04 ↔ REQ05 scenario c); **MR2** T1 ↔ T7 primary, T1 ↔ T4 (T1 ↔ T6 in control) secondary; **MR3** VC07/08/09 (same file, -13 ↔ -19) and VC01 ↔ VC11.
- REQ04 and its permutation are scenario (c), wallet side (work plan Step 11).

**Verification.**
- T10 v1.2 **944/944** (`experiment/vector-generator/sonuclar/t10_oz_dogrulama_v1.2.*`); v1 471/471 and v1.1 549/549 unchanged. New checks (F): v1.1 ⊂ v1.2 byte-identical (100/100); in the MR4 twins the signature content and validities carried over exactly by the permutation; in the SD-JWT twins the `pqjose` result equals the source; in the VP05 twin `sd_hash` binds the 2nd signature; T7 structure; K10 signatures valid with the real key and **cross-verified with the OpenSSL CLI**, REJECT with `pqjose` L3; V± as expected with `pqjose` and OpenSSL; the new Ed25519 twins differ only in label/signature and are verified with OpenSSL.
- **Independent reproduction (25.09):** with the project folder fully read-only, production into a temporary folder with `pq-a09-credgen:1.2` → `diff -r` **no difference (157 files)**; `BATARYA-ESLEME.md` and `sonuclar/v1.2_boyutlar.csv` byte-identical. The v1.2 files were produced from inside the image (image 20:14:47, manifest 20:14:52).
- **Independent audit of the mapping** `experiment/vector-generator/testler/t11_esleme_denetim.py` (a parser separate from the generator; `sonuclar/t11_esleme_denetim.txt`): **293/293** — PR §6.5 content and decision quotes verbatim, every arm cell filled or with a justified "—", K8 with the D-S1 reference, MR1–MR4 definitions verbatim, all ids in the manifest.
- Frozen folders: `vektorler/v1`, `vektorler/v1.1`, `anahtarlar/v1` read-only during production and tests; tree digests before = after (`6b2ac52b…8dcb`, `6f4456cd…79e1`, `d149c25d…3c96`).

**Identity (for anchor 6):**

| File | SHA-256 |
|---|---|
| `experiment/vector-generator/vektorler/v1.2/MANIFEST.json` | `bb17aaa76a3d1859b2dd5df54c62e7039948a715e2c4b4628fed82d184c6e738` |
| `experiment/vector-generator/vektorler/v1.2/SHA256SUMS` | `92663b48f477f51e5a4cdd2a6942d97d36b2d9591fa67af451fd33eb14f0b2a3` |
| `experiment/vector-generator/anahtarlar/v1/SHA256SUMS` (unchanged; no new keys) | `c941feb5ee70de6adbd2f3f9468ae8f9a2d265897db232c34d4dfda8f7ccfc1a` |
| `experiment/vector-generator/BATARYA-ESLEME.md` | `d73352179cdf281825d498000b7f9dc6d1df0fe835c8258c6aa2c516e659e3fc` |

**Note for the anchor (circularity).** The header of `BATARYA-ESLEME.md` contains the digest of the pre-registration file it quotes (`c239d423…8b6e`, version of 24.09 19:57). When Amendment 6 is added to the pre-registration, the digest of the PR file changes. If the mapping is regenerated, its header changes and so does the digest of the mapping. Recommendation: in the anchor, pin this file in the form produced against the `c239d423…` version. If Amendment 6 only adds text and does not change §6.5/§4.20/§2B, it can be shown that the quotes are still verbatim by re-running T11 against the new PR text (T11 does not look at the header digest; it checks the line quotes).

**Tool observations (not a target measurement):**
- In the control arm of K10 the header alg and the real signature have the same length (ES256 and EdDSA 64 B). A verifier that branches on the key type and ignores the alg accepts it; it is therefore a sharp test of L3. In the ML-DSA and composite arms the lengths differ (e.g. `alg=ES256` + a 3309 B ML-DSA signature). In these arms the rejection may come early from a length check; keep this distinction in mind when reporting reason codes.
- Under the AND semantics of `pqjose` the third signature of T7 is dropped with `alg-bilinmiyor` (alg unknown; fail-closed); with any-valid, ACCEPTED in all three arms.

**Images and process.**
- `pq-a09-credgen:1.2` = `5984112f66f6` (FROM `pq-a09-signer:1.0` = `beeb05a70a97`). 1.0 (`55ac321117b7`) and 1.1 (`bd96803a15cd`) kept. The production code of v1 and v1.1 did not change; 1.2 only adds `uretec/v12.py`, `uretec/esleme.py` and the T10 extension.
- The session limit interrupted at ~20:14 on 24.09. The last command had completed; on 25.09 it was verified with the independent reproduction above, T10 and T11.
- Only `--rm` containers named `pq-a09-*` were used. No `prune` or bulk deletion, no git, no outward-facing action. No container was left behind.

## H. v1.3 (Oracle A N-0 and N-2: COSE battery and L4c "old issuer" — 26.09.2026)

**Done.** `experiment/vector-generator/vektorler/v1.3/` = the 153 vectors of v1.2 **byte-identical** (files, `b-uyumlu/vectors.json`, manifest entries) + **47 new vectors** (200 in total; 204 files). Economy: no family outside the brief was added.
- **COSE (45; RFC 9052).** `uretec/cbor.py` (deterministic CBOR, RFC 8949 §4.2.1) and `uretec/cose.py` (COSE_Sign tag 98 / COSE_Sign1 tag 18, Sig_structure, COSE_Key, parser). Algorithm identifiers verbatim from the corpus, with line numbers (`cose.KAYNAK`; manifest `cose_kimlik_kaynaklari`; no guessing): ES256 −7 (RFC9053:248), EdDSA −8 (RFC9053:365), Ed25519 −19 (RFC9864:225, 439), ML-DSA-65 −49 (RFC9964:367), ML-DSA-65-ES256 −55 (JOSECOMP:1268 "TBD (request assignment -55)" → in the manifest "requested, NOT REGISTERED").
  - In every arm (EdDSA / ML-DSA-65 / composite): K1 (COSE_Sign ES256 + X), K2 (X corrupted), K4 (X only), K5 (+ unregistered tstr alg `X-KAYITSIZ-1`, 128 B of HKDF bytes), K10 (two directions, COSE_Sign1), V+/V− (COSE_Sign1), MR4 (signer order of K1 and K2 reversed). K3 is a single file common to the three arms.
  - Composite only: K6 (valid COSE_Sign1), K7 (ML-DSA and ECDSA component corrupted separately).
  - Arm-independent: K8 (protected x5chain = ML-DSA-65 leaf + classical intermediate CA; D-S1 adaptation), K9 (unprotected x5chain, all-PQ).
  - The Ed25519 (−19) twins of the 9 control-arm vectors that carry the EdDSA (−8) label.
- **L4c (2).** A separately identified old issuer: `iss = https://legacy-issuer.example`, key `issuer-eski/ES256` (derivation label `v1.3/issuer-eski/ES256`, kid `GGKBh_lEw5eKZr0XX6kbRRp8H1HYW6hwLhLBagC8MHw`). `L4C-JOSE_eski_ES256` (compact) and `L4C-COSE_eski_ES256` (COSE_Sign1), ES256 only. The "X only" and "ES256 only" counterparts of the migrated issuer are existing vectors (they would be byte-identical if regenerated): JOSE `VPLUS_ML-DSA-65` / `CMP00` / `VPLUS_ES256`, COSE `COSE-VPLUS_ML-DSA-65` / `COSE-K6` / `COSE-VPLUS_ES256`. No decision in the vectors; only `insa.ihracci` (iss, kid, derivation label).
- **`anahtarlar/v1.3/`**: the only new key (old issuer), `acik-jwks-l4c.json` (the 3 migrated keys + the old one; `ihraccilar`: iss → kid), `cose-anahtarlar.json` (public COSE_Keys of 5 roles; EC2 / OKP / AKP), `roller.json`, `SHA256SUMS`. `anahtarlar/v1/` unchanged.
- **`BATARYA-ESLEME.md` v1.3**: §3 COSE (K1–K11, V±, MR1–MR4 × 3 arms; primary/secondary PR §2G item 4), §4 L4c (ML-DSA-65 and composite × 3 rows; basis the L4c sentence of PR §2B item 6 and §6.5 K4, quoted by parsing), quotes of PR §2H items 9, 10, 12. 154 ids; no new v1.3 id is missing from the mapping. Copy of the v1.2 mapping: `experiment/vector-generator/sonuclar/BATARYA-ESLEME_v1.2.md` (`d7335217…`, anchor 7).

**Verification.**
- **T12** (`experiment/vector-generator/testler/t12_cose.py`; `sonuclar/t12_cose.*`) **138/138**: corpus lines of 40 identifiers; RFC 9964 Appendix A.2 COSE (ML-DSA-44/65/87): byte-identical re-encoding of the COSE_Key, AKP COSE thumbprint = kid, Sig_structure = `raw_to_be_signed`, verification with `pqjose` + dilithium-py, **COSE_Sign1 byte-identical with deterministic re-signing**; -04 Appendix A.2 COSE (6 composites): M′ identical with our encoding, the composite and its components (OpenSSL CLI, dilithium-py) valid, our signature byte-identical in the examples with EdDSA.
- **T10 v1.3** **1440/1440** (`sonuclar/t10_oz_dogrulama_v1.3.*`; new section G `testler/t10_cose.py`): v1.2 ⊂ v1.3 byte-identical (153/153), anchors, `MANIFEST.json/.csv`, `SHA256SUMS` and `anahtarlar/v1.3/SHA256SUMS` byte-identical on regeneration; every COSE signature consistent with the construction claim **via three paths** (`pqjose`, OpenSSL CLI, dilithium-py for ML-DSA); composite component states; byte relations K2/K3/K4/K5/V−/K7; x5chain position and OpenSSL chain verification; K10; MR4; Ed25519 twins; the L4c vectors valid with the old key and invalid with the ES256 key of the migrated issuer. v1 471/471, v1.1 549/549, v1.2 944/944 unchanged.
- **T11** v1.3 mapping **592/592** (`sonuclar/t11_esleme_denetim_v1.3.txt`): all v1.2 checks for the JOSE part (with the §2H item 9 adaptation of K8/K9), the COSE table (quotes, cells, ids belonging to COSE and to the arm), L4c (quotes verbatim; `iss` values from the vector files), §2H quotes. The v1.2 mapping against the current PR still **293/293**.
- **Independent reproduction:** with `experiment/vector-generator` fully read-only, production into a temporary folder with `pq-a09-credgen:1.3` → `diff -r` **no difference** (`vektorler/v1.3` 204 files, `anahtarlar/v1.3` 6 files); `BATARYA-ESLEME.md` and `sonuclar/v1.3_boyutlar.csv` byte-identical. The official outputs were produced from inside the image (without mounting the code).
- Frozen folders (`vektorler/v1`, `v1.1`, `v1.2`, `anahtarlar/v1`) read-only during production and tests; tree digests before = after (`6b2ac52b…8dcb`, `6f4456cd…79e1`, `210c9ec7…af4b`, `d149c25d…3c96`).

**Identity (for the v1.3 anchor):**

| File | SHA-256 |
|---|---|
| `experiment/vector-generator/vektorler/v1.3/MANIFEST.json` | `a81424470cf2b773c346795aa1b1880aecd841b77254ebb0c077432bc3c5390a` |
| `experiment/vector-generator/vektorler/v1.3/SHA256SUMS` | `a5b678d60ff474f1991168a694f52acb6d1c8a42b9648b4e8e63913042768812` |
| `experiment/vector-generator/anahtarlar/v1/SHA256SUMS` (unchanged) | `c941feb5ee70de6adbd2f3f9468ae8f9a2d265897db232c34d4dfda8f7ccfc1a` |
| `experiment/vector-generator/anahtarlar/v1.3/SHA256SUMS` | `5d0ccf6bc8cf5de3061ecab1a6c55f8d1165fe10235f366ecd4807b830bb160c` |
| `experiment/vector-generator/BATARYA-ESLEME.md` | `6795ee65f5161b4db90942f7058924061273e5d1eb1546dce444cabb2c7cb982` |
| (quoted) `00-on-kayit/ON-KAYIT-TASLAK.md` | `87932cf00b74063066386b1ade066720c4ac645df3f1e75d895ab9bbc43e3f47` |

**Points that need your decision, and honesty notes.**
1. **The only change in the JOSE mapping (K8/K9).** Since PR §2H item 9 says "It is not a result of the composite arm", the composite cell of K8/K9 is now "—" (in v1.2 `X5C04`/`X5C07` were primary with the ADAPTED note); the ADAPTED/D-S1 note moved to the ML-DSA-65 cell. I did this because §2H takes precedence over §2A–§2G; if you do not want it, these two cells can be reverted; the vectors are not affected.
2. **Targets limited to COSE_Sign1.** K1, K2, K5 and MR4 need COSE_Sign. For a COSE target that does not support multi-signature, Y_i = L4c (§2B item 6). How K1–K5 are counted for these targets (not applicable, or "unknown structure") needs a PR decision; the mapping does not decide. COSE_Sign1 counterparts of K3/K4 were added only as **secondary**.
3. **ES256 = −7 is "Deprecated".** RFC 9864 §4.2.2 deprecates COSE −7 and −8; HAIP §7 says "COSE algorithm identifier -7 or -9, as applicable" (HAIP:498). Because the brief said ES256, only −7 was produced; there is no ESP256 (−9) twin. If a COSE target rejects −7 and accepts −9, an ES256→ESP256 counterpart of the EdDSA→Ed25519 fallback rule (§2D item 2) is needed; it is cheap (only the label and the signature of signer A), but it is not defined in the PR.
4. **Composite −55 is not registered.** The targets will most likely not recognise this value; the observed behaviour is the unknown-alg behaviour (last sentence of §6.5).
5. **K11 and MR3 do not apply to COSE** (justified in the mapping): K11 depends on the OID4VCI batch response (SD-JWT VC), its signature-level counterpart is L4c-2; MR3 is the SD-JWT VC -13/-19 dimension.
6. **No L4c control arm was produced** (brief: treatment arms; L4c is a "PQ/composite mandatory" policy). If needed, it can be set up without new vectors (note under §4 of the mapping).
7. **The -04 Appendix A.2 COSE ML-DSA-87-ES384 example is internally inconsistent (erratum candidate).** The SHA-512 of the shown Sig_structure does not match the PH inside the shown M′; alg −70…−1, the kids of the six examples, no kid, canonical/insertion order, SHA-512/SHAKE256-64/SHA3-512 were tried, none matched. The components are valid over the shown M′; its JOSE Appendix A.1 twin is valid in T01; with the same key and header our signature is internally consistent. The other 5 composite COSE examples were verified exactly. Notifying the JOSE WG is an outward-facing action; it was not done (user's decision).
8. **COSE `kid`.** The 32 base64url-decoded bytes of the JWK `kid` (RFC 7638 thumbprint) (bstr). For targets that expect a text kid, the key path is the COSE_Key or a direct key (§2D item 1); the COSE_Keys are in `anahtarlar/v1.3/cose-anahtarlar.json` and in the field `dogrulama_girdileri.cose_key_hex` of every vector.
9. **Scope.** The COSE vectors are generic COSE (the payload is a CBOR map); they are not mdoc MSO/DeviceResponse (ISO 18013-5 out of scope).
10. **Circularity (the note in G applies).** The PR changed twice during this work (`dcc84092…` → `89648731…` → `87932cf0…`). The mapping header quotes the latest version; if the PR changes again, the mapping digest also changes. T11 does not look at the header digest; it checks the quotes against the current PR.

**Tool observations (not a target measurement).** The COSE vectors are 51–74 % of their JOSE counterparts: `COSE-VPLUS_ES256` 174 B (JOSE 341), `COSE-VPLUS_ML-DSA-65` 3,421 B (4,672), composite `COSE-K6` 3,491 B (`CMP00` 4,775), `COSE-K8` 6,295 B (`X5C04` 11,540), `COSE-K9` 14,659 B (`X5C07` 21,564). In K7 the corruption of the ECDSA component keeps the DER structure (last byte of r); the rejection must come from the signature verification, not from parsing.

**Images and process.**
- `pq-a09-credgen:1.3` = `492b326d64fc` (FROM `pq-a09-signer:1.0` = `beeb05a70a97`). 1.0, 1.1 and 1.2 kept. The production code of v1, v1.1 and v1.2 did not change; 1.3 adds `cbor.py`, `cose.py`, `v13.py`, the v1.3 sections of `esleme.py`, and the tests `t10_cose.py`, `t12_cose.py` with the T10/T11 extension. Image list before/after: `kayit/docker_images_{once,sonra}_2026-09-26.txt` (the only difference is `pq-a09-credgen:1.3`).
- Only `--rm` containers named `pq-a09-*` were used (`pq-a09-credgen`, `-dev13`, `-bagimsiz`, `-ls`). No `prune` or bulk deletion, no git, no outward-facing action. No container was left behind.
