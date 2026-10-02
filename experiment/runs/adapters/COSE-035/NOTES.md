# COSE-035 web-auth/cose-lib 4.8.2 — adapter notes (01.10.2026)

## 1. Version pinning
- PR item 14: the latest published release **4.8.2** (`8849e8bf043a`). The frame HEAD `1c854bf63c5c` has ML-DSA (`src/Algorithm/Signature/MLDSA`), 4.8.2 does not; under item 14 the HEAD capability is reported only descriptively. `spomky-labs/cbor-php` 3.4.2 as in the environment fix.

## 2. TK proposal
| Arm | Proposal | Evidence |
|---|---|---|
| ML-DSA-65 | **TK3** | 4.8.2 `src/Algorithm/Signature`: ECDSA, EdDSA, FullySpecified, RSA; ML-DSA/AKP/−49/−55 pattern 0 matches (end of `evidence/api-tarama.txt`). HEAD is a TK1 candidate (descriptive) |
| composite | **TK3** | the same |

## 3. V± result (`evidence/vpm-kosu.txt`; COSE V± rows, maintainers 01.10)
- COSE-VPLUS_ES256 ×4 `kabul`, COSE-VMINUS_ES256 ×4 `red/imza-gecersiz`.
- COSE-VPLUS_EdDSA (−8) `kabul`, VMINUS `red/imza-gecersiz`; COSE-VPLUS_EdDSA-ED25519 (−19) `kabul`, VMINUS `red/imza-gecersiz`.
- COSE-VPLUS/VMINUS_ML-DSA-65 and COSE-K6/K7 (−55): `red/alg-desteklenmiyor` (consistent with TK3).
- JOSE V± rows: `uygulanamaz/bicim-desteklenmiyor` (B6).
- **Gate: passed (ES256 + EdDSA + Ed25519).** Control label: both supported → `EdDSA` (contract §8 item 4).

## 4. Notes
1. **The documented verifier is the caller's pattern:** according to the README, the alg and crit checks are the caller's responsibility. The adapter applies the README pattern exactly; the allow-list is `Algorithm\Manager` (documented `has/get`). Whether this counts as "documented configuration" or "README example code" in the L-level assessment is the maintainers' decision (code: `adaptor.php` `algKontrol`, 15 lines).
2. **Multiple signers (COSE_Sign):** no documented rule → `ifade-edilemedi`; B4 alternative: loop over `CoseSignature::all()` + R/P0/P1 ≈ 10 lines (not written).
3. **L3:** `Manager::withKeyRestrictionsEnforced()` enforces the `alg` field (label 3) of the key; the EC2/OKP COSE_Keys of the battery carry no `alg`, so the binding is left to the key-type check (verify exception).
4. Synthetic COSE fixture: `evidence/sentetik_cose.py` (NOT the battery), smoke test `evidence/duman-testi.txt`.

## 5. Run record
- Pre-freeze file: 13:00Z (32 rows, the first run passed the gate) and ~13:59Z (with the image after the policy-name normalisation; same result).
- **Last run (14:05Z):** after the rule L4-YOL → `ifade-edilemedi` was added, the image was rebuilt and the same 32-row file was rerun (V± results unchanged).
