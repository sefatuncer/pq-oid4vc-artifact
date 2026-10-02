# Export format of the sampling frame (Step 3 → technical gate → Tamarin)

> **Produced by:** `sampling/disa_aktar.py` (ASP work). **The ASP work does not select samples** (pre-registration §2F item 2): the selection is made with the maintainers' seeded script (seed 20260926; strata goal × type).
> **Files:** `cerceve.jsonl` (gate frame), `kesif_2x2.jsonl` (exploratory grid of §2D item 11; not counted for the gate), `disa_aktarim_ozeti.json` (row counts, SHA-256, stratum counts).
> **Encoding:** UTF-8, one JSON object per line (JSON Lines), keys sorted, line ending `\n`.

## 1. Frame definition (pre-registration §4.18, §2F)

- **Cell:** an element of Q in the primary configuration (§2C 2.3) = goal {G1, G2, G3, G4, all} × Φ {f1, f2, f3} × τ {fast 600 s, medium 259,200 s, slow 2,246,400 s} × anchor {fresh, pinned, cached} × policy {p0…p4}.
- **`asgari` row (minimal):** a subset-minimal set (PQ nodes ∪ expectation carriers) of the cell. **Expectation: verified in Tamarin.**
- **`bir-eksik` row (one-short):** a minimal set with one element (one PQ node or one carrier) removed. If the same set arises from several minimal sets in the same cell, one row is written; `kaynaklar` lists all of them. **Expectation: a trace (falsified in Tamarin).**
- **`birincil-kume` row (primary set)** (only in `kesif_2x2.jsonl`): the verdict of the minimal set of the same Q cell of the primary configuration under the parameters of the grid cell. In the cell `ca_baglama = ad, ayni_ad_klasik_ca = var` all G1–G3 cells are UNSAT, so the mandatory extra sample of §2F can be chosen from this type.
- **UNSAT cells** produce no row (no minimal set). In the primary configuration all G4 and "all" cells are UNSAT (decision notes N5).

## 2. Row fields

| Field | Type | Meaning |
|---|---|---|
| `satir_id` | string | `CERCEVE-000001` … / `KESIF_2X2-000001` … (unique in the file; order = production order) |
| `kaynak` | string | `birincil` (primary) / `kesif_2x2` |
| `hucre_id` | string | Query id, e.g. `birincil|g2|f2|hizli|taze|p4` or `cab|ad|var|g1|f1|hizli|taze|p4` |
| `hucre` | object | `hedef, faz, tau (label), tau_s (seconds), capa, politika, tasarim` (+ in the 2×2 grid `ca_baglama, ayni_ad_klasik_ca`). All other parameters have their primary value (§2C 2.3; REPORT §1.5) |
| `hedef` | string | `G1` `G2` `G3` `G4` `tumu` (stratum key) |
| `tur` | string | `asgari` / `bir-eksik` / `birincil-kume` (stratum key) |
| `kume.pq_dugumler` | list | Decision nodes that are PQ (the 17 nodes of §2C: a01 a02 a03 a04 a05 a06 a07 a08 a09a a09b a10 a11 a12 a13 ecrl ejvi eas). A node not in the list is classical |
| `kume.tasiyicilar` | list | Selected expectation carriers `[C, X]`: artefact C carries the expectation "PQ required" for the entity that signs X (policy P3/P4) |
| `asgari_no` / `kaynaklar` / `birincil_asgari_no` | | The minimal set(s) from which the row was derived and (for one-short) the removed element: `pq(aXX)` or `tasi(C,X)` |
| `asp_tahmini` | string | `verified` (goal met) / `falsified` (goal violated). COMPUTED in the evaluation mode of ASP (`cekirdek.lp`, scenario `tum` = unbounded k, S2); not assumed |
| `ihlal_edilen` | list | All goals violated by this assignment (g1…g4, tum, g5 untimed, g2i exploratory) |
| `tanik_sahte_artefaktlar` | list | Witness: artefacts whose forgery can effectively be delivered to the verifier (attack path hint for the trace) |
| `alt_cizge` | list | The artefacts on the path of the goal(s) (§3) |
| `tamarin` | object | Template and flag mapping (§4) |

## 3. The `alt_cizge` element

