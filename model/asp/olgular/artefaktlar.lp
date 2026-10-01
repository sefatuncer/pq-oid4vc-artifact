% =====================================================================
%  PQ-OID4VC | Adım 3 | ASP sistem modeli — ARTEFAKTLAR (yalnız zemin olgular)
%  Ön kayıt §2C (Değişiklik 3, D1′) ile uyumlu: 17 KARAR DÜĞÜMÜ.
% =====================================================================
%  Sözleşme (Tamarin R1–R5 ve pilot P2 ile aynı):
%    pq(A)  <=>  A'yı İMZALAYAN anahtar PQ'dur (ya da composite; S2 kıramaz).
%    İmzasız artefaktlarda (A06, E_JVI, E_AS) pq(A) = "nesne düzeyinde PQ bağlama" (özet ya da PQ
%    imzalı gösterim); bağlıysa sahteliği pq_baglar/2 ile bağlandığı artefaktınkine indirgenir.
%  KARAR DÜĞÜMLERİ (§2C 2.1): a01 a02 a03 a04 a05 a06 a07 a08 a09a a09b a10 a11 a12 a13 ecrl ejvi eas.
%    dugum(A,D): A artefaktının göçü D düğümünün kararıdır (aynı düğümdeki artefaktlar birlikte göç eder).
%    Modelde bazı sınıflar birden çok örnekle temsil edilir (ör. A02 = ulusal TL + 4 EUDI LoTE); karar
%    ve M2 düğüm düzeyindedir.
%  Olgu biçimleri (hepsi zemin; koşullar parametre olgusu p(Ad,Deger) ile):
%    artefakt(A). sinif(A,S). imzali(A) | imzasiz(A). karar(A). dugum(A,D).
%    karar_kosullu(A,P,V)        A ancak p(P,V) iken karar değişkenidir
%    var_kosul(A,P,V)            A ancak p(P,V) iken vardır (birden çoksa hepsi)
%    sabit(A) | sabit_kosullu(A,P,V)   A'nın imzalayan anahtarı bant dışı sabitli (R5)
%    kanal(A,K) | kanal_kosullu(A,K,P,V)
%        K ∈ {aktarilan, cekilen, sabitlenmis, sunan_uc, yalniz_tasima, kimliksiz}
%    tasima(A,T) | tasima_kosullu(A,T,P,V)     çekilen/yalnız-taşıma artefaktın taşıması
%    tasima_anahtari(T,A)        T taşımasının sunucu kimlik doğrulamasını A temsil eder
%    pencere_sabit(A,Ad)         imzalayan anahtarın güven penceresi: Ad bir sayısal parametre
%                                (w_kok, w_ca, w_ihracci, w_rp, w_tls, w_wia, w_ka) ya da sure/2 adı
%    pq_kosullu(A,P,V)           karar dışı artefakt, p(P,V) iken PQ
%    pq_yasak(A,P,V)             p(P,V) iken A PQ olamaz (ör. WebPKI klasikken A13)
%    ayni_anahtar(A,B)           A ile B aynı anahtarla imzalanır (pq(A) <=> pq(B))
%    pq_baglar(A,B)              imzasız A PQ-bağlıysa sahteliği B'ninkine eşittir
%    klasik_alt_zorla(A,P,V)     p(P,V) iken fazdan bağımsız klasik alternatif açık
%    ozgun_kosullu(A,P,V)        p(P,V) iken A'nın içeriği özgündür (sahtelenemez)
%    onbellekli(A)               çıpa kipi 'onbellek' + ilk pencere ufkunda özgün kopya
%    varyant(A,Av) + varyant_kosul(A,Av,P,V)  A'nın kabul edilen imzasız/zayıf biçimi
%    wscd_artefakt(A)            A'nın PQ olması WSCD donanım değişimi gerektirir (M5)
%    m2_agirlik(D,W)             M2 ağırlığı (A02: 107 TL imzacı sertifikası; 43 işaretçi)
%  Txxx = 02-izlenebilirlik/izlenebilirlik.csv satırı; [K-Ç] = çalışma çıkarımı.
% =====================================================================

