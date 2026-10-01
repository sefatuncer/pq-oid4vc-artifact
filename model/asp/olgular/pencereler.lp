% =====================================================================
%  PQ-OID4VC | Adım 3 | PENCERELER ve ANAHTAR KİPLERİ (saniye) — §2C 2.3 birincil değerleri
% =====================================================================
%  Ön kayıt §4.5 + §2A Ö1 (H2′) + Ö8 + §2C 2.3 + Tamarin R6 (Adım 5A):
%   exposure(K)    = maruziyet(A,E): A'yı imzalayan anahtarın açık anahtarının gözlenebildiği ilk an
%                    (en kötü durum: pencerenin başı, E = 0);
%   last_accept(K) = son_kabul(A,L): o anahtarla atılmış bir imzanın SON kabul edilebileceği an;
%   W_güven(K)     = pencere(A, L - E).
%   S2, klasik K ile imzalanan artefaktı ancak  τ < W_güven(K) + saat_payi  ise sahteleyebilir
%   (CRQC-TAKVIMI §1: max(T0,qday)+τ ≤ T1; ön kayıt §4.5 katı eşitsizlik; saat payı T392).
%   BELİRTECİN (artefaktın) geçerliliği tek başına belirleyici DEĞİLDİR (Ö1): belirteç ömrü ancak anahtar
%   kipi onu anahtara bağladığında (dönem/belirteç sınıfı) son_kabul'e girer.
%  Pencere sınıfları (Tamarin R6 ile eşleme; pencere_sinifi/2):
%   uzun_omurlu  <-> R6 LONG      : anahtar sertifika ömrü boyunca kullanılır (V1; ya da KEY_REUSE)
%   donem        <-> R6 ROTATED   : dönem başına taze anahtar (V2 günlük rotasyon; WIA başına örnek anahtarı)
%   belirtec     <-> R6 PER_TOKEN : belirteç/kimlik bilgisi başına taze anahtar (V3; kimlik bilgisi başına cnf)
%   R6'nın sembolik rejimleri SAYISAL olarak şöyle okunur: FAST: τ ≤ belirteç penceresi; MEDIUM: belirteç
%   penceresi < τ ≤ dönem penceresi; SLOW: τ > dönem penceresi (uzun ömürlü pencerenin altında).
%   ID_PQ <-> anahtarı bağlayan CA zinciri PQ (kenarlar.lp); KEY_REUSE <-> anahtar_yeniden_kullanim = var.
%  Sabit adlı pencereler (pencere_sabit/2) sayısal parametrelere bağlanır (sürücü p_sayi ile verir):
%   w_kok (LOTL/TL/LoTE imzacısı, 5 y), w_ca (CA, 5 y), w_ihracci (x5c yaprağı, 1 y), w_rp (RP anahtarı,
%   WRPAC ile, 1 y), w_tls (TLS sunucu, 1 y), w_wia (WIA'nın bağladığı örnek anahtarı, 1 g), w_ka (cüzdan
%   sağlayıcı / KA, 1 y). Regresyon örnekleri sure/2 adlarını da kullanabilir (sonsuz, uzun).
%  Kipler (V1/V2/V3; Ö1 değişkeleri; Anchuri vd. "transient"):
%   ihracci_anahtari ∈ {uzun, gunluk, gecici}  (V1: w_ihracci; V2: 1 g + kimlik bilgisi geçerliliği; V3: geçerlilik)
%   durum_anahtari   ∈ {uzun, gunluk, gecici}  (V1: w_ihracci; V2: 1 g + durum TTL; V3: durum TTL)
%   cihaz_anahtari   ∈ {kalici, kimlik_basi}   (kalıcı: 5 y; kimlik bilgisi başına: kimlik_gecerlilik = 30 g)
%   wia_anahtari     ∈ {wia_basi, kalici}       (WIA başına: w_wia = 1 g; kalıcı: 5 y)
%  V2'de anahtarın sertifikası imzaladığı son belirtecin kabulünü de kapsamalıdır (kabuk modeli, RFC 5280 §6.1).
%  V2/V3 anahtarları CA'nın düzenlediği kısa ömürlü sertifikayla bağlanır (kimlik = CA zinciri).
% =====================================================================

pencere_parametrik(a07_kimlik). pencere_parametrik(a08_durum).
pencere_parametrik(a10_kbjwt).  pencere_parametrik(a09c_ornek).

uzun_s(W) :- sure(uzun,W).
kimlik_gecerlilik_s(W) :- p_sayi(kimlik_gecerlilik,W).
durum_ttl_s(W) :- p_sayi(durum_ttl,W).
kbjwt_iat_s(W) :- p_sayi(kbjwt_iat,W).
w_ihracci_s(W) :- p_sayi(w_ihracci,W).
yeniden_kullanim :- p(anahtar_yeniden_kullanim,var).

% --- maruziyet (exposure): en kötü durumda açık anahtar pencerenin başında gözlenir
maruziyet(A,0) :- imzali(A), mevcut(A).

