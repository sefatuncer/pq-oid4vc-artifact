# Glossary

The study was carried out in Turkish. All documentation in this release is in English, but many
directory names, file names, script identifiers, data fields and data values are still Turkish. They
are embedded in recorded outputs (logs, manifests, hash lists, result tables) and in code, so they
were kept unchanged on purpose. This page translates them.

- Field names and field values of data files are explained in [`DATA-DICTIONARY.md`](DATA-DICTIONARY.md).
- Old top-level folder names and renamed documents are listed in [`PATHS.md`](PATHS.md).

Turkish letters are written without diacritics in most identifiers (`ç→c`, `ğ→g`, `ı→i`, `ö→o`,
`ş→s`, `ü→u`); for example `sonuc` is *sonuç* (result) and `kosum` is *koşum* (run).

## 1. Abbreviations used in the documents

| Abbreviation | Meaning |
|---|---|
| PR | Pre-registration (Turkish *ön kayıt*, ÖK). "PR §6.5" is section 6.5 of the pre-registration. The pre-registration document itself is not part of this release; scripts that parse it take its path as an argument or expect it at `00-on-kayit/ON-KAYIT-TASLAK.md` |
| PR anchor *n* | A git commit that fixed (anchored) a version of the pre-registration before the corresponding runs (Turkish *çapa*). Anchors 1–9 are listed in the documents with their commit ids |
| Amendment *n* | Numbered change to the pre-registration (Turkish *Değişiklik*) |
| Step *n* | Step of the study plan (Turkish *Adım*). See the step table in the root `README.md` |
| task *n* | Sub-task of a step (Turkish *görev*) |
| item *n* | Numbered item of a pre-registration section (Turkish *madde*, abbreviated *m.*). "PR §2H items 7–10" |
| work plan | The internal step-by-step plan (Turkish *İŞ-PLANI*, `IS-PLANI.md`). Not part of this release; references such as "work plan 6.6" are kept for traceability |
| decision notes | Notes that list interpretation questions and the decisions taken on them (Turkish *KARAR-NOTLARI*; earlier *NOTLAR*) |
| KAT | Known-answer test (Turkish *bilinen-cevap testi*) |
| KAT-SPEC | The known-answer-test specification written before Step 6 (internal; quoted in `models/known-answer-tests/kor-beklenen/GIRDI/KAT-BLIND-INPUT.md`) |
| N-version | Independent derivation of the same expected values by two separate sessions (Turkish *N-sürüm*) |
| design-stage pilots (B) | Feasibility pilots P1–P5 that were run while the study was designed (pilot set "B"). Their files are reproduced in `tools/regression-tests/` |
| [Y] | Own calculation (Turkish *yazarın hesabı*) |
| ✓ | Checked against the primary source |

## 2. Code families used in the study

Several families share a letter. The documents always qualify them.

