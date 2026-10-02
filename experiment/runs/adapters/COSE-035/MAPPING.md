# COSE-035 web-auth/cose-lib — policy → API mapping (contract 1.0 §2.2, RUNNER §2)

- **Target:** `web-auth/cose-lib` **4.8.2** (`8849e8bf043a`) + `spomky-labs/cbor-php` 3.4.2 (environment fix; a `suggest` of cose-lib), `composer.lock` the same as the environment record.
- **Image:** `a10-cose-035:1` (`FROM pq-a09-env-php:1.0`; PHP 8.4.26, OpenSSL 3.5.8). **Call:** `… a10-cose-035:1 adaptor /is/<isler> /c/COSE-035.<kosu>.jsonl`.
- **Source:** `adaptor.php`, `ortak.php` (same skeleton as JOSE-070).

## 1. Shared rules
The same as `JOSE-087/MAPPING.md` §1 (A/X, W/R, effective allow-list for a single signature = R, VARSAYILAN (default), only `dogrulama_girdileri`, policy name normalisation `split('|')[0].split('@')[0]`, P2 ∈ {GEC, P0, P1}). COSE ids (BATARYA-ESLEME §3): ES256 −7, ES384 −35, EdDSA −8, Ed25519 −19, ML-DSA-65 −49, ML-DSA-65-ES256 −55.

## 2. Documented verifier = the README pattern
cose-lib is a primitives library. README "Verifying a COSE_Sign1 Signature": *"The library verifies signatures; it does not decide what a message is allowed to say. Checking that `alg` is the one expected for that key, and refusing any `crit` label … are the caller's responsibility"* (`tests/Signature/DocumentedVerifierTest.php` runs this code). The adapter follows the pattern exactly:
`Decoder::create()->decode()` → `CoseHeaders::fromMessage()` → protected `alg` (label 1) → allow-list → `crit` (understood labels {1, 2}) → rejection of a detached payload → `Signature1::create(protected, payload)` (for COSE_Sign `Signature::create(body_protected, sign_protected, payload)`) → `$algorithm->verify((string)$yapi, $key, $sig)`.

| Policy | Configuration |
|---|---|
| GEC / P0 / P1 / P2 / VARSAYILAN | `Manager::create()->add(ES256, ES384, EdDSA, FullySpecified\Ed25519)`; `Manager::has(alg)` is the allow-list |
| IZIN-A / IZIN-AX | Manager = W ∩ native (ML-DSA-65/composite cannot be added) |
| L4 / L4-S / L4-Y (COSE_Sign1 or COSE_Sign with a single signer) | Manager = {X} (effective allow-list = R) |
| COSE_Sign with several signers × every policy | **`ifade-edilemedi`**: no documented option for a rule over the signers (P0/P1/R); a loop over the `CoseSignature::all()` list would be the caller's code (B4) |
| L4-YOL | **`ifade-edilemedi`**: no documented API for an x5chain path-class policy (B2) |

- **Key path `COSE_Key`:** `dogrulama_girdileri.cose_key_hex[kid]` is decoded with CBOR → `Key::createFromData()` (Ec2Key/OkpKey by kty). The kid is read from header label 4 (unprotected). Enforcement of key restrictions (`withKeyRestrictionsEnforced`) stays at its default (off); the EC2/OKP keys of the battery carry no `alg` (label 3).
- On acceptance `dogrulanan_algoritmalar = [{alg: JOSE name of the COSE id}]`.

## 3. B6 decisions
| Serialization | Decision |
|---|---|
| COSE_Sign1, COSE_Sign | supported |
| compact, general, sd-jwt-*, oid4vci-toplu-yanit, dcapi-json-parametre | **B6** (no JOSE/SD-JWT API) |

## 4. Error → hata_sinifi
| Case | hata_sinifi |
|---|---|
| CBOR could not be decoded / not COSE_Sign1-COSE_Sign / no protected `alg` / detached payload | `ayristirma` |
| `Manager::has(alg)` false: alg exists in the library / does not exist (−49, −55, unregistered) | `alg-izin-disi` / `alg-desteklenmiyor` |
| `crit` not an array, or a label that is not understood | `crit` |
| no COSE_Key for the kid | `anahtar-bulunamadi` |
| `Key::createFromData` fails | `alg-desteklenmiyor` |
| `verify()` exception (key type ≠ alg) | `alg-anahtar-uyusmazligi` |
| `verify()` false | `imza-gecersiz` |
| other | `istisna-diger` |
