# Data dictionary

Data files (`.json`, `.jsonl`, `.csv`, `.tsv`, `.txt`, `.log`, `.meta`) were not translated: their
field names and values are read by scripts and are fixed by hash lists and pre-registration
anchors. This page explains the Turkish field names and values. Directory and file-name words are
in [`GLOSSARY.md`](GLOSSARY.md).

Values that are already English (`verified`, `falsified`, `accept-hybrid`, `reject`, …) are only
listed where their meaning in this study needs a definition.

## 1. Common values

| Value | Meaning |
|---|---|
| `evet` / `hayir` (`hayır`), `EVET` / `HAYIR` | yes / no |
| `var` / `yok` | present / absent |
| `basarili` / `basarisiz` | succeeded / failed |
| `gecerli` / `gecersiz` | valid / invalid |
| `bozuk` | corrupted (for example `bozuk: bayt 5, bit 0` = byte 5, bit 0 flipped) |
| `belirsiz` | undetermined |
| `uygulanamaz` | not applicable |
| `temiz` | clean (no Tamarin well-formedness warning) |
| `ESIT` / `FARKLI` | equal / different |
| `null`, empty cell | no value (the reason is given in a separate field where the schema requires it) |
| `sure_s`, `sure_ms` | duration in seconds / milliseconds |
| `bellek_MiB` | peak memory in MiB |
| `adim` | Tamarin proof steps (in Tamarin tables); otherwise the study step |
| `not`, `aciklama` | note, description (free Turkish text) |
| `dayanak` | basis: the normative clause or source that supports a value |

## 2. C3 runs (`experiment/runs/`)

The adapter contract is `experiment/oracle/oracle-A/adapter-contract.md` (contract 1.0); the call
format is fixed in `experiment/runs/RUNNER.md`.

### 2.1 Job list (`jobs-v1.3.jsonl`, `jobs-prefreeze-v1.3.jsonl` and the v1.4 counterparts)

One JSON object per line. `jobs-prefreeze-*` = the V± jobs that may run before the pre-registration
freeze (formerly `isler.jsonl` and `isler_dondurma_oncesi_V.jsonl`; `isler` = jobs).

| Field | Meaning |
|---|---|
| `vektor_id` | vector id (section 4) |
| `politika` | policy configuration (section 3) |
| `kol` | arm (section 3.2) |
| `dosya` | vector file, relative to the vector set |
| `serilestirme` | serialization (section 4.2) |
| `artefakt` | artefact type (section 4.2) |
| `algler` | algorithms of the signatures, `;`-separated |

### 2.2 Adapter output (`outputs/<set>/<target>[.<run>].jsonl`)

| Field | Meaning |
|---|---|
| `sozlesme` | contract version (`adaptor-sozlesme/1.0`) |
| `hedef_id`, `hedef_surum`, `hedef_commit` | target id, version, commit |
| `imaj_ozeti` | image digest |
| `adaptor_sha256` | SHA-256 of the adapter code |
| `batarya`, `manifest_sha256` | battery version and manifest hash |
| `kosu` | run (`r1`, `r2`, `r3`; three repetitions in fresh containers) |
| `tarih_utc` | timestamp |
| `vektor_sha256` | hash of the vector file |
| `tk` | treatment class `TK1`/`TK2`/`TK3` |
| `sdjwtvc_surum` | SD-JWT VC draft version (`-13`, `-19`) |
| `kontrol_etiketi` | control label in the control arm (`EdDSA` or `Ed25519`) |
| `kullanilan_alg_etiketi` | `alg` label used for X |
| `anahtar_yolu` | key path (how the key was supplied, for example `JWKS`, `x5c`) |
| `api_yolu` | API call used |
| `sonuc_ham` | raw outcome (below) |
| `karar` | four-valued decision derived by the runner (below) |
| `hata_sinifi` | error class (below) |
| `hata_ozeti`, `hata_sha256` | first 200 characters of the error message and the hash of the full text |
| `dogrulanan_algoritmalar` | per signature: `sira` (position), `alg`, `sonuc` = `gecerli` (valid), `gecersiz` (invalid), `denenmedi` (not tried), `bilinmiyor` (unknown) |
| `pq_servis_cagrilari` | number of calls to the local PQ verification service (TK2 only) |
| `zaman_asimi` | timeout flag |
| `stdout_sha256`, `stderr_sha256` | hashes of the captured streams |

