# ERİŞİM KAYDI — Oracle B (Adım 9, görev 6)

> Bağımsızlık kanıtı. Oracle B'nin açtığı, listelediği ya da özetini aldığı **her** dosya ve dizin burada, açılma sırasıyla yazılır.
> Saatler yerel saattir (+03:00). Proje kökü: `C:\Users\tuncer\Desktop\Sefa\PQ-OID4VC` (aşağıda `./`).
>
> **Hiç açılmayanlar (beyan):** `experiment/oracle/oracle-A/` (listelenmedi, okunmadı); `experiment/oracle/` kökündeki başka dosyalar (dizin listelenmedi; yalnız `mkdir -p experiment/oracle/oracle-B` çalıştırıldı); `referans/` (hiçbir alt dizini açılmadı); `model/`; `gozden-gecirme/`; `IS-PLANI.md`. Ağ erişimi yok. Hedef kütüphane koşulmadı. Docker ve git kullanılmadı.

## 1. Dizin listelemeleri (yalnız ad, içerik değil)

| # | Saat | Komut | Kapsam |
|---|---|---|---|
| 1 | 15:3x | `ls -la` | `./` (kök: `.git/`, `00-on-kayit/`, `spec-corpus/`, `traceability/`, `threat-model/`, `proje notları`, `IS-PLANI.md`, `tools/`, `experiment/`, `gozden-gecirme/`, `literatur/`, `model/`, `referans/`, `data/` adları görüldü; içleri açılmadı) |
| 2 | 15:3x | `ls -la` | `./00-on-kayit/` |
| 3 | 15:3x | `ls -la` | `./spec-corpus/` ve `./spec-corpus/metin/` |
| 4 | 15:3x | `ls -la` | `./traceability/` |
| 5 | 15:3x | `ls -la` | `./experiment/` (alt dizin adları: `inventory/`, `signer/`, `statistics/`, `environments/`, `uretec/`; `experiment/oracle/` o anda listede yoktu) |
| 6 | 15:3x | `ls -la` | `./experiment/vector-generator/` |
| 7 | 15:3x | `ls -la` | `./experiment/vector-generator/vektorler/` ve `./experiment/vector-generator/vektorler/v1.2/` |

## 2. Açılan dosyalar

