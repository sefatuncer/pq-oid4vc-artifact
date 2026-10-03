// COSE-001: Signum indispensable-cosef 3.26.0 (+ supreme 0.16.0 verifiers). Only COSE_Sign1 (CoseSigned);
// there is no COSE_Sign (multi-signer) class → uygulanamaz (B6). No algorithm allow-list API: the application builds the
// verifier with the algorithm of the header, and the library does not check the header–verifier match → IZIN-*/L4* ifade-edilemedi.
package c3

import at.asitplus.signum.indispensable.CryptoPublicKey
import at.asitplus.signum.indispensable.CryptoSignature
import at.asitplus.signum.indispensable.ECCurve
import at.asitplus.signum.indispensable.cosef.CoseAlgorithm
import at.asitplus.signum.indispensable.cosef.CoseSigned
import at.asitplus.signum.supreme.sign.verifierFor
import at.asitplus.signum.supreme.sign.verify
import kotlinx.serialization.builtins.ByteArraySerializer
import kotlinx.serialization.json.JsonObject

object Cose : T {
  override val ver = "indispensable-cosef 3.26.0 / supreme 0.16.0"
  override val api = "CoseSigned.deserialize(ByteArraySerializer(), b) → verifierFor(protectedHeader.algorithm, key).verify(prepareCoseSignatureInput(), signature)"
  override val formats = setOf("COSE_Sign1")

  fun ecKey(j: JsonObject): CryptoPublicKey {
    if (j.s("kty") != "EC") throw IllegalArgumentException("unsupported key type ${j.s("kty")} ${j.s("alg")}")
    val c = when (j.s("crv")) { "P-256" -> ECCurve.SECP_256_R_1; "P-384" -> ECCurve.SECP_384_R_1; else -> ECCurve.SECP_521_R_1 }
    return CryptoPublicKey.EC.fromUncompressed(c, b64d(j.s("x")), b64d(j.s("y")))
  }

  override fun verify(job: JsonObject, data: ByteArray, X: String): List<Map<String, Any>> {
    if (temel(job.s("politika")) !in VARSAYILAN) throw IfadeEdilemedi("Signum: algoritma izin listesi API'si yok; doğrulayıcı başlıktaki alg ile kurulur")
    val cs = CoseSigned.deserialize(ByteArraySerializer(), data).getOrElse { e ->
      // An unrecognised alg value surfaces during header parsing as a NoSuchElementException from CoseAlgorithmSerializer.
      if (e.stackTrace.any { it.className.endsWith("CoseAlgorithmSerializer") }) throw IllegalArgumentException("unsupported algorithm (CoseAlgorithmSerializer)", e)
      throw e
    }
    val alg = (cs.protectedHeader.algorithm ?: throw IllegalArgumentException("unsupported: protected alg yok")) as? CoseAlgorithm.Signature
      ?: throw IllegalArgumentException("unsupported: imza algoritması değil")
    // The COSE kid is the base64url-decoded JWK kid (32 bytes): it is encoded back to base64url to find the JWK.
    val kid = (cs.protectedHeader.kid ?: cs.unprotectedHeader?.kid)?.let { java.util.Base64.getUrlEncoder().withoutPadding().encodeToString(it) }
    val name = alg.toString()
    val jwk = (if (kid != null) KID[kid] else null)
      ?: ALG2KID.entries.firstOrNull { name.contains(it.key) && it.key.startsWith("ES") }?.let { KID[it.value] }
      ?: throw IllegalArgumentException("no key for kid=$kid alg=$name")
    val sig = cs.signature as CryptoSignature
    alg.verifierFor(ecKey(jwk)).getOrThrow().verify(cs.prepareCoseSignatureInput(byteArrayOf(), null), sig).getOrThrow()
    return sonuc(name)
  }
}

fun main(a: Array<String>) = calistir(a) { h -> if (h == "COSE-001") Cose else throw IllegalArgumentException(h) }
