// Shared adapter skeleton (C#) — C3 adapter contract 1.0 (experiment/oracle/oracle-A/adapter-contract.md) / RUNNER.md §1–§3.
// This file is IDENTICAL in JOSE-001, JOSE-002 and SDJWT-021. The library-specific verification is in Adaptor.cs.
// NO verification loop: signature verification is done only by the documented API of the target library. No network access.
using System.Diagnostics;
using System.Reflection;
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Text.RegularExpressions;

public sealed record Sonuc(string SonucHam, string? HataSinifi, string? HataOzeti, string? ApiYolu,
    string? AnahtarYolu = null, List<(int sira, string alg, string sonuc)>? Dogrulanan = null);

public sealed record Politika(string Taban, List<string>? W, List<string> R);

public static class Ortak
{
    public const string A = "ES256";
    public static readonly Dictionary<string, string> XKol = new()
    {
        ["kontrol-EdDSA"] = "EdDSA", ["kontrol-Ed25519"] = "Ed25519", ["kontrol-ES384"] = "ES384",
        ["tedavi-ML-DSA-65"] = "ML-DSA-65", ["tedavi-composite"] = "ML-DSA-65-ES256",
    };
    static Dictionary<string, JsonObject>? _manifest;
    static readonly Dictionary<string, JsonObject> _jwks = new();

    public static byte[] B64d(string s)
    {
        s = s.Replace('-', '+').Replace('_', '/');
        return Convert.FromBase64String(s + new string('=', (4 - s.Length % 4) % 4));
    }

    public static string VektorYolu(string dosya)
    {
        foreach (var y in new[] { "/v/" + dosya, "/v/" + Regex.Replace(dosya, "^v1\\.3/", "") })
            if (File.Exists(y)) return y;
        return "/v/" + dosya;
    }

    // ONLY dogrulama_girdileri is read from the manifest; `insa` and the other fields are not read (maintainers 01.10).
    public static JsonObject Girdi(string id)
    {
        if (_manifest == null)
        {
            var y = File.Exists("/v/MANIFEST.json") ? "/v/MANIFEST.json" : "/v/v1.3/MANIFEST.json";
            var m = JsonNode.Parse(File.ReadAllText(y))!.AsObject();
            _manifest = new();
            foreach (var e in m["vektorler"]!.AsArray())
                _manifest[e!["id"]!.GetValue<string>()] = (e["dogrulama_girdileri"] as JsonObject)?.DeepClone().AsObject() ?? new JsonObject();
            // Pre-freeze SD-JWT validity vectors (not in the battery) carry their own manifest in the same schema.
            if (File.Exists("/v/vpm-sdjwt/MANIFEST.json"))
                foreach (var e in JsonNode.Parse(File.ReadAllText("/v/vpm-sdjwt/MANIFEST.json"))!["vektorler"]!.AsArray())
                    _manifest[e!["id"]!.GetValue<string>()] = (e["dogrulama_girdileri"] as JsonObject)?.DeepClone().AsObject() ?? new JsonObject();
        }
        return _manifest.TryGetValue(id, out var g) ? g : throw new InvalidOperationException("manifestte yok: " + id);
    }

    public static string AnahtarDosyasi(string goreli) => "/anahtarlar/" + Regex.Replace(goreli, "^anahtarlar/", "");

    public static JsonObject Jwks(string goreli)
    {
        if (!_jwks.TryGetValue(goreli, out var j))
            _jwks[goreli] = j = JsonNode.Parse(File.ReadAllText(AnahtarDosyasi(goreli)))!.AsObject();
        return j;
    }