karar_dugumu(a01). karar_dugumu(a02). karar_dugumu(a03). karar_dugumu(a04). karar_dugumu(a05).
karar_dugumu(a06). karar_dugumu(a07). karar_dugumu(a08). karar_dugumu(a09a). karar_dugumu(a09b).
karar_dugumu(a10). karar_dugumu(a11). karar_dugumu(a12). karar_dugumu(a13).
karar_dugumu(ecrl). karar_dugumu(ejvi). karar_dugumu(eas).
m2_agirlik(a02,107). m2_isaretci(a02,43).         % veri/eu-lotl_seq394.xml (P5 pilotu; betikle yeniden sayılır)

% ---------------------------------------------------------------- A00
% OJEU yayını: LOTL imzacısı, LoTE çapaları ve LOTL indirme kanalı sertifikası özetleri.
% Bant dışı, özgün kaynak (sabitlenmiş). Beklenti taşıyıcısı olabilir (M-f, LOTL/LoTE için).
artefakt(a00_ojeu). sinif(a00_ojeu,a00). imzasiz(a00_ojeu). kanal(a00_ojeu,sabitlenmis).   % T001,T002,T029

% ---------------------------------------------------------------- A01 LOTL
artefakt(a01_lotl). sinif(a01_lotl,a01). imzali(a01_lotl). karar(a01_lotl). dugum(a01_lotl,a01).
sabit(a01_lotl).                                   % imzacı sertifikası OJEU özetiyle doğrulanır (T001, T004, T005)
kanal(a01_lotl,cekilen).                           % çekilir (T001-T003)
tasima_kosullu(a01_lotl,lotl_kanal,lotl_indirme,ojeu_sabit).   % kanal sertifikası OJEU'da (T002)
tasima_kosullu(a01_lotl,webpki,lotl_indirme,webpki).
pencere_sabit(a01_lotl,w_kok).                     % §2C: LOTL/TL imzacısı 5 yıl (duyarlılık 1 yıl)
onbellekli(a01_lotl).

% ---------------------------------------------------------------- A02 TL/LoTE (tek düğüm; 5 örnek)
% Ulusal TL (XAdES-B-B, tek ds:Signature; T013, T016). İmzacıları LOTL işaretçisinde (T008);
% birden çok geçerli imzacı sertifikası = OR (T018). 43 işaretçi / 107 imzacı sertifikası.
artefakt(a02_tl). sinif(a02_tl,a02). imzali(a02_tl). karar(a02_tl). dugum(a02_tl,a02).
sabit_kosullu(a02_tl,capa,sabit).                  % çıpa kipi 'sabit': TL imza anahtarı bant dışı (R5)
kanal(a02_tl,cekilen). tasima(a02_tl,webpki).      % T008-T012, T027, T028
pencere_sabit(a02_tl,w_kok).
onbellekli(a02_tl).
% EUDI LoTE'leri (compact JAdES-B, tek imza; T023-T025). İmza çapaları OJEU'da (TLPub_07, T029) => sabit.
artefakt(a02_lote_pid).     sinif(a02_lote_pid,a02).     imzali(a02_lote_pid).     karar(a02_lote_pid).     dugum(a02_lote_pid,a02).
artefakt(a02_lote_cuzdan).  sinif(a02_lote_cuzdan,a02).  imzali(a02_lote_cuzdan).  karar(a02_lote_cuzdan).  dugum(a02_lote_cuzdan,a02).
artefakt(a02_lote_erisim).  sinif(a02_lote_erisim,a02).  imzali(a02_lote_erisim).  karar(a02_lote_erisim).  dugum(a02_lote_erisim,a02).
artefakt(a02_lote_kayit).   sinif(a02_lote_kayit,a02).   imzali(a02_lote_kayit).   karar(a02_lote_kayit).   dugum(a02_lote_kayit,a02).
sabit(a02_lote_pid). sabit(a02_lote_cuzdan). sabit(a02_lote_erisim). sabit(a02_lote_kayit).     % T029
kanal(a02_lote_pid,cekilen).    tasima(a02_lote_pid,webpki).
kanal(a02_lote_cuzdan,cekilen). tasima(a02_lote_cuzdan,webpki).
kanal(a02_lote_erisim,cekilen). tasima(a02_lote_erisim,webpki).
kanal(a02_lote_kayit,cekilen).  tasima(a02_lote_kayit,webpki).
pencere_sabit(a02_lote_pid,w_kok). pencere_sabit(a02_lote_cuzdan,w_kok).
pencere_sabit(a02_lote_erisim,w_kok). pencere_sabit(a02_lote_kayit,w_kok).
onbellekli(a02_lote_pid). onbellekli(a02_lote_cuzdan). onbellekli(a02_lote_erisim). onbellekli(a02_lote_kayit).