| Code | Meaning |
|---|---|
| C1–C3 | The three contributions: C1 proven abstraction (minimal post-quantum sets), C2 expectation-conveyance mechanisms, C3 library capability measurement |
| H0–H6 | Hypotheses. H0 sanity check, H1 channel substitution, H2/H2′ time phase, H3 expectation conveyance, H4 limits of published ("root-first") orderings, H5 aggregate-and-forge, H6 expressiveness of library APIs |
| G1–G5 | Security goals: G1 credential (claims) unforgeability, G2 presentation unforgeability, G3 status soundness, G4 request/relying-party authenticity, G5 no classical acceptance after migration (three forms: G5-untimed, G5-timed, G5-migrated, the last one including first contact) |
| A01–A13 | The 13 artefacts of the threat model (A01 LOTL … A13 transport TLS/WebPKI), see `threat-model/THREAT-MODEL.md` |
| T001–T400 | Rows of the traceability matrix (`traceability/izlenebilirlik.csv`) |
| R1–R7 | Tamarin rule schemata: R1 chain, R2 downgrade, R3 channel, R4 WSCD device key, R5 trust anchor, R6 time window, R7 monotone expectation. Not to be confused with risk codes R1–R33 of the internal work plan |
| M-a … M-h | Expectation-conveyance mechanism classes; M-b0 is the unsigned-request baseline and M-e′ a variant of M-e; M-f is the proposed mechanism |
| S0–S8 | Baseline strategies for the comparison step (not the attacker classes S1–S3 of the threat model) |
| S1–S3 | Attacker classes of the threat model |
| M1–M5 | Baseline comparison metrics (not the metamorphic relations MR1–MR4) |
| MR1–MR4 | Metamorphic relations used on the test battery |
| P0–P4 | Verifier multi-signature policies (PR §4.8). Not to be confused with the design-stage pilots P1–P5 |
| L0–L5 | Library capability levels (PR §4.13); L4m = L4 with multi-signature (General JSON) form, L4c = L4 with compact form (two issuers) |
| K1–K11, V+, V− | Cases of the C3 test battery (PR §6.5); V± is the adapter validity gate |
| TK1–TK3 | Treatment classes of a target library (Turkish *tedavi kolu/sınıfı*): TK1 native (the library verifies the PQ signature itself), TK2 plug-in (the study's PQ verifier is plugged into the public API; the policy layer stays the library's), TK3 unknown-algorithm (only the unknown-algorithm behaviour is observed) |
| T1–T5 | Statistical tests of PR §6.6 (not the treatment classes) |
| B1–B6 | Pre-registered behaviour flags of the C3 measurement (for example B5 multi-signature semantics, B6 format not supported) |
| Φ1–Φ3 (`f1`–`f3`) | Coexistence phases of classical and post-quantum artefacts |
| τ (`tau`) | Time a cryptographically relevant quantum computer (CRQC) needs per key; regimes `hizli` (fast), `orta` (medium), `yavas` (slow) |
| V1–V3 | Key modes (validity windows) of signing keys in the ASP model |
| D1′ | Primary configuration of the formal part (PR §2C), |Q| = 675 queries |
| A1–A5 | Ablations |
| Ö1–Ö12 | Decisions recorded in PR §2A (Amendment 1), for example Ö6 = four-valued oracle output and the reframing of H6 |
| İ1–İ7 | Human touch points of the study (authorship, notification, archive upload, submission, final reading, gate approvals) |
| N-*n*, N*n* | Numbered decision notes |
| B-*n*, B*n* | Numbered reasons for an `indeterminate` oracle decision |

## 3. Directory names

