% Migration ordering: given a target PQ set and conveyance channels, choose an order
% (one migration per step) maximising the number of "effective" migrations over time
% (a migrated artefact is effective at step T if it is no longer forgeable at T).
% base facts are prepended by the driver

n(N) :- N = #count { L : target_pq(L) }.
time(1..N) :- n(N).
1 { step(L,T) : time(T) } 1 :- target_pq(L).
:- time(T), 2 { step(L,T) : target_pq(L) }.

pq_at(L,T) :- step(L,T0), time(T), T0 <= T.
classical_at(L,T) :- link(L), time(T), not pq_at(L,T).
forg(L,T) :- classical_at(L,T).
forg(L,T) :- signed_under(L,P), forg(P,T), not anchored(L).
exp_at(X,T) :- conv(C,X), time(T), not forg(C,T).
forg(L,T) :- pq_at(L,T), coexist(L), not exp_at(L,T).

effective(L,T) :- pq_at(L,T), not forg(L,T).
#maximize { 1,L,T : effective(L,T) }.
#show step/2.
