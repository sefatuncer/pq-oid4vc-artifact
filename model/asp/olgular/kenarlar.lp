% =====================================================================
%  PQ-OID4VC | Adım 3 | KENARLAR (anahtar tanıtımı; any-valid-path)
% =====================================================================
%  kenar(E,A,B): A'yı imzalayan anahtar B-sınıfı bir artefaktla TANITILIR (sertifikalanır /
%  listelenir / cnf ile bağlanır). Doğrulayıcının KABUL ettiği her tanıtıcı ayrı bir kenardır
%  (OR): A, kabul edilen herhangi bir tanıtıcısı sahtelenebiliyorsa sahtelenebilir
%  (RFC 5280 §6.2 "A system may provide any one of its trusted CAs as the trust anchor for a
%  particular path" [RFC5280, korpus ek]; RFC 6840 §5.11 "any single valid path" T364;
%  S/MIME "every valid path" KAT-3; Tamarin R1 X_alt_ca: anahtar sınıfı semantiği).
%  kenar_kosul(E,P,V): kenar ancak p(P,V) iken etkin (birden çoksa hepsi).
%  kenar_kosul_degil(E,P,V): kenar p(P,V) iken etkin DEĞİL.
%  Ok yönü: guven-bagimliligi.dot'taki "X -> Y" (X, Y'nin doğrulanmasında kullanılır)
%  burada kenar(_,Y,X) olarak yazılır.
% =====================================================================

