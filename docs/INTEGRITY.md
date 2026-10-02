# Integrity of the hash-anchored files

Many files of this study were fixed with SHA-256 lists **before** the runs that used them, so that
a reader can check that the procedures, expectations and inputs were not changed after the results
were seen. These lists are kept exactly as they were recorded:

- per-folder `SHA256SUMS` files, `*.sha256`, `SHA256-ON-KAYIT.txt` (pre-registration list of the
  mechanism step), `HAZIRLIK_SHA256SUMS` (KAT preparation), `models/tamarin/sonuc/sha256*.txt`;
- hard-coded expected digests in scripts (see section 4).

For this English release the hand-written documents were translated and renamed, and code comments
were translated. **None of the SHA-256 records was edited.** The translated files are the
working versions; the recorded bytes are kept in an archive, so that every record can still be
checked.

Per-folder integrity lists describe the recorded state. Files were edited for language; earlier
pre-run anchors that are older than the base of this release are kept in the maintainers' private
working history and are available on request.

## 1. The archive

`archive/hash-anchored/<original path>` holds, byte for byte, the version of every file that is named
in a SHA-256 record and that this release renamed, deleted or changed (documents that were translated
and renamed, and code files whose comments or diagnostic messages were translated in place). The copies
were taken with `git show <revision>:<path>` from the last revision before the translation (the base
revision of this release) and checked with SHA-256 after writing. Three statistics scripts
(`experiment/statistics/betikler/c3istat/analiz.py`, `.../rapor.py` and
`experiment/statistics/sentetik-testler/test_uctan_uca.py`) were changed by pre-registration amendment 11
after their record had been written; for these the archive holds the recorded bytes from the earlier
revision, and the statistics record is renewed when the pre-registration is frozen.

The archived files are the original Turkish texts. They are not maintained and are not meant to be
read instead of the English files; they exist only so that the records can be verified.

`archive/hash-anchored/ANCHOR-NOTES.tsv` lists the record entries that the archive cannot match by
itself:

- `edited-before-base`: the file already differed from its record in the base commit. These files were
  edited in the private working history before this release was prepared (mostly by the commits that
  neutralised the wording of process notes and renamed the top-level folders). The table gives the
  digest of the base version, so the current or archived file can still be identified exactly.
- `recorded-path-rewritten-in-base`: the path written in the record was rewritten in the base commit
  (`sentetik-testler/data/` instead of `sentetik-testler/veri/`); the file itself still matches.
- `outside-repository`: the record names a file outside this repository (the original design-stage
  pilot under `referans/`; its copy `tools/regression-tests/p1/weakest_link.spthy` is listed in the same
  record and matches).

## 2. Original path → archived copy → English file

"Anchor = base" says whether the archived (base) copy matches the record. "no" means the record
predates the base version (see `edited-before-base` above).

