% R3 kanal — Tamarin modeli: ../R3_channel.spthy
% Birlikte yaşama hep açık; beklenti tek bir kanalla (chan) taşınır.
link(cred). pq(cred). anchored(cred). coexist(cred).

% chan: beklenti kaynağının kimlik doğrulama anahtarı doğrulayıcıda sabitli.
% VIA_TLS (taşıma) ile nesne imzası arasında Datalog farkı yoktur: ikisi de
% convey(chan,cred) ve aynı anahtar türü. (H1: çekilen artefaktta ikame.)
link(chan). anchored(chan).
pq(chan) :- flag(chan_pq).
convey(chan, cred).

violated(g1) :- forgeable(cred).
violated(g5) :- coexist(cred), not expected(cred).
