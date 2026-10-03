// Adapter for SDJWT-002 selective_disclosure_jwt 1.1.1 (affinidi-sdjwt-dart) — C3 contract 1.0 (experiment/oracle/oracle-A/adapter-contract.md) / RUNNER §1–§3.
// Documented public API (README "Usage"): SdJwtHandlerV1().decodeAndVerify(sdJwtToken:, verifier: SDKeyVerifier(
// SdPublicKey(jwk_map, SdJwtSignAlgorithm)), verifyKeyBinding:) → SdJwt.isVerified.
// Policy: SDKeyVerifier.isAllowedAlgorithm = "every alg supported by the library" (fixed); the documented mechanism is the
// algorithm to which the key is bound in SdPublicKey (verification is done with this alg). Mapping and reasons: MAPPING.md.
// NO verification loop; only dogrulama_girdileri is read from the manifest; no network.
import 'dart:convert';
import 'dart:io';
import 'package:selective_disclosure_jwt/selective_disclosure_jwt.dart';

const xKol = {'kontrol-EdDSA': 'EdDSA', 'kontrol-Ed25519': 'Ed25519', 'kontrol-ES384': 'ES384', 'tedavi-ML-DSA-65': 'ML-DSA-65', 'tedavi-composite': 'ML-DSA-65-ES256'};
// Native support among the battery's algorithms (SdJwtSignAlgorithm: ES256/384/512, ES256K, RS*, HS*, EdDSA; no ML-DSA)
const kutuphane = ['ES256', 'ES384', 'EdDSA'];
const api = 'SdJwtHandlerV1().decodeAndVerify(sdJwtToken: sd_jwt, verifier: SDKeyVerifier(SdPublicKey(jwk, alg_ignesi)), verifyKeyBinding: kb) -> isVerified';
final algAd = {'ES256': SdJwtSignAlgorithm.es256, 'ES384': SdJwtSignAlgorithm.es384, 'EdDSA': SdJwtSignAlgorithm.eddsa};

Map<String, dynamic>? _manifest;
Map<String, dynamic> girdi(String id) {
  if (_manifest == null) {
    final y = File('/v/MANIFEST.json').existsSync() ? '/v/MANIFEST.json' : '/v/v1.3/MANIFEST.json';
    final m = jsonDecode(File(y).readAsStringSync()) as Map<String, dynamic>;
    _manifest = {for (final e in m['vektorler'] as List) e['id'] as String: (e['dogrulama_girdileri'] ?? {}) as Map<String, dynamic>};
    // Pre-freeze SD-JWT validity vectors (not in the battery) carry their own manifest in the same schema.
    final vpm = File('/v/vpm-sdjwt/MANIFEST.json');
    if (vpm.existsSync()) {
      for (final e in (jsonDecode(vpm.readAsStringSync()) as Map<String, dynamic>)['vektorler'] as List) {
        _manifest![e['id'] as String] = (e['dogrulama_girdileri'] ?? {}) as Map<String, dynamic>;
      }
    }
  }
  return _manifest![id] ?? (throw StateError('manifestte yok: $id'));
}

String vektorYolu(String d) {
  for (final y in ['/v/$d', '/v/${d.replaceFirst(RegExp(r'^v1\.3/'), '')}']) {
    if (File(y).existsSync()) return y;
  }
  return '/v/$d';
}

Map<String, dynamic> b64json(String s) => jsonDecode(utf8.decode(base64Url.decode(base64Url.normalize(s)))) as Map<String, dynamic>;

// Policy → (taban, W|null, R). METHOD.md §2; VARSAYILAN = contract §5.2 L5.
// L4 family: two issuer records (pre-registration §5.13, contract §5.3), selected by the iss of the object: legacy issuer
// W = {A, X}, R = ∅; every other issuer (migrated) W = {A, X}, R = {X}. The selected record is enforced through the key–alg
// binding of the library ("L4c (consecutive)", decision D9).
const eskiIss = 'https://legacy-issuer.example';
(String, List<String>?, List<String>) politika(Map is_, [String? iss]) {
  final taban = (is_['politika'] as String).split('|').first.split('@').first; // the suffixes only split the oracle
  final x = xKol[is_['kol']];
  String gx() => x ?? (throw StateError('kol icin X tanimsiz'));
  switch (taban) {
    case 'GEC' || 'P0' || 'P1' || 'P2' || 'VARSAYILAN': return (taban, null, []);
    case 'IZIN-A': return (taban, ['ES256'], []);
    case 'IZIN-AX': return (taban, ['ES256', gx()], []);
    case 'L4' || 'L4-S' || 'L4-Y' || 'L4-YOL': return (taban, ['ES256', gx()], iss == eskiIss ? [] : [gx()]);
  }
  throw StateError('bilinmeyen politika ${is_['politika']}');
}

