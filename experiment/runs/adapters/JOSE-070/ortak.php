<?php
// Shared adapter skeleton (PHP) — C3 adapter contract 1.0 (experiment/oracle/oracle-A/adapter-contract.md) / RUNNER.md §1–§3.
// This file is IDENTICAL in JOSE-070, JOSE-071 and COSE-035. The library-specific verification is in adaptor.php.
// NO verification loop: signature verification is done only by the documented API of the target library. No network access.
declare(strict_types=1);

final class Ortak
{
    public const SOZLESME = 'adaptor-sozlesme/1.0';
    public const A = 'ES256';
    public const ESKI_ISS = 'https://legacy-issuer.example';   // legacy issuer of L4c (battery v1.3)
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

    /** iss of a compact JWS payload (read before verification only to select the issuer record of L4c). */
    public static function iss(string $kompakt): ?string
    {
        $p = json_decode(self::b64d(explode('.', $kompakt)[1] ?? ''), true);
        return is_array($p) && is_string($p['iss'] ?? null) ? $p['iss'] : null;
    }

    // RUNNER §2: /v = v1.3; the file in the job row may carry the prefix "v1.3/...".
    public static function vektorYolu(string $dosya): string
    {
        foreach (['/v/' . $dosya, '/v/' . preg_replace('#^v1\.3/#', '', $dosya)] as $y) {
            if (is_file($y)) return $y;
        }
        return '/v/' . $dosya;
    }

    // ONLY dogrulama_girdileri is read from the manifest; `insa` and the other fields are not read (maintainers 01.10).
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

    /**
     * Policy → ['w' => W|null, 'r' => R, 'taban' => ...]. METHOD.md §2; VARSAYILAN = contract §5.2 L5.
     * L4 family: two issuer records (pre-registration §5.13, contract §5.3), selected by the iss of the object: legacy
     * issuer W = {A, X}, R = ∅; every other issuer (migrated) W = {A, X}, R = {X}. The selected record is enforced by
     * the library's allow-list ("L4c (consecutive)", decision D9).
     */
    public static function politika(array $is, array $kutuphaneAlgleri, ?string $iss = null): array
    {
        $taban = explode('@', explode('|', $is['politika'])[0])[0]; // the suffixes '|sdjwtvc=..' and '@-19' only split the oracle
        $x = self::X_KOL[$is['kol']] ?? null;
        $gerekX = static function () use ($x, $is) { if ($x === null) throw new RuntimeException("kol {$is['kol']} icin X tanimsiz"); };
        switch ($taban) {
            case 'GEC': case 'P0': case 'P1': case 'P2': return ['w' => $kutuphaneAlgleri, 'r' => [], 'taban' => $taban];
            case 'VARSAYILAN': return ['w' => null, 'r' => [], 'taban' => $taban];
            case 'IZIN-A': return ['w' => [self::A], 'r' => [], 'taban' => $taban];
            case 'IZIN-AX': $gerekX(); return ['w' => [self::A, $x], 'r' => [], 'taban' => $taban];
            case 'L4': case 'L4-S': case 'L4-Y': case 'L4-YOL': $gerekX();
                return ['w' => [self::A, $x], 'r' => $iss === self::ESKI_ISS ? [] : [$x], 'taban' => $taban];
        }
        throw new RuntimeException("bilinmeyen politika {$is['politika']}");
    }

    /** For a single-signature object with R ≠ ∅ the effective allow-list is R (a single signature satisfies R only if it is X itself; R ⊆ W). */
    public static function tekImzaIzin(array $pol): ?array
    {
        if ($pol['w'] === null) return null;
        return $pol['r'] ? $pol['r'] : $pol['w'];
    }

    /** Key selection (contract §8 item 1): header kid → the vector's JWKS; otherwise alg_kid[alg]; otherwise the single kid. DPoP: header jwk. */
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

    /** The "natural" JOSE algorithm of the JWK's key type (for libraries that need a key–alg binding). */
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

    /** Main loop: job rows in sequence in one process. $dogrula(array $is): array */
    public static function kos(array $argv, callable $dogrula): void
    {
        if (count($argv) < 3) { fwrite(STDERR, "usage: adaptor <jobs-v1.3.jsonl> <output.jsonl>\n"); exit(2); }
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
