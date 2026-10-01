% R1 zincir — Tamarin modeli: ../R1_chain.spthy
% Zincir: kök (sabitlenmiş) -> ca_cert -> iss_cert -> cred
link(ca_cert; iss_cert; cred).
anchored(ca_cert).                 % ca_cert'i sabitlenmiş kök anahtarı imzalar
signed_under(iss_cert, ca_cert).   % iss_cert'i imzalayan CA anahtarını ca_cert bağlar
signed_under(cred, iss_cert).      % cred'i imzalayan ihraççı anahtarını iss_cert bağlar

pq(ca_cert) :- flag(root_pq).
pq(cred)    :- flag(iss_pq).

% pq(iss_cert): iss_cert'i imzalayan CA anahtarı PQ.
% EK (ALT_CA / NAME_BIND): doğrulayıcı aynı kök altındaki HER CA'nın imzaladığı
% iss_cert'i kabul ediyorsa, "pq(iss_cert)" ancak bu ihraççı için kabul edilen
% BÜTÜN imzacılar PQ ise doğrudur (sem=class). sem=naive yalnız gerçek ebeveyne
% bakar (pilotun örtük okuması); Tamarin ALT_CA varyantında bunu yanlışlar.
#const sem=class.
alt_acceptable :- flag(alt_ca), not flag(name_bind).
pq(iss_cert) :- flag(ca_pq), sem=naive.
pq(iss_cert) :- flag(ca_pq), not alt_acceptable, sem=class.

violated(g1) :- forgeable(cred).
