# Freeze input — `experiment/statistics/` (C3 / H6 statistics scripts)

**Prepared by:** the statistics work (Step 9, task 9) · **Date:** 25.09.2026 · **Tool:** `c3istat` 1.0.0.

**Status:** validated with synthetic data only. No target library was touched; no real measurement data was used.

**Basis:** PR `00-on-kayit/ON-KAYIT-TASLAK.md` draft v0.6 (anchor 5 `facbf26`): §2B, §2D-A, §2E, §3.7, §6, Appendix A, Appendix C.

**Open decisions:** the interpretations that the maintainers must decide before the freeze are in `DECISION-NOTES.md` N-1…N-12. These decisions may change the constants in `scripts/c3istat/yapilandirma.py`. If they change, the tests are re-run and the digests in this file are renewed.

## 1. Files to be frozen and their SHA-256

Source: `SHA256SUMS`; produced by step 4 of `run_all.sh`. To verify, run `sha256sum -c SHA256SUMS` in this folder.

SHA-256 of the file `SHA256SUMS` itself: `513ac318770c2f7199fd878d4a6eb9fff8ec2cfcf01adeb6ccabec8e4f06f370`

(The values and file names below are those of 25.09.2026, before the files were translated and renamed for this release; the current list is `SHA256SUMS`. `docs/INTEGRITY.md` maps the old values to the new ones and `docs/PATHS.tsv` the old names: `betikler/` is now `scripts/`, `sentetik-testler/` `synthetic-tests/`, `veri/` `data/`, `kaynak/` `sources/`, `tumunu_calistir.sh` `run_all.sh`.)

