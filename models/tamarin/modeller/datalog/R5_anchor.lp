% R5 çıpa — Tamarin modeli: ../R5_anchor.spthy
% Zincir: LOTL (anahtarı sabitli) -> tl (LOTL işaretçisi TL anahtarını bağlar) -> cred
link(lotl; tl; cred).
anchored(lotl).                    % LOTL imza anahtarı sabitli (ör. OJEU)
anchored(tl) :- flag(pin_tl).      % TL imza anahtarı bant dışı sabitlenmiş
signed_under(tl, lotl).
signed_under(cred, tl).
pq(lotl) :- flag(lotl_pq).
pq(tl)   :- flag(tl_pq).
pq(cred).                          % ihraççı anahtarı R5'te hep PQ

violated(g1) :- forgeable(cred).
