<?php

declare(strict_types=1);

// COSE-035 evidence-rule second attempt: web-auth/cose-lib 4.8.2 with spomky-labs/cbor-php 3.4.2
// (composer.json/composer.lock of the installation record). Own keys and objects only; no battery vectors.
// Run: composer install (frozen lock), then php attempt.php
// Form L4m (primary, COSE_Sign): R = {EdDSA}, W = {ES256, EdDSA}. Form L4c (supplement, COSE_Sign1).

require __DIR__ . '/vendor/autoload.php';

use CBOR\ByteStringObject;
use CBOR\Decoder;
use CBOR\ListObject;
use CBOR\MapItem;
use CBOR\MapObject;
use CBOR\NegativeIntegerObject;
use CBOR\StringStream;
use CBOR\Tag\CoseSign1Tag;
use CBOR\Tag\CoseSignTag;
use CBOR\TextStringObject;
use CBOR\UnsignedIntegerObject;
use Cose\Algorithm\Manager;
use Cose\Algorithm\Signature\ECDSA\ES256;
use Cose\Algorithm\Signature\EdDSA\EdDSA;
use Cose\Algorithm\Signature\Signature as SignatureAlgorithm;
use Cose\Key\Ec2Key;
use Cose\Key\Key;
use Cose\Key\OkpKey;
use Cose\Signature\CoseSignature;
use Cose\Signature\Signature;
use Cose\Signature\Signature1;
use Cose\Structure\CoseHeaders;
use Cose\Structure\HeaderMapHelper;

const ISS_MIG = 'https://issuer.example';
const ISS_LEG = 'https://legacy-issuer.example';

$GLOBALS['ok'] = 0;
$GLOBALS['n'] = 0;

function row(string $label, array $d, string $expect): void
{
    [$got, $why] = $d;
    $status = '-';
    if ($expect !== '-') {
        $GLOBALS['n']++;
        $status = $got === $expect ? 'OK' : 'MISMATCH';
        if ($status === 'OK') {
            $GLOBALS['ok']++;
        }
    }
    printf("  %-56s %-7s expect=%-7s %-9s %s\n", $label, $got, $expect, $status, $why);
}

/** Runs a verification and maps the outcome: true -> accept, false or exception -> reject (with the reason). */
function decide(callable $f): array
{
    try {
        return $f() ? ['accept', ''] : ['reject', 'signature invalid'];
    } catch (Throwable $t) {
        return ['reject', $t->getMessage()];
    }
}

// ---- own keys -----------------------------------------------------------------------------------------------------

function ecKey(array $extra = []): Ec2Key
{
    $k = openssl_pkey_new(['private_key_type' => OPENSSL_KEYTYPE_EC, 'curve_name' => 'prime256v1']);
    $e = openssl_pkey_get_details($k)['ec'];
    $pad = static fn (string $v): string => str_pad($v, 32, "\x00", STR_PAD_LEFT);

    return Ec2Key::create([
        Key::TYPE => Key::TYPE_EC2, Ec2Key::DATA_CURVE => Ec2Key::CURVE_P256,
        Ec2Key::DATA_X => $pad($e['x']), Ec2Key::DATA_Y => $pad($e['y']), Ec2Key::DATA_D => $pad($e['d']),
    ] + $extra);
}

function edKey(): OkpKey
{
    $seed = random_bytes(32);
    $kp = sodium_crypto_sign_seed_keypair($seed);

    return OkpKey::create([
        Key::TYPE => Key::TYPE_OKP, OkpKey::DATA_CURVE => OkpKey::CURVE_ED25519,
        OkpKey::DATA_X => sodium_crypto_sign_publickey($kp), OkpKey::DATA_D => $seed,
    ]);
}

/** Public part of a key, optionally with key parameters (alg = label 3, key_ops = label 4) added. */
function pub(Key $k, array $extra = []): Key
{
    if ($k instanceof Ec2Key) {
        return Ec2Key::create([Key::TYPE => Key::TYPE_EC2, Ec2Key::DATA_CURVE => Ec2Key::CURVE_P256,
            Ec2Key::DATA_X => $k->x(), Ec2Key::DATA_Y => $k->y()] + $extra);
    }

    return OkpKey::create([Key::TYPE => Key::TYPE_OKP, OkpKey::DATA_CURVE => OkpKey::CURVE_ED25519,
        OkpKey::DATA_X => $k->x()] + $extra);
}

