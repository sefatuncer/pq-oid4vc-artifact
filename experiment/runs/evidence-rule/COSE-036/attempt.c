/* COSE-036 evidence-rule second attempt: wolfCOSE f907071b1012 on wolfSSL v5.9.2-stable,
 * library built with -DWOLFCOSE_ENABLE_DEPRECATED_ALGS (ES256 -7 and EdDSA -8 enabled).
 * Own keys and objects only; no battery vectors. Build and run: see run.sh.
 * Form L4m (primary, COSE_Sign): R = {EdDSA}, W = {ES256, EdDSA}. Form L4c (supplement, COSE_Sign1). */

#include <stdio.h>
#include <string.h>
#include <wolfcose/wolfcose.h>
#include <wolfssl/wolfcrypt/ecc.h>
#include <wolfssl/wolfcrypt/ed25519.h>
#include <wolfssl/wolfcrypt/random.h>
#include <wolfssl/version.h>

#define ISS_MIG "https://issuer.example"
#define ISS_LEG "https://legacy-issuer.example"
#define A_ALG WOLFCOSE_ALG_ES256
#define X_ALG WOLFCOSE_ALG_EDDSA

static int okRows = 0, nRows = 0;
static WC_RNG rng;
static uint8_t scratch[WOLFCOSE_MAX_SCRATCH_SZ];

static const char* errName(int r)
{
    switch (r) {
    case 0: return "";
    case WOLFCOSE_E_INVALID_ARG: return "WOLFCOSE_E_INVALID_ARG";
    case WOLFCOSE_E_CBOR_MALFORMED: return "WOLFCOSE_E_CBOR_MALFORMED";
    case WOLFCOSE_E_COSE_BAD_ALG: return "WOLFCOSE_E_COSE_BAD_ALG";
    case WOLFCOSE_E_COSE_SIG_FAIL: return "WOLFCOSE_E_COSE_SIG_FAIL";
    case WOLFCOSE_E_COSE_KEY_TYPE: return "WOLFCOSE_E_COSE_KEY_TYPE";
    case WOLFCOSE_E_UNSUPPORTED: return "WOLFCOSE_E_UNSUPPORTED";
    case WOLFCOSE_E_CRYPTO: return "WOLFCOSE_E_CRYPTO";
    default: { static char b[32]; snprintf(b, sizeof(b), "error %d", r); return b; }
    }
}

static void row(const char* label, int rc, const char* why, const char* expect)
{
    const char* got = (rc == 0) ? "accept" : "reject";
    const char* st = "-";
    if (strcmp(expect, "-") != 0) {
        nRows++;
        if (strcmp(got, expect) == 0) { okRows++; st = "OK"; } else { st = "MISMATCH"; }
    }
    printf("  %-56s %-7s expect=%-7s %-9s %s\n", label, got, expect, st, why);
}

/* ---- own keys: private keys for signing, public-only WOLFCOSE_KEYs for verification ---- */
typedef struct { ecc_key priv, pub; WOLFCOSE_KEY sk, vk; } EcPair;
typedef struct { ed25519_key priv, pub; WOLFCOSE_KEY sk, vk; } EdPair;

static int makeEc(EcPair* p, int32_t pin)
{
    byte buf[200]; word32 len = sizeof(buf);
    int r = wc_ecc_init(&p->priv);
    if (r == 0) r = wc_ecc_make_key(&rng, 32, &p->priv);
    if (r == 0) r = wc_ecc_export_x963(&p->priv, buf, &len);
    if (r == 0) r = wc_ecc_init(&p->pub);
    if (r == 0) r = wc_ecc_import_x963(buf, len, &p->pub);
    if (r == 0) { wc_CoseKey_Init(&p->sk); r = wc_CoseKey_SetEcc(&p->sk, WOLFCOSE_CRV_P256, &p->priv); }
    if (r == 0) { wc_CoseKey_Init(&p->vk); r = wc_CoseKey_SetEcc(&p->vk, WOLFCOSE_CRV_P256, &p->pub); }
    p->vk.alg = pin;
    return r;
}

static int makeEd(EdPair* p, int32_t pin)
{
    byte buf[64]; word32 len = sizeof(buf);
    int r = wc_ed25519_init(&p->priv);
    if (r == 0) r = wc_ed25519_make_key(&rng, 32, &p->priv);
    if (r == 0) r = wc_ed25519_export_public(&p->priv, buf, &len);
    if (r == 0) r = wc_ed25519_init(&p->pub);
    if (r == 0) r = wc_ed25519_import_public(buf, len, &p->pub);
    if (r == 0) { wc_CoseKey_Init(&p->sk); r = wc_CoseKey_SetEd25519(&p->sk, &p->priv); }
    if (r == 0) { wc_CoseKey_Init(&p->vk); r = wc_CoseKey_SetEd25519(&p->vk, &p->pub); }
    p->vk.alg = pin;
    return r;
}