% ---------------------------------------------------------------- A03 CA (x5c ara sertifikası)
% İmzalayan: sağlayıcının güven çapası (kök CA) anahtarı; çapa TL/LoTE'de listelenir (T063),
% x5c'de yasak (T043). Aktarılan (T038). Dış kaynak durum CA'sı (a08_ca) da A03 sınıfındadır.
artefakt(a03_ca). sinif(a03_ca,a03). imzali(a03_ca). karar(a03_ca). dugum(a03_ca,a03).
kanal(a03_ca,aktarilan). pencere_sabit(a03_ca,w_ca).        % §2C: CA 5 yıl (TS 119 312 §9.4, T069)

% ---------------------------------------------------------------- A04 İhraççı (belge imzacı) sertifikası
% İmzalayan: CA anahtarı. Aktarılan (x5c yaprak; T039, T042). Anahtar sınıfı semantiğinde a04,
% "aynı CA'nın düzenlediği uç-varlık sertifikası" sınıfını temsil eder (durum/meta veri imzacı
% sertifikaları dahil; T160, T161, T084).
artefakt(a04_ihr). sinif(a04_ihr,a04). imzali(a04_ihr). karar(a04_ihr). dugum(a04_ihr,a04).
kanal(a04_ihr,aktarilan). pencere_sabit(a04_ihr,w_ca).

% ---------------------------------------------------------------- A05 İhraççı meta verisi
% İmzalı biçim: meta veri anahtarı (x5c ile; T084). Çekilen, TLS zorunlu (T070). İmzasız biçim
% varsayılan ve cüzdanlarca desteklenir (T071, T086) => yalnız-taşıma varyantı.
artefakt(a05_meta). sinif(a05_meta,a05). imzali(a05_meta). karar(a05_meta). dugum(a05_meta,a05).
kanal(a05_meta,cekilen). tasima(a05_meta,webpki). pencere_sabit(a05_meta,w_ihracci).
artefakt(a05_meta_imzasiz). sinif(a05_meta_imzasiz,a05). imzasiz(a05_meta_imzasiz).
kanal(a05_meta_imzasiz,yalniz_tasima). tasima(a05_meta_imzasiz,webpki).
varyant(a05_meta,a05_meta_imzasiz). varyant_kosul(a05_meta,a05_meta_imzasiz,imzasiz_meta_kabul,var).

% ---------------------------------------------------------------- A06 Type Metadata (karar düğümü)
% İmzasız. pq(a06_tip) = vct#integrity özetiyle kimlik bilgisine bağlı (T090, T093); bağlı değilse
% tek koruma HTTPS (T095, T100). Birlikte yaşamada özetsiz tür verisinin kabulü klasik alternatiftir.
artefakt(a06_tip). sinif(a06_tip,a06). imzasiz(a06_tip). karar(a06_tip). dugum(a06_tip,a06).
kanal(a06_tip,yalniz_tasima). tasima(a06_tip,webpki). pq_baglar(a06_tip,a07_kimlik).

% ---------------------------------------------------------------- A07 Kimlik bilgisi (SD-JWT VC)
% İmzalayan: ihraççı imza anahtarı; pencere anahtar kipine bağlı (pencereler.lp; §2C: V1 = 1 yıl). Aktarılan.
% V2 (dönem) ve V3 (kimlik bilgisi başına) kiplerinde imza anahtarı, CA'nın düzenlediği kısa ömürlü
% sertifikayla (a04 sınıfı) bağlanır: uzun ömürlü KİMLİK = CA zinciri (Tamarin R6 ID_PQ karşılığı).
% pq(a07) = kimlik bilgisini imzalayan anahtar(lar) PQ; klasikse pencere kipten gelir.
artefakt(a07_kimlik). sinif(a07_kimlik,a07). imzali(a07_kimlik). karar(a07_kimlik). dugum(a07_kimlik,a07).
kanal(a07_kimlik,aktarilan).

