# ASP çalışmasından yürütücüye notlar (Adım 3)

> Plan ya da ön kayıt değişikliği gerektirebilecek her şey burada. Her madde: ne, neden, önerilen karar, etkilenen belge.
> Durum: TAMAMLANDI (25.09.2026). Madde numaraları kalıcıdır. Sayıların kaynağı: `sorgular/sonuc/rapor_sayilari.json` ve RAPOR.md'de adı geçen sonuç dosyaları.

## N1. §2C D1′ uyarlaması: 17 karar düğümü (uygulandı)
- **Ne:** Karar değişkenleri düğüm düzeyinde (`pqd/1`): a01 a02 a03 a04 a05 a06 a07 a08 a09a a09b a10 a11 a12 a13 ecrl ejvi eas. Modelde bazı sınıflar birden çok örnekle temsil ediliyor (A02 = ulusal TL + 4 EUDI LoTE; A03 = sağlayıcı CA + dış kaynak durum CA'sı; A11 = WRPAC + WRPRC; A13 = WebPKI + OJEU-sabit LOTL indirme kanalı); aynı düğümdeki örnekler birlikte göç eder.
- **Yorum kararları (onay gerekir):**
  - A09a düğümü = WIA'nın bağladığı cüzdan örneği anahtarı (§2C W_güven WIA = 1 gün); A09b düğümü = cüzdan sağlayıcı imza anahtarı (KA ve WIA imzaları; W_güven KA = 1 yıl). Gerekçe: H2′'ye göre WIA'nın <24 sa geçerliliği bir belirteç penceresidir; 1 günlük W_güven ancak WIA başına yenilenen örnek anahtarına ait olabilir.
  - A13 = "çekilen artefaktların TLS sunucu kimlik doğrulaması PQ ve klasik zincir reddediliyor" kararı. WebPKI klasikken (birincil) PQ seçilemez (`pq_yasak`); WebPKI PQ iken seçilebilir bir göç kararıdır.
  - **DÜZELTME (25.09):** Bu maddenin önceki sürümü "`pq_birlikte` (PQ sertifika var, klasik de kabul) any-valid-path ile klasikle eşdeğerdir (OAT'ta doğrulandı)" diyordu. **Bu yanlıştı.** OAT `webpki_pq_birlikte` 63 hücrede (G1–G3, P4) küme ailesini değiştiriyor. Düğüm kümeleri aynı kalıyor ama a01'in yerine {a13 + `tasi(a00_ojeu, a13_lotl_kanal)`} alternatifi ekleniyor. Nedeni: OJEU-sabit LOTL indirme kanalının sertifikası OJEU'da yayımlanıyor (T002), modelde OJEU bu kanal için "PQ gerekli" beklentisi taşıyabilir (M-f kancası) ve bu, `pq_birlikte`'deki klasik kabulü kapatır. Genel WebPKI (`a13_webpki`) için varlık başına kimliği doğrulanmış beklenti taşıyıcısı yok; orada `pq_birlikte` gerçekten klasikle eşdeğer. **Karar gerekir:** OJEU'nun LOTL kanalı için PQ beklentisi taşıyabileceği varsayımı M-f'nin kapsamına alınacak mı? Alınmazsa `tasiyabilir(a00_ojeu, a13_lotl_kanal, m_f)` olgusu kaldırılır; birincil sonuçlar değişmez (birincilde WebPKI klasik, A13 seçilemez).
  - İmzasız kenar-artefaktlar (A06, E_JVI, E_AS) için "PQ" = nesne düzeyinde PQ bağlama (A06: vct#integrity özeti; E_JVI: JWKS'nin CA zincirine PQ imzayla bağlanması; E_AS: imzalı AS meta verisi). Bağlıysa sahteliği bağlandığı artefaktınkine indirgenir; birlikte yaşamada bağsız biçimin kabulü klasik alternatiftir.
  - E_CRL kendi imza anahtarıyla ayrı düğüm (CA sınıfı pencere, 5 y).
- **Etkilenen:** ön kayıt §2C 2.1 metninde bu yorumlar yok; dondurulan sürüme "işlemsel eşleme" olarak eklenmesi önerilir.

## N2. §2D madde 11: ca_baglama ve ayni_ad_klasik_ca (uygulandı)
- `ca_baglama ∈ {yok, ad, anahtar}` (birincil yok), `ayni_ad_klasik_ca ∈ {yok, var}` (birincil yok).
- **Eşleme (Tamarin R7hx ile aynı yapı):** "aynı adlı klasik CA", aynı çıpa altındaki alternatif klasik CA'nın (ALT_CA) ad ilişkisidir. ASP'de alternatif CA'nın varlığı `diger_ca`, ad ilişkisi `ayni_ad_klasik_ca`. Kabul: `yok` → alternatif her zaman; `ad` → yalnız aynı adlıysa; `anahtar` → hiçbir zaman.
- **Sonuç:** 2×2'nin dört kombinasyonu ve iki sağlık yapılandırması önceden yazılan beklentilerle **6/6** tuttu. ad/var: 675/675 UNSAT (birincilin 279 asgari kümesinin hepsi falsified); ad/yok, anahtar/yok, anahtar/var: 675/675 birincil ile aynı. §2D m.11'deki "ca_baglama = yok iken bayrak etkisizdir" iki yapılandırmada (diger_ca var/yok) 675/675 + 675/675 sağlandı. Yön, Tamarin R7hx ile aynı (`X_namebind_unique` V, `X_namebind_samename` F, `X_keybind_distinct` V, `X_keybind_samename` V; `M_no_namebind` F).
- **Beklentiler koşumdan önce:** `sorgular/beklenti_2x2.json`, SHA-256 `c0899c5f3f0d587b62d94ecff1fdd2e4dd6f2c1bafa2c656d067fc93fa895546` (2026-09-25T12:33:27Z). **Şeffaflık:** beklenti dosyasından önce altı kombinasyon tek bir hücrede (g1, Φ3, P0, taze, hızlı) uygulama duman testi olarak koşuldu; tam ızgaranın hiçbir sonucu görülmeden beklentiler yazıldı.
- **G5 notu:** Tamarin R7hx'te G5 ile G1 aynı hükmü veriyor; ASP'de alternatif CA yolu bir tanıtıcı (K2) yoludur ve G1 ihlali olarak görünür. Karşılaştırma G1 üzerinden.

## N3. Pencere sınıfları ve Tamarin R6 (uygulandı; kural farkı yok, eşleme notu)
- `pencere_sinifi/2` ∈ {uzun_omurlu, donem, belirtec}; `maruziyet/2` (exposure, en kötü durumda 0) ve `son_kabul/2` (last_accept); W_güven = son_kabul − maruziyet.
- V2/V3 anahtarları CA'nın düzenlediği kısa ömürlü sertifikayla bağlanır (kimlik = CA zinciri = R6 `ID_PQ`); `anahtar_yeniden_kullanim = var` = R6 `KEY_REUSE` (pencere uzun ömürlüye döner). Önceki taslaktaki ayrı `a07_sert`/`a08_sert` düğümleri kaldırıldı: 17 düğümlü bağlamada kimlik ile geçici anahtar aynı karara düşüyordu ve V3 anlamsızlaşıyordu.
- R6'nın FAST/MEDIUM/SLOW rejimleri sembolik; sayısal okuma: FAST τ ≤ belirteç penceresi; MEDIUM belirteç < τ ≤ dönem penceresi; SLOW τ > dönem penceresi. §2C birincil değerlerinde (TTL 1 g; V2 penceresi 1 g + 1 g) **nominal "orta" τ = 3 gün, V2 için R6'nın SLOW sınıfına düşer.** Bu bir kural farkı değil, sayısal eşlemedir: rotasyonlu anahtar ASP'de orta ve yavaş nominal rejimde korunur; R6 dilinde bu iki hücre SLOW'dur. MEDIUM sınıfı yalnız A5 ızgarasında görünür (TTL 1 sa; τ 14 sa ve 1 g; 8 satırın 8'i uyumlu: V2 korunmaz = `E_rot_medium` F, V3 korunur = `P_tok_medium` V).
- **Sonuç:** R6 kapsamındaki 588/588 hücre uyumlu; KEY_REUSE hücrelerinde A08 6/6 gerekli (`M_rot_reuse` ile aynı yön). **ASP kuralları R6 sonuçlarına göre değiştirilmedi.**
- **Şeffaflık (sonuç görüldükten sonra, yalnız karşılaştırma betiğinde):** İlk karşılaştırmada iki sınıflama hatası çıktı ve `analiz.py`'de düzeltildi. (a) V1 anahtarının penceresi sınıflamada yanlış okunuyordu. (b) τ, TLS penceresini aşınca çekilen durum belirteci klasik taşımayla da korunuyor; R6'da taşıma yok. Bu 42 hücre (`TASIMA_KORUR`) ve τ'nun uzun ömürlü pencereyi de aştığı 42 hücre (`UZUN_OTESI`) kapsam dışı bırakılıp ayrı raporlandı (`analiz/r6_esleme.csv`).

## N4. Strateji dosyasının yolu (Ö5)
- Ö5'e göre dondurulmuş dosya `model\comparison\stratejiler.yaml`. ASP çalışmasının oraya yazma izni yok. Taslak: `models\asp\sorgular\stratejiler_taslak.json` (sürüm 2, SHA-256 `11b05877024f49e01df19ec906468ba7b59240cf8ba9c1ee8c76df788c131e41`, 2026-09-25T12:34:31Z). Sürüm 1 (`b749dd47…`, 24.09) §2C öncesi artefakt düzeyi modele aitti; hiçbir karşılaştırma koşulmadan değiştirildi. Adım 8'de YAML'a taşınıp dondurulması önerilir.
- S5e (S5 kümeleri + P4 + M-f) **keşifseldir**: sıra etkisini beklenti etkisinden ayırmak için eklendi, ön kayıtta yok.

## N5. Teknik kapı örneklem çerçevesi (§2F madde 2): dışa aktarıldı, ÖRNEK SEÇİLMEDİ
- **`models/asp/sampling/cerceve.jsonl`**: birincil yapılandırmada Q'nun (675 hücre) her asgari kümesi ("asgari") ve her asgari kümeden tek elemanı eksik her küme ("bir-eksik"; aynı hücrede aynı küme birden çok kaynaktan doğarsa tek satır, kaynaklar listelenir).
  - **Satır: 2.442** · **SHA-256: `0a9b10d169a2898b97a6463fc481385a359744a981c392560ad0355f01942d87`**
  - Katmanlar (hedef × tür): G1 asgari 81 / bir-eksik 546; G2 117 / 1.071; G3 81 / 546; **G4 ve tümü: 0 satır.** Satırı olan hücre: 189.
  - Neden G4/tümü boş: bkz. N7. Seçim betiği için dolu katman sayısı 6'dır (§2F: kalan örnekler tohumla bütün çerçeveden tamamlanır).
  - Tutarlılık denetimi: 279 "asgari" satırın hepsi `verified`, 2.163 "bir-eksik" satırın hepsi `falsified` (değerlendirme kipinde hesaplandı, varsayılmadı).
- **`models/asp/sampling/kesif_2x2.jsonl`**: §2D m.11 keşifsel ızgara {ca_baglama: ad, anahtar} × {ayni_ad_klasik_ca: yok, var} (diger_ca = var, klasik_sabit): SAT hücrelerde asgari + bir-eksik; ayrıca her hücrede birincil asgari kümelerin o hücredeki hükmü ("birincil-kume").
  - **Satır: 8.442** · **SHA-256: `c1e810c8c5f077790e9feb27ab6ddd8c0031ac3019a2d0c1503a4a2e5a3fb2ec`**
  - Katmanlar (hedef × tür): G1 asgari 243 / bir-eksik 1.638 / birincil-kume 324; G2 351 / 3.213 / 468; G3 243 / 1.638 / 324. Satırı olan hücre: 756.
  - Kombinasyon × tür: ad/yok 279 + 2.163 + 279; anahtar/yok ve anahtar/var aynı; **ad/var: yalnız 279 "birincil-kume" satırı, hepsi `falsified`** (aynı adlı klasik CA ile ad bağlaması atlatılıyor; ad/var'daki bütün G1–G3 hücreleri UNSAT olduğundan asgari/bir-eksik satırı yok). §2F'deki zorunlu ek örnek bu türden seçilebilir (şablon `R7_mh_x.spthy`: CA_PQ, ALT_CA, NAME_BIND, ALT_SAME_NAME).
- Biçim: `sampling/SEMA.md`; özet: `sampling/disa_aktarim_ozeti.json`.

## N6. S2'nin önceden kayıtlı beklentisi tutmadı (0 beklenmişti, 9 gözlendi)
- **Ne:** Strateji karşılaştırmasının 3. önceden kayıtlı sorusu "S1 ve S2 Q-day sonrası kaç hücreyi sağlıyor? (beklenen 0; sağlık)". S1: 0 (tuttu). **S2 (ECCG AND, P1, beklentisiz): 9 hücre** (cl; G1–G3 × Φ3 × 3 τ). WebPKI PQ iken 15.
- **Neden:** Φ3'te hiçbir varlığın klasik alternatifi kabul edilmiyor (sınıf düzeyi gün batımı). Bu durumda beklenti kanalına gerek yok: bütün düğümler PQ ise G1–G3 sağlanır. "Beklenen 0", Φ3'ün gün batımı okumasını hesaba katmıyordu. Φ1/Φ2'nin 24 hücresinde S2 0/24 (beklentiyle uyumlu).
- **Önerilen karar:** Beklentinin "Φ1/Φ2'de 0" diye okunması ve farkın sonuç görüldükten sonra §11'e yazılması. Sonuç değiştirilmedi.
- **Etkilenen:** ön kayıt strateji karşılaştırması (sağlık sorusu), RAPOR §4.2.

## N7. Birincil yapılandırmada G4 ve "tümü" sağlanamıyor (135 + 135 hücre UNSAT)
- **Ne:** Birincilde G4 hiçbir PQ kümesiyle sağlanamıyor: imzasız istek HAIP gereği kabul ediliyor (T281), origin'i klasik WebPKI doğruluyor (T282), WRPRC doğrulaması ertelenmiş (faz0, T254), dolayısıyla RP başına kimliği doğrulanmış beklenti taşıyıcısı yok. "Tümü" G4'ü içerdiği için o da UNSAT.
- **Sonuçları:**
  - Kapı çerçevesinde G4/tümü katmanları boş (N5).
  - M1 paydası 36 hücre: G4'ün 9 hücresini S3 (M-d, bant dışı) dışında hiçbir strateji WebPKI klasikken sağlayamıyor.
  - H4 birincilde G4 hücreleri "ikisi de sağlamaz" (9).
- **Bu bir bulgudur** (M-b0 izinin ve H1'in G4 yüzünün biçimsel karşılığı), model hatası değil. OAT `wrprc_faz1` G4/tümü P4 hücrelerini SAT yapıyor (54 hücre; G4 kümesi {a02, a11, a12} + `tasi(a11_kayit, a12_istek)`). `md_kanca_acik` de aynı 54 hücreyi SAT yapıyor.
- **Önerilen karar:** (a) Teknik kapı örnekleminde G4 için ayrı bir keşifsel katman (ör. `wrprc_faz1` ya da H1 tasarımının WebPKI-PQ hücrelerinden) eklenip eklenmeyeceği. Bu, ASP çalışmasının değil yürütücünün seçimidir; istenirse aynı biçimde ikinci bir çerçeve dosyası üretilebilir. (b) Makalede G4'ün birincil sonucunun "WRPRC doğrulaması zorunlu olmadıkça RP kimliği PQ'ya taşınamaz" diye raporlanması.

## N8. H4 (2a) sınıflamasının yorumu (onay gerekir)
- **Ne:** `sorgular/h4.py` S5'i S7 ile hücre başına karşılaştırıyor ve farkı şöyle sınıflıyor:
  - **yetersiz(beklenti):** S5 + P4 + M-f (S5e) sağlıyor. Bu H3 kaynaklıdır (Ö2); (2a) sayılmaz.
  - **yetersiz(düğüm):** eksik düğüm G4'te ya da A13'te ya da kısa pencereli bir anahtarda ise (2a) adayı. Eksik düğümler uzun ömürlüyse (Ö3) sayılmaz.
  - **israflı(τ):** S5'in fazlası, aynı hücrenin hızlı τ karşılığında gerekli olan kısa pencereli bir anahtar. Bu (2a) adayıdır.
  - **israflı(diğer):** fazlalık yol dışı ya da uzun ömürlü düğümlerdir; sayılmaz.
- **Birincil 36 hücre:**
  - yetersiz(düğüm) 12: G1/G2 Φ1'de eksik {a04, a07}, G3 Φ1'de {a04, a08}, G3 Φ2'de {a08}. Hepsi V1 ya da CA anahtarı, yani uzun ömürlü; Ö3 gereği sayılmadı.
  - yetersiz(beklenti) 6: G1/G2 Φ2.
  - israflı(diğer) 9: Φ3'te G1–G3.
  - ikisi de sağlamaz 9: G4.
- **Yorum sorusu:** Φ3'teki 9 israflı hücre (2a)'nın lafzına ("S5 en az bir artefakt sınıfı fazladan göç ettiriyor, M2 farkı ≥ 1") uyuyor. Ama fazlalık, S5'in Φ3 tanımından ("HEPSI") ve hedefe özgü hücre tanımından geliyor. Aynı fark S2, S3, S4 ve S6'da da var; fazla düğümler (10–11 düğüm) hedef yolunda değil. Bunları (2a) saymak koşulu önemsizleştirir (GİRMEYİN #18 ile çelişir). **Saymadım; karar yürütücüde.**
- **Ö3 hücrelerinde 10 aday:**
  - G4 imzasız istek + WRPRC faz1 (cl/pq × Φ1/Φ2), 4 hücre: S5'te a11/a12 yok → yetersiz(düğüm).
  - `G2_cnf1g_{orta,yavas}`: a10 fazla → israflı(τ).
  - `G3_durum_{gunluk,gecici}_{orta,yavas}`: a08 fazla → israflı(τ).
  - (2a)'nın ek koşulu gereği her biri için en az bir Tamarin örneği gerekir; henüz yok.
- **Şeffaflık (sonuç görüldükten sonra değişen tanımlar):**
  - H4 filtresi ilk sürümde uzun ömürlü V1 anahtarlarını da sayıyordu; rejim-bilinçli hale getirildi.
  - A.3.2.2 adlandırılmış hücrelerinde M-b0 (imzasız istek) farkı maskeliyordu; bu hücreler `wrprc_dogrulama = faz1` ile yeniden tanımlandı.
  - Model kuralları değişmedi.

## N9. Politika eşdeğerliği ve P3
- P0, P1 ve P2 bu soyutlamada aynı sonucu veriyor: birincil, h1, h2, h5, cab, oat ve tau gruplarındaki 10.305 hücre grubunun hepsinde üç politikanın asgari küme ailesi özdeş. Nedeni: kırılan klasik anahtarla tek imza yeter. Soyma ve anahtar–alg bağlama farkları uygulama düzeyindedir ve C3'e aittir.
- **P3** (beklenti klasik kanaldan):
  - S2'de, k sınırsızken Φ1/Φ2'de UNSAT.
  - k = 1'de yalnız G1'e bakılınca SAT (OAT k1): klasik kanal tek başına bir sahtecilik açmıyor.
  - G1+G5 birlikte k = 1'de de UNSAT, çünkü zamansız G5 çiğneniyor.
  - S1'de (kırma yok) G1+G5 ve "tümü" ∅ ile sağlanıyor.
- **Önerilen karar:** H3 değerlendirmesinde G5'in zamansız tanımının (Ö11) P3'ü k'dan bağımsız olarak düşürdüğü açıkça yazılmalı.

## N10. k-bütçesi duyarlılığı: çekilen artefakt = iki kırma
- OAT `k1` 297 hücreyi değiştiriyor (108'i UNSAT→SAT). k = 1'de çekilen bir artefaktı sahtelemek hem imza hem taşıma anahtarını kırmayı gerektirdiği için:
  - G1/G2 kümesi {a03, a04, a07 (+a10)} oluyor; a01/a02 düşüyor.
  - **G3 ∅ ile sağlanıyor**, çünkü durum belirteci çekilen.
- `k3` yalnız 9 hücreyi değiştiriyor: sabit çıpa + Φ1 + P4'te a01 düşüyor. LOTL üzerinden TL beklentisini düşürmek 4 kırma istiyor: {a01_lotl, a13_lotl_kanal, alt(a02_tl), a13_webpki}. Değerlendirme kipinde doğrulandı: bu dört anahtar birlikte G1'i çiğniyor, dört üçlüsünün hiçbiri çiğnemiyor.
- **Önerilen karar:** Makalede k'nin OAT olarak raporlanması (birincil k sınırsız kalır). H1'in "klasik taşımada ikame yok" koşulunun **k sınırsız** varsayımına bağlı olduğu yazılmalı.

## N11. H1'in zaman sınırı: τ > TLS penceresi
- A5 ızgarasında 42 hücrede (`TASIMA_KORUR`) τ, TLS sunucu anahtarının penceresini aşıyor. Çekilen durum belirteci klasik taşımayla da korunuyor: H1'in (ii) koşulu bu τ'larda geçerli değil.
- Birincil w_tls = 1 y, nominal τ ≤ 26 g olduğundan birincil ve 2.4 tasarımlarında bu sınır görünmüyor.
- OAT `w_tls_47g` tek başına etkisiz (0 hücre), çünkü τ nominalde ≤ 26 g < 47 g.
- **w_tls 47 g + τ ≥ 47 g** birleşimi (CA/B Forum'un kısalan TLS sertifika ömrü + yavaş CRQC) iki sapmalı olduğu için OAT'ta yok.
- **Önerilen karar:** Bu birleşimin makalede "H1'in kapsam sınırı" olarak keşifsel bir hücreyle raporlanması. İstenirse tek sorguyla eklenebilir.

## N12. Önbellekli çıpa, sdjwtvc ve model dışı kalanlar
- `onbellek` kararlı durumda `taze` ile aynı (225/225 hücre). Q-day'den önce doldurulmuş kopyanın ilk penceresi `onbellek_ufku = ilk_pencere` OAT'ıyla modellendi: önbellekli 63 SAT hücrenin hepsinde a01 ve a02 düşüyor.
- `sdjwtvc_surum` biçimsel modelde etkisiz (OAT 0 hücre). §2D m.7'deki -13/-19 farkları C3 test vektörlerine aittir.
- **KAT'lar (isteğe bağlı) uygulanmadı; Adım 6'ya bırakıldı.** `literatur\analiz\KAT-SPEC.md` taslakları, olgu dosyası olarak doğrudan çekirdeğe verilebilecek biçimdedir.
- M3 (bayt) ve M4 (reddedilen eski ihraççı) **yapısal vekildir**; gerçek ölçümler Adım 12 ve C3'tedir.

## N13. Modele özgü varsayılanlar (§2C tablosunda olmayan parametreler)
- §2C 2.3 tablosunda olmayan parametreler temkinli ya da spesifikasyon varsayılanında tutuldu:
  - kimlik_turu pid, guven_deposu birleşik (T033, T034), anahtar_cozumleme x5c, lotl_indirme OJEU-sabit (T002), durum_imzaci aynı CA, durum_baglama sıkı, durum_kanali çekilen;
  - istek_iletimi DC API, imzasız istek/meta kabulü var (T281, T086), tmd_isleme yok (T096), durum_listesi var, tek_kullanim cüzdan (T230);
  - wscd_pq var, diger_ca yok, coklu_cerceve yok, mekanizma kancaları kapalı;
  - saat payı 300 s (T392).
- Bunların OAT etkileri RAPOR §4.5'te. En etkilileri: `diger_ca` (189 hücre SAT→UNSAT), `guven_deposu_liste_bagli` (135; a01 düşer), `durum_listesi_yok` (135).
- **Önerilen karar:** Bu varsayılanların dondurulan ön kayda "işlemsel eşleme" ekiyle yazılması (N1 ile birlikte).

## N14. İleriye dönük: beklenti_kapsami ve A1
- §2D m.13'teki `beklenti_kapsami ∈ {yaprak_alg, yol_sinifi, anahtar}` modelde henüz parametre değil. `kenar/3` kimlikleri ve `tasi/2` kancası, kabul edilen yolun kenar sınıfları üzerinden eklenmesine hazır (Adım 7).
- A1 gereklilik matrisi çerçeveden türetildi. Bir-eksik satırların 2.163/2.163'ü hücrenin hedefini çiğniyor. Başka hedeflerin çiğnenmesi bilgi vermez, çünkü kümeler hedefe özgü.

## N15. Sınırlılık: tek model yazarı
- ASP, z3 ve Jacobi değerlendiricisi aynı çalışmanın elinden çıktı. Bağımsızlık yöntem ve kod düzeyinde: z3 ASP çekirdeğini okumuyor, sonlu k'da CEGAR kullanıyor. Gerçek bağımsız doğrulama teknik kapıdaki Tamarin örneklemesidir.
- **Önerilen karar:** Teknik kapı raporunda bu sınırlılığın açıkça yazılması.