// Key selection (contract §8 item 1): header kid → the vector's JWKS; otherwise alg_kid[alg]; otherwise the single kid.
Map<String, dynamic>? jwkSec(Map<String, dynamic> baslik, Map<String, dynamic> dg) {
  if (dg['jwks'] == null) return null;
  var kid = baslik['kid'];
  if (kid == null) {
    var ak = dg['alg_kid'];
    if (ak is String) ak = jsonDecode(ak);
    if (ak is Map) kid = ak[baslik['alg']];
    if (kid == null && dg['kid'] is List && (dg['kid'] as List).length == 1) kid = dg['kid'][0];
  }
  final yol = '/anahtarlar/${(dg['jwks'] as String).replaceFirst(RegExp(r'^anahtarlar/'), '')}';
  for (final k in (jsonDecode(File(yol).readAsStringSync())['keys'] as List)) {
    if (k['kid'] == kid) return Map<String, dynamic>.from(k as Map);
  }
  return null;
}

String? dogalAlg(Map<String, dynamic> jwk) {
  if (jwk['kty'] == 'EC') return {'P-256': 'ES256', 'P-384': 'ES384'}[jwk['crv']];
  if (jwk['kty'] == 'OKP' && jwk['crv'] == 'Ed25519') return 'EdDSA';
  if (jwk['kty'] == 'AKP') return jwk['alg'] as String?;
  return null;
}

Map<String, dynamic> sonuc(String ham, String? sinif, String? ozet, {String? yol, List? dog}) =>
    {'sonuc_ham': ham, 'hata_sinifi': sinif, 'hata_ozeti': ozet, 'api_yolu': api, 'anahtar_yolu': yol, 'dogrulanan': dog ?? []};

Map<String, dynamic> dogrula(Map<String, dynamic> is_) {
  final seri = is_['serilestirme'] as String;
  final artefakt = (is_['artefakt'] ?? '') as String;
  final cekirdek = seri == 'compact' && artefakt == 'jws-cekirdek'; // maintainers 01.10: "<jws>~"
  if (!(seri == 'sd-jwt-compact' || cekirdek || seri == 'oid4vci-toplu-yanit')) {
    return sonuc('uygulanamaz', 'bicim-desteklenmiyor', 'B6: MAPPING.md (API incelemesi)');
  }
  final dg = girdi(is_['vektor_id'] as String);
  final ham = File(vektorYolu(is_['dosya'] as String)).readAsStringSync().trim();
  String sunum;
  if (cekirdek) {
    sunum = '$ham~';
  } else if (seri == 'oid4vci-toplu-yanit') {
    final c0 = (jsonDecode(ham)['credentials'] as List).first; // BATARYA-ESLEME K11: credentials[0]
    sunum = c0 is Map ? c0['credential'] as String : c0 as String;
  } else {
    sunum = ham;
  }
  final baslik = b64json(sunum.split('~').first.split('.').first);
  final alg = baslik['alg'] as String?;
  // iss of the issuer-signed JWT, read before verification only to select the issuer record of L4c.
  String? iss;
  try {
    iss = b64json(sunum.split('~').first.split('.')[1])['iss'] as String?;
  } catch (_) {}
  final (taban, w, r) = politika(is_, iss);
  if (taban == 'L4-YOL') return sonuc('ifade-edilemedi', null, 'x5c/x5chain yol sinifi politikasi (L4-YOL, B2) icin belgeli API yok');
  final izin = w == null ? null : (r.isNotEmpty ? r : w);
  final jwk = jwkSec(baslik, dg);
  if (jwk == null) return sonuc('red', 'anahtar-bulunamadi', 'JWK secilemedi (kid/alg_kid)', yol: 'JWK');
  // Key–alg binding: the natural alg if it is in W and supported; otherwise the first of W ∩ supported is pinned.
  final dogal = dogalAlg(jwk);
  String? igne;
  if (izin == null) {
    igne = dogal;
  } else {
    final aday = izin.where((a) => kutuphane.contains(a)).toList();
    igne = aday.contains(dogal) ? dogal : (aday.isEmpty ? null : aday.first);
  }
  if (igne == null || !algAd.containsKey(igne)) {
    return sonuc('red', 'alg-desteklenmiyor', 'alg ignesi kurulamaz (dogal=$dogal, W=${izin ?? 'varsayilan'}): SdPublicKey yapilamaz; kutuphane cagrilmadi', yol: 'JWK');
  }
  final SdPublicKey anahtar;
  try {
    anahtar = SdPublicKey(jwk, algAd[igne]!);
  } catch (e) {
    return sonuc('red', 'alg-desteklenmiyor', 'SdPublicKey: $e', yol: 'JWK');
  }
  final kb = artefakt == 'sd-jwt-vc+kb';
  try {
    final s = SdJwtHandlerV1().decodeAndVerify(sdJwtToken: sunum, verifier: SDKeyVerifier(anahtar), verifyKeyBinding: kb);
    if (s.isVerified == true) {
      // the library verifies the signature with the algorithm of the SdPublicKey (jwt_verifier_base.dart → SDKeyVerifier.verify)
      return sonuc('kabul', null, null, yol: 'JWK', dog: [{'sira': 0, 'alg': igne, 'sonuc': 'gecerli'}]);
    }
    // The library swallows the cause (sd_jwt_verifier.dart: catch → _isJwsVerified = false); the class is inferred from the header alg and W.
    String sinif;
    if (alg == null || !kutuphane.contains(alg)) {
      sinif = 'alg-desteklenmiyor';
    } else if (izin != null && !izin.contains(alg)) {
      sinif = 'alg-izin-disi';
    } else if (alg != igne) {
      sinif = 'alg-anahtar-uyusmazligi';
    } else {
      sinif = kb ? 'kb' : 'imza-gecersiz';
    }
    return sonuc('red', sinif, 'isVerified=${s.isVerified} (alg=$alg, igne=$igne, kb=$kb)', yol: 'JWK');
  } catch (e, st) {
    if (Platform.environment['ADAPTOR_HATA_TAM'] == '1') stderr.writeln('ERROR ${is_['vektor_id']} $e $st');
    final m = e.toString();
    // Errors of SdJwt.parse (sdjwt.dart L107-170): "Invalid SD-JWT ..." (Exception), or the TypeError of
    // Hasher.fromString(null) when `_sd_alg` is missing (L143-144; in RFC 9901 _sd_alg is optional) → parsing.
    final ayr = m.contains('Invalid SD-JWT') || m.contains('FormatException') || (e is TypeError && st.toString().contains('SdJwt.parse'));
    return sonuc(e is Exception ? 'red' : 'istisna', ayr ? 'ayristirma' : 'istisna-diger', m, yol: 'JWK');
  }
}

