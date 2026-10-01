# Exploratory: encrypted responses and harvest-and-forge (H5)

`R6_h5_enc.spthy` is a copy of the pre-registered model `../modeller/R6_h5.spthy` with one added flag
family (`ENC`, `ENC_CL`). It is not part of the pre-registered run set. Expectations were written to
`EXPECTED.tsv` before the runs. `run.sh` runs all variants (Tamarin 1.12.0, 4 GB, 600 s each); the full
outputs are the `E*.txt` files.

- **Setting.** OpenID4VP responses are encrypted to the verifier; HAIP uses ECDH-ES with P-256. The holder presents only to registered verifiers and encrypts each response to the verifier's encryption key.
- **`ENC_CL`.** The verifier's encryption key is classical. After Q-day a CRQC can extract it and decrypt responses harvested earlier.
- **Without `ENC_CL`.** The encryption key is post-quantum and cannot be extracted.
- **In all variants the device (WSCD) key is classical.**

| Variant | Flags | G2 presentation unforgeability | Attribution |
|---|---|---|---|
| E0 | none (plaintext responses, fast tau) | falsified | device key extracted inside the validity window |
| E1 | ENC, ENC_CL (fast tau) | falsified | `M_harvest_decrypt_forge` verified: decrypt harvested response, extract device key, forge |
| E2 | ENC (PQ encryption, fast tau) | verified | the credential and its `cnf` key never reach the attacker |
| E3 | ENC, SINGLE_USE | verified | |
| E4 | ENC, ENC_CL, SLOW | verified | the device key is extracted only after the credential expired |
| E5 | ENC, KEY_REUSE | verified | a reused classical holder key is not exposed either |

All six results match the recorded expectations. Every well-formedness check passed, and every health lemma (`executable*`, `attack_needs_crqc`) is verified.

**Reading.** In the harvest-and-forge attack the attacker needs the presented credential and its `cnf` key. Under classical response encryption, harvest-now-decrypt-later supplies them. Post-quantum response encryption removes that network path, so with a classical device key the forgery disappears even at fast tau.

**Limits.** The model assumes three things:
- issuance is confidential;
- the attacker is not a registered verifier;
- the credential leaks through no other path (wallet backup, compromised verifier storage).

A registered but malicious verifier receives the credential directly, so post-quantum response encryption does not replace a post-quantum device key against that attacker.
