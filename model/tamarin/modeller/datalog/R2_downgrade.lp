% R2 downgrade — Tamarin modeli: ../R2_downgrade.spthy
% Göç etmiş ihraççının kimlik bilgisi: PQ yolu var, anahtarları doğrulayıcıya
% özgün biçimde ulaşıyor (zincir yok).
link(cred). pq(cred). anchored(cred).
coexist(cred) :- not flag(no_coexist).

% cfg: kimliği doğrulanmış bant dışı yapılandırma -> sahtelenemez halka
link(cfg). pq(cfg). anchored(cfg).
% net: kimliği doğrulanmamış alan (yetenek müzakeresi, M-a) -> sahtelenebilir
% (PQ koruması yok; S1 bile değiştirebilir)
link(net). anchored(net).

convey(cfg, cred) :- flag(expect_auth).
convey(net, cred) :- flag(expect_unauth), not flag(expect_auth).

violated(g1) :- forgeable(cred).
violated(g5) :- coexist(cred), not expected(cred).