| Directory | English | Notes |
|---|---|---|
| `adaptorler` | adapters | old name of `experiment/runs/adapters/` (see `PATHS.md`) |
| `anahtarlar` | keys | test keys and test PKI; `ozel/` = private keys |
| `asp` | ASP (answer set programming) model | |
| `b-uyumlu` | B-compatible | vector file in the format of the design-stage pilot P3 |
| `betik`, `betikler` | script(s) | |
| `birlesik` | merged | merged oracle |
| `c3istat` | C3 statistics package | |
| `cikti`, `cikti-maven` | output (Maven output) | third-party build output of a target; not translated |
| `datalog` | Datalog counterpart of a Tamarin rule schema | |
| `dis-vektorler` | external test vectors | |
| `dnssec`, `x509`, `smime` | the three known-answer-test ecosystems | |
| `hedefler` | targets | one folder per target library |
| `_bilgi-<target>-…` | informational run | extra build of a target (for example HEAD instead of the release); not part of the sample |
| `h3_sadelestirme` | H3 simplification | |
| `ham` | raw | raw tool output |
| `imajlar` | images | language environment Dockerfiles |
| `iyi_bicim` | well-formedness | Tamarin well-formedness check output |
| `json` | JSON output of Tamarin runs | |
| `kanit` | evidence | |
| `kayit` | record, log | run records, Docker state snapshots |
| `kaynak` | source | |
| `kesif` | exploration | exploratory (not pre-registered as confirmatory) |
| `konteyner` | container | in-container installer scripts |
| `kor-beklenen` | blind expected values | blind N-version derivation of KAT expected values |
| `GIRDI` | input | the frozen input of the blind derivation |
| `kosu` | run | |
| `loglar` | logs | |
| `me_gocmus` | M-e migrated | copy of the M-e model used by the exploration run |
| `modeller` | models | |
| `nsurum` | N-version | comparison of the two derivations |
| `olgular` | facts | ASP fact files |
| `ornekler` | samples, instances | generated model instances; not translated |
| `ornek_analiz*`, `ornek_girdi` | sample analysis, sample input | statistics example on synthetic data |
| `ozel` | private | private keys |
| `pki` | test PKI | |
| `regresyon` | regression | |
| `secim` | selection | sample selection of the technical gate |
| `sentetik-testler` | synthetic tests | |
| `servis` | service | local PQ verification service |
| `sonuc`, `sonuclar`, `sonuc_v2` | result(s), results of the corrected run (v2) | |
| `sorgular` | queries | ASP query catalogue and driver |
| `tamarin_datalog` | Tamarin-to-Datalog regression instances | |
| `tamarin_ham` | raw Tamarin output | |
| `tani` | diagnosis | diagnostic run |
| `tau_israf` | τ-waste | instances for wasted post-quantum effort under τ |
| `teknik-kapi` | technical gate | |
| `test1`, `test2` | first and second test run | |
| `testler` | tests | |
| `uretec` | generator | Python package of the vector generator |
| `uretilen` | generated | generated ProVerif models |
| `vektorler` | vectors | test vector sets v1, v1.1, v1.2, v1.3 |
| `veri` | data | (only `experiment/statistics/sentetik-testler/veri/`; the top-level `veri/` is now `data/`) |
| `yeniden_kosum_0110` | re-run of 01.10.2026 | |
| `yetenek` | capability | capability probe of a language environment |

## 4. Words in file names

