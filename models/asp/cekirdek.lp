% =====================================================================
%  PQ-OID4VC | Adım 3 | ASP SİSTEM MODELİ — ÇEKİRDEK SEMANTİK
% =====================================================================
%  Pilot P2 / Tamarin datalog çekirdeğinin (K1-K4) genellemesi:
%    K1  forgeable(L) :- classical(L).                       -> basar(S,A) :- kirilir(S,A).   (+ zaman)
%    K2  forgeable(L) :- signed_under(L,P), forgeable(P),    -> basar(S,A) :- kabul_alti(A,B), etkin_sahte(S,B),
%                        not anchored(L).                                      not sabit_etkin(A).   (her kabul yolu)
%    K3  expected(X) :- convey(C,X), not forgeable(C).       -> beklenir(S,X) :- tasi(C,X), ... not etkin_sahte(S,C).
%    K4  forgeable(L) :- pq(L), coexist(L), not expected(L). -> basar(S,A) :- kirilir_alt(S,A), not beklenir(S,A). (+ zaman)
%  Yenilikler:
%   (i)  any-valid-path / anahtar sınıfı: A'nın imzacısını tanıtan HER kabul edilen artefakt bir
%        OR-kenarıdır; sahte(B) "saldırgan B-sınıfından doğrulayıcının kabul edeceği keyfi içerikli
%        bir örnek üretebilir" demektir (Tamarin R1 X_alt_ca; RFC 5280 §6.2; RFC 6840 §5.11).
%   (ii) zaman: klasik anahtar ancak τ < W_güven + saat_payı iken kırılır (pencereler.lp; Ö1 H2′).
%   (iii) kanal: sahte = basar ∧ ulasir. Çekilen/yalnız-taşıma artefakt yalnız taşımanın sunucu
%        kimlik doğrulaması sahtelenebiliyorsa ulaştırılır (R3a, H1). Aktarılan, sunan-uç ve
%        kimliksiz kanallar her zaman ulaştırır. Sabitlenmiş hiç ulaştırmaz.
%   (iv) varyantlar (M-b0 imzasızlaştırma vb.): A'nın imzasız biçimi kabul ediliyorsa (ve varlık
%        için beklenti yoksa) A'nın tüketimi o biçimin sahteliğini de devralır.
%   (v)  kırılma senaryoları: S = 'tum' (k sınırsız: her anahtar kırılabilir), 'bos' (S1: hiçbiri),
%        ya da sürücünün ürettiği k-altkümeleri (Ö8 k ∈ {1,3}); anahtar kimlikleri A | alt(A) | p3_kanal.
%  Semantik her S için tabakalıdır (artefakt bağımlılık grafiği döngüsüz; z3 kodlaması denetler).
% =====================================================================

% ---------------------------------------------------------------- parametre denetimi
parametre_hatasi(P) :- p(P,V), not param_alan(P,V).
parametre_hatasi(P) :- param_alan(P,_), not p_var(P).
p_var(P) :- p(P,_).
parametre_hatasi(P) :- p(P,V1), p(P,V2), V1 < V2.
parametre_hatasi(P) :- sayisal_param(P), not p_sayi_var(P).
p_sayi_var(P) :- p_sayi(P,_).
tau_s(T) :- p_sayi(tau,T).
saat_payi_s(Y) :- p_sayi(saat_payi,Y).

% ---------------------------------------------------------------- varlık, kenar, kanal
yok(A) :- var_kosul(A,P,V), not p(P,V).
mevcut(A) :- artefakt(A), not yok(A).

karar_etkin(A) :- karar(A), mevcut(A).
karar_etkin(A) :- karar_kosullu(A,P,V), p(P,V), mevcut(A).

kenar_pasif(E) :- kenar_kosul(E,P,V), not p(P,V).
kenar_pasif(E) :- kenar_kosul_degil(E,P,V), p(P,V).
kabul_alti(A,B) :- kenar(E,A,B), not kenar_pasif(E), mevcut(A), mevcut(B).

kanal_kosullu_var(A) :- kanal_kosullu(A,_,_,_).
kanal_etkin(A,K) :- kanal(A,K), mevcut(A), not kanal_kosullu_var(A).
kanal_etkin(A,K) :- kanal_kosullu(A,K,P,V), p(P,V), mevcut(A).
tasima_kosullu_var(A) :- tasima_kosullu(A,_,_,_).
tasima_etkin(A,T) :- tasima(A,T), mevcut(A), not tasima_kosullu_var(A).
tasima_etkin(A,T) :- tasima_kosullu(A,T,P,V), p(P,V), mevcut(A).
sabit_etkin(A) :- sabit(A), mevcut(A).
sabit_etkin(A) :- sabit_kosullu(A,P,V), p(P,V), mevcut(A).

