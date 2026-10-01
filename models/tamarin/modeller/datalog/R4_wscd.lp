% R4 WSCD — Tamarin modeli: ../R4_wscd.spthy
% cred: ihraççı imzası (ihraççı anahtarı doğrulayıcıda sabitli)
% kb  : KB-JWT; imzalayan cihaz anahtarını cred içindeki cnf bağlar
link(cred). anchored(cred).
pq(cred) :- flag(iss_pq).
link(kb). signed_under(kb, cred).
pq(kb)   :- flag(dev_pq).

% SINGLE_USE'un Datalog karşılığı yoktur (H5: tahmin değişmemeli).
violated(g2) :- forgeable(kb).
