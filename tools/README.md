# tools/ — Adım 2: araç zinciri (konteynerler)

Bütün biçimsel araçlar Linux konteynerinde koşar. Windows Uygulama Denetimi, ana makinede clingo'nun yerel DLL'ini engelliyor.

## İmajlar

| İmaj | İçerik | Kimlik (23.09.2026) |
|---|---|---|
| `pq-a02-tamarin:1.12.0` | Tamarin 1.12.0 (resmî linux64 ikilisi) + Maude 3.5.1 (resmî) | `sha256:7dd7a72d…` |
| `pq-a02-solver:1.0` | clingo 5.8.2 + z3-solver 5.1.0.0 (PyPI) | `sha256:5909c48b…` |

**Taban imaj** (her iki Dockerfile'da özetle sabit): `python:3.11-slim@sha256:9534e5a8e315485d4061ed659af0fd78a284c015f9b73661b41d6bab25604534`

**İndirilen ikililer** (GitHub release digest'leriyle doğrulandı; `tamarin/indir/beklenen.sha256`):

| Dosya | SHA-256 |
|---|---|
| `tamarin-prover-1.12.0-linux64-ubuntu.tar.gz` | `201be06f469e47cff554df6ca93db8366fc2c69d70c61fcbd1370a1074b469c6` |
| `Maude-3.5.1-linux-x86_64.zip` | `72ed1ca87e3b3d0dfc6ee1436baf154bf04c45ff97d521bec040c5e8dfc8f92c` |
| Çıkarılmış `tamarin-prover` | `9d3fcbaa65aeea244cff5b8074338d129427161cc8b02e5aee72d30ee072acc9` |
| Çıkarılmış `maude` | `9dd4044e693944aae97ad72086bc70275fa34bf635f9b377a5b2100bf3ed8655` |

**ProVerif 2.05** (`pq-a02-proverif:2.05`, kimlik `sha256:9d15c7a7…`, ≈51 MB):
- Resmî kaynak arşivinden **arayüzsüz** derlendi (`./build -nointeract`); çok aşamalı derleme.
- Kaynak arşivi `proverif2.05.tar.gz`, SHA-256 `4871f53c32ab4a04669a060c4886ba5d9080496963fb980a9a62d2c429ceabc4`. Kaynak: `https://bblanche.gitlabpages.inria.fr/proverif/`.
- opam yolu kullanılmadı. Gerekçe: opam paketi `lablgtk`'ye zorunlu bağımlı; bu yüzden `--no-depexts` ile derleme başarısız olur. Varsayılan hâliyle de izinsiz GTK paketleri çeker ve 3,2 GB'lık bir imaj üretir.

## Kullanım (Git Bash)

Derleme:
```
sh tools/build.sh
```

Tamarin'i bellek sınırıyla koşmak için (her ağır işte zorunlu):
```
MSYS_NO_PATHCONV=1 docker run --rm --memory=12g --memory-swap=12g -v "$(cygpath -m "$PWD/models/tamarin"):/work" pq-a02-tamarin:1.12.0 tamarin-prover --prove /work/<dosya>.spthy
```

Çözücüleri koşmak için:
```
MSYS_NO_PATHCONV=1 docker run --rm -v "$(cygpath -m "$PWD/models/asp"):/work" -w /work pq-a02-solver:1.0 python <betik>.py
```

## Kabul testi (`test/calistir.sh`)

Test, B'nin pilotlarını yeni imajlarla yeniden üretir. Sonuç (23.09.2026): **birebir aynı.**

| Test | Beklenen (B) | Gözlenen |
|---|---|---|
| V1 base | falsified (8) | falsified (8), 1,2 s, 108 MiB |
| V2 expectTL | falsified (8) | falsified (8) |
| V3 tlPQ | falsified (9) | falsified (9) |
| V4 tlPQ + expectTL | verified (12) | verified (12) |
| V5 tlPQ + nocoexist | verified (7) | verified (7) |
| V6 tlClassical + nocoexist | falsified (8) | falsified (8) |
| L2 `[use_induction]` | verified (20) | verified (20), 0,27 s |
| L1 tümevarımsız | zaman aşımı | 60 s'de zaman aşımı, 1.976 MiB (bellek sınırı çalışıyor) |
| P2 ASP + z3 | 48 sorgu, 48/48 uyum, tek optimum sıra | 48 sorgu 0,028 s; z3–clingo **48/48**; optimum sıra 1 |
| P1b ProVerif, 4 varyant | 1 true, 1 false, 2 "cannot be proved" | Aynı (TLpq+required: true; TLpq+none: false; TLclassical: 2× cannot be proved) |

Ham çıktılar: `test/sonuc/`, `test/p1/out_*.txt`, `test/p2/`.

## Docker protokolü

- Açılıştaki imaj ve konteyner listesi: `docker_images_once_2026-09-23.txt`, `docker_ps_once_2026-09-23.txt`. Bu listelerdeki imajlara ve konteynerlere **dokunulmaz** (ör. `cql-xlate`).
- Projenin imajları `pq-` önekini taşır. Proje bitince ya da kullanıcı isterse şöyle silinir:
  ```
  docker rmi $(docker images --format '{{.Repository}}:{{.Tag}}' | grep '^pq-')
  ```
- Çalışma oturumu biterken Docker Desktop kapatılır: `docker desktop stop`.
