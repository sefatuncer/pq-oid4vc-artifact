# frozen_string_literal: true
# Adapter for JOSE-087 ruby-jwt 3.3.0. Documented public API: JWT.decode(token, key, verify, options) { keyfinder } (README
# "Algorithms and Usage", "JSON Web Key (JWK)"), JWT::JWK.import. Mapping and reasons: MAPPING.md.
require_relative 'ortak'
require 'jwt'

# The subset of the battery's algorithms that the library supports natively (evidence/api-tarama.txt: jwa/ecdsa.rb NAMED_CURVES;
# EdDSA is in the separate jwt-eddsa gem since 3.0; no ML-DSA/composite).
KUTUPHANE_ALGLERI = %w[ES256 ES384].freeze
DESTEKLI_BICIM = %w[compact].freeze
API = 'JWT.decode(token, nil, true, algorithms: W) { |hdr| JWT::JWK.import(jwk).verify_key }'

def baslik_alg(token)
  JSON.parse(Ortak.b64d(token.split('.').first))['alg']
rescue StandardError
  nil
end

def sinifla(e, alg)
  m = e.message.to_s
  case e
  when JWT::UnsupportedKeyType then 'alg-desteklenmiyor'
  when JWT::UnsupportedEcdsaCurve then 'alg-anahtar-uyusmazligi'
  when JWT::IncorrectAlgorithm
    if m.include?('verification key was provided') then 'alg-anahtar-uyusmazligi'
    elsif !KUTUPHANE_ALGLERI.include?(alg) then 'alg-desteklenmiyor'
    else 'alg-izin-disi'
    end
  when JWT::VerificationKeyError
    if m.include?('not supported') then 'alg-desteklenmiyor'
    elsif m.include?('do not support one of the specified') then 'alg-anahtar-uyusmazligi'
    else 'imza-gecersiz'
    end
  when JWT::VerificationError then 'imza-gecersiz'
  when JWT::ExpiredSignature, JWT::ImmatureSignature, JWT::InvalidIatError then 'zaman'
  when JWT::InvalidCritError then 'crit'
  when JWT::MalformedTokenError then 'ayristirma'
  when JWT::SignatureError then m.match?(/key/i) ? 'anahtar-bulunamadi' : 'imza-gecersiz'
  else 'istisna-diger'
  end
end

def dogrula(is)
  return Ortak.b6(API) unless DESTEKLI_BICIM.include?(is['serilestirme'])

  giris = Ortak.manifest[is['vektor_id']] or raise "manifestte yok: #{is['vektor_id']}"
  token = File.read(Ortak.vektor_yolu(is['dosya'])).strip
  pol = Ortak.politika(is, KUTUPHANE_ALGLERI)
  return Ortak.ifade_edilemedi('x5c/x5chain yol sinifi politikasi (L4-YOL, B2) icin belgeli API yok', API) if pol[:taban] == 'L4-YOL'
  alg = baslik_alg(token)
  anahtar_yolu = 'JWK'
  opts = {}
  opts[:algorithms] = Ortak.tek_imza_izin_listesi(pol) unless pol[:w].nil? # VARSAYILAN: no algorithm is given
  api = pol[:w].nil? ? 'JWT.decode(token, nil, true) { |hdr| JWT::JWK.import(jwk).verify_key }' : API
  begin
    _yuk, hdr = JWT.decode(token, nil, true, opts) do |baslik|
      jwk, anahtar_yolu = Ortak.jwk_sec(baslik, giris)
      # verify_key instead of the JWK object (README section "JWK"): in 3.3.0 JWT.decode compares the JWK object with JWA
      # objects and also rejects a valid ES256 signature (evidence/duman-testi.txt, first attempt).
      jwk && JWT::JWK.import(jwk).verify_key
    end
    { sonuc_ham: 'kabul', hata_sinifi: nil, hata_ozeti: nil, api_yolu: api, anahtar_yolu: anahtar_yolu,
      dogrulanan: [{ 'sira' => 0, 'alg' => hdr['alg'], 'sonuc' => 'gecerli' }] }
  rescue JWT::Error => e
    { sonuc_ham: 'red', hata_sinifi: sinifla(e, alg), hata_ozeti: "#{e.class}: #{e.message}", api_yolu: api,
      anahtar_yolu: anahtar_yolu }
  rescue StandardError => e
    { sonuc_ham: 'istisna', hata_sinifi: 'istisna-diger', hata_ozeti: "#{e.class}: #{e.message}", api_yolu: api,
      anahtar_yolu: anahtar_yolu }
  end
end

Ortak.kos(ARGV) { |is| dogrula(is) }
