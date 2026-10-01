% =====================================================================
%  PQ-OID4VC | Adım 3 | SEÇİM: karar düğümleri ve alt küme bakımından asgari kümeler
% =====================================================================
%  Kullanım: clingo 0 --heuristic=Domain --enum-mode=domRec  (pilot P2 ile aynı; §7.9; §2C 2.2 "tam sayım")
%  Karar atomları: pqd(D) (D düğümünün imzalayan anahtar(lar)ı PQ; §2C: 17 düğüm) ve tasi(C,X)
%  (C, X için beklenti taşır). Asgari küme = hedefi sağlayan (pqd ∪ tasi) kümelerinin alt küme
%  bakımından en küçükleri. Çıktıda düğüm atomları pq(D) olarak gösterilir.
% =====================================================================
{ pqd(D) : karar_dugumu_etkin(D) }.
{ tasi(C,X) : tasiyabilir_etkin(C,X,_) } :- beklenti_politikasi.
:- pqd(D), dugum_e(A,D), pq_yasak(A,P,V), p(P,V).         % ör. WebPKI klasikken A13 PQ olamaz
:- pqd(D), dugum_e(A,D), wscd_artefakt(A), p(wscd_pq,yok). % WSCD donanımı PQ desteklemiyor (M5; pilot 'wscd=p256')
#heuristic pqd(D) : karar_dugumu_etkin(D). [1,false]
#heuristic tasi(C,X) : tasiyabilir_etkin(C,X,_), beklenti_politikasi. [1,false]
#show pq(D) : pqd(D).
#show tasi/2.
