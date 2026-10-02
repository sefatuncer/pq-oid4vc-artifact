# SDJWT-018 sd-jwt-python 0.10.4: evidence-rule second attempt

| Field | Value |
|---|---|
| Library | sd-jwt-python, PyPI `sd-jwt` 0.10.4 (wheel sha256 `d7ae669e...`); verification delegated to `jwcrypto` 1.6.1 |
| Repository / commit | https://github.com/openwallet-foundation-labs/sd-jwt-python, `cf27b5b89aba03fd676a51aec4737f5f46d4105d` |
| Environment | `pq-a09-env-python:1.0` (Python 3.13.15), `pip install --require-hashes -r requirements.lock` (lock copied from the installation record) |
| Date | 2026-10-03 (UTC 2026-10-02 22:51 to 22:59) |
| Time spent | about 10 minutes |
| Form | **L4c** (primary); L4m run as a supplement |
| Verdict | **expressible** through the documented key-resolution callback (caller-written per-issuer check of 8 lines; no own verification loop) |
| API hook found | yes: `SDJWTVerifier(..., cb_get_issuer_key, ...)`, callback signature `(issuer, header_parameters)` |

## Form and basis

- The issuance API signs with one key: `SDJWTIssuer(user_claims, issuer_key, ...)` and a single
  `add_signature` call (`src/sd_jwt/issuer.py` L159-186). Compact serialization is the default.
  The library's SD-JWT type is a single-signature SD-JWT, so the primary form is L4c.
- The verifier also accepts `serialization_format="json"` and hands the parsed JSON to
  `jwcrypto.jws.JWS.deserialize`, which accepts the General JSON serialization with several signatures.
  `JWS.verify` then succeeds if at least one signature verifies (`jwcrypto/jws.py` 1.6.1, L373-395).
  Because such objects pass through, L4m was also tested (section 4 of the run log).

## API scan (summary; full commands and outputs in `api-scan.txt`)

- `SDJWTVerifier.__init__(sd_jwt_presentation, cb_get_issuer_key, expected_aud, expected_nonce, serialization_format)`
  (`src/sd_jwt/verifier.py` L22-34). No algorithm parameter.
- `_verify_sd_jwt(cb_get_issuer_key, sign_alg=None)` is private and is called without `sign_alg`
  (L34, L52-63), so the verification runs with `alg=None`: the algorithm comes from the protected header.
- The callback is called as `cb_get_issuer_key(unverified_issuer, unverified_header_parameters)` (L60-62).
  It receives the `iss` value and the JOSE header (with `alg` and `kid`) and returns the key or key set.
  This is the documented way to bind keys to issuers (type annotation L25; usage in
  `src/sd_jwt/bin/generate.py` L84-91 and `tests/test_e2e_testcases.py` L53-55). The README documents only
  the test-case tooling, not the API.
- jwcrypto: `allowed_algs` is a property of each `JWS` object (L192-214), but the object is created inside
  the verifier (verifier.py L57), so the caller cannot set it. The module-level `default_allowed_algs`
  (L28-36) is a global list (L1 at most). The JWK `alg` member is not checked against the header for EC/OKP
  keys (it is read only for AKP keys, jwk.py L256-276).

## Attempt (`attempt.py`, output `attempt-run.log`)

Own keys: migrated issuer `https://issuer.example` with an ES256 key and an Ed25519 key (X = EdDSA);
legacy issuer `https://legacy-issuer.example` with its own ES256 key. The verifier always receives the
complete key set of each issuer (`JWKSet`).

1. Validity check with a callback that only resolves keys: all V+ accepted, V- rejected.
2. Native options only: there is no per-call or per-issuer option. The global jwcrypto list set to `['EdDSA']`
   rejects the migrated ES256 object but also the legacy ES256 object (mismatch), so it cannot express L4c.
3. L4c: one shared policy configuration with two issuer records, used by every `SDJWTVerifier` call:

   ```python
   POLICY_L4C = {MIG: {"W": {"ES256", "EdDSA"}, "R": {"EdDSA"}},
                 LEG: {"W": {"ES256", "EdDSA"}, "R": set()}}
   def cb_l4c(issuer, header_parameters):
       rec = POLICY_L4C[issuer]
       alg = header_parameters["alg"]
       if alg not in rec["W"] or (rec["R"] and alg not in rec["R"]):
           raise ValueError(...)
       return ISSUER_KEYS[issuer]
   SDJWTVerifier(presentation, cb_l4c)
   ```

   Result: migrated ES256 rejected, migrated EdDSA accepted, legacy ES256 accepted (all three as required).
   A corrupted EdDSA object is still rejected, and an ES256 object relabelled `alg=EdDSA` is rejected by
   the library, because jwcrypto verifies under the protected-header `alg` that the callback saw
   (jws.py L280-291).
4. Supplementary L4m (General JSON, ES256 + EdDSA signatures). Default callback: T2 and T3 are accepted
   (at-least-one semantics of jwcrypto). Callback that returns only the issuer keys whose algorithm is in
   R = {EdDSA}: T1 accept, T2 reject, T3 reject, T5 accept.

Summary line of the run: 14 of 14 checked rows as required.

## Verdict

**expressible.** The library has no native algorithm-policy option. The per-issuer policy is expressed
through the documented key-resolution callback, which receives the issuer and the protected header before
verification. The policy records and the check inside the callback are caller code (8 lines). The signature verification itself is
done only by the library; no own verification loop is written.

Interpretation note for the maintainers: if "the library's own mechanism" (pre-registration Section 5.13,
interpretation note) is read so that a caller-written check inside a callback does not count, this result
becomes "expressible with custom code" (B4, 8 lines). In either reading the API has a hook, so condition 1
of the evidence rule ("no hook in the API") does not hold and the rule is not satisfied.

Line reference for the hook: openwallet-foundation-labs/sd-jwt-python @ `cf27b5b89aba03fd676a51aec4737f5f46d4105d`,
`src/sd_jwt/verifier.py` L22-34 and L52-63.
