# Kör türetme girdisi — nasıl hazırlandı (yürütücü, 24.09.2026)

Kaynak: `literatur/analiz/KAT-SPEC.md` (SHA-256 `f8ba9a51…8b80`). Çıktı: `KAT-KOR-GIRDI.md` (`1b0dac38…26f2`).

**Adımlar:**
1. `kat_redakte.py`: (d) bölümlerindeki tablolardan "Beklenen…", "Dayanak", "Not", "accept strict/transitional" ve attack/violation sütunları atıldı. "Tamarin bayrakları → sonuç" biçimli sütunlarda yalnız okun solu tutuldu.
2. Yürütücünün satır içi Python'u (betik bu dosyada anlatılıyor):
   - (a)–(c) bölümlerindeki bütün kod blokları çıkarıldı (taslak ASP/Tamarin kodu);
   - pilot sonuç notları çıkarıldı;
   - (d) ve (e) bölümleriyle §5, §6 ve §7 hiç alınmadı;
   - KAT-2c tablosunun hücreleri "?" yapıldı;
   - KAT-3b'deki "Pilot Tamarin" sütunu atıldı;
   - kalın vurgu işaretleri silindi;
   - Kim vd. Tablo IV ve Tablo V sonuç özetleri çıkarıldı (birincil metne yönlendirildi);
   - değer sözlüğü elle yazıldı. Değerlerin kümesi verildi, hücrelerle eşlemesi verilmedi.
3. Kalan sızıntı taraması: Kalan tek eşleşmeler genel ölçüt cümlesi ve yayımlanmış iddiaların birebir alıntıları.

**Amaç:** ÖK §4.19 ve KAT-SPEC §5.3'teki kör N-sürüm beklenen-değer türetmesi.
