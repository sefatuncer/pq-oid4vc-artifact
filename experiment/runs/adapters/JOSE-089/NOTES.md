# JOSE-089 json-jwt 1.17.2 — adapter notes (01.10.2026)

## 1. Version pinning
- Latest published release 1.17.2 (tag v1.17.2 → `5fc6faed950f`; not the frame HEAD `fa5ef904013b`). The environment's `Gemfile.lock` (21 dependencies, CHECKSUMS) was used exactly.

## 2. TK proposal
| Arm | Proposal | Evidence |
|---|---|---|
| ML-DSA-65 | **TK3** | `jws.rb` only HS/RS/PS/ES; ML-DSA/EdDSA/OKP pattern 0 matches (`evidence/api-tarama.txt`) |
| composite | **TK3** | the same |

## 3. V± result (`evidence/vpm-kosu.txt`)
- ES256: VPLUS `kabul` (4 arms), VMINUS `red/imza-gecersiz` → **passed**.
- EdDSA/Ed25519: not supported (`red/alg-desteklenmiyor`); ML-DSA-65 and CMP00/01: `red/alg-desteklenmiyor`.
- **Gate: passed (ES256 only).**

## 4. Issues and notes for the maintainers
1. **No control arm X** (neither EdDSA nor Ed25519 is supported) → in the control arm the L measurement cannot be made with X = EdDSA.
2. **General JSON only the first signature:** `JSON::JWT.decode(Hash)` → `JWS.decode_json_serialized` verifies only `input[:signatures].first` (`lib/json/jws.rb` L199–216, lines at the end of `evidence/api-tarama.txt`). No option for a multi-signature rule (P0/P1/R) → for multi-signed General JSON P0/P1/L4/L4-S/L4-Y are `ifade-edilemedi`. For B5 (semantic class) this requires observing the "first signature" behaviour with **default configuration** rows (the additional policy `VARSAYILAN`); `jobs-v1.3.jsonl` has no VARSAYILAN row.
3. **B4 (custom-code alternative):** a loop that verifies each signature as a separate compact JWS with `JSON::JWS.decode_compact_serialized` and applies the R/P0/P1 rule ≈ 12 lines of Ruby (excluding blank lines/comments; not written, and under contract §1 it does not raise the L level).
4. json-jwt does not check claims (`exp`/`iat`).

## 5. Run record
- Synthetic smoke test: `evidence/duman-testi.txt`.
- The pre-freeze file was run twice: 12:48Z (16 rows) and 12:55Z (32 rows, after the COSE rows were added and after the change to not read `insa`). The last output is valid.
- **Last run (~13:59Z):** after the maintainers' policy-name normalisation rule (`|sdjwtvc=`, `@-19`; P2) was added, the image was rebuilt and the same 32-row file was rerun; the results did not change, `adaptor_sha256` reflects the current image.
- **Last run (14:05Z):** after the rule L4-YOL → `ifade-edilemedi` was added, the image was rebuilt and the same 32-row file was rerun (V± results unchanged).
