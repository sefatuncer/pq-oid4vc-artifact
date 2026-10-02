// Evidence-rule second attempt, SDJWT-001 (vck 7.0.1).
// Own keys and objects only. A = ES256, X = ES384 (Signum JwsAlgorithm has no EdDSA).
import at.asitplus.signum.indispensable.josef.JsonWebKey
import at.asitplus.signum.indispensable.josef.JwsCompact
import at.asitplus.wallet.lib.agent.ValidatorSdJwt
import at.asitplus.wallet.lib.agent.VerifySignature
import at.asitplus.wallet.lib.jws.PublicJsonWebKeyLookup
import at.asitplus.wallet.lib.jws.SdJwtSigned
import at.asitplus.wallet.lib.jws.VerifyJwsObject
import at.asitplus.wallet.lib.jws.VerifyJwsSignature
import at.asitplus.wallet.lib.jws.VerifyJwsSignatureFun
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import java.math.BigInteger
import java.security.KeyPair
import java.security.KeyPairGenerator
import java.security.Signature
import java.security.interfaces.ECPublicKey
import java.security.spec.ECGenParameterSpec
import java.util.Base64

const val MIG = "https://issuer.example"
const val LEG = "https://legacy-issuer.example"
var ok = 0
var n = 0

fun b64(b: ByteArray): String = Base64.getUrlEncoder().withoutPadding().encodeToString(b)
fun fixed(i: BigInteger, len: Int): ByteArray { val b = i.toByteArray().dropWhile { it == 0.toByte() }.toByteArray(); return ByteArray(len - b.size) + b }
fun ec(curve: String): KeyPair = KeyPairGenerator.getInstance("EC").apply { initialize(ECGenParameterSpec(curve)) }.generateKeyPair()
fun jwkJson(kp: KeyPair, kid: String?): String {
    val p = kp.public as ECPublicKey; val len = (p.params.curve.field.fieldSize + 7) / 8
    val crv = if (len == 32) "P-256" else "P-384"
    return """{"kty":"EC","crv":"$crv","x":"${b64(fixed(p.w.affineX, len))}","y":"${b64(fixed(p.w.affineY, len))}"${kid?.let { ",\"kid\":\"$it\"" } ?: ""}}"""
}
fun jwk(kp: KeyPair, kid: String): JsonWebKey = JsonWebKey.deserialize(jwkJson(kp, kid)).getOrThrow()

fun sdJwt(kp: KeyPair, alg: String, kid: String, iss: String, embedJwk: Boolean = false): String {
    val extra = if (embedJwk) ",\"jwk\":" + jwkJson(kp, null) else ""
    val hdr = """{"alg":"$alg","typ":"dc+sd-jwt","kid":"$kid"$extra}"""
    val pl = """{"iss":"$iss","vct":"urn:example:pid","sub":"user-1","_sd_alg":"sha-256"}"""
    val si = b64(hdr.toByteArray()) + "." + b64(pl.toByteArray())
    val jca = Signature.getInstance(if (alg == "ES256") "SHA256withECDSAinP1363Format" else "SHA384withECDSAinP1363Format")
    jca.initSign(kp.private); jca.update(si.toByteArray())
    return si + "." + b64(jca.sign()) + "~"
}
fun corrupt(s: String): String { val i = s.lastIndexOf('.') + 5; return s.substring(0, i) + (if (s[i] == 'A') 'B' else 'A') + s.substring(i + 1) }

fun run(label: String, v: ValidatorSdJwt, sd: String, expect: String?) = runBlocking {
    val r = v.verifySdJwt(SdJwtSigned.parseCatching(sd).getOrThrow(), null)
    val res = if (r.isSuccess) "accept" else "reject"
    var mark = "-"
    if (expect != null) { n++; if (res == expect) { ok++; mark = "OK" } else mark = "MISMATCH" }
    println("%-56s %-7s expect=%-7s %-9s %s".format(label, res, expect ?: "-", mark, (r.exceptionOrNull()?.message ?: "").take(70)))
}

