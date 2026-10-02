# JOSE-089 json-jwt 1.17.2: evidence-rule second attempt

| Field | Value |
|---|---|
| Library | json-jwt, RubyGems `json-jwt` 1.17.2 (Gemfile.lock CHECKSUMS `sha256:97e37c1c...`) |
| Repository / commit | https://github.com/nov/json-jwt, `5fc6faed950f9dff9fd41ca663cf35ef12f46575` (tag v1.17.2); the installed `lib/` is identical to the commit archive |
| Environment | `pq-a09-env-ruby:1.0` (Ruby 3.4.11, OpenSSL 3.5.7), `bundle install` frozen to the record's Gemfile.lock |
| Date | 2026-10-03 (UTC 2026-10-02 23:25 to 23:29) |
| Time spent | about 5 minutes |
| X | ES384 (no EdDSA in json-jwt 1.17.2) |
| Form | **L4c** |
| Verdict | **not-expressible** (in one verifier configuration); "L4c (consecutive)" of contract §5.3 is reachable with the per-call allow-list |
| API hook found | no per-issuer or per-key mechanism and no callback; only the per-call `algorithms` allow-list (L2) |

## Form and basis

`JSON::JWS.decode_json_serialized` takes only `signatures.first` of a General JSON object and verifies it as a
compact JWS (`lib/json/jws.rb` L199-216); output in the general syntax has one signature (`lib/json/jwt.rb`
L62-71). The run (section 5) shows that the decision depends only on `signatures[0]`. Multi-signature objects are
not supported: form L4c.

## API scan (summary; full commands and outputs in `api-scan.txt`)

- Entry point `JSON::JWT.decode(input, key_or_secret = nil, algorithms = nil, ...)` (`lib/json/jose.rb` L59-67).
  The README documents `JSON::JWT.decode(input, public_key)` (README L45-48).
- `JWS#verify!(public_key_or_secret, algorithms = nil)` accepts if the header `alg` is in `algorithms`
  (or `algorithms` is blank) and the signature verifies (`lib/json/jws.rb` L21-32). This is one allow-list per call.
- A `JSON::JWK::Set` key argument is resolved by `kid` only (`lib/json/jose.rb` L24-33, `lib/json/jwk/set.rb`
  L22-26). The JWK `alg` member is not checked, so there is no per-key algorithm binding. There is no
  key-resolution callback, no issuer concept and no required-set rule.

## Attempt (`attempt.rb`, output `attempt-run.log`)

Own keys: migrated issuer ES256 and ES384 (kids `mig-es256`, `mig-es384`), legacy issuer ES256 (`leg-es256`).

1. Validity check: V+ accepted, V- rejected.
2. One configuration for both issuers (all keys in one JWK set): with `algorithms = [:ES384]` the legacy ES256
   object is rejected; with `[:ES256, :ES384]` the migrated ES256 object is accepted. No single configuration
   gives the three L4c decisions.
3. Labelling the migrated ES256 key `alg: ES384` does not change anything: the ES256 object is still accepted.
4. Per-issuer records applied by the caller (contract §5.3 "L4c (consecutive)"): the caller reads the unverified
   `iss` (`JSON::JWT.decode(t, :skip_verification)`) and calls `decode` with that issuer's key set and allow-list.
   Migrated ES256 reject (`UnexpectedAlgorithm`), migrated ES384 accept, legacy ES256 accept. The record selection
   happens in caller code outside the library, with two different configurations of the per-call mechanism.

Summary line of the run: 11 of 13 checked rows as required; the 2 mismatches are the single-configuration rows
of section 2.

## Verdict

**not-expressible** as defined for L4c (one verifier configuration holding a per-issuer policy). No hook found:
the library has a per-call allow-list but no per-issuer or per-key algorithm binding and no callback through which
it could apply different allow-lists to different issuers. The attempt with one configuration failed (section 2).

Line reference: nov/json-jwt @ `5fc6faed950f9dff9fd41ca663cf35ef12f46575`, `lib/json/jose.rb` L24-33 (key
selection by `kid` only) and L59-67 (`decode` takes a single key argument and a single `algorithms` list),
`lib/json/jws.rb` L21-32 (`verify!`: one allow-list, no issuer).

Note for the maintainers: with two consecutive configurations of the per-call allow-list (section 4), the three
L4c decisions are reached. Contract §5.3 names this "L4c (consecutive)" and calls it a candidate deviation from
the pre-registration text. If "L4c (consecutive)" is accepted as L4c, this target is expressible and the evidence
rule is not satisfied.
