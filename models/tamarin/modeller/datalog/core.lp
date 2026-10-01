% =====================================================================
%  PQ-OID4VC | Adım 4 | Katman 1 <-> Katman 2 bağı: Datalog/ASP çekirdeği
% =====================================================================
%  Pilot P2 ile aynı dört kural (referans/denetim/denetim-B §3.3).
%  Anlam (Q-day sonrası, CRQC saldırganı):
%    pq(L)            L'yi İMZALAYAN anahtar PQ'dur (CRQC çıkaramaz).
%    classical(L)     L'yi imzalayan anahtar klasiktir.
%    signed_under(L,P) L'yi imzalayan anahtar P tarafından doğrulanır (bağlanır).
%    anchored(L)      L'yi imzalayan anahtar bant dışı sabitlenmiştir.
%    convey(C,X)      X'e ilişkin "PQ zorunlu" beklentisi C kanalıyla taşınır.
%    coexist(L)       L'nin klasik ve PQ biçimi birlikte geçerlidir.
%
%  K1  forgeable(L) :- classical(L).                                   (R1, R4)
%  K2  forgeable(L) :- signed_under(L,P), forgeable(P), not anchored(L). (R1, R4, R5)
%  K3  expected(X)  :- convey(C,X), not forgeable(C).                  (R3, R2)
%  K4  forgeable(L) :- pq(L), coexist(L), not expected(L).             (R2)
%  G5 karşılığı (K4'ün gövdesi, "PQ" koşulu olmadan):
%      violated(g5) :- coexist(X), not expected(X).   -- örnek dosyalarında
%
%  Örnek dosyaları (R1_chain.lp ... R5_anchor.lp) flag/1 olgularını Tamarin
%  -D bayraklarıyla birebir aynı adlarla (küçük harf) alır.

classical(L) :- link(L), not pq(L).
forgeable(L) :- classical(L).                                        % K1
forgeable(L) :- signed_under(L,P), forgeable(P), not anchored(L).    % K2
expected(X)  :- convey(C,X), not forgeable(C).                       % K3
forgeable(L) :- pq(L), coexist(L), not expected(L).                  % K4

#show violated/1.
#show forgeable/1.