% --- son kabul (last_accept) ve pencere sınıfı
% Sabit adlı pencereler (sayısal parametre ya da sure/2 adı): uzun ömürlü
son_kabul(A,L) :- pencere_sabit(A,Ad), p_sayi(Ad,L), mevcut(A), not pencere_parametrik(A).
son_kabul(A,L) :- pencere_sabit(A,Ad), sure(Ad,L), mevcut(A), not pencere_parametrik(A).
pencere_sinifi(A,uzun_omurlu) :- pencere_sabit(A,_), mevcut(A), not pencere_parametrik(A).

% İhraççı imza anahtarı (A07)
kip_sinifi(uzun,uzun_omurlu). kip_sinifi(gunluk,donem). kip_sinifi(gecici,belirtec).
son_kabul(a07_kimlik,L) :- mevcut(a07_kimlik), p(ihracci_anahtari,uzun), w_ihracci_s(L).
son_kabul(a07_kimlik,L) :- mevcut(a07_kimlik), p(ihracci_anahtari,gunluk), kimlik_gecerlilik_s(K), L = 86400 + K, not yeniden_kullanim.
son_kabul(a07_kimlik,K) :- mevcut(a07_kimlik), p(ihracci_anahtari,gecici), kimlik_gecerlilik_s(K), not yeniden_kullanim.
son_kabul(a07_kimlik,L) :- mevcut(a07_kimlik), not p(ihracci_anahtari,uzun), yeniden_kullanim, w_ihracci_s(L).
pencere_sinifi(a07_kimlik,S) :- mevcut(a07_kimlik), p(ihracci_anahtari,K), kip_sinifi(K,S), not yeniden_kullanim.
pencere_sinifi(a07_kimlik,uzun_omurlu) :- mevcut(a07_kimlik), yeniden_kullanim.

% Durum listesi imza anahtarı (A08; H2′ tasarım faktörü)
son_kabul(a08_durum,L) :- mevcut(a08_durum), p(durum_anahtari,uzun), w_ihracci_s(L).
son_kabul(a08_durum,L) :- mevcut(a08_durum), p(durum_anahtari,gunluk), durum_ttl_s(T), L = 86400 + T, not yeniden_kullanim.
son_kabul(a08_durum,T) :- mevcut(a08_durum), p(durum_anahtari,gecici), durum_ttl_s(T), not yeniden_kullanim.
son_kabul(a08_durum,L) :- mevcut(a08_durum), not p(durum_anahtari,uzun), yeniden_kullanim, w_ihracci_s(L).
pencere_sinifi(a08_durum,S) :- mevcut(a08_durum), p(durum_anahtari,K), kip_sinifi(K,S), not yeniden_kullanim.
pencere_sinifi(a08_durum,uzun_omurlu) :- mevcut(a08_durum), yeniden_kullanim.

% Cihaz (cnf) anahtarı (A10): W_güven(K_cnf) = bağlayan kimlik bilgisinin kalan geçerliliği (ön kayıt §4.5).
% Tek kullanım (cüzdanda ya da doğrulayıcıda; saldırgan dürüst sunumu düşürebilir) pencereyi DEĞİŞTİRMEZ (H5;
% Tamarin R6h5 M_single_fast = F). Yalnız 'kuresel_pasif' sınır varyantı: pasif toplayan saldırgan + küresel
% tek kullanım => yarış penceresi = iat penceresi. Kalıcı cihaz anahtarı = R6h5 KEY_REUSE.
son_kabul(a10_kbjwt,L) :- mevcut(a10_kbjwt), p(cihaz_anahtari,kalici), uzun_s(L).
son_kabul(a10_kbjwt,K) :- mevcut(a10_kbjwt), p(cihaz_anahtari,kimlik_basi), kimlik_gecerlilik_s(K), not p(tek_kullanim,kuresel_pasif).
son_kabul(a10_kbjwt,I) :- mevcut(a10_kbjwt), p(cihaz_anahtari,kimlik_basi), p(tek_kullanim,kuresel_pasif), kbjwt_iat_s(I).
pencere_sinifi(a10_kbjwt,uzun_omurlu) :- mevcut(a10_kbjwt), p(cihaz_anahtari,kalici).
pencere_sinifi(a10_kbjwt,belirtec)    :- mevcut(a10_kbjwt), p(cihaz_anahtari,kimlik_basi).

% WIA'nın bağladığı örnek anahtarı (A09a): WIA < 24 sa (T204) yalnız anahtar WIA başına yenilenirse pencere olur.
son_kabul(a09c_ornek,L) :- mevcut(a09c_ornek), p(wia_anahtari,wia_basi), p_sayi(w_wia,L).
son_kabul(a09c_ornek,L) :- mevcut(a09c_ornek), p(wia_anahtari,kalici), uzun_s(L).
pencere_sinifi(a09c_ornek,donem)       :- mevcut(a09c_ornek), p(wia_anahtari,wia_basi).
pencere_sinifi(a09c_ornek,uzun_omurlu) :- mevcut(a09c_ornek), p(wia_anahtari,kalici).

% --- W_güven
pencere(A,W) :- son_kabul(A,L), maruziyet(A,E), W = L - E.

% P3 politikasının klasik yapılandırma kanalı (sanal anahtar; at-rest)
pencere_p3(W) :- uzun_s(W).
