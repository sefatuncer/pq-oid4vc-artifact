% =====================================================================
%  PQ-OID4VC | Adım 3 | PARAMETRE ALANLARI, FAZLAR, τ ve PENCERE IZGARALARI
% =====================================================================
%  Sürücü her kategorik parametre için tam bir p(Ad,Deger), her sayısal parametre için
%  tam bir p_sayi(Ad,Deger) verir. Çekirdek alan ve teklik denetimi yapar (hatalı sorgu UNSAT
%  değil, 'parametre_hatasi' üretir). Varsayılanlar sürücüdedir (sorgular/ortak.py) ve
%  RAPOR.md §1.5'te tablolanır.
% =====================================================================

% --- Saldırgan ve kırılma sınırı (ön kayıt §4.3; Ö8)
param_alan(saldirgan,s1).  param_alan(saldirgan,s2).            % s1: Q-day öncesi ağ saldırganı; s2: CRQC(τ,k)
param_alan(k_sinir,sinirsiz). param_alan(k_sinir,k1). param_alan(k_sinir,k3).
% --- Faz Φ (ön kayıt §4.2; Ö10#1 onaylandı)
param_alan(faz,f1). param_alan(faz,f2). param_alan(faz,f3).
% --- Çıpa kipleri (§4.6) ve önbellek ufku
param_alan(capa,taze). param_alan(capa,sabit). param_alan(capa,onbellek).
param_alan(onbellek_ufku,kararli). param_alan(onbellek_ufku,ilk_pencere).
% --- WebPKI PQ durumu (H1; §4.3 varsayımı)
param_alan(webpki,cl). param_alan(webpki,pq). param_alan(webpki,pq_birlikte).
% --- Politikalar P0–P4 (§4.8)
param_alan(politika,p0). param_alan(politika,p1). param_alan(politika,p2). param_alan(politika,p3). param_alan(politika,p4).
% --- Durum listesi kullanılıyor mu ('yok': ≤24 sa kısa ömürlü kimlik bilgisi seçeneği, T175; iptal süre dolumuyla)
param_alan(durum_listesi,var). param_alan(durum_listesi,yok).
% --- Anahtar rejimleri (Ö1: V1/V2/V3)
param_alan(ihracci_anahtari,uzun). param_alan(ihracci_anahtari,gunluk). param_alan(ihracci_anahtari,gecici).
param_alan(durum_anahtari,uzun).   param_alan(durum_anahtari,gunluk).   param_alan(durum_anahtari,gecici).
param_alan(cihaz_anahtari,kalici). param_alan(cihaz_anahtari,kimlik_basi).
param_alan(wia_anahtari,wia_basi). param_alan(wia_anahtari,kalici).
param_alan(tek_kullanim,yok). param_alan(tek_kullanim,cuzdan). param_alan(tek_kullanim,dogrulayici). param_alan(tek_kullanim,kuresel_pasif).
param_alan(anahtar_yeniden_kullanim,yok). param_alan(anahtar_yeniden_kullanim,var).   % Tamarin R6 KEY_REUSE: V2/V3 sertifikası döner, anahtar dönmez
% --- Güven deposu, kimlik türü, anahtar çözümleme, LOTL indirme kanalı
param_alan(kimlik_turu,pid). param_alan(kimlik_turu,qeaa).
param_alan(guven_deposu,birlesik). param_alan(guven_deposu,liste_bagli).
param_alan(anahtar_cozumleme,x5c). param_alan(anahtar_cozumleme,x5c_jvi).
param_alan(lotl_indirme,ojeu_sabit). param_alan(lotl_indirme,webpki).
% --- Durum listesi
param_alan(durum_imzaci,ayni_ca). param_alan(durum_imzaci,farkli_capa).
param_alan(durum_baglama,siki). param_alan(durum_baglama,gevsek).
param_alan(durum_kanali,cekilen). param_alan(durum_kanali,aktarilan).
% --- İstek nesnesi ve imzasızlaştırma (M-b0)
param_alan(istek_iletimi,dc_api). param_alan(istek_iletimi,request_uri).
param_alan(imzasiz_istek_kabul,var). param_alan(imzasiz_istek_kabul,yok).
param_alan(imzasiz_meta_kabul,var).  param_alan(imzasiz_meta_kabul,yok).
% --- Type Metadata
param_alan(tmd_isleme,var). param_alan(tmd_isleme,yok).     % özet bağlaması artık A06 karar düğümüdür (pq(a06_tip))
% --- Politika parametreleri (Ö9)
param_alan(iptal_denetimi,var). param_alan(iptal_denetimi,yok).
param_alan(cihaz_bagi,var). param_alan(cihaz_bagi,yok).
param_alan(rp_auth_fail_open,var). param_alan(rp_auth_fail_open,yok).
param_alan(wrprc_dogrulama,faz0). param_alan(wrprc_dogrulama,faz1).
param_alan(ca_baglama,yok). param_alan(ca_baglama,ad). param_alan(ca_baglama,anahtar).   % §2D m.11 (ad_baglama'nın yerine)
param_alan(ayni_ad_klasik_ca,yok). param_alan(ayni_ad_klasik_ca,var).                    % §2D m.11 (yapısal bayrak)
param_alan(sdjwtvc_surum,s13). param_alan(sdjwtvc_surum,s19).
% --- Birden çok CA / çerçeve (OR-kenarları)
param_alan(diger_ca,var). param_alan(diger_ca,yok).
param_alan(diger_ca_rejimi,klasik_sabit). param_alan(diger_ca_rejimi,karar).
param_alan(coklu_cerceve,var). param_alan(coklu_cerceve,yok).
param_alan(cerceve_baglama,var). param_alan(cerceve_baglama,yok).
param_alan(f2_rejimi,klasik). param_alan(f2_rejimi,pq).
% --- WSCD donanımı PQ destekliyor mu (M5; pilot 'wscd' karşılığı)
param_alan(wscd_pq,var). param_alan(wscd_pq,yok).
% --- Mekanizma kancaları (Adım 7'de tam modellenecek)
param_alan(mekanizma_kancalari,acik). param_alan(mekanizma_kancalari,kapali).   % M-g, M-h
param_alan(md_kanca,acik). param_alan(md_kanca,kapali).                         % M-d
param_alan(ma_kanca,acik). param_alan(ma_kanca,kapali).                         % M-a
param_alan(ilk_temas,qday_oncesi). param_alan(ilk_temas,qday_sonrasi).          % M-g
param_alan(gun_batimi,guven_deposu). param_alan(gun_batimi,iptal).              % Φ3 gün batımının uygulanışı

sayisal_param(tau). sayisal_param(saat_payi). sayisal_param(kimlik_gecerlilik).
sayisal_param(durum_ttl). sayisal_param(kbjwt_iat).
% §2C 2.3 anahtar güven pencereleri (W_güven; saniye). Birincil: w_kok 5 y, w_ca 5 y, w_ihracci 1 y,
% w_rp 1 y, w_tls 1 y, w_wia 1 g, w_ka 1 y; kimlik_gecerlilik (cnf) 30 g; durum_ttl 1 g; kbjwt_iat 10 dk.
sayisal_param(w_kok). sayisal_param(w_ca). sayisal_param(w_ihracci). sayisal_param(w_rp).
sayisal_param(w_tls). sayisal_param(w_wia). sayisal_param(w_ka).

% --- Faz sınıflandırması (§4.2): Φ2'de klasik alternatif yalnız YAPRAK sınıflarda açık.
%     PKI/çıpa sınıfları: a01 LOTL, a02 TL/LoTE, a03 CA, a04 CA'nın düzenlediği sertifikalar, a13 taşıma.
yaprak_sinif(a05). yaprak_sinif(a06). yaprak_sinif(a07). yaprak_sinif(a08).
yaprak_sinif(a09). yaprak_sinif(a10). yaprak_sinif(a11). yaprak_sinif(a12).
yaprak_sinif(e_jvi). yaprak_sinif(e_asmeta).   % e_crl: CA'nın imzaladığı iptal bilgisi => PKI sınıfı

% --- τ ızgaraları (saniye; CRQC-TAKVIMI §0, Ö8, §2C 2.3)
tau_nominal(hizli,600). tau_nominal(orta,259200). tau_nominal(yavas,2246400).
tau_duyarlilik(hizli,60). tau_duyarlilik(hizli,600). tau_duyarlilik(hizli,3600).
tau_duyarlilik(orta,86400). tau_duyarlilik(orta,259200). tau_duyarlilik(orta,604800). tau_duyarlilik(orta,864000).
tau_duyarlilik(yavas,1209600). tau_duyarlilik(yavas,2246400). tau_duyarlilik(yavas,5184000).
tau_genis(84). tau_genis(600). tau_genis(3600). tau_genis(50400). tau_genis(259200). tau_genis(864000).
tau_genis(2246400). tau_genis(4492800). tau_genis(22809600). tau_genis(86400000). tau_genis(2100000000).   % son: ∞ (CRQC yok)
% --- Pencere ızgarası (§4.5 logaritmik; saniye): 1 sa, 1 g, 7 g, 30 g, 180 g, 1 y, 5 y
pencere_izgara(3600). pencere_izgara(86400). pencere_izgara(604800). pencere_izgara(2592000).
pencere_izgara(15552000). pencere_izgara(31536000). pencere_izgara(157680000).
% --- Sabit pencereler (Ö8): TL/LoTE ≤ 6 ay (T010, T021; LOTL örneği 181 gün); WIA < 24 sa (T204); kısa ömürlü KB ≤ 24 sa (T175)
%     TL/LoTE ≤ 6 ay bir BELİRTEÇ (W_kabul) penceresidir: imzacı anahtarın W_güven'i değil (H2′ yanlışlama testi i).
sabit_pencere(tl_lote,15638400). sabit_pencere(wia,86400). sabit_pencere(kisa_kimlik,86400).
