# frozen_string_literal: true
# JOSE-089 json-jwt 1.17.2 adaptörü. Belgeli genel API: JSON::JWT.decode(input, key, algorithms) — String girdi
# kompakt, Hash girdi JSON serileştirme (lib/json/jose.rb:59-64; lib/json/jws.rb decode_json_serialized).
# Anahtar: JSON::JWK.new(jwk_hash) (lib/json/jwk.rb). Eşleme ve gerekçeler: ESLEME.md.
require_relative 'ortak'
require 'json/jwt'

KUTUPHANE_ALGLERI = %w[ES256 ES384].freeze # jws.rb ecdsa?: ES256/ES384/ES512/ES256K; EdDSA, ML-DSA, composite yok
DESTEKLI_BICIM = %w[compact general].freeze  # general: decode_json_serialized (yalnız signatures.first doğrulanır)
API_KOMPAKT = 'JSON::JWT.decode(token_str, JSON::JWK.new(jwk), W.map(&:to_sym))'
API_GENEL = 'JSON::JWT.decode(JSON.parse(general_json), JSON::JWK.new(jwk), W.map(&:to_sym))'

def sinifla(e, alg, anahtar_var)
  m = e.message.to_s
  case e
  when JSON::JWT::UnexpectedAlgorithm
    if m.include?('Unexpected alg header')
      KUTUPHANE_ALGLERI.include?(alg) ? 'alg-izin-disi' : 'alg-desteklenmiyor'
    elsif m.include?('Unknown Signature Algorithm') then 'alg-desteklenmiyor'
    else 'alg-anahtar-uyusmazligi' # valid? içindeki TypeError (anahtar türü ≠ alg)
    end
  when JSON::JWK::Set::KidNotFound then 'anahtar-bulunamadi'
  when JSON::JWK::UnknownAlgorithm then 'alg-desteklenmiyor' # 'Unknown Key Type' (OKP/AKP)
  when JSON::JWT::VerificationFailed then anahtar_var ? 'imza-gecersiz' : 'anahtar-bulunamadi'
  when JSON::JWT::InvalidFormat then 'ayristirma'
  else 'istisna-diger'
  end
end

def dogrula(is)
  seri = is['serilestirme']
  return Ortak.b6(seri == 'general' ? API_GENEL : API_KOMPAKT) unless DESTEKLI_BICIM.include?(seri)

  giris = Ortak.manifest[is['vektor_id']] or raise "manifestte yok: #{is['vektor_id']}"
  ham = File.read(Ortak.vektor_yolu(is['dosya'])).strip
  pol = Ortak.politika(is, KUTUPHANE_ALGLERI)
  return Ortak.ifade_edilemedi('x5c/x5chain yol sinifi politikasi (L4-YOL, B2) icin belgeli API yok', API_KOMPAKT) if pol[:taban] == 'L4-YOL'
  if seri == 'general'
    girdi = JSON.parse(ham)
    imzalar = girdi['signatures'] || []
    ilk_baslik = JSON.parse(Ortak.b64d(imzalar.first['protected']))
    api = API_GENEL
    if imzalar.size > 1 && pol[:taban] != 'VARSAYILAN'
      # Çoklu imza kuralı (P0 en-az-biri / P1 tümü / L4 gerekli küme) için belgeli seçenek yok: kütüphane yalnız
      # signatures.first'ü doğrular (jws.rb decode_json_serialized). Özel döngü yazılmaz (B4, NOTLAR.md).
      return Ortak.ifade_edilemedi('coklu imza kurali (P0/P1/R) icin API secenegi yok; yalniz signatures.first dogrulanir', api)
    end
  else
    girdi = ham
    ilk_baslik = JSON.parse(Ortak.b64d(ham.split('.').first)) rescue {}
    api = API_KOMPAKT
  end
  alg = ilk_baslik['alg']
  jwk, anahtar_yolu = Ortak.jwk_sec(ilk_baslik, giris)
  izin = pol[:w].nil? ? nil : Ortak.tek_imza_izin_listesi(pol).map(&:to_sym)
  api = api.sub(', W.map(&:to_sym)', '') if izin.nil?
  begin
    jws = JSON::JWT.decode(girdi, jwk && JSON::JWK.new(jwk), izin)
    { sonuc_ham: 'kabul', hata_sinifi: nil, hata_ozeti: nil, api_yolu: api, anahtar_yolu: anahtar_yolu,
      dogrulanan: [{ 'sira' => 0, 'alg' => jws.alg.to_s, 'sonuc' => 'gecerli' }] }
  rescue JSON::JWT::Exception => e
    { sonuc_ham: 'red', hata_sinifi: sinifla(e, alg, !jwk.nil?), hata_ozeti: "#{e.class}: #{e.message}", api_yolu: api,
      anahtar_yolu: anahtar_yolu }
  rescue StandardError => e
    { sonuc_ham: 'istisna', hata_sinifi: 'istisna-diger', hata_ozeti: "#{e.class}: #{e.message}", api_yolu: api,
      anahtar_yolu: anahtar_yolu }
  end
end

Ortak.kos(ARGV) { |is| dogrula(is) }
