# C3 (H6) statistics input — schema `c3-istat-girdi/1.0`

**Scope:** the single input format of the `c3istat` scripts (Step 9 task 9). Step 10 produces one file in this format; the frozen scripts read only this.

**Source of the definitions:** the pre-registration (PR) `00-on-kayit\ON-KAYIT-TASLAK.md`. Sections referred to:
- §2B (n = 31; L4m/L4c; TK1–TK3; delegation),
- §2D-A item 2 (control label),
- §3.7, §4.13–§4.15, §6.3–§6.11.

In case of conflict the PR prevails. The interpretations made in this schema are listed in `DECISION-NOTES.md`.

**Formats:**
- Canonical format: a single UTF-8 **JSON** file (§1).
- Equivalent **CSV** format: `hedefler.csv` (+ optional `vakalar.csv`) (§4).

Both formats pass through the same validator and give the same result (test `test_uctan_uca.CsvJsonEsdegerlik`).

---

## 1. Top level of the JSON file

```json
{
  "sema_surumu": "c3-istat-girdi/1.0",
  "veri_turu": "sentetik",
  "aciklama": "serbest metin",
  "hedefler": [ { "...": "§2" } ],
  "vakalar":  [ { "...": "§3" } ]
}
```

| Field | Type | Required | Rule |
|---|---|---|---|
| `sema_surumu` (schema version) | string | yes | Exactly `c3-istat-girdi/1.0` |
| `veri_turu` (data type) | `sentetik` \| `olcum` | yes | Only `sentetik` (synthetic) is used in Step 9. `olcum` (measurement) only after the freeze, in Step 10 |
| `aciklama` (description) | string | no | — |
| `hedefler` (targets) | array | yes | At least 1 record; `hedef_id` unique |
| `vakalar` (cases) | array | no | For the cluster bootstrap (PR §6.9). If absent, the bootstrap is reported as "no data" |

An unrecognised field is an **error** (so that typos are not silently swallowed).

## 2. Target record (`hedefler[]`)

Value rules:
- `null` = no value. The reason is written in `belirsiz_nedenleri`.
- Binary fields take only `0` or `1` (`true`/`false` is also accepted in JSON).
- Ordinal fields are integers.