**`sonuc_ham` (raw outcome)**

| Value | Meaning |
|---|---|
| `kabul` | accept: the library accepted the object |
| `red` | reject: the library rejected the object |
| `istisna` | exception: the library threw an exception (mapped to a rejection with an error class) |
| `zaman-asimi` | timeout (60 s per vector) |
| `cokme` | crash |
| `uygulanamaz` | not applicable: the format is not supported by the documented API (flag B6, `hata_sinifi = bicim-desteklenmiyor`); decided in advance by API review |
| `ifade-edilemedi` | could not be expressed: the API cannot express the policy (for example a required set R) |

**`karar` (four-valued decision; also the oracle decisions)**

| Value | Meaning |
|---|---|
| `accept-hybrid` | accepted, and every acceptance path allowed by the configuration requires a valid post-quantum component (ML-DSA, or the ML-DSA component of a composite signature) |
| `accept-classical` | accepted, and validating the classical signature(s) alone is enough under the configuration; or the object has only classical signatures |
| `reject` | a conforming verifier must reject (MUST level) |
| `indeterminate` | the clauses and construction facts do not determine the decision (oracle); or timeout, crash or a result that differs between the three runs (measurement) |
| `uygulanamaz` | not applicable; excluded from the comparison |

**`hata_sinifi` (error class, closed list)**

| Value | Meaning |
|---|---|
| `imza-gecersiz` | invalid signature |
| `alg-desteklenmiyor` | algorithm not supported |
| `alg-izin-disi` | algorithm outside the allowed set |
| `alg-anahtar-uyusmazligi` | algorithm/key mismatch |
| `gerekli-kume-eksik` | required set missing |
| `anahtar-bulunamadi` | key not found |
| `zincir-gecersiz` | invalid certificate chain |
| `x5c-korumasiz` | unprotected `x5c` |
| `baslik-cakismasi` | header conflict |
| `crit`, `typ`, `zaman`, `kb`, `sd_hash` | failure in the `crit` or `typ` header, time checks (`zaman`), key binding (`kb`), `sd_hash` |
| `ayristirma` | parse error (counts as a rejection when the API exists) |
| `istisna-diger` | other exception (message summary recorded) |
| `zaman-asimi`, `cokme` | timeout, crash |
| `adaptor-hatasi` | adapter error |
| `bicim-desteklenmiyor` | format not supported (B6) |

## 3. Policies and arms

### 3.1 `politika` (policy configuration)

A = ES256 in every arm; X depends on the arm (section 3.2). W = allowed set, R = required set.
Definitions: `experiment/oracle/oracle-A/METHOD.md` §2 and `experiment/oracle/oracle-B/METHOD.md` §4.

