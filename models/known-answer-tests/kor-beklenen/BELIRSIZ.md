# Belirsiz ve yoruma bağlı hücreler (kat-kor, Adım 6 görev 0)

Bu dosyanın iki bölümü var:
- **§A:** `BEKLENEN-KOR.tsv`'de değeri `belirsiz` yazılan satırlar. Kaynak ya da hücre tanımı değeri belirlemiyor.
- **§B:** Değer yazılmış, ama bir yorum kararına dayanan hücreler. Her birinde alternatif okuma ve o okumanın değeri de veriliyor.

İlk çalışmanın tablosuyla uyuşmazlık çıkarsa önce buraya bakın: uyuşmazlığın çoğu, §B'deki bir yorum ayrımına denk gelmeli.

---

## §A. `belirsiz` satırlar (3)

### A1. K2d-01, K2d-02, K2d-03: `Tamarin` sütunu

**Neden belirsiz:**
- Değer sözlüğü KAT-2b için lemmayı adlandırıyor ("Tamarin bayrakları verilmişse `cert_authentic`"), KAT-2d için adlandırmıyor ("Tamarin verilmişse ∈ {verified, falsified}").
- Girdi §1.4'e göre KAT-2 Tamarin dosyasında bir kimlik doğrulama lemması (all-traces) ve bir duyarlılık lemması (exists-trace) var.
- K2d bayraklarında `CRQC` yok, yani saldırgan M1'dir. Üç aday lemma üç ayrı sonuç veriyor:

| Aday lemma | K2d-01 (V_IGNORE) | K2d-02 (V_ENFORCE_IF_PRESENT) | K2d-03 (V_REQUIRE) | Dayanak |
|---|---|---|---|---|
| (a) `cert_authentic`: kabul edilen sertifika CA'nın verdiği sertifikadır | verified | verified | verified | Kim s. 60: M1 "cannot forge a classical signature … so every certificate it presents was issued by a real authority" |
| (b) hibrit kimlik doğrulama (all-traces): kabul ⇒ PQ kanıtı doğrulandı | falsified | falsified | verified | Kim §III-D güvenlik hedefi; s. 445: "Under M1, P1 provides no more protection than P0" |
| (c) duyarlılık (exists-trace): PQ kanıtı yokken ya da geçersizken kabul eden bir iz var | verified | verified | falsified | Girdi §1.4 "duyarlılık lemması (exists-trace)"; Lee s. 121 |

**Bu çalışmanın sıralaması (kanıt değil):**
- (b) en olası. Girdi §0 ölçüt 3 ortak hücrelerde ASP–Tamarin uyumu istiyor. K2d'nin ASP kararı P0/P1'de accept_classical, P2'de reject; bu farkı yalnız (b) ya da (c) yansıtır.
- (a), K2b ile aynı lemma adını kullanması bakımından olası. O durumda K2d Tamarin sütunu M1/M2 ayrımını gösterir: M1 altında sahteleme yok.

**Çözüm:** Tamarin dosyasındaki lemma tanımına bakılmalı.

---

## §B. Yoruma bağlı değerler (değer yazıldı; alternatif okuma verildi)

### B1. Zaman sabitleri (KAT-1, KAT-2b; genel)

Girdide şunlar yok: varsayılan `now`, `qday`, `tau` (τ), `exposure` ve sürüm imza aralıkları. Değerleri Tamarin bayraklarının kodladığı mantıksal durumdan türettim (TURETME §0.1). Aşağıdaki sayısal koşullar sağlanmıyorsa ASP değeri değişir:

| Hücre | Yazılan | Varsayılan koşul [Y] | Koşul tutmazsa |
|---|---|---|---|
| K1-05 | SALDIRI | Eski DS'nin imzası now=50'de geçerli ve max(qday, exposure(K_1 ya da Z_10)) + τ ≤ 50 | YOK |
| K1-07 | SALDIRI | Eski DK3'ün K_2 imzası varsayılan `now`'da geçerli; klasik Z_10 kırık | YOK |
| K1-09 | YOK | DK3'ün ve eski DS'nin imzası 150'de dolmuş | SALDIRI |
| K1-14 | SALDIRI | K1-09 koşulu + ek çapa klasik ve kırık | (bkz. B3) |
| K1-13 | YOK | Varsayılan `now` < 200 | SALDIRI |
| KAT-1, KAT-2b diğer CRQC hücreleri | SALDIRI | Varsayılan qday ≤ now, τ kırılmayı `now`'dan sonraya itmiyor | YOK |

### B2. K1-04, K1-06, K1-11: bütünlük testinin kapsamı

- **Yazılan:** YOK / verified. Test, DS'nin işaretlediği algoritmaları A RRset'i dahil zincirin tamamında ister.
- **Alternatif:** Test yalnız DNSKEY RRset'inde yapılır (RFC 6840 §5.11: "insist that all algorithms signaled in the DS RRset work"). Bu durumda DK3'teki Z_10 sahte A'yı doğrular (§6.2) → **SALDIRI / falsified**.
- **Gerekçe:** "work", algoritmanın doğrulama yolunda çalışmasını ifade ediyor. Girdi §0 da "bütün algoritmaları isteyen politikada inmediğini" beklenen sonuç olarak anıyor (ÖK §4.19).

### B3. K1-14: `extra_ta`'nın sınıfı

- **Yazılan:** SALDIRI / falsified. Ek çapa eski klasik çapadır (RFC 6840 Ek C.2: "old trust anchors configured in perpetuity", "weakest of these trust anchors").
- **Alternatif:** Ek çapa PQ ise hücre K1-09'un eşi olur → **YOK / verified**.

