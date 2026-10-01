% =====================================================================
%  PQ-OID4VC | Adım 3 | HEDEFLER G1–G5 (+ keşifsel G2i) — yalnız zemin olgular
% =====================================================================
%  Ön kayıt §4.7 (ASP karşılığı): ihlal(gX) = hedef artefaktın etkin sahteliği.
%  "Etkin sahte" = sahtelenebilir VE doğrulayıcıya ulaştırılabilir (kanal kuralı R3a).
%  hedef_artefakt(G,A) + hedef_kosul(G,A,P,V) (hepsi).
%  politika_ihlali(G,Id) + politika_ihlal_kosul(Id,P,V): politika parametresi hedefi
%  kriptografiden bağımsız olarak düşürür (Ö9; T178, T228, T247, T253).
% =====================================================================

% G1 claims unforgeability (T107, T046, T047, T038)
hedef_artefakt(g1,a07_kimlik).
% Type Metadata işleniyorsa: tip bütünlüğü; özetle bağlı değilse (pq(a06_tip) yok) yalnız HTTPS'e dayanır (T096-T101)
hedef_artefakt(g1,a06_tip). hedef_kosul(g1,a06_tip,tmd_isleme,var).

% G2 sunum sahtelenemezliği / holder binding (T212-T225, T219)
hedef_artefakt(g2,a10_kbjwt).
politika_ihlali(g2,pi_g2). politika_ihlal_kosul(pi_g2,cihaz_bagi,yok).                 % T228

% G3 iptal sağlamlığı (T151-T156, T172, T176) — durum listesi yoksa (T175) iptal süre dolumuyla
hedef_artefakt(g3,a08_durum).
politika_ihlali(g3,pi_g3). politika_ihlal_kosul(pi_g3,iptal_denetimi,yok).             % T178
                           politika_ihlal_kosul(pi_g3,durum_listesi,var).

% G4 RP kimlik doğrulaması (cüzdan tarafı) (T240, T241, T244-T248, T268)
hedef_artefakt(g4,a12_istek).
politika_ihlali(g4,pi_g4). politika_ihlal_kosul(pi_g4,rp_auth_fail_open,var).          % T247, T253

% G2i (KEŞİFSEL; ön kayıtta yok): ihraç tarafı cüzdan/cihaz güvencesi (WIA/KA; T199, T203, T204)
hedef_artefakt(g2i,a09a_wia). hedef_artefakt(g2i,a09b_ka). hedef_artefakt(g2i,a09c_ornek).

ana_hedef(g1). ana_hedef(g2). ana_hedef(g3). ana_hedef(g4).