| Original path | Archived copy | English file in this release | Record(s) | Anchored SHA-256 (record) | Archived SHA-256 (base) | Anchor = base | Release SHA-256 |
|---|---|---|---|---|---|---|---|
| `experiment/environments/DEGISIKLIKLER.md` | `archive/hash-anchored/experiment/environments/DEGISIKLIKLER.md` | `experiment/environments/TARGET-CHANGES.md` | experiment/environments/SHA256SUMS | `ea93387f31a16ffe…` | `ea4d4bf7b27c50d1…` | no | `a3c0689fbc6c0ca1…` |
| `experiment/environments/DURUM.md` | `archive/hash-anchored/experiment/environments/DURUM.md` | `experiment/environments/STATUS.md` | experiment/environments/SHA256SUMS | `87c7c857a77ae046…` | `1ddcf10abe5d93d8…` | no | `43e04919d6f33b86…` |
| `experiment/environments/IMAJLAR.md` | `archive/hash-anchored/experiment/environments/IMAJLAR.md` | `experiment/environments/IMAGES.md` | experiment/environments/SHA256SUMS | `da868a4cb1617c7c…` | `9c325b9eb2a2a52d…` | no | `c01e608506200093…` |
| `experiment/environments/KARAR-NOTLARI.md` | `archive/hash-anchored/experiment/environments/KARAR-NOTLARI.md` | `experiment/environments/DECISION-NOTES.md` | experiment/environments/SHA256SUMS | `61b801683f470842…` | `3551d7343ff560d8…` | no | `677a824ef80c123d…` |
| `experiment/environments/betikler/etiket_coz.py` | `archive/hash-anchored/experiment/environments/betikler/etiket_coz.py` | `experiment/environments/betikler/etiket_coz.py` | experiment/environments/SHA256SUMS | `fc1b5a2901677f9e…` | `fc1b5a2901677f9e…` | yes | `14a71218b22e27a7…` |
| `experiment/environments/betikler/hedef_listesi.py` | `archive/hash-anchored/experiment/environments/betikler/hedef_listesi.py` | `experiment/environments/betikler/hedef_listesi.py` | experiment/environments/SHA256SUMS | `f1bad55d378a55e2…` | `4027bfca4c54c21a…` | no | `7fdd6a9302c561cf…` |
| `experiment/environments/betikler/konteyner/KontrolYukle.java` | `archive/hash-anchored/experiment/environments/betikler/konteyner/KontrolYukle.java` | `experiment/environments/betikler/konteyner/KontrolYukle.java` | experiment/environments/SHA256SUMS | `30a2f63140415d4e…` | `30a2f63140415d4e…` | yes | `422d6796e32987d3…` |
| `experiment/environments/betikler/konteyner/cargo.sh` | `archive/hash-anchored/experiment/environments/betikler/konteyner/cargo.sh` | `experiment/environments/betikler/konteyner/cargo.sh` | experiment/environments/SHA256SUMS | `835fafb3cf702f71…` | `835fafb3cf702f71…` | yes | `ef2d0450ec9dad8a…` |
| `experiment/environments/betikler/konteyner/composer.sh` | `archive/hash-anchored/experiment/environments/betikler/konteyner/composer.sh` | `experiment/environments/betikler/konteyner/composer.sh` | experiment/environments/SHA256SUMS | `b91f301991dc3c9e…` | `b91f301991dc3c9e…` | yes | `de05e14feedf1258…` |
| `experiment/environments/betikler/konteyner/gem.sh` | `archive/hash-anchored/experiment/environments/betikler/konteyner/gem.sh` | `experiment/environments/betikler/konteyner/gem.sh` | experiment/environments/SHA256SUMS | `1d78cb2f444e0914…` | `1d78cb2f444e0914…` | yes | `3b283904d591234f…` |
| `experiment/environments/betikler/konteyner/go.sh` | `archive/hash-anchored/experiment/environments/betikler/konteyner/go.sh` | `experiment/environments/betikler/konteyner/go.sh` | experiment/environments/SHA256SUMS | `252ac8a9ddb5c036…` | `252ac8a9ddb5c036…` | yes | `2e753f7027a462d2…` |
| `experiment/environments/betikler/konteyner/gradle-lib.sh` | `archive/hash-anchored/experiment/environments/betikler/konteyner/gradle-lib.sh` | `experiment/environments/betikler/konteyner/gradle-lib.sh` | experiment/environments/SHA256SUMS | `25a0e815bd60a775…` | `25a0e815bd60a775…` | yes | `c5980985f6c4cff2…` |
| `experiment/environments/betikler/konteyner/maven.sh` | `archive/hash-anchored/experiment/environments/betikler/konteyner/maven.sh` | `experiment/environments/betikler/konteyner/maven.sh` | experiment/environments/SHA256SUMS | `ea1d0cd97e69cca1…` | `ea1d0cd97e69cca1…` | yes | `052d122f82588237…` |
| `experiment/environments/betikler/konteyner/npm.sh` | `archive/hash-anchored/experiment/environments/betikler/konteyner/npm.sh` | `experiment/environments/betikler/konteyner/npm.sh` | experiment/environments/SHA256SUMS | `8126d5f234bef715…` | `8126d5f234bef715…` | yes | `f7fc09973ff7a6e5…` |
| `experiment/environments/betikler/konteyner/nuget.sh` | `archive/hash-anchored/experiment/environments/betikler/konteyner/nuget.sh` | `experiment/environments/betikler/konteyner/nuget.sh` | experiment/environments/SHA256SUMS | `7134d5d956d8dd0a…` | `7134d5d956d8dd0a…` | yes | `2a86a7a05bd5de23…` |
| `experiment/environments/betikler/konteyner/ortak.sh` | `archive/hash-anchored/experiment/environments/betikler/konteyner/ortak.sh` | `experiment/environments/betikler/konteyner/ortak.sh` | experiment/environments/SHA256SUMS | `5f11a3d0942ec84d…` | `5f11a3d0942ec84d…` | yes | `592c54e15d3a1afd…` |
| `experiment/environments/betikler/konteyner/pip.sh` | `archive/hash-anchored/experiment/environments/betikler/konteyner/pip.sh` | `experiment/environments/betikler/konteyner/pip.sh` | experiment/environments/SHA256SUMS | `ff6896837170858d…` | `f95f87875f6a12e7…` | no | `2a7e1223654ef27b…` |
| `experiment/environments/betikler/konteyner/swiftpm.sh` | `archive/hash-anchored/experiment/environments/betikler/konteyner/swiftpm.sh` | `experiment/environments/betikler/konteyner/swiftpm.sh` | experiment/environments/SHA256SUMS | `5fb20a5ec248af46…` | `5fb20a5ec248af46…` | yes | `8e03c0fb4b8da131…` |
| `experiment/environments/betikler/kos.sh` | `archive/hash-anchored/experiment/environments/betikler/kos.sh` | `experiment/environments/betikler/kos.sh` | experiment/environments/SHA256SUMS | `6d3d620b5203424e…` | `71be00451f554ae1…` | no | `108bfcbb74387040…` |
| `experiment/environments/betikler/surum_dayanak.py` | `archive/hash-anchored/experiment/environments/betikler/surum_dayanak.py` | `experiment/environments/betikler/surum_dayanak.py` | experiment/environments/SHA256SUMS | `3f68ac06b347bfc1…` | `89b9b7ae8e91dd11…` | no | `eb0bafd92d700f22…` |
| `experiment/environments/betikler/surum_ozet.py` | `archive/hash-anchored/experiment/environments/betikler/surum_ozet.py` | `experiment/environments/betikler/surum_ozet.py` | experiment/environments/SHA256SUMS | `417d3710c49cb150…` | `417d3710c49cb150…` | yes | `313d2c08bebe328f…` |
| `experiment/environments/betikler/topla_sonuc.py` | `archive/hash-anchored/experiment/environments/betikler/topla_sonuc.py` | `experiment/environments/betikler/topla_sonuc.py` | experiment/environments/SHA256SUMS | `717e10182c9846b6…` | `717e10182c9846b6…` | yes | `03e41dfce49b7c31…` |
| `experiment/environments/hedefler/COSE-001/kur-maven.sh` | `archive/hash-anchored/experiment/environments/hedefler/COSE-001/kur-maven.sh` | `experiment/environments/hedefler/COSE-001/kur-maven.sh` | experiment/environments/SHA256SUMS | `bbad50f89cfa20d1…` | `bbad50f89cfa20d1…` | yes | `abe9bb284db0dbf3…` |
| `experiment/environments/hedefler/COSE-001/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/COSE-001/kur.sh` | `experiment/environments/hedefler/COSE-001/kur.sh` | experiment/environments/SHA256SUMS | `e0570c0435e224f2…` | `e0570c0435e224f2…` | yes | `82ca6bb6c2beb76b…` |
| `experiment/environments/hedefler/COSE-014/ice_aktar.mjs` | `archive/hash-anchored/experiment/environments/hedefler/COSE-014/ice_aktar.mjs` | `experiment/environments/hedefler/COSE-014/ice_aktar.mjs` | experiment/environments/SHA256SUMS | `8fb6fc7c3c6b371b…` | `8fb6fc7c3c6b371b…` | yes | `06a2eab0da181808…` |
| `experiment/environments/hedefler/COSE-014/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/COSE-014/kur.sh` | `experiment/environments/hedefler/COSE-014/kur.sh` | experiment/environments/SHA256SUMS | `5c12998185fc8ba7…` | `5c12998185fc8ba7…` | yes | `3b9a80057406767e…` |
| `experiment/environments/hedefler/COSE-034/ice_aktar.go` | `archive/hash-anchored/experiment/environments/hedefler/COSE-034/ice_aktar.go` | `experiment/environments/hedefler/COSE-034/ice_aktar.go` | experiment/environments/SHA256SUMS | `6a8a57092e9ad648…` | `6a8a57092e9ad648…` | yes | `b338c1b8e9121b07…` |
| `experiment/environments/hedefler/COSE-034/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/COSE-034/kur.sh` | `experiment/environments/hedefler/COSE-034/kur.sh` | experiment/environments/SHA256SUMS | `64fd8ebf11e6d96c…` | `64fd8ebf11e6d96c…` | yes | `a551e1eeefbb3453…` |
| `experiment/environments/hedefler/COSE-035/ek.sh` | `archive/hash-anchored/experiment/environments/hedefler/COSE-035/ek.sh` | `experiment/environments/hedefler/COSE-035/ek.sh` | experiment/environments/SHA256SUMS | `2fb7656a79eabe60…` | `2fb7656a79eabe60…` | yes | `c2652e3a2445412b…` |
| `experiment/environments/hedefler/COSE-035/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/COSE-035/kur.sh` | `experiment/environments/hedefler/COSE-035/kur.sh` | experiment/environments/SHA256SUMS | `70803d1e84b00856…` | `70803d1e84b00856…` | yes | `1ddf97814d8ba358…` |
| `experiment/environments/hedefler/COSE-036/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/COSE-036/kur.sh` | `experiment/environments/hedefler/COSE-036/kur.sh` | experiment/environments/SHA256SUMS | `5485b55612e5500b…` | `c6a1150efd7e3f18…` | no | `23ae4a39903ae325…` |
| `experiment/environments/hedefler/JOSE-001/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/JOSE-001/kur.sh` | `experiment/environments/hedefler/JOSE-001/kur.sh` | experiment/environments/SHA256SUMS | `7853849091cd2831…` | `7853849091cd2831…` | yes | `155b0e6b138a2d2a…` |
| `experiment/environments/hedefler/JOSE-002/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/JOSE-002/kur.sh` | `experiment/environments/hedefler/JOSE-002/kur.sh` | experiment/environments/SHA256SUMS | `20845915b77522b6…` | `20845915b77522b6…` | yes | `c4ac6cb9d573369b…` |
| `experiment/environments/hedefler/JOSE-009/ice_aktar.mjs` | `archive/hash-anchored/experiment/environments/hedefler/JOSE-009/ice_aktar.mjs` | `experiment/environments/hedefler/JOSE-009/ice_aktar.mjs` | experiment/environments/SHA256SUMS | `c886417a3ba13daf…` | `c886417a3ba13daf…` | yes | `ce6f9cf84fe0bdc0…` |
| `experiment/environments/hedefler/JOSE-009/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/JOSE-009/kur.sh` | `experiment/environments/hedefler/JOSE-009/kur.sh` | experiment/environments/SHA256SUMS | `b6312de7f45948fe…` | `b6312de7f45948fe…` | yes | `aaf17a1bca9d8915…` |
| `experiment/environments/hedefler/JOSE-017/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/JOSE-017/kur.sh` | `experiment/environments/hedefler/JOSE-017/kur.sh` | experiment/environments/SHA256SUMS | `c43fec0c8cc88413…` | `c43fec0c8cc88413…` | yes | `aed77c3b45fc90be…` |
| `experiment/environments/hedefler/JOSE-031/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/JOSE-031/kur.sh` | `experiment/environments/hedefler/JOSE-031/kur.sh` | experiment/environments/SHA256SUMS | `7d5648c018235224…` | `7d5648c018235224…` | yes | `f5180f15b5d26ca5…` |
| `experiment/environments/hedefler/JOSE-033/ice_aktar.go` | `archive/hash-anchored/experiment/environments/hedefler/JOSE-033/ice_aktar.go` | `experiment/environments/hedefler/JOSE-033/ice_aktar.go` | experiment/environments/SHA256SUMS | `f6deb6578c9065bf…` | `f6deb6578c9065bf…` | yes | `3a6833017943fd72…` |
| `experiment/environments/hedefler/JOSE-033/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/JOSE-033/kur.sh` | `experiment/environments/hedefler/JOSE-033/kur.sh` | experiment/environments/SHA256SUMS | `a0446a3db83304df…` | `a0446a3db83304df…` | yes | `18c0f030b04d6a67…` |
| `experiment/environments/hedefler/JOSE-034/ice_aktar.go` | `archive/hash-anchored/experiment/environments/hedefler/JOSE-034/ice_aktar.go` | `experiment/environments/hedefler/JOSE-034/ice_aktar.go` | experiment/environments/SHA256SUMS | `15f59b5c8ba97eb9…` | `15f59b5c8ba97eb9…` | yes | `a5e4670ae3b7a229…` |
| `experiment/environments/hedefler/JOSE-034/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/JOSE-034/kur.sh` | `experiment/environments/hedefler/JOSE-034/kur.sh` | experiment/environments/SHA256SUMS | `acf70cd77ebd2a8b…` | `acf70cd77ebd2a8b…` | yes | `aaabd67a8efc4268…` |
| `experiment/environments/hedefler/JOSE-052/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/JOSE-052/kur.sh` | `experiment/environments/hedefler/JOSE-052/kur.sh` | experiment/environments/SHA256SUMS | `5b195707385d1125…` | `5b195707385d1125…` | yes | `ecd78fb6d9e2419e…` |
| `experiment/environments/hedefler/JOSE-055/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/JOSE-055/kur.sh` | `experiment/environments/hedefler/JOSE-055/kur.sh` | experiment/environments/SHA256SUMS | `860dbbab1d62e058…` | `860dbbab1d62e058…` | yes | `8051015eb9f98d71…` |
| `experiment/environments/hedefler/JOSE-065/ice_aktar.mjs` | `archive/hash-anchored/experiment/environments/hedefler/JOSE-065/ice_aktar.mjs` | `experiment/environments/hedefler/JOSE-065/ice_aktar.mjs` | experiment/environments/SHA256SUMS | `ba74b27d9382be99…` | `ba74b27d9382be99…` | yes | `6e0559fa1332fedd…` |
| `experiment/environments/hedefler/JOSE-065/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/JOSE-065/kur.sh` | `experiment/environments/hedefler/JOSE-065/kur.sh` | experiment/environments/SHA256SUMS | `79ed455b4ccf0f26…` | `79ed455b4ccf0f26…` | yes | `b0ad2b6a1336e12b…` |
| `experiment/environments/hedefler/JOSE-070/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/JOSE-070/kur.sh` | `experiment/environments/hedefler/JOSE-070/kur.sh` | experiment/environments/SHA256SUMS | `4430d1120a2fb57f…` | `4430d1120a2fb57f…` | yes | `29a765ac5922d672…` |
| `experiment/environments/hedefler/JOSE-071/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/JOSE-071/kur.sh` | `experiment/environments/hedefler/JOSE-071/kur.sh` | experiment/environments/SHA256SUMS | `3d17733094b81522…` | `3d17733094b81522…` | yes | `70c1e0a6416ed859…` |
| `experiment/environments/hedefler/JOSE-083/ice_aktar.py` | `archive/hash-anchored/experiment/environments/hedefler/JOSE-083/ice_aktar.py` | `experiment/environments/hedefler/JOSE-083/ice_aktar.py` | experiment/environments/SHA256SUMS | `28af62e5ca77be9f…` | `28af62e5ca77be9f…` | yes | `b83901743dc31b29…` |
| `experiment/environments/hedefler/JOSE-083/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/JOSE-083/kur.sh` | `experiment/environments/hedefler/JOSE-083/kur.sh` | experiment/environments/SHA256SUMS | `e3970a6bc772b72c…` | `e3970a6bc772b72c…` | yes | `f2a15affc9456a0b…` |
| `experiment/environments/hedefler/JOSE-084/ice_aktar.py` | `archive/hash-anchored/experiment/environments/hedefler/JOSE-084/ice_aktar.py` | `experiment/environments/hedefler/JOSE-084/ice_aktar.py` | experiment/environments/SHA256SUMS | `8643b8a7fd6c569c…` | `8643b8a7fd6c569c…` | yes | `f8df1a048997f0d4…` |
| `experiment/environments/hedefler/JOSE-084/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/JOSE-084/kur.sh` | `experiment/environments/hedefler/JOSE-084/kur.sh` | experiment/environments/SHA256SUMS | `db8a42dfcfefa52c…` | `db8a42dfcfefa52c…` | yes | `9d4e2096756654f7…` |
| `experiment/environments/hedefler/JOSE-087/ice_aktar.rb` | `archive/hash-anchored/experiment/environments/hedefler/JOSE-087/ice_aktar.rb` | `experiment/environments/hedefler/JOSE-087/ice_aktar.rb` | experiment/environments/SHA256SUMS | `8fb0fe675c1329e8…` | `8fb0fe675c1329e8…` | yes | `649c42bd458a1a25…` |
| `experiment/environments/hedefler/JOSE-087/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/JOSE-087/kur.sh` | `experiment/environments/hedefler/JOSE-087/kur.sh` | experiment/environments/SHA256SUMS | `3b9e5837dfc344c4…` | `3b9e5837dfc344c4…` | yes | `d40d9ee4b8e085b7…` |
| `experiment/environments/hedefler/JOSE-089/ice_aktar.rb` | `archive/hash-anchored/experiment/environments/hedefler/JOSE-089/ice_aktar.rb` | `experiment/environments/hedefler/JOSE-089/ice_aktar.rb` | experiment/environments/SHA256SUMS | `eca7577a756ff384…` | `eca7577a756ff384…` | yes | `7d0439e59493b1f5…` |
| `experiment/environments/hedefler/JOSE-089/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/JOSE-089/kur.sh` | `experiment/environments/hedefler/JOSE-089/kur.sh` | experiment/environments/SHA256SUMS | `af0591f425d6db02…` | `af0591f425d6db02…` | yes | `23d7c953459f40c3…` |
| `experiment/environments/hedefler/JOSE-091/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/JOSE-091/kur.sh` | `experiment/environments/hedefler/JOSE-091/kur.sh` | experiment/environments/SHA256SUMS | `322b6bf05837e9bf…` | `322b6bf05837e9bf…` | yes | `3d33c4bbda932e38…` |
| `experiment/environments/hedefler/JOSE-092/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/JOSE-092/kur.sh` | `experiment/environments/hedefler/JOSE-092/kur.sh` | experiment/environments/SHA256SUMS | `08e1c6501f995b77…` | `08e1c6501f995b77…` | yes | `0ee24634933195c4…` |
| `experiment/environments/hedefler/JOSE-102/ek.sh` | `archive/hash-anchored/experiment/environments/hedefler/JOSE-102/ek.sh` | `experiment/environments/hedefler/JOSE-102/ek.sh` | experiment/environments/SHA256SUMS | `ea40277e169146ea…` | `ea40277e169146ea…` | yes | `eea3ab1fa2b4be95…` |
| `experiment/environments/hedefler/JOSE-102/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/JOSE-102/kur.sh` | `experiment/environments/hedefler/JOSE-102/kur.sh` | experiment/environments/SHA256SUMS | `b8d2f023c97dba94…` | `b8d2f023c97dba94…` | yes | `d14fd5d752414481…` |
| `experiment/environments/hedefler/JOSE-104/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/JOSE-104/kur.sh` | `experiment/environments/hedefler/JOSE-104/kur.sh` | experiment/environments/SHA256SUMS | `cb8926a8464e8f85…` | `cb8926a8464e8f85…` | yes | `01e439ce4f5d7140…` |
| `experiment/environments/hedefler/REF-003/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/REF-003/kur.sh` | `experiment/environments/hedefler/REF-003/kur.sh` | experiment/environments/SHA256SUMS | `69de7d29a00f354a…` | `69de7d29a00f354a…` | yes | `22c4486fc2b08e53…` |
| `experiment/environments/hedefler/REF-010/ice_aktar.py` | `archive/hash-anchored/experiment/environments/hedefler/REF-010/ice_aktar.py` | `experiment/environments/hedefler/REF-010/ice_aktar.py` | experiment/environments/SHA256SUMS | `25399a407147f6cd…` | `8e0af06347e1e1c3…` | no | `804605ad514c1262…` |
| `experiment/environments/hedefler/REF-010/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/REF-010/kur.sh` | `experiment/environments/hedefler/REF-010/kur.sh` | experiment/environments/SHA256SUMS | `56288c368f15f1c1…` | `29bdce4a0628c414…` | no | `ff6c74dc629677ab…` |
| `experiment/environments/hedefler/REF-011/ice_aktar.mjs` | `archive/hash-anchored/experiment/environments/hedefler/REF-011/ice_aktar.mjs` | `experiment/environments/hedefler/REF-011/ice_aktar.mjs` | experiment/environments/SHA256SUMS | `adfc36acaf35ed24…` | `70056861f7bdaa19…` | no | `ccbd697b2c236a36…` |
| `experiment/environments/hedefler/REF-011/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/REF-011/kur.sh` | `experiment/environments/hedefler/REF-011/kur.sh` | experiment/environments/SHA256SUMS | `509ba49d1c005011…` | `509ba49d1c005011…` | yes | `ad7cfd1cce837bc5…` |
| `experiment/environments/hedefler/SDJWT-001/kur-maven.sh` | `archive/hash-anchored/experiment/environments/hedefler/SDJWT-001/kur-maven.sh` | `experiment/environments/hedefler/SDJWT-001/kur-maven.sh` | experiment/environments/SHA256SUMS | `fd653a569cd92fe0…` | `fd653a569cd92fe0…` | yes | `af3ef87188dfa9f4…` |
| `experiment/environments/hedefler/SDJWT-001/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/SDJWT-001/kur.sh` | `experiment/environments/hedefler/SDJWT-001/kur.sh` | experiment/environments/SHA256SUMS | `027d6e2b5598093d…` | `027d6e2b5598093d…` | yes | `84d0bb80fac1d098…` |
| `experiment/environments/hedefler/SDJWT-002/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/SDJWT-002/kur.sh` | `experiment/environments/hedefler/SDJWT-002/kur.sh` | experiment/environments/SHA256SUMS | `9d5523f53377ae06…` | `9d5523f53377ae06…` | yes | `e0e526b530f5b418…` |
| `experiment/environments/hedefler/SDJWT-004/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/SDJWT-004/kur.sh` | `experiment/environments/hedefler/SDJWT-004/kur.sh` | experiment/environments/SHA256SUMS | `cdc10b88a37be59b…` | `cdc10b88a37be59b…` | yes | `673aadbdb19e0887…` |
| `experiment/environments/hedefler/SDJWT-010/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/SDJWT-010/kur.sh` | `experiment/environments/hedefler/SDJWT-010/kur.sh` | experiment/environments/SHA256SUMS | `9eac5f1260847123…` | `9eac5f1260847123…` | yes | `507ea650e55a646a…` |
| `experiment/environments/hedefler/SDJWT-015/ice_aktar.mjs` | `archive/hash-anchored/experiment/environments/hedefler/SDJWT-015/ice_aktar.mjs` | `experiment/environments/hedefler/SDJWT-015/ice_aktar.mjs` | experiment/environments/SHA256SUMS | `78216a6f7ba0b877…` | `78216a6f7ba0b877…` | yes | `704d64412a511f06…` |
| `experiment/environments/hedefler/SDJWT-015/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/SDJWT-015/kur.sh` | `experiment/environments/hedefler/SDJWT-015/kur.sh` | experiment/environments/SHA256SUMS | `9889efa4367545b5…` | `9889efa4367545b5…` | yes | `c7ff1da38b6b55cd…` |
| `experiment/environments/hedefler/SDJWT-018/ice_aktar.py` | `archive/hash-anchored/experiment/environments/hedefler/SDJWT-018/ice_aktar.py` | `experiment/environments/hedefler/SDJWT-018/ice_aktar.py` | experiment/environments/SHA256SUMS | `2a93a4a374600bc7…` | `2a93a4a374600bc7…` | yes | `9580644dba734f8f…` |
| `experiment/environments/hedefler/SDJWT-018/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/SDJWT-018/kur.sh` | `experiment/environments/hedefler/SDJWT-018/kur.sh` | experiment/environments/SHA256SUMS | `bfa523b3c82298bc…` | `bfa523b3c82298bc…` | yes | `fc9ac2fa884bf23c…` |
| `experiment/environments/hedefler/SDJWT-021/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/SDJWT-021/kur.sh` | `experiment/environments/hedefler/SDJWT-021/kur.sh` | experiment/environments/SHA256SUMS | `adc1cc91852865b5…` | `adc1cc91852865b5…` | yes | `ba3ec46d04f2aa1e…` |
| `experiment/environments/hedefler/SDJWT-025/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/SDJWT-025/kur.sh` | `experiment/environments/hedefler/SDJWT-025/kur.sh` | experiment/environments/SHA256SUMS | `9ddc47e12eeb55b1…` | `9ddc47e12eeb55b1…` | yes | `47e26c8646295e09…` |
| `experiment/environments/hedefler/_bilgi-COSE-034-HEAD/ice_aktar.go` | `archive/hash-anchored/experiment/environments/hedefler/_bilgi-COSE-034-HEAD/ice_aktar.go` | `experiment/environments/hedefler/_bilgi-COSE-034-HEAD/ice_aktar.go` | experiment/environments/SHA256SUMS | `6a8a57092e9ad648…` | `6a8a57092e9ad648…` | yes | `b338c1b8e9121b07…` |
| `experiment/environments/hedefler/_bilgi-COSE-034-HEAD/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/_bilgi-COSE-034-HEAD/kur.sh` | `experiment/environments/hedefler/_bilgi-COSE-034-HEAD/kur.sh` | experiment/environments/SHA256SUMS | `1e12f72459fecf45…` | `1e12f72459fecf45…` | yes | `e9cfa5a80da250c0…` |
| `experiment/environments/hedefler/_bilgi-COSE-035-HEAD/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/_bilgi-COSE-035-HEAD/kur.sh` | `experiment/environments/hedefler/_bilgi-COSE-035-HEAD/kur.sh` | experiment/environments/SHA256SUMS | `a378437bdd92489b…` | `a378437bdd92489b…` | yes | `3c6406984b6ec211…` |
| `experiment/environments/hedefler/_bilgi-JOSE-092-rust_crypto/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/_bilgi-JOSE-092-rust_crypto/kur.sh` | `experiment/environments/hedefler/_bilgi-JOSE-092-rust_crypto/kur.sh` | experiment/environments/SHA256SUMS | `3c8c59e5e34613a9…` | `3c8c59e5e34613a9…` | yes | `6c9ce7cbe9b1a516…` |
| `experiment/environments/hedefler/_bilgi-JOSE-102-mldsa-spi/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/_bilgi-JOSE-102-mldsa-spi/kur.sh` | `experiment/environments/hedefler/_bilgi-JOSE-102-mldsa-spi/kur.sh` | experiment/environments/SHA256SUMS | `3325ae0ea9e578d8…` | `3325ae0ea9e578d8…` | yes | `7ec09ee2a553bcd3…` |
| `experiment/environments/hedefler/_bilgi-SDJWT-021-SdJwtLib/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/_bilgi-SDJWT-021-SdJwtLib/kur.sh` | `experiment/environments/hedefler/_bilgi-SDJWT-021-SdJwtLib/kur.sh` | experiment/environments/SHA256SUMS | `96e71c649598a144…` | `96e71c649598a144…` | yes | `a25f74442f3712b1…` |
| `experiment/environments/hedefler/_bilgi-SDJWT-025-ozellik/kur.sh` | `archive/hash-anchored/experiment/environments/hedefler/_bilgi-SDJWT-025-ozellik/kur.sh` | `experiment/environments/hedefler/_bilgi-SDJWT-025-ozellik/kur.sh` | experiment/environments/SHA256SUMS | `5772ec9fd8226fce…` | `5772ec9fd8226fce…` | yes | `2981417bd98db07c…` |
| `experiment/environments/imajlar/c/Dockerfile` | `archive/hash-anchored/experiment/environments/imajlar/c/Dockerfile` | `experiment/environments/imajlar/c/Dockerfile` | experiment/environments/SHA256SUMS | `622c73b3d1a2135b…` | `622c73b3d1a2135b…` | yes | `013c1bf8f4f57a2a…` |
| `experiment/environments/imajlar/dart/Dockerfile` | `archive/hash-anchored/experiment/environments/imajlar/dart/Dockerfile` | `experiment/environments/imajlar/dart/Dockerfile` | experiment/environments/SHA256SUMS | `000380abf912fa22…` | `000380abf912fa22…` | yes | `9f5bb982ffc1eab9…` |
| `experiment/environments/imajlar/dotnet/Dockerfile` | `archive/hash-anchored/experiment/environments/imajlar/dotnet/Dockerfile` | `experiment/environments/imajlar/dotnet/Dockerfile` | experiment/environments/SHA256SUMS | `669d967af37a5c73…` | `669d967af37a5c73…` | yes | `ff9bd12fdb4dde23…` |
| `experiment/environments/imajlar/elixir/Dockerfile` | `archive/hash-anchored/experiment/environments/imajlar/elixir/Dockerfile` | `experiment/environments/imajlar/elixir/Dockerfile` | experiment/environments/SHA256SUMS | `635944261caa27ff…` | `635944261caa27ff…` | yes | `752b9b7ae970c066…` |
| `experiment/environments/imajlar/go/Dockerfile` | `archive/hash-anchored/experiment/environments/imajlar/go/Dockerfile` | `experiment/environments/imajlar/go/Dockerfile` | experiment/environments/SHA256SUMS | `7f180060c9bc8f3a…` | `7f180060c9bc8f3a…` | yes | `5ea3e0a466a8628f…` |
| `experiment/environments/imajlar/jvm/Dockerfile` | `archive/hash-anchored/experiment/environments/imajlar/jvm/Dockerfile` | `experiment/environments/imajlar/jvm/Dockerfile` | experiment/environments/SHA256SUMS | `7fc30e6f56d331a0…` | `7fc30e6f56d331a0…` | yes | `d3ae1cc76653c9c1…` |
| `experiment/environments/imajlar/jvm/Yetenek.java` | `archive/hash-anchored/experiment/environments/imajlar/jvm/Yetenek.java` | `experiment/environments/imajlar/jvm/Yetenek.java` | experiment/environments/SHA256SUMS | `96cbc1cf083da9a1…` | `96cbc1cf083da9a1…` | yes | `deffae38332ce0cf…` |
| `experiment/environments/imajlar/node/Dockerfile` | `archive/hash-anchored/experiment/environments/imajlar/node/Dockerfile` | `experiment/environments/imajlar/node/Dockerfile` | experiment/environments/SHA256SUMS | `4e80ce25e9c5d3f3…` | `4e80ce25e9c5d3f3…` | yes | `b1eb3754af3c0255…` |
| `experiment/environments/imajlar/php/Dockerfile` | `archive/hash-anchored/experiment/environments/imajlar/php/Dockerfile` | `experiment/environments/imajlar/php/Dockerfile` | experiment/environments/SHA256SUMS | `396c2211296b4710…` | `396c2211296b4710…` | yes | `b9153d60f58ba5b3…` |
| `experiment/environments/imajlar/python/Dockerfile` | `archive/hash-anchored/experiment/environments/imajlar/python/Dockerfile` | `experiment/environments/imajlar/python/Dockerfile` | experiment/environments/SHA256SUMS | `7fab95a8e69260fd…` | `7fab95a8e69260fd…` | yes | `8a83482860b0a9a4…` |
| `experiment/environments/imajlar/ruby/Dockerfile` | `archive/hash-anchored/experiment/environments/imajlar/ruby/Dockerfile` | `experiment/environments/imajlar/ruby/Dockerfile` | experiment/environments/SHA256SUMS | `25d02f309ce5b12a…` | `25d02f309ce5b12a…` | yes | `33f8dafd2ae85b24…` |
| `experiment/environments/imajlar/rust/Dockerfile` | `archive/hash-anchored/experiment/environments/imajlar/rust/Dockerfile` | `experiment/environments/imajlar/rust/Dockerfile` | experiment/environments/SHA256SUMS | `2ff2125b5ef2293c…` | `2ff2125b5ef2293c…` | yes | `7a449c9fe8a07d9a…` |
| `experiment/environments/imajlar/swift/Dockerfile` | `archive/hash-anchored/experiment/environments/imajlar/swift/Dockerfile` | `experiment/environments/imajlar/swift/Dockerfile` | experiment/environments/SHA256SUMS | `5f6204395faf83e7…` | `5f6204395faf83e7…` | yes | `b2dac28d237e762f…` |
| `experiment/oracle/oracle-A/BELIRSIZ.md` | `archive/hash-anchored/experiment/oracle/oracle-A/BELIRSIZ.md` | `experiment/oracle/oracle-A/UNDETERMINED.md` | experiment/oracle/oracle-A/SHA256SUMS | `7885a9ae9528dd80…` | `7885a9ae9528dd80…` | yes | `c36fd2b16405231e…` |
| `experiment/oracle/oracle-A/KARAR-NOTLARI.md` | `archive/hash-anchored/experiment/oracle/oracle-A/KARAR-NOTLARI.md` | `experiment/oracle/oracle-A/DECISION-NOTES.md` | experiment/oracle/oracle-A/SHA256SUMS | `3aa9f994fda6f692…` | `c6017e1fa3343e26…` | no | `2adb3438ed4b040b…` |
| `experiment/oracle/oracle-A/L4-TURETME.md` | `archive/hash-anchored/experiment/oracle/oracle-A/L4-TURETME.md` | `experiment/oracle/oracle-A/L4-DERIVATION.md` | experiment/oracle/oracle-A/SHA256SUMS | `694e41863b2c7903…` | `ce96099610ce3752…` | no | `f5609b7102c0d851…` |
| `experiment/oracle/oracle-A/YONTEM.md` | `archive/hash-anchored/experiment/oracle/oracle-A/YONTEM.md` | `experiment/oracle/oracle-A/METHOD.md` | experiment/oracle/oracle-A/SHA256SUMS | `4c731e42648793ea…` | `e75a83cb95d34194…` | no | `dca57353a7912fe3…` |
| `experiment/oracle/oracle-A/adaptor-sozlesme.md` | `archive/hash-anchored/experiment/oracle/oracle-A/adaptor-sozlesme.md` | `experiment/oracle/oracle-A/adapter-contract.md` | experiment/oracle/oracle-A/SHA256SUMS | `922512fd65ce5679…` | `6d6a6e0d45049a3a…` | no | `aa2debc288bdf70f…` |
| `experiment/oracle/oracle-A/ayrisma-dedektoru.md` | `archive/hash-anchored/experiment/oracle/oracle-A/ayrisma-dedektoru.md` | `experiment/oracle/oracle-A/divergence-detector.md` | experiment/oracle/oracle-A/SHA256SUMS | `a2b9fa2ae233039a…` | `a092bd71a84561e6…` | no | `dba8e2614573e956…` |
| `experiment/oracle/oracle-B/BELIRSIZ.md` | `archive/hash-anchored/experiment/oracle/oracle-B/BELIRSIZ.md` | `experiment/oracle/oracle-B/UNDETERMINED.md` | experiment/oracle/oracle-B/SHA256SUMS | `87ea3893ef17bfe6…` | `87ea3893ef17bfe6…` | yes | `8077656ee1143a18…` |
| `experiment/oracle/oracle-B/ERISIM-KAYDI.md` | `archive/hash-anchored/experiment/oracle/oracle-B/ERISIM-KAYDI.md` | `experiment/oracle/oracle-B/ACCESS-LOG.md` | experiment/oracle/oracle-B/SHA256SUMS | `d0989d1dd3934f8c…` | `f5c64307c48f377e…` | no | `3b818207c52745a8…` |
| `experiment/oracle/oracle-B/KARAR-NOTLARI.md` | `archive/hash-anchored/experiment/oracle/oracle-B/KARAR-NOTLARI.md` | `experiment/oracle/oracle-B/DECISION-NOTES.md` | experiment/oracle/oracle-B/SHA256SUMS | `377e5c953e304055…` | `b709542b76380e5f…` | no | `07fd39b2d266c74b…` |
| `experiment/oracle/oracle-B/L4-TURETME-B.md` | `archive/hash-anchored/experiment/oracle/oracle-B/L4-TURETME-B.md` | `experiment/oracle/oracle-B/L4-DERIVATION-B.md` | experiment/oracle/oracle-B/SHA256SUMS | `59d27102f85dcb05…` | `51ac17d37968764e…` | no | `d0667a5b2b4aecf4…` |
| `experiment/oracle/oracle-B/YONTEM.md` | `archive/hash-anchored/experiment/oracle/oracle-B/YONTEM.md` | `experiment/oracle/oracle-B/METHOD.md` | experiment/oracle/oracle-B/SHA256SUMS | `8430759d1fb1d1cd…` | `7284ed226f572926…` | no | `75ecd3e5997314ad…` |
| `experiment/statistics/SEMA.md` | `archive/hash-anchored/experiment/statistics/SEMA.md` | `experiment/statistics/SCHEMA.md` | experiment/statistics/SHA256SUMS | `92bb18b74592a517…` | `cb1979cc712fd55b…` | no | `5505d6c2128bfd0a…` |
| `experiment/statistics/betikler/c3istat/analiz.py` | `archive/hash-anchored/experiment/statistics/betikler/c3istat/analiz.py` | `experiment/statistics/betikler/c3istat/analiz.py` | experiment/statistics/SHA256SUMS | `39f206acd30dfe5b…` | `39f206acd30dfe5b…` | yes | `794f1da5672b79b9…` |
| `experiment/statistics/betikler/c3istat/rapor.py` | `archive/hash-anchored/experiment/statistics/betikler/c3istat/rapor.py` | `experiment/statistics/betikler/c3istat/rapor.py` | experiment/statistics/SHA256SUMS | `7de41aa0be63011f…` | `7de41aa0be63011f…` | yes | `c2448fb97f3aef1e…` |
| `experiment/statistics/betikler/c3istat/yapilandirma.py` | `archive/hash-anchored/experiment/statistics/betikler/c3istat/yapilandirma.py` | `experiment/statistics/betikler/c3istat/yapilandirma.py` | experiment/statistics/SHA256SUMS | `b0b980421e4cf6ae…` | `5d31179b8f554710…` | no | `88ec153a62be7373…` |
| `experiment/statistics/kaynak/NEWCOMBE-KAYNAK.md` | `archive/hash-anchored/experiment/statistics/kaynak/NEWCOMBE-KAYNAK.md` | `experiment/statistics/kaynak/NEWCOMBE-SOURCE.md` | experiment/statistics/SHA256SUMS | `a9eaf810614fd15f…` | `62a68c9bf41ce57c…` | no | `6e25f6e04a2f3f08…` |
| `experiment/statistics/sentetik-testler/test_uctan_uca.py` | `archive/hash-anchored/experiment/statistics/sentetik-testler/test_uctan_uca.py` | `experiment/statistics/sentetik-testler/test_uctan_uca.py` | experiment/statistics/SHA256SUMS | `e9539f26d0d35966…` | `e9539f26d0d35966…` | yes | `5f9d9522eda896a3…` |
| `experiment/statistics/tumunu_calistir.sh` | `archive/hash-anchored/experiment/statistics/tumunu_calistir.sh` | `experiment/statistics/tumunu_calistir.sh` | experiment/statistics/SHA256SUMS | `65df0818d2a54fcf…` | `c4ac60755b0f2ca2…` | no | `722578b66f68633b…` |
| `models/known-answer-tests/ADIM06-RAPOR.md` | `archive/hash-anchored/models/known-answer-tests/ADIM06-RAPOR.md` | `models/known-answer-tests/STEP06-REPORT.md` | models/known-answer-tests/SHA256SUMS | `7b9fbafa884b54fc…` | `d32e74d16cde6e6d…` | no | `3e09ad6487fa0726…` |
| `models/known-answer-tests/ESLEME.md` | `archive/hash-anchored/models/known-answer-tests/ESLEME.md` | `models/known-answer-tests/MAPPING.md` | models/known-answer-tests/SHA256SUMS, models/known-answer-tests/dnssec/HAZIRLIK_SHA256SUMS | `8576c074039943c0…` | `958429ecaa9f3bc3…` | no | `fd284c335c4818ba…` |
| `models/known-answer-tests/SONUC.md` | `archive/hash-anchored/models/known-answer-tests/SONUC.md` | `models/known-answer-tests/RESULTS.md` | models/known-answer-tests/SHA256SUMS | `839ea1d5efd3ef12…` | `e8e09684d675e90b…` | no | `95d9005f2a827d0d…` |
| `models/known-answer-tests/dnssec/tamarin_kos_v2.py` | `archive/hash-anchored/models/known-answer-tests/dnssec/tamarin_kos_v2.py` | `models/known-answer-tests/dnssec/tamarin_kos_v2.py` | models/known-answer-tests/SHA256SUMS | `c19f697294e8b5f1…` | `797d85838be9d3a4…` | no | `4919686b01f21ecc…` |
| `models/known-answer-tests/dnssec/yanyana_v1_v2.py` | `archive/hash-anchored/models/known-answer-tests/dnssec/yanyana_v1_v2.py` | `models/known-answer-tests/dnssec/yanyana_v1_v2.py` | models/known-answer-tests/SHA256SUMS | `777c1b86e06bcb3a…` | `148559abee761d0c…` | no | `f04b0264b1a6b193…` |
| `models/known-answer-tests/kor-beklenen/BELIRSIZ.md` | `archive/hash-anchored/models/known-answer-tests/kor-beklenen/BELIRSIZ.md` | `models/known-answer-tests/kor-beklenen/UNDETERMINED.md` | models/known-answer-tests/kor-beklenen/SHA256SUMS | `15bce46215044e91…` | `990039d6a1b749cc…` | no | `f7edd4bf5fc8384d…` |
| `models/known-answer-tests/kor-beklenen/ERISIM-KAYDI.md` | `archive/hash-anchored/models/known-answer-tests/kor-beklenen/ERISIM-KAYDI.md` | `models/known-answer-tests/kor-beklenen/ACCESS-LOG.md` | models/known-answer-tests/kor-beklenen/SHA256SUMS | `bc24a18fcbb9e1c6…` | `b65a7eb64a3461c3…` | no | `624f02efa6d6f215…` |
| `models/known-answer-tests/kor-beklenen/GIRDI/KAT-KOR-GIRDI.md` | `archive/hash-anchored/models/known-answer-tests/kor-beklenen/GIRDI/KAT-KOR-GIRDI.md` | `models/known-answer-tests/kor-beklenen/GIRDI/KAT-BLIND-INPUT.md` | models/known-answer-tests/kor-beklenen/GIRDI/GIRDI.sha256 | `1b0dac3876b7a618…` | `723acd3277961be6…` | no | `112b43d5cbdaad1c…` |
| `models/known-answer-tests/kor-beklenen/TURETME.md` | `archive/hash-anchored/models/known-answer-tests/kor-beklenen/TURETME.md` | `models/known-answer-tests/kor-beklenen/DERIVATION.md` | models/known-answer-tests/kor-beklenen/SHA256SUMS | `fa138b1069fca7cb…` | `96c3ac20d6ea1c91…` | no | `c9482402466431d7…` |
| `models/known-answer-tests/nsurum/NSURUM-KARSILASTIRMA.md` | `archive/hash-anchored/models/known-answer-tests/nsurum/NSURUM-KARSILASTIRMA.md` | `models/known-answer-tests/nsurum/N-VERSION-COMPARISON.md` | models/known-answer-tests/nsurum/SHA256SUMS | `43b7a58cf8788fd3…` | `c68db6027987a496…` | no | `380d5dd47ea2222e…` |
| `models/known-answer-tests/nsurum/kat_nsurum.py` | `archive/hash-anchored/models/known-answer-tests/nsurum/kat_nsurum.py` | `models/known-answer-tests/nsurum/kat_nsurum.py` | models/known-answer-tests/nsurum/SHA256SUMS | `ab444834dee8ee8e…` | `81b9687b350899a4…` | no | `b9797031ab2a9b1f…` |
| `models/mechanisms/ON-KAYIT-GEREKCE.md` | `archive/hash-anchored/models/mechanisms/ON-KAYIT-GEREKCE.md` | `models/mechanisms/PRE-REGISTRATION-RATIONALE.md` | models/mechanisms/SHA256-ON-KAYIT.txt | `d5da725136307d35…` | `716188bb159afbea…` | no | `2a8ab4431d7329c5…` |
| `models/sampling/teknik-kapi/cevir.py` | `archive/hash-anchored/models/sampling/teknik-kapi/cevir.py` | `models/sampling/teknik-kapi/cevir.py` | models/sampling/teknik-kapi/SHA256SUMS, models/sampling/teknik-kapi/on_ceviri.sha256 | `08fb5fbc2ca5cabe…` | `49189649783b5c8d…` | no | `caaf6caad82af8f2…` |

