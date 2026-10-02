<?php
// Adapter for COSE-035 web-auth/cose-lib 4.8.2 (+ spomky-labs/cbor-php 3.4.2).
// cose-lib is a primitives library: the README section "Verifying a COSE_Sign1 Signature" gives the documented verifier
// as a pattern written by the caller (Decoder → CoseHeaders::fromMessage → alg check → crit check → Signature1 →
// $algorithm->verify). The adapter follows this pattern EXACTLY; the allow-list W = Algorithm\Manager (Manager::has/get).
// Mapping and reasons: MAPPING.md.
declare(strict_types=1);
require '/opt/a/vendor/autoload.php';
require __DIR__ . '/ortak.php';

use CBOR\Decoder;
use CBOR\ListObject;
use CBOR\OtherObject\NullObject;
use CBOR\StringStream;
use CBOR\Tag\CoseSign1Tag;
use CBOR\Tag\CoseSignTag;
use Cose\Algorithm\Manager;
use Cose\Algorithm\Signature\ECDSA\ES256;
use Cose\Algorithm\Signature\ECDSA\ES384;
use Cose\Algorithm\Signature\EdDSA\EdDSA;
use Cose\Algorithm\Signature\FullySpecified\Ed25519;
use Cose\Key\Key;
use Cose\Signature\CoseSignature;
use Cose\Signature\Signature;
use Cose\Signature\Signature1;
use Cose\Structure\CoseHeaders;

// JOSE name → COSE id (BATARYA-ESLEME §3; RFC 9053, RFC 9864, RFC 9964, composite -04 §7.2 requested -55)
const COSE_ID = ['ES256' => -7, 'ES384' => -35, 'EdDSA' => -8, 'Ed25519' => -19, 'ML-DSA-65' => -49, 'ML-DSA-65-ES256' => -55];
// Native algorithms of 4.8.2 that intersect with the battery (src/Algorithm/Signature: ECDSA, EdDSA, FullySpecified; NO MLDSA folder)
const KUTUPHANE_ALGLERI = ['ES256', 'ES384', 'EdDSA', 'Ed25519'];
const DESTEKLI_BICIM = ['COSE_Sign1', 'COSE_Sign'];
const ANLASILAN_ETIKETLER = [1, 2]; // README pattern: 1 = alg, 2 = crit
const API = 'Decoder::decode → CoseHeaders::fromMessage → Manager(W)::has(alg) → crit → Signature1|Signature::create → Manager::get(alg)->verify(sig_structure, Key::createFromData(COSE_Key), sig)';

function algoritma(string $ad): ?\Cose\Algorithm\Algorithm
{
    return match ($ad) {
        'ES256' => ES256::create(), 'ES384' => ES384::create(), 'EdDSA' => new EdDSA(), 'Ed25519' => Ed25519::create(),
        default => null,
    };
}

final class Red extends \RuntimeException
{
    public function __construct(public readonly string $sinif, string $m) { parent::__construct($m); }
}

function coseAnahtari(array $dg, ?string $kidHex): Key
{
    $harita = $dg['cose_key_hex'] ?? [];
    if (is_string($harita)) $harita = json_decode($harita, true) ?: [];
    if ($kidHex === null && is_array($dg['cose_kid_hex'] ?? null) && count($dg['cose_kid_hex']) === 1) $kidHex = $dg['cose_kid_hex'][0];
    if ($kidHex === null || !isset($harita[$kidHex])) throw new Red('anahtar-bulunamadi', "COSE_Key bulunamadi (kid=$kidHex)");
    $veri = Decoder::create()->decode(new StringStream(hex2bin($harita[$kidHex])))->normalize();
    try {
        return Key::createFromData($veri); // Ec2Key / OkpKey / RsaKey / SymmetricKey by kty
    } catch (\Throwable $e) {
        throw new Red('alg-desteklenmiyor', 'Key::createFromData: ' . $e->getMessage());
    }
}

function algKontrol(CoseHeaders $h, Manager $m, array $izin): int
{
    $a = $h->getProtectedHeaderParameter(1);
    if ($a === null) throw new Red('ayristirma', 'korumali baslikta alg yok');
    $id = $a->normalize();
    if (!is_int($id) && !(is_string($id) && preg_match('/^-?\d+$/', $id))) throw new Red('alg-desteklenmiyor', 'alg tamsayi degil: ' . json_encode($id));
    $id = (int) $id;
    if (!$m->has($id)) {
        $ad = array_search($id, COSE_ID, true);
        $sinif = ($ad !== false && in_array($ad, KUTUPHANE_ALGLERI, true)) ? 'alg-izin-disi' : 'alg-desteklenmiyor';
        throw new Red($sinif, "alg $id izin listesinde (Manager) yok");
    }
    $crit = $h->getProtectedHeaderParameter(2);
    if ($crit !== null) {
        if (!$crit instanceof ListObject) throw new Red('crit', 'crit dizi degil');
        foreach ($crit as $l) if (!in_array($l->normalize(), ANLASILAN_ETIKETLER, true)) throw new Red('crit', 'islenmeyen crit etiketi');
    }
    return $id;
}

