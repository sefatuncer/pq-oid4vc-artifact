# M-f — simplified definition and path scope (Step 7, task 9)

- **Date:** 26.09.2026. **Status:** Definition; the proof references refer to the runs under `sonuc/` (after anchor 8).
- **Scope:** Formal definition and verification rule. The proposal for specification text is in Step 13.

## 1. Definition

**M-f:** A per-entity expectation published by an authorised third party (the TL/LoTE operator), authenticated with PQ, which the verifier sees as current at decision time. The expectation constrains which evidence of the entity is accepted, via the **path** of the evidence.

**Core** (online or pinned current view; four components):
1. **Third party:** The expectation is a TL/LoTE entry, not the entity's own declaration.
2. **PQ authentication:** The entry or the resolution response is signed with a PQ key. The signer's key is pinned out of band (OJEU).
3. **Per entity:** Each entity has its own state: `none` → `pq_required` → `retired`. Legacy entities stay `none`.
4. **Current value:** The verifier sees the current value at decision time. This is achieved either with a fresh query bound to a nonce or with a pinned view that is kept current.

**Scope** (`yol_sinifi`, path class): If the expectation is not `none`, the verifier accepts the credential under one condition only: **every edge** of the accepted path from the anchor listed in the TL/LoTE to the credential must be signed with a PQ key.
- The class of the anchor edge is the algorithm in the TL entry, not its name.
- The class of an intermediate-CA edge is the algorithm in the intermediate CA certificate.
- Alternative scope `anahtar` (key): the credential must be verified with the PQ issuer key conveyed together with the expectation. This prevents forgery but does not secure the path class.
- The scope `yaprak_alg` (leaf algorithm) is not sufficient (§4).

**Offline annex** (only if the expectation may be stale; path-sensitive definitions, Amendment 8):
- **Monotonicity (extended):** After the verifier has seen `pq_required` for an entity, it never uses a `none` expectation for that entity again. Rejecting only a classical leaf is not enough.
- **Sunset (at expectation level):** A `none` expectation is invalid after the sunset time announced in advance for the entity. The mere expiry of the classical key does not protect the path class. The other option is to remove the classical anchors from the TL/LoTE at sunset.

## 2. Fields (per-entity record)

| Field | Value | Note |
|---|---|---|
| `state` | `none` / `pq_required` / `retired` | Life cycle; moves forward only |
| `scope` | `path` (proposed) / `key` | if `key`, the bound PQ key (or its digest) is carried in the entry |
| `sunset` | timestamp | end of validity of the `none` expectation (offline annex) |
| signature | TL/LoTE signature (ML-DSA) | The entry is protected by the single signature of the list (T013, T022–T025) |

Deterministic size: about 87 B per entity as an XML or JSON element (`sonuc/ek_yuk.csv`). In online mode one extra fetch per verification; zero with a pinned current view.

## 3. Verification rule

For an artefact `x` (credential, request, status token) and its issuer `I`:

1. **Obtain the expectation.**
   - Online: a query with a nonce to the TL/LoTE source; the response is PQ-signed and bound to this verification.
   - Pinned: the entry in the current view.
   - Verify the signature of the entry against the pinned PQ anchor.
2. **`state = none`** (and, in the offline annex, sunset not passed and `pq_required` never seen before for `I`): verify under today's rule (every valid path).
3. **`state ∈ {pq_required, retired}`:**
   - The leaf algorithm must be PQ; a classical leaf is rejected.
   - `scope = path`: every edge on the path must be PQ; reject at the first classical edge.
   - `scope = key`: the key of the leaf must be the bound key of the entry.
4. **Offline annex:** When `pq_required` is seen, the local state for `I` becomes `pq_required` permanently. If the sunset has passed, the `none` expectation is not used.

## 4. Proof status (Tamarin; `sonuc/karsilastirma.csv`)

This section is filled in with the run results: §5.

## 5. Limits

- **First contact:** The core provides the expectation before the first contact, because the entry is held by the third party. In the offline annex, a verifier that has never seen the expectation can be downgraded after the migration. This lasts until the cache is updated (TS 119 612 "Next update" window, ≤ 6 months: T009/T010).
- **Carrier:**
  - A fetched, current TL/LoTE or an OpenID Federation resolution provides the core; in a federation the key of the intermediate entity must also be PQ.
  - WRPRC is an unauthenticated field until the verification phase starts (T254). In phase 1 it is a conveyed, replayable object.
  - The `crit` header is not a carrier.
- **Time:** The symbolic model represents delay and window length with ordering constraints. The numerical τ analysis is in R6 and in the ASP model.
