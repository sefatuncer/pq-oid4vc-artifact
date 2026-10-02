# JOSE-071 lcobucci/jwt 5.6.0 — adapter notes (01.10.2026)

## 1. Version pinning
- Latest published release 5.6.0 (`bb3e9f21e419`). Package id in `SECIM.csv`/`CERCEVE.csv`: `lcobucci/jwt` (packagist; jwt.io name "jwt").

## 2. TK proposal
| Arm | Proposal | Evidence |
|---|---|---|
| ML-DSA-65 | **TK3** | `src/Signer`: Ecdsa (Sha256/384/512), Eddsa, Rsa, Hmac, Blake2b; ML-DSA/JWK 0 matches (`evidence/api-tarama.txt`). The `Signer` interface is an extension point, but TK2 is out of scope |
| composite | **TK3** | the same |

## 3. V± result (`evidence/vpm-kosu.txt`)
- ES256 ×4 accept / VMINUS ×4 `red/imza-gecersiz`; EdDSA accept / VMINUS_EdDSA `red/imza-gecersiz`; label `Ed25519` `alg-desteklenmiyor` (control arm EdDSA); ML-DSA-65 and CMP `alg-desteklenmiyor`; COSE B6.
- **Gate: passed (ES256 + EdDSA).**

## 4. Notes
1. No JWK API → the key is converted in the adapter to PEM/raw bytes (`dogrudan`). This conversion is not verification.
2. L2/L3 mechanism: per-call (Signer, Key) constraint set; the alg binding is explicit through the choice of signer (SignedWith checks header alg = algorithmId).
3. Multi-signature B6; no B4 candidate.
4. Because the `RequiredConstraintsViolated` message exceeds 200 characters, `hata_ozeti` was shortened (format only; classification uses the full message).

## 5. Run record
- The pre-freeze file was run four times (12:56–12:58Z); the first run passed the gate, the next three were only for `hata_ozeti` format corrections (classes unchanged). The last output is valid.
- **Last run (~13:59Z):** after the maintainers' policy-name normalisation rule (`|sdjwtvc=`, `@-19`; P2) was added, the image was rebuilt and the same 32-row file was rerun; the results did not change, `adaptor_sha256` reflects the current image.
- **Last run (14:05Z):** after the rule L4-YOL → `ifade-edilemedi` was added, the image was rebuilt and the same 32-row file was rerun (V± results unchanged).