| # | Saat | Dosya | Kapsam | Araç |
|---|---|---|---|---|
| 1 | 15:3x | `00-on-kayit/ON-KAYIT-TASLAK.md` | `grep -n "^#"` (başlıklar) | grep |
| 2 | 15:3x | aynı | satır 1–210 (başlık bloğu, §0–§2, §2A Ö1–Ö12; Ö6 dahil) | Read |
| 3 | 15:3x | aynı | satır 211–272 (§2B) | Read |
| 4 | 15:3x | aynı | satır 368–489 (§2D; A bölümü m.1–8 **ve** B bölümü m.9–17 aynı parçada göründü — B bölümü biçimsel kısım sonuçlarıdır, oracle türetmesinde kullanılmadı; yalnız m.10'daki G5 biçim adları not edildi, bkz. `L4-TURETME-B.md` §0) | Read |
| 5 | 15:3x | aynı | satır 490–669 (§2E, §2F, §2G, §3.1–§3.7; §3.2–§3.6 aynı parçada göründü) | Read |
| 6 | 15:3x | aynı | satır 758–781 (§4.7 G1–G5, §4.8 P0–P4) | Read |
| 7 | 15:3x | aynı | satır 836–883 (§4.13, §4.14, §4.15) | Read |
| 8 | 15:3x | aynı | satır 939–948 (§4.20) | Read |
| 9 | 15:3x | aynı | satır 1039–1118 (§6.4, §6.5, §6.6–§6.11) | Read |
| 10 | 15:3x | aynı | `grep -n -i "MR4\|L4c\|L4m\|oracle\|..."` — eşleşen satırlar (364 = §2C m.4 ad düzeltmesi; 888, 1232, 1259, 1270, 1307 tek satır olarak) | grep |
| 11 | 15:3x | `experiment/vector-generator/BATARYA-ESLEME.md` | tamamı | Read |
| 12 | 15:3x | `experiment/vector-generator/vektorler/v1.2/MANIFEST.json` | tamamı, Python `json` ile (üst alanlar + 153 vektör) | python |
| 13 | 15:3x | SHA-256: `v1.2/MANIFEST.json`, `v1.2/SHA256SUMS`, `BATARYA-ESLEME.md`, `ON-KAYIT-TASLAK.md` | yalnız özet | sha256sum |
| 14 | 15:4x | çalışma dökümleri (scratchpad, proje dışı): `manifest_dokum.txt`, `manifest_sikisik.txt` | MANIFEST.json'dan Python ile üretilen okunabilir dökümler; proje klasörüne yazılmadı | python |
| 15 | 15:4x | `spec-corpus/metin/JWTBCP.txt` (draft-ietf-oauth-rfc8725bis-10) | baş (1–60), bölüm listesi, satır 239–907 (§1.2–§6.1) | Read/grep |
| 16 | 15:4x | `spec-corpus/metin/JOSECOMP.txt` (draft-ietf-jose-pq-composite-sigs-04) | baş, bölüm listesi, satır 136–1183 (§1–§7.1.3) | Read/grep |
| 17 | 15:4x | `spec-corpus/metin/RFC9964.txt` | baş, bölüm listesi, satır 82–341 (§1–§8.1) | Read/grep |
| 18 | 15:4x | `spec-corpus/metin/RFC7515.txt` | bölüm listesi, satır 464–743, 753–1142, 1500–1559 | Read/grep |
| 19 | 15:4x | `spec-corpus/metin/RFC9864.txt` | baş, bölüm listesi, satır 97–246, 332–376, 514–583, 629–672 | Read/grep |
| 20 | 15:5x | `spec-corpus/metin/RFC9901.txt` | bölüm listesi, satır 484–553, 904–977, 1642–2095, 2263–2337 | Read/grep |
| 21 | 15:5x | `spec-corpus/metin/SDJWTVC.txt` (-19) | baş, bölüm listesi, satır 293–352, 978–1067; `grep typ`; değişiklik günlüğü satır 3608–3625 | Read/grep |
| 22 | 15:5x | `spec-corpus/metin/SDJWTVC13.txt` (-13) | baş, bölüm listesi, satır 278–347, 694–783 | Read/grep |
| 23 | 15:5x | `spec-corpus/metin/HAIP.txt` (1.0 Final) | bölüm listesi, satır 186–633 | Read/grep |
| 24 | 15:5x | `spec-corpus/metin/OID4VP.txt` (1.0 Final) | bölüm listesi, Ek A satır 2434–2683; `grep` ile satır 605, 862, 882–894, 945–947 | Read/grep |
| 25 | 15:5x | `traceability/` | `head -c 3000 izlenebilirlik.csv`; Python ile sütun ve dağılım özeti; seçili belgelerin satırları (kimlik, belge, bölüm, anahtar sözcük, alıntının ilk 200–230 karakteri). **Düzeltme:** `head -c 3000` çıktısında T001–T008'in (LOTL/TL konulu; oracle ile ilgisiz) `not` sütunu da göründü; bunun dışında `not` sütunu listelenmedi. `OZET.md`, `kapsama_tablolari.md`, betikler açılmadı | head/python |
| 26 | 16:0x | `spec-corpus/metin/RFC9449.txt` | satır 393–527 (§4.2–§4.3) | Read/grep |
| 27 | 16:0x | `spec-corpus/metin/TSL.txt` (draft-ietf-oauth-status-list-21) | baş, satır 747–794 (§5.1) | Read/grep |
| 28 | 16:0x | `spec-corpus/metin/RFC9101.txt` | `grep`, satır 925–946 | Read/grep |
| 29 | 16:0x | `spec-corpus/metin/ACM2.txt` | `grep` (Note 50/51, satır 944–946) | grep |
| 30 | 16:0x | `spec-corpus/metin/LAMPSCOMP.txt` (draft-ietf-lamps-pq-composite-sigs-19) | `grep`, satır 1256–1365 (§4.3), 3405–3444 (Ek A) | Read/grep |
| 31 | 16:0x | SHA-256: atıf yapılan 15 korpus dosyası + `izlenebilirlik.csv` | yalnız özet (YONTEM.md §8'e yazıldı) | sha256sum |
| 32 | 16:1x–16:4x | `turet_karar.py` koşumları (hata ayıklama dahil 9 kez: sözdizimi/alıntı aralığı düzeltmeleri, 4 kol birikimli üretim, son iki koşum bayt-aynı çıktı) | Betik şunları **programla** okur: `MANIFEST.json` (tamamı); alıntı denetimi için ÖK ve 14 korpus metninin (JWTBCP, JOSECOMP, LAMPSCOMP, RFC9964, RFC7515, RFC9864, RFC9901, SDJWTVC, SDJWTVC13, HAIP, OID4VP, RFC9449, TSL, ACM2) tamamı. Vektör dosyası açmaz | python |
| 33 | 16:4x | `L4-TURETME-B.md` ve `BELIRSIZ.md` alıntı doğrulama parçacıkları | Aynı 12 belgede tam metin alt dize araması | python |
| 34 | 16:4x | `karar.tsv` | Kendi çıktısının denetimi (anahtar tekliği, değer kümeleri, dayanak biçimi, 153 vektör kapsaması; manifest ile karşılaştırma) | python |

## 3. Açılmayanlar (ek beyan)

- `experiment/vector-generator/vektorler/v1.2/` altındaki **hiçbir vektör dosyası** (`T/`, `CMP/`, `X5C/`, `VC/`, `VP/`, `REQ/`, `TSL/`, `DPOP/`, `CRIT/`, `UNK/`, `K10/`, `V/`, `b-uyumlu/`) açılmadı; `MANIFEST.csv` ve `anahtarlar/` açılmadı.
- `experiment/vector-generator/README.md`, `uretec/`, `testler/`, `sonuclar/`, `Dockerfile` açılmadı.
- `experiment/inventory/`, `experiment/signer/`, `experiment/statistics/`, `experiment/environments/` açılmadı (yalnız adları `ls deney` çıktısında göründü).
- `spec-corpus/` altında `metin/` dışındaki dosyalar açılmadı; `threat-model/`, `literatur/`, `data/`, `tools/`, `proje notları` (proje kökü) açılmadı.

## 4. Yazılan dosyalar (yalnız `experiment/oracle/oracle-B/`)

`ERISIM-KAYDI.md`, `YONTEM.md`, `turet_karar.py`, `karar.tsv`, `L4-TURETME-B.md`, `BELIRSIZ.md`, `KARAR-NOTLARI.md`, `SHA256SUMS`. Geçici dökümler oturumun scratchpad klasöründe (proje dışı).