| Code | Used by | W | R | Rule |
|---|---|---|---|---|
| `GEC` (*geçerli*, "valid") | Oracle A, runner | all supported algorithms | ∅ | single-signature objects only; adapter validity gate V± and plain validity baseline |
| `IZIN-A` (*izin*, "allow") | Oracle A, runner | {A} | ∅ | allow-list test L1/L2 |
| `IZIN-AX` | Oracle A, runner | {A, X} | ∅ | positive side of L1/L2; L3 (K10 must be rejected); old issuer of L4c |
| `L4` | both oracles, runner | {A, X} | {X} | the PR §6.5 policy: every present signature valid with an allowed algorithm and bound key, and one valid signature for every algorithm in R. Oracle A marks the extra-signature case K5 `indeterminate` when the strict and lenient readings differ |
| `L4-S` | Oracle A, runner | {A, X} | {X} | strict reading "S" (*sıkı*, P3/P1 semantics): every present signature must be in W and valid |
| `L4-Y` | Oracle A, runner | {A, X} | {X} | ignoring reading "Y" (*yok say*, "ignore"; R-only): signatures outside W are ignored; those inside W must be valid |
| `L4-YOL` (*yol*, "path") | Oracle A, runner | {A, X} | {X} | plus: every certificate signature on the `x5c` path must be post-quantum (X5C vectors only) |
| `P0` | both oracles, runner | {A, X} (Oracle B) / all supported (Oracle A) | ∅ | at least one valid signature |
| `P1` | Oracle A, runner | all supported | ∅ | all present signatures valid |
| `P2` | Oracle B | {A, X} | ∅ | all present signatures valid with key–algorithm binding (P1 ≡ P2 for conforming libraries) |
| `GEC@-19`, `L4@-19` | Oracle A, runner | as `GEC` / `L4` | | evaluated against SD-JWT VC draft -19 instead of -13 |
| `<code>|sdjwtvc=-13`, `<code>|sdjwtvc=-19` | Oracle B | as `<code>` | | the same policy with the SD-JWT VC draft version fixed explicitly |

### 3.2 `kol` (arm)

| Value | X | Meaning |
|---|---|---|
| `kontrol-EdDSA` | EdDSA | control arm |
| `kontrol-Ed25519` | Ed25519 | control arm with the RFC 9864 label (fallback rule A9) |
| `tedavi-ML-DSA-65` | ML-DSA-65 | treatment arm, pure post-quantum |
| `tedavi-composite` | ML-DSA-65-ES256 | treatment arm, composite |
| `klasik-taban` | | classical baseline |
| `kapsam-pq`, `kapsam-hibrit` | | scope vectors (post-quantum / hybrid) |
| `ortak` | | common to all arms; `ortak (L4c; iki tedavi kolu)` = common to the two treatment arms |
| `yok`, `null` | | no arm |

In the statistics input the arm is coded `K` (control), `T` (treatment) or `diger` (other).

## 4. Test vectors (`experiment/vector-generator/vektorler/`)

### 4.1 Vector ids {#vector-ids}

| Pattern | Meaning |
|---|---|
| family prefix `T`, `UNK`, `CMP`, `X5C`, `REQ`, `VC`, `VP`, `TSL`, `DPOP`, `CRIT` | v1 families: multi-signature JWS (T), unknown algorithms (UNK), composite (CMP), certificate chains (X5C), OID4VP request objects (REQ), credentials (VC), presentations (VP), status list tokens (TSL), DPoP proofs (DPOP), `crit` header (CRIT) |
| `K10…` | case K10 (algorithm/key mismatch); `K10K_alg-EdDSA_anahtar-ES256` = header `alg` EdDSA, key (`anahtar`) ES256 |
| `VPLUS_<alg>`, `VMINUS_<alg>` | adapter validity gate V+ (valid object) and V− (invalid object) for one algorithm |
| `COSE-…` | COSE counterpart (v1.3) of a JOSE case, for example `COSE-K1K_iki_gecerli` |
| `L4C-JOSE_eski_ES256`, `L4C-COSE_eski_ES256` | L4c "old issuer" (`eski` = old) vectors (v1.3) |
| letter after the case: `K`, `P`, `C` (for example `T1K`, `T1P`, `T1C`) | arm: control (EdDSA), post-quantum (ML-DSA-65), composite |
| suffix `-ED25519` | twin of a control vector labelled `Ed25519` instead of `EdDSA` |
| suffix `-SIRA-ters` | signature order reversed (`sıra ters`) |
| words in ids | `iki_gecerli` both valid, `X_bozuk` X corrupted, `X_soyuldu` X stripped, `yalniz_X` X only, `arti_kayitsiz` plus an unregistered algorithm, `gecerli_referans` valid reference, `ml_bileseni_bozuk` ML component corrupted, `ecdsa_bileseni_bozuk` ECDSA component corrupted, `x5chain_karisik` mixed chain, `x5chain_korumasiz` unprotected chain, `onozet` pre-hash, `ikili_ihrac` double issuance |

