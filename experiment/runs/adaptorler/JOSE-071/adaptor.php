<?php
// JOSE-071 lcobucci/jwt 5.6.0 adaptörü. Belgeli genel API: Token\Parser(JoseEncoder)->parse(), Validation\Validator->assert(
// $token, SignedWithOneInSet(SignedWithUntilDate(Signer, Key, validUntil, clock)...), LooseValidAt(clock)),
// Signer\Ecdsa\Sha256|Sha384, Signer\Eddsa, Signer\Key\InMemory::plainText. Eşleme ve gerekçeler: ESLEME.md.
declare(strict_types=1);
require '/opt/a/vendor/autoload.php';
require __DIR__ . '/ortak.php';

use Lcobucci\JWT\Encoding\JoseEncoder;
use Lcobucci\JWT\Signer;
use Lcobucci\JWT\Signer\Key\InMemory;
use Lcobucci\JWT\Token\Parser;
use Lcobucci\JWT\Validation\Constraint\LooseValidAt;
use Lcobucci\JWT\Validation\Constraint\SignedWithOneInSet;
use Lcobucci\JWT\Validation\Constraint\SignedWithUntilDate;
use Lcobucci\JWT\Validation\NoConstraintsGiven;
use Lcobucci\JWT\Validation\RequiredConstraintsViolated;
use Lcobucci\JWT\Validation\Validator;
use Psr\Clock\ClockInterface;

// Bataryadaki algoritmalardan yerel destek (src/Signer: Ecdsa\Sha256/384/512, Eddsa, Rsa, Hmac, Blake2b; ML-DSA yok)
const KUTUPHANE_ALGLERI = ['ES256', 'ES384', 'EdDSA'];
const DESTEKLI_BICIM = ['compact'];
const API = 'Validator::assert(Parser::parse($jwt), SignedWithOneInSet(SignedWithUntilDate(Signer(a), InMemory::plainText(anahtar), ...) | a ∈ W), LooseValidAt(saat=simdi))';

function imzalayici(string $alg): ?Signer
{
    return match ($alg) {
        'ES256' => new Signer\Ecdsa\Sha256(),
        'ES384' => new Signer\Ecdsa\Sha384(),
        'EdDSA' => new Signer\Eddsa(),
        default => null,
    };
}

// lcobucci'de JWK API'si yok: JWK, kütüphanenin beklediği biçime adaptörde çevrilir (anahtar_yolu = "dogrudan").
// EC → SubjectPublicKeyInfo PEM (RFC 5480 sabit öneki + 04||x||y); OKP Ed25519 → ham 32 bayt (Eddsa sodium bekler).
function anahtarMalzemesi(array $jwk): ?string
{
    $kty = $jwk['kty'] ?? '';
    if ($kty === 'EC') {
        $onek = ['P-256' => '3059301306072a8648ce3d020106082a8648ce3d030107034200',
                 'P-384' => '3076301006072a8648ce3d020106052b81040022036200'][$jwk['crv'] ?? ''] ?? null;
        if ($onek === null) return null;
        $der = hex2bin($onek) . "\x04" . Ortak::b64d($jwk['x']) . Ortak::b64d($jwk['y']);
        return "-----BEGIN PUBLIC KEY-----\n" . chunk_split(base64_encode($der), 64, "\n") . "-----END PUBLIC KEY-----\n";
    }
    if ($kty === 'OKP') return Ortak::b64d($jwk['x'] ?? '');
    if ($kty === 'AKP') return Ortak::b64d($jwk['pub'] ?? '');
    return null;
}

// hata_ozeti 200 karakterle kesildiği için kütüphanenin sabit giriş cümleleri kısaltılır (ihlal metinleri korunur).
function kisalt(string $m): string
{
    return str_replace(["\n", 'The token violates some mandatory constraints, details:', 'It was not possible to verify the signature of the token, reasons:'],
                       [' ', 'ihlaller:', 'imza kumesi:'], $m);
}

