# data — trusted-list snapshot and pilot statistics

Measured input data that the threat model and the ASP model refer to. Nothing in this folder is
modified; new data are added as new files.

| File | Content |
|---|---|
| `eu-lotl_seq394.xml` | Snapshot of the EU List of Trusted Lists (LOTL), sequence number 394, issued 2026-09-10T15:35:23Z. Third-party data published by the European Commission, kept unchanged |
| `eu-lotl_seq394.xml.sha256` | SHA-256 of the snapshot: `24c47f10c2dee1821e811664978511f0ef2129c46644ff0c61b47311dd639616` (check with `sha256sum -c eu-lotl_seq394.xml.sha256`) |
| `tl_pilot.json` | Statistics of the certificates found in the national trusted lists referenced by the snapshot (design-stage pilot P5) |

## `tl_pilot.json`

| Field | Value | Meaning |
|---|---|---|
| `lotl_issue` | 2026-09-10T15:35:23Z | issue time of the LOTL |
| `xml_tl_locations` | 29 | XML trusted-list locations in the LOTL |
| `tl_fetched` | 28 | trusted lists that could be fetched |
| `unique_certs` | 4,374 | distinct certificates |
| `valid_on_2026_09_23` | 1,929 | certificates valid on 2026-09-23 |
| `notAfter_ge_2031`, `notAfter_ge_2036` | 1,019, 596 | certificates valid until 2031 or later, 2036 or later |
| `key_alg` | e.g. RSA-2048 2,217; RSA-4096 1,202; EC P-256 173 | key algorithm histogram (every parsed key is classical; 8 unparseable) |
| `sig_alg` | e.g. sha256WithRSAEncryption 2,527 | signature algorithm histogram |
| `notAfter_year` | | histogram of expiry years |

## Where it is used

- `threat-model/THREAT-MODEL.md`: the "measured" column of the artefact table (LOTL signed with
  `rsa-sha512`, NextUpdate 181 days later, 43 pointers).
- `models/asp/olgular/artefaktlar.lp`: weight and pointer count of artefact A02 (`m2_agirlik`,
  `m2_isaretci`).
- `models/asp/calistir.sh` mounts this folder read-only as `/veri` (the folder was called `veri/`
  during the study; see `docs/PATHS.md`).