### 4.2 Manifest fields (`MANIFEST.json`, `MANIFEST.csv`)

| Field | Meaning |
|---|---|
| `id`, `dosya`, `sha256`, `bayt` | id, file, hash, size in bytes |
| `aile` | family |
| `artefakt` | artefact type: `jws-cekirdek` (plain JWS core), `sd-jwt-vc`, `sd-jwt-vc+kb`, `status-list-token`, `oid4vp-istek` (OID4VP request), `dpop`, `cose` |
| `serilestirme` | serialization: `compact`, `general` (JWS JSON), `sd-jwt-compact`, `sd-jwt-flattened`, `sd-jwt-general`, `COSE_Sign1`, `COSE_Sign`, `dcapi-json-parametre` (Digital Credentials API parameter), `oid4vci-toplu-yanit` (OID4VCI batch response) |
| `kol` | arm (section 3.2) |
| `senaryo` | scenario of the design document (a–d, M-b0) |
| `sdjwtvc_surum` | SD-JWT VC draft version |
| `sinanan` | what is tested: `basamak` (capability levels L0–L5), `plan_bayraklari` (plan flags), `ek_etiketler` (extra tags, for example `coklu-imza` multi-signature, `saglik-kontrolu(H0)` sanity check) |
| `dayanak` | specification clauses |
| `insa` | construction facts, **not** a verdict: per signature `sira`, `alg`, `alg_sinifi` (`klasik` classical / post-quantum / composite), `anahtar_rolu` (key role), `kid`, `insa` (`gecerli` or a description of the corruption); certificate chain and its class |
| `dogrulama_girdileri` | verification inputs: `jwks`, `kid`, trust anchors, `simdi` (verification time, Unix seconds), `anahtar_secimi` (how the key is selected), `alg_kid`, `kb_aud`, `kb_nonce` |
| `b_pilot_esi` | the matching vector of the design-stage pilot P3 |
| `dcapi_protokol` | Digital Credentials API protocol |
| `algler` | algorithms (CSV only) |
| top level: `surum`, `temel_surum`, `vektor_sayisi`, `yeni_dagilim`, `uyari`, `yedek_kural`, `kayitsiz_alg`, `eski_ihracci`, `anahtar_dizinleri`, `anahtar_sha256sums`, `v1_2_capalari` … | version, base version, number of vectors, distribution of new vectors, warning text, fallback rule (A9), unregistered algorithm name, old issuer (L4c), key directories, hashes of the key lists, hashes of the earlier sets ("anchors") |

Key files: `acik-jwks.json` public JWKS, `ozel/<role>.json` private JWK, `roller.json` roles,
`guven-capalari.pem` trust anchors, `bilesen-yeniden-kullanim-jwks.json` component-reuse JWKS.

## 5. Oracle decision tables (`experiment/oracle/`)

| File | Columns |
|---|---|
| `oracle-A/karar.tsv` | `vektor_id`, `politika`, `kol`, `sinif` (`birincil` primary / `ikincil` secondary row, PR §2G item 4), `vaka` (battery cases, for example `K1;MR1;MR2`), `karar`, `dayanak` (verbatim clause quotes with file and line), `not` |
| `oracle-B/karar.tsv` | `vektor_id`, `politika`, `kol`, `birincil_mi` (primary? `evet`/`hayır`), `karar`, `dayanak`, `not` |
| `oracle-A/maddeler.tsv` | clause register: `anahtar` (key), `kimlik` (traceability id), `belge` (document), `bolum` (section), `surum` (version), `url`, `dosya`, `satir` (line), `alinti` (quote) |
| `birlesik/karar_v13.tsv` | merged decision for battery v1.3: `vektor_id`, `politika`, `kol`, `karar`, `A`, `B` (the two oracle decisions; empty = no row), `kaynak` (source of the merged value) |