### B4. K1-15: `allpresent`

- **Yazılan:** SALDIRI / falsified. Yanıtta bulunan RRSIG'ler denetlenir, saldırgan Q imzasını göndermez.
- **Alternatif:** "DNSKEY RRset'indeki her algoritma gerekli"; bu RFC 6781 §4.1.4'teki "conservative approach"tır. O okumada **YOK / verified**.
- **Neden reddedildi:** Girdi eşlemesi bu politikayı "fırsatçı: varsa denetle" diye tanımlıyor ve DNSSEC karşılığını "—" veriyor. RFC 6840 §5.11 de "MUST NOT insist that all algorithms signaled in the DNSKEY RRset work" diyor.

### B5. K1-08 (ve K1-06): tekdüzelikte "görülmüş sürüm"

- **Yazılan:** YOK / verified. Doğrulayıcı en yeni sürümü (DS_K_2 ya da DK5) görmüştür.
- **Alternatif:** İlk temasta `seen` boştur; K1-08 **SALDIRI** olur.

### B6. K2a-10: catalyst, `enforce_if_present`, geçersiz PQ

- **Yazılan:** reject. Dayanak: Lee s. 121 (wolfSSL "a leaf with a forged ML-DSA alternative signature is rejected"), Kim s. 306 ve s. 97 ("outcome-bearing").
- **Alternatif:** Kim Tablo VI, P1 satırı, "invalid, absent, or unsupported" sütunu: "accept-classical permitted; never accept-hybrid" → **accept_classical**.

### B7. K2d-05: P3, ilk temas

- **Yazılan:** accept_classical. P3 yalnız geri dönüşü yasaklar (Kim s. 90); girdi eşlemesi P3'ü `monotone=1`'e bağlıyor.
- **Alternatif:** Kim Tablo VI'daki "P3 (hybrid + continuity)" başlığı P3'ün P2'yi içerdiği biçiminde okunabilir → **reject**.

### B8. K2d kanıt durumu

- **Yazılan:** PQ kanıtı saklandı (absent; M1). Bu durum, `seen_hybrid`'in kararı etkileyebildiği tek durum.
- **Alternatif:** Kanıt geçerli (dürüst hibrit sunum). O zaman K2d-01 accept_classical, K2d-02/03/04/05 **accept_hybrid** olur.

### B9. K2b-04 / K2b-05: TL beklentisinin silinmesi

- **Yazılan:** tl_cl → SALDIRI, tl_pq → YOK. Sinyal ancak kaynağı sahtelenerek kaldırılabilir.
- **Alternatif:** Saldırgan TL'yi düşürebilir ve doğrulayıcı TL'siz devam edip beklentisiz kabul ederse, K2b-05 de **SALDIRI** olur. Girdi bu davranışı tanımlamıyor.

### B10. K2c: sözlük eşlemesi

Kim Tablo V'nin varsayılan yol sütunu gözlem sözlüğünü kullanıyor (s. 396: "Default-path cells use the observational vocabulary"). "classical-accept" → `accept_classical` eşlemesi Kim s. 130'a ve Şekil 1'e dayanıyor. Değer değişmez, yalnız etiket eşlemesi.

### B11. o6: hibritin onay durumu

- **Yazılan:** unsafe_mixed. Hibrit onaylı sayıldı.
- **Alternatif:** Onaysız ise yol kümesi {Unknown, Classical} olur → `out` = **unknown**.
- Kabul değerleri (0, 0) iki okumada da aynı.

### B12. o10: onaysız hibrit

- **Yazılan:** unknown. Aşama 3: "Unsupported … Unknown"; "fail closed".
- **Alternatif:** Onaysız yapı bir "algorithm-profile requirement" ihlali sayılırsa (Tablo 1) → **invalid**.
- Kabul değerleri (0, 0) iki okumada da aynı.

### B13. o8: yazıldığı gibi ve model farkı

- **Yazılan:** pqc_protected, 1, 1. Das'ın literal kuralı: V_i = 0 olan yol kapsam dışı.
- **Model farkı (ayrı raporlanacak, girdi okuma notu):** CRQC'li saldırgan RSA yolundan CEK'i sertifika geçerliliğinden bağımsız çıkarır. Gizlilik açısından bu vektör unsafe_mixed ve 0/0 olurdu.

### B14. HYBRID_KEM bayrağı

- **Yazılan:** verified. Bayrak tek başına, yalnız hibrit alıcı.
- **Alternatif:** Bayrak klasik bir alıcıyla birlikte koşulursa (o6 benzeri) → **falsified**.

### B15. V4: statik ihlal

- **Yazılan:** 0. Statik denetim, beklentiyi V_i'nin "policy constraints" bileşeni olarak hesaba katar (Das s. 142).
- **Alternatif:** Denetim yalnız yapısal yolları sayarsa (TL, C anahtarını da tanıtıyor) → **1**. Bu durumda statik/dinamik eşdeğerliği V4'te bozulur ve bu bir model bulgusu olur.

### B16. KAT-3b: doğrulayıcı politikası

`expect=0` iken doğrulayıcının anyvalid olduğu varsayıldı. Girdi `pol` vermiyor. Doğrulayıcı yerel bir P2 taşısaydı, V1/V3 dinamik saldırıları yalnız TL yoluyla açılırdı: V1 yine SALDIRI, **V3 YOK** olurdu.
