# İstatistik çalışmasından yürütücüye notlar (Adım 9, görev 9; 25.09.2026)

**Kural:** ÖK dosyasına dokunulmadı. Aşağıdaki öneriler dondurmadan önce yürütücünün kararına sunulur.

**Uygulanan okuma:** Her maddede yazılıdır. `betikler/c3istat/yapilandirma.py`'de ilgili sabitin yanında N-numarası vardır. Bir karar değişirse sabit değiştirilir, `tumunu_calistir.sh` yeniden koşulur ve `SHA256SUMS` ile `DONDURMA-GIRDISI.md` yenilenir.

**Sayılar:** Buradaki bütün sayılar `pq-a09-analiz:1.0` imajında betikle hesaplandı (`c3istat.kesin`).

---

## A. Karar gerektiren belirsizlikler (N-1…N-12)

### N-1 — T2–T5'te "n_eff" ve analiz kümesi
- **ÖK durumu:** §6.3 n_eff'i yalnız T1 için tanımlıyor (dahil − adaptör geçersiz − belirsiz). T2–T5 için küme tanımı yok.
- **Uygulanan:** Her test, kendi değişkenleri belirli (null olmayan) ve adaptörü geçerli hedeflerde hesaplanır:
  - T2: F_K ve F_T belirli, TK1/TK2;
  - T3: F_K ve F_T belirli, SDJWT/JOSE;
  - T4: L ve sürüm bayrağı belirli;
  - T5: D_soy belirli.
- Bu kümeler çıktıda hedef listesiyle raporlanır.
- **Öneri:** ÖK v1.0 §6.10'a bir cümle eklensin: "T2–T5'te belirsiz ya da uygulanamaz değerli hedefler ilgili testin dışında kalır; test başına n raporlanır."

### N-2 — Duyarlılık (i)/(ii) eşikleri ve simetri
- **Belirsizlik:** (i)'de belirsizler Y = 1 sayılınca örneklem n_i = n_eff + b olur. Eşik c(n_i) mi, yoksa birincil c(n_eff) mi?
- **Uygulanan:** c(n_i), Ek A kuralıyla.
  - Gerekçe: "X ≤ c" ölçütü, kendi n'si olan bir kesin testin p ≤ 0,05 kararıdır.
  - Bu okumada (i)'nin destek vermesi birincil desteği gerektirir: c(n+1) ≤ c(n) + 1 (`test_ek_a.GenelKural`).
- **Örnek:** n_eff = 29, X = 9 ⇒ birincil destek (c = 9). (i): X = 11/31 > c = 10 ⇒ "kırılgan destek" (`test_uctan_uca.H6Hukmu`).
- **Asimetri:** §6.10'da "kırılgan destek" var, "kırılgan yanlışlama" yok. Yanlışlama yalnız birincil analizle verilir; (ii) tanımlayıcı olarak raporlanır.
- **Öneri:** ÖK v1.0'da (a) c(n_i) okuması açıkça yazılsın; (b) yanlışlama için de simetrik bir sağlamlık notu istenip istenmediğine karar verilsin. Önerim: (ii) X ≥ u(n_ii) sağlamıyorsa "kırılgan yanlışlama". Bu, dondurmadan önce eklenirse betikte 3 satırlık bir değişikliktir.

### N-3 — Newcombe yöntem 10, eşleştirilmiş: korelasyon düzeltmesi φ\* ve kaynak sınırlılığı
- **ÖK durumu:** §6.7 yalnız "Newcombe GA (eşleştirilmiş, yöntem 10)" diyor.
- **Kaynak bulgusu** (`kaynak/NEWCOMBE-KAYNAK.md`): Açık erişimli ikincil kaynağa göre (ratesci, CRAN; commit `7ad93a58…`) yöntem 10, Wilson-hibrit aralığı **Newcombe'un düzeltilmiş korelasyonuyla** kullanır:
  - ad − bc > 0 ise φ\* = max(ad − bc − N/2, 0)/√(efgh); değilse φ̂; payda 0 ise φ = 0.
- **Ayırt edici kanıt** (betikle):
  - (20, 12, 2, 16) için φ\* yayımlanmış yöntem 10 değerini verir: (0,0562; 0,3292). Düz φ̂ ise "yöntem 8" değerini verir: (0,0618; 0,3242).
  - Fagerland örneğinde (1, 1, 7, 12) yalnız φ\* yayımlanmış değeri verir: (−0,507; −0,026). Düz φ̂ (−0,5017; −0,0361) verir.