fun main() {
    println("== vck 7.0.1, java " + System.getProperty("java.version"))
    val migEs = ec("secp256r1"); val migX = ec("secp384r1"); val legEs = ec("secp256r1")
    // the verifier always holds the complete key set of each issuer
    val issuerKeys = mapOf(MIG to setOf(jwk(migEs, "mig-es256"), jwk(migX, "mig-es384")), LEG to setOf(jwk(legEs, "leg-es256")))
    val pMigEs = sdJwt(migEs, "ES256", "mig-es256", MIG)
    val pMigX = sdJwt(migX, "ES384", "mig-es384", MIG)
    val pLegEs = sdJwt(legEs, "ES256", "leg-es256", LEG)
    val pMigEsJwk = sdJwt(migEs, "ES256", "mig-es256", MIG, embedJwk = true)
    fun iss(jws: JwsCompact) = Json.parseToJsonElement(jws.plainPayload.decodeToString()).jsonObject["iss"]?.jsonPrimitive?.content

    println("\n== 1. Validity check: documented key lookup only (no policy)")
    val vDefault = ValidatorSdJwt(verifyJwsObject = VerifyJwsObject(publicKeyLookup = PublicJsonWebKeyLookup { jws -> issuerKeys[iss(jws)] }))
    run("V+ migrated ES256", vDefault, pMigEs, "accept")
    run("V+ migrated ES384", vDefault, pMigX, "accept")
    run("V+ legacy ES256", vDefault, pLegEs, "accept")
    run("V- migrated ES256 corrupted", vDefault, corrupt(pMigEs), "reject")

    // L4c policy records (one configuration shared by all calls of one ValidatorSdJwt instance)
    val W = setOf("ES256", "ES384")
    val R = mapOf(MIG to setOf("ES384"), LEG to emptySet())
    fun acceptable(jws: JwsCompact): Boolean {
        val r = R[iss(jws)] ?: return false
        val alg = jws.jwsHeader.algorithm.identifier
        return alg in W && (r.isEmpty() || alg in r)
    }

    println("\n== 2. L4c through the documented PublicJsonWebKeyLookup callback (one ValidatorSdJwt instance)")
    val vLookup = ValidatorSdJwt(verifyJwsObject = VerifyJwsObject(
        publicKeyLookup = PublicJsonWebKeyLookup { jws -> if (acceptable(jws)) issuerKeys[iss(jws)] else null }))
    run("L4c migrated ES256", vLookup, pMigEs, "reject")
    run("L4c migrated ES384", vLookup, pMigX, "accept")
    run("L4c legacy ES256", vLookup, pLegEs, "accept")
    run("L4c migrated ES256 with own key in header jwk", vLookup, pMigEsJwk, null)
    println("(VerifyJwsObject uses a header jwk/x5c/jku before the lookup, so the lookup is not consulted for that object)")

    println("\n== 3. L4c through the documented VerifyJwsSignatureFun parameter (same policy, applied to every key)")
    val base = VerifyJwsSignature(VerifySignature())
    val policySig = VerifyJwsSignatureFun { jws, key ->
        if (acceptable(jws)) base(jws, key) else at.asitplus.KmmResult.failure(IllegalArgumentException("alg not acceptable for issuer"))
    }
    val vSig = ValidatorSdJwt(verifyJwsObject = VerifyJwsObject(verifyJwsSignature = policySig,
        publicKeyLookup = PublicJsonWebKeyLookup { jws -> issuerKeys[iss(jws)] }))
    run("L4c migrated ES256", vSig, pMigEs, "reject")
    run("L4c migrated ES384", vSig, pMigX, "accept")
    run("L4c legacy ES256", vSig, pLegEs, "accept")
    run("L4c migrated ES256 with own key in header jwk", vSig, pMigEsJwk, "reject")
    run("L4c migrated ES384 corrupted", vSig, corrupt(pMigX), "reject")

    println("\n== SUMMARY: checked rows OK = $ok of $n")
}
