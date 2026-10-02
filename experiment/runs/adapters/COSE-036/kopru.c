/* COSE-036 wolfCOSE bridge (libkopru.so). It calls only the documented public API of wolfCOSE:
 * wc_CoseKey_PeekInfo / wc_CoseKey_Init / wc_CoseKey_SetEcc|SetEd25519|SetMlDsa / wc_CoseKey_Decode,
 * WOLFCOSE_KEY.alg ("alg pin"; wolfcose.h WOLFCOSE_KEY.alg, sign1.c "Honour the key->alg pin on the verify path"),
 * wc_CoseSign1_Verify and wc_CoseSign_Verify (signerIndex). NO verification loop. JSON/I-O is in the Python driver.
 * asama (stage): 1 = PeekInfo, 2 = key type/insertion, 3 = Decode, 4 = Verify. Return: wolfCOSE/wolfCrypt code (0 = success). */
#include <string.h>
#include <stdint.h>
#include <wolfssl/options.h>
#include <wolfcose/wolfcose.h>
#include <wolfssl/wolfcrypt/ecc.h>
#include <wolfssl/wolfcrypt/ed25519.h>
#include <wolfssl/wolfcrypt/dilithium.h>

static uint8_t g_scratch[65536];

static int anahtar_yukle(WOLFCOSE_KEY* key, const uint8_t* ck, size_t ckLen, ecc_key* ecc, ed25519_key* ed,
                         wc_MlDsaKey* ml, int* tur, int* asama)
{
    WOLFCOSE_KEY_INFO info;
    int ret;
    *asama = 1;
    memset(&info, 0, sizeof(info));
    ret = wc_CoseKey_PeekInfo(ck, ckLen, &info);
    if (ret != 0) return ret;
    *asama = 2;
    ret = wc_CoseKey_Init(key);
    if (ret != 0) return ret;
    if (info.kty == WOLFCOSE_KTY_EC2) {
        if ((ret = wc_ecc_init(ecc)) != 0) return ret;
        *tur = 1;
        ret = wc_CoseKey_SetEcc(key, info.crv, ecc);
    } else if (info.kty == WOLFCOSE_KTY_OKP && info.crv == WOLFCOSE_CRV_ED25519) {
        if ((ret = wc_ed25519_init(ed)) != 0) return ret;
        *tur = 2;
        ret = wc_CoseKey_SetEd25519(key, ed);
    } else if (info.kty == WOLFCOSE_KTY_AKP && (info.alg == WOLFCOSE_ALG_ML_DSA_44 || info.alg == WOLFCOSE_ALG_ML_DSA_65
                                                 || info.alg == WOLFCOSE_ALG_ML_DSA_87)) {
        byte seviye = info.alg == WOLFCOSE_ALG_ML_DSA_44 ? WC_ML_DSA_44 : (info.alg == WOLFCOSE_ALG_ML_DSA_65 ? WC_ML_DSA_65 : WC_ML_DSA_87);
        if ((ret = wc_MlDsaKey_Init(ml, NULL, INVALID_DEVID)) != 0) return ret;
        *tur = 3;
        if ((ret = wc_MlDsaKey_SetParams(ml, seviye)) != 0) return ret;
        ret = wc_CoseKey_SetMlDsa(key, info.alg, ml);
    } else {
        return WOLFCOSE_E_UNSUPPORTED; /* kty/crv/alg not supported in this build (e.g. AKP + composite -55) */
    }
    if (ret != 0) return ret;
    *asama = 3;
    return wc_CoseKey_Decode(key, ck, ckLen);
}

static void serbest(WOLFCOSE_KEY* key, int tur, ecc_key* ecc, ed25519_key* ed, wc_MlDsaKey* ml)
{
    wc_CoseKey_Free(key);
    if (tur == 1) wc_ecc_free(ecc);
    if (tur == 2) wc_ed25519_free(ed);
    if (tur == 3) wc_MlDsaKey_Free(ml);
}

/* If pinKullan = 1, key->alg = pin (0 = WOLFCOSE_ALG_UNSET); if 0, the value left by Decode is kept.
 * imzaci < 0: COSE_Sign1; imzaci >= 0: the signer at that position in COSE_Sign. */
int a10_dogrula(const uint8_t* msg, size_t msgLen, const uint8_t* ck, size_t ckLen, int pinKullan, int32_t pin,
                long imzaci, int32_t* algOut, int* asama)
{
    WOLFCOSE_KEY key;
    WOLFCOSE_HDR hdr;
    ecc_key ecc;
    ed25519_key ed;
    wc_MlDsaKey ml;
    const uint8_t* yuk = NULL;
    size_t yukLen = 0;
    int tur = 0, ret;
    memset(&key, 0, sizeof(key));
    memset(&hdr, 0, sizeof(hdr));
    *algOut = 0;
    ret = anahtar_yukle(&key, ck, ckLen, &ecc, &ed, &ml, &tur, asama);
    if (ret == 0) {
        if (pinKullan) key.alg = pin;
        *asama = 4;
        if (imzaci < 0)
            ret = wc_CoseSign1_Verify(&key, msg, msgLen, NULL, 0, NULL, 0, g_scratch, sizeof(g_scratch), &hdr, &yuk, &yukLen);
        else
            ret = wc_CoseSign_Verify(&key, (size_t)imzaci, msg, msgLen, NULL, 0, NULL, 0, g_scratch, sizeof(g_scratch), &hdr, &yuk, &yukLen);
        *algOut = hdr.alg;
    }
    serbest(&key, tur, &ecc, &ed, &ml);
    return ret;
}
