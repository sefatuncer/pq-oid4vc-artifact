"""Evidence-rule second attempt, SDJWT-018 (sd-jwt-python 0.10.4, jwcrypto 1.6.1).

Question: can the L4 policy be expressed through the documented public API
(SDJWTVerifier and its arguments) without changing library code and without
an own verification loop?

All keys and objects are generated here (own keys; no study vectors).
A = ES256, X = EdDSA (Ed25519).
"""
import json
import jwcrypto.jws
from jwcrypto.jwk import JWK, JWKSet
from sd_jwt.issuer import SDJWTIssuer
from sd_jwt.holder import SDJWTHolder
from sd_jwt.verifier import SDJWTVerifier
from sd_jwt.common import SDObj

MIG = "https://issuer.example"          # migrated issuer: R = {X}
LEG = "https://legacy-issuer.example"   # legacy issuer:   R = {} (ES256 accepted)

mig_es256 = JWK.generate(kty="EC", crv="P-256", kid="mig-es256")
mig_x = JWK.generate(kty="OKP", crv="Ed25519", kid="mig-eddsa")
leg_es256 = JWK.generate(kty="EC", crv="P-256", kid="leg-es256")


def pub(k):
    return JWK.from_json(k.export_public())


def keyset(*keys):
    s = JWKSet()
    for k in keys:
        s.add(pub(k))
    return s


# The verifier always receives the complete key set of each issuer.
ISSUER_KEYS = {MIG: keyset(mig_es256, mig_x), LEG: keyset(leg_es256)}


def issue(iss, key, alg, fmt="compact"):
    claims = {"iss": iss, "sub": "user-1", SDObj("given_name"): "Erika"}
    i = SDJWTIssuer(claims, key, sign_alg=alg, serialization_format=fmt,
                    extra_header_parameters={"kid": key["kid"]})
    return i


def present(issuance, fmt="compact"):
    h = SDJWTHolder(issuance, serialization_format=fmt)
    h.create_presentation({}, None, None, None)  # disclose nothing extra, no KB
    return h.sd_jwt_presentation


def corrupt_compact(p):
    jws, *rest = p.split("~")
    h, b, s = jws.split(".")
    s = ("A" if s[0] != "A" else "B") + s[1:]
    return "~".join([".".join([h, b, s])] + rest)


def run(label, presentation, cb, fmt="compact", expect=None):
    try:
        v = SDJWTVerifier(presentation, cb, serialization_format=fmt)
        v.get_verified_payload()
        res = "accept"
        detail = ""
    except Exception as e:  # report the exception class and first line
        res = "reject"
        detail = f"{type(e).__name__}: {str(e).splitlines()[0][:110]}"
    ok = "" if expect is None else ("OK" if res == expect else "MISMATCH")
    print(f"{label:<44} {res:<7} expect={expect or '-':<7} {ok:<8} {detail}")
    return res == expect if expect else None


# ---------------------------------------------------------------- callbacks
def cb_default(issuer, header_parameters):
    """Key resolution only (no policy): full key set of the issuer."""
    return ISSUER_KEYS[issuer]


# L4c: per-issuer policy records held in ONE configuration object, used by
# every SDJWTVerifier call (the library creates one verifier object per
# presentation; the shared configuration is the callback).
POLICY_L4C = {MIG: {"W": {"ES256", "EdDSA"}, "R": {"EdDSA"}},
              LEG: {"W": {"ES256", "EdDSA"}, "R": set()}}


def cb_l4c(issuer, header_parameters):
    rec = POLICY_L4C[issuer]                      # unknown issuer -> KeyError
    alg = header_parameters["alg"]                # protected header (compact)
    if alg not in rec["W"] or (rec["R"] and alg not in rec["R"]):
        raise ValueError(f"alg {alg} not acceptable for issuer {issuer}")
    return ISSUER_KEYS[issuer]


# L4m (supplementary; General JSON passes through to jwcrypto):
# R = {X}, W = {A, X}. The callback hands the library only the keys whose
# algorithm is in R; jwcrypto then verifies every signature (at-least-one).
POLICY_L4M = {MIG: {"R": {"EdDSA"}}}
KTY_ALG = {("EC", "P-256"): "ES256", ("OKP", "Ed25519"): "EdDSA"}


def cb_l4m(issuer, header_parameters):
    rec = POLICY_L4M[issuer]
    out = JWKSet()
    for k in ISSUER_KEYS[issuer]["keys"]:
        if KTY_ALG[(k["kty"], k["crv"])] in rec["R"]:
            out.add(k)
    return out


results = []
print("== sd-jwt", __import__("importlib.metadata").metadata.version("sd-jwt"),
      "jwcrypto", __import__("importlib.metadata").metadata.version("jwcrypto"))

