# frozen_string_literal: true
# JOSE-087 ruby-jwt 3.3.0 adaptörü. Belgeli genel API: JWT.decode(token, key, verify, options) { keyfinder } (README
# "Algorithms and Usage", "JSON Web Key (JWK)"), JWT::JWK.import. Eşleme ve gerekçeler: MAPPING.md.
require_relative 'ortak'
require 'jwt'

# Bataryadaki algoritmalardan kütüphanenin yerel desteklediği alt küme (evidence/api-tarama.txt: jwa/ecdsa.rb NAMED_CURVES;
# EdDSA 3.0'dan beri ayrı jwt-eddsa gem'inde; ML-DSA/composite yok).
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
  opts[:algorithms] = Ortak.tek_imza_izin_listesi(pol) unless pol[:w].nil? # VARSAYILAN: algoritma verilmez
  api = pol[:w].nil? ? 'JWT.decode(token, nil, true) { |hdr| JWT::JWK.import(jwk).verify_key }' : API
  begin
    _yuk, hdr = JWT.decode(token, nil, true, opts) do |baslik|
      jwk, anahtar_yolu = Ortak.jwk_sec(baslik, giris)
      # JWK nesnesi yerine verify_key (README "JWK" bölümü): 3.3.0'da JWT.decode, JWK nesnesini JWA nesneleriyle
      # karşılaştırıp geçerli ES256 imzasını da reddediyor (evidence/duman-testi.txt, ilk deneme).
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
