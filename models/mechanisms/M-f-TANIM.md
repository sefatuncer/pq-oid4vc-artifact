# M-f — sadeleştirilmiş tanım ve yol kapsamı (Adım 7 görev 9)

- **Tarih:** 26.09.2026. **Durum:** Tanım; kanıt atıfları `sonuc/` altındaki koşumlara göredir (çapa 8'den sonra).
- **Kapsam:** Biçimsel tanım ve doğrulama kuralı. Spesifikasyon metni önerisi Adım 13'tedir.

## 1. Tanım

**M-f:** Yetkili bir üçüncü tarafın (TL/LoTE operatörü) varlık başına yayımladığı, PQ ile kimliği doğrulanmış, doğrulayıcının karar anında güncel gördüğü beklentidir. Beklenti, varlığın hangi kanıtının kabul edileceğini kanıtın **yolu** üzerinden kısıtlar.

**Çekirdek** (çevrimiçi ya da sabitlenmiş güncel görünüm; dört bileşen):
1. **Üçüncü taraf:** Beklenti, varlığın kendi beyanı değil, TL/LoTE kaydıdır.
2. **PQ kimlik doğrulama:** Kayıt ya da çözümleme yanıtı PQ anahtarla imzalıdır. İmzalayanın anahtarı bant dışı sabitlidir (OJEU).
3. **Varlık başına:** Her varlığın ayrı bir durumu vardır: `none` → `pq_required` → `retired`. Eski varlıklar `none` kalır.
4. **Güncel değer:** Doğrulayıcı karar anında güncel değeri görür. Bu, ya nonce'a bağlı taze bir sorguyla ya da sabitlenmiş ve güncel tutulan bir görünümle sağlanır.

**Kapsam** (`yol_sinifi`): Beklenti `none` değilse doğrulayıcı kimlik bilgisini yalnız bir koşulla kabul eder: TL/LoTE'de listelenen çıpadan kimlik bilgisine kadar kabul edilen yolun **her kenarı** PQ anahtarla imzalı olmalıdır.
- Çıpa kenarının sınıfı TL kaydındaki algoritmadır; adı değildir.
- Ara CA kenarının sınıfı, ara CA sertifikasındaki algoritmadır.
- Alternatif kapsam `anahtar`: kimlik bilgisi, beklentiyle birlikte taşınan PQ ihraççı anahtarıyla doğrulanmalıdır. Sahteciliği engeller, ama yol sınıfını güvenceye almaz.
- `yaprak_alg` kapsamı yetmez (§4).

**Çevrimdışı ek** (yalnız beklenti bayat olabilecekse; yola duyarlı tanımlar, Değişiklik 8):
- **Tekdüzelik (genişletilmiş):** Doğrulayıcı bir varlık için `pq_required` gördükten sonra o varlık için `none` beklentisini hiç kullanmaz. Yalnız klasik yaprağı reddetmek yetmez.
- **Sunset (beklenti düzeyinde):** `none` beklentisi, varlığın önceden ilan edilmiş sunset anından sonra geçersizdir. Yalnız klasik anahtarın süresinin dolması yol sınıfını korumaz. Diğer seçenek, sunset'te klasik çıpaların TL/LoTE'den çıkarılmasıdır.

## 2. Alanlar (varlık başına kayıt)

| Alan | Değer | Not |
|---|---|---|
| `state` | `none` / `pq_required` / `retired` | Yaşam döngüsü; yalnız ileri gider |
| `scope` | `path` (öneri) / `key` | `key` ise bağlı PQ anahtar (ya da özeti) kayıtta taşınır |
| `sunset` | zaman damgası | `none` beklentisinin geçerlilik sonu (çevrimdışı ek) |
| imza | TL/LoTE imzası (ML-DSA) | Kayıt, listenin tek imzasıyla korunur (T013, T022–T025) |

Belirlenimci boyut: XML ya da JSON öğesi olarak yaklaşık 87 B/varlık (`sonuc/ek_yuk.csv`). Çevrimiçi kipte doğrulama başına bir ek alım, sabitlenmiş güncel görünümde sıfır.

## 3. Doğrulama kuralı

Artefakt `x` (kimlik bilgisi, istek, durum belirteci) ve ihraççısı `I` için:

1. **Beklentiyi al.**
   - Çevrimiçi: TL/LoTE kaynağına nonce'lu sorgu; yanıt PQ imzalı ve bu doğrulamaya bağlı.
   - Sabitlenmiş: güncel görünümdeki kayıt.
   - Kaydın imzasını sabit PQ çıpaya göre doğrula.
2. **`state = none`** (ve çevrimdışı ekte, sunset geçmemiş ve `I` için daha önce `pq_required` görülmemiş): Bugünkü kurala göre doğrula (her geçerli yol).
3. **`state ∈ {pq_required, retired}`:**
   - Yaprak algoritması PQ olmalı; klasik yaprak reddedilir.
   - `scope = path`: yoldaki her kenar PQ olmalı; ilk klasik kenarda reddedilir.
   - `scope = key`: yaprağın anahtarı kayıttaki bağlı anahtar olmalı.
4. **Çevrimdışı ek:** `pq_required` görüldüğünde `I` için yerel durum kalıcı olarak `pq_required` olur. Sunset geçmişse `none` beklentisi kullanılmaz.

## 4. Kanıt durumu (Tamarin; `sonuc/karsilastirma.csv`)

Bu bölüm koşum sonuçlarıyla doldurulur: §5.

## 5. Sınırlar

- **İlk temas:** Çekirdek, beklentiyi ilk temastan önce sağlar; çünkü kayıt üçüncü taraftadır. Çevrimdışı ekte beklentiyi hiç görmemiş doğrulayıcı göçten sonra düşürülebilir. Bu, önbellek güncellenene kadar sürer (TS 119 612 "Next update" penceresi, ≤ 6 ay: T009/T010).
- **Taşıyıcı:**
  - Çekilen ve güncel TL/LoTE ya da OpenID Federation çözümlemesi çekirdeği sağlar; federasyonda ara varlık anahtarı da PQ olmalıdır.
  - WRPRC, doğrulama fazı başlayana kadar (T254) kimliksiz bir alandır. Faz1'de aktarılan ve yeniden oynatılabilir bir nesnedir.
  - `crit` başlığı taşıyıcı değildir.
- **Zaman:** Sembolik model gecikme ve pencere uzunluğunu sıra kısıtlarıyla temsil eder. Sayısal τ analizi R6 ve ASP'dedir.