/* payload: CWT claims {1: iss} */
static size_t claims(const char* iss, uint8_t* out)
{
    size_t n = strlen(iss), i = 0;
    out[i++] = 0xa1; out[i++] = 0x01;
    if (n < 24u) { out[i++] = (uint8_t)(0x60u + n); } else { out[i++] = 0x78; out[i++] = (uint8_t)n; }
    memcpy(out + i, iss, n);
    return i + n;
}

typedef struct { uint8_t b[1024]; size_t n; } Msg;

static int sign1(WOLFCOSE_KEY* k, int32_t alg, const char* kid, const char* iss, Msg* m)
{
    uint8_t pl[64]; size_t pn = claims(iss, pl);
    return wc_CoseSign1_Sign(k, alg, (const uint8_t*)kid, strlen(kid), pl, pn, NULL, 0, NULL, 0,
        scratch, sizeof(scratch), m->b, sizeof(m->b), &m->n, &rng);
}

static int coseSign(const WOLFCOSE_SIGNATURE* s, size_t cnt, Msg* m)
{
    uint8_t pl[64]; size_t pn = claims(ISS_MIG, pl);
    return wc_CoseSign_Sign(s, cnt, pl, pn, NULL, 0, NULL, 0, scratch, sizeof(scratch),
        m->b, sizeof(m->b), &m->n, &rng);
}

/* ---- library calls: one key per call (Sign1), one key and one signer index per call (Sign) ---- */
static int v1(const WOLFCOSE_KEY* k, const Msg* m, WOLFCOSE_HDR* h)
{
    const uint8_t* p = NULL; size_t pn = 0; WOLFCOSE_HDR tmp;
    return wc_CoseSign1_Verify(k, m->b, m->n, NULL, 0, NULL, 0, scratch, sizeof(scratch), h ? h : &tmp, &p, &pn);
}

static int vS(const WOLFCOSE_KEY* k, size_t idx, const Msg* m)
{
    const uint8_t* p = NULL; size_t pn = 0; WOLFCOSE_HDR h;
    return wc_CoseSign_Verify(k, idx, m->b, m->n, NULL, 0, NULL, 0, scratch, sizeof(scratch), &h, &p, &pn);
}

/* A static configuration of the documented COSE_Sign path: a fixed list of (key, signer index) calls,
 * all of which must succeed (the pattern of examples/scenarios/multi_party_approval.c L196-221). */
typedef struct { const WOLFCOSE_KEY* k; size_t idx; } Call;

static int staticConfig(const Call* c, size_t n, const Msg* m, int* failRc)
{
    size_t i;
    for (i = 0; i < n; i++) {
        int r = vS(c[i].k, c[i].idx, m);
        if (r != 0) { *failRc = r; return r; }
    }
    *failRc = 0;
    return 0;
}

/* ---- own code, recorded as B4 only (lines between the markers are counted by run.sh,
 *      blank lines and comment lines excluded) ---- */

/* B4-BEGIN L4m */
static int ownRequiredSet(const WOLFCOSE_KEY* const* keys, size_t nKeys, const Msg* m, int32_t required)
{
    size_t i, j;
    int seen = 0;
    for (i = 0; ; i++) {
        int matched = 0;
        for (j = 0; j < nKeys; j++) {
            int r = vS(keys[j], i, m);
            if (r == WOLFCOSE_E_INVALID_ARG) { break; }
            if (r == WOLFCOSE_E_COSE_BAD_ALG || r == WOLFCOSE_E_COSE_KEY_TYPE) { continue; }
            if (r != 0) { return r; }
            matched = 1;
            if (keys[j]->alg == required) { seen = 1; }
            break;
        }
        if (j < nKeys && !matched) { break; }
        if (!matched) { return WOLFCOSE_E_COSE_BAD_ALG; }
    }
    return seen ? 0 : WOLFCOSE_E_COSE_BAD_ALG;
}
/* B4-END L4m */

/* B4-BEGIN L4c */
typedef struct { const char* iss; const WOLFCOSE_KEY* keys[2]; const char* kids[2]; int32_t allowed[2]; } IssuerRecord;

static int ownPerIssuer(const IssuerRecord* recs, size_t nRecs, const char* iss, const char* kid, const Msg* m)
{
    size_t i, j;
    WOLFCOSE_HDR h;
    for (i = 0; i < nRecs; i++) {
        if (strcmp(recs[i].iss, iss) != 0) { continue; }
        for (j = 0; j < 2u; j++) {
            if (recs[i].kids[j] == NULL || strcmp(recs[i].kids[j], kid) != 0) { continue; }
            int r = v1(recs[i].keys[j], m, &h);
            if (r != 0) { return r; }
            return (h.alg == recs[i].allowed[0] || h.alg == recs[i].allowed[1]) ? 0 : WOLFCOSE_E_COSE_BAD_ALG;
        }
    }
    return WOLFCOSE_E_INVALID_ARG;
}
/* B4-END L4c */

