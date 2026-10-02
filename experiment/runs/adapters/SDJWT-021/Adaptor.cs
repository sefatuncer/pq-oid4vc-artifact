// Adapter for SDJWT-021 WalletFramework.SdJwtVc 3.1.0. The verifier role is in the transitive WalletFramework.SdJwtLib 3.1.0:
// Roles.Implementation.Verifier.VerifyPresentation(string presentation, string issuerJwk) → bool (IVerifier; public type).
// The API takes only the issuer JWK: NO parameter for an alg allow-list / required set. Mapping and reasons: MAPPING.md.
using System.Text.Json.Nodes;
using WalletFramework.SdJwtLib.Models;
using WalletFramework.SdJwtLib.Roles.Implementation;
using Microsoft.IdentityModel.Logging;

// Diagnosis: make the IDX codes/messages of the inner IdentityModel exceptions visible (documented static; does not change verification).
IdentityModelEventSource.ShowPII = true;

// The library delegates the signature to IdentityModel (transitive System.IdentityModel.Tokens.Jwt 7.5.2 / Microsoft.IdentityModel.Tokens 8.0.1);
// under GEC, W is the library's own default (cannot be given through the API). Known native set for the classification:
string[] KutuphaneAlgleri = { "ES256", "ES384" };
const string Api = "new SdJwtDoc(sd_jwt).AssertThatJwtSignatureIsValid(issuerJwk_json, expectedIssuer)";
const string ApiSunum = "new Verifier().VerifyPresentation(sd_jwt_sunum, issuerJwk_json)";
// Trusted issuer configuration (key ↔ iss): BATARYA-ESLEME §4 and anahtarlar/v1.3/roller.json (issuer-eski).
const string IssGoc = "https://issuer.example";
const string IssEskiKid = "GGKBh_lEw5eKZr0XX6kbRRp8H1HYW6hwLhLBagC8MHw";
const string IssEski = "https://legacy-issuer.example";

string Sinifla(Exception e, string? alg)
{
    var m = e.ToString();
    bool kutuphanede = alg != null && KutuphaneAlgleri.Contains(alg);
    if (!kutuphanede && (m.Contains("IDX10511") || m.Contains("IDX10634") || m.Contains("IDX10503") || m.Contains("IDX10500"))) return "alg-desteklenmiyor";
    if (m.Contains("IDX10256") || m.Contains("IDX10257") || m.Contains("SecurityTokenInvalidTypeException")) return "typ";
    if (m.Contains("IDX10696")) return kutuphanede ? "alg-izin-disi" : "alg-desteklenmiyor";
    if (m.Contains("IDX10634")) return "alg-anahtar-uyusmazligi";
    if (m.Contains("IDX10500") || m.Contains("IDX10503") || m.Contains("IDX10501")) return "anahtar-bulunamadi";
    if (m.Contains("IDX10511") || m.Contains("IDX10504") || m.Contains("SignatureException") || m.Contains("Signature")) return "imza-gecersiz";
    if (m.Contains("IDX10223") || m.Contains("IDX10222") || m.Contains("Lifetime") || m.Contains("Expired")) return "zaman";
    if (m.Contains("sd_hash") || m.Contains("SdHash")) return "sd_hash";
    if (m.Contains("Key binding") || m.Contains("KeyBinding") || m.Contains("kb")) return "kb";
    if (e is FormatException || e is ArgumentException || m.Contains("IDX12741") || m.Contains("IDX14100") || m.Contains("JsonReader")) return "ayristirma";
    return "istisna-diger";
}

Sonuc Dogrula(JsonObject isSatiri)
{
    var seri = isSatiri["serilestirme"]!.GetValue<string>();
    var artefakt = isSatiri["artefakt"]?.GetValue<string>() ?? "";
    // B6 (API review): SdJwtDoc expects a '~'-separated compact SD-JWT. JSON serializations, OID4VP requests,
    // DPoP and status list tokens are not inputs of this API.
    bool kompaktSdJwt = seri == "sd-jwt-compact";
    bool cekirdekJws = seri == "compact" && artefakt == "jws-cekirdek"; // maintainers 01.10: "<jws>~" (SD-JWT without disclosures)
    bool topluYanit = seri == "oid4vci-toplu-yanit";                  // BATARYA-ESLEME K11: credentials[0] is evaluated
    if (!kompaktSdJwt && !cekirdekJws && !topluYanit) return Ortak.B6(Api);
    var pol = Ortak.Pol(isSatiri, KutuphaneAlgleri);
    if (pol.Taban is not ("GEC" or "P0" or "P1" or "P2" or "VARSAYILAN"))
        return Ortak.IfadeEdilemedi("VerifyPresentation(presentation, issuerJwk): alg izin listesi / gerekli kume parametresi yok", Api);
    var dg = Ortak.Girdi(isSatiri["vektor_id"]!.GetValue<string>());
    var ham = File.ReadAllText(Ortak.VektorYolu(isSatiri["dosya"]!.GetValue<string>())).Trim();
    string sunum;
    if (cekirdekJws) sunum = ham + "~";
    else if (topluYanit)
    {
        var c0 = JsonNode.Parse(ham)!["credentials"]![0]!;
        sunum = c0 is JsonObject co ? co["credential"]!.GetValue<string>() : c0.GetValue<string>();
    }
    else sunum = ham;
    var baslik = Ortak.Baslik(sunum.Split('~')[0]);
    var alg = Ortak.Str(baslik, "alg");
    var (jwk, anahtarYolu) = Ortak.JwkSec(baslik, dg);
    if (jwk == null) return new Sonuc("red", "anahtar-bulunamadi", "ihracci JWK secilemedi (kid/alg_kid)", Api, anahtarYolu);
    try
    {
        if (Environment.GetEnvironmentVariable("SDJWT021_YOL") == "sunum")
        {
            var ok = new Verifier().VerifyPresentation(sunum, jwk.ToJsonString());
            return ok ? new Sonuc("kabul", null, null, ApiSunum, anahtarYolu) : new Sonuc("red", "imza-gecersiz", "VerifyPresentation=false", ApiSunum, anahtarYolu);
        }
        var iss = Ortak.Str(jwk, "kid") == IssEskiKid ? IssEski : IssGoc;
        new SdJwtDoc(sunum).AssertThatJwtSignatureIsValid(jwk.ToJsonString(), iss);
        // The API returns void: which algorithm was verified cannot be shown → dogrulanan_algoritmalar = []
        return new Sonuc("kabul", null, null, Api, anahtarYolu);
    }
    catch (Exception e)
    {
        var ic = e is AggregateException ae && ae.InnerException != null ? ae.InnerException : e;
        var oz = ic.GetType().Name + ": " + ic.Message + (ic.InnerException != null ? " <- " + ic.InnerException.GetType().Name + ": " + ic.InnerException.Message : "");
        return new Sonuc("red", Sinifla(ic, alg), oz, Api, anahtarYolu);
    }
}

return Ortak.Kos(args, Dogrula);
