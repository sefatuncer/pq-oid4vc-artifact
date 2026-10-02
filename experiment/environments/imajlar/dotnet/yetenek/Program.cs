// Environment capability (NOT signature verification): the ML-DSA / Composite ML-DSA types of the .NET runtime and their IsSupported flag.
// Read via reflection, so that the build does not depend on the experimental API attributes. No key is generated, no signature is verified.
using System.Reflection;
var asm = typeof(System.Security.Cryptography.RSA).Assembly;
foreach (var ad in new[] { "System.Security.Cryptography.MLDsa", "System.Security.Cryptography.CompositeMLDsa", "System.Security.Cryptography.SlhDsa" })
{
    var t = Type.GetType(ad + ", " + asm.FullName) ?? AppDomain.CurrentDomain.GetAssemblies().Select(a => a.GetType(ad)).FirstOrDefault(x => x != null);
    var p = t?.GetProperty("IsSupported", BindingFlags.Public | BindingFlags.Static);
    Console.WriteLine($".NET {ad}: tur={(t != null ? "var" : "yok")} IsSupported={(p != null ? p.GetValue(null) : "özellik yok")}");
}
Console.WriteLine($".NET çalışma zamanı {Environment.Version}");