Merged `karar` adds two values:

| Value | Meaning |
|---|---|
| `B1-bayragi` | B1 flag: case K5 (extra signature with an unrecognised algorithm) carries no single oracle decision (PR §2H item 8) |
| `kol-bagimsiz` | arm-independent flag K8/K9: rows of the composite arm are not measured (PR §2H item 9) |

Merged `kaynak` values: `A=B` both agree; `A≠B` they disagree (→ `indeterminate`); `A|B` only one
of the readings applies; `tek-oracle` only one oracle has the row; `madde-8`, `madde-9` PR §2H
item 8/9; `COSE-esleme` COSE vector mapped to the JOSE case; `L4c-3` rule L4c-3 (old issuer).

`OZET.json` (summary): `satir` rows, `karar_dagilimi` decision distribution, `kaynak_dagilimi`
source distribution, `cose_esi_bulunamayan` COSE vectors without a JOSE twin, `A_sha256`/`B_sha256`
hashes of the two input tables.

## 6. Statistics (`experiment/statistics/`)

Input schema `c3-istat-girdi/1.0` (full definition in `experiment/statistics/SCHEMA.md`).

| Field | Meaning |
|---|---|
| `sema_surumu`, `veri_turu` (`sentetik` synthetic / `olcum` measurement), `aciklama` | schema version, data type, description |
| `hedefler[]` | one record per target: `hedef_id`, `tabaka` (stratum `JOSE`/`SDJWT`/`COSE`/`REF`), `adaptor_gecersiz` (adapter invalid), `tk_sinifi`, `l4_bicimi` (`L4m`/`L4c`), `kontrol_etiketi`, `Y_L4` (primary variable of H6), `L_duzeyi` (L level), `F_K`/`F_T` (deviation from the oracle in K1–K3 in the control/treatment arm), `D_soy` (stripped document accepted in the default configuration), `B1`…`B6` flags, `surum_8725bis_sonrasi` (released after 8725bis-10), `son_surum_tarihi`, `pilot`, `devralan` (delegates verification), `devraldigi_hedef`, `belirsiz_nedenleri` |
| `vakalar[]` | one record per case: `hedef_id`, `vaka_id`, `kol`, `uyum` (1 = agrees with the oracle), `belirsiz_neden` |
| `B1` values | `red` reject, `yok_sayma` ignore, `dogrulama_duser` verification falls through |
| `B5` values | `en_az_biri_gecerli` at least one valid, `mevcut_tumu_gecerli` all present valid, `gerekli_kume` required set, `diger` other |
| null reasons | `oracle_uyusmazligi` oracle disagreement, `kanit_kurali` evidence rule not met, `kararsiz_3_tekrar` not identical in three runs, `deneme_celiskisi` independent trials conflict, `uygulanamaz` not applicable, `olculmedi` not measured |

Output `sonuc.json`: `H6_hukmu` (H6 verdict; `BELIRSIZ` = undetermined), `T1`…`T5`,
`T1_duyarlilik` (sensitivity), `T2_devralan_haric` (T2 without delegating targets),
`TK3_tanimlayici` (TK3 descriptive), `holm`, `wilson`, `bootstrap`, `tanimlayici` (descriptives),
`orneklem` (sample), `girdi` (input), `arac` (tool versions and `betik_sha256`, the hashes of the
analysis scripts at run time), `iki_uygulama` (two-implementation comparison), `yapilandirma`
(configuration). `sonuc.md` is the same result as a Turkish report.

## 7. Formal models

### 7.1 ASP queries (`models/asp/sorgular/sonuc/`)