| File | SHA-256 |
|---|---|
| `Dockerfile` | `ce1c006cc496945af95275c8ed4fb9dec2bed5c5c5341b24b8f869b601a778c3` |
| `tumunu_calistir.sh` | `65df0818d2a54fcf3d7c6ea981f287a98f4d4b636a661c4c0a0690bf51449d0d` |
| `SEMA.md` (now `SCHEMA.md`) | `92bb18b74592a517df32c079f67b7457628295494fd28098d9f0bb001421ca5c` |
| `.dockerignore` | `0576991d5e27469f781a4128b2eea9a6bdfad56d5e808177560390668356d5e2` |
| `betikler/requirements.txt` | `3cd6369bbf144f740cc1b82ec8d355b522c9dea8698b1266f34e880da2c54c7f` |
| `betikler/c3istat/__init__.py` | `809b210e9e26e0747a7e326c375a087c9d8de5f398cc3aacebda8d040f42684a` |
| `betikler/c3istat/__main__.py` | `6990410d729888995e6463cd1c6d14867302cdbcc80218f50201274f8479c6ff` |
| `betikler/c3istat/analiz.py` | `39f206acd30dfe5be758d1ebcf5e4d8622cfb30b0be1b92d996452620a803ccf` |
| `betikler/c3istat/bootstrap.py` | `df51f9a55a7b2889acc8603e0ecd4495de48fdbb6c508f09d2da929444f9db74` |
| `betikler/c3istat/karsilastir.py` | `5378604763427c160916e97908b15e3975c67f092a7b997215b31ea54dae37c5` |
| `betikler/c3istat/kesin.py` | `e5d6ac2fc76bc29971090898f067d9f66995b7c26598603e433376e20bbf7be0` |
| `betikler/c3istat/rapor.py` | `7de41aa0be63011f5bdfd9f332349308ddc97d021a8a73ead182d7230a2e9738` |
| `betikler/c3istat/referans.py` | `537386516291b9d4a52de38b5f058a26df168f46964512e9767cefe1f5c0283e` |
| `betikler/c3istat/sema.py` | `f7221f182c16a0bafed020691f3bd8bae6f3741c930bf02c1a871f33096a6f22` |
| `betikler/c3istat/yapilandirma.py` | `b0b980421e4cf6ae34c88309ebe261f3565de2f50ea8bac04b00c56e09339abc` |
| `sentetik-testler/_ortak.py` | `caa11f84d8e1209bf6753bc215a20fa40b5130957c49e712ce8ab8a86080f8b6` |
| `sentetik-testler/calistir.py` | `276520703822656239783a63d2979129e20ecfae241f5ec24713a7fb5e3d7859` |
| `sentetik-testler/ornek_veri_uret.py` | `1af397ed60147982e687568ce2a1d6db003a56c0b117c2415dc6f70bb50eec79` |
| `sentetik-testler/test_bootstrap.py` | `d136725937d2d9301be2f37f11cc130410b1e187b3dc4d61ada530336a131b4a` |
| `sentetik-testler/test_ek_a.py` | `59a3f9a6df742de3dbcd3cb4bf12f45329764a34f5731ce9e60dda52e209db9e` |
| `sentetik-testler/test_iki_uygulama.py` | `1854af21c8ccf1d4544ec5df72b6c344001b586b3e9f113844b086e7444b3533` |
| `sentetik-testler/test_sema.py` | `c5dca3eccb4ecdc3d817b56016e7794381ea7c9512563ececaf53e54d993efbf` |
| `sentetik-testler/test_sinir.py` | `6a66788c8012f4139906c3cbb85143b342180c236dbe30add9c593273fcb697d` |
| `sentetik-testler/test_uctan_uca.py` | `e9539f26d0d3596658ceced4888db3268e5a4a61a847a081686dfdcc270a246a` |
| `sentetik-testler/test_yayimlanmis.py` | `bec0e449986879ba36ac77a7351c8a4d8635f819ff6e0342428b239901455d80` |
| `sentetik-testler/veri/ornek_n31_sentetik.json` | `0420f58d7221281f8fb96254394f2f66b7f230e45178332fcb24d24ad52ff57a` |
| `sentetik-testler/veri/yayimlanmis_ornekler.json` | `c4d950b744ca9ff20d979956a59bd2d16e9eff21bd173d3e1b649854fc7aa63a` |
| `sentetik-testler/veri/ornek_n31_sentetik_hedefler.csv` | `4840fdc3197357eb380984810e37b2d1eaaf20b4dd12c2b118622ff027cc9c4a` |
| `sentetik-testler/veri/ornek_n31_sentetik_vakalar.csv` | `13663258db5565e876560768f30c69e8f101f17c5e5b6dbb74c52933574c2ab3` |
| `kaynak/NEWCOMBE-KAYNAK.md` (now `kaynak/NEWCOMBE-SOURCE.md`) | `a9eaf810614fd15fe25ec592f30dd1c513887d57097977459ef6f2d5b1500e35` |

**NOT in the freeze package:**
- `DECISION-NOTES.md`, this file and `results/` (evidence record; summaries in §6).
- `records/` (Docker lists, build log).

## 2. Image

| Item | Value |
|---|---|
| Name | `pq-a09-analiz:1.0` |
| Image id | `sha256:f7bc4aa39c305a85d624de8ff9e75f25aa5fec943d035c664fbc2c5243c45966` (build of 25.09.2026; `records/image_id.txt`) |
| Base | `python:3.11-slim@sha256:9534e5a8e315485d4061ed659af0fd78a284c015f9b73661b41d6bab25604534` (Python 3.11.16; official Docker Hub; the digest used in the project) |
| Packages | `scripts/requirements.txt`: numpy 2.4.6, scipy 1.17.1, statsmodels 0.15.0 + the full dependency closure (pandas 3.0.6, patsy 1.0.3, formulaic 1.2.2, interface-meta 2.0.1, narwhals 2.26.0, packaging 26.3, python-dateutil 2.9.0.post0, six 1.17.0, typing-extensions 4.16.0, wrapt 2.4.1). All from PyPI, version and SHA-256 pinned; `pip install --require-hashes --only-binary=:all: --no-deps` + `pip check` |
| Version gate | The build fails if Python 3.11.16 and the numpy/scipy/statsmodels versions differ from the expected ones |
| Run | `--rm --memory=4g --network none`; container names `pq-a09-analiz-*` |

