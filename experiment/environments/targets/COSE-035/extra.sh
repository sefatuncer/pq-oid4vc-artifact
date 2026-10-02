# COSE-035 additional record (information): ML-DSA traces in the cose-lib source and PHP openssl constants. NO signature verification.
echo "== ML-DSA kaynak izleri (grep; bilgi)"
grep -rn -i -E "ml-?dsa|mldsa|ml_dsa|dilithium" /tmp/p/vendor/web-auth/cose-lib/src 2>/dev/null | head -25 | tee "$C/mldsa-source.txt"
echo "== PHP openssl sabitlerinde ML/PQ adları (ortam; bilgi)"
php -r '$c = get_defined_constants(true)["openssl"] ?? []; foreach ($c as $k => $v) if (preg_match("/ML|DSA|PQ|KEM/i", $k)) echo "$k\n";' | tee "$C/php-openssl-constants.txt"
yaz not "cbor-php kurulan: $(php -r '$l=json_decode(file_get_contents("/tmp/p/composer.lock"),true); foreach($l["packages"] as $p) if($p["name"]=="spomky-labs/cbor-php") echo $p["version"];')"
