# Envanter çalışmasından yürütücüye notlar (Adım 9a)

Ayrıntılar `OZET.md` ve `KRITERLER-TASLAK.md`'de. Burada yalnız ortak dosyaları etkileyebilecek noktalar var.

1. **Pilot dayanağı taşındı (R1).**
   - `openwallet-foundation/sd-jwt-js` Eylül 2026'da arşivlendi ve `openwallet-foundation-labs/identity-common-ts`'e taşındı.
   - `oid4vc-ts` de aynı depoya taşındı. npm'deki `@sd-jwt/core` paketi artık bu depoyu gösteriyor.
   - Sürüm 3 §10'daki `sd-jwt-js` #388/#389 ve commit `c7cf23dbc1b8` eski depoya atıf yapıyor. Ön kayıtta yeni depo ve commit sabitlenmeli.
2. **Authlib dışlandı (K3).** `authlib.jose` kullanımdan kaldırıldı; pilot çıktısındaki uyarı bunu gösteriyor. Halefi `joserfc` yedekte.
3. **Composite -04'ün yerel desteği n içinde hiçbir hedefte yok.**
   - Tek yerel örnek `lestrrat-go/jwx` (yedek; `jwx-go/compsig` eklentisi deneysel).
   - Ana tedavi kolu için T2 (eklenti/geri çağrı) ve T3 (bilinmeyen alg) sınıfları ön kayda girmeli (OZET §3.2).
4. **L4 tanımı.** 31 hedefin 17'si yalnız kompakt serileştirme destekliyor. L4'ün tek imzalı biçimi ön kayda yazılmazsa H6'nın paydası küçülür (OZET P2).
5. **Karar isteyen seçenek (OZET P7).** irmago (Yivi), ML-DSA doğrulayan tek REF adayı. Emülatörün PQ kolu için öne alınması, "önce G kaynakları" kuralını değiştirir.
6. **Gizlilik olayı (R12; kapatıldı).**
   - Silinmiş bir Bitbucket deposunun anonim klonu Git Credential Manager'ı tetikledi. Süreç hiçbir girdi almadan sonlandırıldı; kimlik bilgisi gönderilmedi.
   - Sonraki bütün git çağrıları `credential.helper=` ve `GCM_INTERACTIVE=never` ile çalıştı.
   - Diğer çalışmalar da anonim git kullanıyorsa aynı ayarı öneririm.
