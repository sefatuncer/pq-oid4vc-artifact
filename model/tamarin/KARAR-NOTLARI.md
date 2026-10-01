# Adım 4 (Tamarin) → yürütücüye notlar

- **Tarih:** 24.09.2026
- **Ayrıntı:** `RAPOR.md`
- **Kaynak:** Bütün sayılar `sonuc\` dosyalarından alındı.

## A. Planı etkileyen bulgular

1. **Adım 3 (ASP) için sınıf semantiği kararı gerekiyor.** Bu bulgu araç kanıtına dayanıyor.
   - **Kanıt:**
     - `R1 X_alt_ca` varyantında ihraççının kendi zinciri tamamen PQ. Aynı kök altında klasik kalmış ikinci bir CA varken G1 **falsified**.
     - `X_alt_ca_forges_honest_issuer` **verified**: kurulmuş dürüst bir ihraççının adı sahteleniyor.
     - İhraççıyı kendi CA'sına bağlama (`NAME_BIND`) eklenince G1 verified.
   - **Datalog tarafı:**
     - Pilotun örtük okuması (`pq(L)` = gerçek ebeveyn PQ) bu varyantta "güvenli" diyor. Bu, 44 satırdaki tek uyumsuzluk (`metrikler.txt`).
     - Sınıf semantiği (`pq(L)` = doğrulayıcının `L` için kabul ettiği **bütün** imzacılar PQ) ise 44/44 uyumlu.
   - **Öneri:** ASP'de şu üç yoldan biri seçilmeli:
     - `pq(L)` artefakt sınıfının bütün üyeleri üzerinden tanımlanır,
     - `accepted_signer(L,K)` kenarları eklenir,
     - ad bağlama yüklemi eklenir.

     Aksi hâlde asgari kümeler saldırıları eksik sayar. M2 maliyetinde de bir sınıf ancak bütün üyeleri PQ ise (ya da ad kısıtlıysa) göç etmiş sayılmalı. Örnekler: TL'deki bütün CA'lar; LOTL'nin 43 işaretçisi ve 107 TL imzacı sertifikası (§7.10).
   - **Önemi:** Bu, "önce kök" sırasının kısmi sınıf göçünde yetersiz kaldığı bir hücreye aday (H4). Bariz olmayan sonuç adayı olarak değerlendirilebilir.
   - **KAT-1'e yansıması:** DNSSEC örneğine RFC 6840 §6.2'nin kenar semantiği eklenmeli: "any DNSKEY … may be used to authenticate any RRset". Birincil kaynak `01-korpus\metin\RFC6840.txt` dosyasında açılıp doğrulandı.

2. **G5 iki biçimde ele alınıyor.**
   - Adım 4 **zamansız** G5'i kanıtladı: göç etmiş varlık hiçbir zaman yalnız klasik kanıtla kabul edilmez.
   - Karar belgesindeki tanım (§7.4) "ilan ettiği eski-sürüm penceresi dışında" diyor. Bu zamanlı biçim R7'nin (sunset) işi.
   - **Öneri:** Ön kayıt metni hangi biçimin hangi adımda sınandığını açıkça yazmalı.

3. **H1'in "taze" koşulu henüz sınanmadı.** R3'te nesne imzası ile nonce'a bağlı taşıma aynı hükmü verdi, çünkü beklenti durağan. Tazelik farkı ancak beklenti zamanla değişirse görülebilir. Bu yüzden R7 sürümlü beklenti ve yeniden oynatma içermeli; yoksa H1'in tazelik kısmı Tamarin kanıtından yoksun kalır.

## B. Hipotezlere erken sinyaller (bilgi)

4. **H3, M-a sınıfı: S1 yeter.**
   - Beklenti yoksa ya da kimliği doğrulanmamışsa `S1_downgrade_trace` verified: izde Q-day de kırılma da yok.
   - Kimliği doğrulanmış beklentiyle ya da birlikte yaşama olmadan bu iz yok (4/4 falsified).
5. **H5 ön sinyali.**
   - R4 `SINGLE_USE` varyantında cüzdanda tek kullanım ve doğrulayıcıda küresel tek kullanım birlikte uygulandı. Klasik cihaz anahtarıyla G2 yine falsified.
   - Doğrulayıcının küresel durumu bilerek en güçlü (idealleştirilmiş) biçimde kuruldu.
   - Biçimsel H5 sınaması R6 pencereleriyle yapılacak (R4 × R6).

## C. Araç ve süreç notları

6. **Tamarin 1.12 önişlemcisi.**
   - Atlanan dalda iç içe `#ifdef` ayrıştırma hatası veriyor.
   - `#ifdef not (A | B)` ayrıştırılmıyor. Düz `&` ve `not` çalışıyor.
   - Katman 3 örnekleme üreticisi düz koşul üretmeli ya da örnek başına ayrı dosya yazmalı.