| Field | Meaning |
|---|---|
| `id` | `<group>|<goal>|<phase>|<tau>|<anchor>|<policy>`, for example `birincil|g1|f1|hizli|taze|p0` |
| `grup` | query group: `birincil` primary, `h1`, `h2`, `h4`, `h5`, `cab` (CA binding 2×2), `oat` (one-at-a-time sensitivity), `tau`, `a5`, `h` |
| `hedefler` | goals `g1`…`g4`, `tum` (all) |
| `degisen` | parameters that differ from the primary configuration |
| `etiket` | label |
| `kumeler`, `n` | minimal sets and their number (`n = 0` → UNSAT) |
| `min_pq` | smallest number of post-quantum nodes |
| `bilgi` | solver statistics (`ground_s`, `solve_s`) |
| `ozet` | group summary: `sorgu` queries, `sat`, `unsat`, `duvar_s` wall time, `toplam_asgari_kume` total minimal sets, `en_uzun` longest query |

Parameter values: phase `f1`–`f3` (Φ1–Φ3); τ `hizli` fast, `orta` medium, `yavas` slow; anchor
`taze` fresh, `sabit` pinned, `onbellek` cached; policy `p0`–`p4`. Decision nodes `a01`…`a13`,
`a09a`/`a09b`, `ecrl`, `ejvi`, `eas`; `tasi(C,X)` = carrier C conveys the expectation for entity X.

`analiz/birincil.csv`: `hedef`, `faz`, `tau`, `capa`, `politika`, `n_asgari` (number of minimal
sets), `min_dugum` (fewest nodes), `min_m2_agirlikli` (minimum under metric M2 weights),
`gerekli_dugumler` (nodes in every minimal set), `asgari_kumeler` (the sets).
`z3/sonuc/uyum_*.csv`: `asp_n`, `z3_n`, `esit` (equal), `z3_s`, `cegar` (counter-example rounds).
`analiz/r6_esleme.csv`: R6 window-class mapping: `kip` key mode (`uzun` long-lived, `gunluk` daily,
`gecici` ephemeral), `omur_s` lifetime, `r6_sinif` (R6 class; `TASIMA_KORUR` transport protects,
`UZUN_OTESI` beyond long), `asp_imza_anahtari_klasik_kalabilir` (signing key may stay classical),
`asp_kimlik_pq_gerekli` (identity must be post-quantum), `r6_tahmini` (R6 prediction), `uyum`.

Channel values (`kanal`): `aktarilan` conveyed, `cekilen` fetched, `sabitlenmis` pinned,
`sunan_uc` the presenter's own endpoint, `yalniz_tasima` transport only, `kimliksiz` unauthenticated,
`belirsiz` undetermined (traceability only).

### 7.2 Sampling frame (`models/asp/sampling/`)

Row fields (full definition in `models/asp/sampling/SCHEMA.md`): `satir_id`, `kaynak` (source),
`hucre_id`/`hucre` (cell), `hedef`, `tur` (row type: `asgari` minimal set, `bir-eksik` one-short,
`birincil-kume` primary set), `kume.pq_dugumler` (post-quantum nodes), `kume.tasiyicilar`
(carriers), `asgari_no`, `kaynaklar`, `asp_tahmini` (ASP prediction), `ihlal_edilen` (violated
goals), `tanik_sahte_artefaktlar` (witness: forgeable artefacts), `alt_cizge` (sub-graph),
`tamarin` (template and flag mapping).

### 7.3 Tamarin results (`models/tamarin/sonuc/`, `models/mechanisms/sonuc/`, `models/sampling/teknik-kapi/`)

