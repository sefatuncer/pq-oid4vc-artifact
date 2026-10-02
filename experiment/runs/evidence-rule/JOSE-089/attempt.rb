# Evidence-rule second attempt, JOSE-089 (json-jwt 1.17.2).
# Own keys and objects only. A = ES256, X = ES384 (json-jwt 1.17.2 has no EdDSA: lib/json/jws.rb L50-64).
require 'json/jwt'

MIG = 'https://issuer.example'
LEG = 'https://legacy-issuer.example'
$ok = 0
$n = 0

def pub_jwk(priv, kid, extra = {})
  JSON::JWK.new(OpenSSL::PKey::EC.new(priv.public_to_der), { kid: kid }.merge(extra))
end

def token(priv, alg, kid, iss)
  JSON::JWT.new(iss: iss, sub: 'user-1').sign(JSON::JWK.new(priv, kid: kid), alg).to_s
end

def run(label, expect = nil)
  res, detail = begin
    yield
    ['accept', '']
  rescue StandardError => e
    ['reject', "#{e.class}: #{e.message}"[0, 80]]
  end
  mark = '-'
  if expect
    $n += 1
    if res == expect then $ok += 1; mark = 'OK' else mark = 'MISMATCH' end
  end
  puts format('%-58s %-7s expect=%-7s %-9s %s', label, res, expect || '-', mark, detail)
end

mig_es = OpenSSL::PKey::EC.generate('prime256v1')
mig_x = OpenSSL::PKey::EC.generate('secp384r1')
leg_es = OpenSSL::PKey::EC.generate('prime256v1')
mig_set = JSON::JWK::Set.new(pub_jwk(mig_es, 'mig-es256'), pub_jwk(mig_x, 'mig-es384'))
leg_set = JSON::JWK::Set.new(pub_jwk(leg_es, 'leg-es256'))
all_set = JSON::JWK::Set.new(*mig_set, *leg_set)

t_mig_es = token(mig_es, :ES256, 'mig-es256', MIG)
t_mig_x = token(mig_x, :ES384, 'mig-es384', MIG)
t_leg_es = token(leg_es, :ES256, 'leg-es256', LEG)
bad = t_mig_x.sub(/\.([A-Za-z0-9_-])([A-Za-z0-9_-]*)\z/) { ".#{$1 == 'A' ? 'B' : 'A'}#{$2}" }

puts "== json-jwt #{Gem.loaded_specs['json-jwt'].version}, ruby #{RUBY_VERSION}"
puts 'JSON::JWT.decode parameters: ' + JSON::JWT.method(:decode).parameters.inspect

puts "\n== 1. Validity check (key set of the issuer, algorithms = W)"
w = [:ES256, :ES384]
run('V+ migrated ES256', 'accept') { JSON::JWT.decode(t_mig_es, mig_set, w) }
run('V+ migrated ES384', 'accept') { JSON::JWT.decode(t_mig_x, mig_set, w) }
run('V+ legacy ES256', 'accept') { JSON::JWT.decode(t_leg_es, leg_set, w) }
run('V- migrated ES384 corrupted', 'reject') { JSON::JWT.decode(bad, mig_set, w) }

puts "\n== 2. One configuration for both issuers (all keys in one JWK set; the only policy input is algorithms)"
[[:ES384], [:ES256, :ES384]].each do |algs|
  puts "algorithms = #{algs.inspect}"
  run('  migrated ES256 (L4c wants reject)', 'reject') { JSON::JWT.decode(t_mig_es, all_set, algs) }
  run('  migrated ES384 (L4c wants accept)', 'accept') { JSON::JWT.decode(t_mig_x, all_set, algs) }
  run('  legacy ES256 (L4c wants accept)', 'accept') { JSON::JWT.decode(t_leg_es, all_set, algs) }
end
puts '-> no single configuration gives the three L4c decisions.'

puts "\n== 3. Is an alg member of a JWK enforced? (migrated ES256 key labelled alg=ES384)"
labelled = JSON::JWK::Set.new(pub_jwk(mig_es, 'mig-es256', alg: 'ES384'), pub_jwk(mig_x, 'mig-es384', alg: 'ES384'))
run('  migrated ES256 with labelled key set, algorithms = W') { JSON::JWT.decode(t_mig_es, labelled, w) }
puts '-> accepted: the key set selects by kid only (lib/json/jose.rb L24-33); there is no per-key algorithm binding.'

puts "\n== 4. Per-issuer records applied by the caller (contract §5.3 'L4c (consecutive)'): one decode call per record"
records = { MIG => [mig_set, [:ES384]], LEG => [leg_set, [:ES256, :ES384]] }
route = ->(t) { records.fetch(JSON::JWT.decode(t, :skip_verification)[:iss]) }   # caller reads the unverified iss
run('  migrated ES256', 'reject') { JSON::JWT.decode(t_mig_es, *route.(t_mig_es)) }
run('  migrated ES384', 'accept') { JSON::JWT.decode(t_mig_x, *route.(t_mig_x)) }
run('  legacy ES256', 'accept') { JSON::JWT.decode(t_leg_es, *route.(t_leg_es)) }
puts '-> the library applies a per-call allow-list (L2); choosing the record per object is caller code outside the library.'

puts "\n== 5. Form basis: General JSON with two signatures (only the first is processed)"
h = ->(alg, kid) { Base64.urlsafe_encode64({ alg: alg, kid: kid }.to_json, padding: false) }
payload = Base64.urlsafe_encode64({ iss: MIG, sub: 'user-1' }.to_json, padding: false)
sig = lambda do |priv, alg, kid|
  jws = JSON::JWS.new(JSON::JWT.new({}))
  jws.signature_base_string = "#{h.(alg, kid)}.#{payload}"
  jws.header = { alg: alg, kid: kid }
  jws.sign!(priv)
  { protected: h.(alg, kid), signature: Base64.urlsafe_encode64(jws.signature, padding: false) }
end
s_es = sig.(mig_es, :ES256, 'mig-es256')
s_x = sig.(mig_x, :ES384, 'mig-es384')
s_x_bad = s_x.merge(signature: s_x[:signature].sub(/\A./) { |c| c == 'A' ? 'B' : 'A' })
run('  [ES256 valid, ES384 corrupted]') { JSON::JWT.decode({ payload: payload, signatures: [s_es, s_x_bad] }, mig_set, w) }
run('  [ES384 corrupted, ES256 valid]') { JSON::JWT.decode({ payload: payload, signatures: [s_x_bad, s_es] }, mig_set, w) }
run('  [ES256 valid] only') { JSON::JWT.decode({ payload: payload, signatures: [s_es] }, mig_set, w) }
puts '-> the result depends only on signatures[0] (lib/json/jws.rb L199-216).'

puts "\n== SUMMARY: checked rows OK = #{$ok} of #{$n}"