% ---------------------------------------------------------------- A08 Durum listesi belirteci
% İmzalayan: durum imza anahtarı (V1 uzun ömürlü | V2 dönem (günlük rotasyon) | V3 belirteç başına).
% Anahtarı bağlayan uzun ömürlü KİMLİK: aynı CA (ayni_ca; T160, T161) ya da dış kaynak durum CA'sı
% (farkli_capa; T180) — Tamarin R6'daki ID_PQ'nun karşılığı CA zincirinin PQ olmasıdır.
% Çekilen (T145-T165); çevrimdışı aktarılabilir (T166). Tasarımı taşımaya dayanmaz (T157).
% Durum listesi 'yok' ise (≤24 sa kısa ömürlü seçenek, T175) iptal süre dolumuyla sağlanır.
artefakt(a08_durum). sinif(a08_durum,a08). imzali(a08_durum). karar(a08_durum). dugum(a08_durum,a08).
var_kosul(a08_durum,durum_listesi,var).
kanal_kosullu(a08_durum,cekilen,durum_kanali,cekilen).
kanal_kosullu(a08_durum,aktarilan,durum_kanali,aktarilan).
tasima(a08_durum,webpki).
% farklı çapalı durum CA'sı (dış kaynak durum ihraççısı; T180, T026) — CA sınıfı (A03)
artefakt(a08_ca). sinif(a08_ca,a03). imzali(a08_ca). karar(a08_ca). dugum(a08_ca,a03).
var_kosul(a08_ca,durum_listesi,var).
kanal(a08_ca,aktarilan). pencere_sabit(a08_ca,w_ca).

% ---------------------------------------------------------------- A09a WIA, A09b KA (§2C: iki düğüm)
% A09b düğümü = cüzdan sağlayıcı imza anahtarı: KA'yı ve WIA'yı imzalar (§2C W_güven KA = 1 yıl).
% A09a düğümü = WIA'nın bağladığı cüzdan örneği anahtarı (istemci kanıtlaması PoP'u; T187);
%   güveni WIA'nın < 24 sa geçerliliğiyle sınırlı (§2C W_güven WIA = 1 gün; T204).
% İkisi de yalnız ihraççıya sunulur (T399, T400) => sunum hedeflerinin (G1–G4) yolunda değil.
artefakt(a09a_wia). sinif(a09a_wia,a09). imzali(a09a_wia). karar(a09a_wia). dugum(a09a_wia,a09b).
kanal(a09a_wia,aktarilan). pencere_sabit(a09a_wia,w_ka).
artefakt(a09b_ka). sinif(a09b_ka,a09). imzali(a09b_ka). karar(a09b_ka). dugum(a09b_ka,a09b).
kanal(a09b_ka,aktarilan). pencere_sabit(a09b_ka,w_ka).
artefakt(a09c_ornek). sinif(a09c_ornek,a09). imzali(a09c_ornek). karar(a09c_ornek). dugum(a09c_ornek,a09a).
kanal(a09c_ornek,aktarilan).

% ---------------------------------------------------------------- A10 KB-JWT (WSCD cihaz anahtarı)
% İmzalayan: cihaz anahtarı; cnf ile kimlik bilgisine bağlı (T218, T220). Pencere: cihaz anahtar
% kipi ve kimlik bilgisi geçerliliği (§2C: 30 gün; ön kayıt §4.5 "Cihaz anahtarı").
artefakt(a10_kbjwt). sinif(a10_kbjwt,a10). imzali(a10_kbjwt). karar(a10_kbjwt). dugum(a10_kbjwt,a10).
kanal(a10_kbjwt,aktarilan).
wscd_artefakt(a10_kbjwt).                          % PQ olması WSCD donanım değişimi gerektirir (M5)

% ---------------------------------------------------------------- A11 RP erişim (WRPAC) / kayıt (WRPRC)
% İmzalayanlar: Access CA ve WRPRC sağlayıcısı (CA sınıfı anahtarlar, 5 yıl). A11 tek düğüm.
artefakt(a11_erisim). sinif(a11_erisim,a11). imzali(a11_erisim). karar(a11_erisim). dugum(a11_erisim,a11).
kanal(a11_erisim,aktarilan). pencere_sabit(a11_erisim,w_ca).    % değerle (T252)
artefakt(a11_kayit). sinif(a11_kayit,a11). imzali(a11_kayit). karar(a11_kayit). dugum(a11_kayit,a11).
kanal(a11_kayit,aktarilan). pencere_sabit(a11_kayit,w_ca).      % JAdES B-B, x5c (T257, T259)