| Field | Type | Required | Meaning and PR basis |
|---|---|---|---|
| `hedef_id` | string | yes | Unique id (e.g. `JOSE-009` of `SECIM.csv`). In the bootstrap the cluster order is the lexicographic order of this field |
| `tabaka` (stratum) | `JOSE` \| `SDJWT` \| `COSE` \| `REF` | yes | PR §2B.1–3. `REF` = reference verifier: **outside n**, outside all tests, only in the descriptive list (PR §2B.4) |
| `adaptor_gecersiz` (adapter invalid) | binary | yes | 1 ⇒ outside n_eff (PR §4.15). The measurement fields may then be `null` |
| `adaptor_gecersiz_gerekce` (reason) | string | yes if `adaptor_gecersiz = 1` | — |
| `tk_sinifi` | `TK1` \| `TK2` \| `TK3` | yes (except REF) | Treatment class (PR §2B.7). T2 only TK1 + TK2 |
| `l4_bicimi` | `L4m` \| `L4c` | yes (except REF) | PR §2B.6. Reported descriptively |
| `kontrol_etiketi` | `EdDSA` \| `Ed25519` \| `ES384` (amendment 10) | yes (except REF and `adaptor_gecersiz = 1`) | PR §2D-A.2, §2E.3: the label used is recorded per target. Descriptive |
| `Y_L4` | binary \| null | yes | The primary variable of H6 (PR §3.7, §2B.6) |
| `L_duzeyi` | 0…5 \| null | yes | Ordinal L0–L5 (PR §4.13) |
| `F_K` | binary \| null | yes | Deviation from the oracle in at least one of K1–K3 in the control arm (PR §6.4) |
| `F_T` | binary \| null | yes | The same, in the treatment arm |
| `D_soy` | binary \| null | yes | Acceptance of the stripped document (K3) in the default configuration (PR §6.4) |
| `B1` | `red` \| `yok_sayma` \| `dogrulama_duser` \| null | yes | Behaviour on an unknown composite `alg` (PR §4.13): reject / ignore / verification falls through |
| `B2` | binary \| null | yes | Can a mixed `x5c` chain policy be expressed (1 = yes) |
| `B3` | binary \| null | yes | Is an unprotected `x5c` processed (1 = yes) |
| `B4_ozel_kod` | binary \| null | yes | Flag "expressible with custom code" (determination rule of PR §4.13) |
| `B4_satir` | integer ≥ 1 \| null | yes if `B4_ozel_kod = 1` | Number of lines of custom code (blank lines and comments excluded). Must be `null` if `B4_ozel_kod ≠ 1` |
| `B5` | `en_az_biri_gecerli` \| `mevcut_tumu_gecerli` \| `gerekli_kume` \| `diger` \| null | yes | Semantic class: at least one valid / all present valid / required set / other |
| `B6` | binary \| null | yes | Unsupported format ("not applicable" record) |
| `surum_8725bis_sonrasi` | binary \| null | yes | T4 stratum: did the target release a version **after** 21.08.2026 (8725bis-10) (PR §6.6) |
| `son_surum_tarihi` | `YYYY-MM-DD` \| null | no | Check field. If given, `surum_8725bis_sonrasi = 1 ⇔ date > 2026-08-21` must hold; otherwise an error |
| `pilot` | binary | yes | Library of pilot P3 (PR §0.3, §6.10) |
| `devralan` (delegating) | binary | yes | Delegates verification to another target (PR §2B.9; e.g. WalletFramework → IdentityModel) |
| `devraldigi_hedef` | string \| null | yes if `devralan = 1` | `hedef_id` of the target delegated to; it need not be in n |
| `belirsiz_nedenleri` | object `{field: reason}` | yes if a field is `null` | One reason for each `null` measurement field (§2.1) |

### 2.1 Reasons for `null`

| Code | Meaning | PR |
|---|---|---|
| `oracle_uyusmazligi` | Oracle A and B disagree | §4.15 |
| `kanit_kurali` | The "not expressible" evidence rule was not met | §4.14, §4.15 |
| `kararsiz_3_tekrar` | The value is not identical in the three repetitions (3/3) | §4.15, §6.11 |
| `deneme_celiskisi` | Independent trials conflict | §4.15 |
| `uygulanamaz` | The field is undefined for this target (e.g. `x5c` in COSE) | B6 logic of §4.13 |
| `olculmedi` | No measurement could be made (only while `adaptor_gecersiz = 1` or in a `REF` row) | — |

Rules:
- The first four codes are the **"undetermined"** class of PR §4.15.
- If `Y_L4 = null`, its reason must be one of these four. The only exception is `olculmedi`, which may be used only with `adaptor_gecersiz = 1` or in a `REF` row. There is no "not applicable" for `Y_L4`: L4m or L4c applies to every valid target.
- Sensitivity (i)/(ii) applies only to these "undetermined" targets (PR §6.10).

## 3. Case record (`vakalar[]`, optional)

| Field | Type | Required | Meaning |
|---|---|---|---|
| `hedef_id` | string | yes | Must exist in `hedefler` |
| `vaka_id` | string | yes | Vector id of battery v1.1 (e.g. `T1K_both_valid`). The pair (`hedef_id`, `vaka_id`) is unique |
| `kol` (arm) | `K` \| `T` \| `diger` | yes | Control, treatment or outside the arms (e.g. the X5C, REQ families) |
| `uyum` (agreement) | binary \| null | yes | 1 = the observed decision equals the oracle, 0 = deviation |
| `belirsiz_neden` | §2.1 code \| null | yes if `uyum = null` | E.g. `kararsiz_3_tekrar` (unstable cell, PR §6.11) |

## 4. CSV format

