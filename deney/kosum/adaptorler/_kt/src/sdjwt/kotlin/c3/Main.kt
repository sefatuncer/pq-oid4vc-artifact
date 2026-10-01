// SDJWT-001: A-SIT Plus vck 7.0.1 (Signum josef/supreme bağımlılıkları vck'nin kendi sürümleriyle).
// Doğrulama yolu: SdJwtSigned.parseCatching → vck'nin JWS doğrulama işlevi VerifyJwsObject (ValidatorSdJwt'nin ihraççı
// imzası için kullandığı aynı işlev; anahtar: başlıktaki jwk/x5c ya da PublicJsonWebKeyLookup = deney JWKS'i).
// ValidatorSdJwt.verifySdJwt cüzdan tarafı içindir ve cnf bağlamasını zorunlu tutar ("cnf claim invalid"); doğrulayıcı
// tarafı verifyVpSdJwt KB-JWT ister. V± ve batarya vektörlerinde ikisi de yok → imza katmanı ölçülür (ÖK §2H m.15 okuması;
// NOTLAR.md). Yalnız SD-JWT compact (B6). Algoritma izin listesi API'si yok → IZIN-*/L4* ifade-edilemedi.
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
      // Tanınmayan alg, JwsHeader ayrıştırmasında JwsAlgorithm serileştiricisinden çıkar; vck bunu
      // "Invalid base64url content" iletisine sarar. Neden zincirinde serileştirici aranır.
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