| Column | Meaning |
|---|---|
| `kural` | rule schema (R1–R7, R6h5, R7h, R7hx) or mechanism (M-a … M-h) |
| `varyant` | variant name |
| `rol` | role of the variant: `korumali` protected, `mutant:<what became classical>`; in the mechanism tables `mekanizma` mechanism, `kosul` condition, `tasiyici` carrier, `ablasyon` ablation, `3a`/`3b` task 3a/3b rows |
| `dosya`, `bayraklar` | model file and `-D` flags |
| `lemma` | lemma |
| `tur` | lemma type: `saglik` sanity, `guvenlik` security, `mutasyon` mutation, `ek-sinir` extra boundary, `bilgi` information |
| `sonuc`, `gozlenen`, `beklenen` | result, observed, expected (`verified`/`falsified`; in the mechanism tables `V`/`F`) |
| `uyum` | observed = expected |
| `G_beklenen` | expected value of the security goal: `V` verified, `F` falsified, `-` none |
| `merdiven`, `merdiven_basamagi` | rung of the non-termination ladder that produced the result (1 = first rung) |
| `iyi_bicimlilik` | well-formedness (`temiz` = no warning) |
| `kirilan`, `kirilan_anahtarlar` | keys broken in the attack trace |
| `kurallar`, `iz_protokol_kurallari` | protocol rules in the attack trace |
| `saglik_verified`, `lemma_sayisi`, `max_sure_s`, `max_bellek_MiB`, `merdiven_max`, `hepsi_beklenen_gibi` | variant summary: sanity lemmas verified, number of lemmas, maxima, all as expected |
| `datalog_ihlal`, `datalog_forgeable`, `datalog_tahmini`, `naive_tahmin`, `naive_uyum` | Datalog counterpart: violation, forgeable artefacts, prediction; prediction of the naive reading and its agreement |
| `asp_tahmini`, `tamarin_hukmu` | (technical gate) ASP prediction, Tamarin verdict |
| `satir_id` | frame row id |

### 7.4 Known-answer tests (`models/known-answer-tests/`)

| Column | Meaning |
|---|---|
| `kosu` | run id (`K1-01.asp`, `K1-01.tam`, `MUT01.K1-04.asp`) |
| `hucre`, `sutun` | cell and column of the KAT table (`ASP`, `Tamarin:<lemma>`, `decision(...)`) |
| `beklenen`, `gozlenen`, `uyum` | expected, observed, agreement |
| `tanik` | witness atoms from ASP (`sahte` forged, `kirilir` broken, `kirilir_alt` broken below, `klasik_alt` classical below, `pq`, `beklenir` expected, `geri_alinir` revoked) |
| `mutasyon`, `temel`, `dondu` | mutation, base cell, flipped (`EVET` when the mutation changed the verdict as expected) |
| `lemma_ham_sonucu`, `meta`, `iyi_bicim`, `executable`, `imaj` | raw lemma result, run metadata, well-formed, result of the `executable` sanity lemma, image digest |

ASP verdict values: `SALDIRI` attack exists, `YOK` no attack. `BEKLENEN-KOR.tsv` (blind expected
values): `kat`, `hucre`, `turetilen_sutun` (derived column), `deger` (value), `kaynak` (source),
`alinti` (quote), `satir` (lines). `nsurum/kat_nsurum.tsv` compares the value of the first
derivation (column `ilk_ajan`) with the blind derivation (column `kor_ajan`); `durum` = `ESIT`
equal, `FARKLI` different, `KOR-BELIRSIZ` undetermined in the blind derivation, `YALNIZ-ILK` /
`YALNIZ-KOR` present only in one of them.

`KAT_OZET.json`: `kat`, `karar_Vd` (verdict of acceptance criterion V-d), `kosullar` (conditions),
`sayilar` (counts), `mutasyonlar`, `belirsiz_ya_da_gecersiz` (undetermined or invalid),
`executable_olmayan` (not executable), `alinti_bulundu` (quotes found), `asp_tamarin_uyumsuz`,
`asp_uyumsuz`, `tamarin_uyumsuz` (disagreements), `ek_duyarlilik_kapi_degil` (extra sensitivity,
not a gate value). Verdicts `GEÇTİ` passed, `KALDI` failed.

