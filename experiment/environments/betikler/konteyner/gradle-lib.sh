#!/usr/bin/env bash
# Library resolution with Gradle (Gradle module metadata for Kotlin multiplatform artefacts):
# canonical coordinate → JVM variant; the verification metadata (sha256) is written as a lock; classes are loaded without initialisation.
# Input (kur.sh): GAV (g:a:v), HEDEF_JAR (e.g. vck-jvm-7.0.1.jar), [ANAHTAR]. NO signature verification.
set -uo pipefail
source /b/ortak.sh
: "${GAV:?}"; : "${HEDEF_JAR:?}"
IFS=: read -r G A V <<< "$GAV"
yaz ekosistem "maven (Gradle modül meta verisiyle)"; yaz paket "$G:$A"; yaz istenen_surum "$V"
yaz arac "$(java -version 2>&1 | head -1); $(gradle --version 2>/dev/null | grep -E '^Gradle')"
P=/tmp/p; rm -rf $P; mkdir -p $P; cd $P
echo 'rootProject.name = "ortam-deneme"' > settings.gradle.kts
cat > build.gradle.kts <<KTS
plugins { java }
repositories { mavenCentral() }
dependencies { implementation("$GAV") }
tasks.register<Sync>("kopyala") { from(configurations.runtimeClasspath); into(layout.buildDirectory.dir("lib")) }
KTS
cp settings.gradle.kts build.gradle.kts "$C/"
echo "== gradle kopyala (--write-verification-metadata sha256)"
if ! gradle --no-daemon -q --write-verification-metadata sha256 kopyala; then yaz not "Gradle çözümleme başarısız"; bitir basarisiz 10; fi
gradle --no-daemon -q dependencies --configuration runtimeClasspath > "$C/dependencies.txt" 2>&1 || true
cp gradle/verification-metadata.xml "$C/"
(cd build/lib && sha256sum *.jar | sort -k2) > "$C/jar-sha256.txt"
yaz kilit_dosyasi "verification-metadata.xml (Gradle, sha256) + jar-sha256.txt"
yaz kilit_sha256 "$(ozet "$C/verification-metadata.xml")"
yaz bagimlilik_sayisi "$(grep -c . "$C/jar-sha256.txt")"
J="build/lib/$HEDEF_JAR"
[ -f "$J" ] || { yaz not "hedef JAR yok: $HEDEF_JAR"; bitir basarisiz 11; }
yaz paket_ozeti "sha256:$(ozet "$J") ($HEDEF_JAR)"
yaz kurulan_surum "$V"
cp /b/KontrolYukle.java . && javac -d . KontrolYukle.java
echo "== bağlama kontrolü (sınıflar ilklendirilmeden yüklenir; imza doğrulama YOK)"
if java -cp "build/lib/*:." KontrolYukle "$J" ${ANAHTAR:-} > "$C/ice_aktar.txt" 2>&1; then cat "$C/ice_aktar.txt"; bitir basarili 0
else cat "$C/ice_aktar.txt"; yaz not "bağlama hatası"; bitir basarisiz 20; fi
