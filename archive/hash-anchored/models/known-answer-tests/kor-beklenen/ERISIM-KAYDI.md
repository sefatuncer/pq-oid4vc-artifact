# Erişim kaydı: kör türetme çalışması (kat-kor, Adım 6 görev 0)

Açılan her dosya aşağıda yol ve nedeniyle listelenir. Yollar proje köküne (`PQ-OID4VC/`) göredir.

| # | Yol | Nasıl | Neden |
|---|---|---|---|
| 1 | `model/known-answer-tests/kor-beklenen/` ve `GIRDI/` | `ls` (yalnız dizin listesi) | Çıktı klasörünü ve girdi dosyalarını bulmak. `model/` altında başka dizin listelenmedi |
| 2 | `model/known-answer-tests/kor-beklenen/GIRDI/OKUBENI.md` | tam okuma | Girdinin nasıl hazırlandığını öğrenmek (izinli) |
| 3 | `model/known-answer-tests/kor-beklenen/GIRDI/KAT-KOR-GIRDI.md` | tam okuma | Hücre tanımları, girdi sözlüğü, değer sözlüğü (izinli) |
| 4 | Birincil kaynaklar ve `00-on-kayit/ON-KAYIT-TASLAK.md` | `wc -l` (yalnız satır sayısı) | Boyut kontrolü. ÖK'de yalnız başlık satırları `grep "^#"` ile tarandı; §4.19'un yerini bulmak için |
| 5 | `00-on-kayit/ON-KAYIT-TASLAK.md` satır 830–840 | kısmi okuma | Yalnız §4.19 (geçme ölçütü). Diğer bölümler okunmadı |

**Açılmayan dosyalar:** `GIRDI/kat_redakte.py` ve `GIRDI/GIRDI.sha256` dizin listesinde göründü, ama açılmadı. Redaksiyon betiği izinli listede değil; beklenen değerlere dair ipucu taşıyabilir.

## Oturum 1 (24.09.2026) devamı: KAT-1 birincil kaynakları

| # | Yol | Nasıl | Neden |
|---|---|---|---|
| 6 | `spec-corpus/metin/RFC6840.txt` | `grep` bölüm başlıkları; satır 430–709 ve 985–1074 okundu | KAT-1: §5.4, §5.10, §5.11, §5.12, §6.2, Ek C.2 |
| 7 | `spec-corpus/metin/RFC6781.txt` | `grep` bölüm başlıkları; satır 1188–1332, 1460–1659, 1840–1989, 2133–2182 okundu | KAT-1: §4.1.2 Double-DS (Şekil 5), §4.1.4 algoritma geçişi (Şekil 8), §4.2.1–4.2.3 anahtar ele geçirilmesi, §4.3.4 DS imza geçerlilik süresi |
| 8 | `spec-corpus/metin/RFC9955.txt` | başlık (ilk 30 satır) + `grep` bölüm başlıkları; satır 366–495 ve 1105–1154 okundu | Ayrılabilirlik ve bileşen atlama: §1.3.1, §1.3.3, §1.3.4, §6.2 |
| 9 | Kendi çıktılarım: `BEKLENEN-KOR.tsv`, `TURETME.md` | `ls`, `wc`, `tail`, `awk` | Kesintiden sonra durum doğrulaması |
| 10 | Yardımcı betik `scratchpad/kat1.sh` (oturum geçici klasörü) | yazıldı ve koşuldu | Yalnız TSV satırlarını `printf` ile eklemek için. Model ya da araç değil |

## Oturum 2 (25.09.2026): kullanım limiti kesintisinden sonra devam

| # | Yol | Nasıl | Neden |
|---|---|---|---|
| 11 | Kendi çıktılarım (`BEKLENEN-KOR.tsv`, `TURETME.md`, `BELIRSIZ.md`, `ERISIM-KAYDI.md`) | `ls`, `wc`, `tail`, `awk` | Kesintiden sonra durum doğrulaması |
| 12 | `literatur/metin/kim2026_x509_hybrid.txt` | tam okuma (satır 1–577) | KAT-2: §II–VIII, Tablo IV/V/VI/VII |
| 13 | `literatur/metin/lee2026_eprint1416.txt` | tam okuma (satır 1–298) | KAT-2: §4.1, §4.3, §4.4, §4.5, §6 |
| 14 | `literatur/metin/han2026_nothing_breaks.txt` | ilk 3000 bayt + anahtar sözcük `grep`'i (continuity, downgrade, strip, replay vb.) | Konu ve ilgi kontrolü. SSH/TLS anahtar değişimiyle ve çalışmaların yol açtığı downgrade'lerle ilgili; hiçbir hücre değerinin dayanağı değil |
| 15 | Yardımcı betik `scratchpad/kat2.sh` (oturum geçici klasörü) | Write ile yazıldı ve koşuldu | Yalnız TSV satırlarını `printf` ile eklemek için |
| 16 | `literatur/metin/das2026_smime_eprint1374.txt` | `grep` bölüm başlıkları; satır 120–235 okundu | KAT-3: §3 biçimsel model, Denklem (5)–(8), Önerme 1, §3.1 Aşama 1–5, Tablo 1 |
| 17 | Yardımcı betik `scratchpad/kat3.sh` (oturum geçici klasörü) | Write ile yazıldı ve koşuldu | Yalnız TSV satırlarını `printf` ile eklemek için |
| 18 | Yardımcı betik `scratchpad/alinti_denetle.py` (oturum geçici klasörü) | Write ile yazıldı, Python 3.11 ile koşuldu | Alıntı denetimi. Yalnız yukarıdaki 6 birincil dosyayı ve kendi TSV'mi okur; metin karşılaştırması yapar |
| 19 | `kim2026`, `das2026`, `RFC6781`, `RFC6840` | `grep -n -F` ile sabit dize araması | TURETME'deki metin içi satır atıflarının örneklem denetimi |

## Açılmayan ve okunmayan dosyalar (bağımsızlık beyanı)

Aşağıdakilerin hiçbiri açılmadı, listelenmedi ve `grep` ile taranmadı:
- `literatur/analiz/` (KAT-SPEC.md dahil),
- `model/` altında `kor-beklenen/` dışındaki her şey,
- `gozden-gecirme/`, `referans/` (pilotlar dahil), `experiment/`,
- `IS-PLANI.md`, proje `proje notları`'si, `KARAR-NOTLARI.md`.

Ayrıca:
- `GIRDI/kat_redakte.py` ve `GIRDI/GIRDI.sha256` açılmadı.
- `spec-corpus/metin/RFC5280.txt` yalnız satır sayısı için `wc -l` ile dokunuldu; içeriği okunmadı (gerek olmadı).
- `ON-KAYIT-TASLAK.md`'de yalnız §4.19 (satır 830–840) okundu. Başlık satırları, bölümün yerini bulmak için `grep "^#"` ile tarandı.
- Hiçbir araç (clingo, Tamarin, z3, ProVerif) koşturulmadı.
- Ağ, git ve Docker kullanılmadı. Hiçbir dış hizmete veri gönderilmedi.

| # | Yol | Nasıl | Neden |
|---|---|---|---|
| 20 | Kendi çıktılarım | `awk` (sözlük uyumu, sayımlar), `sha256sum` | Son denetim ve `SHA256SUMS` üretimi |