| Word | English |
|---|---|
| `adim`, `ADIM` | step (`ADIM06` = Step 6) |
| `alinti`, `alintilar` | quote, quotes |
| `alinti_dogrula`, `alinti_denetimi` | verify quotes, quote audit |
| `analiz` | analysis |
| `artefakt`, `artefaktlar` | artefact(s) |
| `asgari` | minimal |
| `bayraklar`, `elle_bayraklar` | flags, manual flags |
| `beklenen`, `beklenti` | expected, expectation |
| `beklenmeyen` | unexpected |
| `birincil` | primary |
| `bootstrap` | (cluster) bootstrap |
| `boyut`, `boyutlar`, `boyutlari` | size(s) |
| `calistir` | run (script entry point) |
| `calistir_log`, `calistir_stdout` | run log, run standard output |
| `capraz`, `capraz_kontrol` | cross, cross-check |
| `cekirdek` | core |
| `cerceve`, `CERCEVE` | frame (sampling frame) |
| `cevir`, `ceviri_plani` | translate (ASP frame row → Tamarin instance), translation plan |
| `degerlendir`, `degerlendirme` | evaluate, evaluation |
| `degisiklikler` | changes |
| `derle`, `derleme-sonuc` | build, build results |
| `destek_kanitlari` | support evidence |
| `disa_aktar`, `disa_aktarim_ozeti` | export, export summary |
| `dogrula`, `dogrulama` | verify, verification |
| `duman-testi` | smoke test |
| `ek`, `ek_yuk` | extra / annex, overhead |
| `esleme`, `ESLEME` | mapping |
| `etiket_coz` | resolve tag |
| `gerekce` | rationale |
| `hazirlik` | preparation |
| `hedef`, `hedef_listesi` | target, target list |
| `hucre`, `hucreler` | cell(s) |
| `ic_kosum` | in-container run |
| `ice_aktar` | import (import smoke test of a target) |
| `indir`, `indirme_kaydi` | download, download log |
| `insa`, `insa_denetimi` | construction, construction audit |
| `isler` | jobs (job list) |
| `izler` | traces (attack traces) |
| `izlenebilirlik` | traceability |
| `kapsama_tablolari` | coverage tables |
| `karar`, `karar_ozet`, `karar_uret` | decision, decision summary, generate decisions |
| `karsilastir`, `karsilastirma` | compare, comparison |
| `katalog` | catalogue |
| `kenarlar` | edges |
| `kesin` | exact (exact tests) |
| `kopru` | bridge |
| `kos`, `kosum`, `kosu` | run |
| `kontrol`, `KontrolYukle` | check, check-load |
| `korpus` | corpus |
| `kur`, `kur-maven` | install (with Maven) |
| `maddeler` | clauses (normative items) |
| `matris_olustur` | build matrix |
| `metrikler` | metrics |
| `mutasyon`, `mutasyonlar` | mutation(s) |
| `on`, `on_kayit` | pre-, pre-registration |
| `once`, `sonra`, `baslangic` | before, after, start (Docker state snapshots) |
| `ortak` | common, shared |
| `ozet` | summary |
| `parametreler` | parameters |
| `pencereler` | windows (time windows) |
| `pqdogrula` | PQ verify (service name) |
| `rapor`, `rapor_sayilari` | report, report numbers |
| `referans` | reference implementation |
| `saglik` | sanity (sanity lemma) |
| `secim` | selection |
| `sema` | schema |
| `sentetik_uret` | generate synthetic data |
| `sira`, `siralar` | order(s) |
| `sorgu` | query |
| `stratejiler`, `stratejiler_taslak` | strategies, strategies draft |
| `surum`, `surum_dayanak`, `surum_ozet` | version, version evidence, version summary |
| `tablolar` | tables |
| `tarama`, `tarama_kararlari` | screening, screening decisions |
| `tasiyicilar` | carriers (expectation carriers) |
| `terim_sayimi` | term count |
| `topla`, `topla_sonuc`, `topla_kayit` | collect, collect results, collection log |
| `tumunu_calistir` | run everything |
| `turet`, `turet_karar` | derive, derive decisions |
| `uclu_rastgele` | three-way random (check) |
| `uret` | generate |
| `uyarilar` | warnings |
| `uyum` | agreement |
| `varyant`, `varyantlar`, `varyant_ozeti` | variant(s), variant summary |
| `yanyana` | side by side |
| `yapi` | structure |
| `yapilandirma` | configuration |
| `yayimlanmis_ornekler` | published examples |
| `yeniden_12g` | re-run with 12 GB memory |

Test script prefixes in `experiment/signer/testler/` and `experiment/vector-generator/testler/`:
`t01_dis_vektorler` external vectors, `t02_openssl_capraz` OpenSSL cross-verification,
`t03_negatif` negative tests, `t04_boyutlar` sizes, `t05_servis` service, `t10_oz_dogrulama`
self-verification, `t10_cose` COSE self-verification, `t11_esleme_denetim` battery-mapping audit,
`t12_cose` COSE external vectors. In `experiment/statistics/sentetik-testler/`: `test_ek_a` PR
Appendix A values, `test_iki_uygulama` two independent implementations, `test_sema` input schema,
`test_sinir` boundary cases, `test_uctan_uca` end to end, `test_yayimlanmis` published values,
`ornek_veri_uret` generate the synthetic example input.

## 5. Identifier prefixes