int main(void)
{
    EcPair migA, legA;
    EdPair migX;
    Msg s1MigA, s1MigX, s1LegA, s1MigABad, t1, t2, t3, t5, t1p;
    int rc, f;
    size_t i;

    printf("== wolfCOSE %s (git f907071b1012), wolfSSL %s; built with -DWOLFCOSE_ENABLE_DEPRECATED_ALGS\n",
        LIBWOLFCOSE_VERSION_STRING, LIBWOLFSSL_VERSION_STRING);
    printf("X = EdDSA (-8): WOLFCOSE_HAVE_EDDSA and the deprecated -8 identifier are compiled in\n");

    if (wc_InitRng(&rng) != 0) { return 1; }
    /* keys; verification keys carry the documented algorithm pin key->alg (wolfcose.h L175-177) */
    if (makeEc(&migA, A_ALG) || makeEd(&migX, X_ALG) || makeEc(&legA, A_ALG)) { printf("key setup failed\n"); return 1; }

    /* COSE_Sign1 objects */
    if (sign1(&migA.sk, A_ALG, "mig-es256", ISS_MIG, &s1MigA) || sign1(&migX.sk, X_ALG, "mig-eddsa", ISS_MIG, &s1MigX) ||
        sign1(&legA.sk, A_ALG, "leg-es256", ISS_LEG, &s1LegA) || sign1(&migA.sk, A_ALG, "mig-es256", ISS_MIG, &s1MigABad)) {
        printf("Sign1 failed\n"); return 1;
    }
    s1MigABad.b[s1MigABad.n - 10u] ^= 0x01u;

    /* COSE_Sign objects: A = ES256, X = EdDSA, both keys of the migrated issuer */
    {
        WOLFCOSE_SIGNATURE sA = { A_ALG, &migA.sk, (const uint8_t*)"mig-es256", 9 };
        WOLFCOSE_SIGNATURE sX = { X_ALG, &migX.sk, (const uint8_t*)"mig-eddsa", 9 };
        WOLFCOSE_SIGNATURE ax[2], xa[2];
        ax[0] = sA; ax[1] = sX; xa[0] = sX; xa[1] = sA;
        if (coseSign(ax, 2, &t1) || coseSign(ax, 2, &t2) || coseSign(&sA, 1, &t3) || coseSign(&sX, 1, &t5) ||
            coseSign(xa, 2, &t1p)) { printf("Sign failed\n"); return 1; }
        t2.b[t2.n - 40u] ^= 0x01u;   /* last 64 bytes of T2: EdDSA signature of signer 1 (R part) */
    }
    const Msg* T[5] = { &t1, &t2, &t3, &t5, &t1p };
    const char* TL[5] = { "T1 A+X both valid", "T2 A valid + X corrupted", "T3 A only (X stripped)", "T5 X only",
        "T1 permuted (X first)" };
    const char* TE[5] = { "accept", "reject", "reject", "accept", "accept" };

    printf("\n== 1. Validity check (keys pinned to their own algorithm)\n");
    rc = v1(&migA.vk, &s1MigA, NULL); row("V+ Sign1 migrated ES256", rc, errName(rc), "accept");
    rc = v1(&migX.vk, &s1MigX, NULL); row("V+ Sign1 migrated EdDSA", rc, errName(rc), "accept");
    rc = v1(&legA.vk, &s1LegA, NULL); row("V+ Sign1 legacy ES256", rc, errName(rc), "accept");
    rc = v1(&migA.vk, &s1MigABad, NULL); row("V- Sign1 migrated ES256 corrupted", rc, errName(rc), "reject");
    {
        Call c[2] = { { &migA.vk, 0 }, { &migX.vk, 1 } };
        rc = staticConfig(c, 2, &t1, &f); row("V+ COSE_Sign T1, Verify(A key, 0) and Verify(X key, 1)", rc, errName(f), "accept");
        rc = staticConfig(c, 2, &t2, &f); row("V- COSE_Sign T2, Verify(A key, 0) and Verify(X key, 1)", rc, errName(f), "reject");
    }
    printf("recorded: wc_CoseSign_Verify checks only the signer at the given index\n");
    rc = vS(&migA.vk, 0, &t2); row("T2 (X corrupted), Verify(A key, 0) only", rc, errName(rc), "-");

    printf("\n== 2. L4m (primary form), R = {EdDSA}, W = {ES256, EdDSA}: static configurations of wc_CoseSign_Verify\n");
    {
        Call cW[2] = { { &migA.vk, 0 }, { &migX.vk, 1 } };
        Call cR1[1] = { { &migX.vk, 1 } };
        Call cR0[1] = { { &migX.vk, 0 } };
        Call cWp[2] = { { &migX.vk, 0 }, { &migA.vk, 1 } };
        struct { const char* name; const Call* c; size_t n; } cfg[4] = {
            { "W in order: Verify(A key, 0), Verify(X key, 1)", cW, 2 },
            { "R at index 1: Verify(X key, 1)", cR1, 1 },
            { "R at index 0: Verify(X key, 0)", cR0, 1 },
            { "W permuted: Verify(X key, 0), Verify(A key, 1)", cWp, 2 },
        };
        size_t k;
        for (k = 0; k < 4u; k++) {
            printf("configuration: %s\n", cfg[k].name);
            for (i = 0; i < 5u; i++) {
                rc = staticConfig(cfg[k].c, cfg[k].n, T[i], &f);
                row(TL[i], rc, errName(f), TE[i]);
            }
        }
    }
    printf("-> every call names one signer index; no static list of (key, index) calls gives T1/T5 accept and T3 reject.\n");
    printf("   The library has no call that verifies a COSE_Sign as a whole, returns the signer count, or takes a required set.\n");

    printf("\n== 3. L4m with own code (B4 record only): loop over signer indices with the issuer's pinned keys,\n");
    printf("      then require that an EdDSA signer verified\n");
    {
        const WOLFCOSE_KEY* keys[2] = { &migA.vk, &migX.vk };
        for (i = 0; i < 5u; i++) {
            rc = ownRequiredSet(keys, 2, T[i], X_ALG);
            row(TL[i], rc, errName(rc), "-");
        }
    }

    printf("\n== 4. L4c (supplement): COSE_Sign1, migrated issuer (R = {EdDSA}; keys mig-es256, mig-eddsa),\n");
    printf("      legacy issuer (R = {}; key leg-es256); one key per call, chosen by kid\n");
    printf("records: migrated = {ES256 key pinned -7, EdDSA key pinned -8}, legacy = {ES256 key pinned -7}\n");
    rc = v1(&migA.vk, &s1MigA, NULL); row("migrated ES256 with the record's ES256 key", rc, errName(rc), "reject");
    rc = v1(&migX.vk, &s1MigX, NULL); row("migrated EdDSA with the record's EdDSA key", rc, errName(rc), "accept");
    rc = v1(&legA.vk, &s1LegA, NULL); row("legacy ES256 with the record's ES256 key", rc, errName(rc), "accept");
    printf("recorded, not counted (README rule 'Key material'):\n");
    {
        WOLFCOSE_KEY relabelled = migA.vk;   /* the migrated ES256 public key, pinned to EdDSA */
        relabelled.alg = X_ALG;
        rc = v1(&relabelled, &s1MigA, NULL); row("migrated ES256, migrated ES256 key relabelled pin -8", rc, errName(rc), "-");
    }
    rc = v1(&migX.vk, &s1MigA, NULL); row("migrated ES256, classical key left out (EdDSA key only)", rc, errName(rc), "-");
    {
        WOLFCOSE_KEY unpinned = migA.vk;
        unpinned.alg = WOLFCOSE_ALG_UNSET;
        rc = v1(&unpinned, &s1MigA, NULL); row("migrated ES256 with an unpinned ES256 key", rc, errName(rc), "-");
    }

    printf("\n== 5. L4c with own code (B4 record only): per-issuer policy records, kid lookup, check of hdr.alg after\n");
    printf("      verification\n");
    {
        IssuerRecord recs[2] = {
            { ISS_MIG, { &migA.vk, &migX.vk }, { "mig-es256", "mig-eddsa" }, { X_ALG, X_ALG } },
            { ISS_LEG, { &legA.vk, NULL }, { "leg-es256", NULL }, { A_ALG, X_ALG } },
        };
        rc = ownPerIssuer(recs, 2, ISS_MIG, "mig-es256", &s1MigA); row("migrated ES256", rc, errName(rc), "-");
        rc = ownPerIssuer(recs, 2, ISS_MIG, "mig-eddsa", &s1MigX); row("migrated EdDSA", rc, errName(rc), "-");
        rc = ownPerIssuer(recs, 2, ISS_LEG, "leg-es256", &s1LegA); row("legacy ES256", rc, errName(rc), "-");
        printf("(record selection, key choice and the algorithm check are caller code; the migrated record holds its ES256 key)\n");
    }

    printf("\n== SUMMARY: checked rows OK = %d of %d\n", okRows, nRows);
    wc_FreeRng(&rng);
    return 0;
}
