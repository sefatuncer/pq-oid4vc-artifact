// C3 adaptörü (JVM/Kotlin) ortak çekirdeği: COSE-001 Signum indispensable-cosef ve SDJWT-001 A-SIT vck.
// Sözleşme: adaptor-sozlesme.md (1.0) + KOSUCU.md. Oracle'ı GÖRMEZ; MANIFEST'ten yalnız dogrulama_girdileri.
// Kullanım: kt-adaptor <hedef_id> <isler.jsonl> <cikti.jsonl> <kosu>
package c3

import kotlinx.serialization.json.*
import java.io.File
import java.security.MessageDigest
import java.util.Base64

val J = Json { ignoreUnknownKeys = true }
const val A = "ES256"
const val LEGACY = "https://legacy-issuer.example"
val X_OF = mapOf("kontrol-EdDSA" to "EdDSA", "kontrol-Ed25519" to "Ed25519", "tedavi-ML-DSA-65" to "ML-DSA-65", "tedavi-composite" to "ML-DSA-65-ES256")
val KID = HashMap<String, JsonObject>()
val ALG2KID = HashMap<String, String>()

class IfadeEdilemedi(m: String) : Exception(m)

fun b64d(s: String): ByteArray = Base64.getUrlDecoder().decode(s.replace("=", ""))
fun JsonObject.s(k: String): String = this[k]?.jsonPrimitive?.contentOrNull ?: ""

fun loadKeys() {
  for (f in listOf("v1/acik-jwks.json", "v1.3/acik-jwks.json"))
    for (k in J.parseToJsonElement(File("/anahtarlar/$f").readText()).jsonObject["keys"]!!.jsonArray) KID[k.jsonObject.s("kid")] = k.jsonObject
  for (f in listOf("v1/roller.json", "v1.3/roller.json"))
    for ((r, v) in J.parseToJsonElement(File("/anahtarlar/$f").readText()).jsonObject["roller"]!!.jsonObject)
      if (r.startsWith("issuer/")) ALG2KID.putIfAbsent(v.jsonObject.s("tur"), v.jsonObject.s("kid"))
}

/** Politikanın temel adı (sdjwtvc ve zaman ekleri kütüphane yapılandırmasını değiştirmez). */
fun temel(pol: String) = pol.substringBefore('|').substringBefore('@')

/** Algoritma izin listesi API'si olmayan hedefler için: kütüphane varsayılanıyla ölçülebilen politikalar. */
val VARSAYILAN = setOf("GEC", "P0", "P1", "P2")

fun klass(e: Throwable): String {
  val m = (e.javaClass.simpleName + " " + e.message + " " + (e.cause?.message ?: "")).lowercase()
  // Algoritma tanınmıyorsa ayrıştırma hatası olarak da yüzeye çıkabilir; algoritma sözcükleri önce aranır.
  val t = listOf("unknown alg" to "alg-desteklenmiyor", "unsupported" to "alg-desteklenmiyor", "not supported" to "alg-desteklenmiyor",
    "no key" to "anahtar-bulunamadi", "signature" to "imza-gecersiz", "verif" to "imza-gecersiz",
    "expired" to "zaman", "not yet valid" to "zaman", "serializ" to "ayristirma", "decod" to "ayristirma", "parse" to "ayristirma")
  for ((p, c) in t) if (m.contains(p)) return c
  return "istisna-diger"
}

interface T {
  val ver: String
  val api: String
  val formats: Set<String>
  fun verify(job: JsonObject, data: ByteArray, X: String): List<Map<String, Any>>
}

fun sonuc(alg: String) = listOf(mapOf<String, Any>("sira" to 0, "alg" to alg, "sonuc" to "gecerli"))

fun anyToJson(v: Any?): JsonElement = when (v) {
  null -> JsonNull
  is String -> JsonPrimitive(v)
  is Number -> JsonPrimitive(v)
  is Boolean -> JsonPrimitive(v)
  is Map<*, *> -> JsonObject(v.entries.associate { it.key.toString() to anyToJson(it.value) })
  is List<*> -> JsonArray(v.map { anyToJson(it) })
  else -> JsonPrimitive(v.toString())
}

fun calistir(a: Array<String>, hedef: (String) -> T) {
  val (hid, isler, cikti, kosu) = a
  loadKeys()
  val t = hedef(hid)
  val md = MessageDigest.getInstance("SHA-256")
  File("/a/src").walkTopDown().filter { it.isFile }.sortedBy { it.path }.forEach { md.update(it.readBytes()) }
  val asha = md.digest().joinToString("") { "%02x".format(it) }
  File(cikti).bufferedWriter(Charsets.UTF_8).use { out ->
    for (line in File(isler).readLines(Charsets.UTF_8)) {
      if (line.isBlank()) continue
      val job = J.parseToJsonElement(line).jsonObject
      val X = X_OF[job.s("kol")] ?: "EdDSA"
      val r = linkedMapOf<String, Any?>("hedef_id" to hid, "hedef_surum" to t.ver, "adaptor_sha256" to asha, "kosu" to kosu,
        "vektor_id" to job.s("vektor_id"), "politika" to job.s("politika"), "kol" to job.s("kol"),
        "sonuc_ham" to null, "hata_sinifi" to null, "hata_ozeti" to null, "dogrulanan_algoritmalar" to emptyList<Any>(), "api_yolu" to t.api)
      val ser = job.s("serilestirme")
      val eff = if (ser == "compact" && "compact-as-sdjwt" in t.formats) "compact-as-sdjwt" else ser
      if (eff !in t.formats) {
        r["sonuc_ham"] = "uygulanamaz"; r["hata_sinifi"] = "bicim-desteklenmiyor"
        out.write(anyToJson(r).toString() + "\n"); continue
      }
      val data = File("/v/" + job.s("dosya")).readBytes()
      val t0 = System.nanoTime()
      try {
        val res = t.verify(job, data, X)
        r["sonuc_ham"] = "kabul"; r["dogrulanan_algoritmalar"] = res
      } catch (e: IfadeEdilemedi) {
        r["sonuc_ham"] = "ifade-edilemedi"; r["hata_sinifi"] = "politika-api-yok"; r["hata_ozeti"] = e.message
      } catch (e: Throwable) {
        r["sonuc_ham"] = "red"; r["hata_sinifi"] = klass(e)
        val m = e.javaClass.simpleName + ": " + e.message
        r["hata_ozeti"] = if (m.length > 200) m.substring(0, 200) else m
      }
      r["sure_ms"] = (System.nanoTime() - t0) / 1e6
      out.write(anyToJson(r).toString() + "\n")
    }
  }
}
