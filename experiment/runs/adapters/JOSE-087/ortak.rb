# frozen_string_literal: true
# Shared adapter skeleton (Ruby) — C3 adapter contract 1.0 (experiment/oracle/oracle-A/adapter-contract.md) / RUNNER.md §1–§3.
# This file is IDENTICAL in JOSE-087 and JOSE-089. The library-specific verification is in adaptor.rb.
# NO verification loop: signature verification is done only by the documented API of the target library.
# No network access; only /v (vectors), /anahtarlar and the job file are read.
require 'json'
require 'base64'

module Ortak
  SOZLESME = 'adaptor-sozlesme/1.0'
  A = 'ES256'
  X_KOL = {
    'kontrol-EdDSA' => 'EdDSA', 'kontrol-Ed25519' => 'Ed25519', 'kontrol-ES384' => 'ES384',
    'tedavi-ML-DSA-65' => 'ML-DSA-65', 'tedavi-composite' => 'ML-DSA-65-ES256'
  }.freeze

  module_function

  def b64d(s)
    Base64.urlsafe_decode64(s + '=' * ((4 - s.length % 4) % 4))
  end

  # Path of the job row under /v: RUNNER §2 (/v = v1.3) or /v = vektorler/ (file with the prefix "v1.3/...")
  def vektor_yolu(dosya)
    adaylar = ["/v/#{dosya}", "/v/#{dosya.sub(%r{\Av1\.3/}, '')}"]
    adaylar.find { |y| File.exist?(y) } || adaylar.first
  end

  def manifest
    @manifest ||= begin
      y = ['/v/MANIFEST.json', '/v/v1.3/MANIFEST.json'].find { |p| File.exist?(p) }
      raise 'MANIFEST.json bulunamadi' unless y
      # Only dogrulama_girdileri is kept; `insa` (construction facts) and the other fields are NOT read (maintainers 01.10).
      JSON.parse(File.read(y))['vektorler'].to_h { |e| [e['id'], { 'dogrulama_girdileri' => e['dogrulama_girdileri'] || {} }] }
    end
  end

  def anahtar_dosyasi(goreli)
    "/anahtarlar/#{goreli.sub(%r{\Aanahtarlar/}, '')}"
  end

  def jwks_oku(goreli)
    @jwks ||= {}
    @jwks[goreli] ||= JSON.parse(File.read(anahtar_dosyasi(goreli)))
  end

  # Policy → (W, R). METHOD.md §2; RUNNER §1. VARSAYILAN: contract §5.2 L5 (key only).
  def politika(is, kutuphane_algleri)
    taban = is['politika'].split('|').first.split('@').first # maintainers: the suffixes '|sdjwtvc=..' and '@-19' only split the oracle
    x = X_KOL[is['kol']]
    case taban
    when 'GEC', 'P0', 'P1', 'P2' then { w: kutuphane_algleri, r: [], taban: taban }
    when 'VARSAYILAN' then { w: nil, r: [], taban: taban }
    when 'IZIN-A' then { w: [A], r: [], taban: taban }
    when 'IZIN-AX'
      raise "kol #{is['kol']} icin X tanimsiz" unless x
      { w: [A, x], r: [], taban: taban }
    when 'L4', 'L4-S', 'L4-Y', 'L4-YOL'
      raise "kol #{is['kol']} icin X tanimsiz" unless x
      { w: [A, x], r: [x], taban: taban }
    else raise "bilinmeyen politika #{is['politika']}"
    end
  end

  # For a single-signature object with R ≠ ∅ the effective allow-list is R (R ⊆ W; a single signature satisfies R only if it is X itself).
  def tek_imza_izin_listesi(pol)
    pol[:r].empty? ? pol[:w] : pol[:r]
  end

  # Key selection (contract §8 item 1: the same path in all arms = "JWK"): header kid → the vector's JWKS;
  # without a kid the manifest alg_kid[alg]; without that the single kid. DPoP: the jwk in the header ("jwk-basligi").
  def jwk_sec(baslik, giris)
    dg = giris['dogrulama_girdileri'] || {}
    if dg['anahtar'] == 'jwk basligindan'
      return [baslik['jwk'], 'jwk-basligi']
    end
    return [nil, 'JWK'] unless dg['jwks']
    anahtarlar = jwks_oku(dg['jwks'])['keys']
    kid = baslik['kid']
    if kid.nil?
      ak = dg['alg_kid']
      ak = JSON.parse(ak) if ak.is_a?(String)
      kid = ak[baslik['alg']] if ak.is_a?(Hash)
      kid ||= dg['kid'].first if dg['kid'].is_a?(Array) && dg['kid'].size == 1
    end
    [anahtarlar.find { |k| k['kid'] == kid }, 'JWK']
  end

  def kosu_adi(cikti)
    return ENV['KOSU'] if ENV['KOSU'] && !ENV['KOSU'].empty?
    ad = File.basename(cikti, '.jsonl')
    parca = ad.split('.')
    parca.size >= 2 ? parca.last : 'oncesi'
  end

  def sabit(ad, varsayilan = '')
    y = "/opt/a/#{ad}"
    File.exist?(y) ? File.read(y).strip : varsayilan
  end

  def satir(is, kosu, sonuc, sure_ms, anahtar_yolu)
    {
      'sozlesme' => SOZLESME,
      'hedef_id' => ENV['HEDEF_ID'] || 'bilinmiyor',
      'hedef_surum' => sabit('HEDEF_SURUM'),
      'adaptor_sha256' => sabit('ADAPTOR_SHA256'),
      'kosu' => kosu,
      'vektor_id' => is['vektor_id'],
      'politika' => is['politika'],
      'kol' => is['kol'],
      'sonuc_ham' => sonuc[:sonuc_ham],
      'hata_sinifi' => sonuc[:hata_sinifi],
      'hata_ozeti' => sonuc[:hata_ozeti] && sonuc[:hata_ozeti].to_s[0, 200],
      'dogrulanan_algoritmalar' => sonuc[:dogrulanan] || [],
      'api_yolu' => sonuc[:api_yolu],
      'anahtar_yolu' => anahtar_yolu,
      'sure_ms' => sure_ms
    }
  end

  # Main loop: every job row in sequence in one process; 60 s per vector (Timeout).
  def kos(argv)
    require 'timeout'
    girdi, cikti = argv
    raise 'usage: adaptor <jobs-v1.3.jsonl> <output.jsonl>' unless girdi && cikti
    kosu = kosu_adi(cikti)
    File.open(cikti, 'w') do |out|
      File.foreach(girdi) do |l|
        next if l.strip.empty?
        is = JSON.parse(l)
        t0 = Process.clock_gettime(Process::CLOCK_MONOTONIC)
        anahtar_yolu = nil
        sonuc = begin
          Timeout.timeout(60) do
            r = yield(is)
            anahtar_yolu = r[:anahtar_yolu]
            r
          end
        rescue Timeout::Error
          { sonuc_ham: 'zaman-asimi', hata_sinifi: 'zaman-asimi', hata_ozeti: '60 s asildi', api_yolu: nil }
        rescue StandardError => e
          { sonuc_ham: 'istisna', hata_sinifi: 'adaptor-hatasi', hata_ozeti: "#{e.class}: #{e.message}", api_yolu: nil }
        end
        ms = ((Process.clock_gettime(Process::CLOCK_MONOTONIC) - t0) * 1000).round
        out.puts(JSON.generate(satir(is, kosu, sonuc, ms, anahtar_yolu)))
        out.flush
      end
    end
  end

  def b6(api)
    { sonuc_ham: 'uygulanamaz', hata_sinifi: 'bicim-desteklenmiyor', hata_ozeti: 'B6: MAPPING.md (API incelemesi)', api_yolu: api }
  end

  def ifade_edilemedi(neden, api)
    { sonuc_ham: 'ifade-edilemedi', hata_sinifi: nil, hata_ozeti: neden, api_yolu: api }
  end
end