    // Policy → (W, R). METHOD.md §2; VARSAYILAN = contract §5.2 L5 (key only).
    public static Politika Pol(JsonObject isSatiri, IReadOnlyList<string> kutuphaneAlgleri)
    {
        var p = isSatiri["politika"]!.GetValue<string>();
        var taban = p.Split('|')[0].Split('@')[0]; // the suffixes '|sdjwtvc=..' and '@-19' only split the oracle
        XKol.TryGetValue(isSatiri["kol"]!.GetValue<string>(), out var x);
        string X() => x ?? throw new InvalidOperationException("kol icin X tanimsiz");
        return taban switch
        {
            "GEC" or "P0" or "P1" or "P2" => new(taban, kutuphaneAlgleri.ToList(), new()),
            "VARSAYILAN" => new(taban, null, new()),
            "IZIN-A" => new(taban, new() { A }, new()),
            "IZIN-AX" => new(taban, new() { A, X() }, new()),
            "L4" or "L4-S" or "L4-Y" or "L4-YOL" => new(taban, new() { A, X() }, new() { X() }),
            _ => throw new InvalidOperationException("bilinmeyen politika " + p),
        };
    }

    // For a single-signature object with R ≠ ∅ the effective allow-list is R (a single signature satisfies R only if it is X itself; R ⊆ W).
    public static List<string>? TekImzaIzin(Politika p) => p.W == null ? null : (p.R.Count > 0 ? p.R : p.W);

    // Key selection (contract §8 item 1): header kid → the vector's JWKS; otherwise alg_kid[alg]; otherwise the single kid. DPoP: header jwk.
    public static (JsonObject? jwk, string yol) JwkSec(JsonObject baslik, JsonObject dg)
    {
        if (dg["anahtar"]?.GetValue<string>() == "jwk basligindan") return (baslik["jwk"] as JsonObject, "jwk-basligi");
        if (dg["jwks"] == null) return (null, "JWK");
        string? kid = baslik["kid"] is JsonValue kv && kv.TryGetValue<string>(out var k) ? k : null;
        if (kid == null)
        {
            var ak = dg["alg_kid"];
            if (ak is JsonValue akv && akv.TryGetValue<string>(out var aks)) ak = JsonNode.Parse(aks);
            var alg = baslik["alg"] is JsonValue av && av.TryGetValue<string>(out var a) ? a : null;
            if (ak is JsonObject ako && alg != null && ako[alg] is JsonValue kidv) kid = kidv.GetValue<string>();
            if (kid == null && dg["kid"] is JsonArray ka && ka.Count == 1) kid = ka[0]!.GetValue<string>();
        }
        foreach (var key in Jwks(dg["jwks"]!.GetValue<string>())["keys"]!.AsArray())
            if (key!["kid"]?.GetValue<string>() == kid) return (key.AsObject(), "JWK");
        return (null, "JWK");
    }

    public static JsonObject Baslik(string kompakt)
    {
        try { return JsonNode.Parse(B64d(kompakt.Split('.')[0]))!.AsObject(); } catch { return new JsonObject(); }
    }

    public static string? Str(JsonObject o, string ad) => o[ad] is JsonValue v && v.TryGetValue<string>(out var s) ? s : null;

    public static string KosuAdi(string cikti)
    {
        var e = Environment.GetEnvironmentVariable("KOSU");
        if (!string.IsNullOrEmpty(e)) return e;
        var p = Path.GetFileNameWithoutExtension(cikti).Split('.');
        return p.Length >= 2 ? p[^1] : "oncesi";
    }

    static string Sabit(string ad) => File.Exists("/opt/a/" + ad) ? File.ReadAllText("/opt/a/" + ad).Trim() : "";

    public static Sonuc B6(string api) => new("uygulanamaz", "bicim-desteklenmiyor", "B6: MAPPING.md (API incelemesi)", api);
    public static Sonuc IfadeEdilemedi(string neden, string api) => new("ifade-edilemedi", null, neden, api);

