// SDJWT-001: A-SIT Plus vck 7.0.1 (Signum josef/supreme dependencies with vck's own versions).
// Verification route: SdJwtSigned.parseCatching → vck's JWS verification function VerifyJwsObject (the same function that
// ValidatorSdJwt uses for the issuer signature; key: jwk/x5c in the header or PublicJsonWebKeyLookup = the experiment's JWKS).
// ValidatorSdJwt.verifySdJwt is for the wallet side and requires the cnf binding ("cnf claim invalid"); the verifier
// side verifyVpSdJwt requires a KB-JWT. Neither is present in the V± and battery vectors → the signature layer is measured (reading of PR §2H item 15;
// noted here). SD-JWT compact only (B6). No algorithm allow-list API → IZIN-*/L4* ifade-edilemedi.
package c3

import at.asitplus.signum.indispensable.josef.JsonWebKey
import at.asitplus.signum.indispensable.josef.JwsCompact
import at.asitplus.wallet.lib.jws.PublicJsonWebKeyLookup
import at.asitplus.wallet.lib.jws.SdJwtSigned
import at.asitplus.wallet.lib.jws.VerifyJwsObject
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.json.JsonObject

object Vck : T {
  override val ver = "vck 7.0.1 (indispensable-josef 3.24.0, supreme 0.15.0)"
  override val api = "SdJwtSigned.parseCatching(s) → VerifyJwsObject(publicKeyLookup = JWKS)(sd.jws)"
  override val formats = setOf("sd-jwt-compact", "compact-as-sdjwt")

  val jwks: Set<JsonWebKey> by lazy {
    KID.values.mapNotNull { runCatching { J.decodeFromString(JsonWebKey.serializer(), it.toString()) }.getOrNull() }.toSet()
  }
  val vjo by lazy {
    VerifyJwsObject(publicKeyLookup = object : PublicJsonWebKeyLookup {
      override suspend fun invoke(jws: JwsCompact): Set<JsonWebKey> = jwks
    })
  }

  override fun verify(job: JsonObject, data: ByteArray, X: String): List<Map<String, Any>> {
    if (temel(job.s("politika")) !in VARSAYILAN) throw IfadeEdilemedi("vck: algoritma izin listesi API'si yok")
    var s = data.decodeToString().trim()
    if (job.s("serilestirme") == "compact") s += "~"
    val sd = SdJwtSigned.parseCatching(s).getOrElse { e ->
      // An unrecognised alg surfaces during JwsHeader parsing from the JwsAlgorithm serializer; vck wraps it into the
      // message "Invalid base64url content". The serializer is searched in the cause chain.
      var c: Throwable? = e
      while (c != null) {
        if (c.stackTrace.any { it.className.contains("JwsAlgorithm") } || (c.message ?: "").contains("JwsAlgorithm"))
          throw IllegalArgumentException("unsupported algorithm (JwsAlgorithm)", e)
        c = c.cause
      }
      throw e
    }
    runBlocking { vjo(sd.jws) }.getOrThrow()
    return sonuc(sd.jws.jwsHeader.algorithm.identifier)
  }
}

fun main(a: Array<String>) = calistir(a) { h -> if (h == "SDJWT-001") Vck else throw IllegalArgumentException(h) }