7. **Pilot modelinde iyi biçimlilik uyarısı.**
   - `arac\test\p1\weakest_link.spthy`, `Qday` adını hem eylem hem durum olgusu olarak kullanıyor. Tamarin 1.12 bu yüzden "WARNING: 1 wellformedness check failed! The analysis results might be wrong!" veriyor. Pilot çıktıları (`arac\test\p1\out_V*.txt`) bu uyarıyı taşıyor.
   - R1–R5'te adlar ayrıldı; 34/34 varyantta iyi biçimlilik denetimi başarılı.
   - Makalede pilot rakamları yerine R1–R5 sonuçları atıf almalı.
8. **clingo kullanımı.**
   - Datalog karşılaştırması `pq-a02-solver:1.0` imajında yapıldı: toplu koşumun sonunda yaklaşık 10 s, 2 GB sınırla.
   - Tamarin sonuçları bu adıma bağlı değil. İmaj kullanımı kurala aykırı görülürse karşılaştırma ayrıca yeniden koşturulabilir.
9. **Süre ve Katman 3 kestirimi.** Toplu koşum 230 konteynerle yaklaşık 10 dakika sürdü. Lemma başına medyan 1,22 s. Katman 3 örneklemesi (50–200 örnek) dakikalar mertebesinde biter (tahmin).
10. **Yöntem notu.**
    - R1 ve R4'ün korumalı varyantlarında klasik anahtar yok; bu yüzden güvenlik kolay sonuçtur.
    - Makalede korumanın gerçekten sınandığı örnekler öne çıkarılmalı: R2, R3, R5 ve R1 `X_alt_ca_namebind` korumalı varyantları. Bunlarda CRQC etkin ve saldırıyı engelleyen, korumanın kendisi.
