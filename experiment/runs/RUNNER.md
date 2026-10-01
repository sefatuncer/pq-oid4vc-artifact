# C3 koşucu arayüzü (yürütücü, 01.10.2026)

Bağlayıcı kaynak: `experiment/oracle/oracle-A/adaptor-sozlesme.md` (sözleşme 1.0). Bu dosya, iki adaptör yazarının uyumlu çıktı üretmesi için ortak **çağrı biçimini** sabitler.

## 1. Girdi

- **Vektörler:** `experiment/vector-generator/vektorler/v1.3/` (MANIFEST SHA-256 `SHA256SUMS`'ta). Konteynere `/v` olarak salt okunur bağlanır.
- **Doğrulama girdileri:** Her vektörün MANIFEST satırı ve `experiment/vector-generator/anahtarlar/` (JWKS ve güven çapaları). Konteynere `/anahtarlar` olarak salt okunur bağlanır.
- **İş listesi:** satır başına bir JSON. Alanlar: `vektor_id`, `politika`, `kol`, `dosya` (`/v`'ye göreli), `serilestirme`, `artefakt`, `algler`.
  - `jobs-v1.3.jsonl`: 858 satır. Oracle kararı **yok**; adaptör oracle'ı görmez.
  - `jobs-prefreeze-v1.3.jsonl`: 16 satır. **Ön kayıt dondurulana kadar YALNIZ bu dosya koşulur:** V± kapısı ve CMP00/CMP01 (TK ataması). `jobs-v1.3.jsonl`'nin geri kalanı dondurmadan sonra koşulur (ÖK §10; sözleşme §1).
- **Politika yapılandırması:** iş satırındaki `politika` alanı (GEC, IZIN-A, IZIN-AX, L4, L4-S, L4-Y, P0, P1, L4-YOL, GEC@-19, L4@-19). Anlamları `YONTEM.md` §2 ve sözleşme §2.2'de. A = ES256; X koldan gelir (kontrol-EdDSA → EdDSA; kontrol-Ed25519 → Ed25519; tedavi-ML-DSA-65 → ML-DSA-65; tedavi-composite → ML-DSA-65-ES256). R = {X} (L4 ailesi); W, sözleşme §2.2'deki gibi.

## 2. Çağrı

```
docker run --rm --network none -v <v1.3>:/v:ro -v <anahtarlar>:/anahtarlar:ro -v <isler>:/is:ro -v <cikti>:/c \
    a10-<hedef>:1 <adaptör komutu> /is/<isler dosyası> /c/<hedef>.<kosu>.jsonl
```

- Ağ kapalı (`--network none`); derleme imaj yapımında yapılır.
- Adaptör bütün iş satırlarını tek süreçte sırayla işler. Vektör başına 60 s sınırı vardır; aşımda `zaman-asimi` yazılır.
- Hedefin belgeli API'siyle temsil edilemeyen biçim için `sonuc_ham = uygulanamaz` ve `hata_sinifi = bicim-desteklenmiyor` (B6) yazılır. Bu karar API incelemesiyle **önceden** verilir ve `MAPPING.md`'ye yazılır.
- API'nin ifade edemediği politika için `sonuc_ham = ifade-edilemedi` yazılır (örnek: R kümesi, yalnız kompakt hedefte L4m).

## 3. Çıktı (satır başına; sözleşme §3'ün alt kümesi, zorunlu alanlar)

`hedef_id`, `hedef_surum`, `adaptor_sha256`, `kosu`, `vektor_id`, `politika`, `kol`, `sonuc_ham` (kabul | red | istisna | zaman-asimi | cokme | uygulanamaz | ifade-edilemedi), `hata_sinifi` (sözleşme §3.2 kapalı listesi ya da null), `hata_ozeti` (ilk 200 karakter), `dogrulanan_algoritmalar` (kütüphane gösterebiliyorsa; yoksa []), `api_yolu`, `sure_ms`.

Dört değerli karara eşlemeyi (accept-hybrid / accept-classical / reject / indeterminate / uygulanamaz) adaptör değil, **koşucu** yapar. Kullandığı girdiler: `sonuc_ham`, vektörün algoritmaları, `dogrulanan_algoritmalar` ve TK ataması.

## 4. Hedef klasörü (`experiment/runs/adapters/<hedef>/`)

- `Dockerfile`: `FROM pq-a09-env-<dil>:1.0`. Hedef, `experiment/environments/hedefler/<hedef>/`'deki kurulum kaydıyla aynı sürüm ya da commit'le kurulur.
- adaptör kaynağı.
- `MAPPING.md`: politika → API çağrısı eşlemesi, B6 kararları, istisna → `hata_sinifi` eşlemesi.
- `evidence/api-tarama.txt`: sözleşme §5.1'deki tarama komutu ve çıktısı.
- `NOTES.md`: TK önerisi (TK1/TK3; TK2 01.10'dan beri kapsam dışı), V± sonucu, sorunlar.

## 5. Kararlar (yürütücü, 01.10.2026)

- **TK2 kapsam dışı.** Yerel ML-DSA desteği olmayan hedef TK3'tür. Gerekçe: hiçbir hipotez TK2'ye dayanmıyor; T2 (McNemar) TK1 hedefleriyle koşulur ya da veri yetmezse tanımlayıcı raporlanır. ÖK v1.0 sapma kaydına girer.
- **Composite kolu:** composite -04'ü yerel destekleyen hedef yoksa bütün hedefler o kolda TK3'tür.
- **Tekrar:** 3 koşu (r1–r3), taze konteynerde (sözleşme §4).