% --- TL <- LOTL (dot #3: TL imzacı sertifikaları LOTL işaretçisinde, 43 işaretçi; T008, T018 OR)
kenar(k03_tl_lotl,a02_tl,a01_lotl).

% --- CA <- TL/LoTE (dot #4, #5). Güven deposu: 'liste_bagli' => kimlik türünün listesi;
%     'birlesik' => bütün listelerin çapaları (OID4VP trusted_authorities/AKI, T033, T034).
kenar(k05_ca_lotepid_tur,a03_ca,a02_lote_pid).  kenar_kosul(k05_ca_lotepid_tur,kimlik_turu,pid).
kenar(k05_ca_lotepid_bir,a03_ca,a02_lote_pid).  kenar_kosul(k05_ca_lotepid_bir,guven_deposu,birlesik).
kenar(k04_ca_tl_tur,a03_ca,a02_tl).             kenar_kosul(k04_ca_tl_tur,kimlik_turu,qeaa).
kenar(k04_ca_tl_bir,a03_ca,a02_tl).             kenar_kosul(k04_ca_tl_bir,guven_deposu,birlesik).

% --- İhraççı sertifikası <- CA (dot #6)
kenar(k06_ihr_ca,a04_ihr,a03_ca).

% --- Kimlik bilgisi <- ihraççı sertifikası (dot #7). Bütün anahtar kiplerinde imza anahtarını CA'nın
%     düzenlediği sertifika bağlar (V2/V3: kısa ömürlü sertifika; kimlik = CA zinciri).
kenar(k07_kimlik_ihr,a07_kimlik,a04_ihr).

% --- Kimlik bilgisi <- JWT VC Issuer Metadata (dot #27: alternatif anahtar yolu; T309-T311)
kenar(k27_kimlik_jvi,a07_kimlik,e_jvi).         kenar_kosul(k27_kimlik_jvi,anahtar_cozumleme,x5c_jvi).

% --- KB-JWT <- kimlik bilgisi (dot #8: cnf; T218, T220)
kenar(k08_kbjwt_kimlik,a10_kbjwt,a07_kimlik).

% --- Durum belirteci imzacısı (dot #10, #11). İmza anahtarını (kip ne olursa olsun) CA'nın düzenlediği
%     sertifika bağlar: durum_imzaci ∈ {ayni_ca (a04 sınıfı), farkli_capa (a08_ca)}; durum_baglama 'gevsek'
%     => her iki yol da kabul (OR; T159-T161 yalnız "should").
kenar(k11_durum_ihr,a08_durum,a04_ihr).         kenar_kosul(k11_durum_ihr,durum_imzaci,ayni_ca).
kenar(k11_durum_ihr_g,a08_durum,a04_ihr).       kenar_kosul(k11_durum_ihr_g,durum_baglama,gevsek).
kenar(k10_durum_dca,a08_durum,a08_ca).          kenar_kosul(k10_durum_dca,durum_imzaci,farkli_capa).
kenar(k10_durum_dca_g,a08_durum,a08_ca).        kenar_kosul(k10_durum_dca_g,durum_baglama,gevsek).
% durum CA'sının çapası PID LoTE'de (revocation service; T026); birleşik depoda TL'den de
kenar(k10_dca_lote,a08_ca,a02_lote_pid).
kenar(k10_dca_tl,a08_ca,a02_tl).                kenar_kosul(k10_dca_tl,guven_deposu,birlesik).

% --- WIA/KA <- cüzdan sağlayıcılar LoTE'si (dot #12); örnek anahtarı <- WIA (cnf)
kenar(k12_wia_lote,a09a_wia,a02_lote_cuzdan).
kenar(k12_ka_lote,a09b_ka,a02_lote_cuzdan).
kenar(k12_ornek_wia,a09c_ornek,a09a_wia).

% --- WRPAC/WRPRC <- ilgili LoTE (dot #13; T245)
kenar(k13_erisim_lote,a11_erisim,a02_lote_erisim).
kenar(k13_kayit_lote,a11_kayit,a02_lote_kayit).
kenar(k13_crl_lote,e_crl,a02_lote_erisim).      % CRL imzacısı = Access CA anahtarı

% --- İstek <- WRPAC (dot #15: x5c ile imza; T240, T299)
kenar(k15_istek_erisim,a12_istek,a11_erisim).

% --- İmzalı meta veri <- CA'nın düzenlediği sertifika (dot #17; T084)
kenar(k17_meta_ihr,a05_meta,a04_ihr).

% --- Birden çok CA / imzacı: OR-kenarları (adlandırılmış hücreler; koordinatör 24.09; ön kayıt §2D m.11)
% Aynı çıpa altında alternatif klasik CA. Doğrulayıcının CA bağlaması (ca_baglama):
%   yok     : kökün onayladığı HER CA'nın sertifikası kabul (RFC 5280 §6.2 [RFC5280]) -> alternatif yol açık;
%   ad      : ihraççı CA ADINA bağlı (RFC 5280 §4.2.1.10 ad kısıtları) -> yalnız aynı adlı alternatif kabul
%             (Tamarin R7hx X_namebind_samename: atlatılır; X_namebind_unique: korur);
%   anahtar : ihraççı CA ANAHTARINA bağlı -> alternatif hiçbir zaman kabul edilmez (R7hx X_keybind_*: korur).
% Her alternatif kenar iki koşullu kopya olarak yazılır: (ca_baglama=yok) VEYA (ca_baglama=ad ∧ ayni_ad_klasik_ca=var).
kenar(kx_digerca_lote,a03_diger,a02_lote_pid).
kenar(kx_digerca_tl,a03_diger,a02_tl).          kenar_kosul(kx_digerca_tl,guven_deposu,birlesik).
kenar(kx_digerihr_ca,a04_diger,a03_diger).
kenar(kx_kimlik_digerihr_y,a07_kimlik,a04_diger).  kenar_kosul(kx_kimlik_digerihr_y,ca_baglama,yok).
kenar(kx_kimlik_digerihr_a,a07_kimlik,a04_diger).  kenar_kosul(kx_kimlik_digerihr_a,ca_baglama,ad).
                                                   kenar_kosul(kx_kimlik_digerihr_a,ayni_ad_klasik_ca,var).
kenar(kx_durum_digerihr_y,a08_durum,a04_diger).    kenar_kosul(kx_durum_digerihr_y,ca_baglama,yok).
kenar(kx_durum_digerihr_a,a08_durum,a04_diger).    kenar_kosul(kx_durum_digerihr_a,ca_baglama,ad).
                                                   kenar_kosul(kx_durum_digerihr_a,ayni_ad_klasik_ca,var).
kenar(kx_meta_digerihr_y,a05_meta,a04_diger).      kenar_kosul(kx_meta_digerihr_y,ca_baglama,yok).
kenar(kx_meta_digerihr_a,a05_meta,a04_diger).      kenar_kosul(kx_meta_digerihr_a,ca_baglama,ad).
                                                   kenar_kosul(kx_meta_digerihr_a,ayni_ad_klasik_ca,var).
kenar(kx_digererisim_lote,a11_erisim_diger,a02_lote_erisim).
kenar(kx_istek_digererisim_y,a12_istek,a11_erisim_diger).  kenar_kosul(kx_istek_digererisim_y,ca_baglama,yok).
kenar(kx_istek_digererisim_a,a12_istek,a11_erisim_diger).  kenar_kosul(kx_istek_digererisim_a,ca_baglama,ad).
                                                           kenar_kosul(kx_istek_digererisim_a,ayni_ad_klasik_ca,var).
% A.3.2.2: ikinci güven çerçevesinin RP sertifikası (M-b); çerçeve bağlama yoksa kabul (T273, T314-T315)
kenar(kx_f2_capa,a11_erisim_f2,a00_f2_capa).
kenar(kx_istek_f2,a12_istek,a11_erisim_f2).     kenar_kosul(kx_istek_f2,cerceve_baglama,yok).

% --- guven-bagimliligi.dot'un 28 kenarının model karşılığı (izlenebilirlik; denetim betiği okur)
% dot_kenar(No, DotKaynak, DotHedef, Karsilik).  Karsilik: kenar kimliği ya da olgu adı.
dot_kenar(1,ojeu,lotl,sabit_a01_lotl).
dot_kenar(2,ojeu,lote,sabit_a02_lote).
dot_kenar(3,lotl,tl,k03_tl_lotl).
dot_kenar(4,tl,ca,k04_ca_tl_bir).
dot_kenar(5,lote,ca,k05_ca_lotepid_tur).
dot_kenar(6,ca,isc,k06_ihr_ca).
dot_kenar(7,isc,cred,k07_kimlik_ihr).
dot_kenar(8,cred,kb,k08_kbjwt_kimlik).
dot_kenar(9,cred,slt,url_kaynagi_a08).          % durum URI/indeks: çekme URL'si kimlik bilgisinden (anahtar tanıtımı değil)
dot_kenar(10,lote,slt,k10_dca_lote).
dot_kenar(11,ca,slt,k11_durum_ihr).
dot_kenar(12,lote,wua,k12_wia_lote).
dot_kenar(13,lote,rpc,k13_erisim_lote).
dot_kenar(14,crl,rpc,crl_gunbatimi_kancasi).   % iptal: gün batımı iptalle uygulanırsa klasik alternatifi açar
dot_kenar(15,rpc,req,k15_istek_erisim).
dot_kenar(16,imd,rpc,ihrac_tarafi_disarida).    % ihraççının erişim/kayıt sertifikası meta veride (ihraç tarafı)
dot_kenar(17,isc,imd,k17_meta_ihr).
dot_kenar(18,cred,tmd,ozet_bagi_a06).
dot_kenar(19,tmc,tmd,ozet_bagi_a06_onbellek).
dot_kenar(20,roots,tls,sabit_a13_webpki).
dot_kenar(21,tls,imd,tasima_a05).
dot_kenar(22,tls,slt,tasima_a08).
dot_kenar(23,tls,tl,tasima_a02).
dot_kenar(24,tls,tmd,tasima_a06).
dot_kenar(25,tls,jvi,tasima_e_jvi).
dot_kenar(26,tls,req,varyant_a12_imzasiz).
dot_kenar(27,jvi,cred,k27_kimlik_jvi).
dot_kenar(28,ojeu,lotl,tasima_a01_lotl_kanal).