// ---- own objects (documented creation path: README "Creating a COSE_Sign1 Message", examples/02) ------------------

function prot(int $alg, string $kid): ByteStringObject
{
    return HeaderMapHelper::encodeProtected(MapObject::create([
        MapItem::create(UnsignedIntegerObject::create(1), NegativeIntegerObject::create($alg)),
        MapItem::create(UnsignedIntegerObject::create(4), ByteStringObject::create($kid)),
    ]));
}

function claims(string $iss): ByteStringObject
{
    return ByteStringObject::create((string) MapObject::create([
        MapItem::create(UnsignedIntegerObject::create(1), TextStringObject::create($iss)),
    ]));
}

function sign1(SignatureAlgorithm $a, Key $k, string $kid, string $iss, bool $corrupt = false): string
{
    $p = prot($a::identifier(), $kid);
    $payload = claims($iss);
    $sig = $a->sign((string) Signature1::create($p, $payload), $k);
    if ($corrupt) {
        $sig[5] = chr(ord($sig[5]) ^ 0x01);
    }

    return (string) CoseSign1Tag::create(ListObject::create([$p, MapObject::create(), $payload, ByteStringObject::create($sig)]));
}

function entry(SignatureAlgorithm $a, Key $k, string $kid, ByteStringObject $body, ByteStringObject $payload, bool $corrupt = false): ListObject
{
    $p = prot($a::identifier(), $kid);
    $sig = $a->sign((string) Signature::create($body, $p, $payload), $k);
    if ($corrupt) {
        $sig[5] = chr(ord($sig[5]) ^ 0x01);
    }

    return ListObject::create([$p, MapObject::create(), ByteStringObject::create($sig)]);
}

function coseSign(ByteStringObject $body, ByteStringObject $payload, array $entries): string
{
    return (string) CoseSignTag::create(ListObject::create([$body, MapObject::create(), $payload, ListObject::create($entries)]));
}

// ---- documented verification path (Usage.md L233-295 for COSE_Sign1, L324-386 and examples/02 for COSE_Sign) ----
// The library has no message-level verify; the documented path is this caller code around the library objects
// that can be configured: the Manager (which algorithm identifiers resolve), the keys (alg / key_ops restrictions)
// and the Signature algorithm instances (key restrictions enforced or not).

function documentedSign1(string $bytes, Manager $m, array $keysByKid): bool
{
    $msg = Decoder::create()->decode(StringStream::create($bytes));
    if (! $msg instanceof CoseSign1Tag) {
        throw new RuntimeException('not a COSE_Sign1');
    }
    $h = CoseHeaders::fromMessage($msg);
    $algorithm = $m->get((int) $h->getProtectedHeaderParameter(1)?->normalize());
    $key = $keysByKid[(string) $h->getProtectedHeaderParameter(4)?->normalize()] ?? throw new RuntimeException('unknown kid');

    return $algorithm->verify((string) Signature1::create($msg->getProtectedHeader(), $msg->getPayload()), $key, $msg->getSignature()->getValue());
}

function documentedSign(string $bytes, Manager $m, array $keysByKid): bool
{
    $msg = Decoder::create()->decode(StringStream::create($bytes));
    if (! $msg instanceof CoseSignTag) {
        throw new RuntimeException('not a COSE_Sign');
    }
    foreach (CoseSignature::all($msg->getSignatures()) as $s) {
        $algorithm = $m->get((int) $s->getProtectedHeaderParameter(1)?->normalize());
        $key = $keysByKid[(string) $s->getProtectedHeaderParameter(4)?->normalize()] ?? throw new RuntimeException('unknown kid');
        $tbs = Signature::create($msg->getProtectedHeader(), $s->getProtectedHeader(), $msg->getPayload());
        if (! $algorithm->verify((string) $tbs, $key, $s->getSignature()->getValue())) {
            return false;
        }
    }

    return true;
}

// ---- own code, recorded as B4 only (the lines between the markers are counted, blank lines and comments excluded) --

