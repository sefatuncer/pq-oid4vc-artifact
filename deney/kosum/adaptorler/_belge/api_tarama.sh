#!/usr/bin/env bash
# =====================================================================
#  PQ-OID4VC | C3 | API taraması (sözleşme §5.1; ÖK §4.14) — yürütücünün yazdığı adaptörler
#  Her hedef için imajın içindeki SABİT sürümlü kütüphane kaynağı (ya da JVM'de genel API'nin bayt kodu)
#  taranır; komut ve çıktı <hedef>/kanit/api-tarama.txt'ye yazılır.
#  Kullanım: bash _belge/api_tarama.sh [hedef_id]   (deney/kosum/adaptorler içinden; hedef verilmezse hepsi)
# =====================================================================
set -u
cd "$(dirname "$0")/.."
export MSYS_NO_PATHCONV=1
HEDEF="${1:-}"
P='algorithms|allow|register|deregister|required|eddsa|ed25519|ml-?dsa|mldsa|composite|okp|verifier|keyselector'
tara() { # <hedef> <imaj> <iç komut>
  local h=$1 img=$2 cmd=$3
  [ -n "$HEDEF" ] && [ "$h" != "$HEDEF" ] && return
  mkdir -p "$h/kanit"
  {
    echo "# $h — API taraması (sözleşme §5.1)"
    echo "# imaj: $img ($(docker image inspect --format '{{.Id}}' "$img"))"
    echo "# komut: docker run --rm --network none --entrypoint sh $img -c '$cmd'"
    echo
    docker run --rm --network none --entrypoint sh "$img" -c "$cmd" 2>&1 | cut -c1-240 | head -400
  } > "$h/kanit/api-tarama.txt"
  echo "$h: $(wc -l < "$h/kanit/api-tarama.txt") satır"
}
SP='/e/lib/python3*/site-packages'

tara JOSE-083 a10-jose-083:1 "cd $SP/jwt && grep -rn -i -E '$P' --include=*.py . "
tara JOSE-084 a10-jose-084:1 "cd $SP/jose && grep -rn -i -E '$P' --include=*.py . "
tara SDJWT-018 a10-sdjwt-018:1 "cd $SP && grep -rn -i -E '$P|cb_get_issuer_key|ES256' --include=*.py sd_jwt; grep -n -i -E 'ML-DSA|mldsa|EdDSA|Ed25519|OKP|AKP' jwcrypto/jwa.py jwcrypto/jwk.py | head -80"
tara JOSE-009 a10-jose-009:1 "cd /a/node_modules/jose && cat package.json | grep '\"version\"'; grep -rn -i -E '$P' dist/types/types.d.ts | head -120; grep -rln -i 'ML-DSA' dist/webapi | head"
tara JOSE-065 a10-jose-065:1 "cd /a/node_modules/jsonwebtoken && grep '\"version\"' package.json; grep -rn -i -E '$P|PUB_KEY_ALGS|EC_KEY_ALGS' *.js lib/*.js"
tara COSE-014 a10-cose-014:1 "cd /a/node_modules/cose-js && grep '\"version\"' package.json; grep -rn -i -E '$P|AlgToTags|ES256|-7|-8' lib/*.js | head -120"
tara SDJWT-015 a10-sdjwt-015:1 "cd /a/node_modules/@sd-jwt/core && grep '\"version\"' package.json; grep -rn -i -E '$P|allowedIssuerAlgorithms|kbVerifier' dist/index.d.mts | head -120"
# Go: kaynak yalnız derleme aşamasında (modül önbelleği); aynı Dockerfile'ın 'b' aşaması geçici imaj olarak kurulur
docker build -q --target b -t pq-a10-go-b:gecici ./_go >/dev/null
M=/go/pkg/mod/github.com
tara JOSE-033 pq-a10-go-b:gecici "cd $M/golang-jwt/jwt/v5@*/ && grep -rn -i -E '$P|WithValidMethods|RegisterSigningMethod|SigningMethodEd' --include=*.go . | grep -v _test.go | head -150"
tara JOSE-034 pq-a10-go-b:gecici "cd $M/dvsekhvalnov/jose2go@*/ && grep -rn -i -E '$P|RegisterJws|DeregisterJws|ES256|EdDSA' --include=*.go . | grep -v _test.go | head -150"
tara COSE-034 pq-a10-go-b:gecici "cd $M/veraison/go-cose@*/ && grep -rn -i -E '$P|AlgorithmEdDSA|AlgorithmES256|AlgorithmMLDSA|NewVerifier' --include=*.go . | grep -v _test.go | head -150"
docker image rm pq-a10-go-b:gecici >/dev/null
# JVM: genel API'nin bayt kodu (javap -public) yağ JAR'dan
J='javap -public -cp /a/adaptor.jar'
tara JOSE-052 a10-jvm:1 "$J com.auth0.jwt.algorithms.Algorithm | grep -i -E 'static|verify'; $J com.auth0.jwt.interfaces.Verification | head -5"
tara JOSE-055 a10-jvm:1 "$J 'io.jsonwebtoken.Jwts\$SIG' | head -40; $J io.jsonwebtoken.JwtParserBuilder | grep -i -E 'sig|key|unsecured'"
tara SDJWT-004 a10-jvm:1 "$J com.authlete.sd.SDJWT | head -30; $J com.nimbusds.jose.JWSAlgorithm | grep -E 'public static final'; $J com.nimbusds.jose.proc.JWSVerificationKeySelector | head -20; $J com.nimbusds.jose.crypto.factories.DefaultJWSVerifierFactory | head"
K='CP=$(ls /a/app/lib/*.jar | tr "\n" ":"); javap -public -cp $CP'
C1='at.asitplus.signum.indispensable.cosef.CoseSigned$Companion'
tara COSE-001 a10-kt-cose:1 "cd /tmp; for j in /a/app/lib/indispensable-cosef-*.jar; do jar tf \$j | grep -E 'CoseAlgorithm.Signature.[A-Z]' ; jar tf \$j | grep -i -E 'CoseSign[^e1]|mldsa|eddsa' ; done; $K '$C1'"
tara SDJWT-001 a10-kt-sdjwt:1 "cd /tmp; for j in /a/app/lib/indispensable-josef-*.jar /a/app/lib/supreme-*.jar; do echo == \$j; jar tf \$j | grep -i -E 'JwsAlgorithm.Signature|mldsa|eddsa|ed25519' ; done; $K at.asitplus.wallet.lib.agent.ValidatorSdJwt | grep verify; $K at.asitplus.wallet.lib.jws.VerifyJwsObject | grep -E 'invoke|public at'"
