<?php
// Ortak adaptör iskeleti (PHP) — C3 adaptör sözleşmesi 1.0 / RUNNER.md §1–§3.
// Bu dosya JOSE-070, JOSE-071 ve COSE-035'te AYNIDIR. Kütüphaneye özgü doğrulama adaptor.php'dedir.
// Doğrulama döngüsü YOK: imza doğrulamasını yalnız hedef kütüphanenin belgeli API'si yapar. Ağ erişimi yok.
declare(strict_types=1);

final class Ortak
{
    public const SOZLESME = 'adaptor-sozlesme/1.0';
    public const A = 'ES256';
    public const X_KOL = [
        'kontrol-EdDSA' => 'EdDSA', 'kontrol-Ed25519' => 'Ed25519', 'kontrol-ES384' => 'ES384',
        'tedavi-ML-DSA-65' => 'ML-DSA-65', 'tedavi-composite' => 'ML-DSA-65-ES256',
    ];
    private static ?array $manifest = null;
    private static array $jwks = [];

    public static function b64d(string $s): string
    {
        return (string) base64_decode(strtr($s, '-_', '+/') . str_repeat('=', (4 - strlen($s) % 4) % 4), false);
    }

    // KOSUCU §2: /v = v1.3; iş satırındaki dosya "v1.3/..." önekli olabilir.
    public static function vektorYolu(string $dosya): string
    {
        foreach (['/v/' . $dosya, '/v/' . preg_replace('#^v1\.3/#', '', $dosya)] as $y) {
            if (is_file($y)) return $y;
        }
        return '/v/' . $dosya;
    }

    // Manifestten YALNIZ dogrulama_girdileri okunur; `insa` ve diğer alanlar okunmaz (yürütücü 01.10).
    public static function girdi(string $id): array
    {
        if (self::$manifest === null) {
            $y = is_file('/v/MANIFEST.json') ? '/v/MANIFEST.json' : '/v/v1.3/MANIFEST.json';
            $m = json_decode((string) file_get_contents($y), true, 512, JSON_THROW_ON_ERROR);
            self::$manifest = [];
            foreach ($m['vektorler'] as $e) self::$manifest[$e['id']] = $e['dogrulama_girdileri'] ?? [];
        }
        if (!array_key_exists($id, self::$manifest)) throw new RuntimeException("manifestte yok: $id");
        return self::$manifest[$id];
    }

    public static function anahtarDosyasi(string $goreli): string
    {
        return '/anahtarlar/' . preg_replace('#^anahtarlar/#', '', $goreli);
    }

    public static function jwks(string $goreli): array
    {
        return self::$jwks[$goreli] ??= json_decode((string) file_get_contents(self::anahtarDosyasi($goreli)), true, 512, JSON_THROW_ON_ERROR);
    }

    /** Politika → ['w' => W|null, 'r' => R, 'taban' => ...]. YONTEM.md §2; VARSAYILAN = sözleşme §5.2 L5. */
    public static function politika(array $is, array $kutuphaneAlgleri): array
    {
        $taban = explode('@', explode('|', $is['politika'])[0])[0]; // '|sdjwtvc=..' ve '@-19' ekleri yalnız oracle'ı böler
        $x = self::X_KOL[$is['kol']] ?? null;
        $gerekX = static function () use ($x, $is) { if ($x === null) throw new RuntimeException("kol {$is['kol']} icin X tanimsiz"); };
        switch ($taban) {
            case 'GEC': case 'P0': case 'P1': case 'P2': return ['w' => $kutuphaneAlgleri, 'r' => [], 'taban' => $taban];
            case 'VARSAYILAN': return ['w' => null, 'r' => [], 'taban' => $taban];
            case 'IZIN-A': return ['w' => [self::A], 'r' => [], 'taban' => $taban];
            case 'IZIN-AX': $gerekX(); return ['w' => [self::A, $x], 'r' => [], 'taban' => $taban];
            case 'L4': case 'L4-S': case 'L4-Y': case 'L4-YOL': $gerekX(); return ['w' => [self::A, $x], 'r' => [$x], 'taban' => $taban];
        }
        throw new RuntimeException("bilinmeyen politika {$is['politika']}");
    }

    /** Tek imzalı nesnede R ≠ ∅ ise etkin izin listesi R'dir (tek imza R'yi ancak kendisi X ise karşılar; R ⊆ W). */
    public static function tekImzaIzin(array $pol): ?array
    {
        if ($pol['w'] === null) return null;
        return $pol['r'] ? $pol['r'] : $pol['w'];
    }