print("\n== 1. Validity check (default callback, no policy)")
p_mig_es = present(issue(MIG, mig_es256, "ES256").sd_jwt_issuance)
p_mig_x = present(issue(MIG, mig_x, "EdDSA").sd_jwt_issuance)
p_leg_es = present(issue(LEG, leg_es256, "ES256").sd_jwt_issuance)
results.append(run("V+ migrated ES256", p_mig_es, cb_default, expect="accept"))
results.append(run("V+ migrated EdDSA", p_mig_x, cb_default, expect="accept"))
results.append(run("V+ legacy ES256", p_leg_es, cb_default, expect="accept"))
results.append(run("V- migrated ES256 (corrupted sig)", corrupt_compact(p_mig_es), cb_default, expect="reject"))
results.append(run("V- migrated EdDSA (corrupted sig)", corrupt_compact(p_mig_x), cb_default, expect="reject"))

print("\n== 2. Native options only (no caller policy logic)")
print("SDJWTVerifier.__init__ parameters:",
      list(SDJWTVerifier.__init__.__code__.co_varnames[1:SDJWTVerifier.__init__.__code__.co_argcount]))
saved = list(jwcrypto.jws.default_allowed_algs)
jwcrypto.jws.default_allowed_algs[:] = ["EdDSA"]   # module-global allow-list (L1 at most)
print("global jwcrypto.jws.default_allowed_algs = ['EdDSA']:")
run("  migrated ES256 (L4c wants reject)", p_mig_es, cb_default, expect="reject")
run("  migrated EdDSA (L4c wants accept)", p_mig_x, cb_default, expect="accept")
run("  legacy ES256 (L4c wants accept)", p_leg_es, cb_default, expect="accept")
jwcrypto.jws.default_allowed_algs[:] = saved
print("-> a global list cannot separate the two issuers (legacy ES256 is rejected).")

print("\n== 3. L4c through the documented key-resolution callback (one shared policy configuration)")
results.append(run("L4c migrated ES256", p_mig_es, cb_l4c, expect="reject"))
results.append(run("L4c migrated EdDSA", p_mig_x, cb_l4c, expect="accept"))
results.append(run("L4c legacy ES256", p_leg_es, cb_l4c, expect="accept"))
results.append(run("L4c migrated EdDSA corrupted (still reject)", corrupt_compact(p_mig_x), cb_l4c, expect="reject"))
# header alg is integrity-protected: relabel the ES256 object as EdDSA -> must fail
h, b, s = p_mig_es.split("~")[0].split(".")
hd = json.loads(jwcrypto.common.base64url_decode(h)); hd["alg"] = "EdDSA"
h2 = jwcrypto.common.base64url_encode(json.dumps(hd))
relabel = "~".join([".".join([h2, b, s])] + p_mig_es.split("~")[1:])
results.append(run("L4c migrated ES256 relabelled alg=EdDSA", relabel, cb_l4c, expect="reject"))

print("\n== 4. Supplementary L4m (General JSON, two signatures) through the same callback mechanism")
iss_j = issue(MIG, mig_es256, "ES256", fmt="json")
jws_obj = iss_j.sd_jwt


# Construct signatures with jwcrypto directly (test-object generation only).
payload = json.dumps(iss_j.sd_jwt_payload)
both = jwcrypto.jws.JWS(payload=payload)
both.add_signature(mig_es256, alg="ES256", protected=json.dumps({"alg": "ES256", "typ": "example+sd-jwt", "kid": "mig-es256"}))
both.add_signature(mig_x, alg="EdDSA", protected=json.dumps({"alg": "EdDSA", "typ": "example+sd-jwt", "kid": "mig-eddsa"}))
gj = json.loads(both.serialize(compact=False))
discl = [d.b64 for d in iss_j.ii_disclosures]


def obj(signatures):
    o = {"payload": gj["payload"], "signatures": signatures, "disclosures": discl}
    return json.dumps(o)


s_es, s_x = gj["signatures"]
s_x_bad = dict(s_x); s_x_bad["signature"] = ("A" if s_x["signature"][0] != "A" else "B") + s_x["signature"][1:]
T1 = obj([s_es, s_x]); T2 = obj([s_es, s_x_bad]); T3 = obj([s_es]); T5 = obj([s_x])
print("default callback (full key set):")
run("  T1 both valid", T1, cb_default, fmt="json", expect="accept")
run("  T2 X corrupted", T2, cb_default, fmt="json", expect="reject")
run("  T3 stripped to ES256", T3, cb_default, fmt="json", expect="reject")
run("  T5 only X", T5, cb_default, fmt="json", expect="accept")
print("L4m callback (keys restricted to R):")
results.append(run("  L4m T1 both valid", T1, cb_l4m, fmt="json", expect="accept"))
results.append(run("  L4m T2 X corrupted", T2, cb_l4m, fmt="json", expect="reject"))
results.append(run("  L4m T3 stripped to ES256", T3, cb_l4m, fmt="json", expect="reject"))
results.append(run("  L4m T5 only X", T5, cb_l4m, fmt="json", expect="accept"))

print("\n== SUMMARY: checked rows OK =", sum(1 for r in results if r), "of", len(results))