127 files are archived. Full digests: `sha256sum archive/hash-anchored/<path>` and the records.

## 3. How to verify

```
python tools/verify_anchors.py            # summary per record; exit code 0 = no failure
python tools/verify_anchors.py --list     # also list every entry that is not matched by the current file
```

The script (standard library only) reads every SHA-256 record and checks each entry against the
current file, then against the archived copy, then against `ANCHOR-NOTES.tsv`. Paths written in the
old folder layout (`model/...`, `deney/...`, absolute paths of the working copy) are resolved with the
table of `docs/PATHS.md`. A single record can also be checked by hand, for example:

```
cd archive/hash-anchored/experiment/oracle/oracle-A && grep BELIRSIZ.md ../../../../../experiment/oracle/oracle-A/SHA256SUMS | sha256sum -c -
```

Output of `python tools/verify_anchors.py` on this release:

```
SHA-256 record check (tools/verify_anchors.py)
record | entries | current | archived | noted | FAIL
data/eu-lotl_seq394.xml.sha256 | 1 | 1 | 0 | 0 | 0
experiment/environments/SHA256SUMS | 559 | 460 | 84 | 15 | 0
experiment/oracle/oracle-A/SHA256SUMS | 11 | 4 | 1 | 6 | 0
experiment/oracle/oracle-B/SHA256SUMS | 7 | 1 | 1 | 5 | 0
experiment/statistics/SHA256SUMS | 30 | 16 | 3 | 11 | 0
experiment/statistics/sonuclar/ornek_analiz_sha256.txt | 2 | 2 | 0 | 0 | 0
experiment/vector-generator/anahtarlar/v1.3/SHA256SUMS | 5 | 5 | 0 | 0 | 0
experiment/vector-generator/anahtarlar/v1/SHA256SUMS | 71 | 71 | 0 | 0 | 0
experiment/vector-generator/vektorler/v1.1/SHA256SUMS | 103 | 103 | 0 | 0 | 0
experiment/vector-generator/vektorler/v1.2/SHA256SUMS | 156 | 156 | 0 | 0 | 0
experiment/vector-generator/vektorler/v1.3/SHA256SUMS | 203 | 203 | 0 | 0 | 0
experiment/vector-generator/vektorler/v1.4/SHA256SUMS | 233 | 233 | 0 | 0 | 0
experiment/vector-generator/vektorler/v1/SHA256SUMS | 96 | 96 | 0 | 0 | 0
models/asp/sorgular/beklenti_2x2.sha256 | 1 | 1 | 0 | 0 | 0
models/asp/sorgular/stratejiler_taslak.sha256 | 1 | 0 | 0 | 1 | 0
models/known-answer-tests/SHA256SUMS | 712 | 689 | 0 | 23 | 0
models/known-answer-tests/dnssec/HAZIRLIK_SHA256SUMS | 319 | 299 | 0 | 20 | 0
models/known-answer-tests/kor-beklenen/GIRDI/GIRDI.sha256 | 2 | 1 | 0 | 1 | 0
models/known-answer-tests/kor-beklenen/SHA256SUMS | 4 | 1 | 0 | 3 | 0
models/known-answer-tests/nsurum/SHA256SUMS | 3 | 1 | 0 | 2 | 0
models/mechanisms/SHA256-ON-KAYIT.txt | 11 | 8 | 0 | 3 | 0
models/mechanisms/kesif/on_kayit.sha256 | 4 | 4 | 0 | 0 | 0
models/mechanisms/tau_israf/on_kayit.sha256 | 4 | 4 | 0 | 0 | 0
models/sampling/5b/on_ceviri.sha256 | 3 | 3 | 0 | 0 | 0
models/sampling/teknik-kapi/SHA256SUMS | 110 | 107 | 0 | 3 | 0
models/sampling/teknik-kapi/on_ceviri.sha256 | 14 | 13 | 0 | 1 | 0
models/tamarin/sonuc/h3_sadelestirme/sha256.txt | 2 | 1 | 0 | 1 | 0
models/tamarin/sonuc/on_kayit_adim5a_kesif.sha256.txt | 2 | 2 | 0 | 0 | 0
models/tamarin/sonuc/on_kayit_adim5a_varyantlar.sha256.txt | 1 | 0 | 0 | 1 | 0
models/tamarin/sonuc/sha256.txt | 15 | 11 | 0 | 4 | 0
models/tamarin/sonuc/sha256_adim5a.txt | 19 | 14 | 0 | 5 | 0
TOTAL 31 records | 2704 entries | current 2510 | archived 89 | noted 105 | FAIL 0
```

