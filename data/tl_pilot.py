# -*- coding: utf-8 -*-
"""Pilot: algorithm / key size / validity distribution of X.509 certs in EU national trusted lists (public data)."""
import re, base64, json, os, urllib.request, datetime, collections, hashlib
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa, ec, ed25519, ed448, dsa
s = open("lotl.xml", encoding="utf-8", errors="ignore").read()
locs = sorted(set(l for l in re.findall(r"<(?:\w+:)?TSLLocation>(.*?)<", s) if l.lower().endswith(".xml") and "eu-lotl" not in l))
print("xml TL locations:", len(locs))
certs = {}
per_tl = {}
for u in locs:
    fn = os.path.join("tl", re.sub(r"[^A-Za-z0-9]", "_", u)[-80:])
    try:
        if not os.path.exists(fn):
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 research-pilot"})
            import ssl
            try:
                data = urllib.request.urlopen(req, timeout=60).read()
            except Exception:
                ctx = ssl._create_unverified_context()
                data = urllib.request.urlopen(req, timeout=90, context=ctx).read()
            open(fn, "wb").write(data)
        t = open(fn, encoding="utf-8", errors="ignore").read()
    except Exception as e:
        print("FAIL", u, str(e)[:80]); continue
    b64s = re.findall(r"<(?:\w+:)?X509Certificate>(.*?)</(?:\w+:)?X509Certificate>", t, flags=re.S)
    n = 0
    for b in b64s:
        b = "".join(b.split())
        try:
            der = base64.b64decode(b)
        except Exception:
            continue
        h = hashlib.sha256(der).hexdigest()
        if h in certs: continue
        certs[h] = (u, der); n += 1
    per_tl[u] = n
print("unique certs:", len(certs))
alg = collections.Counter(); notafter_bins = collections.Counter(); sigalg = collections.Counter()
beyond2030_classical = 0; beyond2035_classical = 0; valid_now = 0
now = datetime.datetime(2026, 9, 23, tzinfo=datetime.timezone.utc)
for h, (u, der) in certs.items():
    try:
        c = x509.load_der_x509_certificate(der)
    except Exception:
        alg["unparseable"] += 1; continue
    try:
        pk = c.public_key()
    except Exception:
        alg["key-unparseable(explicit-params?)"] += 1
        pk = None
    if pk is None: a = None
    elif isinstance(pk, rsa.RSAPublicKey): a = f"RSA-{pk.key_size}"
    elif isinstance(pk, ec.EllipticCurvePublicKey): a = f"EC-{pk.curve.name}"
    elif isinstance(pk, ed25519.Ed25519PublicKey): a = "Ed25519"
    elif isinstance(pk, ed448.Ed448PublicKey): a = "Ed448"
    elif isinstance(pk, dsa.DSAPublicKey): a = f"DSA-{pk.key_size}"
    else: a = type(pk).__name__
    if a: alg[a] += 1
    try: sigalg[c.signature_algorithm_oid._name] += 1
    except Exception: sigalg["?"] += 1
    na = c.not_valid_after_utc
    if na >= now: valid_now += 1
    notafter_bins[str(na.year) if na.year <= 2040 else ">2040"] += 1
    if na.year >= 2031: beyond2030_classical += 1
    if na.year >= 2036: beyond2035_classical += 1
res = {"lotl_issue": re.findall(r"<(?:\w+:)?ListIssueDateTime>(.*?)<", s)[:1], "xml_tl_locations": len(locs), "tl_fetched": len(per_tl),
       "unique_certs": len(certs), "valid_on_2026_09_23": valid_now, "notAfter_ge_2031": beyond2030_classical, "notAfter_ge_2036": beyond2035_classical,
       "key_alg": alg.most_common(), "sig_alg": sigalg.most_common(12), "notAfter_year": sorted(notafter_bins.items())}
json.dump(res, open("tl_pilot.json", "w"), indent=1)
print(json.dumps(res, indent=1))
