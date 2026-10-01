% =====================================================================
%  PQ-OID4VC | Adım 6 | KAT-3b kimlik doğrulama ikiliği — ÖRNEK DOSYASI (çekirdek DIŞI)
% =====================================================================
%  Koşum: model/asp/cekirdek.lp + bu dosya + ornekler/<koşu>.lp (başka hiçbir dosya yok).
%  Kaynak: KAT-SPEC §4(b) kat3b_auth_dual.lp, §4(d) KAT-3b tablosu; pilot referans/pilot/p1/weakest_link.spthy
%  (değiştirilmeden; 6 bayrak birleşimi V1–V6). Eşleme: ../ESLEME.md §4.5.
%  Güven listesi (TL; güven çapası ktl ile imzalı, ÇEKİLEN) ihraççının klasik ve PQ anahtarlarını listeler;
%  kimlik bilgisi (AKTARILAN) PQ anahtarla, birlikte yaşamada klasik anahtarla da imzalıdır. Doğrulayıcı
%  pol=required: klasik yol yalnız TL'den gelen "pq_required" beklentisi yoksa kabul edilir.
%  Hücre sabitleri: kat_tl_sinifi(cl|pq). kat_beklenti(0|1). kat_birlikte(0|1). kat_now/qday/tau.
%    kat_mutasyon(tl_beklenti_denetimi_yok) (KAT-SPEC §6).
%  Zaman kipleri (hücre sabitleriyle): dinamik qday=0 (CRQC 'now'dan önce), dinamik qday=200 (CRQC yok),
%  statik (zaman kısıtı kaldırılmış: now büyük, τ=0 => bütün klasik anahtarlar kırık; V14).
%  Okuma: SALDIRI (dinamik) / violation=1 (statik) <=> ihlal(tum,g1).
% =====================================================================

% TL: çapa anahtarıyla imzalı (sabit); ağdan çekilir, taşıma kimliksiz (pilotta Dolev–Yao ağı).
artefakt(tl). sinif(tl,guven_listesi). imzali(tl). kanal(tl,cekilen). tasima(tl,ag). sabit(tl).
artefakt(ag_yaniti). sinif(ag_yaniti,ag_tasimasi). imzasiz(ag_yaniti). kanal(ag_yaniti,kimliksiz).
tasima_anahtari(ag,ag_yaniti).
pqd(tl) :- kat_tl_sinifi(pq).
% Kimlik bilgisi: imzacı anahtarları TL'den tanıtılır (TL sahtelenirse saldırgan kendi anahtarını listeler).
artefakt(cred). sinif(cred,kimlik_bilgisi). imzali(cred). kanal(cred,aktarilan).
kenar(e_tl_ihracci,cred,tl).
hedef_artefakt(g1,cred). ana_hedef(g1).
pqd(cred).                                                       % ihraççının PQ anahtarı (iss_pq)
param_alan(kat,evet). p(kat,evet).
klasik_alt_zorla(cred,kat,evet) :- kat_birlikte(1).             % ihraççı klasik anahtarını da kullanıyor
% Beklenti: TL girdisi ihraççı için "pq_required" taşır (M-f); pol=required.
param_alan(politika,p4). p(politika,p4).
tasiyabilir(tl,cred,m_f) :- kat_beklenti(1), not kat_mutasyon(tl_beklenti_denetimi_yok).
tasi(tl,cred)            :- kat_beklenti(1), not kat_mutasyon(tl_beklenti_denetimi_yok).

% Zaman (CRQC-TAKVIMI §1) ve senaryo
maruziyet_kat(tl,0). maruziyet_kat(cred,0).
kirilma_basi(A,E) :- maruziyet_kat(A,E), kat_qday(Q), E >= Q.
kirilma_basi(A,Q) :- maruziyet_kat(A,E), kat_qday(Q), E < Q.
pencere(A,W)      :- kirilma_basi(A,B), kat_now(N), W = N - B.
sayisal_param(tau). sayisal_param(saat_payi).
p_sayi(tau,T) :- kat_tau(T).
p_sayi(saat_payi,0).
param_alan(saldirgan,s2). p(saldirgan,s2).
param_alan(k_sinir,sinirsiz). p(k_sinir,sinirsiz).
