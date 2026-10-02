#!/usr/bin/env bash
# NuGet target: PackageReference with the exact version ([x.y.z]), record packages.lock.json (contentHash), build,
# load all types of the target assembly (Assembly.GetTypes). NO signature verification.
# Input (kur.sh): PAKET, SURUM, [ASM (assembly name; default PAKET)], [ANAHTAR "Full.Type.Name ..."]
set -uo pipefail
source /b/ortak.sh
: "${PAKET:?}"; : "${SURUM:?}"; ASM="${ASM:-$PAKET}"
yaz ekosistem nuget; yaz paket "$PAKET"; yaz istenen_surum "$SURUM"
yaz arac "dotnet-sdk $(dotnet --version); net10.0; sistem $(openssl version | cut -d' ' -f1-2)"
P=/tmp/p; rm -rf $P; mkdir -p $P; cd $P
cat > Deneme.csproj <<X
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><Nullable>disable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings><RestorePackagesWithLockFile>true</RestorePackagesWithLockFile>
    <NuGetAudit>false</NuGetAudit></PropertyGroup>
  <ItemGroup><PackageReference Include="$PAKET" Version="[$SURUM]" /></ItemGroup>
</Project>
X
cat > Program.cs <<X
// Link check: the target assembly is loaded by name and all its types are loaded (GetTypes); NO method is called.
using System.Reflection;
var asm = Assembly.Load(new AssemblyName("$ASM"));
Type[] tipler; int eksik = 0;
try { tipler = asm.GetTypes(); }
catch (ReflectionTypeLoadException e) { tipler = e.Types.Where(t => t != null).ToArray(); eksik = e.Types.Count(t => t == null);
  foreach (var le in e.LoaderExceptions.Take(10)) Console.WriteLine("  yuklenemedi: " + le?.Message); }
Console.WriteLine(\$"derleme={asm.GetName().Name} {asm.GetName().Version} tip_yuklendi={tipler.Length} tip_yuklenemedi={eksik}");
var tamam = eksik == 0;
foreach (var k in "${ANAHTAR:-}".Split(' ', StringSplitOptions.RemoveEmptyEntries)) {
  var t = asm.GetType(k); Console.WriteLine(\$"anahtar_tip {k} {(t != null ? "OK" : "HATA")}"); tamam &= t != null; }
Console.WriteLine("ad_eslesen_tipler (Valid|Verif|SdJwt; bilgi): " + string.Join(",", tipler.Where(t => t.IsPublic && (t.Name.Contains("Valid") || t.Name.Contains("Verif") || t.Name.Contains("SdJwt"))).Select(t => t.FullName).Take(25)));
return tamam ? 0 : 3;
X
echo "== dotnet restore (kilit dosyasıyla)"
if ! dotnet restore; then yaz not "dotnet restore başarısız"; bitir basarisiz 10; fi
cp Deneme.csproj packages.lock.json "$C/"
yaz kilit_dosyasi "packages.lock.json (NuGet contentHash)"; yaz kilit_sha256 "$(ozet packages.lock.json)"
dotnet --list-runtimes > /dev/null
# contentHash of the target package and number of dependencies from the lock file (no jq/python: grep/sed)
L=packages.lock.json
yaz bagimlilik_sayisi "$(grep -c '"type": "\(Direct\|Transitive\|CentralTransitive\)"' $L)"
CH=$(awk -v p="\"$PAKET\": {" 'index($0,p){a=1} a&&/"contentHash"/{gsub(/[",]/,"",$2);print $2;exit}' $L)
[ -n "$CH" ] && yaz paket_ozeti "sha512:$CH (NuGet contentHash)"
PKL=$(echo "$PAKET" | tr '[:upper:]' '[:lower:]')
NS=/root/.nuget/packages/$PKL/$SURUM/$PKL.nuspec
if [ -f "$NS" ]; then
  cp "$NS" "$C/"
  CM=$(grep -o '<repository[^>]*commit="[0-9a-f]*"' "$NS" | grep -o 'commit="[0-9a-f]*"' | cut -d'"' -f2)
  [ -n "$CM" ] && { yaz commit "$CM"; yaz commit_kaynagi "nuspec <repository commit>"; }
  yaz lisans_kayit "$(grep -o '<license[^>]*>[^<]*</license>' "$NS" | sed 's/<[^>]*>//g')"
fi
yaz kurulan_surum "$SURUM"
echo "== dotnet build + çalıştır"
if ! dotnet build -c Release --no-restore; then yaz not "dotnet build başarısız"; bitir basarisiz 12; fi
if dotnet bin/Release/net10.0/Deneme.dll > "$C/ice_aktar.txt" 2>&1; then cat "$C/ice_aktar.txt"; bitir basarili 0
else cat "$C/ice_aktar.txt"; yaz not "tür yükleme hatası"; bitir basarisiz 20; fi