    // Main loop: job rows in sequence in one process; 60 s per vector (task timeout).
    public static int Kos(string[] args, Func<JsonObject, Sonuc> dogrula)
    {
        if (args.Length >= 1 && args[0] == "tara") { Tara(args.Length > 1 ? args[1] : "."); return 0; }
        if (args.Length < 2) { Console.Error.WriteLine("usage: adaptor <jobs-v1.3.jsonl> <output.jsonl>"); return 2; }
        var kosu = KosuAdi(args[1]);
        using var w = new StreamWriter(args[1]) { NewLine = "\n" };
        foreach (var l in File.ReadLines(args[0]))
        {
            if (string.IsNullOrWhiteSpace(l)) continue;
            var isSatiri = JsonNode.Parse(l)!.AsObject();
            var sw = Stopwatch.StartNew();
            Sonuc s;
            try
            {
                var t = Task.Run(() => dogrula(isSatiri));
                s = t.Wait(TimeSpan.FromSeconds(60)) ? t.Result
                    : new Sonuc("zaman-asimi", "zaman-asimi", "60 s asildi", null);
            }
            catch (Exception e)
            {
                var ic = e is AggregateException ae && ae.InnerException != null ? ae.InnerException : e;
                s = new Sonuc("istisna", "adaptor-hatasi", ic.GetType().Name + ": " + ic.Message, null);
            }
            sw.Stop();
            var dog = new JsonArray();
            foreach (var d in s.Dogrulanan ?? new()) dog.Add(new JsonObject { ["sira"] = d.sira, ["alg"] = d.alg, ["sonuc"] = d.sonuc });
            var satir = new JsonObject
            {
                ["sozlesme"] = "adaptor-sozlesme/1.0",
                ["hedef_id"] = Environment.GetEnvironmentVariable("HEDEF_ID") ?? "bilinmiyor",
                ["hedef_surum"] = Sabit("HEDEF_SURUM"),
                ["adaptor_sha256"] = Sabit("ADAPTOR_SHA256"),
                ["kosu"] = kosu,
                ["vektor_id"] = isSatiri["vektor_id"]!.GetValue<string>(),
                ["politika"] = isSatiri["politika"]!.GetValue<string>(),
                ["kol"] = isSatiri["kol"]!.GetValue<string>(),
                ["sonuc_ham"] = s.SonucHam,
                ["hata_sinifi"] = s.HataSinifi,
                ["hata_ozeti"] = s.HataOzeti == null ? null : (s.HataOzeti.Length > 200 ? s.HataOzeti[..200] : s.HataOzeti),
                ["dogrulanan_algoritmalar"] = dog,
                ["api_yolu"] = s.ApiYolu,
                ["anahtar_yolu"] = s.AnahtarYolu,
                ["sure_ms"] = sw.ElapsedMilliseconds,
            };
            w.WriteLine(satir.ToJsonString(new JsonSerializerOptions { Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping }));
            w.Flush();
        }
        return 0;
    }

    // API scan (contract §5.1): the public types and members of the target assemblies, filtered with a regular expression.
    static void Tara(string desen)
    {
        var rx = new Regex(desen, RegexOptions.IgnoreCase);
        var adlar = (Environment.GetEnvironmentVariable("TARA_DERLEMELER") ?? "").Split(',', StringSplitOptions.RemoveEmptyEntries);
        foreach (var ad in adlar)
        {
            var asm = Assembly.Load(new AssemblyName(ad));
            Console.WriteLine($"## derleme {asm.GetName().Name} {asm.GetName().Version} ({asm.GetCustomAttribute<AssemblyInformationalVersionAttribute>()?.InformationalVersion})");
            Type[] tipler;
            try { tipler = asm.GetExportedTypes(); } catch (ReflectionTypeLoadException e) { tipler = e.Types.Where(t => t != null).ToArray()!; }
            foreach (var t in tipler.OrderBy(t => t.FullName))
            {
                if (rx.IsMatch(t.FullName!)) Console.WriteLine($"tip {t.FullName}");
                foreach (var m in t.GetMembers(BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static | BindingFlags.DeclaredOnly))
                {
                    var imza = $"{t.Name}.{m.Name}";
                    string? deger = null;
                    if (m is FieldInfo f && f.IsLiteral) deger = f.GetRawConstantValue()?.ToString();
                    if (rx.IsMatch(imza) || (deger != null && rx.IsMatch(deger)))
                        Console.WriteLine($"  uye {m.MemberType} {t.FullName}.{m.Name}{(deger != null ? " = \"" + deger + "\"" : "")}");
                }
            }
        }
    }
}
