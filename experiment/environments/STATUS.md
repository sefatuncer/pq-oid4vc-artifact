# STATUS (interim record; work plan §3.1 item 7)

- **Last update:** 25.09.2026 — task 4a DONE.
- **Done:**
  - 12 environment images (`IMAGES.md`).
  - 34 targets: 33 succeeded, 1 failed (JOSE-104).
  - Two reserve candidates for JOSE-104 (JOSE-031, JOSE-017) were built; the choice lies with the maintainers (`TARGET-CHANGES.md`).
  - Informational runs: `_info-*` (6).
  - `DECISION-NOTES.md`, `SHA256SUMS`.
- **Next (maintainers):**
  - K1 choice of the reserve.
  - K2 version pinning (son_surum ↔ son_commit_sha).
  - K3–K6 (`DECISION-NOTES.md` §1).
  - Clean-up of base images and build cache.
- **Open file:** none.
- **Last command:** `sha256sum` (generation of SHA256SUMS).
- **Lessons:**
  - On Windows, Python `write_text` writes CRLF; use `write_bytes` when patching scripts.
  - In the Bash tool, `\` collapses to a single `\`.
  - Alpine-based images have no `bash`.