**Note:** the Docker image id may change on a rebuild (creation time in the configuration). The content is determined by:
- the base digest,
- the `requirements.txt` digests,
- the file digests of §1.

At the freeze the maintainers build the image once and write its id into the package. Step 10 runs with the same id.

## 3. Seeds

| Seed | Value | Use | Basis |
|---|---|---|---|
| Bootstrap | **20260927** | `bootstrap.kume_bootstrap_saf/numpy`. Every bootstrap call (scope: all / K / T) starts with a new `random.Random(20260927)` | PR §6.9, Appendix C |
| Other Appendix C seeds (20260924–26, 20260928–29) | — | **Not used** in the statistics scripts (generator, mutation, sampling, differential test, overhead) | — |
| Test seeds | 910001–910005, 910010 | Synthetic test data only (`test_iki_uygulama.py`, `make_sample_data.py`). Not an analysis seed | — |

**Full definition of the random stream (not in the PR; decision notes N-7):**
- `rng = random.Random(20260927)` (Mersenne Twister).
- Clusters are ordered lexicographically by `hedef_id`. Clusters with m = 0 are excluded beforehand; k = the number of remaining clusters.
- For r = 1…B and j = 1…k, `indeks = floor(rng.random() · k)` (replication-major order).
- The statistic is the pooled proportion: θ\* = Σ x / Σ m.
- Percentile CI: Hyndman–Fan type 7, q = 1/40 and 39/40.

Python guarantees the stability of the `random()` sequence; therefore the definition is built on `random()` instead of `randrange`.

## 4. Traceability: PR item → implementation → test

A = `scripts/c3istat/kesin.py`: standard library only, exact fractions and Decimal.
B = `scripts/c3istat/referans.py`: scipy/statsmodels/numpy.
Pipeline = `scripts/c3istat/analiz.py`.

