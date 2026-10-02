// Evidence-rule second attempt, COSE-001 (Signum indispensable-cosef 3.26.0).
// Own keys and objects only. A = ES256, X = ES384 (no EdDSA in CoseAlgorithm.Signature).
import at.asitplus.signum.indispensable.CryptoPublicKey
import at.asitplus.signum.indispensable.CryptoSignature
import at.asitplus.signum.indispensable.ECCurve
import at.asitplus.signum.indispensable.cosef.CoseAlgorithm
import at.asitplus.signum.indispensable.cosef.CoseHeader
import at.asitplus.signum.indispensable.cosef.CoseSigned
import at.asitplus.signum.indispensable.getJCASignatureInstance
import at.asitplus.signum.indispensable.jcaSignatureBytes
import at.asitplus.signum.indispensable.parseFromJca
import kotlinx.serialization.builtins.ByteArraySerializer
import java.lang.reflect.Modifier
import java.security.KeyPair
import java.security.KeyPairGenerator
import java.security.PublicKey
import java.security.spec.ECGenParameterSpec

const val MIG = "https://issuer.example"
const val LEG = "https://legacy-issuer.example"
var ok = 0
var n = 0

fun ec(curve: String): KeyPair =
    KeyPairGenerator.getInstance("EC").apply { initialize(ECGenParameterSpec(curve)) }.generateKeyPair()

fun sign1(kp: KeyPair, alg: CoseAlgorithm.Signature, curve: ECCurve, kid: String, iss: String): ByteArray {
    val ph = CoseHeader(algorithm = alg, kid = kid.encodeToByteArray())
    val payload = """{"iss":"$iss","sub":"user-1"}""".encodeToByteArray()
    val input = CoseSigned.prepare(ph, byteArrayOf(), payload, ByteArraySerializer())
    val jca = alg.algorithm.getJCASignatureInstance().getOrThrow()
    jca.initSign(kp.private); jca.update(input.serialize())
    val sig = CryptoSignature.EC.parseFromJca(jca.sign()).withCurve(curve)
    return CoseSigned.create(ph, null, payload, sig, ByteArraySerializer()).serialize(ByteArraySerializer())
}

fun report(label: String, accepted: Boolean?, detail: String, expect: String?) {
    val res = if (accepted == true) "accept" else "reject"
    var mark = "-"
    if (expect != null) { n++; if (res == expect) { ok++; mark = "OK" } else mark = "MISMATCH" }
    println("%-54s %-7s expect=%-7s %-9s %s".format(label, res, expect ?: "-", mark, detail.take(80)))
}

fun main() {
    println("== indispensable-cosef 3.26.0, java " + System.getProperty("java.version"))
    val migEs = ec("secp256r1"); val migX = ec("secp384r1"); val legEs = ec("secp256r1")
    val oMigEs = sign1(migEs, CoseAlgorithm.Signature.ES256, ECCurve.SECP_256_R_1, "mig-es256", MIG)
    val oMigX = sign1(migX, CoseAlgorithm.Signature.ES384, ECCurve.SECP_384_R_1, "mig-es384", MIG)
    val oLegEs = sign1(legEs, CoseAlgorithm.Signature.ES256, ECCurve.SECP_256_R_1, "leg-es256", LEG)

    println("\n== 1. Public API of CoseSigned (reflection on the pinned jar)")
    val pub = { c: Class<*> -> c.declaredMethods.filter { Modifier.isPublic(it.modifiers) }.map { it.name }.distinct().sorted() }
    println("CoseSigned methods: " + pub(CoseSigned::class.java))
    println("CoseSigned.Companion methods: " + pub(CoseSigned.Companion::class.java))
    val any = (pub(CoseSigned::class.java) + pub(CoseSigned.Companion::class.java)).any { it.contains("verif", ignoreCase = true) }
    println("any method containing 'verif': $any")
    val parsed = CoseSigned.deserialize(ByteArraySerializer(), oMigEs).getOrThrow()
    println("deserialize() of the migrated ES256 object succeeds; it carries alg=${parsed.protectedHeader.algorithm} and is not verified")

    // The only path to a verification decision: the caller takes prepareCoseSignatureInput() and verifies
    // it with a primitive of its own choice (JCA here; Supreme is not in the dependency closure).
    fun callerVerify(bytes: ByteArray, key: PublicKey, alg: CoseAlgorithm.Signature): Pair<Boolean, String> {
        val cs = CoseSigned.deserialize(ByteArraySerializer(), bytes).getOrThrow()
        val jca = alg.algorithm.getJCASignatureInstance().getOrThrow()
        jca.initVerify(key); jca.update(cs.prepareCoseSignatureInput())
        return try { jca.verify(cs.signature.jcaSignatureBytes) to "" } catch (e: Exception) { false to e.toString() }
    }

    println("\n== 2. Validity check (verification assembled by the caller, alg taken from the header)")
    for ((label, o, k) in listOf(Triple("V+ migrated ES256", oMigEs, migEs.public),
                                 Triple("V+ migrated ES384", oMigX, migX.public),
                                 Triple("V+ legacy ES256", oLegEs, legEs.public))) {
        val alg = CoseSigned.deserialize(ByteArraySerializer(), o).getOrThrow().protectedHeader.algorithm as CoseAlgorithm.Signature
        val (r, d) = callerVerify(o, k, alg); report(label, r, d, "accept")
    }
    val bad = oMigEs.copyOf().also { it[it.size - 3] = (it[it.size - 3].toInt() xor 1).toByte() }
    report("V- migrated ES256 corrupted", callerVerify(bad, migEs.public, CoseAlgorithm.Signature.ES256).first, "", "reject")

    println("\n== 3. L4c with own code (B4 record only): per-issuer policy + own verification")
    // BEGIN custom
    val keys = mapOf(MIG to mapOf("mig-es256" to migEs.public, "mig-es384" to migX.public),
                     LEG to mapOf("leg-es256" to legEs.public))
    val required = mapOf(MIG to setOf(CoseAlgorithm.Signature.ES384), LEG to emptySet<CoseAlgorithm.Signature>())
    fun l4c(bytes: ByteArray, iss: String): Pair<Boolean, String> {
        val cs = CoseSigned.deserialize(ByteArraySerializer(), bytes).getOrThrow()
        val alg = cs.protectedHeader.algorithm as? CoseAlgorithm.Signature ?: return false to "no alg"
        val r = required.getValue(iss)
        if (r.isNotEmpty() && alg !in r) return false to "alg $alg not acceptable for $iss"
        val key = keys.getValue(iss)[cs.protectedHeader.kid?.decodeToString()] ?: return false to "no key"
        return callerVerify(bytes, key, alg)
    }
    // END custom
    l4c(oMigEs, MIG).let { report("L4c migrated ES256", it.first, it.second, "reject") }
    l4c(oMigX, MIG).let { report("L4c migrated ES384", it.first, it.second, "accept") }
    l4c(oLegEs, LEG).let { report("L4c legacy ES256", it.first, it.second, "accept") }
    println("(these decisions come from the own code above, not from a library mechanism)")

    println("\n== SUMMARY: checked rows OK = $ok of $n")
}
