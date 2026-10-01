// Ortam yeteneği (imza doğrulama DEĞİL): .NET çalışma zamanının ML-DSA / Composite ML-DSA türleri ve IsSupported bayrağı.
// Yansıma ile okunur; derleme deneysel API özniteliklerine bağlı kalmaz. Anahtar üretilmez, imza doğrulanmaz.
using System.Reflection;
var asm = typeof(System.Security.Cryptography.RSA).Assembly;
foreach (var ad in new[] { "System.Security.Cryptography.MLDsa", "System.Security.Cryptography.CompositeMLDsa", "System.Security.Cryptography.SlhDsa" })
{
    var t = Type.GetType(ad + ", " + asm.FullName) ?? AppDomain.CurrentDomain.GetAssemblies().Select(a => a.GetType(ad)).FirstOrDefault(x => x != null);
    var p = t?.GetProperty("IsSupported", BindingFlags.Public | BindingFlags.Static);
    Console.WriteLine($".NET {ad}: tur={(t != null ? "var" : "yok")} IsSupported={(p != null ? p.GetValue(null) : "özellik yok")}");
}
Console.WriteLine($".NET çalışma zamanı {Environment.Version}");
