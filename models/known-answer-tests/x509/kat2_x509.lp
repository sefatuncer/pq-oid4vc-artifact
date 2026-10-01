% =====================================================================
%  PQ-OID4VC | Adım 6 | KAT-2 X.509 hibrit — ÖRNEK DOSYASI (çekirdek DIŞI)
% =====================================================================
%  Koşum: models/asp/cekirdek.lp + bu dosya + ornekler/<hücre>.lp (başka hiçbir dosya yok).
%  Kaynak: KAT-SPEC §3(a)–(d); Kim vd. arXiv:2607.20800 (§VI-A, Tablo IV–VI); Lee vd. ePrint 2026/1416
%  (§4.3, §4.4, §6). Eşlemenin gerekçesi ve OKUMA KURALLARI: ../ESLEME.md §3.
%
%  İki kip (hücre sabiti kat_mod):
%   saldiri (K2b; Kim M2 = CRQC): senaryo 'tum'. Okuma: SALDIRI <=> ihlal(tum,g1).
%   karar   (K2a/K2c/K2d; Kim M1 = CRQC yok, dürüst nesne): senaryo 'bos' (S1). Çekirdek, doğrulayıcının
%           bu nesne için PQ kanıtını GEREKLİ KILIP KILMADIĞINI G5 ile hesaplar: ihlal(bos,g5) <=> göç etmiş
%           (hibrit ihraç edilmiş) varlığın klasik kanıtı, kimliği doğrulanmış bir PQ beklentisi olmadan kabul
%           ediliyor ("classical acceptance"; Tamarin no_silent_promotion'ın karşılığı). Karar etiketi
%           ESLEME.md §3.4'teki sabit okuma kuralıyla (kos.py: karar_oku) G5'ten ve nesnenin kanıt
%           durumundan (kat_pqev, kat_leafb) elde edilir.
%  Hücre sabitleri: kat_mod(karar|saldiri). kat_sema(catalyst|chameleon|related|composite).
%    kat_vb(ignore|parse_no_enforce|enforce_if_present|require|require_tl|continuity|legacy_oid).
%    kat_pqev(valid|invalid|absent). kat_leafb(valid|revoked|expired|unknown|absent|yok).
%    kat_goruldu_hibrit(0|1). kat_tl_sinifi(cl|pq). kat_birlikte_klasik(0|1). kat_now(N). kat_qday(Q).
%    kat_tau(T). kat_mutasyon(M) (KAT-SPEC §6).
% =====================================================================

% ---------------------------------------------------------------- uç varlık sertifikası (hedef)
% CA anahtarları güven çapasıdır (KAT-SPEC: anchor(ca_*), anchored(ca_*,ee)) => sabit. Kanal: aktarılan.
artefakt(ee). sinif(ee,ee_sertifikasi). imzali(ee). kanal(ee,aktarilan). sabit(ee). karar(ee).
hedef_artefakt(g1,ee). ana_hedef(g1). g5_degerlendir(g1).

% PQ yolu: CA'nın PQ (ya da composite) anahtarıyla hibrit ihraç. Nesnenin KENDİ PQ kanıtının durumu
% (geçerli/geçersiz/yok) bir politika sorusu değildir; okuma kuralına girer (ESLEME.md §3.4).
hibrit_sema(catalyst). hibrit_sema(chameleon). hibrit_sema(related). hibrit_sema(composite).
pqd(ee) :- kat_sema(S), hibrit_sema(S), not pq_guvencesi_yok.
% §6 mutasyonu: composite doğrulamasında PQ bileşen denetimi silindi => composite'in güvencesi klasik bileşene iner.
pq_guvencesi_yok :- kat_sema(composite), kat_mutasyon(comp_pq_denetimi_yok).

% Klasik alternatif: ayrılabilir şemalarda temel (klasik, kritik) imza varsayılan yolda tek başına kabul
% edilir (Kim §VI-A). Composite tek imzadır; klasik yol yalnız birlikte yaşamada, aynı CA'nın düz klasik
% sertifikaları da kabul edildiğinde vardır (KAT-SPEC coexist_cl; Lee §6).
param_alan(kat,evet). p(kat,evet).
ayrilabilir(catalyst). ayrilabilir(chameleon). ayrilabilir(related).
klasik_alt_zorla(ee,kat,evet) :- kat_sema(S), ayrilabilir(S).
klasik_alt_zorla(ee,kat,evet) :- kat_sema(composite), kat_birlikte_klasik(1).

% ---------------------------------------------------------------- doğrulayıcı politikası -> beklenti taşıyıcısı
% ignore / parse_no_enforce / legacy_oid: PQ kanıtı karara girmez (beklenti yok; P0).
param_alan(politika,p0). param_alan(politika,p4).
beklentisiz(ignore). beklentisiz(parse_no_enforce). beklentisiz(legacy_oid).
p(politika,p0) :- kat_vb(V), beklentisiz(V).
p(politika,p4) :- kat_vb(V), not beklentisiz(V).

% enforce_if_present ("varsa denetle", P1): PQ kanıtının VARLIĞI beklenti taşır. Varlık, nesnenin klasik
% temel imzasıyla korunur (Catalyst/Chameleon: TBS içindeki uzantı) => taşıyıcı klasik imzalı; klasik
% anahtar kırılırsa saldırgan PQ kanıtını soyar ve yeniden imzalar (Lee §4.4: "a stripped classical-only
% leaf is accepted"). Kanıt yoksa sinyal de yoktur.
pq_kaniti_mevcut :- kat_pqev(valid).
pq_kaniti_mevcut :- kat_pqev(invalid).
artefakt(pq_kanit_varligi) :- kat_vb(enforce_if_present), pq_kaniti_mevcut.
% require (P2, yerel politika "require-PQC"): bant dışı statik yapılandırma (M-d; sabitlenmiş, özgün).
% §6 mutasyonu: P2'de bağlı sertifika durum denetimi silindi => Related'da politika bağlı PQ sertifikasını
% kapsama almaz (V9: bağlı artefakt yalnız politika kapsama alırsa karara girer).
artefakt(yerel_politika) :- kat_vb(require), not bagli_kapsam_disi.
bagli_kapsam_disi :- kat_sema(related), kat_mutasyon(bagli_durum_denetimi_yok).
% require_tl (K2b-04/05): beklenti imzalı bir güven listesinden (M-f); TL anahtarının sınıfı hücreye göre.
artefakt(tl) :- kat_vb(require_tl).
pqd(tl) :- kat_vb(require_tl), kat_tl_sinifi(pq).
% continuity (P3): doğrulayıcının yerel süreklilik durumu ("bu özne hibrit görüldü"); yalnız ilk temastan
% SONRA vardır (Kim Tablo VI notu). §6 mutasyonu: hybrid_seen durumu yok sayılır.
artefakt(sureklilik_durumu) :- kat_vb(continuity), kat_goruldu_hibrit(1),
                               not kat_mutasyon(sureklilik_durumu_yok_sayilir).

tasiyici(pq_kanit_varligi,m_a). tasiyici(yerel_politika,m_d). tasiyici(tl,m_f). tasiyici(sureklilik_durumu,m_g).
tasiyabilir(C,ee,M) :- tasiyici(C,M), artefakt(C).
tasi(C,ee)          :- tasiyici(C,_), artefakt(C).
sinif(pq_kanit_varligi,oz_sinyal)   :- artefakt(pq_kanit_varligi).
imzali(pq_kanit_varligi)            :- artefakt(pq_kanit_varligi).
kanal(pq_kanit_varligi,aktarilan)   :- artefakt(pq_kanit_varligi).
sabit(pq_kanit_varligi)             :- artefakt(pq_kanit_varligi).
sinif(yerel_politika,yapilandirma)  :- artefakt(yerel_politika).
imzasiz(yerel_politika)             :- artefakt(yerel_politika).
kanal(yerel_politika,sabitlenmis)   :- artefakt(yerel_politika).
sinif(tl,guven_listesi)             :- artefakt(tl).
imzali(tl)                          :- artefakt(tl).
kanal(tl,aktarilan)                 :- artefakt(tl).
sabit(tl)                           :- artefakt(tl).
sinif(sureklilik_durumu,yerel_durum):- artefakt(sureklilik_durumu).
imzasiz(sureklilik_durumu)          :- artefakt(sureklilik_durumu).
kanal(sureklilik_durumu,sabitlenmis):- artefakt(sureklilik_durumu).

% ---------------------------------------------------------------- zaman (CRQC-TAKVIMI §1) ve senaryo
maruziyet_kat(ee,0). maruziyet_kat(pq_kanit_varligi,0). maruziyet_kat(tl,0).
kirilma_basi(A,E) :- maruziyet_kat(A,E), kat_qday(Q), E >= Q.
kirilma_basi(A,Q) :- maruziyet_kat(A,E), kat_qday(Q), E < Q.
pencere(A,W)      :- kirilma_basi(A,B), kat_now(N), W = N - B.
sayisal_param(tau). sayisal_param(saat_payi).
p_sayi(tau,T) :- kat_tau(T).
p_sayi(saat_payi,0).
param_alan(saldirgan,s1). param_alan(saldirgan,s2).
p(saldirgan,s1) :- kat_mod(karar).      % Kim M1: CRQC yok (dürüst nesnenin kararı)
p(saldirgan,s2) :- kat_mod(saldiri).    % Kim M2: CRQC
param_alan(k_sinir,sinirsiz). p(k_sinir,sinirsiz).