- **Uygulanan:** φ\* (`NEWCOMBE_ESLESTIRILMIS_PHI = "newcombe_duzeltmeli"`).
- **Sınırlılık:**
  - Newcombe 1998a/b'nin birincil metni ödeme duvarlı; erişilemedi. OpenAlex "closed"; Wiley 403; CiteSeerX kaydı Wayback'e yönleniyor ve 429 veriyor. Hiçbir duvar atlatılmadı.
  - Yayımlanmış değerler ikincil kaynaktan birebir aktarıldı.
  - Güvence üç katmanlı: iki uygulamanın 8.814 vakada uyumu; φ = 0'da statsmodels'ın bağımsız `newcomb` aralığına 4.844 vakada eşitlik; elle türetilebilir sınır vakaları.
- **Öneri:**
  - (a) ÖK v1.0 §6.7'ye φ\* formülü açıkça yazılsın.
  - (b) **İnsan adımı (isteğe bağlı):** Kurum erişimiyle Newcombe 1998b Tablo II'deki yöntem 10 sütunu ve 1998a (bağımsız, 11 yöntem) örnekleri bir kez karşılaştırılsın. Değerler `sentetik-testler/veri/yayimlanmis_ornekler.json`'a "birincil" etiketiyle eklenebilir; test otomatik koşar.

### N-4 — T3'ün kapsamı: COSE ve TK3
- **COSE:** §6.6 T3 "SD-JWT'ye özgü ve genel JOSE hedeflerinde" diyor.
  - **Uygulanan:** COSE hedefleri T3'ün dışında (`T3_TABAKALAR = ("SDJWT", "JOSE")`). JOSE ile birleştirilmez.
- **TK3:** ÖK §2B.7, TK3'ü yalnız T2'den çıkarıyor. T3'ün ölçütü (F_T = 1 ∧ F_K = 0) de tedavi koluna dayanıyor.
  - TK3 hedeflerinde (PQ imzayı doğrulayamayan) F_T = 1 neredeyse kesindir. Bu yüzden T3, katmanların TK bileşimini ölçmeye kayabilir. Aynı gerekçe TK3'ü T2'den çıkarmıştı.
  - **Uygulanan:** literal okuma, yani bütün TK sınıfları (`T3_TK_KAPSAMI = ("TK1", "TK2", "TK3")`).
- **Öneri:** Dondurmadan önce karar verilsin:
  - (a) literal okuma korunur ve tartışmada TK bileşimi raporlanır;
  - (b) T3 de TK1 + TK2 ile sınırlanır (tek satır değişiklik; testler yeniden koşulur).

  Önerim (b); gerekçe T2 ile tutarlılık. Karar ÖK v1.0'a yazılmalı.

### N-5 — T4'ün sınıflama değişkeni
- **ÖK durumu:** "8725bis-10'dan (21.08.2026) sonra sürüm çıkaran" ifadesinde üç şey açık:
  - (i) hangi tarihe kadar (ölçüm günü mü, çerçeve günü mü);
  - (ii) "sonra" kesin mi (22.08 ve sonrası);
  - (iii) resmî sürümü olmayan hedefler (yalnız commit ya da Go modülü etiketi).
- **Uygulanan:**
  - Girdi, Adım 10'un belirlediği `surum_8725bis_sonrasi` bayrağını taşır.
  - İsteğe bağlı `son_surum_tarihi` verilirse doğrulayıcı "sonra ⇔ tarih > 2026-08-21" kuralıyla tutarlılığı denetler.
  - Sürüm kavramı yoksa değer `null` (`uygulanamaz`) olur; hedef T4'ün dışında kalır.
- **Öneri:** ÖK v1.0'a şu yazılsın: "Paket kaydında ya da depo etiketlerinde, 22.08.2026 ile ölçüm için sürümün sabitlendiği gün arasında (ikisi dahil) yayımlanmış en az bir sürüm varsa 1; hiç sürüm yoksa uygulanamaz."

### N-6 — Holm ailesinde hesaplanamayan test
- **Durum:** Bir testin verisi olmayabilir. Örnekler: TK1/TK2 hedefi yok; SDJWT'de belirli F_K/F_T yok.
- **Uygulanan:**
  - p = 1 alınır (McNemar b + c = 0 ve Fisher sıfır marjinal zaten 1 verir); `veri_yok` bayrağı konur.
  - Aile boyutu m = 4 korunur (tutucu).
