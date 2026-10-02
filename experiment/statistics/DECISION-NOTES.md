# Notes from the statistics work to the maintainers (Step 9, task 9; 25.09.2026)

**Rule:** the PR file was not touched. The recommendations below are submitted to the maintainers' decision before the freeze.

**Applied reading:** written in each item. In `betikler/c3istat/yapilandirma.py` the relevant constant carries its N number. If a decision changes, the constant is changed, `tumunu_calistir.sh` is re-run, and `SHA256SUMS` and `FREEZE-INPUT.md` are renewed.

**Numbers:** all numbers here were computed by script in the image `pq-a09-analiz:1.0` (`c3istat.kesin`).

(Quotations from the pre-registration are translated from Turkish.)

---

## A. Ambiguities that require a decision (N-1…N-12)

### N-1 — "n_eff" and the analysis set in T2–T5
- **PR status:** §6.3 defines n_eff only for T1 (included − adapter invalid − undetermined). There is no set definition for T2–T5.
- **Applied:** each test is computed on the targets whose own variables are determined (not null) and whose adapter is valid:
  - T2: F_K and F_T determined, TK1/TK2;
  - T3: F_K and F_T determined, SDJWT/JOSE;
  - T4: L and the version flag determined;
  - T5: D_soy determined.
- These sets are reported in the output with the target list.
- **Recommendation:** add one sentence to PR v1.0 §6.10: "In T2–T5, targets with undetermined or not-applicable values stay outside the relevant test; n is reported per test."

### N-2 — Thresholds and symmetry of sensitivity (i)/(ii)
- **Ambiguity:** in (i), counting the undetermined as Y = 1 makes the sample n_i = n_eff + b. Is the threshold c(n_i) or the primary c(n_eff)?
- **Applied:** c(n_i), with the Appendix A rule.
  - Rationale: the criterion "X ≤ c" is the p ≤ 0.05 decision of an exact test with its own n.
  - Under this reading, support by (i) requires primary support: c(n+1) ≤ c(n) + 1 (`test_ek_a.GenelKural`).
- **Example:** n_eff = 29, X = 9 ⇒ primary support (c = 9). (i): X = 11/31 > c = 10 ⇒ "fragile support" (`test_uctan_uca.H6Hukmu`).
- **Asymmetry:** §6.10 has "fragile support" but no "fragile falsification". Falsification is given only by the primary analysis; (ii) is reported descriptively.
- **Recommendation:** in PR v1.0 (a) write the c(n_i) reading explicitly; (b) decide whether a symmetric robustness note is also wanted for falsification. My recommendation: "fragile falsification" if (ii) does not meet X ≥ u(n_ii). If added before the freeze, this is a 3-line change in the script.

### N-3 — Newcombe method 10, paired: correlation correction φ\* and source limitation
- **PR status:** §6.7 says only "Newcombe CI (paired, method 10)".
- **Source finding** (`kaynak/NEWCOMBE-SOURCE.md`): according to the open-access secondary source (ratesci, CRAN; commit `7ad93a58…`), method 10 uses the Wilson-hybrid interval **with Newcombe's corrected correlation**:
  - if ad − bc > 0, φ\* = max(ad − bc − N/2, 0)/√(efgh); otherwise φ̂; if the denominator is 0, φ = 0.
- **Discriminating evidence** (by script):
  - for (20, 12, 2, 16), φ\* gives the published method 10 value: (0.0562; 0.3292). The plain φ̂ gives the "method 8" value: (0.0618; 0.3242).
  - in the Fagerland example (1, 1, 7, 12) only φ\* gives the published value: (−0.507; −0.026). The plain φ̂ gives (−0.5017; −0.0361).
- **Applied:** φ\* (`NEWCOMBE_ESLESTIRILMIS_PHI = "newcombe_duzeltmeli"`).
- **Limitation:**
  - The primary texts of Newcombe 1998a/b are paywalled and were not accessible. OpenAlex "closed"; Wiley 403; the CiteSeerX record redirects to Wayback and returns 429. No paywall was bypassed.
  - The published values were taken verbatim from the secondary source.
  - Assurance has three layers: agreement of the two implementations on 8,814 cases; equality with the independent `newcomb` interval of statsmodels at φ = 0 on 4,844 cases; boundary cases derivable by hand.
- **Recommendation:**
  - (a) Write the φ\* formula explicitly into PR v1.0 §6.7.
  - (b) **Human step (optional):** compare once, with institutional access, the method 10 column of Newcombe 1998b Table II and the examples of 1998a (independent, 11 methods). The values can be added to `sentetik-testler/veri/yayimlanmis_ornekler.json` with the label "primary"; the test runs automatically.