String sabit(String ad) {
  final f = File('/opt/a/$ad');
  return f.existsSync() ? f.readAsStringSync().trim() : '';
}

void main(List<String> a) {
  if (a.length < 2) {
    stderr.writeln('usage: adaptor <jobs-v1.3.jsonl> <output.jsonl>');
    exit(2);
  }
  final ad = a[1].split('/').last.replaceAll(RegExp(r'\.jsonl$'), '').split('.');
  final kosu = (Platform.environment['KOSU'] ?? '').isNotEmpty ? Platform.environment['KOSU']! : (ad.length >= 2 ? ad.last : 'oncesi');
  final out = File(a[1]).openSync(mode: FileMode.write);
  for (final l in File(a[0]).readAsLinesSync()) {
    if (l.trim().isEmpty) continue;
    final is_ = jsonDecode(l) as Map<String, dynamic>;
    final sw = Stopwatch()..start();
    Map<String, dynamic> s;
    try {
      s = dogrula(is_);
    } catch (e) {
      s = {'sonuc_ham': 'istisna', 'hata_sinifi': 'adaptor-hatasi', 'hata_ozeti': '$e', 'api_yolu': null};
    }
    final oz = s['hata_ozeti'] as String?;
    out.writeStringSync('${jsonEncode({
      'sozlesme': 'adaptor-sozlesme/1.0', 'hedef_id': Platform.environment['HEDEF_ID'] ?? 'bilinmiyor',
      'hedef_surum': sabit('HEDEF_SURUM'), 'adaptor_sha256': sabit('ADAPTOR_SHA256'), 'kosu': kosu,
      'vektor_id': is_['vektor_id'], 'politika': is_['politika'], 'kol': is_['kol'], 'sonuc_ham': s['sonuc_ham'],
      'hata_sinifi': s['hata_sinifi'], 'hata_ozeti': oz == null ? null : (oz.length > 200 ? oz.substring(0, 200) : oz),
      'dogrulanan_algoritmalar': s['dogrulanan'] ?? [], 'api_yolu': s['api_yolu'], 'anahtar_yolu': s['anahtar_yolu'],
      'sure_ms': sw.elapsedMilliseconds,
    })}\n');
  }
  out.closeSync();
}
