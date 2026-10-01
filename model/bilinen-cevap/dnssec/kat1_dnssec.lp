% =====================================================================
%  PQ-OID4VC | Adım 6 | KAT-1 DNSSEC — ÖRNEK DOSYASI (çekirdek DIŞI)
% =====================================================================
%  Koşum: model/asp/cekirdek.lp + bu dosya + ornekler/<hücre>.lp  (başka hiçbir dosya yok;
%  olgular/*.lp, secim.lp, sorgu.lp YÜKLENMEZ). Okuma kuralı: SALDIRI <=> ihlal(tum,g1).
%  Kaynak: KAT-SPEC §2(a)–(d) (literatur/analiz/KAT-SPEC.md); RFC 6840 §5.11, §6.2, Ek C.2;
%  RFC 6781 §4.1.4 (Şekil 8) ve §4.3.4. Eşlemenin gerekçesi: ../ESLEME.md §2.
%
%  Bu dosyada çekirdek kuralı YOKTUR. İçerik:
%   (A) DNSSEC sürüm tablosu (KAT-SPEC §2(b) kat1_dnssec.lp ile aynı sayılar);
%   (B) ekosistem türetmesi: doğrulayıcının 'now' anında kabul ettiği sürümler (imza geçerliliği,
%       tekdüzelik) ve bu sürümlerde hangi anahtar sınıflarının listeli olduğu;
%   (C) çekirdeğin sözlüğüyle artefaktlar, kanal, kenarlar, PQ/klasik alternatif, politika, beklenti,
%       zaman penceresi ve kırılma senaryosu.
%  Hücre sabitleri (ornekler/K1-XX.lp; uret.py üretir):
%    kat_asama(r2|r3|r5|dds). kat_politika(anyvalid|allpresent|required). kat_now(N). kat_qday(Q).
%    kat_tau(T). kat_tekduze(0|1). kat_ust_sinif(pq|cl). kat_ek_capa(0|1). kat_mutasyon(M) (KAT-SPEC §6).
% =====================================================================

% ---------------------------------------------------------------- (A) sürüm tablosu
% surum(I,V,Bas,Son): I artefaktının V sürümü; imzası [Bas,Son] aralığında geçerli.
surum(ds,1,0,200)    :- kat_asama(r2).                    % güncel DS: yalnız klasik KSK
surum(ds,1,0,S)      :- kat_asama(r3), eski_son(60,S).    % eski DS: imzası t=60'ta biter (yeniden oynatılabilir)
surum(ds,1,0,S)      :- kat_asama(r5), eski_son(60,S).
surum(ds,2,40,200)   :- kat_asama(r3).                    % yeni DS: yalnız PQ KSK (t=40'ta yayımlandı)
surum(ds,2,40,200)   :- kat_asama(r5).
surum(ds,12,0,200)   :- kat_asama(dds).                   % liberal çift-DS
surum(dnskey,3,20,S) :- eski_son(120,S).                  % her iki algoritma (new DNSKEY … new DS)
surum(dnskey,5,90,300) :- kat_asama(r5).                  % eski anahtarlar çıkarıldı (yalnız PQ)
% KAT-SPEC §6 mutasyonu "eski sürüm geçerliliğini uzat (Exp=∞)": eski sürümlerin imzası süresiz geçerli.
eski_son_aday(60). eski_son_aday(120).
eski_son(E,E)          :- eski_son_aday(E), not kat_mutasyon(eski_surum_suresiz).
eski_son(E,1000000000) :- eski_son_aday(E), kat_mutasyon(eski_surum_suresiz).

% listeler(I,V,K): I'nin V sürümü K anahtarını listeler (DS -> KSK; DNSKEY RRset -> bölgenin anahtarları)
listeler(ds,1,ksk_cl). listeler(ds,2,ksk_pq). listeler(ds,12,ksk_cl). listeler(ds,12,ksk_pq).
listeler(dnskey,3,ksk_cl). listeler(dnskey,3,ksk_pq). listeler(dnskey,3,zsk_cl). listeler(dnskey,3,zsk_pq).
listeler(dnskey,5,ksk_pq). listeler(dnskey,5,zsk_pq).
anahtar_sinifi(ksk_cl,cl). anahtar_sinifi(zsk_cl,cl). anahtar_sinifi(ksk_pq,pq). anahtar_sinifi(zsk_pq,pq).
% goruldu(I,V): doğrulayıcının gördüğü en yeni sürüm (yalnız kat_tekduze(1) iken etkili; KAT-SPEC seen/2)
goruldu(ds,2) :- kat_asama(r3). goruldu(ds,2) :- kat_asama(r5). goruldu(dnskey,5) :- kat_asama(r5).

% ---------------------------------------------------------------- (B) 'now' anındaki kabul
gecerli(I,V)     :- surum(I,V,Bas,Son), kat_now(N), Bas <= N, N <= Son.   % imza now'da geçerli
reddedilir(I,V)  :- gecerli(I,V), kat_tekduze(1), goruldu(I,V2), V < V2.   % tekdüze: geri dönmez
kabul_surum(I,V) :- gecerli(I,V), not reddedilir(I,V).
% listeli(I,C): kabul edilen bir I sürümünde C sınıfından anahtar var. DNSKEY RRset için bu, RFC 6840
% §6.2'nin kenar semantiğidir: RRset'teki HERHANGİ bir anahtar bölgedeki HERHANGİ bir RRset'i doğrular.
listeli(I,C) :- kabul_surum(I,V), listeler(I,V,K), anahtar_sinifi(K,C).

% ---------------------------------------------------------------- (C) çekirdek sözlüğü
% Artefaktlar. Hepsi DNS'ten ÇEKİLEN; DNS taşımasının kimliği doğrulanmamıştır (dns_yaniti: kimliksiz,
% imzasız => taşıma her zaman sahtelenebilir; H1 tipi ikame mümkün değil — KAT-SPEC §1.1 sağlık notu).
artefakt(ds).     sinif(ds,ds_rrset).         kanal(ds,cekilen).     tasima(ds,dns).
artefakt(dnskey). sinif(dnskey,dnskey_rrset). kanal(dnskey,cekilen). tasima(dnskey,dns).
artefakt(a_rr).   sinif(a_rr,a_rrset).        kanal(a_rr,cekilen).   tasima(a_rr,dns).   imzali(a_rr).
artefakt(dns_yaniti). sinif(dns_yaniti,dns_tasimasi). imzasiz(dns_yaniti). kanal(dns_yaniti,kimliksiz).
tasima_anahtari(dns,dns_yaniti).
% DS'yi imzalayan üst bölge anahtarı güven çapasıdır (anchored(kp,ds)) => sabit.
sabit(ds).
imzali(ds)      :- not kat_mutasyon(ds_imza_denetimi_yok).
imzasiz(ds)     :- kat_mutasyon(ds_imza_denetimi_yok).       % §6: DS imza denetimi silindi
imzali(dnskey)  :- not kat_mutasyon(ds_ksk_eslesmesi_yok).
imzasiz(dnskey) :- kat_mutasyon(ds_ksk_eslesmesi_yok).       % §6: DS–KSK eşleşmesi silindi (her KSK kabul)
% Kenarlar (any-valid-path): DNSKEY RRset'in imzacısı (KSK) DS'ten; A RRset'in imzacısı DNSKEY RRset'ten.
kenar(e_ds_ksk,dnskey,ds).
kenar(e_dnskey_anahtar,a_rr,dnskey).
hedef_artefakt(g1,a_rr). ana_hedef(g1).

% PQ ve klasik alternatif: imzalayan anahtar sınıfı, kabul edilen sürümlerde listeli anahtarlardan.
param_alan(kat,evet). p(kat,evet).                            % klasik_alt_zorla/3 için sabit koşul
pqd(ds)     :- kat_ust_sinif(pq), not kat_mutasyon(ds_imza_denetimi_yok).
pqd(dnskey) :- listeli(ds,pq), not kat_mutasyon(ds_ksk_eslesmesi_yok).
klasik_alt_zorla(dnskey,kat,evet) :- pqd(dnskey), listeli(ds,cl).     % DS klasik KSK'yı da gösteriyor
klasik_alt_zorla(dnskey,kat,evet) :- pqd(dnskey), kat_ek_capa(1).     % RFC 6840 Ek C.2: eski klasik KSK çapa
pqd(a_rr)   :- listeli(dnskey,pq).
klasik_alt_zorla(a_rr,kat,evet)   :- pqd(a_rr), listeli(dnskey,cl).   % §6.2: klasik anahtar RRset'te

% Politika (KAT-SPEC §1.1 eşlemesi): anyvalid = P0 (RFC 6840 varsayılanı); allpresent = "varsa denetle";
% required = imza bütünlüğü testi (RFC 6840 §5.11 MAY seçeneği), beklenti kaynağı DS.
param_alan(politika,p0). param_alan(politika,p4).
p(politika,p0) :- kat_politika(anyvalid).
p(politika,p4) :- kat_politika(allpresent).
p(politika,p4) :- kat_politika(required).

% allpresent ("varsa denetle"): PQ imzasının VARLIĞI beklenti taşır. DNS yanıtındaki RRSIG kümesi hiçbir
% imzayla korunmaz => taşıyıcı kimliksiz; saldırgan PQ RRSIG'ini soyar (RFC 9955 §6.2).
p1_kapsam(dnskey,pqvar_dnskey). p1_kapsam(a_rr,pqvar_a_rr).
artefakt(C)          :- kat_politika(allpresent), p1_kapsam(_,C).
sinif(C,oz_sinyal)   :- kat_politika(allpresent), p1_kapsam(_,C).
imzasiz(C)           :- kat_politika(allpresent), p1_kapsam(_,C).
kanal(C,kimliksiz)   :- kat_politika(allpresent), p1_kapsam(_,C).
tasiyabilir(C,X,m_a) :- kat_politika(allpresent), p1_kapsam(X,C).
tasi(C,X)            :- kat_politika(allpresent), p1_kapsam(X,C).

% required (bütünlük testi): DS'nin işaretlediği her algoritma zincirde (DNSKEY RRset ve A RRset)
% doğrulanmalı. Beklenti taşıyıcısı = güncel DS (üst bölge imzalı; M-f sınıfı "kimliği doğrulanmış kaynak").
ds_pq_isaret(V)       :- listeler(ds,V,K), anahtar_sinifi(K,pq).
daha_yeni_kabul(I,V)  :- kabul_surum(I,V), kabul_surum(I,V2), V < V2.
guncel_ds(V)          :- kabul_surum(ds,V), not daha_yeni_kabul(ds,V).
bt_beklenti           :- kat_politika(required), guncel_ds(V), ds_pq_isaret(V).
bt_kapsam(dnskey). bt_kapsam(a_rr).
tasiyabilir(ds,X,m_f) :- bt_beklenti, bt_kapsam(X).
tasi(ds,X)            :- bt_beklenti, bt_kapsam(X).
% Yeniden oynatma (RFC 6781 §4.3.4): PQ'yu işaretlemeyen eski bir DS sürümünün imzası 'now' anında hâlâ
% geçerliyse tazelik yoktur; doğrulayıcı tekdüze değilse tekdüzelik de yoktur. Çekirdeğin M-f kancası
% (geri_alinir) ikisi birlikte yoksa taşıyıcının beklentisini geri alır.
mf_kapali(tazelik)    :- bt_beklenti, gecerli(ds,V), not ds_pq_isaret(V).
mf_kapali(tekduzelik) :- kat_tekduze(0).

% Zaman (CRQC-TAKVIMI §1: max(T0,qday)+τ ≤ T1). Doğrulama anı T1 = now; bütün anahtarlar durağan
% (exposure T0 = 0; KAT-SPEC §2(d)). Çekirdek: τ < W + saat_payi, W = now − max(T0,qday), pay = 0.
maruziyet_kat(ds,0). maruziyet_kat(dnskey,0). maruziyet_kat(a_rr,0).
kirilma_basi(A,E) :- maruziyet_kat(A,E), kat_qday(Q), E >= Q.
kirilma_basi(A,Q) :- maruziyet_kat(A,E), kat_qday(Q), E < Q.
pencere(A,W)      :- kirilma_basi(A,B), kat_now(N), W = N - B.
sayisal_param(tau). sayisal_param(saat_payi).
p_sayi(tau,T) :- kat_tau(T).
p_sayi(saat_payi,0).

% Kırılma senaryosu: S2, k sınırsız (CRQC'nin kırabildiği her klasik anahtar; zaman koşuluyla).
param_alan(saldirgan,s2). p(saldirgan,s2).
param_alan(k_sinir,sinirsiz). p(k_sinir,sinirsiz).