11. **Kesinti.**
    - Oturum, koşumlar bittikten sonra kullanım limiti yüzünden kesildi.
    - Koşumlar tekrarlanmadı. Rapor `sonuc\` dosyalarından yazıldı.
    - Kesintiden önce hazırlanan ama hiç koşturulmayan `betik\iz_dok.py` silindi. Metin izleri zaten `sonuc\ham\*.txt` dosyalarında var.

---

# Adım 5A (24.09.2026) → yürütücüye notlar

**Ayrıntı:** `RAPOR.md` §12. Sayıların kaynağı `sonuc\metrikler.txt` (Adım 5A bölümü) ve `sonuc\proverif\metrikler.txt`.

## D. Planı etkileyen bulgular

12. **R7h'de beklenmeyen sonuç: ad bağlama yetmiyor, anahtar bağlama gerekiyor.** Bu bulgu araç kanıtına dayanıyor.
    - **Ön kayıtlı beklenti:** Korumalı `P_ca_pq_alt_namebind` (CA_PQ, ALT_CA, NAME_BIND) için G5 ve G1 = V.
    - **Gözlenen:** İkisi de **F**. Ön kayıtlı toplam 347/349.
    - **İz:** Kök, alternatif klasik CA'yı meşru CA ile **aynı adla** sertifikalıyor. Ad bağlama bu yüzden taahhütsüz sertifikayı kabul ediyor.
    - **Keşif (R7hx):** Ayrı ön kayıt özetiyle, 35/35 beklendiği gibi:
      - CA adları tekilse ad bağlama koruyor,
      - aynı adlı klasik CA (CA anahtar değişimi) varsa atlatılıyor,
      - **anahtar bağlama** her iki durumda da koruyor.
    - **Adım 4'e etkisi:** R1'deki `X_alt_ca_namebind` = V sonucu CA adı tekilliği varsayımına bağlıydı (`Unique(<'ca', ad>)`).
    - **ASP'ye (Adım 3) iletilmeli:** `ad_baglama` parametresi **anahtar bağlama** olarak tanımlanmalı. Ya da "CA adı tekil" ayrı bir varsayım olarak yazılmalı. Aynı adın klasik ve PQ sertifikalarının birlikte geçerli olduğu anahtar değişimi dönemi ayrı bir hücre olmalı.
    - **Önemi:** L-D4'teki "M-h'nin alternatif yolla atlatılması" adayına somut bir iz. Ad bağlama altında bile atlatılması tahmin olarak bariz olmayan bir sonuç adayı. Yenilik değerlendirmesini yürütücü yapmalı.
13. **H3'ün ön kayıt metni güncellenmeli.** "M-f'nin her bileşeni gerekli" öngörüsü **bağlama bağlı** çıktı.
    - **Çevrimiçi (FRESH) ya da sabitlenmiş kurgu:** MONOTONE ve SUNSET_CHECK gereksiz (`A_online_no_monotone`, `A_online_no_sunset`, `A_pinned_min`: V/V/V). Bu, önceden kayıtlı bir öngörüydü.
    - **Çevrimdışı kurgu:** İkisi de gerekli (`M_off_monotone`, `M_off_sunset`).
    - **Her kurguda gerekli çekirdek:** üçüncü taraf + PQ kanal + varlık başına + güncel değer.
    - Ön kayıttaki yanlışlanma koşulunun "mekanizma sadeleştirilir" kolu devreye giriyor. Sadeleştirilmiş M-f tanımı `RAPOR.md` §12.4'te.
14. **G5'in iki biçimi resmîleşti.**
    - Zamansız biçim: R2, R3, R7h.
    - Zamanlı biçim: R7 `G5_timed`, sunset sonrası.
    - Ek olarak ilk teması kapsayan `G5_migrated`.
    - Ön kayıtta üçü ayrı hedef olarak yazılmalı.

## E. Hipotezlere ön sonuçlar

15. **H2 (L-D3 doğrulandı).**
    - Uzun ömürlü durum imza anahtarı her rejimde sahtelenebiliyor.
    - Rotasyonlu anahtar yalnız SLOW'da, belirteç başına anahtar MEDIUM ve SLOW'da korunuyor.
    - İki ek koşul var: PQ kimlik bağlama ve anahtarın yeniden kullanılmaması.
    - ASP için pencere sınıfları gerekli: uzun ömürlü / dönem / belirteç. Ayrıca `exposure(K)` ve `last_accept(K)`.
16. **H5 (biçimsel):** Klasik cihaz anahtarında tek kullanım (cüzdan + küresel doğrulayıcı) sahteciliği önlemiyor (`M_single_fast` = F). Yalnız şu ikisi birlikte koruyor: geçerlilik penceresinin τ'dan kısa olması ve kimlik bilgisi başına cihaz anahtarı.
17. **H3 / L-D1 (M-f ↔ M-g):**
    - M-g üç varyantta da ilk temasta downgrade izi veriyor; Q-day gerekmiyor.
    - M-f (çevrimiçi ya da sabitli) ilk teması koruyor.
    - L-D2'deki ayırt edici özellik Tamarin'de gösterildi.

## F. Araç ve süreç notları

18. **İyi biçimlilik kuralı uygulandı.**
    - `calistir.sh` her lemma koşumunu denetliyor; uyarılı koşum `gecersiz_wf` olarak kaydediliyor.
    - Adım 5A'da 390/390, toplamda 620/620 çıktı uyarısız; geçersiz koşum 0.
19. **ProVerif ikinci görüşü:**
    - R1–R5'in 15 varyantı, 20 güvenlik sorgusu. Kesin sonuç 20/20, Tamarin uyumu 20/20; "cannot be proved" 0.
    - Pilottaki 2/4 "bilinmiyor" burada görülmedi. Kodlama farkı olası neden [Y].
    - R6/R7 ProVerif'e aktarılmadı: fazlar τ'yu ifade etmekte zayıf.
20. **Kesinti sonrası TSV denetimi.**
    - `varyantlar.tsv` ön kayıt özetiyle aynı; ilk 38 satırı Adım 4 dosyasıyla bayt bayt aynı; CR ve `|` 0.
    - Biçim düzeltmesi gerekmedi. İlk denetimdeki "CRLF: 81" çıktısı bir kabuk tırnak hatasıydı.
21. **`degerlendir.py` genelleştirildi.** Adım 4 sonuçları birebir yeniden üretildi; tek fark "bilgi-H3" → "bilgi" etiketi.
22. **Kaynak kullanımı:**
    - Adım 5A'nın Tamarin koşumları 19:11:34–19:31:45 arasında yaklaşık 18 dk sürdü.
    - Lemma başına en uzun 3,58 s, medyan 1,03 s; bellek en çok 115,8 MiB.
    - Merdiven hiç gerekmedi.
    - Docker açık bırakıldı; yalnız `pq-a04-*` adlı, `--rm` ile açılan konteynerler kullanıldı.
