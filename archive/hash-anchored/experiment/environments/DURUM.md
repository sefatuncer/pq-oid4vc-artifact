# DURUM (ara kayıt; IS-PLANI §3.1 madde 7)

- **Son güncelleme:** 25.09.2026 — görev 4a TAMAM.
- **Yapılan:**
  - 12 ortam imajı (`IMAJLAR.md`).
  - 34 hedef: 33 başarılı, 1 başarısız (JOSE-104).
  - JOSE-104 için iki yedek adayı (JOSE-031, JOSE-017) derlendi; seçim yürütücüde (`DEGISIKLIKLER.md`).
  - Bilgi koşuları: `_bilgi-*` (6).
  - `KARAR-NOTLARI.md`, `SHA256SUMS`.
- **Sıradaki (yürütücü):**
  - K1 yedek seçimi.
  - K2 sürüm sabitleme (son_surum ↔ son_commit_sha).
  - K3–K6 (`KARAR-NOTLARI.md` §1).
  - Taban imaj ve build-cache temizliği.
- **Açık dosya:** yok.
- **Son komut:** `sha256sum` (SHA256SUMS üretimi).
- **Ders:**
  - Windows'ta Python `write_text` CRLF yazar; betik yamalarında `write_bytes` kullan.
  - Bash aracında `\` tek `\`'e iner.
  - Alpine tabanlı imajlarda `bash` yok.
