# threat-model — threat model (Step 1)

**What it does.** Defines the system, the 13 signed artefacts, the channel classes, the attacker
classes, the assumptions and the security goals G1–G5 on which the formal models are built. Every
statement taken from the specifications cites a row of the traceability matrix (`Txxx`).

**Inputs.** `traceability/izlenebilirlik.csv` (400 rows, 400/400 quotes verified),
`spec-corpus/` and the LOTL snapshot `data/eu-lotl_seq394.xml`.

**Used by.** `models/asp/` (artefacts, edges, channels, windows and goals are encoded as facts),
`models/tamarin/` (attacker classes and goals become rules and lemmas), the mechanism models in
`models/mechanisms/`.

## Files

| File | Content |
|---|---|
| `THREAT-MODEL.md` | The threat model (draft of 24.09.2026): §1 system and roles, §2 the 13 artefacts (signer, base algorithm, channel, acceptance window, exposure of the public key), §3 channel classes, §4 trust dependency graph (Mermaid), §5 attacker classes S1–S3, §6 assumptions, §7 security goals and their closest normative basis, §8 τ regimes × acceptance windows (a priori comparison, input to the sensitivity grid), §9 out of scope |
| `guven-bagimliligi.dot` | The trust dependency graph as Graphviz source: arrows follow the verification flow, node colour gives the channel class (pinned, fetched, conveyed, transport) |

Render the graph with `dot -Tsvg threat-model/guven-bagimliligi.dot -o trust-dependency.svg`
(the file is readable without rendering).

## Key definitions

- **Channel classes.** *Conveyed*: the presenting party brings the object (credential, `x5c`,
  KB-JWT, request object, access and registration certificates, wallet attestations). *Fetched*:
  the verifier or wallet obtains it from an authoritative source (LOTL, TL/LoTE, status list,
  issuer metadata, Type Metadata, CRL). *Pinned/cached*: provided out of band or from a cache (OJEU
  digests, WebPKI root store, Type Metadata pinned by digest).
- **Attacker classes.** S1 network attacker (Dolev–Yao) before and after Q-day; S2 CRQC(τ, k) that
  recovers the private key of an observed classical public key in time τ, at most k keys per
  window; S3 harvest-now-forge-later attacker.
- **Goals.** G1 claims unforgeability, G2 presentation unforgeability / holder binding, G3
  revocation soundness, G4 relying-party authentication (wallet side), G5 downgrade resistance: a
  migrated entity cannot be accepted with classical evidence only outside its announced legacy
  window.

## Turkish names in this folder

`guven-bagimliligi` trust dependency. Labels in the document: [V3] taken from the design
document, version 3; [C] added or corrected from the corpus; [inf] inference of the study.