### N-4 — Scope of T3: COSE and TK3
- **COSE:** §6.6 says T3 is "on SD-JWT-specific and general JOSE targets".
  - **Applied:** COSE targets are outside T3 (`T3_TABAKALAR = ("SDJWT", "JOSE")`). They are not merged with JOSE.
- **TK3:** PR §2B.7 removes TK3 only from T2. The criterion of T3 (F_T = 1 ∧ F_K = 0) also rests on the treatment arm.
  - For TK3 targets (which cannot verify the PQ signature) F_T = 1 is almost certain. T3 may therefore drift towards measuring the TK composition of the strata. The same reason removed TK3 from T2.
  - **Applied:** the literal reading, i.e. all TK classes (`T3_TK_KAPSAMI = ("TK1", "TK2", "TK3")`).
- **Recommendation:** decide before the freeze:
  - (a) keep the literal reading and report the TK composition in the discussion;
  - (b) restrict T3 to TK1 + TK2 as well (a one-line change; the tests are re-run).

  My recommendation is (b), for consistency with T2. The decision must be written into PR v1.0.

### N-5 — Classification variable of T4
- **PR status:** three things are open in the phrase "released a version after 8725bis-10 (21.08.2026)":
  - (i) up to which date (the measurement day or the frame day);
  - (ii) whether "after" is strict (22.08 and later);
  - (iii) targets without an official release (only a commit or a Go module tag).
- **Applied:**
  - The input carries the flag `surum_8725bis_sonrasi` determined by Step 10.
  - If the optional `son_surum_tarihi` is given, the validator checks consistency with the rule "after ⇔ date > 2026-08-21".
  - If there is no notion of a release, the value is `null` (`uygulanamaz`); the target stays outside T4.
- **Recommendation:** write into PR v1.0: "1 if at least one release was published in the package registry or the repository tags between 22.08.2026 and the day on which the version for the measurement is pinned (both inclusive); not applicable if there is no release at all."

### N-6 — A test that cannot be computed in the Holm family
- **Situation:** a test may have no data. Examples: no TK1/TK2 target; no determined F_K/F_T in SDJWT.
- **Applied:**
  - p = 1 is taken (McNemar b + c = 0 and Fisher with a zero margin give 1 anyway); the flag `veri_yok` (no data) is set.
  - The family size m = 4 is kept (conservative).
- **Recommendation:** write this rule into PR v1.0 §6.6.

### N-7 — Incomplete specification of the cluster bootstrap
- **PR status:** §6.9 says only "unit library, B = 10,000, percentile CI, seed 20260927".
- **Applied specification** (details in `FREEZE-INPUT.md` §3):
  - statistic = pooled proportion (Σ non-conforming / Σ determined cases);
  - clusters in `hedef_id` order; a cluster with 0 determined cases is excluded;
  - RNG `random.Random(20260927)`, `indeks = floor(random()·k)`;
  - percentile type 7;
  - scopes: all cases, arm K, arm T; each restarts with the same seed.
- **Open option:** the mean of the per-library proportions is also a defensible estimator; its weights differ. The pooled proportion fits the phrase "within-library case proportions" and clustered proportion estimation better.
- **Recommendation:** write this specification into PR v1.0 §6.9 (or by reference to the freeze package). Also fix which case proportions are reported (all / K / T).

### N-8 — Tolerances of the two implementations and the "borderline" rule
- **Applied:**
  - A (exact fractions and Decimal) is authoritative; B (scipy/statsmodels) is the check.
  - Absolute 1e-10 for p and CI; relative 1e-8 for OR.
  - A decision difference counts as "borderline" and is reported only if the reference value is within ≤ 1e-12 of the threshold. Any other difference invalidates the analysis (exit code 2).
- **Observation** (information): the z values differ in the last digit between the two implementations. Python `statistics.NormalDist` gives 1.9599639845400536, scipy 1.959963984540054 (1 ulp). Effect ≤ 5.6e-16; seen in the tests.
- **Recommendation:** accept the rule as part of the freeze package (short reference in PR §6).

### N-9 — Pilot sensitivity: the PR and the inventory proposal differ
- **PR status:** §0.3 and §6.10: "T1 is repeated **leaving out** the 5 libraries of pilot P3."
- **The inventory proposal differs:** `experiment/inventory/SUMMARY.md` §2.5 says the pilots should not be forced in and an "n + pilots" sensitivity should be done.
- **Applied:** the PR reading (n targets with pilot = 1 are removed).
- **Pilots inside n according to the inventory:** only `jose` and `@sd-jwt/core`. `joserfc` is a reserve; it enters n if the reserve is activated. `jwcrypto` is outside n, Authlib is excluded. So the sensitivity removes at most 2–3 targets.
- **Recommendation:** keep the PR reading. Since "n + pilots" will not have been measured (pilots outside n are not measured), either drop it or label it "exploratory".