| Field | Meaning |
|---|---|
| `artefakt`, `dugum` | Model artefact and the decision node it belongs to (same node = migrated together) |
| `pq` | Is the signing key PQ (for the unsigned A06/E_JVI/E_AS: is it PQ-bound) |
| `sabit` | Is the signing key pinned out of band (R5; OJEU) |
| `kanal` | `aktarilan` (conveyed) / `cekilen` (fetched) / `sabitlenmis` (pinned) / `sunan_uc` (presenter's own endpoint) / `yalniz_tasima` (transport only) / `kimliksiz` (unauthenticated) |
| `tasima`, `tasima_sahtelenebilir` | The transport of a fetched/transport-only artefact (webpki / lotl_kanal) and whether the server authentication is forgeable |
| `tanitici` | The artefacts that introduce (certify/list) the signing key: OR edges (any-valid-path) |
| `klasik_alternatif` | Is the entity's classical key also accepted because of the phase (K4) |
| `beklenti_var` | Is an authenticated per-entity expectation active (K3) |
| `pencere_s`, `pencere_sinifi` | W_trust (seconds) and class: `uzun_omurlu` (long-lived) / `donem` (period) / `belirtec` (token) (Tamarin R6 LONG / ROTATED / PER_TOKEN) |
| `klasikse_pencerede_kirilir` | Is τ < W_trust + clock skew (300 s) |
| `varyant` | Active unsigned form (e.g. `a05_meta_imzasiz`, `a12_istek_imzasiz`; M-b0) |
| `sahte` | Is it effectively forged under this assignment |

## 4. The `tamarin` mapping

- `sablonlar`: the Tamarin templates that build the path of the cell; `spthy_onerisi`: file names (`models\tamarin\modeller\`).
  - `R5` LOTL (pinned) → TL/LoTE; `R1` anchor → CA → leaf (G1/G2: credential; G3: status token signer); `R1(WRPAC)` G4 chain; `R4` cnf/KB-JWT; `R2/R3` coexistence + expectation channel; `R6/R6h5` short-window keys; `R7hx` alternative/same-name classical CA (2×2 only).
- `bayraklar` (flat Booleans; the same names as the Tamarin `-D` flags were used):

| Flag | ASP counterpart |
|---|---|
| `LOTL_PQ`, `TL_PQ` | a01, a02 ∈ `pq_dugumler` |
| `PIN_TL` | anchor = pinned (TL signing key out of band; R5) |
| `LOTE_OJEU_YOLU` | combined trust store: the anchor is also listed in the OJEU-pinned LoTE (a second path independent of the LOTL) |
| `LOTL_KANAL_PQ`, `CEKILEN_TASIMA_PQ` | a13 ∈ `pq_dugumler` (WebPKI classical in the primary configuration → always false) |
| `ROOT_PQ`, `CA_PQ`, `ISS_PQ` | a03 (anchor key), a04 (CA key), a07 (issuer key) — R1 convention: pq(L) = the key that SIGNS L is PQ |
| `DURUM_YAPRAK_PQ`, `DURUM_CEKILEN_VIA_TLS` | a08 ∈ set; the status token is fetched (R3 VIA_TLS; deliverable if the transport is classical) |
| `DEV_PQ`, `SINGLE_USE` | a10 ∈ set; single use in the wallet (does not change the window; H5) |
| `ACCESS_CA_PQ`, `RP_KEY_PQ`, `IMZASIZ_ISTEK_KABUL` | a11, a12 ∈ set; acceptance of unsigned requests (M-b0) |
| `COEXIST`, `BEKLENTI`, `BEKLENTI_TASIYICI_PQ` | the PQ nodes on the path whose classical alternative is open, and for each whether the expectation is active; carrier mapping X → C |
| `R6`, `R6_tau_s` | short-window keys: class, window, "is τ longer than the window" (symbolic R6 regime: FAST ⇔ false) |
| `ALT_CA`, `NAME_BIND`, `KEY_BIND`, `ALT_SAME_NAME`, `ALT_CA_KLASIK_SABIT` | 2×2: diger_ca = var; ca_baglama = ad / anahtar; ayni_ad_klasik_ca = var; the alternative CA key cannot be migrated (R7hx) |

- `lemma`: the security lemma to translate. The expected Tamarin verdict is `asp_tahmini`.
- **Abstraction note:** the Tamarin templates represent time with flags (τ is in ASP). If the R6 flag `tau_pencereden_uzun = true`, the break rule of the corresponding key can fire only after the window has closed (R6 SLOW/MEDIUM). Long-lived keys can always be broken on the primary τ grid.