- **Öneri:** ÖK v1.0 §6.6'ya bu kural yazılsın.

### N-7 — Küme bootstrap'ın eksik belirtimi
- **ÖK durumu:** §6.9 yalnız "birim kütüphane, B = 10.000, yüzdelik GA, tohum 20260927" diyor.
- **Uygulanan belirtim** (ayrıntı `DONDURMA-GIRDISI.md` §3):
  - istatistik = havuzlanmış oran (Σ uymayan / Σ belirli vaka);
  - kümeler `hedef_id` sırasında; belirli vakası 0 olan küme dışlanır;
  - RNG `random.Random(20260927)`, `indeks = floor(random()·k)`;
  - yüzdelik tip 7;
  - kapsamlar: bütün vakalar, K kolu, T kolu; her biri aynı tohumla yeniden başlar.
- **Açık seçenek:** Kütüphane başına oranların ortalaması da savunulabilir bir tahmin edicidir; ağırlıkları farklıdır. Havuzlanmış oran "kütüphane içi vaka oranları" ifadesine ve kümelenmiş oran tahminine daha uygun.
- **Öneri:** Bu belirtim ÖK v1.0 §6.9'a (ya da dondurma paketine atıfla) yazılsın. Ayrıca hangi vaka oranlarının raporlanacağı (bütün / K / T) kesinleşsin.

### N-8 — İki uygulama toleransları ve "sınırda" kuralı
- **Uygulanan:**
  - A (kesin kesir ve Decimal) esastır; B (scipy/statsmodels) denetimdir.
  - p ve GA için mutlak 1e-10; OR için göreli 1e-8.
  - Bir karar farkı yalnız referans değeri eşiğe ≤ 1e-12 yakınsa "sınırda" sayılır ve raporlanır. Diğer her fark analizi geçersiz kılar (çıkış kodu 2).