// B4-BEGIN L4m
function ownRequiredSet(string $bytes, Manager $w, array $keysByKid, array $required): bool
{
    $msg = Decoder::create()->decode(StringStream::create($bytes));
    if (! $msg instanceof CoseSignTag) {
        throw new RuntimeException('not a COSE_Sign');
    }
    $seen = [];
    foreach (CoseSignature::all($msg->getSignatures()) as $s) {
        $alg = (int) $s->getProtectedHeaderParameter(1)?->normalize();
        $key = $keysByKid[(string) $s->getProtectedHeaderParameter(4)?->normalize()] ?? throw new RuntimeException('unknown kid');
        $tbs = Signature::create($msg->getProtectedHeader(), $s->getProtectedHeader(), $msg->getPayload());
        if (! $w->get($alg)->verify((string) $tbs, $key, $s->getSignature()->getValue())) {
            return false;
        }
        $seen[$alg] = true;
    }
    foreach ($required as $r) {
        if (! isset($seen[$r])) {
            throw new RuntimeException("required algorithm {$r} missing");
        }
    }

    return true;
}
// B4-END L4m

// B4-BEGIN L4c
function ownPerIssuer(string $bytes, array $records): bool
{
    $msg = Decoder::create()->decode(StringStream::create($bytes));
    if (! $msg instanceof CoseSign1Tag) {
        throw new RuntimeException('not a COSE_Sign1');
    }
    $h = CoseHeaders::fromMessage($msg);
    $kid = (string) $h->getProtectedHeaderParameter(4)?->normalize();
    $iss = Decoder::create()->decode(StringStream::create($msg->getPayload()->getValue()))->normalize()[1] ?? '';
    $rec = $records[$iss] ?? throw new RuntimeException('unknown issuer');
    $key = $rec['keys'][$kid] ?? throw new RuntimeException('kid not in the issuer record');
    $algorithm = $rec['manager']->get((int) $h->getProtectedHeaderParameter(1)?->normalize());

    return $algorithm->verify((string) Signature1::create($msg->getProtectedHeader(), $msg->getPayload()), $key, $msg->getSignature()->getValue());
}
// B4-END L4c

function b4Count(string $tag): int
{
    $in = false;
    $n = 0;
    foreach (file(__FILE__) as $line) {
        $t = trim($line);
        if ($t === "// B4-BEGIN {$tag}") {
            $in = true;
            continue;
        }
        if ($t === "// B4-END {$tag}") {
            break;
        }
        if ($in && $t !== '' && ! str_starts_with($t, '//') && ! str_starts_with($t, '/*') && ! str_starts_with($t, '*')) {
            $n++;
        }
    }

    return $n;
}

// =====================================================================================================================

$lock = json_decode(file_get_contents(__DIR__ . '/composer.lock'), true);
$ver = [];
foreach ($lock['packages'] as $p) {
    $ver[$p['name']] = $p['version'] . ' (' . substr($p['dist']['reference'] ?? '', 0, 12) . ')';
}
printf("== web-auth/cose-lib %s, spomky-labs/cbor-php %s; %s; %s; sodium %s; composer.lock sha256 %s\n",
    $ver['web-auth/cose-lib'], $ver['spomky-labs/cbor-php'], 'PHP ' . PHP_VERSION, OPENSSL_VERSION_TEXT,
    extension_loaded('sodium') ? 'loaded' : 'missing', hash_file('sha256', __DIR__ . '/composer.lock'));
printf("X = EdDSA (-8): EdDSA::isSupported() = %s\n", EdDSA::isSupported() ? 'true' : 'false');

echo "\n== 0. Public surface (reflection): public methods whose name contains 'verif', 'polic', 'allow', 'requir', 'issuer'\n";
$classes = [CoseSign1Tag::class, CoseSignTag::class, CoseSignature::class, Signature::class, Signature1::class,
    CoseHeaders::class, Manager::class, Cose\Algorithm\ManagerFactory::class, ES256::class, EdDSA::class,
    Cose\Algorithm\Signature\CertificateSignatureVerifier::class, Key::class];
