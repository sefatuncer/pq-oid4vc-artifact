#!/usr/bin/env bash
# Maven Central target: resolve the dependencies (--strict-checksums), record the JAR digests, load the classes without initialisation.
# Input (kur.sh): HEDEF_GAV (g:a:v), [EK_GAV "g:a:v ..."], [EK_KONTROL "jar-name.jar ..."], [ANAHTAR "class ..."]
# NO signature verification.
set -uo pipefail
source /b/ortak.sh
: "${HEDEF_GAV:?}"
IFS=: read -r G A V <<< "$HEDEF_GAV"
yaz ekosistem maven; yaz paket "$G:$A"; yaz istenen_surum "$V"
yaz arac "$(java -version 2>&1 | head -1); $(mvn -v 2>&1 | head -1 | cut -d'(' -f1)"
P=/tmp/p; rm -rf $P; mkdir -p $P; cd $P
{ echo '<project xmlns="http://maven.apache.org/POM/4.0.0"><modelVersion>4.0.0</modelVersion>'
  echo '<groupId>pq.a09</groupId><artifactId>ortam-deneme</artifactId><version>0</version><packaging>jar</packaging><dependencies>'
  for gav in $HEDEF_GAV ${EK_GAV:-}; do IFS=: read -r g a v <<< "$gav"
    echo "<dependency><groupId>$g</groupId><artifactId>$a</artifactId><version>$v</version></dependency>"; done
  echo '</dependencies></project>'; } > pom.xml
cp pom.xml "$C/"
DP=org.apache.maven.plugins:maven-dependency-plugin:3.8.1
echo "== mvn copy-dependencies ($HEDEF_GAV ${EK_GAV:-})"
if ! mvn -B -ntp --strict-checksums $DP:copy-dependencies -DoutputDirectory=$P/lib -DincludeScope=runtime; then
  yaz not "Maven çözümleme başarısız"; bitir basarisiz 10; fi
mvn -B -ntp -q $DP:tree -DoutputFile="$C/dependency-tree.txt" || true
(cd lib && sha256sum *.jar | sort -k2) > "$C/jar-sha256.txt"
yaz kilit_dosyasi "jar-sha256.txt (çalışma zamanı JAR'ları; Maven --strict-checksums)"
yaz kilit_sha256 "$(ozet "$C/jar-sha256.txt")"
yaz bagimlilik_sayisi "$(grep -c . "$C/jar-sha256.txt")"
J="lib/$A-$V.jar"
[ -f "$J" ] || { yaz not "hedef JAR yok: $J"; bitir basarisiz 11; }
yaz paket_ozeti "sha256:$(ozet "$J") ($A-$V.jar)"
yaz kurulan_surum "$V"
POM=/root/.m2/repository/$(echo "$G" | tr . /)/$A/$V/$A-$V.pom
[ -f "$POM" ] && { cp "$POM" "$C/"; T=$(tr -d '\n' < "$POM" | grep -o '<scm>.*</scm>' | grep -o '<tag>[^<]*</tag>' | sed 's/<[^>]*>//g'); [ -n "$T" ] && yaz not "POM scm/tag=$T"; }
cp /b/KontrolYukle.java . && javac -d . KontrolYukle.java
echo "== bağlama kontrolü (sınıflar ilklendirilmeden yüklenir; imza doğrulama YOK)"
RC=0
for j in "$J" ${EK_KONTROL:+$(for x in $EK_KONTROL; do echo "lib/$x"; done)}; do
  java -cp "lib/*:." KontrolYukle "$j" ${ANAHTAR:-} >> "$C/ice_aktar.txt" 2>&1 || RC=$?
  ANAHTAR=""   # the key classes are checked only in the first JAR round
done
cat "$C/ice_aktar.txt"
[ $RC -eq 0 ] && bitir basarili 0 || { yaz not "bağlama hatası"; bitir basarisiz 20; }