### N-10 — Delegation sensitivity: exclusion or a single unit?
- **PR status:** §2B.9 says "removing the delegating targets".
- **The inventory proposal differs:** `SUMMARY.md` R6 proposes counting delegation clusters as a single unit.
- **Applied:** the PR reading. T1 and T2 are recomputed without the delegating targets; descriptive, outside Holm. The only direct delegation inside n is WalletFramework → IdentityModel.
- **Recommendation:** keep it. The two readings give the same result in this single cluster: when the delegating target is removed, the cluster reduces to a single unit.

### N-11 — Old phrases left over from n = 30 inside the PR
- **Old phrases:** §2 (H6 row: "≥20/30 at n=30") and §3.7 ("for n_eff = 30: c = 10, u = 20"). §2B takes precedence over them; the scripts always compute the threshold from n_eff with the Appendix A rule.
- **§6.6 rationale note:** the computation is for n = 30. If T1 entered Holm at n = 31, the threshold would be ≤ 8 / ≥ 23. P(X ≤ 8) = 0.0053; P(X ≤ 9) = 0.0147.
- **§6.14 power note:** for n = 30. For n = 31 and X ≤ 10:

  | True proportion | Probability of support |
  |---|---|
  | 0.2 | 0.9673 |
  | 0.3 | 0.6879 |
  | 0.4 | 0.2454 |

  For X ≥ 21, with a true proportion of 0.7, the probability of falsification is 0.6879.
- **Recommendation:** in PR v1.0 update these three places for n = 31, or mark them "§2B and Appendix A apply". The n = 30 values in the PR themselves are correct; `test_ek_a` reproduces them.

### N-12 — Effect directions and the scope of §6.8
- **Applied directions:**
  - T2 difference P(F_T=1) − P(F_K=1); if positive, there is a PQ-specific excess.
  - In T3, OR and difference of JOSE relative to SDJWT.
  - In T4, "0" relative to "after = 1".
- **Reading of §6.8:**
  - "Each L level" = proportion with L = k. The proportions L ≥ k are given separately, labelled "descriptive addition".
  - B1 and B5 are reported per category.
  - B4 = proportion "expressible with custom code"; the line count is given as median and range.
  - B6 = proportion "not applicable".
- **Recommendation:** write the directions and this reading into PR v1.0 §6.7–6.8.

---

## B. Information notes (no decision needed)

1. **Out of scope:** the divergence detector ("targets that decide differently on the same case") and MR1–MR4 are the job of the oracle folder (Step 9 task 6/8). The statistics scripts do not compute them.
2. **Not computed:**
   - The 3-repetition rule (3/3) and the "unstable" label are produced in Step 10. The scripts only count the reason codes (number of unstable cells, PR §6.11).
   - F_K, F_T, D_soy and the L level are inputs; deriving them from the battery cases is the job of Step 10.
3. **Protection by `veri_turu`:** for `olcum` (measurement) input the output carries the warning "valid only after the freeze". The real protection is PR §10.7: `sha256sum -c SHA256SUMS` at the start of Step 10.
4. **Versions:** numpy 2.4.6, scipy 1.17.1, statsmodels 0.15.0. These are the latest compatible versions that pip chooses for Python 3.11.
   - The behaviour of the relevant functions was verified by reading the source of the wheels and with tests: scipy `odds_ratio(kind="conditional")` brentq `xtol = 1e-13`; `fisher_exact` relative tolerance 1e-14; statsmodels `newcomb` = Wilson square-and-add; Wilson is clipped to [0, 1]; Holm rejection with p ≤ α/k.
5. **Docker:**
   - Image `pq-a09-analiz:1.0` (`sha256:f7bc4aa3…`).
   - The old untagged image left from the first build disappeared by itself; there is no `pq-a09-analiz-*` container any more.
   - **The build cache was not cleaned:** `docker builder prune` is a prune command and forbidden by the project rule. The maintainers decide on the clean-up.
   - The image lists at start and end are in `kayit/`. No other image or container was touched.
6. **Time:** the test suite takes 95–112 s in one container. Most of it is the exhaustive two-implementation sweeps: all 2×2 tables, N ≤ 20.
7. **Privacy:** the only external requests were: OpenAlex (anonymous, no `mailto`), the GitHub API and raw (anonymous, no credentials), the Wiley link (403), CiteSeerX (Wayback 429), Scholar Gateway (abstract only) and PyPI (package download). None contained an e-mail address or personal data. Git was not used.