function kidHex(CoseHeaders $h): ?string
{
    $k = $h->getHeaderParameter(4);
    return $k === null ? null : bin2hex((string) $k->normalize());
}

function dogrula(array $is): array
{
    if (!in_array($is['serilestirme'], DESTEKLI_BICIM, true)) return Ortak::b6(API);
    $dg = Ortak::girdi($is['vektor_id']);
    $pol = Ortak::politika($is, KUTUPHANE_ALGLERI);
    if ($pol['taban'] === 'L4-YOL') return Ortak::ifadeEdilemedi('x5c/x5chain yol sinifi politikasi (L4-YOL, B2) icin belgeli API yok', API);
    $izin = Ortak::tekImzaIzin($pol) ?? KUTUPHANE_ALGLERI;
    $m = Manager::create();
    foreach ($izin as $ad) if (($a = algoritma($ad)) !== null) $m->add($a);
    try {
        try {
            $mesaj = Decoder::create()->decode(new StringStream((string) file_get_contents(Ortak::vektorYolu($is['dosya']))));
        } catch (\Throwable $e) {
            throw new Red('ayristirma', 'CBOR: ' . $e->getMessage());
        }
        if ($mesaj instanceof CoseSign1Tag) {
            $h = CoseHeaders::fromMessage($mesaj);
            $id = algKontrol($h, $m, $izin);
            $yuk = $mesaj->getPayload();
            if ($yuk instanceof NullObject) throw new Red('ayristirma', 'ayrik yuk');
            $anahtar = coseAnahtari($dg, kidHex($h));
            $yapi = Signature1::create($mesaj->getProtectedHeader(), $yuk);
            $imza = $mesaj->getSignature()->getValue();
        } elseif ($mesaj instanceof CoseSignTag) {
            $imzalar = CoseSignature::all($mesaj->getSignatures());
            if (count($imzalar) !== 1 && $pol['taban'] !== 'VARSAYILAN') {
                // No documented option for a multi-signer rule (P0/P1/R); a loop over every signer would be the caller's code (B4).
                return Ortak::ifadeEdilemedi('COSE_Sign coklu imzaci kurali (P0/P1/R) icin API secenegi yok', API);
            }
            if (count($imzalar) !== 1) return Ortak::ifadeEdilemedi('VARSAYILAN: COSE_Sign coklu imzaci icin varsayilan dogrulayici yok', API);
            $govde = CoseHeaders::fromMessage($mesaj);
            $s = $imzalar[0];
            $id = algKontrol($s->headers(), $m, $izin);
            $yuk = $mesaj->getPayload();
            if ($yuk instanceof NullObject) throw new Red('ayristirma', 'ayrik yuk');
            $anahtar = coseAnahtari($dg, kidHex($s->headers()));
            $yapi = Signature::create($govde->getProtectedHeader(), $s->getProtectedHeader(), $yuk);
            $imza = $s->getSignature()->getValue();
        } else {
            throw new Red('ayristirma', 'COSE_Sign1/COSE_Sign degil: ' . get_class($mesaj));
        }
        try {
            $ok = $m->get($id)->verify((string) $yapi, $anahtar, $imza);
        } catch (\Throwable $e) {
            throw new Red('alg-anahtar-uyusmazligi', get_class($e) . ': ' . $e->getMessage());
        }
        if (!$ok) throw new Red('imza-gecersiz', 'verify() false');
        $ad = array_search($id, COSE_ID, true);
        return ['sonuc_ham' => 'kabul', 'hata_sinifi' => null, 'hata_ozeti' => null, 'api_yolu' => API, 'anahtar_yolu' => 'COSE_Key',
                'dogrulanan' => [['sira' => 0, 'alg' => $ad === false ? (string) $id : $ad, 'sonuc' => 'gecerli']]];
    } catch (Red $r) {
        return ['sonuc_ham' => 'red', 'hata_sinifi' => $r->sinif, 'hata_ozeti' => $r->getMessage(), 'api_yolu' => API, 'anahtar_yolu' => 'COSE_Key'];
    } catch (\Throwable $e) {
        return ['sonuc_ham' => 'istisna', 'hata_sinifi' => 'istisna-diger', 'hata_ozeti' => get_class($e) . ': ' . $e->getMessage(), 'api_yolu' => API, 'anahtar_yolu' => 'COSE_Key'];
    }
}

Ortak::kos($argv, 'dogrula');
