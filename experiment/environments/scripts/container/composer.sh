#!/bin/sh
# Packagist target: composer require with a pinned version, record composer.lock, load all classes of the target package.
# Input (install.sh): PAKET (vendor/name), SURUM. NO signature verification.
set -uo pipefail
. /b/common.sh
: "${PAKET:?}"; : "${SURUM:?}"
yaz ekosistem packagist; yaz paket "$PAKET"; yaz istenen_surum "$SURUM"
yaz arac "$(php -v | head -1 | cut -d'(' -f1); $(composer --version 2>/dev/null | cut -d' ' -f1-3); php-openssl $(php -r 'echo OPENSSL_VERSION_TEXT;')"
P=/tmp/p; rm -rf $P; mkdir -p $P; cd $P
echo '{"name":"pq-a09/ortam-deneme","type":"project","config":{"platform-check":true,"preferred-install":"dist"}}' > composer.json
echo "== composer require $PAKET:${SURUM#v}"
if ! composer require --no-progress --prefer-dist --optimize-autoloader "$PAKET:${SURUM#v}" ${EK_PAKET:-}; then
  yaz not "composer require başarısız"; bitir basarisiz 10; fi
cp composer.json composer.lock "$C/"
yaz kilit_dosyasi composer.lock; yaz kilit_sha256 "$(ozet composer.lock)"
php -r '$l=json_decode(file_get_contents("composer.lock"),true); echo count($l["packages"]);' > /tmp/n; yaz bagimlilik_sayisi "$(cat /tmp/n)"
php -r '
$l = json_decode(file_get_contents("composer.lock"), true);
foreach ($l["packages"] as $p) if ($p["name"] === getenv("PAKET")) {
  $f = fopen("/w/output/result.tsv", "a");
  fwrite($f, "kurulan_surum\t" . $p["version"] . "\n");
  fwrite($f, "commit\t" . ($p["dist"]["reference"] ?? $p["source"]["reference"] ?? "") . "\n");
  fwrite($f, "commit_kaynagi\tcomposer.lock dist.reference\n");
  fwrite($f, "lisans_kayit\t" . implode(",", $p["license"] ?? []) . "\n");
}'
Z=$(find /tmp/composer-cache/files/$PAKET -name '*.zip' | head -1)
[ -n "$Z" ] && yaz paket_ozeti "sha256:$(ozet "$Z") (Packagist dist zip)"
[ -n "${EK_PAKET:-}" ] && yaz not "ek paket (ortam düzeltmesi): $EK_PAKET"
[ -f /w/extra.sh ] && . /w/extra.sh
echo "== sınıf yükleme kontrolü (hedef paketin sınıfları otomatik yükleyiciyle yüklenir; imza doğrulama YOK)"
cat > /tmp/kontrol.php <<'PHP'
<?php
require '/tmp/p/vendor/autoload.php';
$paket = getenv('PAKET');
$cm = require '/tmp/p/vendor/composer/autoload_classmap.php';
$ok = 0; $hata = [];
foreach ($cm as $sinif => $dosya) {
    if (strpos(str_replace(chr(92), '/', $dosya), "/vendor/$paket/") === false) continue;
    try { if (class_exists($sinif) || interface_exists($sinif) || trait_exists($sinif) || enum_exists($sinif)) $ok++; else $hata[] = "$sinif: bulunamadı"; }
    catch (\Throwable $t) { $hata[] = "$sinif: " . get_class($t) . ' ' . $t->getMessage(); }
}
echo "paket=$paket sinif_yuklendi=$ok sinif_yuklenemedi=" . count($hata) . PHP_EOL;
foreach (array_slice($hata, 0, 15) as $h) echo "  yuklenemedi: $h" . PHP_EOL;
foreach (array_slice($argv, 1) as $k) echo "anahtar_sinif $k " . (class_exists($k) || interface_exists($k) ? 'OK' : 'HATA') . PHP_EOL;
exit(($ok > 0) ? 0 : 3);
PHP
if php /tmp/kontrol.php ${ANAHTAR:-} > "$C/import_check.txt" 2>&1 && ! grep -q "anahtar_sinif .* HATA" "$C/import_check.txt"; then
  cat "$C/import_check.txt"; bitir basarili 0
else cat "$C/import_check.txt"; yaz not "sınıf yükleme hatası"; bitir basarisiz 20; fi
