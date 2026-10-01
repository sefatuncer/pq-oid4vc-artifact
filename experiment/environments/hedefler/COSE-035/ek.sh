# COSE-035 ek kayıt (bilgi): cose-lib kaynağında ML-DSA izleri ve PHP openssl sabitleri. İmza doğrulama YOK.
echo "== ML-DSA kaynak izleri (grep; bilgi)"
grep -rn -i -E "ml-?dsa|mldsa|ml_dsa|dilithium" /tmp/p/vendor/web-auth/cose-lib/src 2>/dev/null | head -25 | tee "$C/mldsa-kaynak.txt"
echo "== PHP openssl sabitlerinde ML/PQ adları (ortam; bilgi)"
php -r '$c = get_defined_constants(true)["openssl"] ?? []; foreach ($c as $k => $v) if (preg_match("/ML|DSA|PQ|KEM/i", $k)) echo "$k\n";' | tee "$C/php-openssl-sabitleri.txt"
yaz not "cbor-php kurulan: $(php -r '$l=json_decode(file_get_contents("/tmp/p/composer.lock"),true); foreach($l["packages"] as $p) if($p["name"]=="spomky-labs/cbor-php") echo $p["version"];')"
