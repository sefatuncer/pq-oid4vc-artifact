# C3 (H6) istatistik girdisi — şema `c3-istat-girdi/1.0`

**Kapsam:** `c3istat` betiklerinin (Adım 9 görev 9) tek girdi biçimi. Adım 10 bu biçimde tek bir dosya üretir; dondurulmuş betikler yalnız bunu okur.

**Tanımların kaynağı:** ön kayıt (ÖK) `00-on-kayit\ON-KAYIT-TASLAK.md`. Başvurulan bölümler:
- §2B (n = 31; L4m/L4c; TK1–TK3; devir),
- §2D-A madde 2 (kontrol etiketi),
- §3.7, §4.13–§4.15, §6.3–§6.11.

Çelişki olursa ÖK geçerlidir. Bu şemadaki yorumlar `KARAR-NOTLARI.md`'de listelenir.

**Biçimler:**
- Kanonik biçim: tek bir UTF-8 **JSON** dosyası (§1).
- Eşdeğer **CSV** biçimi: `hedefler.csv` (+ isteğe bağlı `vakalar.csv`) (§4).

İki biçim aynı doğrulayıcıdan geçer ve aynı sonucu verir (test `test_uctan_uca.CsvJsonEsdegerlik`).

---

## 1. JSON dosyasının üst düzeyi

```json
{
  "sema_surumu": "c3-istat-girdi/1.0",
  "veri_turu": "sentetik",
  "aciklama": "serbest metin",
  "hedefler": [ { "...": "§2" } ],
  "vakalar":  [ { "...": "§3" } ]
}
```

| Alan | Tür | Zorunlu | Kural |
|---|---|---|---|
| `sema_surumu` | dize | evet | Tam olarak `c3-istat-girdi/1.0` |
| `veri_turu` | `sentetik` \| `olcum` | evet | Adım 9'da yalnız `sentetik` kullanılır. `olcum` yalnız dondurmadan sonra, Adım 10'da |
| `aciklama` | dize | hayır | — |
| `hedefler` | dizi | evet | En az 1 kayıt; `hedef_id` benzersiz |
| `vakalar` | dizi | hayır | Küme bootstrap'ı (ÖK §6.9) için. Yoksa bootstrap "veri yok" olarak raporlanır |

Tanınmayan alan **hata**dır (yazım yanlışları sessizce yutulmasın diye).

## 2. Hedef kaydı (`hedefler[]`)