% ---------------------------------------------------------------- karar düğümleri (§2C: 17 düğüm) ve PQ
% dugum_e(A,D): etkin karar artefaktı A, D düğümünün kararına bağlıdır (dugum/2 yoksa A kendi düğümüdür).
% Karar atomu pqd(D) (secim.lp); artefakt düzeyi pq(A) türetilir (aynı düğüm = birlikte göç).
dugum_tanimli(A) :- dugum(A,_).
dugum_e(A,D) :- dugum(A,D), karar_etkin(A).
dugum_e(A,A) :- karar_etkin(A), not dugum_tanimli(A).
karar_dugumu_etkin(D) :- dugum_e(_,D).
pq(A) :- pqd(D), dugum_e(A,D).
pq(A) :- pqd(A), mevcut(A), not karar_etkin(A).       % regresyon örnekleri: karar dışı artefakta sabit atama
pq(A) :- pq_kosullu(A,P,V), p(P,V), mevcut(A).
pq(A) :- ayni_anahtar(A,B), pq(B), mevcut(A).

% ---------------------------------------------------------------- faz: klasik alternatif
klasik_alt(A) :- p(faz,f1), karar_etkin(A).
klasik_alt(A) :- p(faz,f2), karar_etkin(A), sinif(A,C), yaprak_sinif(C).
klasik_alt(A) :- klasik_alt_zorla(A,P,V), p(P,V), mevcut(A).

% ---------------------------------------------------------------- kırılma senaryoları
senaryo(tum) :- p(saldirgan,s2), p(k_sinir,sinirsiz).
senaryo(bos) :- p(saldirgan,s1).
anahtar_adayi(A)      :- imzali(A), mevcut(A).
anahtar_adayi(alt(A)) :- imzali(A), mevcut(A).
anahtar_adayi(p3_kanal).
kir_izin(tum,K) :- senaryo(tum), anahtar_adayi(K).
% sonlu k: sürücü senaryo(sN) ve kir_izin(sN,K) olgularını verir.

zaman_uygun(A) :- pencere(A,W), tau_s(T), saat_payi_s(Y), T < W + Y.
kirilir(S,A)     :- senaryo(S), kir_izin(S,A), imzali(A), mevcut(A), not pq(A), zaman_uygun(A).
kirilir_alt(S,A) :- senaryo(S), kir_izin(S,alt(A)), imzali(A), mevcut(A), pq(A), klasik_alt_s(S,A), zaman_uygun(A).
p3_kirik(S)      :- senaryo(S), kir_izin(S,p3_kanal), pencere_p3(W), tau_s(T), saat_payi_s(Y), T < W + Y.

