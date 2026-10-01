% Sorgu kısıtı: sorgulanan hedef hiçbir kırılma senaryosunda çiğnenmemeli.
% sorgu_hedef(G), G ∈ {g1,g2,g3,g4,tum,g5,g2i} sürücü tarafından verilir (birden çok olabilir).
:- sorgu_hedef(G), senaryo(S), ihlal(S,G).
:- parametre_hatasi(_).
