:- pq(kb), wscd=p256.
{ pq(L) : link(L) }.
{ convey(C,X) : can_convey(C,X) }.
classical(L) :- link(L), not pq(L).

anchored(lotl).
anchored(tl_pid) :- anchor=pinned_tl.

% CRQC attacker after Q-day
forgeable(L) :- classical(L).
forgeable(L) :- signed_under(L,P), forgeable(P), not anchored(L).
expected(X)  :- convey(C,X), not forgeable(C).
forgeable(L) :- pq(L), coexist(L), not expected(L).

goal(claims;holder;revocation;rp_auth;wscd_assurance).
violated(claims)         :- forgeable(cred).
violated(holder)         :- forgeable(kb).
violated(revocation)     :- forgeable(status).
violated(rp_auth)        :- forgeable(req).
violated(wscd_assurance) :- forgeable(wua).

tgoal(G) :- goal(G), target=all.
tgoal(G) :- goal(G), G=target.
:- tgoal(G), violated(G).

% subset-minimal enumeration (use --heuristic=Domain --enum-mode=domRec)
#heuristic pq(L) : link(L). [1,false]
#heuristic convey(C,X) : can_convey(C,X). [1,false]

#show pq/1.
#show convey/2.
