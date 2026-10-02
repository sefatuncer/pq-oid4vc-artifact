# COSE-036 wolfCOSE @ f907071b1012 — adapter notes (01.10.2026)

## 1. Version pinning
- No release → frame `son_commit_sha` `f907071b1012` (PR item 14); wolfSSL v5.9.2-stable `ac01707f552c`, with the flags of the environment. `HEDEF_SURUM = git:f907071b1012`. GPL-3.0: only measured.

## 2. TK proposal
| Arm | Proposal | Evidence |
|---|---|---|
| ML-DSA-65 | **TK1** | `wolfcose.h` `WOLFCOSE_ALG_ML_DSA_65 (-49)`, `WOLFCOSE_KTY_AKP`, `wc_CoseKey_SetMlDsa`; wolfSSL `--enable-mldsa` (`WOLFSSL_HAVE_MLDSA`); V± passed in the ML-DSA arm |
| composite | **TK3** | no −55/composite; COSE-K6/K7 `red/alg-desteklenmiyor` (AKP + −55 key `UNSUPPORTED`) |

## 3. V± result (`evidence/vpm-kosu.txt`; COSE V± rows)
- COSE-VPLUS_ES256 ×4 `kabul`, VMINUS ×4 `red/imza-gecersiz`.
- COSE-VPLUS_EdDSA (−8) `kabul`, VMINUS `red/imza-gecersiz`; COSE-VPLUS_EdDSA-ED25519 (−19) `kabul`, VMINUS `red/imza-gecersiz`.
- **COSE-VPLUS_ML-DSA-65 `kabul` (`dogrulanan: ML-DSA-65`), COSE-VMINUS_ML-DSA-65 `red/imza-gecersiz`.**
- COSE-K6/K7 (−55): `red/alg-desteklenmiyor`. JOSE rows B6.
- **Gate: passed (ES256 + EdDSA + Ed25519 + ML-DSA-65)** — with the `WOLFCOSE_ENABLE_DEPRECATED_ALGS` configuration.

## 4. Notes for the maintainers (decision needed)
1. **The RFC 9053 ids are off in the default build:** with the default `make`, −7 and −8 are rejected with `COSE_BAD_ALG` (−9011) (synthetic evidence `evidence/duman-varsayilan-derleme.txt`; `docs/Macros.md` L149–157 "Off by default"). The measurement was made with a build where the documented macro is on. Alternative: default build + ESP256 (−9) vectors for ES256 (open question H in the battery-mapping notes). The environment record (`kur.sh`) was `make all` without the macro.
2. The policy mechanism is the `alg` pin (a single alg); for a W with several algs the natural alg is chosen (MAPPING §2). This is an adapter mapping decision.
3. **B4:** for a COSE_Sign multi-signer rule, a signer loop over `wc_CoseSign_Verify` ≈ 12 lines of C (not written).
4. In the Python driver ctypes calls cannot be interrupted → the 60 s limit per vector is not applied (a time limit at runner level is recommended).

## 5. Run record
- Smoke tests: `evidence/duman-varsayilan-derleme.txt` (without the macro), `evidence/duman-testi.txt` (with the macro; fixture `../COSE-035/evidence/sentetik_cose.py`, ML-DSA-65 included).
- Pre-freeze file: 13:45Z (first), ~13:59Z, 14:05Z; V± the same.
