# Notes from the inventory work to the maintainers (Step 9a)

Details are in `SUMMARY.md` and `CRITERIA-DRAFT.md`. Only points that may affect shared files are listed here.

1. **The pilot basis has moved (R1).**
   - `openwallet-foundation/sd-jwt-js` was archived in September 2026 and moved to `openwallet-foundation-labs/identity-common-ts`.
   - `oid4vc-ts` moved to the same repository. The npm package `@sd-jwt/core` now points to this repository.
   - `sd-jwt-js` #388/#389 and commit `c7cf23dbc1b8` in version 3 §10 refer to the old repository. The new repository and commit should be pinned in the pre-registration.
2. **Authlib excluded (K3).** `authlib.jose` is deprecated; the warning in the pilot output shows this. Its successor `joserfc` is a reserve.
3. **No target in n has native support for composite -04.**
   - The only native example is `lestrrat-go/jwx` (reserve; the `jwx-go/compsig` extension is experimental).
   - For the main treatment arm, the classes T2 (plug-in/callback) and T3 (unknown alg) should enter the pre-registration (SUMMARY §3.2).
4. **Definition of L4.** 17 of the 31 targets support only compact serialization. If the single-signature form of L4 is not written into the pre-registration, the denominator of H6 shrinks (SUMMARY P2).
5. **Option that needs a decision (SUMMARY P7).** irmago (Yivi) is the only REF candidate that verifies ML-DSA. Moving it forward for the PQ arm of the emulator changes the rule "G sources first".
6. **Privacy incident (R12; closed).**
   - An anonymous clone of a deleted Bitbucket repository triggered Git Credential Manager. The process was terminated without receiving any input; no credentials were sent.
   - All later git calls ran with `credential.helper=` and `GCM_INTERACTIVE=never`.
   - I recommend the same setting if other work also uses anonymous git.