## 4. Hard-coded digests and scripts that check records

| Where | What is checked | State in this release |
|---|---|---|
| `experiment/oracle/oracle-A/karar_uret.py` (`BEKLENEN`) | pre-registration draft (outside the repository), v1.2 `MANIFEST.json` and `SHA256SUMS`, `BATARYA-ESLEME.md` | unchanged files; still valid |
| `models/known-answer-tests/{dnssec,x509,smime}/kos.py` (`CEKIRDEK_BEKLENEN`) | `models/asp/cekirdek.lp` | model file not changed; still valid |
| `models/mechanisms/betik/calistir.sh`, `kesif/calistir.sh`, `tau_israf/calistir.sh`, `models/sampling/teknik-kapi/betik/calistir.sh` | run `sha256sum -c` on their record and only log the result | the logged check reports the entries listed as `noted` above; verify with `tools/verify_anchors.py` |
| `experiment/statistics/betikler/c3istat/analiz.py` (`betik_sha256` in `sonuc.json`) | digests of the statistics scripts at the time of each recorded analysis | recorded outputs keep the digests of the scripts that produced them |
| `experiment/runs/adapters/_py/adaptor.py` (`adaptor_sha256` in the output rows) | digest of the adapter source at run time | recorded outputs keep the digests of the sources that produced them; a rerun records the new digest |