## 8. Target inventory and environments

| File | Columns |
|---|---|
| `experiment/inventory/CERCEVE.csv` (frame) | `tabaka` stratum, `ad` name, `dil` language, `dil_grubu` language group, `paket_ekosistemi` package ecosystem, `paket_adi` package name, `depo_url` repository, `alt_dizin` sub-directory, `kaynak` source, `yildiz` stars, `son_commit`(`_sha`) last commit, `son_surum`(`_tarihi`) last release (date), `lisans` licence, `aylik_indirme` monthly downloads, `toplam_indirme` total downloads, `bagimli_paket`/`bagimli_depo` dependent packages/repositories, `arsiv` archived, `pop_puani` popularity score, `p_*` percentile components, `jwtio_*` jwt.io support flags |
| `experiment/inventory/TARAMA.csv` (screening) | `karar`: `aday` candidate, `ilgisiz` irrelevant, `taban-alti` below baseline, `uygulama` application, `yinelenen` duplicate, `belge` document, `cuzdan` wallet, `kapsam-disi-mdoc` out of scope (mdoc), `ihracci` issuer |
| `experiment/inventory/SECIM.csv` (selection) | `uygun_E*`, `karar_E*`, `neden_E*` = eligible, decision, reason under threshold option E1–E5; decisions `SECILDI` selected, `YEDEK` reserve, `DISLANDI` excluded, `uygun-disarida` eligible but outside the quota; reasons cite the criteria K1–K8 |
| `experiment/environments/derleme-sonuc.csv` (build results) | `surum` version, `commit`, `paket_ozeti` package digest, `imaj` image, `sonuc` result, `yedek_mi` is a reserve, `yerine_gectigi_id` replaces |
| `experiment/environments/kayit/<target>.kosu.json` | run record: `imaj`, `imaj_id`, `baslangic` start, `sure_s`, `cikis_kodu` exit code |
| `experiment/environments/kayit/*.csv` | `degisiklikler` target changes (`dusen_id` dropped, `yedek_id` reserve, `neden` reason, `kural_kolu` rule branch, `gerekce` rationale); `hedef_listesi` target list; `surum_commit`, `surum_dayanak`, `surum_ozet` version/commit evidence (`etiket` tag, `etiket_commit`, `kurulan_commit` installed commit, `cerceve_head` frame HEAD, `durum` status) |
| `experiment/environments/hedefler/<target>/cikti/sonuc.tsv` | key/value record written by the install script (`yaz` = write): `kilit_dosyasi` lock file, `kilit_sha256`, `paket_ozeti`, `bagimlilik_sayisi` dependency count, `not` |

## 9. Corpus and traceability

| File | Columns |
|---|---|
| `spec-corpus/MANIFEST.csv` | `id`, `baslik` title, `surum_tarih` version and date, `durum` status (`RFC`, `final`, `taslak` draft, `rehber` guidance), `url`, `erisim_utc` access time, `sha256_orijinal` hash of the downloaded file, `sha256_metin` hash of the extracted text, `boyut_bayt` size, `not` |
| `traceability/izlenebilirlik.csv` | `id` (T001…), `belge_id` document, `bolum` section, `birebir_alinti` verbatim quote, `anahtar_sozcuk` normative keyword (`bilgi` = informative), `artefakt` (A01–A13 or `genel` general), `imzalayan_rol` signer role, `algoritma_kosulu` algorithm condition, `kanal` channel, `hedef` goals, `kategori`, `not` |

Traceability categories: `guven-capasi` trust anchor, `gecerlilik` validity, `tazelik` freshness,
`tl-lote` trusted list / LoTE, `alg-muzakere` algorithm negotiation, `anahtar-baglama` key binding,
`downgrade`, `x5c`, `durum-listesi` status list, `kanitlama` attestation, `istek-imzasi` request
signature, `dpop`, `diger` other.