klasik_alt_s(S,A) :- senaryo(S), klasik_alt(A).
% Φ3 gün batımı iptalle uygulanıyorsa, sahte CRL eski klasik RP sertifikasını yeniden açar (dot #14 kancası)
klasik_alt_s(S,a12_istek) :- p(faz,f3), p(gun_batimi,iptal), etkin_sahte(S,e_crl), mevcut(a12_istek), karar_etkin(a12_istek).

% ---------------------------------------------------------------- beklenti (convey kancası = tasi/2)
tasiyici_pasif(C,X) :- tasiyabilir_kosul(C,X,P,V), not p(P,V).
tasiyabilir_etkin(C,X,M) :- tasiyabilir(C,X,M), mevcut(C), mevcut(X), not tasiyici_pasif(C,X).
beklenti_politikasi :- p(politika,p3).
beklenti_politikasi :- p(politika,p4).

% M-h: sertifika ekindeki taahhüt ancak C, X'in bütün kabul edilen tanıtım yollarına baskınsa
% (alternatif CA / JVI yolu yoksa) ve klasik alternatifin de yolundaysa (ortak_ata) etkilidir.
mh_aday(C) :- tasiyabilir_etkin(C,_,m_h).
tanitici_var(A) :- kabul_alti(A,_).
kok(A) :- mevcut(A), sabit_etkin(A).
kok(A) :- mevcut(A), not tanitici_var(A).
kacinir(A,C) :- mh_aday(C), kok(A), A != C.
kacinir(A,C) :- mh_aday(C), kabul_alti(A,B), not sabit_etkin(A), kacinir(B,C), A != C.
baskin(C,X) :- tasiyabilir_etkin(C,X,m_h), not kacinir(X,C).
mekanizma_uygun(C,X) :- tasiyabilir_etkin(C,X,M), M != m_h.
mekanizma_uygun(C,X) :- tasiyabilir_etkin(C,X,m_h), baskin(C,X), ortak_ata(C,X).

% M-f bileşen kancaları (A3; Adım 7): tazelik ve tekdüzelik birlikte yoksa eski sürüm geri oynatılır;
% varlık başına kapsam yoksa birlikte yaşamada (eski varlıklar varken) beklenti kurulamaz.
geri_alinir(C) :- tasiyabilir_etkin(C,_,_), mf_kapali(tazelik), mf_kapali(tekduzelik).
kapsam_engeli :- mf_kapali(kapsam), p(faz,f1).
kapsam_engeli :- mf_kapali(kapsam), p(faz,f2).

beklenir(S,X) :- senaryo(S), tasi(C,X), mekanizma_uygun(C,X), p(politika,p4),
                 not etkin_sahte(S,C), not geri_alinir(C), not kapsam_engeli.
beklenir(S,X) :- senaryo(S), tasi(C,X), mekanizma_uygun(C,X), p(politika,p3),
                 not etkin_sahte(S,C), not p3_kirik(S), not geri_alinir(C), not kapsam_engeli.

% ---------------------------------------------------------------- basım (içerik üretebilme)
basar(S,A) :- kirilir(S,A).                                                        % K1 (zamanlı)
basar(S,A) :- senaryo(S), kabul_alti(A,B), etkin_sahte(S,B), not sabit_etkin(A).  % K2 (herhangi bir kabul yolu)
basar(S,A) :- kirilir_alt(S,A), not beklenir(S,A).                                % K4 (zamanlı)
basar(S,A) :- senaryo(S), imzasiz(A), mevcut(A), not pq(A).                         % bağlanmamış imzasız içerik
basar(S,A) :- senaryo(S), imzasiz(A), mevcut(A), pq(A), klasik_alt_s(S,A),
              not beklenir(S,A).                                                    % PQ-bağlı, ama bağsız biçim de kabul (birlikte yaşama)

% ---------------------------------------------------------------- ulaştırma (kanal)
tasima_sahte(S,T) :- tasima_anahtari(T,A), etkin_sahte(S,A).
ulasir(S,A) :- senaryo(S), kanal_etkin(A,aktarilan).
ulasir(S,A) :- senaryo(S), kanal_etkin(A,sunan_uc).
ulasir(S,A) :- senaryo(S), kanal_etkin(A,kimliksiz).
ulasir(S,A) :- kanal_etkin(A,cekilen),       tasima_etkin(A,T), tasima_sahte(S,T).
ulasir(S,A) :- kanal_etkin(A,yalniz_tasima), tasima_etkin(A,T), tasima_sahte(S,T).

ozgun(A) :- ozgun_kosullu(A,P,V), p(P,V), mevcut(A).
ozgun(A) :- onbellekli(A), mevcut(A), p(capa,onbellek), p(onbellek_ufku,ilk_pencere).

sahte(S,A) :- basar(S,A), ulasir(S,A), not ozgun(A).
% PQ-bağlı imzasız artefakt (A06 özet, E_JVI, E_AS): sahteliği bağlandığı artefaktınkine eşittir
sahte(S,A) :- senaryo(S), imzasiz(A), pq(A), pq_baglar(A,B), etkin_sahte(S,B), not ozgun(A).

% ---------------------------------------------------------------- varyantlar ve etkin sahtelik
varyant_pasif(A,Av) :- varyant_kosul(A,Av,P,V), not p(P,V).
varyant_etkin(S,A,Av) :- senaryo(S), varyant(A,Av), mevcut(A), mevcut(Av),
                         not varyant_pasif(A,Av), not beklenir(S,A).
etkin_sahte(S,A) :- sahte(S,A).
etkin_sahte(S,A) :- varyant_etkin(S,A,Av), sahte(S,Av).

% ---------------------------------------------------------------- hedefler
hedef_pasif(G,A) :- hedef_kosul(G,A,P,V), not p(P,V).
hedef_etkin(G,A) :- hedef_artefakt(G,A), mevcut(A), not hedef_pasif(G,A).
pi_pasif(I) :- politika_ihlal_kosul(I,P,V), not p(P,V).
ihlal(S,G) :- senaryo(S), hedef_etkin(G,A), etkin_sahte(S,A).
ihlal(S,G) :- senaryo(S), politika_ihlali(G,I), not pi_pasif(I).
ihlal(S,tum) :- ihlal(S,G), ana_hedef(G).

% G5 (zamansız; Ö11): hedeflerin yolundaki göç etmiş (pq) varlık, klasik alternatifi açık ve
% kimliği doğrulanmış beklentisi yokken yalnız klasik kanıtla (ya da imzasız biçimle) kabul edilir.
g5_kapsam(G) :- sorgu_hedef(G), ana_hedef(G).
g5_kapsam(G) :- sorgu_hedef(tum), ana_hedef(G).
g5_kapsam(G) :- sorgu_hedef(g5), ana_hedef(G).
g5_kapsam(G) :- g5_degerlendir(G).
yolda(S,A)  :- senaryo(S), g5_kapsam(G), hedef_etkin(G,A).
yolda(S,B)  :- yolda(S,A), kabul_alti(A,B).
yolda(S,Av) :- yolda(S,A), varyant_etkin(S,A,Av).
yolda(S,C)  :- yolda(S,X), tasi(C,X), tasiyabilir_etkin(C,X,_), beklenti_politikasi.
yolda(S,K)  :- yolda(S,A), tasima_etkin(A,T), tasima_anahtari(T,K).
ihlal(S,g5) :- yolda(S,A), karar_etkin(A), pq(A), klasik_alt_s(S,A), not beklenir(S,A).
ihlal(S,g5) :- yolda(S,A), karar_etkin(A), pq(A), varyant_etkin(S,A,_).