| Prefix | Meaning | Where |
|---|---|---|
| `T001`… | traceability row | `traceability/izlenebilirlik.csv` |
| `JOSE-nnn`, `SDJWT-nnn`, `COSE-nnn`, `REF-nnn` | C3 target library ids per stratum (REF = reference verifier) | `experiment/inventory/`, `experiment/environments/hedefler/` |
| `CERCEVE-nnnnnn` | row of the ASP sampling frame | `models/asp/sampling/cerceve.jsonl` |
| `KESIF_2X2-nnnnnn` | row of the exploratory 2×2 grid | `models/asp/sampling/kesif_2x2.jsonl` |
| `K1-nn`, `K2a-nn` … `K2d-nn`, `K3a-…`, `o1`…`o12`, `V1`…`V6` | known-answer-test cells (KAT-1 DNSSEC, KAT-2 X.509 sub-tables a–d, KAT-3 S/MIME) | `models/known-answer-tests/*/hucreler.tsv` |
| `MUTnn` | known-answer-test mutation | `models/known-answer-tests/*/mutasyonlar.tsv` |
| `birincil|g1|f1|hizli|taze|p0` | ASP query id: group \| goal \| phase \| τ \| anchor \| policy | `models/asp/sorgular/sonuc/*.json` |
| `M_…`, `P_…`, `E_…`, `X_…` | Tamarin variant names: mutant, protected (all post-quantum), extra/exploratory, alternative-path | `models/tamarin/betik/varyantlar.tsv` |
| `pq-a02-…`, `pq-a03-…`, `pq-a09-…`, `a10-<target>` | Docker image and container names by step (a02 = Step 2, a09 = Step 9, a10 = Step 10) | Dockerfiles and scripts |

Vector id prefixes (`T1K_…`, `CMP…`, `X5C…`, `COSE-…` and so on) are listed in
[`DATA-DICTIONARY.md`](DATA-DICTIONARY.md#vector-ids).

## 6. Technical terms

| Turkish term | English used in this release |
|---|---|
| aktarılan (kanal) | conveyed: the presenting party brings the object (credential, `x5c`, KB-JWT, request object) |
| çekilen (kanal) | fetched: the verifier or wallet fetches the object from an authoritative source (LOTL, TL/LoTE, status list, metadata) |
| sabitlenmiş / önbellekli (kanal) | pinned / cached (out-of-band or cached objects such as OJEU digests and the WebPKI root store) |
| asgari küme | minimal set (minimal set of artefacts that must be post-quantum) |
| beklenti taşıma / taşıyıcı | expectation conveyance / expectation carrier |
| bir-eksik | one-short (a minimal set with one element removed) |
| birincil / ikincil | primary / secondary |
| bilimsel kapı / teknik kapı | scientific gate / technical gate |
| çapa | anchor (pre-registration anchor commit); also trust anchor (güven çapası) |
| dondurma | freeze (of the pre-registration and its inputs) |
| downgrade (sürüm düşürme) | downgrade |
| G5 biçimi | form of goal G5 (untimed, timed, migrated) |
| güven çapası | trust anchor |
| ihraççı | issuer |
| iyi biçimlilik | well-formedness |
| kanıt kuralı | evidence rule (PR §4.14, for "not expressible" verdicts) |
| kapsam ekonomisi | scope economy (reducing the set of runs while keeping coverage) |
| kesim kümesi | cut set |
| keşifsel | exploratory |
| kol | arm (control or treatment arm) |
| kontrol kolu / tedavi kolu | control arm / treatment arm |
| kör türetme | blind derivation |
| merdiven (sonlanmama merdiveni) | ladder (non-termination ladder for Tamarin runs) |
| mutasyon skoru | mutation score |
| ön / ÖN (sonuç) | preliminary (result) |
| örneklem çerçevesi | sampling frame |
| sağlık lemması | sanity lemma |
| soyma | stripping (removal of a signature) |
| sonuç görüldükten sonra | after results were seen (label for post-hoc changes) |
| taban | baseline |
| tabaka | stratum |
| tekdüze beklenti | monotone expectation |
| topla-sahtele | aggregate-and-forge |
| vaka | case |
| varlık başına beklenti | per-entity expectation |
| yürütme / koşum | run |
