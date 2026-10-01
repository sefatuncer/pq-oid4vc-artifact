// SDJWT-002 selective_disclosure_jwt 1.1.1 (affinidi-sdjwt-dart) adaptörü — C3 sözleşmesi 1.0 / KOSUCU §1–§3.
// Belgeli genel API (README "Usage"): SdJwtHandlerV1().decodeAndVerify(sdJwtToken:, verifier: SDKeyVerifier(
// SdPublicKey(jwk_map, SdJwtSignAlgorithm)), verifyKeyBinding:) → SdJwt.isVerified.
// Politika: SDKeyVerifier.isAllowedAlgorithm = "kütüphanede destekli her alg" (sabit); belgeli mekanizma anahtarın
// SdPublicKey'e bağlandığı algoritmadır (doğrulama bu alg ile yapılır). Eşleme ve gerekçeler: ESLEME.md.
// Doğrulama döngüsü YOK; manifestten yalnız dogrulama_girdileri okunur; ağ yok.
import 'dart:convert';
import 'dart:io';
import 'package:selective_disclosure_jwt/selective_disclosure_jwt.dart';

const xKol = {'kontrol-EdDSA': 'EdDSA', 'kontrol-Ed25519': 'Ed25519', 'tedavi-ML-DSA-65': 'ML-DSA-65', 'tedavi-composite': 'ML-DSA-65-ES256'};
// Bataryadaki algoritmalardan yerel destek (SdJwtSignAlgorithm: ES256/384/512, ES256K, RS*, HS*, EdDSA; ML-DSA yok)
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

// Politika → (taban, W|null, R). YONTEM.md §2; VARSAYILAN = sözleşme §5.2 L5.
(String, List<String>?, List<String>) politika(Map is_) {
  final taban = (is_['politika'] as String).split('|').first.split('@').first; // ekler yalnız oracle'ı böler
  final x = xKol[is_['kol']];
  String gx() => x ?? (throw StateError('kol icin X tanimsiz'));
  switch (taban) {
    case 'GEC' || 'P0' || 'P1' || 'P2' || 'VARSAYILAN': return (taban, null, []);
    case 'IZIN-A': return (taban, ['ES256'], []);
    case 'IZIN-AX': return (taban, ['ES256', gx()], []);
    case 'L4' || 'L4-S' || 'L4-Y' || 'L4-YOL': return (taban, ['ES256', gx()], [gx()]);
  }
  throw StateError('bilinmeyen politika ${is_['politika']}');
}

// Anahtar seçimi (sözleşme §8 m.1): başlık kid → vektörün JWKS'i; yoksa alg_kid[alg]; yoksa tek kid.
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
  final cekirdek = seri == 'compact' && artefakt == 'jws-cekirdek'; // yürütücü 01.10: "<jws>~"
  if (!(seri == 'sd-jwt-compact' || cekirdek || seri == 'oid4vci-toplu-yanit')) {
    return sonuc('uygulanamaz', 'bicim-desteklenmiyor', 'B6: ESLEME.md (API incelemesi)');
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
  final (taban, w, r) = politika(is_);
  if (taban == 'L4-YOL') return sonuc('ifade-edilemedi', null, 'x5c/x5chain yol sinifi politikasi (L4-YOL, B2) icin belgeli API yok');
  final izin = w == null ? null : (r.isNotEmpty ? r : w);
  final jwk = jwkSec(baslik, dg);
  if (jwk == null) return sonuc('red', 'anahtar-bulunamadi', 'JWK secilemedi (kid/alg_kid)', yol: 'JWK');
  // Anahtar–alg bağlaması: doğal alg W'de ve destekliyse o; değilse W ∩ destekli kümenin ilki iğnelenir.
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
      // kütüphane imzayı SdPublicKey'in algoritmasıyla doğrular (jwt_verifier_base.dart → SDKeyVerifier.verify)
      return sonuc('kabul', null, null, yol: 'JWK', dog: [{'sira': 0, 'alg': igne, 'sonuc': 'gecerli'}]);
    }
    // Kütüphane nedeni yutar (sd_jwt_verifier.dart: catch → _isJwsVerified = false); sınıf başlık alg'ı ve W ile çıkarılır.
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
    if (Platform.environment['ADAPTOR_HATA_TAM'] == '1') stderr.writeln('HATA ${is_['vektor_id']} $e $st');
    final m = e.toString();
    // SdJwt.parse (sdjwt.dart L107-170) hataları: "Invalid SD-JWT ..." (Exception) ya da `_sd_alg` yokken
    // Hasher.fromString(null) TypeError'ı (L143-144; RFC 9901'de _sd_alg isteğe bağlıdır) → ayrıştırma.
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
    stderr.writeln('kullanim: adaptor <isler.jsonl> <cikti.jsonl>');
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