function sinifla(\Throwable $e, ?string $alg, array $izin): string
{
    $m = $e->getMessage();
    if ($e instanceof RequiredConstraintsViolated) {
        if (str_contains($m, 'Token signature mismatch')) return 'imza-gecersiz';
        if (preg_match('/issued in the future|cannot be used yet|is expired/i', $m)) return 'zaman';
        if (str_contains($m, 'Token signer mismatch')) {
            if ($alg === null || !in_array($alg, KUTUPHANE_ALGLERI, true)) return 'alg-desteklenmiyor';
            return in_array($alg, $izin, true) ? 'alg-anahtar-uyusmazligi' : 'alg-izin-disi';
        }
        return 'istisna-diger';
    }
    if ($e instanceof NoConstraintsGiven) return 'alg-desteklenmiyor';
    if ($e instanceof Signer\InvalidKeyProvided || $e instanceof Signer\Ecdsa\ConversionFailed) return 'alg-anahtar-uyusmazligi';
    if ($e instanceof \Lcobucci\JWT\Token\InvalidTokenStructure || $e instanceof \Lcobucci\JWT\Encoding\CannotDecodeContent
        || $e instanceof \Lcobucci\JWT\Token\UnsupportedHeaderFound) return 'ayristirma';
    return 'istisna-diger';
}

function dogrula(array $is): array
{
    if (!in_array($is['serilestirme'], DESTEKLI_BICIM, true)) return Ortak::b6(API);
    $dg = Ortak::girdi($is['vektor_id']);
    $jwt = trim((string) file_get_contents(Ortak::vektorYolu($is['dosya'])));
    $pol = Ortak::politika($is, KUTUPHANE_ALGLERI);
    if ($pol['taban'] === 'L4-YOL') return Ortak::ifadeEdilemedi('x5c/x5chain yol sinifi politikasi (L4-YOL, B2) icin belgeli API yok', API);
    $izin = Ortak::tekImzaIzin($pol) ?? KUTUPHANE_ALGLERI; // VARSAYILAN: lcobucci'de imza kısıtı her zaman açıkça verilir
    $baslik = json_decode(Ortak::b64d(explode('.', $jwt)[0]), true) ?: [];
    $alg = is_string($baslik['alg'] ?? null) ? $baslik['alg'] : null;
    [$jwk, $anahtarYolu] = Ortak::jwkSec($baslik, $dg);
    $anahtarYolu = $anahtarYolu === 'jwk-basligi' ? 'jwk-basligi' : 'dogrudan';
    if ($jwk === null || ($malzeme = anahtarMalzemesi($jwk)) === null || $malzeme === '') {
        return ['sonuc_ham' => 'red', 'hata_sinifi' => 'anahtar-bulunamadi', 'hata_ozeti' => 'dogrulama anahtari secilemedi (kid/alg_kid)',
                'api_yolu' => API, 'anahtar_yolu' => $anahtarYolu];
    }
    $saat = new class ((int) ($dg['simdi'] ?? time())) implements ClockInterface {
        public function __construct(private int $t) {}
        public function now(): \DateTimeImmutable { return new \DateTimeImmutable('@' . $this->t); }
    };
    // W'deki her alg için (Signer, anahtar) çifti; lcobucci SignedWith önce başlık alg = Signer::algorithmId() denetler.
    $imzaKisitlari = [];
    foreach ($izin as $a) {
        $s = imzalayici($a);
        if ($s !== null) $imzaKisitlari[] = new SignedWithUntilDate($s, InMemory::plainText($malzeme), new \DateTimeImmutable('9999-12-31'), $saat);
    }
    $kisitlar = $imzaKisitlari ? [new SignedWithOneInSet(...$imzaKisitlari), new LooseValidAt($saat)] : [];
    try {
        $token = (new Parser(new JoseEncoder()))->parse($jwt);
        (new Validator())->assert($token, ...$kisitlar); // kısıt yoksa kütüphane NoConstraintsGiven atar
        return ['sonuc_ham' => 'kabul', 'hata_sinifi' => null, 'hata_ozeti' => null, 'api_yolu' => API, 'anahtar_yolu' => $anahtarYolu,
                'dogrulanan' => [['sira' => 0, 'alg' => (string) $token->headers()->get('alg'), 'sonuc' => 'gecerli']]];
    } catch (\Lcobucci\JWT\Exception $e) {
        return ['sonuc_ham' => 'red', 'hata_sinifi' => sinifla($e, $alg, $izin), 'hata_ozeti' => get_class($e) . ': ' . kisalt($e->getMessage()),
                'api_yolu' => API, 'anahtar_yolu' => $anahtarYolu];
    } catch (\Throwable $e) {
        return ['sonuc_ham' => 'istisna', 'hata_sinifi' => sinifla($e, $alg, $izin) === 'istisna-diger' ? 'istisna-diger' : sinifla($e, $alg, $izin),
                'hata_ozeti' => get_class($e) . ': ' . $e->getMessage(), 'api_yolu' => API, 'anahtar_yolu' => $anahtarYolu];
    }
}

Ortak::kos($argv, 'dogrula');
