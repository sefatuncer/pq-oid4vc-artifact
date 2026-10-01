% =====================================================================
%  PQ-OID4VC | Adım 6 | KAT-3a S/MIME (CMS gizliliği) — ÖRNEK DOSYASI (çekirdek DIŞI)
% =====================================================================
%  Koşum: models/asp/cekirdek.lp + bu dosya + ornekler/<koşu>.lp (başka hiçbir dosya yok).
%  Kaynak: KAT-SPEC §4(a)–(d); Das & Chattopadhyay ePrint 2026/1374 (özet; §3 Denk. (8), Önerme 1;
%  §3.1 Aşama 3–5, Tablo 1). Eşlemenin gerekçesi ve OKUMA KURALLARI: ../ESLEME.md §4.
%
%  YAPI EŞLEMESİ ("yol tabanlı politika sağlama"; ÖK §4.19): gizlilik -> kimlik doğrulama ikiliği.
%   - CEK = hedef artefakt (cek). Her alıcı yapısı (RecipientInfo) CEK'e giden bir yol = CEK'in bir
%     tanıtıcısı (kenar). Çekirdeğin any-valid-path kuralı (K2): kabul edilen HERHANGİ bir yol
%     "sahtelenebilir" (CEK'i kurtarabilir) ise hedef çiğnenir  <=>  Das: herhangi bir geçerli alıcı yolu
%     CEK'i kurtarırsa ED açığa çıkar (Önerme 1: en zayıf geçerli yol).
%   - V_i(t) = 1 (alıcı sertifikası geçerli) => kenar var; değilse yol sayılmaz (Das'ın kuralı YAZILDIĞI gibi).
%   - Etkin göç politikası A_t bir SONDA ile uygulanır: A_t dışındaki sınıfların yolları "kırılabilir"
%     (klasik), içindekiler PQ sayılır. Evrensel kabul (Denk. 8) <=> A_t dışında geçerli yol yok
%     <=> çekirdekte ihlal yok (V14: statik politika denetimi = bütün izin dışı anahtarlar kırıkken
%     dinamik saldırı araması).
%  Hücre sabitleri: kat_vektor(o1..o12). kat_prob(kati|gecis|klasik|bilinmeyen|gecersiz|pq_hibrit|
%    tum_klasik_yol). kat_now/qday/tau. kat_mutasyon(bilinmeyen_izinli) (KAT-SPEC §6).
%  Okuma: E(prob) := ihlal(tum,g1). Etiketler (kos.py; ESLEME.md §4.4) yalnız sonda sonuçlarından.
% =====================================================================

% ---------------------------------------------------------------- test vektörleri (KAT-SPEC §4(d))
% ri(O,I,Tur,Sertifika): O vektörünün I. alıcı yolu.
ri(o1,1,mlkem,gecerli).
ri(o2,1,mlkem,gecerli).       ri(o2,2,mlkem,gecerli).
ri(o3,1,rsa_kt,gecerli).
ri(o4,1,mlkem,gecerli).       ri(o4,2,rsa_kt,gecerli).
ri(o5,1,hybrid_kem,gecerli).
ri(o6,1,hybrid_kem,gecerli).  ri(o6,2,ecdh_ka,gecerli).
ri(o7,1,mlkem,gecerli).       ri(o7,2,unknown_oid,gecerli).
ri(o8,1,mlkem,gecerli).       ri(o8,2,rsa_kt,gecersiz).
ri(o9,1,malformed,gecerli).
ri(o10,1,hybrid_kem,gecerli).
ri(o11,1,mlkem,gecerli).      ri(o11,2,hybrid_kem,gecerli).
ri(o12,1,ecdh_ka,gecerli).    ri(o12,2,rsa_kt,gecerli).
onayli_hibrit(o5). onayli_hibrit(o6). onayli_hibrit(o11).   % "approved_hybrid yalnız o5, o6, o11'de doğru"

% Das Aşama 3 yol sınıfları (KAT-SPEC kat3a_smime.lp ile aynı)
yol_sinifi(O,I,pqc)       :- ri(O,I,mlkem,_).
yol_sinifi(O,I,hybrid)    :- ri(O,I,hybrid_kem,_), onayli_hibrit(O).
yol_sinifi(O,I,unknown)   :- ri(O,I,hybrid_kem,_), not onayli_hibrit(O).
yol_sinifi(O,I,classical) :- ri(O,I,rsa_kt,_).
yol_sinifi(O,I,classical) :- ri(O,I,ecdh_ka,_).
yol_sinifi(O,I,unknown)   :- ri(O,I,unknown_oid,_).
yol_sinifi(O,I,invalid)   :- ri(O,I,malformed,_).

% ---------------------------------------------------------------- sondalar: kırılabilir (izin dışı) sınıflar
% Politika sondaları: kati (strict-PQC: A = {pqc}), gecis (transitional-hybrid: A = {pqc, hybrid}).
% "Unknown mechanisms fail closed" => unknown hiçbir A'da yok. malformed => invalid (A'da yok).
kirilabilir(kati,hybrid). kirilabilir(kati,classical). kirilabilir(kati,unknown). kirilabilir(kati,invalid).
kirilabilir(gecis,classical). kirilabilir(gecis,unknown). kirilabilir(gecis,invalid).
% Sınıf sondaları (Tablo 1 etiketleri için "geçerli yollar arasında C sınıfı var mı?"):
kirilabilir(klasik,classical).
kirilabilir(bilinmeyen,unknown).
kirilabilir(gecersiz,invalid).
kirilabilir(pq_hibrit,pqc). kirilabilir(pq_hibrit,hybrid).
% Model farkı sondası (okuma notu; kapı değeri değil): CRQC klasik yolu sertifika geçerliliğinden bağımsız kırar.
kirilabilir(tum_klasik_yol,classical).
% KAT-SPEC §6 mutasyonu "fail-closed: unknown sınıfını izinli say" (yalnız politika sondalarında)
politika_sondasi(kati). politika_sondasi(gecis).
izinli_yapildi(P,unknown) :- kat_mutasyon(bilinmeyen_izinli), politika_sondasi(P).
kirilabilir_etkin(P,C) :- kirilabilir(P,C), not izinli_yapildi(P,C).

% ---------------------------------------------------------------- çekirdek sözlüğü
artefakt(cek). sinif(cek,cek). imzali(cek). kanal(cek,aktarilan). pqd(cek).   % CEK'in kendi zayıflığı yok
hedef_artefakt(g1,cek). ana_hedef(g1).
artefakt(yol(I))        :- kat_vektor(O), ri(O,I,_,_).
sinif(yol(I),alici_yolu) :- artefakt(yol(I)).
imzali(yol(I))          :- artefakt(yol(I)).
kanal(yol(I),aktarilan) :- artefakt(yol(I)).
% Yolun anahtarı: sınıfı sondanın kırılabilir kümesindeyse klasik (CRQC kırar), değilse PQ.
pqd(yol(I)) :- kat_vektor(O), yol_sinifi(O,I,C), kat_prob(P), not kirilabilir_etkin(P,C).
% Kenar: CEK <- geçerli alıcı yolu (Das V_i(t) = 1). Model farkı sondasında geçersiz sertifikalı yollar da.
kenar(e(I),cek,yol(I)) :- kat_vektor(O), ri(O,I,_,gecerli).
kenar(e(I),cek,yol(I)) :- kat_vektor(O), ri(O,I,_,gecersiz), kat_prob(tum_klasik_yol).

% ---------------------------------------------------------------- zaman ve senaryo (CRQC var: KAT-SPEC 'crqc.')
maruziyet_kat(cek,0).
maruziyet_kat(yol(I),0) :- artefakt(yol(I)).
kirilma_basi(A,E) :- maruziyet_kat(A,E), kat_qday(Q), E >= Q.
kirilma_basi(A,Q) :- maruziyet_kat(A,E), kat_qday(Q), E < Q.
pencere(A,W)      :- kirilma_basi(A,B), kat_now(N), W = N - B.
sayisal_param(tau). sayisal_param(saat_payi).
p_sayi(tau,T) :- kat_tau(T).
p_sayi(saat_payi,0).
param_alan(politika,p0). p(politika,p0).           % CMS'te varlık başına beklenti taşıyıcısı yok
param_alan(saldirgan,s2). p(saldirgan,s2).
param_alan(k_sinir,sinirsiz). p(k_sinir,sinirsiz).