- **Gözlem** (bilgi): z değerleri iki uygulamada son basamakta farklı. Python `statistics.NormalDist` 1,9599639845400536, scipy 1,959963984540054 veriyor (1 ulp). Etki ≤ 5,6e-16; testlerde görüldü.
- **Öneri:** Kural dondurma paketinin parçası olarak kabul edilsin (ÖK §6'ya kısa atıf).

### N-9 — Pilot duyarlılığı: ÖK ile envanter önerisi farklı
- **ÖK durumu:** §0.3 ve §6.10: "P3 pilotundaki 5 kütüphane **dışarıda bırakılarak** T1 tekrarlanır."
- **Envanter önerisi farklı:** `deney/envanter/OZET.md` §2.5, pilotlar zorla eklenmesin ve "n + pilotlar" duyarlılığı yapılsın diyor.
- **Uygulanan:** ÖK okuması (pilot = 1 olan n hedefleri çıkarılır).
- **Envantere göre n içindeki pilotlar:** yalnız `jose` ve `@sd-jwt/core`. `joserfc` yedekte; yedek devreye girerse n'ye girer. `jwcrypto` n dışında, Authlib dışlanmış. Yani duyarlılık en fazla 2–3 hedefi çıkarır.
- **Öneri:** ÖK okuması korunsun. "n + pilotlar" ölçülmüş olmayacağından (pilotlar n dışında ölçülmez) ya düşürülsün ya "keşifsel" etiketlensin.

### N-10 — Devir duyarlılığı: dışlama mı, tek birim mi?
- **ÖK durumu:** §2B.9 "devralan hedefler çıkarılarak" diyor.
- **Envanter önerisi farklı:** `OZET.md` R6, devir kümelerinin tek birim sayılmasını öneriyor.
- **Uygulanan:** ÖK okuması. T1 ve T2 devralanlar çıkarılarak yeniden hesaplanır; tanımlayıcı, Holm dışı. n içindeki tek doğrudan devir WalletFramework → IdentityModel.
- **Öneri:** Korunsun. İki okuma bu tek kümede aynı sonucu verir: devralan çıkınca küme tek birime iner.

### N-11 — ÖK içinde n = 30'dan kalan eski ifadeler
- **Eski ifadeler:** §2 (H6 satırı: "n=30'da ≥20/30") ve §3.7 ("n_eff = 30 için: c = 10, u = 20"). §2B bunların önüne geçiyor; betikler eşiği her zaman n_eff'ten Ek A kuralıyla hesaplar.
- **§6.6 gerekçe notu:** Hesap n = 30 için. n = 31'de T1 Holm'a girseydi eşik ≤ 8 / ≥ 23 olurdu. P(X ≤ 8) = 0,0053; P(X ≤ 9) = 0,0147.
- **§6.14 güç notu:** n = 30 için. n = 31 ve X ≤ 10 için:

  | Gerçek oran | Destek olasılığı |
  |---|---|
  | 0,2 | 0,9673 |
  | 0,3 | 0,6879 |
  | 0,4 | 0,2454 |

  X ≥ 21 için gerçek oran 0,7 ise yanlışlama olasılığı 0,6879.
- **Öneri:** ÖK v1.0'da bu üç yer n = 31'e göre güncellensin ya da "§2B ve Ek A geçerlidir" diye işaretlensin. ÖK'deki n = 30 değerlerinin kendisi doğru; `test_ek_a` onları yeniden üretir.

### N-12 — Etki yönleri ve §6.8'in kapsamı
- **Uygulanan yönler:**
  - T2 farkı P(F_T=1) − P(F_K=1); pozitifse PQ'ya özgü fazlalık vardır.
  - T3'te OR ve fark SDJWT'ye göre JOSE.
  - T4'te "sonra = 1"e göre "0".
- **§6.8 okuması:**
  - "Her L basamağı" = L = k oranı. L ≥ k oranları "tanımlayıcı ek" etiketiyle ayrıca verilir.
  - B1 ve B5 kategori başına raporlanır.
  - B4 = "özel kodla ifade edilebilir" oranı; satır sayısı medyan ve aralık olarak verilir.
  - B6 = "uygulanamaz" oranı.
- **Öneri:** Yönler ve bu okuma ÖK v1.0 §6.7–6.8'e yazılsın.

---

## B. Bilgi notları (karar gerektirmez)

1. **Kapsam dışı:** Ayrışma dedektörü ("aynı vakada farklı karar veren hedefler") ve MR1–MR4, oracle klasörünün işidir (Adım 9 görev 6/8). İstatistik betikleri bunları hesaplamaz.
2. **Hesaplanmayanlar:**
   - 3 tekrar kuralı (3/3) ve "kararsız" etiketi Adım 10'da üretilir. Betikler yalnız neden kodlarını sayar (kararsız hücre sayısı, ÖK §6.11).
   - F_K, F_T, D_soy ve L düzeyi girdidir; batarya vakalarından türetilmesi Adım 10'un işidir.
3. **`veri_turu` koruması:** `olcum` girdisinde çıktıya "yalnız dondurmadan sonra geçerli" uyarısı yazılır. Asıl koruma ÖK §10.7'dir: Adım 10 başında `sha256sum -c SHA256SUMS`.
4. **Sürümler:** numpy 2.4.6, scipy 1.17.1, statsmodels 0.15.0. Bunlar pip'in Python 3.11 için seçtiği en güncel uyumlu sürümlerdir.
   - İlgili işlevlerin davranışı tekerleklerin kaynağından okunarak ve testlerle doğrulandı: scipy `odds_ratio(kind="conditional")` brentq `xtol = 1e-13`; `fisher_exact` göreli tolerans 1e-14; statsmodels `newcomb` = Wilson kare-ve-topla; Wilson [0, 1]'e kırpılır; Holm reddi p ≤ α/k ile.
5. **Docker:**
   - İmaj `pq-a09-analiz:1.0` (`sha256:f7bc4aa3…`).
   - İlk inşadan kalan eski etiketsiz imaj kendiliğinden kalktı; artık `pq-a09-analiz-*` konteyneri yok.
   - **Build cache temizlenmedi:** `docker builder prune` bir prune komutu ve proje kuralı gereği yasak. Temizliğe yürütücü karar verir.
   - Başlangıç ve bitiş imaj listeleri `kayit/`'te. Başka hiçbir imaja ya da konteynere dokunulmadı.
6. **Süre:** Test takımı bir konteynerde 95–112 s sürüyor. Bunun çoğu kapsamlı iki uygulama süpürmeleri: 2×2 tabloların tamamı, N ≤ 20.
7. **Gizlilik:** Dış istekler yalnız şunlardı: OpenAlex (anonim, `mailto` yok), GitHub API ve raw (anonim, kimlik bilgisi yok), Wiley bağlantısı (403), CiteSeerX (Wayback 429), Scholar Gateway (yalnız özet) ve PyPI (paket indirme). Hiçbirinde e-posta ya da kişisel veri yoktu. Git kullanılmadı.
