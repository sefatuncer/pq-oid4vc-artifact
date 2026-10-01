// JOSE-002 JWT (jwt-dotnet/jwt) 11.1.0 adaptörü. Belgeli genel API: JwtBuilder.Create().WithAlgorithm(IJwtAlgorithm)
// .WithDateTimeProvider(..).MustVerifySignature().Decode(token); ES256Algorithm/ES384Algorithm(ECDsa açık anahtar).
// JWT.NET'te JWK API'si ve izin listesi seçeneği yok: politika, anahtara bağlanan algoritma nesnesiyle kurulur.
// Eşleme ve gerekçeler: ESLEME.md.
using System.Security.Cryptography;
using System.Text.Json.Nodes;
using JWT;
using JWT.Algorithms;
using JWT.Builder;
using JWT.Exceptions;

// Bataryadaki algoritmalardan yerel destek (JwtAlgorithmName: HS*, RS*, ES256/384/512, None; EdDSA/ML-DSA/composite yok)
string[] KutuphaneAlgleri = { "ES256", "ES384" };
string[] DestekliBicim = { "compact" };
const string Api = "JwtBuilder.Create().WithAlgorithm(new ES256Algorithm|ES384Algorithm(ECDsa(jwk))  [alg(anahtar_turu) ∈ W]).WithDateTimeProvider(simdi).MustVerifySignature().Decode(jwt)";

// JWK (EC) → ECDsa: kütüphanenin beklediği doğrudan anahtar nesnesi (anahtar_yolu = "dogrudan").
ECDsa? EcAnahtar(JsonObject jwk)
{
    if (Ortak.Str(jwk, "kty") != "EC") return null;
    var egri = Ortak.Str(jwk, "crv") switch { "P-256" => ECCurve.NamedCurves.nistP256, "P-384" => ECCurve.NamedCurves.nistP384, _ => (ECCurve?)null };
    if (egri == null) return null;
    return ECDsa.Create(new ECParameters { Curve = egri.Value, Q = new ECPoint { X = Ortak.B64d(Ortak.Str(jwk, "x")!), Y = Ortak.B64d(Ortak.Str(jwk, "y")!) } });
}

string Sinifla(Exception e, string? alg, List<string> izin)
{
    var m = e.Message;
    bool kutuphanede = alg != null && KutuphaneAlgleri.Contains(alg);
    if (e is SignatureVerificationException) return kutuphanede ? (m.Contains("lgorithm") ? "alg-anahtar-uyusmazligi" : "imza-gecersiz") : "alg-desteklenmiyor";
    if (e is TokenExpiredException || e is TokenNotYetValidException) return "zaman";
    if (e is InvalidTokenPartsException || e is FormatException) return "ayristirma";
    if (e is NotSupportedException) return "alg-desteklenmiyor";
    if (e is InvalidOperationException && m.Contains("decode a token")) return kutuphanede ? (izin.Contains(alg!) ? "alg-anahtar-uyusmazligi" : "alg-izin-disi") : "alg-desteklenmiyor";
    if (e is ArgumentException) return "ayristirma";
    return "istisna-diger";
}

Sonuc Dogrula(JsonObject isSatiri)
{
    if (!DestekliBicim.Contains(isSatiri["serilestirme"]!.GetValue<string>())) return Ortak.B6(Api);
    var dg = Ortak.Girdi(isSatiri["vektor_id"]!.GetValue<string>());
    var jwt = File.ReadAllText(Ortak.VektorYolu(isSatiri["dosya"]!.GetValue<string>())).Trim();
    var pol = Ortak.Pol(isSatiri, KutuphaneAlgleri);
    if (pol.Taban == "L4-YOL") return Ortak.IfadeEdilemedi("x5c/x5chain yol sinifi politikasi (L4-YOL, B2) icin belgeli API yok", Api);
    var izin = Ortak.TekImzaIzin(pol) ?? KutuphaneAlgleri.ToList(); // VARSAYILAN: JWT.NET'te algoritma her zaman açıkça verilir
    var baslik = Ortak.Baslik(jwt);
    var alg = Ortak.Str(baslik, "alg");
    var (jwk, anahtarYolu) = Ortak.JwkSec(baslik, dg);
    anahtarYolu = anahtarYolu == "jwk-basligi" ? "jwk-basligi" : "dogrudan";
    var simdi = DateTimeOffset.FromUnixTimeSeconds(dg["simdi"]?.GetValue<long>() ?? DateTimeOffset.UtcNow.ToUnixTimeSeconds());
    // Anahtar–alg bağlaması: seçilen anahtarın türüne karşılık gelen algoritma nesnesi, alg W içindeyse yapılandırılır.
    IJwtAlgorithm? algoritma = null;
    var ec = jwk == null ? null : EcAnahtar(jwk);
    if (ec != null)
    {
        var dogal = ec.KeySize == 384 ? "ES384" : "ES256";
        if (izin.Contains(dogal)) algoritma = dogal == "ES256" ? new ES256Algorithm(ec) : new ES384Algorithm(ec);
    }
    try
    {
        var b = JwtBuilder.Create().WithDateTimeProvider(new SabitSaat(simdi)).MustVerifySignature();
        if (algoritma != null) b = b.WithAlgorithm(algoritma); // yapılandırılamıyorsa kütüphane kendi hatasını verir
        b.Decode(jwt);
        return new Sonuc("kabul", null, null, Api, anahtarYolu, new() { (0, algoritma!.Name, "gecerli") });
    }
    catch (Exception e)
    {
        // "Can't decode a token. Check if you have called WithAlgorithm": W içinde bu anahtar türüne bağlanabilen algoritma yok
        var red = e is SignatureVerificationException || e is TokenExpiredException || e is TokenNotYetValidException || e is InvalidTokenPartsException
                  || (e is InvalidOperationException && algoritma == null);
        return new Sonuc(red ? "red" : "istisna", Sinifla(e, alg, izin), e.GetType().Name + ": " + e.Message, Api, anahtarYolu);
    }
}

return Ortak.Kos(args, Dogrula);

sealed class SabitSaat : IDateTimeProvider
{
    readonly DateTimeOffset _t;
    public SabitSaat(DateTimeOffset t) => _t = t;
    public DateTimeOffset GetNow() => _t;
}

