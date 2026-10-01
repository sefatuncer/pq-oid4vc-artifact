% =====================================================================
%  PQ-OID4VC | Adım 3 | BEKLENTİ TAŞIYICILARI (convey/2 kancası = tasi/2)
% =====================================================================
%  tasiyabilir(C,X,M): C artefaktı, X'i imzalayan VARLIK için "PQ gerekli" beklentisini
%  taşıyabilir; M mekanizma sınıfıdır. Karar değişkeni tasi(C,X) (sorgu minimal kümesinde yer alır).
%  tasiyabilir_kosul(C,X,P,V): taşıyıcı ancak p(P,V) iken kullanılabilir (hepsi).
%  Politika: P0-P2 beklenti kullanmaz; P3 klasik kanaldan öğrenir (yalnız Q-day öncesi sağlam);
%  P4 PQ ile kimliği doğrulanmış taşıyıcıdan (C sahtelenemez) — ön kayıt §4.8.
%  Mekanizma sınıfları (ön kayıt §4.11 + literatür L-D1):
%    m_f   TL/LoTE (ya da LOTL/OJEU) kaydında varlık başına beklenti (önerilen M-f'nin taşıyıcısı)
%    m_f2  WRPRC alanında varlık başına beklenti (ikincil M-f taşıyıcısı; doğrulama fazı: T254)
%    m_e2  imzalı meta veride "*_alg_values_required" (M-e′; T393, T394 emsali)
%    m_h   sertifikaya gömülü PQ taahhüt eki (reddy-x509-pq-commit, vicente-pqchc) — kanca
%    m_g   öz-beyanlı süreklilik / TOFU (sheffer-tls-pqc-continuity) — kanca
%    m_d   bant dışı statik yapılandırma (DCR, CIMD; HAIP §7 T123) — kanca (S3 ve regresyon)
%    m_a   kimliği doğrulanmamış yetenek alanı (R2 EXPECT_UNAUTH) — kanca
%  NOT: e_asmeta (AS meta verisi) yalnız "supported" taşır (M-a) => hiçbir X için taşıyıcı değildir.
%  NOT: Beklenti yalnız K4'ü (klasik alternatif) ve imzasız varyantları kapatır; alternatif
%       TANITICI yollarını (K2: başka CA, JVI, ikinci çerçeve) kapatmaz — saldırganın kendi
%       anahtarı da PQ olabilir. Onları bağlama parametreleri kapatır (ca_baglama, cerceve_baglama,
%       anahtar_cozumleme, guven_deposu). Adım 7'de beklenti_kapsami ∈ {yaprak_alg, yol_sinifi, anahtar}
%       (§2D m.13) kabul edilen yolun KENAR sınıfları üzerinden değerlendirilecek: kenar/3 kimlikleri ve
%       kabul_alti/2 bu kapsam denetimine hazırdır (çekirdek değişmeden eklenebilir).
% =====================================================================

% --- M-f: OJEU (LOTL ve LoTE imzacıları için; Φ1'de anlamlı)
tasiyabilir(a00_ojeu,a01_lotl,m_f).
tasiyabilir(a00_ojeu,a02_lote_pid,m_f).
tasiyabilir(a00_ojeu,a02_lote_cuzdan,m_f).
tasiyabilir(a00_ojeu,a02_lote_erisim,m_f).
tasiyabilir(a00_ojeu,a02_lote_kayit,m_f).
tasiyabilir(a00_ojeu,a13_lotl_kanal,m_f).
% --- M-f: LOTL işaretçisi (TL imzacıları için)
tasiyabilir(a01_lotl,a02_tl,m_f).
% --- M-f: PID LoTE kaydı (PID sağlayıcısının zinciri, kimlik bilgisi, cihaz bağı, durum, meta veri)
tasiyabilir(a02_lote_pid,a03_ca,m_f).       tasiyabilir_kosul(a02_lote_pid,a03_ca,kimlik_turu,pid).
tasiyabilir(a02_lote_pid,a04_ihr,m_f).      tasiyabilir_kosul(a02_lote_pid,a04_ihr,kimlik_turu,pid).
tasiyabilir(a02_lote_pid,a07_kimlik,m_f).   tasiyabilir_kosul(a02_lote_pid,a07_kimlik,kimlik_turu,pid).
tasiyabilir(a02_lote_pid,a10_kbjwt,m_f).    tasiyabilir_kosul(a02_lote_pid,a10_kbjwt,kimlik_turu,pid).
tasiyabilir(a02_lote_pid,a08_durum,m_f).    tasiyabilir_kosul(a02_lote_pid,a08_durum,kimlik_turu,pid).
tasiyabilir(a02_lote_pid,a08_ca,m_f).
tasiyabilir(a02_lote_pid,a05_meta,m_f).     tasiyabilir_kosul(a02_lote_pid,a05_meta,kimlik_turu,pid).
tasiyabilir(a02_lote_pid,a06_tip,m_f).      tasiyabilir_kosul(a02_lote_pid,a06_tip,kimlik_turu,pid).     % "tür bütünlüğü özeti zorunlu"
tasiyabilir(a02_lote_pid,e_jvi,m_f).        tasiyabilir_kosul(a02_lote_pid,e_jvi,kimlik_turu,pid).       % "anahtar yalnız bağlı JWKS/x5c ile"
% --- M-f: ulusal TL kaydı (QEAA sağlayıcıları için)
tasiyabilir(a02_tl,a03_ca,m_f).             tasiyabilir_kosul(a02_tl,a03_ca,kimlik_turu,qeaa).
tasiyabilir(a02_tl,a04_ihr,m_f).            tasiyabilir_kosul(a02_tl,a04_ihr,kimlik_turu,qeaa).
tasiyabilir(a02_tl,a07_kimlik,m_f).         tasiyabilir_kosul(a02_tl,a07_kimlik,kimlik_turu,qeaa).
tasiyabilir(a02_tl,a10_kbjwt,m_f).          tasiyabilir_kosul(a02_tl,a10_kbjwt,kimlik_turu,qeaa).
tasiyabilir(a02_tl,a08_durum,m_f).          tasiyabilir_kosul(a02_tl,a08_durum,kimlik_turu,qeaa).
tasiyabilir(a02_tl,a05_meta,m_f).           tasiyabilir_kosul(a02_tl,a05_meta,kimlik_turu,qeaa).
tasiyabilir(a02_tl,a06_tip,m_f).            tasiyabilir_kosul(a02_tl,a06_tip,kimlik_turu,qeaa).
tasiyabilir(a02_tl,e_jvi,m_f).              tasiyabilir_kosul(a02_tl,e_jvi,kimlik_turu,qeaa).
% --- M-f: cüzdan sağlayıcılar LoTE'si
tasiyabilir(a02_lote_cuzdan,a09a_wia,m_f).
tasiyabilir(a02_lote_cuzdan,a09b_ka,m_f).
tasiyabilir(a02_lote_cuzdan,a09c_ornek,m_f).
% --- M-f: Access CA ve WRPRC sağlayıcı LoTE'leri (sağlayıcı düzeyi; RP düzeyi değil)
tasiyabilir(a02_lote_erisim,a11_erisim,m_f).
tasiyabilir(a02_lote_kayit,a11_kayit,m_f).
% --- M-f (ikincil): WRPRC alanında RP başına beklenti; doğrulama zorunluluğu fazına bağlı (T254)
tasiyabilir(a11_kayit,a12_istek,m_f2).      tasiyabilir_kosul(a11_kayit,a12_istek,wrprc_dogrulama,faz1).

% --- M-e′: imzalı meta veride "gerekli" algoritma alanı (ablasyon varyantı; Adım 1 kararı)
tasiyabilir(a05_meta,a07_kimlik,m_e2).
tasiyabilir(a05_meta,a08_durum,m_e2).
tasiyabilir(a05_meta,a10_kbjwt,m_e2).

% --- M-h (kanca): sertifikaya gömülü taahhüt. Etkinlik koşulu (çekirdek): C, X'in bütün kabul
%     edilen tanıtım yollarında baskın (alternatif CA yolu yok) ve C klasik alternatifin de
%     yolunda (ortak_ata). Yaprak sertifikadaki ek, eski klasik sertifikalı yolu kapatamaz.
tasiyabilir(a04_ihr,a07_kimlik,m_h).        tasiyabilir_kosul(a04_ihr,a07_kimlik,mekanizma_kancalari,acik).
tasiyabilir(a03_ca,a07_kimlik,m_h).         tasiyabilir_kosul(a03_ca,a07_kimlik,mekanizma_kancalari,acik).
tasiyabilir(a11_erisim,a12_istek,m_h).      tasiyabilir_kosul(a11_erisim,a12_istek,mekanizma_kancalari,acik).
ortak_ata(a03_ca,a07_kimlik).               % varsayım: aynı CA hem klasik hem PQ ihraççı anahtarını sertifikalar [K-Ç]

% --- M-g (kanca): öz-beyanlı süreklilik / TOFU
tasiyabilir(m_g_oz,a07_kimlik,m_g).         tasiyabilir_kosul(m_g_oz,a07_kimlik,mekanizma_kancalari,acik).
tasiyabilir(m_g_oz,a12_istek,m_g).          tasiyabilir_kosul(m_g_oz,a12_istek,mekanizma_kancalari,acik).
tasiyabilir(m_g_oz,a05_meta,m_g).           tasiyabilir_kosul(m_g_oz,a05_meta,mekanizma_kancalari,acik).

% --- M-d (kanca): bant dışı yapılandırma; her varlık için (S3 stratejisi; md_kanca=acik)
tasiyabilir(m_d_cfg,a01_lotl,m_d).    tasiyabilir(m_d_cfg,a02_tl,m_d).       tasiyabilir(m_d_cfg,a02_lote_pid,m_d).
tasiyabilir(m_d_cfg,a02_lote_cuzdan,m_d). tasiyabilir(m_d_cfg,a02_lote_erisim,m_d). tasiyabilir(m_d_cfg,a02_lote_kayit,m_d).
tasiyabilir(m_d_cfg,a03_ca,m_d).      tasiyabilir(m_d_cfg,a04_ihr,m_d).      tasiyabilir(m_d_cfg,a05_meta,m_d).
tasiyabilir(m_d_cfg,a07_kimlik,m_d).  tasiyabilir(m_d_cfg,a08_durum,m_d).
tasiyabilir(m_d_cfg,a08_ca,m_d).      tasiyabilir(m_d_cfg,a09a_wia,m_d).
tasiyabilir(m_d_cfg,a09b_ka,m_d).     tasiyabilir(m_d_cfg,a09c_ornek,m_d).   tasiyabilir(m_d_cfg,a10_kbjwt,m_d).
tasiyabilir(m_d_cfg,a11_erisim,m_d).  tasiyabilir(m_d_cfg,a11_kayit,m_d).    tasiyabilir(m_d_cfg,a12_istek,m_d).
tasiyabilir(m_d_cfg,a13_lotl_kanal,m_d).

% --- M-a (kanca): kimliksiz alan (yalnız downgrade gösterimi; hiçbir politikada sağlam değil)
tasiyabilir(m_a_alan,a07_kimlik,m_a).       tasiyabilir_kosul(m_a_alan,a07_kimlik,ma_kanca,acik).
tasiyabilir(m_a_alan,a12_istek,m_a).        tasiyabilir_kosul(m_a_alan,a12_istek,ma_kanca,acik).