% ---------------------------------------------------------------- A12 OID4VP istek nesnesi
% İmzalayan: RP anahtarı; güveni WRPAC geçerliliğiyle sınırlı (§2C W_güven RP erişim sertifikası 1 yıl;
% kısa ömürlü değil, T261). DC API: değerle (aktarılan). Yönlendirmeli akış: RP'nin kendi
% request_uri'sinden çekilir (T284) => 'sunan_uc' (H1 anlamında çekilen değil).
artefakt(a12_istek). sinif(a12_istek,a12). imzali(a12_istek). karar(a12_istek). dugum(a12_istek,a12).
kanal_kosullu(a12_istek,aktarilan,istek_iletimi,dc_api).
kanal_kosullu(a12_istek,sunan_uc,istek_iletimi,request_uri).
pencere_sabit(a12_istek,w_rp).
% İmzasız istek: cüzdan desteklemek zorunda (T281); origin + WebPKI'ye dayanır (T282, T227, T280).
artefakt(a12_istek_imzasiz). sinif(a12_istek_imzasiz,a12). imzasiz(a12_istek_imzasiz).
kanal(a12_istek_imzasiz,yalniz_tasima). tasima(a12_istek_imzasiz,webpki).
varyant(a12_istek,a12_istek_imzasiz). varyant_kosul(a12_istek,a12_istek_imzasiz,imzasiz_istek_kabul,var).