foreach ($classes as $c) {
    $hits = [];
    foreach ((new ReflectionClass($c))->getMethods(ReflectionMethod::IS_PUBLIC) as $m) {
        if (preg_match('/verif|polic|allow|requir|issuer/i', $m->getName())) {
            $hits[] = $m->getName() . '(' . implode(', ', array_map(static fn ($p) => (string) $p->getType() . ' $' . $p->getName(), $m->getParameters())) . ')';
        }
    }
    printf("  %-52s %s\n", $c, $hits === [] ? '-' : implode('; ', $hits));
}

// keys: migrated issuer ES256 + Ed25519, legacy issuer ES256
$migA = ecKey();
$migX = edKey();
$legA = ecKey();
$es256 = ES256::create();
$eddsa = new EdDSA();
$keys = ['mig-es256' => pub($migA), 'mig-eddsa' => pub($migX), 'leg-es256' => pub($legA)];

// COSE_Sign1 objects
$s1MigA = sign1($es256, $migA, 'mig-es256', ISS_MIG);
$s1MigX = sign1($eddsa, $migX, 'mig-eddsa', ISS_MIG);
$s1LegA = sign1($es256, $legA, 'leg-es256', ISS_LEG);
$s1MigABad = sign1($es256, $migA, 'mig-es256', ISS_MIG, true);

// COSE_Sign objects (A = ES256, X = EdDSA, both migrated issuer keys)
$body = HeaderMapHelper::encodeProtected(MapObject::create());
$pl = claims(ISS_MIG);
$eA = entry($es256, $migA, 'mig-es256', $body, $pl);
$eX = entry($eddsa, $migX, 'mig-eddsa', $body, $pl);
$eXBad = entry($eddsa, $migX, 'mig-eddsa', $body, $pl, true);
$T = [
    'T1 A+X both valid' => [coseSign($body, $pl, [$eA, $eX]), 'accept'],
    'T2 A valid + X corrupted' => [coseSign($body, $pl, [$eA, $eXBad]), 'reject'],
    'T3 A only (X stripped)' => [coseSign($body, $pl, [$eA]), 'reject'],
    'T5 X only' => [coseSign($body, $pl, [$eX]), 'accept'],
    'T1 permuted (X first)' => [coseSign($body, $pl, [$eX, $eA]), 'accept'],
];

$mW = Manager::create()->add($es256, $eddsa);
$mR = Manager::create()->add($eddsa);

echo "\n== 1. Validity check (documented path, Manager W = {ES256, EdDSA}, keys by kid)\n";
row('V+ Sign1 migrated ES256', decide(fn () => documentedSign1($s1MigA, $mW, $keys)), 'accept');
row('V+ Sign1 migrated EdDSA', decide(fn () => documentedSign1($s1MigX, $mW, $keys)), 'accept');
row('V+ Sign1 legacy ES256', decide(fn () => documentedSign1($s1LegA, $mW, $keys)), 'accept');
row('V- Sign1 migrated ES256 corrupted', decide(fn () => documentedSign1($s1MigABad, $mW, $keys)), 'reject');
row('V+ COSE_Sign T1 both valid (documented loop)', decide(fn () => documentedSign($T['T1 A+X both valid'][0], $mW, $keys)), 'accept');
row('V- COSE_Sign T2 X corrupted (documented loop)', decide(fn () => documentedSign($T['T2 A valid + X corrupted'][0], $mW, $keys)), 'reject');

echo "\n== 2. L4m (primary form), R = {EdDSA}, W = {ES256, EdDSA}: documented COSE_Sign path, every configurable library object\n";
$configs = [
    'Manager W, keys without restrictions' => [$mW, $keys],
    'Manager R = {EdDSA}' => [$mR, $keys],
    'Manager W with key restrictions enforced, keys carry their own alg (3)' => [$mW->withKeyRestrictionsEnforced(),
        ['mig-es256' => pub($migA, [Key::ALG => -7]), 'mig-eddsa' => pub($migX, [Key::ALG => -8])]],
    'Manager R with key restrictions enforced, keys carry their own alg (3)' => [$mR->withKeyRestrictionsEnforced(),
        ['mig-es256' => pub($migA, [Key::ALG => -7]), 'mig-eddsa' => pub($migX, [Key::ALG => -8])]],
];
foreach ($configs as $name => [$m, $k]) {
    echo "configuration: {$name}\n";
    foreach ($T as $label => [$bytes, $expect]) {
        row($label, decide(fn () => documentedSign($bytes, $m, $k)), $expect);
    }
}
echo "recorded, not counted (relabelling the migrated classical key, README rule 'Key material'):\n";
echo "configuration: Manager W enforced, migrated ES256 key relabelled alg = -8\n";
$relabel = ['mig-es256' => pub($migA, [Key::ALG => -8]), 'mig-eddsa' => pub($migX, [Key::ALG => -8])];
foreach ($T as $label => [$bytes, $expect]) {
    row($label, decide(fn () => documentedSign($bytes, $mW->withKeyRestrictionsEnforced(), $relabel)), '-');
}
echo "-> the documented COSE_Sign path is 'every present signature verifies' (all-present-valid): T3 is accepted under W;\n";
echo "   under R the classical signature of T1 has no algorithm. No library object is told which algorithms must be present.\n";

