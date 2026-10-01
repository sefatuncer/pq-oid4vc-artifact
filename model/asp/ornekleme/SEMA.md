# Örneklem çerçevesi dışa aktarım biçimi (Adım 3 → teknik kapı → Tamarin)

> **Üreten:** `ornekleme/disa_aktar.py` (ASP çalışması). **ASP çalışması örnek seçmez** (ön kayıt §2F madde 2): seçim yürütücünün tohumlu betiğiyle yapılır (tohum 20260926; katmanlar hedef × tür).
> **Dosyalar:** `cerceve.jsonl` (kapı çerçevesi), `kesif_2x2.jsonl` (§2D m.11 keşifsel ızgara; kapı sayımına girmez), `disa_aktarim_ozeti.json` (satır sayıları, SHA-256, katman sayımları).
> **Kodlama:** UTF-8, satır başına bir JSON nesnesi (JSON Lines), anahtarlar sıralı, satır sonu `\n`.

## 1. Çerçeve tanımı (ön kayıt §4.18, §2F)

- **Hücre:** birincil yapılandırmada (§2C 2.3) Q'nun bir elemanı = hedef {G1, G2, G3, G4, tümü} × Φ {f1, f2, f3} × τ {hızlı 600 s, orta 259.200 s, yavaş 2.246.400 s} × çıpa {taze, sabit, onbellek} × politika {p0…p4}.
- **`asgari` satırı:** hücrenin bir alt küme bakımından asgari (PQ düğümü ∪ beklenti taşıyıcısı) kümesi. **Beklenti: Tamarin'de verified.**
- **`bir-eksik` satırı:** bir asgari kümeden tek bir eleman (bir PQ düğümü ya da bir taşıyıcı) çıkarılmış küme. Aynı hücrede aynı küme birden çok asgari kümeden doğarsa tek satır yazılır; `kaynaklar` hepsini listeler. **Beklenti: iz (Tamarin'de falsified).**
- **`birincil-kume` satırı** (yalnız `kesif_2x2.jsonl`): birincil yapılandırmanın aynı Q hücresindeki asgari kümesinin, ızgara hücresinin parametreleri altındaki hükmü. `ca_baglama = ad, ayni_ad_klasik_ca = var` hücresinde bütün G1–G3 hücreleri UNSAT olduğu için §2F'deki zorunlu ek örnek bu türden seçilebilir.
- **UNSAT hücreler** satır üretmez (asgari küme yok). Birincil yapılandırmada G4 ve "tümü" hücrelerinin hepsi UNSAT'tır (NOTLAR N5).

## 2. Satır alanları

| Alan | Tür | Anlam |
|---|---|---|
| `satir_id` | dize | `CERCEVE-000001` … / `KESIF_2X2-000001` … (dosya içinde tekil, sıra = üretim sırası) |
| `kaynak` | dize | `birincil` / `kesif_2x2` |
| `hucre_id` | dize | Sorgu kimliği, ör. `birincil|g2|f2|hizli|taze|p4` ya da `cab|ad|var|g1|f1|hizli|taze|p4` |
| `hucre` | nesne | `hedef, faz, tau (etiket), tau_s (saniye), capa, politika, tasarim` (+ 2×2'de `ca_baglama, ayni_ad_klasik_ca`). Diğer bütün parametreler birincil değerdedir (§2C 2.3; RAPOR §1.5) |
| `hedef` | dize | `G1` `G2` `G3` `G4` `tumu` (katman anahtarı) |
| `tur` | dize | `asgari` / `bir-eksik` / `birincil-kume` (katman anahtarı) |
| `kume.pq_dugumler` | liste | PQ olan karar düğümleri (§2C 17 düğüm: a01 a02 a03 a04 a05 a06 a07 a08 a09a a09b a10 a11 a12 a13 ecrl ejvi eas). Listede olmayan düğüm klasiktir |
| `kume.tasiyicilar` | liste | Seçilen beklenti taşıyıcıları `[C, X]`: C artefaktı, X'i imzalayan varlık için "PQ gerekli" beklentisi taşır (politika P3/P4) |
| `asgari_no` / `kaynaklar` / `birincil_asgari_no` | | Satırın türettiği asgari küme(ler) ve (bir-eksik için) çıkarılan eleman: `pq(aXX)` ya da `tasi(C,X)` |
| `asp_tahmini` | dize | `verified` (hedef sağlanır) / `falsified` (hedef çiğnenir). ASP'nin değerlendirme kipinde (`cekirdek.lp`, senaryo `tum` = k sınırsız S2) HESAPLANMIŞTIR; varsayılmamıştır |
| `ihlal_edilen` | liste | Bu atamayla çiğnenen bütün hedefler (g1…g4, tum, g5 zamansız, g2i keşifsel) |
| `tanik_sahte_artefaktlar` | liste | Tanık: doğrulayıcıya etkin biçimde sahtesi ulaştırılabilen artefaktlar (iz için saldırı yolu ipucu) |
| `alt_cizge` | liste | Hedef(ler)in yolundaki artefaktlar (§3) |
| `tamarin` | nesne | Şablon ve bayrak eşlemesi (§4) |

## 3. `alt_cizge` öğesi

| Alan | Anlam |
|---|---|
| `artefakt`, `dugum` | Model artefaktı ve ait olduğu karar düğümü (aynı düğüm = birlikte göç) |
| `pq` | İmzalayan anahtar PQ mu (imzasız A06/E_JVI/E_AS için: PQ-bağlı mı) |
| `sabit` | İmzalayan anahtar bant dışı sabitli mi (R5; OJEU) |
| `kanal` | `aktarilan` / `cekilen` / `sabitlenmis` / `sunan_uc` / `yalniz_tasima` / `kimliksiz` |
| `tasima`, `tasima_sahtelenebilir` | Çekilen/yalnız-taşıma artefaktın taşıması (webpki / lotl_kanal) ve sunucu kimlik doğrulamasının sahtelenebilirliği |
| `tanitici` | İmzalayan anahtarı tanıtan (sertifikalayan/listeleyen) artefaktlar: OR-kenarları (any-valid-path) |
| `klasik_alternatif` | Faz gereği varlığın klasik anahtarı da kabul ediliyor mu (K4) |
| `beklenti_var` | Kimliği doğrulanmış varlık başına beklenti etkin mi (K3) |
| `pencere_s`, `pencere_sinifi` | W_güven (saniye) ve sınıf: `uzun_omurlu` / `donem` / `belirtec` (Tamarin R6 LONG / ROTATED / PER_TOKEN) |
| `klasikse_pencerede_kirilir` | τ < W_güven + saat payı (300 s) mı |
| `varyant` | Etkin imzasız biçim (ör. `a05_meta_imzasiz`, `a12_istek_imzasiz`; M-b0) |
| `sahte` | Bu atamada etkin sahte mi |

## 4. `tamarin` eşlemesi

- `sablonlar`: hücrenin yolunu kuran Tamarin şablonları; `spthy_onerisi`: dosya adları (`model\tamarin\modeller\`).
  - `R5` LOTL(sabit) → TL/LoTE; `R1` çapa → CA → yaprak (G1/G2: kimlik bilgisi; G3: durum belirteci imzacısı); `R1(WRPAC)` G4 zinciri; `R4` cnf/KB-JWT; `R2/R3` birlikte yaşama + beklenti kanalı; `R6/R6h5` kısa pencereli anahtar; `R7hx` alternatif/aynı adlı klasik CA (yalnız 2×2).
- `bayraklar` (düz Boole; Tamarin `-D` bayraklarıyla aynı adlar kullanıldı):

| Bayrak | ASP karşılığı |
|---|---|
| `LOTL_PQ`, `TL_PQ` | a01, a02 ∈ `pq_dugumler` |
| `PIN_TL` | çıpa = sabit (TL imza anahtarı bant dışı; R5) |
| `LOTE_OJEU_YOLU` | birleşik güven deposu: çapa OJEU-sabit LoTE'de de listeli (LOTL'den bağımsız ikinci yol) |
| `LOTL_KANAL_PQ`, `CEKILEN_TASIMA_PQ` | a13 ∈ `pq_dugumler` (birincilde WebPKI klasik → her zaman yanlış) |
| `ROOT_PQ`, `CA_PQ`, `ISS_PQ` | a03 (çapa anahtarı), a04 (CA anahtarı), a07 (ihraççı anahtarı) — R1 sözleşmesi: pq(L) = L'yi İMZALAYAN anahtar PQ |
| `DURUM_YAPRAK_PQ`, `DURUM_CEKILEN_VIA_TLS` | a08 ∈ küme; durum belirteci çekilen (R3 VIA_TLS; taşıma klasikse ulaştırılabilir) |
| `DEV_PQ`, `SINGLE_USE` | a10 ∈ küme; tek kullanım cüzdanda (pencereyi değiştirmez; H5) |
| `ACCESS_CA_PQ`, `RP_KEY_PQ`, `IMZASIZ_ISTEK_KABUL` | a11, a12 ∈ küme; imzasız istek kabulü (M-b0) |
| `COEXIST`, `BEKLENTI`, `BEKLENTI_TASIYICI_PQ` | yoldaki PQ düğümlerinden klasik alternatifi açık olanlar ve her biri için beklentinin etkinliği; taşıyıcı eşlemesi X → C |
| `R6`, `R6_tau_s` | kısa pencereli anahtarlar: sınıf, pencere, "τ pencereden uzun mu" (R6 sembolik rejimi: FAST ⇔ yanlış) |
| `ALT_CA`, `NAME_BIND`, `KEY_BIND`, `ALT_SAME_NAME`, `ALT_CA_KLASIK_SABIT` | 2×2: diger_ca = var; ca_baglama = ad / anahtar; ayni_ad_klasik_ca = var; alternatif CA anahtarı göç ettirilemez (R7hx) |

- `lemma`: çevrilecek güvenlik lemması. Beklenen Tamarin hükmü `asp_tahmini`'dir.
- **Soyutlama notu:** Tamarin şablonları zamanı bayrakla temsil eder (τ ASP'de). R6 bayrağı `tau_pencereden_uzun = doğru` ise ilgili anahtarın kırma kuralı yalnız pencere kapandıktan sonra tetiklenebilir (R6 SLOW/MEDIUM). Uzun ömürlü anahtarlar birincil τ ızgarasında her zaman kırılabilir.