    /** Anahtar seçimi (sözleşme §8 m.1): başlık kid → vektörün JWKS'i; yoksa alg_kid[alg]; yoksa tek kid. DPoP: başlık jwk. */
    public static function jwkSec(array $baslik, array $dg): array
    {
        if (($dg['anahtar'] ?? null) === 'jwk basligindan') return [$baslik['jwk'] ?? null, 'jwk-basligi'];
        if (empty($dg['jwks'])) return [null, 'JWK'];
        $kid = $baslik['kid'] ?? null;
        if ($kid === null) {
            $ak = $dg['alg_kid'] ?? null;
            if (is_string($ak)) $ak = json_decode($ak, true);
            if (is_array($ak) && isset($baslik['alg']) && is_string($baslik['alg'])) $kid = $ak[$baslik['alg']] ?? null;
            if ($kid === null && is_array($dg['kid'] ?? null) && count($dg['kid']) === 1) $kid = $dg['kid'][0];
        }
        foreach (self::jwks($dg['jwks'])['keys'] as $k) if (($k['kid'] ?? null) === $kid) return [$k, 'JWK'];
        return [null, 'JWK'];
    }

    /** JWK'nın anahtar türünden "doğal" JOSE algoritması (anahtar–alg bağlaması gerektiren kütüphaneler için). */
    public static function dogalAlg(array $jwk, string $kol): ?string
    {
        $kty = $jwk['kty'] ?? ''; $crv = $jwk['crv'] ?? '';
        if ($kty === 'EC') return ['P-256' => 'ES256', 'P-384' => 'ES384', 'P-521' => 'ES512'][$crv] ?? null;
        if ($kty === 'OKP' && $crv === 'Ed25519') return $kol === 'kontrol-Ed25519' ? 'Ed25519' : 'EdDSA';
        if ($kty === 'OKP' && $crv === 'Ed448') return 'Ed448';
        if ($kty === 'AKP') return $jwk['alg'] ?? null;
        return null;
    }

    public static function kosuAdi(string $cikti): string
    {
        $e = getenv('KOSU');
        if ($e !== false && $e !== '') return $e;
        $p = explode('.', basename($cikti, '.jsonl'));
        return count($p) >= 2 ? end($p) : 'oncesi';
    }

    private static function sabit(string $ad): string
    {
        $y = "/opt/a/$ad";
        return is_file($y) ? trim((string) file_get_contents($y)) : '';
    }

    public static function b6(string $api): array
    {
        return ['sonuc_ham' => 'uygulanamaz', 'hata_sinifi' => 'bicim-desteklenmiyor', 'hata_ozeti' => 'B6: MAPPING.md (API incelemesi)', 'api_yolu' => $api];
    }

    public static function ifadeEdilemedi(string $neden, string $api): array
    {
        return ['sonuc_ham' => 'ifade-edilemedi', 'hata_sinifi' => null, 'hata_ozeti' => $neden, 'api_yolu' => $api];
    }

    /** Ana döngü: iş satırları tek süreçte sırayla. $dogrula(array $is): array */
    public static function kos(array $argv, callable $dogrula): void
    {
        if (count($argv) < 3) { fwrite(STDERR, "kullanim: adaptor <jobs-v1.3.jsonl> <cikti.jsonl>\n"); exit(2); }
        [, $girdi, $cikti] = $argv;
        $kosu = self::kosuAdi($cikti);
        $out = fopen($cikti, 'w');
        foreach (file($girdi, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) as $l) {
            $is = json_decode($l, true, 512, JSON_THROW_ON_ERROR);
            $t0 = hrtime(true);
            try {
                $s = $dogrula($is);
            } catch (\Throwable $e) {
                $s = ['sonuc_ham' => 'istisna', 'hata_sinifi' => 'adaptor-hatasi', 'hata_ozeti' => get_class($e) . ': ' . $e->getMessage(), 'api_yolu' => null];
            }
            $ms = (int) round((hrtime(true) - $t0) / 1e6);
            $satir = [
                'sozlesme' => self::SOZLESME,
                'hedef_id' => getenv('HEDEF_ID') ?: 'bilinmiyor',
                'hedef_surum' => self::sabit('HEDEF_SURUM'),
                'adaptor_sha256' => self::sabit('ADAPTOR_SHA256'),
                'kosu' => $kosu,
                'vektor_id' => $is['vektor_id'],
                'politika' => $is['politika'],
                'kol' => $is['kol'],
                'sonuc_ham' => $s['sonuc_ham'],
                'hata_sinifi' => $s['hata_sinifi'] ?? null,
                'hata_ozeti' => isset($s['hata_ozeti']) ? mb_substr((string) $s['hata_ozeti'], 0, 200) : null,
                'dogrulanan_algoritmalar' => $s['dogrulanan'] ?? [],
                'api_yolu' => $s['api_yolu'] ?? null,
                'anahtar_yolu' => $s['anahtar_yolu'] ?? null,
                'sure_ms' => $ms,
            ];
            fwrite($out, json_encode($satir, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . "\n");
            fflush($out);
        }
        fclose($out);
    }
}
