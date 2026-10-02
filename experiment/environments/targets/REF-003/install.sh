#!/usr/bin/env bash
# REF-003 — EUDI verifier endpoint: Gradle `assemble` from the source (commit pinned) (no tests run) + link check.
# Step 9 task 4a. NO signature verification; the service is NOT STARTED.
set -uo pipefail
source /b/common.sh
DEPO=https://github.com/eu-digital-identity-wallet/eudi-srv-verifier-endpoint
SHA=b1f17e8fe247504e7541a0121c1b6c9f1c7d4908
yaz ekosistem "kaynak (git) + Gradle"; yaz paket "eudi-srv-verifier-endpoint"; yaz istenen_surum "git:$SHA"
yaz arac "$(java -version 2>&1 | head -1); $(gradle --version 2>/dev/null | grep -E '^Gradle') (kurulu dağıtım)"
mkdir -p /tmp/src && cd /tmp/src
if ! { git_anonim init -q . && git_anonim remote add origin "$DEPO.git" && git_anonim fetch -q --depth 1 origin "$SHA" && git_anonim checkout -q FETCH_HEAD; }; then
  yaz sonuc erisilemedi; yaz not "anonim git fetch başarısız"; bitir basarisiz 30; fi
HEAD=$(git rev-parse HEAD); echo "HEAD=$HEAD"
yaz commit "$HEAD"; yaz commit_kaynagi "git checkout (CERCEVE son_commit_sha)"
yaz paket_ozeti "git-tree:$(git rev-parse 'HEAD^{tree}')"
W=$(grep distributionUrl gradle/wrapper/gradle-wrapper.properties | sed 's/.*gradle-\(.*\)-bin.zip/\1/')
yaz not "sarmalayıcı Gradle $W = kurulu Gradle; ./gradlew kullanılmadı (services.gradle.org indirmesi yok)"
echo "== gradle assemble (--write-verification-metadata sha256; test yok)"
if ! gradle --no-daemon --console=plain --write-verification-metadata sha256 assemble; then
  yaz not "gradle assemble başarısız"; bitir basarisiz 10; fi
cp gradle/verification-metadata.xml "$C/"
yaz kilit_dosyasi "verification-metadata.xml (Gradle, sha256; bu koşuda üretildi)"; yaz kilit_sha256 "$(ozet gradle/verification-metadata.xml)"
gradle --no-daemon -q dependencies --configuration runtimeClasspath > "$C/dependencies.txt" 2>&1 || true
ls -la build/libs | tee "$C/build-libs.txt"
BOOT=$(ls build/libs/*.jar | grep -v -- '-plain.jar' | head -1); PLAIN=$(ls build/libs/*-plain.jar | head -1)
yaz kurulan_surum "git:${HEAD:0:12} (proje sürümü $(grep '^version=' gradle.properties | cut -d= -f2))"
yaz not "bootJar sha256 $(ozet "$BOOT" | cut -c1-16)… (yeniden üretilebilir yapı iddia edilmez)"
mkdir -p /tmp/x && (cd /tmp/x && jar xf "/tmp/src/$BOOT")
(cd /tmp/x/BOOT-INF/lib && sha256sum *.jar | sort -k2) > "$C/jar-sha256.txt"
yaz bagimlilik_sayisi "$(grep -c . "$C/jar-sha256.txt")"
# MANIFEST lines are folded at 72 bytes (a continuation line starts with a space): unfold first (the script error in attempts 1-2)
BASLAT=$(tr -d '\r' < /tmp/x/META-INF/MANIFEST.MF | sed -e ':a' -e 'N' -e '$!ba' -e 's/\n //g' | grep -i '^Start-Class:' | cut -d' ' -f2)
echo "Start-Class=$BASLAT"
grep -o -E '(eudi-lib-jvm-sdjwt-kt[^ ]*|nimbus-jose-jwt[^ ]*|oauth2-oidc-sdk[^ ]*|bcprov[^ ]*|tink[^ ]*|cose-java[^ ]*)\.jar' "$C/jar-sha256.txt" | tr '\n' ' ' > "$C/crypto-dependencies.txt"
yaz not "kripto bağımlılıkları: $(cat "$C/crypto-dependencies.txt")"
cp /b/KontrolYukle.java /tmp/ && javac -d /tmp /tmp/KontrolYukle.java
echo "== bağlama kontrolü (uygulama sınıfları ilklendirilmeden yüklenir; servis başlatılmaz)"
if java -cp "/tmp/x/BOOT-INF/lib/*:/tmp/x/BOOT-INF/classes:/tmp" KontrolYukle "/tmp/src/$PLAIN" "$BASLAT" > "$C/import_check.txt" 2>&1; then
  cat "$C/import_check.txt"; bitir basarili 0
else cat "$C/import_check.txt"; yaz not "bağlama hatası"; bitir basarisiz 20; fi