Değer kuralları:
- `null` = değer yok. Nedeni `belirsiz_nedenleri` içinde yazılır.
- İkili alanlar yalnız `0` ya da `1` alır (JSON'da `true`/`false` da kabul edilir).
- Sıralı alanlar tamsayıdır.

| Alan | Tür | Zorunlu | Anlamı ve ÖK dayanağı |
|---|---|---|---|
| `hedef_id` | dize | evet | Benzersiz kimlik (ör. `SECIM.csv`'deki `JOSE-009`). Bootstrap'ta küme sırası bu alana göre sözlük sırasıdır |
| `tabaka` | `JOSE` \| `SDJWT` \| `COSE` \| `REF` | evet | ÖK §2B.1–3. `REF` = referans doğrulayıcı: **n'nin dışında**, bütün testlerin dışında, yalnız tanımlayıcı listede (ÖK §2B.4) |
| `adaptor_gecersiz` | ikili | evet | 1 ⇒ n_eff dışı (ÖK §4.15). Bu durumda ölçüm alanları `null` olabilir |
| `adaptor_gecersiz_gerekce` | dize | `adaptor_gecersiz = 1` ise evet | — |
| `tk_sinifi` | `TK1` \| `TK2` \| `TK3` | evet (REF hariç) | Tedavi kolu (ÖK §2B.7). T2 yalnız TK1 + TK2 |
| `l4_bicimi` | `L4m` \| `L4c` | evet (REF hariç) | ÖK §2B.6. Tanımlayıcı olarak raporlanır |
| `kontrol_etiketi` | `EdDSA` \| `Ed25519` | evet (REF ve `adaptor_gecersiz = 1` hariç) | ÖK §2D-A.2, §2E.3: kullanılan etiket hedef başına kaydedilir. Tanımlayıcı |
| `Y_L4` | ikili \| null | evet | H6'nın birincil değişkeni (ÖK §3.7, §2B.6) |
| `L_duzeyi` | 0…5 \| null | evet | Sıralı L0–L5 (ÖK §4.13) |
| `F_K` | ikili \| null | evet | Kontrol kolunda K1–K3'ten en az birinde oracle'dan sapma (ÖK §6.4) |
| `F_T` | ikili \| null | evet | Aynısı, tedavi kolunda |
| `D_soy` | ikili \| null | evet | Varsayılan yapılandırmada soyulmuş belgenin (K3) kabulü (ÖK §6.4) |
| `B1` | `red` \| `yok_sayma` \| `dogrulama_duser` \| null | evet | Bilinmeyen composite `alg` davranışı (ÖK §4.13) |
| `B2` | ikili \| null | evet | Karışık `x5c` zinciri politikası ifade edilebiliyor mu (1 = evet) |
| `B3` | ikili \| null | evet | Korumasız `x5c` işleniyor mu (1 = evet) |
| `B4_ozel_kod` | ikili \| null | evet | "Özel kodla ifade edilebilir" bayrağı (ÖK §4.13 belirleme kuralı) |
| `B4_satir` | tamsayı ≥ 1 \| null | `B4_ozel_kod = 1` ise evet | Özel kod satır sayısı (boş satır ve yorum hariç). `B4_ozel_kod ≠ 1` ise `null` olmalı |
| `B5` | `en_az_biri_gecerli` \| `mevcut_tumu_gecerli` \| `gerekli_kume` \| `diger` \| null | evet | Semantik sınıf |
| `B6` | ikili \| null | evet | Desteklenmeyen biçim ("uygulanamaz" kaydı) |
| `surum_8725bis_sonrasi` | ikili \| null | evet | T4 katmanı: hedef 21.08.2026'dan (8725bis-10) **sonra** sürüm çıkardı mı (ÖK §6.6) |
| `son_surum_tarihi` | `YYYY-MM-DD` \| null | hayır | Denetim alanı. Verilirse `surum_8725bis_sonrasi = 1 ⇔ tarih > 2026-08-21` olmalı; aksi hâlde hata |
| `pilot` | ikili | evet | P3 pilotu kütüphanesi (ÖK §0.3, §6.10) |
| `devralan` | ikili | evet | Doğrulamayı başka bir hedefe devrediyor (ÖK §2B.9; ör. WalletFramework → IdentityModel) |
| `devraldigi_hedef` | dize \| null | `devralan = 1` ise evet | Devredilen hedefin `hedef_id`'si; n içinde olması gerekmez |
| `belirsiz_nedenleri` | nesne `{alan: neden}` | `null` alan varsa evet | Her `null` ölçüm alanı için bir neden (§2.1) |

### 2.1 `null` nedenleri

| Kod | Anlamı | ÖK |
|---|---|---|
| `oracle_uyusmazligi` | Oracle A ile B uyuşmuyor | §4.15 |
| `kanit_kurali` | "İfade edilemez" kanıt kuralı sağlanmadı | §4.14, §4.15 |
| `kararsiz_3_tekrar` | Üç tekrarda değer 3/3 aynı değil | §4.15, §6.11 |
| `deneme_celiskisi` | Bağımsız denemeler çelişiyor | §4.15 |
| `uygulanamaz` | Alan bu hedef için tanımsız (ör. COSE'da `x5c`) | §4.13 B6 mantığı |
| `olculmedi` | Ölçüm yapılamadı (yalnız `adaptor_gecersiz = 1` iken ya da `REF` satırında) | — |

Kurallar:
- İlk dört kod ÖK §4.15'teki **"belirsiz"** sınıfıdır.
- `Y_L4 = null` ise nedeni bu dördünden biri olmalı. Tek istisna `olculmedi`dir; o da yalnız `adaptor_gecersiz = 1` ya da `REF` satırında kullanılabilir. `Y_L4` için "uygulanamaz" yoktur: her geçerli hedefe L4m ya da L4c uygulanır.
- Duyarlılık (i)/(ii) yalnız bu "belirsiz" hedeflere uygulanır (ÖK §6.10).

## 3. Vaka kaydı (`vakalar[]`, isteğe bağlı)

| Alan | Tür | Zorunlu | Anlamı |
|---|---|---|---|
| `hedef_id` | dize | evet | `hedefler`'de bulunmalı |
| `vaka_id` | dize | evet | Batarya v1.1 vektör kimliği (ör. `T1K_both_valid`). (`hedef_id`, `vaka_id`) çifti benzersiz |
| `kol` | `K` \| `T` \| `diger` | evet | Kontrol, tedavi ya da kol dışı (ör. X5C, REQ aileleri) |
| `uyum` | ikili \| null | evet | 1 = gözlenen karar oracle ile aynı, 0 = sapma |
| `belirsiz_neden` | §2.1 kodu \| null | `uyum = null` ise evet | Ör. `kararsiz_3_tekrar` (kararsız hücre, ÖK §6.11) |

## 4. CSV biçimi

**`hedefler.csv`**
- Başlık satırı §2'deki alan adlarıdır; sıra serbesttir.
- `null` → boş hücre. İkili → `0`/`1`.
- `belirsiz_nedenleri` → `alan:kod;alan:kod` (ör. `Y_L4:kanit_kurali;B2:uygulanamaz`).
- `sema_surumu` ve `veri_turu`, dosyanın ilk satırında yorum olarak verilir: `# sema_surumu=c3-istat-girdi/1.0; veri_turu=sentetik`.

**`vakalar.csv`**
- §3'teki sütunlar; aynı kurallar.

## 5. Analiz kümeleri (betiklerin uyguladığı tanımlar)

**Kümeler:**
- H_n = { tabaka ∈ {JOSE, SDJWT, COSE} }, n = |H_n|. ÖK §2B'ye göre n = 31 beklenir; farklıysa uyarı verilir, analiz sürer.
- H_g = H_n \ { adaptor_gecersiz = 1 }.
- Her değişken v için H_v = { h ∈ H_g : v(h) ≠ null }.

**n_eff (T1)** = |H_{Y_L4}| = n − adaptör geçersiz − belirsiz(Y_L4) (ÖK §6.3).

**Testler:**

| Test | Küme | Değişken | Yöntem |
|---|---|---|---|
| T1 | H_{Y_L4} | X = Σ Y_L4 | Kesin binom, alt kuyruk; c(n_eff), u = n_eff − c (Ek A kuralı); n_eff < 20 ⇒ yalnız tanımlayıcı |
| T2 | H_g ∩ {TK1, TK2} ∩ H_{F_K} ∩ H_{F_T} | b = #(F_K=0, F_T=1), c = #(F_K=1, F_T=0) | Kesin McNemar, iki yönlü; b + c = 0 ⇒ p = 1 |
| T3 | H_g ∩ {SDJWT, JOSE} ∩ H_{F_K} ∩ H_{F_T} | PQ = [F_T = 1 ∧ F_K = 0]; satırlar SDJWT, JOSE | Fisher kesin, iki yönlü. TK kapsamı `yapilandirma.T3_TK_KAPSAMI` (varsayılan: hepsi; bkz. NOTLAR N-4) |
| T4 | H_g ∩ H_{L_duzeyi} ∩ H_{surum_8725bis_sonrasi} | [L ≥ 3]; satırlar sonra = 1, sonra = 0 | Fisher kesin, iki yönlü |
| T5 | H_{D_soy} | X = Σ D_soy | Kesin binom, üst kuyruk |

**Holm ve etki büyüklükleri:**
- Holm yalnız {T2, T3, T4, T5} ailesine uygulanır; m = 4 sabittir. Veri yoksa p = 1 alınır ve `veri_yok` bayrağı konur.
- Etki büyüklükleri ÖK §6.7'ye göre hesaplanır:
  - T1 ve T5: oran + Wilson;
  - T2: eşleştirilmiş fark (F_T − F_K) + Newcombe yöntem 10;
  - T3 ve T4: koşullu MLE OR + koşullu kesin GA; fark + Newcombe yöntem 10 (bağımsız).

**Duyarlılıklar (ÖK §6.10, §2B.9):**

| Kod | Tanım | Uygulandığı test |
|---|---|---|
| (i) | `Y_L4` belirsiz olanlar Y = 1 | T1 |
| (ii) | `Y_L4` belirsiz olanlar Y = 0 | T1 |
| pilot | `pilot = 1` hariç | T1 |
| devir | `devralan = 1` hariç | T1 ve T2; tanımlayıcı, Holm dışı |

**Küme bootstrap (ÖK §6.9):**
- Birim: `vakalar`'daki hedef (yalnız H_g).
- Oran: oracle'a uymayan vaka oranı = Σ(1 − uyum) / Σ vaka, `uyum ≠ null` vakalar üzerinden.
- Kapsam: hepsi, `K`, `T`.
- Ayarlar: B = 10.000; yüzdelik GA (tip 7); tohum 20260927. Ayrıntı: `DONDURMA-GIRDISI.md`.

## 6. Doğrulayıcı hataları (örnekler)

Şu durumlarda analiz **başlamaz** (çıkış kodu 3):
- eksik zorunlu alan, tanımsız enum değeri, yinelenen `hedef_id`;
- nedeni yazılmamış `null` ya da değeri `null` olmayan alana yazılmış neden;
- geçerli n hedefinde `kontrol_etiketi` yok;
- `Y_L4 = null` iken "belirsiz" dışı bir neden;
- `devralan = 1` iken `devraldigi_hedef` yok (ya da `devralan = 0` iken var);
- tarih ile `surum_8725bis_sonrasi` çelişkisi;
- `B4_satir` ile `B4_ozel_kod` tutarsızlığı;
- `vakalar`'da bilinmeyen `hedef_id` ya da yinelenen (`hedef_id`, `vaka_id`).