**`hedefler.csv`**
- The header row contains the field names of §2; the order is free.
- `null` → empty cell. Binary → `0`/`1`.
- `belirsiz_nedenleri` → `field:code;field:code` (e.g. `Y_L4:kanit_kurali;B2:uygulanamaz`).
- `sema_surumu` and `veri_turu` are given as a comment on the first line of the file: `# sema_surumu=c3-istat-girdi/1.0; veri_turu=sentetik`.

**`vakalar.csv`**
- The columns of §3; the same rules.

## 5. Analysis sets (definitions applied by the scripts)

**Sets:**
- H_n = { tabaka ∈ {JOSE, SDJWT, COSE} }, n = |H_n|. Under PR §2B, n = 31 is expected; if different, a warning is given and the analysis continues.
- H_g = H_n \ { adaptor_gecersiz = 1 }.
- For every variable v, H_v = { h ∈ H_g : v(h) ≠ null }.

**n_eff (T1)** = |H_{Y_L4}| = n − adapter invalid − undetermined(Y_L4) (PR §6.3).

**Tests:**

| Test | Set | Variable | Method |
|---|---|---|---|
| T1 | H_{Y_L4} | X = Σ Y_L4 | Exact binomial, lower tail; c(n_eff), u = n_eff − c (Appendix A rule); n_eff < 20 ⇒ descriptive only |
| T2 | H_g ∩ {TK1, TK2} ∩ H_{F_K} ∩ H_{F_T} | b = #(F_K=0, F_T=1), c = #(F_K=1, F_T=0) | Exact McNemar, two-sided; b + c = 0 ⇒ p = 1 |
| T3 | H_g ∩ {SDJWT, JOSE} ∩ H_{F_K} ∩ H_{F_T} | PQ = [F_T = 1 ∧ F_K = 0]; rows SDJWT, JOSE | Fisher exact, two-sided. TK scope `yapilandirma.T3_TK_KAPSAMI` (default: all; see decision notes N-4) |
| T4 | H_g ∩ H_{L_duzeyi} ∩ H_{surum_8725bis_sonrasi} | [L ≥ 3]; rows after = 1, after = 0 | Fisher exact, two-sided |
| T5 | H_{D_soy} | X = Σ D_soy | Exact binomial, upper tail |

**Holm and effect sizes:**
- Holm is applied only to the family {T2, T3, T4, T5}; m = 4 is fixed. If there is no data, p = 1 is taken and the flag `veri_yok` is set.
- Effect sizes are computed according to PR §6.7:
  - T1 and T5: proportion + Wilson;
  - T2: paired difference (F_T − F_K) + Newcombe method 10;
  - T3 and T4: conditional MLE OR + conditional exact CI; difference + Newcombe method 10 (independent).

**Sensitivities (PR §6.10, §2B.9):**

| Code | Definition | Applied to test |
|---|---|---|
| (i) | targets with undetermined `Y_L4` counted as Y = 1 | T1 |
| (ii) | targets with undetermined `Y_L4` counted as Y = 0 | T1 |
| pilot | without `pilot = 1` | T1 |
| devir (delegation) | without `devralan = 1` | T1 and T2; descriptive, outside Holm |

**Cluster bootstrap (PR §6.9):**
- Unit: the target in `vakalar` (H_g only).
- Proportion: proportion of cases not agreeing with the oracle = Σ(1 − uyum) / Σ cases, over the cases with `uyum ≠ null`.
- Scope: all, `K`, `T`.
- Settings: B = 10,000; percentile CI (type 7); seed 20260927. Details: `FREEZE-INPUT.md`.

## 6. Validator errors (examples)

In these cases the analysis does **not start** (exit code 3):
- a missing required field, an undefined enum value, a duplicate `hedef_id`;
- a `null` without a written reason, or a reason written for a field whose value is not `null`;
- no `kontrol_etiketi` for a valid n target;
- a reason other than "undetermined" while `Y_L4 = null`;
- no `devraldigi_hedef` while `devralan = 1` (or present while `devralan = 0`);
- a conflict between the date and `surum_8725bis_sonrasi`;
- an inconsistency between `B4_satir` and `B4_ozel_kod`;
- an unknown `hedef_id` or a duplicate (`hedef_id`, `vaka_id`) in `vakalar`.
