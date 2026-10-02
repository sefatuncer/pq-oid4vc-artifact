# Source of the published example values for Newcombe method 10 and Wilson

**Date:** 25.09.2026 (search 12:25:54–12:30:41 UTC; at most 10 min, by decision of the maintainers).
**Prepared by:** the statistics work (Step 9, task 9).

## 1. Primary sources: NOT ACCESSIBLE

| Paper | DOI | Status |
|---|---|---|
| Newcombe RG (1998). Improved confidence intervals for the difference between binomial proportions based on paired data. *Stat Med* 17(22):2635–2650 | `10.1002/(SICI)1097-0258(19981130)17:22<2635::AID-SIM954>3.0.CO;2-C` | Closed access |
| Newcombe RG (1998). Interval estimation for the difference between independent proportions: comparison of eleven methods. *Stat Med* 17(8):873–890 | `10.1002/(SICI)1097-0258(19980430)17:8<873::AID-SIM779>3.0.CO;2-I` | Closed access |

Legal routes tried:
- OpenAlex (anonymous, no `mailto`): for both papers `is_oa = false`, `oa_status = closed`, `any_repository_has_fulltext = false`.
- Scholar Gateway (Wiley): only the abstract was returned (`total_chunks = 1`). The abstract of the paired-data paper confirms the method number: "*A computationally simpler method based on the score interval for the single proportion also performs well (method 10).*"
- Wiley link: HTTP 403. The paywall was **not bypassed**.
- The CiteSeerX record redirects to the Wayback Machine; HTTP 429. An archived copy was **not used**.

Result: the values in Newcombe's tables could **not be verified** from the primary text.

## 2. Open-access secondary source used

**R package `ratesci`** (Pete Laud; CRAN; licence GPL (≥ 3)).
- Repository: `https://github.com/petelaud/ratesci`, commit `7ad93a580144fe78b9545263975621967bd8c0a0` (21.09.2026).
- Package version (DESCRIPTION): `1.1.0.9000`.
- File: `tests/testthat/test3.R`, SHA-256 `57bb060993d3cad7f36827109018ec97dd962b0a727a56d280668a01206b20f4`.
  - First line of the file: "`# Tests of outputs vs published examples in the literature`".
- Definition file: `R/moverpairci.R`, SHA-256 `d49c463b94411385bbe4342a6990130df6c2970f97fc04a5351618efa83c1094`.

The values below were taken **verbatim** from `test3.R`. Line numbers in brackets refer to this commit. The file itself is GPL and was therefore not copied into the repository; only these short quotes are kept.

| # | Data | Method (ratesci call) | Value given in the source | Description in the source |
|---|---|---|---|---|
| Y1 | x = 15, n = 148 | `wilsonci(cc = FALSE)` | (0.0624; 0.1605) | "Single proportion, Newcombe examples" (l. 347, 360–364) |
| Y2 | x = 0, n = 20 | same | (0; 0.1611) | same |
| Y3 | x = 1, n = 29 | same | (0.0061; 0.1718) | same |
| Y4 | x1 = 5, n1 = 56; x2 = 0, n2 = 29 | `moverci(type = "wilson")` (square-and-add) | (−0.0381; 0.1926) | "Newcombe RD example (d)", "Newcombe/'Score'/Square&add" (l. 7, 20–24) |
| Y5 | (a, b, c, d) = (20, 12, 2, 16) | `moverpairci(type = "wilson", corc = TRUE)` | (0.0562; 0.3292) | "and against Newcombe's method 10 result" (l. 525–528) |
| Y6 | (20, 12, 2, 16) | `moverpairci(type = "wilson", corc = FALSE)` | (0.0618; 0.3242) | "example from Newcombe, against Newcombe's method 8 result" (l. 520–523) |
| Y7 | (1, 1, 7, 12) | `moverpairci(type = "wilson", corc = TRUE)` | (−0.507; −0.026) | "MOVER Wilson - Fagerland use Newcombe's correlation-corrected 'method 10'" (l. 487–492; example of Fagerland et al. 2014) |

**Table layout** (`moverpairci` documentation): x = (a, b, c, d).
- a: event under both conditions,
- b: event under condition 1 only,
- c: event under condition 2 only,
- d: event under neither.

Difference θ = (a + b)/N − (a + c)/N = (b − c)/N.

## 3. Definition of method 10: the critical detail from this source

`R/moverpairci.R` (commit above) computes the correlation as follows:
- φ̂ = (ad − bc) / √((a+b)(c+d)(a+c)(b+d)).
- With `corc = TRUE` ("Newcombe's adjusted correlation estimate") and ad − bc > 0: φ* = max(ad − bc − N/2, 0) / √(…).
- If the denominator is 0 or the value is undefined, φ = 0.

ratesci reproduces the published method 10 result (Y5) only with **this corrected φ\***. With the plain φ̂ it reproduces Y6 ("method 8").

Therefore `c3istat` implements the paired Newcombe method 10 with φ\*. The PR does not state this detail; see `DECISION-NOTES.md` N-3.

## 4. Limitation

- The values were taken from a secondary source (comparison tests against published examples in an open-source package). A comparison with Newcombe's printed tables was **not made**.
- Assurance has three layers:
  1. `c3istat` reproduces Y1–Y7 to 4 decimals (3 for Y7);
  2. the two independent implementations agree on every synthetic case;
  3. boundary cases that can be checked by hand from the definition of the method.
- **Suggested human step:** if someone with institutional access opens the example tables of the two papers and compares Y4–Y6, this limitation is removed. The values can be added to `sentetik-testler/veri/yayimlanmis_ornekler.json` with a primary-source label.