| PR item | Definition | A / B | Pipeline | Tests (`synthetic-tests/`) |
|---|---|---|---|---|
| §2B.5, §3.7, §6.6 T1, Appendix A | One-sided exact binomial (lower), X = Σ Y_L4. c(n_eff) = max{c : P(X ≤ c) ≤ 0.05}, u = n_eff − c. X ≤ c support, X ≥ u falsification, in between undetermined | `kesin.binom_alt_p`, `kesin.kritik_degerler` / `referans.binom_alt_p`, `referans.kritik_degerler` | `t1_karari`, `_t1` | `test_ek_a` (EkATablosu, N31, GenelKural); `test_sinir.T1Karari`; `test_iki_uygulama.test_binom_p_degerleri`, `test_kritik_degerler` |
| §6.3 | n_eff = included − adapter invalid − undetermined. If n_eff < 20, descriptive only (Wilson) | — | `analiz_et`, `t1_karari` | `test_sinir.T1Karari` (n_eff_20_alti, n_eff_degisimi, butun_hedefler_belirsiz); `test_uctan_uca.H6Hukmu.test_tanimlayici` |
| §6.10 | (i) undetermined = 1, (ii) undetermined = 0. **support** = primary AND (i) X ≤ c; primary only ⇒ **fragile support** | — | `_t1_duyarliliklar`, `h6_hukmu` | `test_uctan_uca.H6Hukmu` (destek, kirilgan_destek, destek_belirsizle_saglam, yanlislama, belirsiz) |
| §0.3, §6.10 | T1 without the pilot libraries | — | `_t1_duyarliliklar` | `test_uctan_uca.Duyarliliklar.test_pilot_haric` |
| §2B.9 | T1 and T2 without the delegating targets; descriptive, outside Holm | — | `_t1_duyarliliklar`, `analiz_et` (T2d) | `test_uctan_uca.Duyarliliklar.test_devralan_haric_t1_t2` |
| §6.6 T2, §2B.7 | Exact McNemar (F_K, F_T), two-sided; TK1 + TK2 only; TK3 separate and descriptive | `kesin.mcnemar_kesin` / `referans.mcnemar_kesin` (statsmodels) | `_t2`, `_tanimlayici` | `test_iki_uygulama.test_mcnemar`; `test_sinir.McNemarSinir`; `test_uctan_uca.T2KapsamVeEtki` |
| §6.7 T2 | Paired difference P(F_T=1) − P(F_K=1) + Newcombe method 10 (φ\*) | `kesin.newcombe_eslestirilmis` / `referans.newcombe_eslestirilmis` | `_t2` | `test_yayimlanmis` (Y5–Y7, NewcombeTanimi); `test_iki_uygulama.test_newcombe_eslestirilmis`, `…phi0_statsmodels_bagimsiz`; `test_sinir.NewcombeSinir` |
| §6.6 T3 | Fisher exact, two-sided; PQ-specific = F_T = 1 ∧ F_K = 0; SDJWT ↔ JOSE | `kesin.fisher_iki_yonlu` / `referans.fisher_iki_yonlu` (scipy) | `_t3`, `_fisher_blok` | `test_iki_uygulama.test_fisher`; `test_sinir.FisherSinir`; `test_uctan_uca.T3T4T5.test_t3` |
| §6.6 T4 | Fisher exact; L ≥ 3; release after 8725bis-10 (21.08.2026) | same | `_t4`, `_fisher_blok` | `test_uctan_uca.T3T4T5.test_t4`; `test_sema.test_tarih_bayrak_celiskisi` |
| §6.7 T3, T4 | OR (conditional MLE) + conditional exact CI; difference + Newcombe method 10 (independent) | `kesin.kosullu_or` / `referans.kosullu_or` (scipy `odds_ratio`, conditional); `kesin.newcombe_bagimsiz` / `referans.newcombe_bagimsiz` (statsmodels `newcomb`) | `_fisher_blok` | `test_iki_uygulama.test_kosullu_or`, `test_newcombe_bagimsiz`; `test_yayimlanmis` (Y4); `test_sinir.FisherSinir.test_or_*` |
| §6.6 T5 | One-sided exact binomial (upper), D_soy | `kesin.binom_ust_p` / `referans.binom_ust_p` | `_t5` | `test_uctan_uca.T3T4T5.test_t5`; `test_iki_uygulama.test_binom_p_degerleri` |
| §6.7 T1, T5 | Proportion + Wilson 95 % CI (+ difference from 0.5 for T1) | `kesin.wilson` / `referans.wilson` (statsmodels) | `_t1`, `_t5` | `test_uctan_uca.H6Hukmu.test_etki_buyuklugu_t1`; `test_yayimlanmis` (Y1–Y3); `test_ek_a.Tablo613` |
| §6.6 Holm | Holm (T2–T5), m = 4, α = 0.05; T1 outside the family | `kesin.holm` / `referans.holm` (statsmodels `multipletests`) | `_holm` | `test_sinir.HolmSinir` (known example, ties, α/k boundary, permutation); `test_iki_uygulama.test_holm`; `test_uctan_uca.T3T4T5.test_holm_butunlesik` |
| §6.8 | Wilson 95 % CI: every L level, B1–B6 (B1/B5 per category; B4 = `B4_ozel_kod`) | `kesin.wilson` / `referans.wilson` | `_wilson_tablolari` | `test_uctan_uca.GenelYapi.test_wilson_l_duzeyleri`; `test_iki_uygulama.test_wilson` |
| §6.9 | Cluster bootstrap: unit library, B = 10,000, percentile CI, seed 20260927 | `bootstrap.kume_bootstrap_saf` / `kume_bootstrap_numpy`; `kesin.yuzdelik_tip7` | `_bootstrap` | `test_bootstrap` (bit-level repetition, separate process, known distribution); `test_iki_uygulama.test_bootstrap_numpy_ve_saf`; `test_uctan_uca.GenelYapi.test_bootstrap_hatti` |
| §6.11 | The number of unstable cells is reported | — | `_tanimlayici` (`kararsiz_hucre_sayisi`) | `test_uctan_uca.CsvJsonEsdegerlik` |
| §6.13 | Threshold table (25/30/40) and Wilson widths | `kesin.kritik_degerler`, `kesin.wilson` | — | `test_ek_a.Tablo613` |
| §6.14 | Power note (n = 30) | `kesin.binom_cdf` (general p) | — | `test_ek_a.Not614Guc` |
| §6.6 rationale | If T1 entered Holm, ≤ 8 / ≥ 22 at n = 30 | `kesin.kritik_degerler(α = 0.01)` | — | `test_ek_a.Not66Holm` |
| §2B.3–4 | n = 31 expected (warning otherwise); REF outside n | — | `analiz_et` | `test_uctan_uca.GenelYapi` (n_uyarisi, ref_hedefler_disarida) |
| §2B.6, §2D-A.2, §4.13–4.15 | Y_L4 (L4m/L4c), control label, L0–L5, B1–B6, reasons for undetermined | `sema` | `_tanimlayici`, `_wilson_tablolari` | `test_sema` |
| Appendix C | Bootstrap seed | `yapilandirma.BOOTSTRAP_TOHUM` | — | `test_bootstrap.BilinenCevap.test_yapilandirma_ok_ile_ayni` |

