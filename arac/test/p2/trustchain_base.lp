% Pilot P2 (toy, not the paper model): OpenID4VC/EUDI trust chain after Q-day.
% Minimal PQ migration set (+ expectation channels) = minimal hitting set of attack paths.

link(lotl; tl_pid; tl_wp; tl_rp; ca_iss; iss_cert; meta; cred; status; wua; kb; rp_cert; req).

% signed_under(A,B): A's signing key is authenticated by artefact B
signed_under(tl_pid,lotl). signed_under(tl_wp,lotl). signed_under(tl_rp,lotl).
signed_under(ca_iss,tl_pid). signed_under(iss_cert,ca_iss).
signed_under(cred,iss_cert). signed_under(meta,iss_cert). signed_under(status,iss_cert).
signed_under(wua,tl_wp). signed_under(kb,cred).
signed_under(rp_cert,tl_rp). signed_under(req,rp_cert).

% channels that could carry an authenticated "PQ required for this signer" expectation
can_convey(tl_pid,cred). can_convey(tl_pid,meta). can_convey(tl_pid,status).
can_convey(meta,cred). can_convey(meta,status). can_convey(ca_iss,cred).
can_convey(tl_rp,req). can_convey(rp_cert,req). can_convey(tl_wp,wua).

#const phase=coexist.   % coexist | post
#const wscd=p256.       % p256 | pq
#const anchor=lotl.     % lotl | pinned_tl
#const target=all.      % all | claims | holder | revocation | rp_auth | wscd_assurance

leaf(cred;meta;status;req;wua).
coexist(L) :- phase=coexist, leaf(L).  % dual issuance / multi-signed requests only
%(kb constraint moved)