echo "\n== 3. L4m with own code (B4 record only): required-set check after the signer loop (" . b4Count('L4m') . " lines)\n";
foreach ($T as $label => [$bytes, $expect]) {
    row($label, decide(fn () => ownRequiredSet($bytes, $mW, $keys, [EdDSA::identifier()])), '-');
}

echo "\n== 4. L4c (supplement): COSE_Sign1, migrated issuer (R = {EdDSA}, keys mig-es256 + mig-eddsa), legacy issuer (R = {}, key leg-es256)\n";
$l4c = [
    'migrated ES256' => [$s1MigA, 'reject'],
    'migrated EdDSA' => [$s1MigX, 'accept'],
    'legacy ES256' => [$s1LegA, 'accept'],
];
$single = [
    'one configuration: Manager W, all keys' => [$mW, $keys],
    'one configuration: Manager R = {EdDSA}, all keys' => [$mR, $keys],
    'one configuration: Manager W enforced, keys carry their own alg (3)' => [$mW->withKeyRestrictionsEnforced(),
        ['mig-es256' => pub($migA, [Key::ALG => -7]), 'mig-eddsa' => pub($migX, [Key::ALG => -8]), 'leg-es256' => pub($legA, [Key::ALG => -7])]],
];
foreach ($single as $name => [$m, $k]) {
    echo "{$name}\n";
    foreach ($l4c as $label => [$bytes, $expect]) {
        row($label, decide(fn () => documentedSign1($bytes, $m, $k)), $expect);
    }
}
echo "recorded, not counted (README rule 'Key material'):\n";
$noCount = [
    'Manager W enforced, migrated ES256 key relabelled alg = -8' => ['mig-es256' => pub($migA, [Key::ALG => -8]), 'mig-eddsa' => pub($migX), 'leg-es256' => pub($legA)],
    'Manager W enforced, migrated ES256 key key_ops = [sign] (no verify)' => ['mig-es256' => pub($migA, [Key::KEY_OPS => [Key::OP_SIGN]]), 'mig-eddsa' => pub($migX), 'leg-es256' => pub($legA)],
    'Manager W, migrated ES256 key left out' => ['mig-eddsa' => pub($migX), 'leg-es256' => pub($legA)],
];
foreach ($noCount as $name => $k) {
    echo "{$name}\n";
    foreach ($l4c as $label => [$bytes, $expect]) {
        row($label, decide(fn () => documentedSign1($bytes, $mW->withKeyRestrictionsEnforced(), $k)), '-');
    }
}
echo "\n== 5. L4c with own code (B4 record only; 'L4c (consecutive)': one Manager per issuer, selected by the caller) (" . b4Count('L4c') . " lines)\n";
$records = [
    ISS_MIG => ['manager' => $mR, 'keys' => ['mig-es256' => pub($migA), 'mig-eddsa' => pub($migX)]],
    ISS_LEG => ['manager' => $mW, 'keys' => ['leg-es256' => pub($legA)]],
];
foreach ($l4c as $label => [$bytes, $expect]) {
    row($label, decide(fn () => ownPerIssuer($bytes, $records)), '-');
}
echo "(the record selection and the verification are assembled by the caller; the migrated record holds its ES256 key)\n";

printf("\n== SUMMARY: checked rows OK = %d of %d; B4 lines: L4m %d, L4c %d\n", $GLOBALS['ok'], $GLOBALS['n'], b4Count('L4m'), b4Count('L4c'));