**Tolerances and the knife-edge rule** (`yapilandirma.TOLERANSLAR`, `karsilastir.py`):
- p and CI: absolute 1e-10.
- OR: relative 1e-8 (absolute floor 1e-12).
- Bootstrap: 1e-12.
- A decision difference counts as "borderline" only if the reference value is within ≤ 1e-12 of the threshold; in that case exact arithmetic (A) is authoritative and the difference is reported.
- Every other difference is an error. The pipeline exits with code 2 and the analysis is invalid.

## 5. Running (for Step 10)

1. First run `sha256sum -c SHA256SUMS` (in this folder). Stop on any mismatch (PR §10.7).
2. The input is a single JSON file conforming to `SCHEMA.md` (`veri_turu = "olcum"`). CSV is accepted as well: `hedefler.csv` + `vakalar.csv`.
3. Command:

   ```
   docker run --rm --name pq-a09-analiz-kosu --memory=4g --network none \
     -v <input>:/girdi:ro -v <output>:/cikti pq-a09-analiz:1.0 \
     python -m c3istat analiz --girdi /girdi/<file>.json --cikti /cikti
   ```

4. Outputs:
   - `sonuc.json` (machine-readable; deterministic, contains no date; carries the script digests in `arac.betik_sha256`),
   - `sonuc.md` (human-readable table),
   - `karsilastirma.json` (two-implementation comparison of every quantity).
5. Exit codes: 0 done · 2 the two implementations disagree (analysis invalid) · 3 the input could not be validated (`dogrulama_hatalari.json`).

## 6. Validation evidence (25.09.2026; `results/`)

**Synthetic test suite** run in two fresh containers; the `test_summary.json` of the two runs is byte-identical:
- test methods **115/115**, sub-tests **729/729**,
- two implementations **56,269/56,269 cases**, **90,058/90,058 quantities**. Largest deviations per family:
  - binomial 2.8e-16; Fisher 3.3e-16; McNemar 4.4e-16;
  - Wilson 3.3e-16; Newcombe (independent and paired) 5.6e-16;
  - conditional OR relative 4.6e-11;
  - Holm 0; bootstrap 4.4e-16 (distribution SHA-256 values equal).

**Appendix A:** all 21 rows n = 20…40 were reproduced exactly with both implementations (c, u, P(X ≤ c) to 4 decimals). **n = 31:** c = 10, u = 21, P(X ≤ 10) = 75973189/2147483648 = 0.035378 (PR: 0.0354).

**Published examples (Y1–Y7):** reproduced with both implementations. The source is secondary; the primary text was not accessible (`sources/NEWCOMBE-SOURCE.md`).

**Determinism:**
- The example synthetic analysis (`synthetic-tests/data/sample_n31_synthetic.json`) was run in two fresh containers; `sonuc.json`, `sonuc.md` and `karsilastirma.json` byte-identical. SHA-256 of `sonuc.json`: `388b48a27049b3d52ab559ab3c212fcafeb8f2e02f56ffe45e9ace18ce1931d4`.
- The run with CSV input is identical to the JSON run except for the `girdi` metadata block.
