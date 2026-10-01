# Adım 7 görev 0 (Tamarin çalışması) → yürütücüye notlar

- **Tarih:** 25.09.2026
- **Klasör:** `model\mechanisms\` (sahibi: Tamarin çalışması). `models\tamarin\` değiştirilmedi.
- **Koşum kuralı (bağlayıcı):**
  - `--prove` yok. Yalnız iyi biçimlilik denetimi yapıldı (`tamarin-prover dosya.spthy -D=…`, uyarı 0).
  - Beklenti dosyası ve modellerin SHA-256'sı çapaya alınmadan ve teknik kapı kararından önce koşum yok.
- **Kapsam ekonomisi (25.09 kararı) uygulandı.** Ayrıntı: `ON-KAYIT-GEREKCE.md` §0.1.

## Durum

- [x] İskelet dosyaları: `on_kayit_varyantlar.tsv`, `ON-KAYIT-GEREKCE.md`, bu dosya.
- [x] Beklentiler. 63 satır:
  - 33 koşulacak;
  - 18 `5A-kapsandi` (R7 atfı);
  - 11 `indirgendi`;
  - 1 `betimsel` (KB 3c, model yok).
- [x] Model taslakları (`modeller\`):
  - `ortak_g5.spthy` (G5'in üç biçimi, `#include`);
  - `M_istek.spthy`: M-b0, M-a, M-b / A.3.2.2; M-c indirgendi;
  - `M_metaveri.spthy`: M-e, M-e′, M-d; tek parametreli aile;
  - `Mf_yol.spthy`: M-f çekirdeği yol dahil, 3b, taşıyıcılar;
  - `M_h.spthy`: reddy ve vicente tipleri, 3a/3b.
  - `M_g.spthy` ve `KB_coklu.spthy` yazılmadı (5A'da kapsandı / betimsel).
- [x] İyi biçimlilik: 33/33 koşum satırı `wf_ok=1`, uyarı 0. Kayıt: `iyi_bicimlilik_on_kayit.txt`.
- [x] SHA-256 listesi: `SHA256-ON-KAYIT.txt` (aşağıda da var). → DUR.

## Koşulacak 33 satır

| Model | Satırlar |
|---|---|
| `M_istek` (3) | `MB0_taban`, `MA_taban`, `MB_taban` (= M-b / A.3.2.2) |
| `M_metaveri` (4) | `ME_signed_fresh` (M-e), `MEP_signed_fresh` (M-e′, koşullu kanıt), `MEP_tls_classical` (M-e′, çekilen kanal), `MD_reg_pq` (M-d) |
| `Mf_yol` (17) | `MF_cekirdek` (kabul ölçütü 2); 3b'nin 9 hücresi; taşıyıcılar: `MF_tas_tl_onbellek`, `MF_tas_wrprc_faz0`, `MF_tas_wrprc_faz1`, `MF_tas_federasyon_pq`, `MF_tas_federasyon_klasik_ara`, `MF_tas_federasyon_bayat`, `MF_tas_crit_baslik` |
| `M_h` (9) | reddy × {klasik zincir, 3 saldırı, ad bağlama + farklı ad}; vicente × {klasik zincir, 3 saldırı} |

- Kapsam kararından önce yazılmış 23 koşum satırının bayrakları ve beklentileri değişmedi (betikle karşılaştırıldı). Yeni koşum satırları 10'dur: `MF_tas_tl_onbellek` ve M-h'nin 9 satırı.
- Beklentisi yazılmayan lemma yoktur (betikle denetlendi). Tek istisna `M_metaveri` satırlarındaki `executable_learn`; bu lemma başlıktaki "executable* varsayılan V" kuralına girer.

## Koşum çalışması için uyarılar

1. **Türetme denetimi zaman aşımı.** `Mf_yol` ve `M_h` büyüklüğündeki modellerde Tamarin'in öntanımlı türetme denetimi zaman aşımına uğruyor. Bu durumda "Derivation checks timed out" iyi biçimlilik uyarısı çıkıyor; 5A kuralına göre bu, koşumu geçersiz kılar.
   - Bu yüzden `betik\iyi_bicimlilik.sh`'ye `--derivcheck-timeout=60` eklendi (ortam değişkeni `DCT`). Denetim kapatılmadı, yalnız süresi uzatıldı; 60 s ile her model yaklaşık 7 s'de temiz geçti.
   - **Asıl koşumlarda da aynı bayrak kullanılmalı.** Yoksa `--prove` çıktısında uyarı görünür.
2. **Satır süzgeci.** Koşucu yalnız `rol` ∈ {mekanizma, kosul, tasiyici, ablasyon, 3b, 3a} satırlarını koşmalı. `5A-kapsandi` satırlarının `dosya` / `bayraklar` sütunları R7 varyantına atıftır (`models\tamarin\`); bunlar koşulmaz.
3. **Kaynak kestirimi.** `Mf_yol`'un üç saldırılı satırları (`MF_cekirdek` ve taşıyıcılar) derinlik-2 yol ve üç kırılabilir çıpa içerir; en ağır satırlar bunlardır. Merdiven uygulanır: `--memory=12g`, lemma başına süre sınırı.
4. **Tutarlılık denetimi.** `ATK_*` yalnız kurulum kuralı ekler. `MF_cekirdek`'in V hükümleri, üç `MF_3b_yol_*` hücresinin V hükümlerini gerektirir; çelişki çıkarsa model hatasıdır.

## Model varsayımları (raporda açık yazılmalı)

- **`M_istek` `RequestSamePhase`:** dürüst istek oluşturulduğu evrede kabul edilir. İstekler kısa ömürlü olduğu için yapay göç yarışı dışlanır. Sahte isteklere uygulanmaz.
- **`M_metaveri`:** "aynı evre" kısıtı yok (kimlik bilgileri uzun ömürlü).
- **`Mf_yol`:**
  - `Freshness`: yanıt kullanım anına dek güncel; gecikme R6'nın konusu.
  - `SCOPE_KEY`: bağlı PQ anahtar, beklentiyle aynı doğrulanmış görünümden gelir.
  - `FED`: çözümleme yanıtı sorguya bağlı ve güncel.
- **`M_h`:**
  - R1: reddy'nin "SHOULD terminate" kuralı uygulanır.
  - V1: vicente'de taahhüt hatası reddedilir; taslak sonucu tanımlamaz.
  - V2: doğrulayıcı özne başına ilk taahhüdü tutar.
  - Pencere ve süre sonu modellenmedi. Pencere sonrası koruma olmadığı taslak metninden çıkar.
- **M-c:** "varsa önce PQ" tercihi sembolik modelde ifade edilemez (olumsuz öncül yok). İndirgeme bu yüzden M-b'yedir.
- **A.3.2.2:** semantik tanımsız (T273). "Cüzdan güvendiği herhangi bir çerçeveyle doğrular" okuması bir varsayımdır.

## Bulgu adayları ve karar bekleyen noktalar

1. **M-d için plan metniyle çelişen ön kayıt.** İş planı 7.4: "PQ kanaldan → kanıt". Ön kayıt: `MD_reg_pq` G5_migrated = F. Sebep: güncelleme iletileri PQ ile imzalı ama yeniden oynatılabilir; göç öncesi `'none'` kaydı göçten sonra oynatılır (S1). Bilerek böyle kaydedildi.
2. **reddy: (b) niteleyicisi adayı.** Taslağın kendi kuralları altında (§3.1 yol doğrulaması değişmez; §3.3 önbellek SAN + algoritma), herhangi bir klasik CA'dan sahte PQC sertifikası fark edilmez.
   - **Uyarı:** sheffer-02 §3.2 (ortak yazar Reddy) olguyu öngörüyor; "türetilemeyen" koşulu tartışmalı. GEREKCE §6.3.
3. **Ad bağlama sınırı (R7h/R7hx'in inceltilmesi).** Ara CA'lar modellenince saldırgan meşru CA'nın adını taşıyan bir ara CA çıkarır. Ad bağlama farklı adlı alternatif CA'ya karşı bile düşer; ön kayıt F (`MH_reddy_adbag_farkli_ad`).
4. **Ön kayda alınmadı, karar bekliyor: sheffer-02'nin zincir politikası belirsizliği.** §3.1 "not traditional-only" tanımı ile §3.2 "every CertificateEntry" kuralı, anahtar okumasına açık.
   - Anahtar okumasında önbellek dolduktan sonra da 3b saldırıları geçer.
   - Ayrıca `algorithm_validity_period = 0` ile önbellek sildirilebilir (§3.6).
   - `M_h` altyapısıyla 2–4 satırlık ek olarak ön kayda alınabilir. GEREKCE §5.
5. **Ön kayda alınmadı, karar bekliyor: yola duyarlı M-f tanımları** (M-f-TANIM için). `MONOTONE` = "'none' beklentisi hiç kullanılmaz"; sunset beklenti düzeyinde olmalı.
   - Anahtar düzeyi sunset yalnız klasik yaprağı kapatır. Sunset'ten sonra bayat `'none'` klasik kenarlı PQ yolu kabul ettirir.
   - Bayraklar `Mf_yol`'da duruyor; istenirse ayrı satır olarak kaydedilir. GEREKCE §3.4.
6. **KB 3c:** model yazılmadı; beklenen cevap RFC 9901 §8.1/§8.3 metninden (GEREKCE §7). Araç kanıtı istenirse küçük bir model eklenebilir.

## Çalışma ortamı

- **Docker:** yalnız `pq-a07-wf<pid>` adlı, `--rm`, 4 GB sınırlı iyi biçimlilik konteynerleri koştu. Yeni imaj yok, `prune` yok, başka konteynere dokunulmadı. Docker açık bırakıldı.
- **Dışa dönük eylem yok;** e-posta ya da kişisel veri hiçbir yere gönderilmedi. Git commit atılmadı.

## SHA-256 (`SHA256-ON-KAYIT.txt`)

```
16fae232503d525c804b1ab6742df7eb1972c804a39dfa3851840dda8d4cfccd  on_kayit_varyantlar.tsv
42e79bd0ca472808d288c4f089ec608d45c745b3c9c68bb92162af9c3e30b750  modeller/ortak_g5.spthy
74b0e4407e390b3c548c11d73f603ab647d279ff6c9a7611b8fb8377baf41cf5  modeller/M_istek.spthy
f56fb4ce22c9a269384e55d35432d7cf853ae7a3094f3c87b7cd3d54f8ad72f7  modeller/M_metaveri.spthy
00c1b35d7dda7db5740b46c189f87cd6384e15059daf15659fb31cf06f4dcfa4  modeller/Mf_yol.spthy
1fb460cf9820f0f285a8238f971e688db33477ee776f9c1cf8bf164e56f543d5  modeller/M_h.spthy
64f72f8ce0b005078968c8ed92de09b818daabc08c1f646165db63fa67d06dab  ON-KAYIT-GEREKCE.md
fdb8bf9b41b69f02607a98be92c47fa60665382554208d6b8e1492da0b7a5cf7  betik/iyi_bicimlilik.sh
423938ce2447c63cd027eb7fc564707d6124e2577ff5d50d6390b9101a283c05  iyi_bicimlilik_on_kayit.txt
516f01bea8329ca0af778590b42156c7566bb258002f3f68a1f55ac5860e170a  SHA256-ON-KAYIT.txt
```

## EK — Değişiklik 8 (26.09.2026)

- İki aday grup ön kayda alındı; beklenti dosyasının sonuna 10 satır eklendi (önceki 63 satır bayt bayt aynı).
  - [8a] `modeller\Mg_yol.spthy`: sheffer-02 zincir politikası, anahtar / imza okuması × 3 saldırı (6 satır).
  - [8b] `modeller\Mf_ek.spthy`: çevrimdışı ekin yola duyarlı tanımları, tekdüzelik {dar, geniş} × sunset {anahtar, beklenti} (4 satır).
- Önceki model dosyaları değişmedi (özetler aynı); yeni satırlar için iki yeni dosya yazıldı.
- İyi biçimlilik 10/10 temiz. Gerekçe: `ON-KAYIT-GEREKCE.md` §9. Koşulacak satır: 43.
- `on_kayit_varyantlar.tsv` SHA-256: `ebb87d64216d81e927d9d117f792b99f59e83b1d72ea964d92bb440412f3a5e2` (`EK-HAZIR.txt`). Güncel liste: `SHA256-ON-KAYIT.txt`.