% ---------------------------------------------------------------- A13 Taşıma (karar düğümü)
% pq(A13) = çekilen artefaktların TLS sunucu kimlik doğrulaması PQ ve klasik zincir reddediliyor.
% WebPKI klasikken (§2C birincil) PQ seçilemez; 'pq' iken seçilebilir bir göç kararıdır;
% 'pq_birlikte' (PQ sertifika var ama klasik de kabul) any-valid-path ile klasikle eşdeğerdir.
% LOTL indirme kanalı sertifikası (OJEU'da sabit, T002) aynı düğümdedir.
artefakt(a13_webpki). sinif(a13_webpki,a13). imzali(a13_webpki). karar(a13_webpki). dugum(a13_webpki,a13).
sabit(a13_webpki). kanal(a13_webpki,aktarilan). pencere_sabit(a13_webpki,w_tls).   % §2C: 1 yıl (duyarlılık 47 gün)
pq_yasak(a13_webpki,webpki,cl).
klasik_alt_zorla(a13_webpki,webpki,pq_birlikte).
tasima_anahtari(webpki,a13_webpki).
artefakt(a13_lotl_kanal). sinif(a13_lotl_kanal,a13). imzali(a13_lotl_kanal). karar(a13_lotl_kanal). dugum(a13_lotl_kanal,a13).
sabit(a13_lotl_kanal). kanal(a13_lotl_kanal,aktarilan). pencere_sabit(a13_lotl_kanal,w_tls).
pq_yasak(a13_lotl_kanal,webpki,cl).
klasik_alt_zorla(a13_lotl_kanal,webpki,pq_birlikte).
tasima_anahtari(lotl_kanal,a13_lotl_kanal).

% ---------------------------------------------------------------- Kenar-artefaktlar (3 karar düğümü)
% Access CA CRL/OCSP (T255; çevrimdışı önbellek T256). CRL/OCSP imza anahtarı (CA sınıfı).
artefakt(e_crl). sinif(e_crl,e_crl). imzali(e_crl). karar(e_crl). dugum(e_crl,ecrl).
kanal(e_crl,cekilen). tasima(e_crl,webpki). pencere_sabit(e_crl,w_ca). onbellekli(e_crl).
% JWT VC Issuer Metadata / JWK Set: ihraççı anahtarı yalnız HTTPS ile (T309-T311).
% pq(e_jvi) = JWKS'nin CA zincirine PQ imzayla bağlanması (bağlıysa bağımsız yol değildir).
artefakt(e_jvi). sinif(e_jvi,e_jvi). imzasiz(e_jvi). karar(e_jvi). dugum(e_jvi,ejvi).
kanal(e_jvi,yalniz_tasima). tasima(e_jvi,webpki). pq_baglar(e_jvi,a04_ihr).
% İhraççının OAuth AS meta verisi: yalnız yetenek ("supported") (T188, T381) => M-a sınıfı; beklenti taşımaz.
artefakt(e_asmeta). sinif(e_asmeta,e_asmeta). imzasiz(e_asmeta). karar(e_asmeta). dugum(e_asmeta,eas).
kanal(e_asmeta,yalniz_tasima). tasima(e_asmeta,webpki). pq_baglar(e_asmeta,a05_meta).

% ---------------------------------------------------------------- Senaryo artefaktları (adlandırılmış hücreler)
% (1) Aynı çıpa altında geçerli ALTERNATİF klasik CA (Tamarin R1/R7h ALT_CA). Ad ilişkisi ayrı bayraktır:
%     ayni_ad_klasik_ca = var: alternatif CA meşru CA ile AYNI ADI taşır (CA anahtar değişimi: göç öncesi
%     klasik sertifika; Tamarin R7hx ALT_SAME_NAME); yok: farklı adlı (başka sağlayıcının) CA'sı.
%     Kabul (kenarlar.lp): ca_baglama = yok -> her zaman; ad -> yalnız aynı adlıysa; anahtar -> hiçbir zaman.
%     'diger_ca_rejimi': klasik_sabit (strateji dışı / süresi dolana kadar geçerli) | karar (A03/A04 ile göç eder).
artefakt(a03_diger). sinif(a03_diger,a03). imzali(a03_diger). var_kosul(a03_diger,diger_ca,var).
karar_kosullu(a03_diger,diger_ca_rejimi,karar). dugum(a03_diger,a03).
kanal(a03_diger,aktarilan). pencere_sabit(a03_diger,w_ca).
artefakt(a04_diger). sinif(a04_diger,a04). imzali(a04_diger). var_kosul(a04_diger,diger_ca,var).
karar_kosullu(a04_diger,diger_ca_rejimi,karar). dugum(a04_diger,a04).
kanal(a04_diger,aktarilan). pencere_sabit(a04_diger,w_ca).
% (2) Aynı LoTE'de başka bir klasik Access CA (RP adı için; G4).
artefakt(a11_erisim_diger). sinif(a11_erisim_diger,a11). imzali(a11_erisim_diger). var_kosul(a11_erisim_diger,diger_ca,var).
karar_kosullu(a11_erisim_diger,diger_ca_rejimi,karar). dugum(a11_erisim_diger,a11).
kanal(a11_erisim_diger,aktarilan). pencere_sabit(a11_erisim_diger,w_ca).
% (3) A.3.2.2 çoklu imzalı istek: cüzdanın ayrıca güvendiği ikinci güven çerçevesi F2 (T269, T270, T273).
artefakt(a00_f2_capa). sinif(a00_f2_capa,a00). imzasiz(a00_f2_capa). kanal(a00_f2_capa,sabitlenmis).
artefakt(a11_erisim_f2). sinif(a11_erisim_f2,a11). imzali(a11_erisim_f2). var_kosul(a11_erisim_f2,coklu_cerceve,var).
pq_kosullu(a11_erisim_f2,f2_rejimi,pq).
kanal(a11_erisim_f2,aktarilan). pencere_sabit(a11_erisim_f2,w_ca).

% ---------------------------------------------------------------- Mekanizma kanca artefaktları (Adım 7)
% M-d: bant dışı statik yapılandırma (DCR, CIMD; HAIP §7 T123). Özgün (sabitlenmiş).
artefakt(m_d_cfg). sinif(m_d_cfg,mekanizma). imzasiz(m_d_cfg). kanal(m_d_cfg,sabitlenmis).
var_kosul(m_d_cfg,md_kanca,acik).
% M-g: öz-beyanlı süreklilik / TOFU (sheffer-tls-pqc-continuity). İlk temas Q-day'den önceyse özgün.
artefakt(m_g_oz). sinif(m_g_oz,mekanizma). imzasiz(m_g_oz). kanal(m_g_oz,aktarilan).
var_kosul(m_g_oz,mekanizma_kancalari,acik).
ozgun_kosullu(m_g_oz,ilk_temas,qday_oncesi).
% Kimliksiz alan (M-a sınıfı; R2 EXPECT_UNAUTH karşılığı): S1 bile değiştirir.
artefakt(m_a_alan). sinif(m_a_alan,mekanizma). imzasiz(m_a_alan). kanal(m_a_alan,kimliksiz).
var_kosul(m_a_alan,ma_kanca,acik).

% ---------------------------------------------------------------- Pencere sabitleri (saniye; sure/2)
sure(uzun,157680000).   % 5 yıl: kalıcı cihaz/örnek anahtarı ve P3 kanalı
sure(gun,86400).
