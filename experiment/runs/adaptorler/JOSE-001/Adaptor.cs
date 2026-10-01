// JOSE-001 Microsoft.IdentityModel.JsonWebTokens 8.23.0 (System.IdentityModel.Tokens.Jwt 8.23.0 paket kümesi) adaptörü.
// Belgeli genel API: JsonWebTokenHandler.ValidateTokenAsync(string, TokenValidationParameters);
// TokenValidationParameters.ValidAlgorithms (izin listesi), IssuerSigningKey = new JsonWebKey(json) (JWK; AKP/ML-DSA dahil).
// Eşleme ve gerekçeler: ESLEME.md.
using System.Text.Json.Nodes;
using Microsoft.IdentityModel.JsonWebTokens;
using Microsoft.IdentityModel.Tokens;
using Microsoft.IdentityModel.Logging;

// Tanılama: IDX10511 iletisindeki "Exceptions caught" bölümünün görünmesi için (belgeli statik; doğrulamayı değiştirmez).
IdentityModelEventSource.ShowPII = true;

// Bataryadaki algoritmalardan yerel destek (kanit/api-tarama.txt: SecurityAlgorithms.EcdsaSha256/384, MlDsa44/65/87;
// EdDSA/Ed25519 ve composite yok).
string[] KutuphaneAlgleri = { "ES256", "ES384", "ML-DSA-44", "ML-DSA-65", "ML-DSA-87" };
string[] DestekliBicim = { "compact" };
const string Api = "JsonWebTokenHandler.ValidateTokenAsync(jwt, new TokenValidationParameters{ ValidAlgorithms = W, IssuerSigningKey = new JsonWebKey(jwk), ValidateIssuer=false, ValidateAudience=false, RequireExpirationTime=false })";

// hata_ozeti: istisna türü + IDX10511'in "Exceptions caught" bölümü (asıl neden) kısaltılarak.
string Ozet(Exception e)
{
    var m = e.Message;
    var i = m.IndexOf("Exceptions caught:", StringComparison.Ordinal);
    var neden = i >= 0 ? m[(i + 18)..] : m;
    var j = neden.IndexOf("token: '", StringComparison.Ordinal);
    if (j > 0) neden = neden[..j];
    return e.GetType().Name + ": " + (i >= 0 ? "IDX10511 <- " : "") + System.Text.RegularExpressions.Regex.Replace(neden, @"\s+", " ").Trim();
}

string Sinifla(Exception e, string? alg, List<string> izin)
{
    var m = e.ToString();
    bool kutuphanede = alg != null && KutuphaneAlgleri.Contains(alg);
    if (e is SecurityTokenInvalidAlgorithmException || m.Contains("IDX10696"))
        return kutuphanede ? "alg-izin-disi" : "alg-desteklenmiyor";
    if (m.Contains("IDX10634") || m.Contains("IDX10652") || e is NotSupportedException)
        return kutuphanede ? "alg-anahtar-uyusmazligi" : "alg-desteklenmiyor";
    if (e is SecurityTokenSignatureKeyNotFoundException) return "anahtar-bulunamadi";
    // Kütüphanenin tanımadığı alg (EdDSA, composite, kayıtsız): IDX10511 "Exceptions caught" boş döner, doğrulama denenmez.
    if (e is SecurityTokenInvalidSignatureException && !kutuphanede) return "alg-desteklenmiyor";
    if (e is SecurityTokenInvalidSignatureException) return "imza-gecersiz";
    if (e is SecurityTokenExpiredException || e is SecurityTokenNotYetValidException || e is SecurityTokenNoExpirationException
        || e is SecurityTokenInvalidLifetimeException) return "zaman";
    if (e is SecurityTokenMalformedException || e is ArgumentException) return "ayristirma";
    if (e is SecurityTokenInvalidTypeException) return "typ";
    return "istisna-diger";
}

Sonuc Dogrula(JsonObject isSatiri)
{
    if (!DestekliBicim.Contains(isSatiri["serilestirme"]!.GetValue<string>())) return Ortak.B6(Api);
    var dg = Ortak.Girdi(isSatiri["vektor_id"]!.GetValue<string>());
    var jwt = File.ReadAllText(Ortak.VektorYolu(isSatiri["dosya"]!.GetValue<string>())).Trim();
    var pol = Ortak.Pol(isSatiri, KutuphaneAlgleri);
    if (pol.Taban == "L4-YOL") return Ortak.IfadeEdilemedi("x5c/x5chain yol sinifi politikasi (L4-YOL, B2) icin belgeli API yok", Api);
    var izin = Ortak.TekImzaIzin(pol);
    var baslik = Ortak.Baslik(jwt);
    var alg = Ortak.Str(baslik, "alg");
    var (jwkJson, anahtarYolu) = Ortak.JwkSec(baslik, dg);
    var tvp = new TokenValidationParameters
    {
        ValidateIssuer = false, ValidateAudience = false, RequireExpirationTime = false, ValidateLifetime = true,
        ValidAlgorithms = izin,                       // VARSAYILAN: null (kütüphane varsayılanı)
        IssuerSigningKey = jwkJson == null ? null : new JsonWebKey(jwkJson.ToJsonString()),
    };
    var api = izin == null ? Api.Replace("ValidAlgorithms = W, ", "") : Api;
    try
    {
        var r = new JsonWebTokenHandler().ValidateTokenAsync(jwt, tvp).GetAwaiter().GetResult();
        if (r.IsValid)
        {
            var algDog = (r.SecurityToken as JsonWebToken)?.Alg ?? alg ?? "";
            return new Sonuc("kabul", null, null, api, anahtarYolu, new() { (0, algDog, "gecerli") });
        }
        var e = r.Exception ?? new Exception("IsValid=false");
        if (Environment.GetEnvironmentVariable("ADAPTOR_HATA_TAM") == "1") Console.Error.WriteLine("HATA " + isSatiri["vektor_id"] + " " + e);
        return new Sonuc("red", Sinifla(e, alg, izin ?? new()), Ozet(e), api, anahtarYolu);
    }
    catch (Exception e)
    {
        return new Sonuc("istisna", Sinifla(e, alg, izin ?? new()), e.GetType().Name + ": " + e.Message, api, anahtarYolu);
    }
}

return Ortak.Kos(args, Dogrula);
