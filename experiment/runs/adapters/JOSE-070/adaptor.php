<?php
// JOSE-070 firebase/php-jwt 7.2.0 adaptörü. Belgeli genel API: JWT::decode(string $jwt, Key|array<kid,Key>, &$headers),
// JWK::parseKey(array $jwk, ?string $defaultAlg), Key(material, alg), JWT::$timestamp (sahte saat). Eşleme: MAPPING.md.
declare(strict_types=1);
require '/opt/a/vendor/autoload.php';
require __DIR__ . '/ortak.php';

use Firebase\JWT\BeforeValidException;
use Firebase\JWT\ExpiredException;
use Firebase\JWT\JWK;
use Firebase\JWT\JWT;
use Firebase\JWT\Key;
use Firebase\JWT\SignatureInvalidException;

// Bataryadaki algoritmalardan yerel destek: JWT::$supported_algs (ES256, ES384, EdDSA; Ed25519 etiketi, ML-DSA, composite yok)
const KUTUPHANE_ALGLERI = ['ES256', 'ES384', 'EdDSA'];
const DESTEKLI_BICIM = ['compact'];
const API = 'JWT::decode($jwt, [kid => JWK::parseKey($jwk, alg(anahtar_turu)) | alg ∈ W] (kid yoksa tek Key), $hdr); JWT::$timestamp = simdi';

function sinifla(\Throwable $e, ?string $alg, array $izin): string
{
    $m = $e->getMessage();
    if ($e instanceof SignatureInvalidException) return 'imza-gecersiz';
    if ($e instanceof ExpiredException || $e instanceof BeforeValidException) return 'zaman';
    if (str_contains($m, 'Algorithm not supported')) return 'alg-desteklenmiyor';
    if (str_contains($m, 'Incorrect key for this algorithm')) return 'alg-anahtar-uyusmazligi';
    if (str_contains($m, '"kid"') || str_contains($m, 'Key may not be empty')) {
        // W, anahtar–alg bağlamasıyla kurulur: W dışındaki alg'ın anahtarı yapılandırılmaz → kid bulunamaz.
        return ($alg !== null && !in_array($alg, $izin, true)) ? 'alg-izin-disi' : 'anahtar-bulunamadi';
    }
    if (preg_match('/segments|encoding|Payload|Empty algorithm|Malformed|Syntax/i', $m)) return 'ayristirma';
    return 'istisna-diger';
}

function dogrula(array $is): array
{
    if (!in_array($is['serilestirme'], DESTEKLI_BICIM, true)) return Ortak::b6(API);
    $dg = Ortak::girdi($is['vektor_id']);
    $jwt = trim((string) file_get_contents(Ortak::vektorYolu($is['dosya'])));
    $pol = Ortak::politika($is, KUTUPHANE_ALGLERI);
    if ($pol['taban'] === 'L4-YOL') return Ortak::ifadeEdilemedi('x5c/x5chain yol sinifi politikasi (L4-YOL, B2) icin belgeli API yok', API);
    $izin = Ortak::tekImzaIzin($pol) ?? KUTUPHANE_ALGLERI; // VARSAYILAN: php-jwt'de alg her zaman anahtara bağlı
    $baslik = json_decode(Ortak::b64d(explode('.', $jwt)[0]), true) ?: [];
    $alg = is_string($baslik['alg'] ?? null) ? $baslik['alg'] : null;
    [$jwk, $anahtarYolu] = Ortak::jwkSec($baslik, $dg);
    JWT::$timestamp = (int) ($dg['simdi'] ?? time()); // sözleşme §2.1: saat = simdi
    $notlar = [];
    // Anahtar–alg bağlaması (php-jwt'nin tek politika mekanizması; Key(material, alg)): vektörün JWKS'indeki her JWK,
    // anahtar türünün doğal alg'ı W içindeyse JWK::parseKey ile Key'e çevrilir → [kid => Key] (README "JWKs" deseni).
    // Başlıkta kid yoksa (REQ/TSL x5c'li, DPoP) seçilen JWK tek Key olarak verilir.
    $anahtarlar = [];
    $kaynak = ($anahtarYolu === 'jwk-basligi' || empty($dg['jwks'])) ? ($jwk ? [$jwk] : []) : Ortak::jwks($dg['jwks'])['keys'];
    foreach ($kaynak as $j) {
        $dalg = Ortak::dogalAlg($j, $is['kol']);
        if ($dalg === null || !in_array($dalg, $izin, true)) continue;
        try {
            $k = JWK::parseKey($j, $dalg);
            if ($k instanceof Key) $anahtarlar[$j['kid'] ?? ''] = $k;
        } catch (\Throwable $e) {
            if ($jwk !== null && ($j['kid'] ?? null) === ($jwk['kid'] ?? null)) $notlar[] = 'JWK::parseKey: ' . get_class($e) . ': ' . $e->getMessage();
        }
    }
    if ($jwk !== null && !$notlar && !isset($anahtarlar[$jwk['kid'] ?? ''])
        && in_array(Ortak::dogalAlg($jwk, $is['kol']), $izin, true)) {
        $notlar[] = 'JWK::parseKey: kty ' . ($jwk['kty'] ?? '?') . ' icin Key uretilmedi (desteklenmiyor)';
    }
    if (isset($baslik['kid'])) {
        $anahtarArg = $anahtarlar;
        $anahtarYolu = 'JWKS';
    } else {
        $sec = $jwk !== null ? ($anahtarlar[$jwk['kid'] ?? ''] ?? null) : null;
        $anahtarArg = $sec ?? $anahtarlar;
    }
    $hdr = new \stdClass();
    try {
        JWT::decode($jwt, $anahtarArg, $hdr);
        return ['sonuc_ham' => 'kabul', 'hata_sinifi' => null, 'hata_ozeti' => null, 'api_yolu' => API, 'anahtar_yolu' => $anahtarYolu,
                'dogrulanan' => [['sira' => 0, 'alg' => (string) ($hdr->alg ?? ''), 'sonuc' => 'gecerli']]];
    } catch (\UnexpectedValueException | \DomainException | \InvalidArgumentException $e) {
        $oz = get_class($e) . ': ' . $e->getMessage() . ($notlar ? ' | ' . implode(' | ', $notlar) : '');
        $sinif = sinifla($e, $alg, $izin);
        if ($sinif === 'anahtar-bulunamadi' && $notlar) $sinif = 'alg-desteklenmiyor'; // anahtar türü kütüphanede yok
        return ['sonuc_ham' => 'red', 'hata_sinifi' => $sinif, 'hata_ozeti' => $oz, 'api_yolu' => API, 'anahtar_yolu' => $anahtarYolu];
    } catch (\Throwable $e) {
        return ['sonuc_ham' => 'istisna', 'hata_sinifi' => 'istisna-diger', 'hata_ozeti' => get_class($e) . ': ' . $e->getMessage(),
                'api_yolu' => API, 'anahtar_yolu' => $anahtarYolu];
    }
}

Ortak::kos($argv, 'dogrula');
